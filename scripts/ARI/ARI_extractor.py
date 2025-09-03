# Complete!!
# You have ARI_base (or any other version of ARI). You want to grab a portion of it. 
# For example, you want to grab all NER Regional MUs. or you want to grab all GLSL SFU forests.
# or you want to grab just the OWNER = CROWN or POLYTYPE = FOR.
# Do this using this script

# ADD an option to make polyid unique again



import arcpy
import os, csv

arcpy.env.overwriteOutput = True
arcpy.env.XYTolerance = "0.01 Meters" # by default, it is 0.001 meters, which can generate 1mm-wide overlaps and gaps. So 0.01m is preferred.
projfile = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"MNRLambert_d.prj") # this works for all scripts that are one folder level deep. eg. scripts/sqlite/script.py


def ari_extractor(ari_gdb,boundary_fc,f_to_keep,repopulate_polyid,para):
	# eg of para = {'out_gdb': out_gdb, 'out_fc_name': 'ARI_3W','mu_sql': "LG_REGION = '3W'", 'fc_sql': "POLYTYPE='FOR'"}
	# unpack
	out_gdb = para['out_gdb']
	out_fc_name = para['out_fc_name']
	mu_sql = para['mu_sql']
	fc_sql = para['fc_sql']

	logger.print2("\n\n## ARI_EXTRACTOR - %s (%s)"%(out_fc_name,mu_sql))
	# use mu_sql to make a list of fc to append
	logger.print2("\nMaking a list of fc to append.")
	logger.print2("\nSelecting where %s"%mu_sql)
	mu_list = []
	with arcpy.da.SearchCursor(boundary_fc, ["INV_NAME"], where_clause=mu_sql) as cursor:
		for row in cursor:
			mu_list.append(row[0])
	logger.print2("\nMUs to append: %s"%mu_list)

	if len(mu_list) < 1:
		logger.print2("No INV_NAME found. Check your mu_sql (%s)"%mu_sql,'w')
		raise Exception("Check your mu_sql")

	arcpy.env.workspace = ari_gdb
	logger.print2("\nDeleting %s if exists"%out_fc_name)
	out_fc_path = os.path.join(out_gdb,out_fc_name)
	arcpy.Delete_management(out_fc_path)

	# copy & delete fields
	# ArcPro is too slow at deleting fields when it comes to large dataset - work around is to copy empty fc and delete fields, then append.
	logger.print2("\nCopying the data structure from %s"%os.path.split(ari_gdb)[1])
	oid_fieldname = arcpy.Describe(mu_list[0]).OIDFieldName
	select_none_sql = "%s<0"%oid_fieldname # "OBJECTID < 0" will select zero records
	# copy input to output - note that zero record are copied over. This will significantly speed up the AddField process
	arcpy.FeatureClassToFeatureClass_conversion(in_features=mu_list[0], out_path=os.path.split(out_fc_path)[0], out_name=os.path.split(out_fc_path)[1], where_clause=select_none_sql)
	# delete fields
	if f_to_keep != None:
		logger.print2("\nDeleting fields except the following:\n%s"%f_to_keep)
		arcpy.management.DeleteField(out_fc_path,f_to_keep, "KEEP_FIELDS")

	# append
	logger.print2("\nAppending...")
	for mu in mu_list:
		logger.print2("\tAppending %s to %s"%(mu, os.path.split(out_fc_path)[1]))
		logger.print2("\t\tSelected %s"%fc_sql)
		arcpy.MakeFeatureLayer_management(mu, "appendlayer1")
		if fc_sql != None and len(fc_sql) > 0:
			arcpy.SelectLayerByAttribute_management("appendlayer1", "NEW_SELECTION",fc_sql)
		app_out = arcpy.management.Append(inputs="appendlayer1", target=out_fc_path, schema_type="NO_TEST")
		append_count = int(app_out.getOutput("appended_row_count"))
		logger.print2("\t\tAppended %s records"%append_count)


	# repopulate POLYID
	if repopulate_polyid:
		fields = [str(f.name).upper() for f in arcpy.ListFields(out_fc_path)] # all the fields, uppercase
		if 'POLYID' in fields:
			logger.print2("\nRepopulating POLYID to make them unique again")
			f = ['OID@','POLYID']
			with arcpy.da.UpdateCursor(out_fc_path, f) as cursor:
				for row in cursor:
					new_polyid = row[0]
					row[1] = new_polyid
					cursor.updateRow(row)

	logger.print2("\nDone!")



