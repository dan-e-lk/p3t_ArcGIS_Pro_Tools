# Make event layer out of NatDist_MT_LatestOnly and Analysis-Ready AR

# NatDist event layer:

prefix = 'NEO_'
neofields = {
	# fieldname | field type | length 		
	'YRSOURCE':	['SHORT'],
	'SOURCE':	['TEXT',	16],
	'YRDEP':	['SHORT'],
	'DEPTYPE':	['TEXT',	16],
	'DEVSTAGE':	['TEXT',	16],
	'STKG':		['FLOAT'],
	'YRORG':	['SHORT'],
	'AGE':		['SHORT'],
	'HT':		['FLOAT'],
	'CCLO':		['SHORT'],
	'SILVSYS':	['TEXT',	4],
	'SPCOMP':	['TEXT',	120],
	'PLANFU':	['TEXT',	30],
	'YIELD':	['TEXT',	20],
	'SGR':		['TEXT',	50],
	'LEADSPC':	['TEXT',	3],
}

# only used for nat dist to select and calculate field for NEO_DEPTYPE field
sql_deptype = {
	'BLOWDOWN': " NATDID = 'BLDN' ",
	'DISEASE':	" SOURCE = 'Disease' ",
	'DROUGHT': " NATDID = 'DROT' ",
	'FIRE': " SOURCE = 'FIRE' ",
	'FLOOD': " NATDID = 'FLOD' ",
	'ICE': " NATDID = 'ICED' ",
	'INSECTS': " SOURCE in ('Budworm','FTCT','OthPest') ",
	'SNOW': " NATDID = 'SNOW' "}


import arcpy
import os, csv
import pandas as pd

arcpy.env.overwriteOutput = True
arcpy.env.XYTolerance = "0.01 Meters" # by default, it is 0.001 meters, which can generate 1mm-wide overlaps and gaps. So 0.01m is preferred.
projfile = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"MNRLambert_d.prj") # this works for all scripts that are one folder level deep. eg. scripts/sqlite/script.py


def make_event_layer(in_arar_gdb, in_natdist_gdb, out_event_gdb, time_range, year_now, ht_per_year):
	
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
	in_arar_gdb = r''
	in_natdist_gdb = r''
	out_event_gdb = r''
	time_range = {
	'HRV': "AR_YEAR >= 2015",
	'RGN': "AR_YEAR >= 2010", # only affects devstage. without RGN, we can't figure out if devstage is ESTNAT or ESTPLANT
	'EST': "AR_YEAR >= 2020",
	'NATDIST': "YEAR >= 2020",
	} # 
	year_now = 2025 # used to re-calculate age
	para = {
	'ht_per_year': 0.3,
	'simplify_meters': 2,
	'eliminate_sqm': 500,
	}
	step_list = ['AR1']


	######### logfile stuff

	tool_shortname = 'Make_Event_Layer' # the output logfile will include this text in its filename.

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
	make_event_layer(in_arar_gdb, in_natdist_gdb, out_event_gdb, time_range, year_now, ht_per_year)

	# finish writing the logfile
	logger.log_close()