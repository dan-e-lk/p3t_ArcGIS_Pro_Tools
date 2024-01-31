# slivers will be merged to neighboring polygon with similar attributes
# the tool doesn't alter the original input data
# the tool won't work if the uniq_id_fname values are not unique!!!!!

# To do for Daniel:
# Script to add the final output to the current map on ArcGIS Pro
# ArcGIS Tool - write help section

version = '0.1.0'

import arcpy
from datetime import datetime
import os

# my library
from messages import print_n_log


def main(inputfc, outputWS, uniq_id_fname, sliver_SQL, fields_to_match):

	p.print2("\n\n## PART I.  HOUSEKEEPING #######################################################")
	# start by printing out inputs...
	p.print2("\nInput Feature Class: %s"%inputfc)
	p.print2("Output GDB: %s"%outputWS)
	p.print2("Unique ID Fieldname: %s"%uniq_id_fname)
	p.print2("Sliver Selection SQL:\n\t%s"%sliver_SQL)
	p.print2("List of Fields to match: %s"%fields_to_match)

	arcpy.env.workspace = outputWS
	global pn_output, temp_fc_1, gdbpath, final_fc, rand # these will be defined later, but setting them global here.
	rand = rand_alphanum_gen(4) # this random mix of alphanumeric characters will be used throughout this script

	if outputWS.upper().endswith('.GDB'):
		gdbpath = outputWS
	else:
		p.print2("\nERROR: Your output workstaion must be a file geodatabase (~.gdb)",'error')
		raise

	# check if the input has mandatory fields
	p.print2("\nChecking mandatory fields...")
	mand_fields = [uniq_id_fname,'SHAPE_AREA'] + fields_to_match
	existingFields = [str(f.name).upper() for f in arcpy.ListFields(inputfc)]
	# p.print2(str(existingFields))

	for mf in mand_fields:
		if mf.upper() in existingFields:
			pass
		else:
			msg = "%s field is missing!"%mf
			arcpy.AddWarning(msg)
			raise Exception(msg)
	p.print2("All mandatory fields are there.")

	# get count and area of the original input fc
	# and check if the unique field values are actually unique
	uniq_id_values = []
	rec_count_orig=0
	total_area_orig=0
	with arcpy.da.SearchCursor(inputfc, ['SHAPE_AREA',uniq_id_fname]) as cursor:
		for row in cursor:
			rec_count_orig += 1
			total_area_orig += row[0]
			uniq_id_values.append(row[1])

	p.print2("\nTotal Number of records in input fc = %s"%rec_count_orig)
	p.print2("Total area of input fc = %s sqm\n"%round(total_area_orig,4))

	if type(uniq_id_values[0]) != int:
		p.print2("Your unique field values should be integers.",'warning')
	if len(uniq_id_values) != len(set(uniq_id_values)):
		p.print2("Your unique field values are not all unique. Please create a new unique value field.",'error')
		raise
	else:
		p.print2("Your unique field values are all unique.")


	p.print2("\n\n## PART II. IDENTIFY SLIVERS  ##################################################")

	# select using Sliver SQL, then get the unique_id of all slivers
	p.print2("\nSelecting the slivers: %s"%sliver_SQL)
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
	# p.print2("List of sliver %s: %s"%(uniq_id_fname,sliver_ids))
	p.print2("Quick Sliver Stats:")
	p.print2("\tSliver total count: %s (%s %% of total)"%(sliver_count,round(sliver_count*100/rec_count_orig,2)))
	p.print2("\tSliver total area: %s sqm (%s %% of total)"%(round(sliver_total_area,4),round(sliver_total_area*100/total_area_orig,4)))
	p.print2("\tSliver area average: %s sqm"%round(sliver_area_average,4))



	p.print2("\n\n## PART III. POLYGON NEIGHBORS  ################################################")
	
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

	# p.print2("sliver and its neighbors:\n%s"%sliver_n_neighbors)


	p.print2("\n\n## PART IV. DECIDING WHICH NEIGHBOR TO MERGE TO  ################################")

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
	# a neighbor can be a dominant neighbor only if the values in fields_to_match matches
	# if there are more than one candidate of dominant neighbor, the bigger neighbor becomes the dominant neighbor
	# a sliver cannot be the dominant neighbor of another sliver
	# the_pair consists of the pair of sliver polygon and the dominant neighbor polygon
	p.print2("\nBuilding sliver to dominant neighbor pairs...")
	the_pair = {sliver_id:None for sliver_id in sliver_n_neighbors.keys()} # eg. {340:365, 344:None,...}  <----- this is the most important dictionary!
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

	p.print2("Tada~! First number is the id of the sliver and the second number is the id of the dominant neighbor that the sliver will merge into:")
	p.print2(str(the_pair) + '\n')



	p.print2("\n\n## PART V. PREPARE TO DISSOLVE  ##########################################")

	# making a copy of the input, so we can edit it.
	p.print2("\nMaking a copy of the input feature class so we can edit it...")
	temp_fc_1 = "t_%s_temp0"%os.path.split(inputfc)[1]
	arcpy.conversion.FeatureClassToFeatureClass(inputfc, outputWS, temp_fc_1)

	# find all the fields to edit. these are all fields except the default fields = OBJECTID, SHAPE, SHAPE_AREA and SHAPE_LENGTH
	uneditable_fields = ['OBJECTID','SHAPE','SHAPE_AREA','SHAPE_LENGTH']
	editable_fields = [f for f in existingFields if f not in uneditable_fields] # eg. ['POLYTYPE', 'OWNER', 'SPCOMP', 'AGE', 'UNIQUE_ID'...]
	p.print2("editable_fields: %s"%editable_fields)
	uniq_id_f_index = editable_fields.index(uniq_id_fname.upper())

	# first loop through to grab all the values of the dominant polygon
	# second loop through to update the sliver values using the values of the dominant polygon
	neighb_lst = list(set(the_pair.values())) # one neighbor might appear more than once. we don't want that in a dictionary.
	if None in neighb_lst: neighb_lst.remove(None) # remove the None value
	sliver_lst = list(the_pair.keys())
	neighb_info = {neighb_id:None for neighb_id in neighb_lst} # "None" will be replaced by a dictionary such as {'AGE': 154, 'SPCOMP': 'SB  90LA  10',...}
	p.print2("Copying the values of the dominant neighbor polygon...")
	with arcpy.da.SearchCursor(temp_fc_1, editable_fields) as cursor:
		for row in cursor:
			row_id = row[uniq_id_f_index]
			if row_id in neighb_lst:
				# p.print2("\tCopying %s=%s"%(uniq_id_fname,row_id))
				neighb_record = {fname:row[ind] for ind, fname in enumerate(editable_fields)} # eg. {'AGE': 154, 'SPCOMP': 'SB  90LA  10',...}
				neighb_info[row_id] = neighb_record

	# secondly, update the sliver records with the values of its dominant neighbor polygon
	p.print2("\nUpdating the sliver records with the values of the dominant neighbor polygon...")
	with arcpy.da.UpdateCursor(temp_fc_1, editable_fields) as cursor:
		for row in cursor:
			row_id = row[uniq_id_f_index]
			if row_id in sliver_lst:
				if the_pair[row_id] != None: #ignore if there's no dominant neighbor to that sliver
					# p.print2("\tUpdating %s=%s"%(uniq_id_fname,row_id))
					# load the values of the dominant neighbor
					neighb_info_dict = neighb_info[the_pair[row_id]]
					# update the sliver record values with the neighb_info
					for i, f in enumerate(editable_fields):
						row[i] = neighb_info_dict[f]
					# save it
			cursor.updateRow(row)



	p.print2("\n\n## PART VI. DISSOLVE  ###########################################################")

	p.print2("\nRunning Dissolve...")
	final_fc = "%s_SlvrDslv_%s"%(os.path.split(inputfc)[1],rand)
	# set the environment - xy tolerance to 0.1 Meters. this is to avoid generating gaps between polygons
	arcpy.env.XYTolerance = "0.1 Meters"
	arcpy.management.Dissolve(temp_fc_1, final_fc, editable_fields, "", "SINGLE_PART")
	p.print2("\nSuccess!!")



	p.print2("\n\n## PART VII. CHECK FOR OBVIOUS ERRORS AND CLEAN UP  ###########################")

	# get count and area of the final fc
	rec_count_fin=0
	total_area_fin=0
	with arcpy.da.SearchCursor(final_fc, ['SHAPE_AREA']) as cursor:
		for row in cursor:
			rec_count_fin += 1
			total_area_fin += row[0]

	count_diff = rec_count_fin-rec_count_orig
	count_diff_perc = round(count_diff*100/rec_count_orig,2)
	area_diff = round(total_area_fin-total_area_orig,4)
	area_diff_perc = round(area_diff*100/total_area_orig,10)

	p.print2("\nOriginal vs Final:")
	p.print2("\tRecord Count:")
	p.print2("\t\tOriginal: %s"%rec_count_orig)
	p.print2("\t\tFinal: %s"%rec_count_fin)
	p.print2("\t\tDifference: %s (%s%%)"%(count_diff,count_diff_perc))
	p.print2("\tArea:")
	p.print2("\t\tOriginal: %s sqm"%round(total_area_orig,4))
	p.print2("\t\tFinal: %s sqm"%round(total_area_fin,4))
	p.print2("\t\tDifference: %s sqm (%s%%)"%(area_diff,area_diff_perc))
	if abs(area_diff_perc)>0.1:
		p.print2("\nToo much area change detected. Check the topology of your input feature class and make sure there are no overlaps.",'warning')


	### Record count increase - the reason would be because the input fc had many multipart polygons.








