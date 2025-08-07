# Just started working on this...
# before writing this code, I first need to have a clean inventory with standard fields populated.


import arcpy
import os, csv
import pandas as pd

arcpy.env.overwriteOutput = True

def chc(inputfc):
	
	# loading csv to list of dictionary
	tbl_chc = 'habitat_classification.csv'
	parent_folder = os.path.split(__file__)[0]
	l_tbl_chc = list(csv.DictReader(open(os.path.join(parent_folder,tbl_chc))))
	logger.print2(tbl_chc)

	# loading csv to pandas dataframe
	tbl_plonski = 'tbl_plonski_metrics.csv'
	df = pd.read_csv(tbl_plonski, na_filter=False) # if you don't disable na_filter, then it will change 'NA' 'N/A','null' into 'nan'
	# https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html

	# see if a fc is polygon or polyline
	desc = arcpy.Describe(fc)
	shape = desc.shapeType # eg. Polyline, Polygon, etc.

	# here are some lines I write all the time:
	existingFields = [str(f.name).upper() for f in arcpy.ListFields(inputfc)]
	oid_fieldname = arcpy.Describe(inputfc).OIDFieldName
	count_orig = int(arcpy.management.GetCount(inputfc)[0])
	arcpy.AddField_management(in_table = outputfc, field_name = check_field, field_type = "TEXT", field_length = "120")
	arcpy.FeatureClassToFeatureClass_conversion(in_features=inputfc, out_path=os.path.split(outputfc)[0], out_name=os.path.split(outputfc)[1], where_clause=select_none_sql)
	with arcpy.da.UpdateCursor(inputfc, existingFields) as cursor:
		for row in cursor:
			row[1] = 4
			cursor.updateRow(row)	

	# Make Layer, Select, and Calculate Field
	arcpy.management.MakeFeatureLayer(inputfc, "temp_lyr")
	arcpy.management.SelectLayerByAttribute("temp_lyr", "NEW_SELECTION", "")
	num_selected = int(arcpy.management.GetCount("temp_lyr")[0])
	arcpy.management.CalculateField("temp_lyr", fieldName, expression, code_block=code_block)


if __name__ == '__main__':
	
	# gather inputs
	inputARAR = arcpy.GetParameterAsText(0) # path to existing AnalysisReadyAR database
	year_now = 2025 # used to re-calculate age
	AR_select_sql = {
	'HRV': "AR_YEAR >= 2010",
	'RGN': "AR_YEAR >= 2015",
	'EST': "AR_YEAR >= 2020"
	} # 
	ht_per_year = 0.3


	######### logfile stuff

	tool_shortname = 'ARAR2INV' # the output logfile will include this text in its filename.

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
	chc(inputfc)

	# finish writing the logfile
	logger.log_close()