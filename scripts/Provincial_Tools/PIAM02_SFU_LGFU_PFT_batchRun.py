# you should run PIAM01 before running this script.
"""
This script alters the input fc.
This is a batch run version - designed to be used for Analysis Ready Inventory.
FC930 has ecosite problem. too many of them are 000.

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

man_fields = ['POLYTYPE','PRI_ECO','SC']
sql_tbl_csv = 'tbl_sql_classify.csv' # this should be saved in the same parent folder as this script


def populate_fu(inputfc,region,field,skip_eco_if_exists):
	
	# loading csv to pandas dataframe
	df = pd.read_csv(sql_tbl_csv, na_filter=False)
	df = df[['REGION','FIELD','SQL_ORDER','SQL_NAME','SQL_SYNTAX']] # select only the fields we need
	df = df[df['REGION']==region]
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
		logger.print2("Number of records where ECONUM was invalid (values such as 0 or 999 are invalid): %s"%ecoerror_counter)
		eco_err_perc = round(ecoerror_counter*100/forest_rec_counter,2)
		if eco_err_perc > 5:
			logger.print2("WARNING: Many errors (%s%%) detected while populating ECONUM from PRI_ECO."%eco_err_perc,'w')
			logger.print2("\tCheck PRI_ECO values of the records where ECO_ERROR = 1")
			if eco_err_perc > 30:
				logger.print2("Too many ECONUM error! (%s) Check your PRI_ECO field."%eco_err_perc,'w')

	# Populate ECOGRP
	f = 'ECOGRP'
	execute_sqls(f, inputfc, existingFields, df)

	# Populate SFU
	f = 'SFU'
	if f in field:
		execute_sqls(f, inputfc, existingFields, df)

	# Populate PFT
	f = 'PFT'
	if f in field:
		execute_sqls(f, inputfc, existingFields, df)

	# Populate ECOGRP, LGFU, LGDS, LGCLS
	if 'LGFU' in field:
		for LG_field in ['LGFU','LGDS','LGCLS']: # must be in this order
			execute_sqls(LG_field, inputfc, existingFields, df)




def execute_sqls(f, inputfc, existingFields, df):
	logger.print2("\n\nAdding a new field: %s"%f)
	if f not in existingFields:
		f_exist = False
		arcpy.AddField_management(in_table = inputfc, field_name = f, field_type = "TEXT", field_length = "10")
	else:
		f_exist = True
		logger.print2("\t%s field already exists"%f)

	# prepare layer file so we can select and calculate field on them
	lyr = '%s_lyr'%f
	arcpy.management.MakeFeatureLayer(inputfc, lyr)
	# wipe out the values if the field existed before
	if f_exist:
		logger.print2("\tDeleting existing values in %s field"%f)
		arcpy.management.CalculateField(lyr, f, 'None')

	# get SQLs in order
	select_df = df[df["FIELD"]==f].sort_values(by=['SQL_ORDER']) # select (SFUs) and sort by SQL_ORDER

	# loop through the select_df
	logger.print2("\nPopulating %s"%f)
	logger.print2("NOTE: The follwing SQLs use grouped species. For example CE=CE+CW and all Elms are EX.")
	for index, row in select_df.iterrows():
		sql_order = row['SQL_ORDER']
		sql_name = row['SQL_NAME']
		sql = row['SQL_SYNTAX'] + ' AND %s IS NULL'%f #########################
		logger.print2("\t%s. %s:"%(sql_order,sql_name))
		logger.print2("\t%s"%sql)
		arcpy.management.SelectLayerByAttribute(lyr, "NEW_SELECTION", sql)
		num_selected = int(arcpy.management.GetCount(lyr)[0])
		logger.print2("\t%s records selected. Populating values..."%num_selected)
		arcpy.management.CalculateField(lyr, f, "'%s'"%sql_name)
		logger.print2("\t\tDone\n")		




if __name__ == '__main__':
	
	# gather inputs
	spcomp_parsed_inv_gdb = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - FRO\FRO2026\02InventoryCleanUp\ARI_wFU.gdb'
	boundary_fc = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\D\GeoData\PIAMMar2024.gdb\FMU_FN_PARK_Boundary_Simp2m'
	mu_list = ['FC035', 'FC060', 'FC110', 'FC120', 'FC130', 'FC140', 'FC175', 'FC177', 'FC210', 'FC220',
		'FC230', 'FC280', 'FC350', 'FC360', 'FC390', 'FC406', 'FC415', 'FC421', 'FC438', 'FC443',
		'FC451', 'FC490', 'FC535', 'FC574', 'FC601', 'FC615', 'FC644', 'FC680', 'FC702', 'FC754',
		'FC780', 'FC796', 'FC816', 'FC840', 'FC889', 'FC898', 'FC930', 'FC966', 'FC994',
		'FarNorth_BerensRiver', 'FarNorth_CatLake', 'FarNorth_ConstanceL', 'FarNorth_MooseCree',
		'FarNorth_NorthCentral', 'FarNorth_Northeast', 'FarNorth_Northwest', 'FarNorth_Taash',
		'Lake_Superior_Islands', 'Lake_Nipigon_Islands', 'Park_EagleSnowshoe', 'Park_LitGrRap',
		'Park_LkSuperior', 'Park_Quetico', 'Park_WCaribou', 'Park_Wabakimi', 'Park_pukaskwa']

	mu_list = ['FC930', 'FC966', 'FC994',
		'FarNorth_BerensRiver', 'FarNorth_CatLake', 'FarNorth_ConstanceL', 'FarNorth_MooseCree',
		'FarNorth_NorthCentral', 'FarNorth_Northeast', 'FarNorth_Northwest', 'FarNorth_Taash',
		'Lake_Superior_Islands', 'Lake_Nipigon_Islands', 'Park_EagleSnowshoe', 'Park_LitGrRap',
		'Park_LkSuperior', 'Park_Quetico', 'Park_WCaribou', 'Park_Wabakimi', 'Park_pukaskwa']

	field = ['SFU','LGFU','PFT'] # can pick multiples from ['SFU','LGFU','PFT']  eg. 'SFU;LGFU;PFT' NOTE: PFT and LGFU cannot be generated without SFU
	skip_eco_if_exists = True # skip populating values if ECONUM already exists


	######### logfile stuff

	tool_shortname = 'POPULATE_FU_BATCH' # the output logfile will include this text in its filename.

	# importing libraries (only works if arclog.py file is located on the parent folder of this script)
	from datetime import datetime
	parent_d = os.path.split(os.path.split(__file__)[0])[0]
	sys.path.append(parent_d)
	from arclog import Print2 as p2

	# find full path where the logfile will be written
	folder_path = arcpy.Describe(spcomp_parsed_inv_gdb).path
	while arcpy.Describe(folder_path).dataType != 'Folder':
		folder_path = os.path.split(folder_path)[0]
	outfile = os.path.split(spcomp_parsed_inv_gdb)[1] + '_' + tool_shortname + '-LOG_' + datetime.now().strftime('%Y%m%d_%H%M') + '.txt'
	logfile_path = os.path.join(folder_path,outfile)

	# importing arclog in the parent directory
	logger = p2(logfile_path)

	##########


	# run the main function in batch!
	arcpy.env.workspace = spcomp_parsed_inv_gdb
	for mu in mu_list:
		inputfc = mu
		logger.print2("\n\n######  Working on %s"%mu)
		# find SFU_REGION from boundary_fc
		region = []
		with arcpy.da.SearchCursor(boundary_fc, ["SFU_REGION"], where_clause="INV_NAME LIKE '%s'"%mu) as cursor:
			for row in cursor:
				region.append(row[0])
		if len(region) > 0:
			region = region[0]
			logger.print2("\nApplying Forest Unit SQL for %s"%region)
			populate_fu(inputfc,region,field,skip_eco_if_exists)
		else:
			logger.print2("!!!! Couldn't find the SFU Region for %s"%mu,'w')

	# finish writing the logfile
	logger.log_close()