def rand_alphanum_gen(length):
    """
    Generates a random string (with specified length) that consists of A-Z and 0-9.
    """
    import random, string
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(length))










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
	if uniq_id_fname == 'OBJECTID':
		arcpy.AddError("Unique ID Field cannot be OBJECTID for this tool. Please create a new field (long) and generate its values with the existing OBJECTID.")
		raise


	######### Running the script ##############################

	# doing try, except, and finally to delete temp files even if the script fails to run
	try:
		script_ran_successfully = True
		starttime = datetime.now()

		# start logging
		global p
		p = print_n_log()
		p.print2("Selective Sliver Dissolve Tool v%s"%version)
		p.print2('Start of process: %(start)s.' %{'start':starttime.strftime('%Y-%m-%d %H:%M:%S')})

		main(inputfc, outputWS, uniq_id_fname, sliver_SQL, fields_to_match)

	except:
		script_ran_successfully = False
		# if any error encountered, log it, but MOVE ON
		var = traceback.format_exc()
		p.print2(var,'warning')


	finally:
		# clean up the temporary outputs whether the tool run successfully or not
		p.print2("\n\nDeleting the temporary files...")
		fc_to_be_deleted = [pn_output,temp_fc_1]
		for i, fc in enumerate(fc_to_be_deleted):
			try:
				p.print2("\t%s of %s..."%(i+1,len(fc_to_be_deleted)))
				arcpy.management.Delete(fc)
			except:
				pass
		if script_ran_successfully:
			p.print2("Selective Sliver Dissolve script ran SUCCESSFULLY!")
			p.print2("The final product is located here:\n%s"%os.path.join(outputWS,final_fc))
			p.print2("\nREMEMBER to re-calculate your area-dependent fields such as HECTARES field!")

		else:
			p.print2("Failed to complete the task and here's why:")
			p.print2(var,'warning')

		# write up the log file
		log_path = os.path.split(gdbpath)[0]
		date = starttime.strftime('%Y%m%d')
		log_filename = "SelectiveSliverDissolve_LOG_ %s%s.txt"%(date,rand)
		p.create_logfile(log_path,log_filename)
		p.print2("Logfile created:\n%s"%os.path.join(log_path,log_filename))