# There are two main upgrades to this script since the v1 (ArcMap) edition.
# 1. the end-user gets to group species, instead of creating over 80 species fields. The end-user can also customize this grouping.
# 2. This script runs faster.  The trick is to export the fc with zero records, add fields to the empty fc, then append the original data to the new fc.


import arcpy
import os, csv

# Species set is a speices group combinations that was hardcoded in Larry's ProcessPI script (under update spp combos)
# The key is the species set name (also a new fieldname) and the value is the list of species percentages that will be all added up.
spc_set_tbl = {
	'UH':		['MH','MR','QR','OW','OB','YB'],
	'LH':		['AB','EX','PB'],
	'ALLCON':	['PW','PR','PJ','SB','SW','BF','CE','LA','HE','OC'],
	'ALLHWD':	['MH','MR','QR','OW','OB','YB']+['AB','EX','PB']+['AW','BE','BD','BW','CH','IW','PL','PO','PT']+['OH'] # UH + LH + more + OH
}


def spcVal(data, fieldname, all_spc_list): #sample data: 'Cw  70La  20Sb  10'
	#assuming the data is not None or empty string
	try:
		if len(data)%6 == 0:
			n = int(len(data)/6) # this is the change in python3. must put int()
			spcList = [data[6*i:6*i+3].strip().upper() for i in range(n)]
			percentList = [int(data[6*i+3:6*i+6].strip()) for i in range(n)]
			# build species to percent dictionary
			spcPercentDict = dict(zip(spcList,percentList)) # this should look like {'AX':60,'CW':40}

			if sum(percentList) == 100:
				if len(set(spcList)) == len(spcList):

					correctList = list(set(spcList)&set(all_spc_list))
					if len(correctList) == len(spcList):
						return ['Pass',spcPercentDict]
					else:
						wrongList = list(set(spcList) - set(correctList))
						return ["Error","%s has invalid species code(s): %s"%(fieldname,wrongList)]
				else:
					return ["Error","%s has duplicate species codes"%fieldname]
			else:
				return ["Error","%s does not add up to 100"%fieldname]
		else:
			return ["Error", "%s does not follow the SSSPPPSSSPPP patern"%fieldname]
	except:
		return ["Error", "%s does not follow the SSSPPPSSSPPP patern"%fieldname]


# here are some lines I write all the time:
# existingFields = [str(f.name).upper() for f in arcpy.ListFields(inputfc)]
# oid_fieldname = arcpy.Describe(input_fc).OIDFieldName

