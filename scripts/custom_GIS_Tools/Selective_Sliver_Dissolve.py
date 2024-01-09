# slivers will be merged to neighboring polygon with similar attributes
# the tool doesn't alter the original input data
version = '0.1.0'

import arcpy
from datetime import datetime
import os

# my library
from messages import print_n_log


def main(inputfc, outputWS, uniq_id_fname, sliver_SQL, fields_to_match):

	## PART I.  HOUSEKEEPING #######################################################

	starttime = datetime.now()

	# start logging
	p = print_n_log()
	p.print2("Selective Sliver Dissolve Tool v%s"%version)
	p.print2('Start of process: %(start)s.' %{'start':starttime.strftime('%Y-%m-%d %H:%M:%S')})

	# start by printing out inputs...
	#....

	arcpy.env.workspace = outputWS

	if outputWS.upper().endswith('.GDB'):
		gdbpath = outputWS
	else:
		gdbpath = os.path.split(outputWS)[0] # gdb path is used later to create log file on its parent folder
	p.print2("path to gdb: %s"%gdbpath)

	# check if the input has mandatory fields
	p.print2("Checking mandatory fields...")
	mand_fields = [uniq_id_fname,'SHAPE_AREA'] + fields_to_match
	existingFields = [str(f.name).upper() for f in arcpy.ListFields(inputfc)]

	for mf in mand_fields:
		if mf.upper() in existingFields:
			pass
		else:
			msg = "%s field is missing!"%mf
			arcpy.AddWarning(msg)
			raise Exception(msg)
	p.print2("All mandatory fields are there.")

	# get count and area of the original input fc
	rec_count_orig=0
	total_area_orig=0
	with arcpy.da.SearchCursor(inputfc, ['SHAPE_AREA']) as cursor:
		for row in cursor:
			rec_count_orig += 1
			total_area_orig += row[0]

	p.print2("\nTotal Number of records in input fc = %s"%rec_count_orig)
	p.print2("\nTotal area of input fc = %s sqm\n"%round(total_area_orig,4))



	## PART II. IDENTIFY SLIVERS  ################################################

	# select using Sliver SQL, then get the unique_id of all slivers
	p.print2("Selecting the slivers: %s"%sliver_SQL)
	sliver_id_area = {} # eg. {354: 35.5533, ....}
	with arcpy.da.SearchCursor(inputfc, [uniq_id_fname, 'SHAPE_AREA'], sliver_SQL) as cursor:
		for row in cursor:
			sliver_id_area[row[0]] = row[1]
	# end script here if no sliver selected
	sliver_count = len(sliver_id_area)
	if sliver_count == 0:
		arcpy.AddError("Your Sliver SQL selected no record. No sliver to remove!")
	# p.print2("Sliver id and area:\n%s"%sliver_id_area)

	# give a little stats on the slivers
	sliver_ids = list(sliver_id_area.keys())
	sliver_total_area = sum(sliver_id_area.values())
	sliver_area_average = sliver_total_area/sliver_count
	p.print2("List of sliver %s: %s"%(uniq_id_fname,sliver_ids))
	p.print2("Sliver total count: %s (%s %% of total)"%(sliver_count,round(sliver_count*100/rec_count_orig,2)))
	p.print2("Sliver total area: %s sqm (%s %% of total)"%(round(sliver_total_area,4),round(sliver_total_area*100/total_area_orig,4)))
	p.print2("Sliver area average: %s sqm"%round(sliver_area_average,4))



	## PART III. POLYGON NEIGHBORS  ############################################
	
	# output of this tool is a table. the fields in this table have src_unique_id and nbr_unique_id
	p.print2("\nRunning Polygon Neighbors tool...")
	pn_output = "t_%s_pn_temp"%os.path.split(inputfc)[1]
	arcpy.analysis.PolygonNeighbors(inputfc, pn_output, uniq_id_fname)

	# iterate through the output table. For each unique_ID of the slivers find the unique_IDs of the neighbors.
	sliver_n_neighbors = {uid:[] for uid in sliver_ids} # eg. {340:[97,168,214,347,352,364,365],  344:[...],...}
	with arcpy.da.SearchCursor(pn_output, ['src_'+uniq_id_fname, 'nbr_'+uniq_id_fname]) as cursor:
		for row in cursor:
			src_id = row[0]
			if src_id in sliver_ids:
				nbr_id = row[1]
				sliver_n_neighbors[src_id].append(nbr_id)

	p.print2("sliver and its neighbors:\n%s"%sliver_n_neighbors)
	# delete the temporary PN tool output
	p.print2("Deleting the temporary file...")
	arcpy.management.Delete(pn_output) # for ESRI, this is the most time consuming part of all...



	## PART IV. DECIDING WHICH NEIGHBOR TO MERGE TO  ########################

	# turn the original input fc into a dictionary using unique_id as the key, and incl the values in the fields_to_match and SHAPE_AREA
	p.print2("\nGrabbing info from the input feature class...")
	inputfc_dict = {} #eg. {1: {'UNIQUE_ID': 1, 'SHAPE_AREA': 295932.4065195683, 'AGE': 154, 'SPCOMP': 'SB  90LA  10', 'f2m_str':'154SB  90LA  10'}, 2:{'UNIQUE_ID': 2,..},..}
	with arcpy.da.SearchCursor(inputfc, mand_fields) as cursor:
		for row in cursor:
			row_dict = {}
			for index, fname in enumerate(mand_fields):
				row_dict[fname] = row[index]

			f2m_str = '' # field to match string is a concatenation of all values in field_to_match fields into one string. eg. '154SB  90LA  10'
			for fname in fields_to_match:
				f2m_str += str(row[mand_fields.index(fname)]) #eg. 'SB  90LA  10' or '154' (whatever values the fields_to_match has)
			row_dict['f2m_str'] = f2m_str
			inputfc_dict[row[0]] = row_dict # row[0] is the unique_id value of that row.
	
	# loop through the unique ids of the slivers and decide to which neighboring polygon the sliver should merge
	# a neighbor can be an absorbing neighbor only if the values in fields_to_match matches
	# if there are more than one candidate of absorbing neighbor, the bigger neighbor becomes the absorbing neighbor
	# a sliver cannot be the absorbing neighbor of another sliver
	# the_pair consists of the pair of sliver polygon and the absorbing neighbor polygon
	p.print2("\nBuilding sliver to absorbing neighbor pairs...")
	the_pair = {sliver_id:None for sliver_id in sliver_n_neighbors.keys()} # eg. {340:365, 344:None,...}
	for sliv, neighb in sliver_n_neighbors.items():
		target_f2m_str = inputfc_dict[sliv]['f2m_str'] #eg. '154SB  90LA  10'
		candidate_neighbor_area = 0
		for uid in neighb:
			# if there is a match and the match is not another sliver
			if inputfc_dict[uid]['f2m_str'] == target_f2m_str and uid not in sliver_ids:
				# and if this match is the biggest neighbor
				if inputfc_dict[uid]['SHAPE_AREA'] > candidate_neighbor_area:
					# we found it!
					the_pair[sliv]=uid # eg. {340:365}

	p.print2("Done! First number is the id of the sliver and the second number is the id of the neighbor that the sliver will merge into:")
	p.print2(str(the_pair))





	# output1, output2, output3 = None,None,None

	# # run 1st Eliminate
	# p.print2("Running the Eliminate tool the first time...")
	# output1 = outputfc_filename + "_1stElim"
	# arcpy.Eliminate_management("lyr0",output1,elim_by_border, exclusion_SQL)
	# arcpy.MakeFeatureLayer_management(output1, "lyr1")
	# rec_count_output1 = arcpy.management.GetCount("lyr1")
	# p.print2("Success! Output fc feature count: %s\n\n"%rec_count_output1)




if __name__ == '__main__':

	inputfc = arcpy.GetParameterAsText(0)
	outputWS = arcpy.GetParameterAsText(1) # should be the path to an existing gdb
	uniq_id_fname = arcpy.GetParameterAsText(2) # text
	sliver_SQL = arcpy.GetParameterAsText(3) # should be an SQL that you can run on the inputfc
	fields_to_match = arcpy.GetParameterAsText(4) # list of fields in inputfc that needs to match with the sliver for the polygons to merge

	# cleaning up the paramters
	if '.GDB' not in outputWS.upper():
		arcpy.AddWarning("Output GDB should be the path to a geodatabase")
	fields_to_match = fields_to_match.split(";")
	uniq_id_fname = uniq_id_fname.upper()

	# checking the inputs - debug only
	for i in [inputfc, outputWS, uniq_id_fname, sliver_SQL, fields_to_match]:
		arcpy.AddMessage(i)


	main(inputfc, outputWS, uniq_id_fname, sliver_SQL, fields_to_match)