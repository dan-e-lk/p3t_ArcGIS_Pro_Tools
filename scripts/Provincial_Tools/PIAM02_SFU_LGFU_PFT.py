# you should run PIAM01 before running this script.
"""
This script alters the input fc.

What this script does:
1. Create ECONUM fields and populate them based on PRI_ECO
2. Create and populate the following fields (in the order of population):
	Will use tbl_sql_classify.csv saved in the same parent folder as this script.
	SFU, PFT, and optional package: ECOGRP, LGFU, LGDS, LGCLS 
	Note that PFT is dependent on SFU, and LGFU is dependent on ECOGRP, and LGDS is dependent on LGFU and LGCLS is dependent on both LGDS and LGFU.


This script assumes that
- You ran the PIAM01 script first - with Species group populated with 'Original' method.
- the mandatory field list below exist in the inputfc
- PRI_ECO field is populated correctly. i.e. first 4 letters of the value is something like 'B055' when POLYTYPE = 'FOR'

"""

import arcpy
import os, csv
import pandas as pd

man_fields = ['POLYTYPE','PRI_ECO']
sql_tbl_csv = 'tbl_sql_classify.csv' # this should be saved in the same parent folder as this script


def populate_fu(inputfc,skip_eco_if_exists):
	
	# loading csv to pandas dataframe
	df = pd.read_csv(sql_tbl_csv)
	df = df[['REGION','FIELD','SQL_ORDER','SQL_NAME','SQL_SYNTAX']] # select only the fields we need
	# logger.print2(df)

	# housekeeping first
	existingFields = [str(f.name).upper() for f in arcpy.ListFields(inputfc)]
	oid_fieldname = arcpy.Describe(inputfc).OIDFieldName
	count_orig = int(arcpy.management.GetCount(inputfc)[0])
	# checking mandatory fields
	for fname in man_fields:
		if fname not in existingFields:
			logger.print2('Missing mandatory field: %s'%fname,'w')


	# Add a new field: ECONUM
	logger.print2("Adding a new field: ECONUM")
	if 'ECONUM' not in existingFields:
		econum_exists = False
		arcpy.AddField_management(in_table = inputfc, field_name = 'ECONUM', field_type = "SHORT")
	else:
		logger.print2("\tECONUM already exists")
		econum_exists = True
	# also add ECO_ERROR if not exist
	if 'ECO_ERROR' not in existingFields:
		logger.print2("Adding a new field: ECO_ERROR")
		arcpy.AddField_management(in_table = inputfc, field_name = 'ECO_ERROR', field_type = "SHORT") # 0 or 1, 1 being error

	# populate the ECONUM field if required
	if econum_exists and skip_eco_if_exists:
		logger.print2("The script will move on, assuming that ECONUM is correctly populated with numbers between 0 and 999")
		pass # skip populating econum values
	else:
		# populate ECONUM
		logger.print2("\nPopulating ECONUM...")
		ecoerror_counter = 0
		forest_rec_counter = 0
		select_FOR = "POLYTYPE='FOR'"
		f = [oid_fieldname, 'POLYTYPE','PRI_ECO','ECONUM','ECO_ERROR']
		with arcpy.da.UpdateCursor(inputfc, f, select_FOR) as cursor:
			for row in cursor:
				forest_rec_counter += 1
				prieco = row[2] # should be something like 'B050TtD n'
				ecoerror = 0
				econum = 0

				try:
					econum = int(prieco[1:4]) # eg. 50
				except:
					ecoerror = 1
					ecoerror_counter += 1

				# also no good if econum is zero or 997,998,999 where polytype is FOR
				if econum in [0,997,998,999]:
					ecoerror = 1
					ecoerror_counter += 1

				row[3] = econum
				row[4] = ecoerror
				cursor.updateRow(row)

		# warn if too many errors - how many is too many?
		logger.print2("Number of records where ECONUM was invalid (0 or 999 is also invalid): %s"%ecoerror_counter)
		eco_err_perc = round(ecoerror_counter*100/forest_rec_counter,2)
		if eco_err_perc > 5:
			logger.print2("WARNING: Many errors (%s%%) detected while populating ECONUM from PRI_ECO.",'w')
			logger.print2("\tCheck PRI_ECO values of the records where ECO_ERROR = 1")
			if eco_err_perc > 30:
				raise Exception("Too many ECONUM error! Check your PRI_ECO field.")




	# # loading habitat_classification.csv to memory
	# tbl_chc = 'habitat_classification.csv'
	# parent_folder = os.path.split(__file__)[0]
	# l_tbl_chc = list(csv.DictReader(open(os.path.join(parent_folder,tbl_chc))))
	# logger.print2(tbl_chc)

	# # here are some lines I write all the time:
	# existingFields = [str(f.name).upper() for f in arcpy.ListFields(inputfc)]
	# oid_fieldname = arcpy.Describe(inputfc).OIDFieldName
	# count_orig = int(arcpy.management.GetCount(inputfc)[0])
	# arcpy.AddField_management(in_table = outputfc, field_name = check_field, field_type = "TEXT", field_length = "120") # SHORT, LONG, FLOAT, DOUBLE
	# arcpy.FeatureClassToFeatureClass_conversion(in_features=inputfc, out_path=os.path.split(outputfc)[0], out_name=os.path.split(outputfc)[1], where_clause=select_none_sql)
	# with arcpy.da.UpdateCursor(inputfc, existingFields) as cursor:
	# 	for row in cursor:
	# 		row[1] = 4
	# 		cursor.updateRow(row)	

	# # Make Layer, Select, and Calculate Field
	# arcpy.management.MakeFeatureLayer(inputfc, "temp_lyr")
	# arcpy.management.SelectLayerByAttribute("temp_lyr", "NEW_SELECTION", "")
	# arcpy.management.CalculateField("temp_lyr", fieldName, expression, code_block=code_block)


if __name__ == '__main__':
	
	# gather inputs
	inputfc = arcpy.GetParameterAsText(0)
	skip_eco_if_exists = False # skip populating values if ECONUM already exists

	######### logfile stuff

	tool_shortname = 'PIAM02' # the output logfile will include this text in its filename.

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
	populate_fu(inputfc,skip_eco_if_exists)

	# finish writing the logfile
	logger.log_close()