def main(inputfc,outputfc,spfield, spc_group_method):
	
	## loading habitat_classification.csv to memory
	tbl_spp = 'tbl_spp.csv'
	parent_folder = os.path.split(__file__)[0]
	l_tbl_spp = list(csv.DictReader(open(os.path.join(parent_folder,tbl_spp))))
	# logger.print2(l_tbl_spp) # eg. [{'spc': 'AB', 'spc_grp_orig': 'AB', 'spc_grp_alt': 'AB'}, {'spc': 'AG', 'spc_grp_orig': 'AW', 'spc_grp_alt': 'AW'},...]
	# need a map of species code to species group code
	spc_to_grp_map = {i['spc']:i[spc_group_method] for i in l_tbl_spp}
	logger.print2("Species code to species group mapping:\n%s"%spc_to_grp_map) # eg. {'AB': 'AB', 'AG': 'AW', 'AL': 'OH', ... 'YB':'YB'}
	# all possible species code list
	all_spc_list = list(spc_to_grp_map.keys())
	# logger.print2(all_spc_list) # eg. ['AB', 'AG', 'AL',...'WB', 'WI', 'YB']


	## export an empty inputfc to outputfc
	logger.print2("\nCreating a new feature class:\n%s\n"%outputfc)
	oid_fieldname = arcpy.Describe(inputfc).OIDFieldName
	select_none_sql = "%s<0"%oid_fieldname # "OBJECTID < 0" will select zero records
	arcpy.FeatureClassToFeatureClass_conversion(in_features=inputfc, out_path=os.path.split(outputfc)[0], out_name=os.path.split(outputfc)[1], where_clause=select_none_sql)


	## make fields (also add SPC_CHECK field)
	# get list of species groups (original or alternative)
	spc_grp_lst = list(set([row[spc_group_method] for row in l_tbl_spp]))
	spc_grp_lst.sort()
	all_new_field_lst = spc_grp_lst.copy()
	for spc_grp in spc_grp_lst:
		logger.print2("Creating a new field: %s"%spc_grp)
		arcpy.AddField_management(in_table = outputfc, field_name = spc_grp, field_type = "SHORT")
	# SPC Check field
	check_field = 'SPC_Check'
	logger.print2("Creating a new field: %s"%check_field)
	arcpy.AddField_management(in_table = outputfc, field_name = check_field, field_type = "TEXT", field_length = "120")
	all_new_field_lst.append(check_field)
	# species set fields
	spc_set_lst = list(spc_set_tbl.keys()) # i.e. ['UH','LH','ALLCON','ALLHWD'] # do not change these values!
	for spc_set in spc_set_lst:
		logger.print2("Creating a new field: %s"%spc_set)
		arcpy.AddField_management(in_table = outputfc, field_name = spc_set, field_type = "SHORT")
		all_new_field_lst.append(spc_set)

	## append records from inputfc to outputfc.
	recordCount = int(arcpy.management.GetCount(inputfc)[0])
	logger.print2("\n\nAppending %s records from input to output feature class."%recordCount)
	arcpy.management.Append([inputfc], outputfc, "NO_TEST")


	## populate values (or zeros) for all the newly created fields (except SPC_Check field) - all fields where SPCOMP IS NOT NULL OR SPCOMP not in ('','-',' ')

	# prep work
	# SppOccurSet = set()    ## Create a set to contain a unique list of species with occurances in the inventory. (to be used for summary) Delete this later!
	SpcOccurDict = dict()   ## Create a dictionary to contain a count of the species occurances in the inventory. (to be used for summary)
	SpcGrp_OccurDict = {row['spc']:0 for row in l_tbl_spp} # eg. {'AB': 0, 'AG': 0, 'AL': 0,... 'YB': 0}

	sppErrorCount = 0  ## If the spcomp value is invalid, count them.
	spcompPopulCount = 0  ## number of records with spcomp value populated.

	logger.print2("\nPopulating species fields with percentage values...")
	f = all_new_field_lst.copy() + [spfield]
	SPCOMPy = {spc:0 for spc in spc_grp_lst+spc_set_lst} # eg. {'AB':0, 'AW':0, ... 'ALLHWD':0} (note that this doesn't include the SPC_Check field)
	SPCOMPy_lst = [] # list of all SPCOMPy (one for each row) to be used for summary later
	sql = "{0} IS NOT NULL AND {0} not in ('','-',' ')".format(spfield) # ie "SPCOMP IS NOT NULL OR SPCOMP not in ('','-',' ')"

	with arcpy.da.UpdateCursor(outputfc, f, sql) as cursor:
		for row in cursor:
			spcompPopulCount += 1
			s = SPCOMPy.copy()

			# parsing out species string and finding errors
			spcomp_str = str(row[f.index(spfield)]).strip()
			# logger.print2(spcomp_str)
			ValResult = spcVal(spcomp_str,spfield,all_spc_list) ## ValResult example: ["Pass", {'AX':60,'CW':40}]

			if ValResult[0] != "Error":
				row[f.index(check_field)] = "Pass"				
				for k, v in ValResult[1].items():
					k = str(k) ## we don't want unicode
					
					if k in SpcOccurDict:
						SpcOccurDict[k] += 1    ## Once the species code and value 'passes; add that species to the speciec orrurance list and increment count by one.
					else:
						SpcOccurDict[k] = 1

					# map this spc to the spc group
					spc_grp = spc_to_grp_map[k] # eg. 'AW' if k = 'AG' according to the tbl_spp.csv
					SpcGrp_OccurDict[spc_grp] += 1

					# assign values to s
					s[spc_grp] += v # filling out SPCOMPy dictionary. eg. {'AB':30, 'AW':10, ... 'ALLHWD':40}

				# calculating species sets: 'UH','LH','ALLCON','ALLHWD'
				for spcset, spclist in spc_set_tbl.items():
					set_value = 0
					for spc in spclist: # for 'UH', add all the values of ['MH','MR','QR','OW','OB','YB']
						set_value += s[spc]
					s[spcset] = set_value

				# species edits for PO and PT - I am not doing this because of the risk of duplicated values

			else:
				sppErrorCount += 1
				row[f.index(check_field)] = "%s: %s"%(ValResult[0], ValResult[1])

			# updating the row with new values collected in s
			# logger.print2(str(s))
			for spcgrp, val in s.items():
				row[f.index(spcgrp)] = val
			cursor.updateRow(row)


	## summarize and log
	logger.print2("\n\nSummarizing results...(tab delimited)")
	# Species Group and individual species occurrence summary
	SpcOccurDict = dict(sorted(SpcOccurDict.items(), key=lambda item: item[1], reverse=True)) # only works python 3+
	logger.print2("\nSpc\tGrp\tOccurrence")
	for spc, occ in SpcOccurDict.items():
		spcgrp = spc_to_grp_map[spc]
		logger.print2("%s\t%s\t%s"%(spc,spcgrp,occ))

	# Species Group Occurrence
	SpcGrp_OccurDict = dict(sorted(SpcGrp_OccurDict.items(), key=lambda item: item[1], reverse=True)) # only works python 3+
	logger.print2("\nGrp\tOccurrence")
	for spcgrp, occ in SpcGrp_OccurDict.items():
		if occ>0:
			logger.print2("%s\t%s"%(spcgrp,occ))

	# Error report, if any
	if sppErrorCount >0:
		logger.print2("\n\n!!!! Error on %s records. %s value does not meet tech spec and the tool was not able to parse them out"%(sppErrorCount,spfield))
		logger.print2("To find these errors use this query:\n%s LIKE 'Error%'")
	else:
		logger.print2("\nNo SPCOMP parsing error found! All Good!")