if __name__ == '__main__':
	
	testing = True

	# gather inputs
	ari_gdb = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - FRO\FRO2026\02InventoryCleanUp\ARI_base.gdb' # output gdb must already exist and should contain feature classes in mu_list
	boundary_fc = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\D\GeoData\PIAMMar2024.gdb\FMU_FN_PARK_Boundary_Simp2m'
	# f_to_keep. Only these fields will be appended. if you want all fields, then put f_to_keep = None
	f_to_keep =['POLYID', 'POLYTYPE', 'OWNER', 'DEVSTAGE', 'YRDEP', 'DEPTYPE', 'PRI_ECO', 'YRORG', 'LEADSPC', 'SPCOMP', 'AGE', 'HT', 'CCLO', 'STKG', 'SC','VERT', 'MANAGED', 'PLANFU', 'AVAIL', 'SILVSYS', 'MUNO', 'ORG_OWNER']

	out_gdb = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - FRO\FRO2026\indicators\ARI_BY_LGRegion_ALL.gdb' # this will be the output fc

	# option to repopulate POLYID (to keep it unique)
	repopulate_polyid = True

	# batch run using input_para
	# mu_sql is run on boundary_fc to select fcs to append
	# fc_sql is run on each fc to select a subset of the record. IMPORTANT: fields in this sql should be on the of the fields in f_to_keep
	# keep_fields - only these fields will be kept in the end
	# input_para =[
	# {'out_gdb': out_gdb, 'out_fc_name': 'ARI_3W','mu_sql': "LG_REGION = '3W'", 'fc_sql': "POLYTYPE='FOR'"},
	# ]

	input_para =[
	{'out_gdb': out_gdb, 'out_fc_name': 'ARI_3W','mu_sql': "LG_REGION = '3W'", 'fc_sql': ""},
	{'out_gdb': out_gdb, 'out_fc_name': 'ARI_4W','mu_sql': "LG_REGION = '4W'", 'fc_sql': ""},
	{'out_gdb': out_gdb, 'out_fc_name': 'ARI_3S4S','mu_sql': "LG_REGION = '4S/3S'", 'fc_sql': ""},
	{'out_gdb': out_gdb, 'out_fc_name': 'ARI_3E','mu_sql': "LG_REGION = '3E'", 'fc_sql': ""},
	{'out_gdb': out_gdb, 'out_fc_name': 'ARI_4E5E','mu_sql': "LG_REGION in ('4E','5E')", 'fc_sql': ""},
	]
	

	######### logfile stuff

	tool_shortname = 'ARI_EXTRACTOR' # the output logfile will include this text in its filename.

	# importing libraries (only works if arclog.py file is located on the parent folder of this script)
	from datetime import datetime
	parent_d = os.path.split(os.path.split(__file__)[0])[0]
	sys.path.append(parent_d)
	from arclog import Print2 as p2
	import common_func

	# find full path where the logfile will be written
	folder_path = arcpy.Describe(out_gdb).path
	while arcpy.Describe(folder_path).dataType != 'Folder':
		folder_path = os.path.split(folder_path)[0]
	outfile = os.path.split(out_gdb)[1] + '_' + tool_shortname + '-LOG_' + datetime.now().strftime('%Y%m%d_%H%M') + '.txt'
	logfile_path = os.path.join(folder_path,outfile)

	# importing arclog in the parent directory
	logger = p2(logfile_path)

	##########

	# run the main function(s)
	for para in input_para:
		ari_extractor(ari_gdb,boundary_fc,f_to_keep,repopulate_polyid,para)

	# finish writing the logfile
	logger.log_close()





# ari_fields = ['OBJECTID', 'SHAPE', 'ARI_ID', 'POLYID', 'POLYTYPE', 'OWNER', 'YRSOURCE', 'SOURCE', 'FORMOD', 'DEVSTAGE', 'YRDEP', 'DEPTYPE', 'INCIDSPC', 'VERT', 'PRI_ECO', 'ACCESS1', 'MGMTCON1', 'YRORG', 'LEADSPC', 'SPCOMP', 'AGE', 'HT', 'CCLO', 'STKG', 'SC', 'MANAGED', 'SMZ', 'OMZ', 'PLANFU', 'AU', 'AVAIL', 'SILVSYS', 'NEXTSTG', 'YIELD', 'SGR', 'HA', 'STORY', 'MUNO', 'ORIG_FID', 'SHAPE_LENGTH', 'SHAPE_AREA', 'ORG_POLYID', 'ORG_OWNER']

# mu_list = ['FC035', 'FC060', 'FC110', 'FC120', 'FC130', 'FC140', 'FC175', 'FC177', 'FC210', 'FC220',
# 	'FC230', 'FC280', 'FC350', 'FC360', 'FC390', 'FC406', 'FC415', 'FC421', 'FC438', 'FC443',
# 	'FC451', 'FC490', 'FC535', 'FC574', 'FC601', 'FC615', 'FC644', 'FC680', 'FC702', 'FC754',
# 	'FC780', 'FC796', 'FC816', 'FC840', 'FC889', 'FC898', 'FC930', 'FC966', 'FC994',
# 	'FarNorth_BerensRiver', 'FarNorth_CatLake', 'FarNorth_ConstanceL', 'FarNorth_MooseCree',
# 	'FarNorth_NorthCentral', 'FarNorth_Northeast', 'FarNorth_Northwest', 'FarNorth_Taash',
# 	'Lake_Superior_Islands', 'Lake_Nipigon_Islands', 'Park_EagleSnowshoe', 'Park_LitGrRap',
# 	'Park_LkSuperior', 'Park_Quetico', 'Park_WCaribou', 'Park_Wabakimi', 'Park_pukaskwa']
