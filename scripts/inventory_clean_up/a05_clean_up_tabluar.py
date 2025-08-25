# work in progress...
# this script is ideally run on inventories after 04_transplant_event_layer.py, but should be able to run on any existing inventories
#   as long as the feature classes are named the same way (eg. FC421, Lake_Superior_Islands, etc.) and mandatory fields exists.
#   mandatory fields are those in field_types dictionary of a02_standardize_using_template.py script


import arcpy
import os, csv
from a02_standardize_using_template import field_types as invfields_dict
invfields = list(invfields_dict.keys())

arcpy.env.overwriteOutput = True
arcpy.env.XYTolerance = "0.01 Meters" # by default, it is 0.001 meters, which can generate 1mm-wide overlaps and gaps. So 0.01m is preferred.
projfile = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"MNRLambert_d.prj") # this works for all scripts that are one folder level deep. eg. scripts/sqlite/script.py


def transplant_event_layer(event_lyr,clean02_inv_gdb,output_ARAR_gdb,mu_list,para,step_list):

	# parameters
	clean_inv_suffix = para['clean_inv_suffix']
	elim_select = para['elim_select']

	# step A
	step = 'a'
	ds = os.path.join(output_ARAR_gdb,step) # eg. .../AnalysisReadyInventory.gdb/a/
	a1_fc_suffix = "_%s1_intersect"%step
	a2_fc_suffix = "_%s2_dislv"%step
	a3_fc_suffix = "_%s3_elim"%step
	if 'A' in step_list:
		# select from event layer where INV_NAME = inventory fc name, then intersect
		# loop through NEO_ fields and populate values where needed
		# dissolve using invfields

		logger.print2("\n\n#########   Step A. Intersect, repopulate and dissolve  ##########\n")
		arcpy.env.workspace = clean02_inv_gdb
		logger.print2("Making a new Feature dataset: %s"%step)
		arcpy.Delete_management(os.path.join(output_ARAR_gdb,step))
		arcpy.CreateFeatureDataset_management(output_ARAR_gdb, step, projfile)

		for mu in mu_list:
			logger.print2("\nWorking on %s"%mu)
			mu_fcname = "%s%s"%(mu,clean_inv_suffix) # eg. FC421_g_standardfield
			out_fcname = "%s%s"%(mu,a1_fc_suffix) # eg. FC421_a_intersect
			out_fc_path = os.path.join(ds,out_fcname)

			# select from event layer where INV_NAME = inventory fc name, then intersect
			logger.print2("\tIntersecting with event layer")
			select_sql = "INV_NAME = '%s'"%mu
			logger.print2("\t\tSelecting where %s"%select_sql)
			arcpy.management.MakeFeatureLayer(event_lyr, "temp_lyr")
			arcpy.management.SelectLayerByAttribute("temp_lyr", "NEW_SELECTION", select_sql)




if __name__ == '__main__':
	
	# gather inputs
	event_lyr = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - FRO\FRO2026\02InventoryCleanUp\EventLayer.gdb\NEO4\NEO_fin' # path to cleaner 03 output feature class (NEO_fin)
	clean02_inv_gdb = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - FRO\FRO2026\02InventoryCleanUp\InvCleaner01_fin.gdb' # path to cleaner 02 output gdb
	output_ARAR_gdb = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - FRO\FRO2026\02InventoryCleanUp\Transplant_event.gdb' # output gdb must already exist.

	# mu_list values must be identical to the feature class names within PIAM.gdb (upper/lower case doesn't matter)
	mu_list = ['FC035', 'FC060', 'FC110', 'FC120', 'FC130', 'FC140', 'FC175', 'FC177', 'FC210', 'FC220',
			'FC230', 'FC280', 'FC350', 'FC360', 'FC390', 'FC406', 'FC415', 'FC421', 'FC438', 'FC443',
			'FC451', 'FC490', 'FC535', 'FC574', 'FC601', 'FC615', 'FC644', 'FC680', 'FC702', 'FC754',
			'FC780', 'FC796', 'FC816', 'FC840', 'FC889', 'FC898', 'FC930', 'FC966', 'FC994',
			'FarNorth_BerensRiver', 'FarNorth_CatLake', 'FarNorth_ConstanceL', 'FarNorth_MooseCree',
			'FarNorth_NorthCentral', 'FarNorth_Northeast', 'FarNorth_Northwest', 'FarNorth_Taash',
			'Lake_Superior_Islands', 'Lake_Nipigon_Islands', 'Park_EagleSnowshoe', 'Park_LitGrRap',
			'Park_LkSuperior', 'Park_Quetico', 'Park_WCaribou', 'Park_Wabakimi', 'Park_pukaskwa']
	# mu_list = ['Lake_Superior_Islands', 'Lake_Nipigon_Islands'] # testing

	para = {
	'clean_inv_suffix': '_g_standardfield', # this must match with the final fc name suffic of step G of 02_standardize_using_template.py
	'elim_select': "SHAPE_AREA < 100 OR (POLYTYPE='FOR' AND SHAPE_AREA < 400)", 
	}

	step_list = 'ALL'
	# step_list = ['B','C']

	if step_list == 'ALL':
		step_list = ['A','B','C']


	######### logfile stuff

	tool_shortname = 'CleanUp_Tabular' # the output logfile will include this text in its filename.

	# importing libraries (only works if arclog.py file is located on the parent folder of this script)
	from datetime import datetime
	parent_d = os.path.split(os.path.split(__file__)[0])[0]
	sys.path.append(parent_d)
	from arclog import Print2 as p2
	import common_func

	# find full path where the logfile will be written
	folder_path = arcpy.Describe(output_ARAR_gdb).path
	while arcpy.Describe(folder_path).dataType != 'Folder':
		folder_path = os.path.split(folder_path)[0]
	outfile = os.path.split(output_ARAR_gdb)[1] + '_' + tool_shortname + '-LOG_' + datetime.now().strftime('%Y%m%d_%H%M') + '.txt'
	logfile_path = os.path.join(folder_path,outfile)

	# importing arclog in the parent directory
	logger = p2(logfile_path)

	##########

	# run the main function(s)
	transplant_event_layer(event_lyr,clean02_inv_gdb,output_ARAR_gdb,mu_list,para,step_list)

	# finish writing the logfile
	logger.log_close()