if __name__ == '__main__':
	
	# gather inputs
	inputfc = arcpy.GetParameterAsText(0) # this should be bmi or pci
	outputfc = arcpy.GetParameterAsText(1) # where to save your work
	spfield = arcpy.GetParameterAsText(2) # OSPCOMP, USPCOMP, SPCOMP or any other fields
	spc_group_method = arcpy.GetParameterAsText(3) # it will generate strings 'original' or 'alternate'

	spc_group_method = 'spc_grp_alt' if spc_group_method == 'alternate' else 'spc_grp_orig'

	######### logfile stuff

	tool_shortname = 'SpcParser2' # the output logfile will include this text in its filename.

	# importing libraries (only works if arclog.py file is located on the parent folder of this script)
	from datetime import datetime
	parent_d = os.path.split(os.path.split(__file__)[0])[0]
	sys.path.append(parent_d)
	from arclog import Print2 as p2

	# find full path where the logfile will be written
	folder_path = arcpy.Describe(inputfc).path
	while arcpy.Describe(folder_path).dataType != 'Folder':
		folder_path = os.path.split(folder_path)[0]
	outfile = os.path.split(inputfc)[1] + '_' + tool_shortname + '-LOG_' + datetime.now().strftime('%Y%m%d_%H%M') + '.txt'
	logfile_path = os.path.join(folder_path,outfile)

	# importing arclog in the parent directory
	logger = p2(logfile_path)

	##########

	# run the main function(s)
	main(inputfc,outputfc,spfield, spc_group_method)

	# finish writing the logfile
	logger.log_close()