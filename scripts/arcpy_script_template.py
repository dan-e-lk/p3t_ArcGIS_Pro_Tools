# this is a template to build arcpy tools
# using this conveniently lets you create log txt file at the end of the script.
# this script should be on one folder level deeper than scripts folder. for example, "scripts/new_folder/this_script.py"  If this is not the case, the logger won't work.


import arcpy
import os, csv
import pandas as pd

arcpy.env.overwriteOutput = True
arcpy.env.XYTolerance = "0.01 Meters" # by default, it is 0.001 meters, which can generate 1mm-wide overlaps and gaps. So 0.01m is preferred.
projfile = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"MNRLambert_d.prj") # this works for all scripts that are one folder level deep. eg. scripts/sqlite/script.py

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

	# copy fc and rename
	arcpy.CopyFeatures_management(in_features=ARI_template,out_feature_class=new_fc_name)

	# replace existing DS
	arcpy.Delete_management(os.path.join(output_gdb,dsG)) # this will be ignored if the DS doesn't already exist.
	arcpy.CreateFeatureDataset_management(output_gdb, dsG, projfile)

	# append - will find and append only those fields that has the same fieldname - be careful of the field length difference
	app_out = arcpy.management.Append(inputs=last_mu_list[index], target=new_fc_name, schema_type="NO_TEST")
	append_count = int(app_out.getOutput("appended_row_count"))


	# make feature layer with only the join_include_field_list visible. (cause deleting them later takes way too long)
	fields= arcpy.ListFields(join_full_path)
	fieldinfo = arcpy.FieldInfo()
	for field in fields:
		if field.name.upper() in join_include_field_list:
			fieldinfo.addField(field.name, field.name, "VISIBLE", "NONE")
		else:
			fieldinfo.addField(field.name, field.name, "HIDDEN", "NONE")
	arcpy.management.MakeFeatureLayer(join_full_path, "join_lyr", field_info=fieldinfo)




if __name__ == '__main__':
	
	# gather inputs
	inputfc = arcpy.GetParameterAsText(0)

	######### logfile stuff

	tool_shortname = 'CaribouHab' # the output logfile will include this text in its filename.

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