# prerequisite:
# Must already have run 02 create base hex per MU - must already have a gdb that contains layers such as f_443_base


# workflow:
# - loop through the mu_list


import arcpy
import os

arcpy.env.overwriteOutput = True
arcpy.env.XYTolerance = "0.01 Meters" # by default, it is 0.001 meters, which can generate 1mm-wide overlaps and gaps. So 0.01m is preferred.
projfile = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"MNRLambert_d.prj") # this works for all scripts that are one folder level deep. eg. scripts/sqlite/script.py

def hexagonizer(hex_base_gdb,out_gdb,join_info,mu_list):

	arcpy.env.workspace = hex_base_gdb

	# loop through mu
	logger.print2("List of MUs:\n%s"%mu_list)
	logger.print2("List of joining fcs:\n%s"%join_info.keys())
	logger.print2("\nLooping through each MU")
	for mu in mu_list:
		muno_txt = mu[2:] # eg. when mu = 'FC040', then muno_txt = '040'
		logger.print2("\n- Working on %s"%mu)

		# make a new feature dataset with MNR Lambert Conformal Conic Projection
		DS_name = 'f_%s'%muno_txt
		logger.print2(" -- Generating dataset: %s..."%DS_name)
		# find the projection file location
		projfile = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"MNRLambert_d.prj")
		if not os.path.isfile(projfile):
			# if the file doesn't exist, show error
			arcpy.AddError("Can't find MNRLambert_d.prj file at the parent folder of %s"%__file__)
			raise
		arcpy.Delete_management(DS_name)
		arcpy.CreateFeatureDataset_management(out_gdb, DS_name, projfile)

		# loop through the join_info dictionary
		for layer_type, info in join_info.items():
			join_full_path = info[0]
			join_sql = info[1]
			join_exclude_field_list = info[2]
			output_suffix = info[3]
			logger.print2(" -- joining %s"%layer_type)

			# turn the joining fc into a layer
			arcpy.management.MakeFeatureLayer(join_full_path, "join_lyr")
			if join_sql != None:
				logger.print2("\tSelect from %s WHERE %s"%(layer_type,join_sql))
				arcpy.management.SelectLayerByAttribute("join_lyr", "NEW_SELECTION", join_sql)
				num_selected = int(arcpy.management.GetCount("join_lyr")[0])
				logger.print2("\t%s records selected"%num_selected)

			# run spatial join
			target_fc = 'f_%s_base'%muno_txt # eg. f_443_base found in hex_base_gdb
			out_fc_name = 'f_%s_%s'%(muno_txt,output_suffix)
			out_fc_fullpath = os.path.join(out_gdb,DS_name,out_fc_name)
			logger.print2("\tRunning Spatial Join. out_fc_name = %s"%out_fc_name)
			arcpy.analysis.SpatialJoin(target_features=target_fc, join_features="join_lyr", out_feature_class=out_fc_fullpath, join_operation="JOIN_ONE_TO_ONE", join_type="KEEP_COMMON", match_option="HAVE_THEIR_CENTER_IN")

			# delete extra fields
			# always delete these fields
			delete_field_lst = ['JOIN_COUNT','TARGET_FID','SHAPE_LENGTH_1','SHAPE_AREA_1']
			# add user-specified delete fields
			if join_exclude_field_list != None:
				for f in join_exclude_field_list:
					if f.upper() not in delete_field_lst:
						delete_field_lst.append(f)
			logger.print2("\tDeleting fields: %s"%delete_field_lst)
			arcpy.management.DeleteField(out_fc_fullpath, delete_field_lst)





		# # turn hex grid into a layer then select by location using neo_lyr
		# arcpy.management.MakeFeatureLayer(hex_fc_name, "hex_lyr")
		# sql = Neofin_select_sql + " AND INV_NAME = '%s'"%mu
		# logger.print2("\tSelect by location: where hex grid have center in event polygons from the selected NEO_FIN")
		# arcpy.management.SelectLayerByLocation(in_layer="hex_lyr", overlap_type="HAVE_THEIR_CENTER_IN", select_features='neo_lyr', search_distance=None, selection_type="NEW_SELECTION")
		# num_selected = int(arcpy.management.GetCount("hex_lyr")[0])
		# logger.print2("\t%s records selected"%num_selected)

		# # exporting the selected hex grid to out_gdb
		# base_hex_fc_name = hex_fc_name + '_base'
		# logger.print2("\tExporting the selected hex grid as %s"%base_hex_fc_name)
		# base_hex_fullpath = os.path.join(out_gdb, DS_name, base_hex_fc_name)
		# arcpy.conversion.ExportFeatures("hex_lyr",base_hex_fullpath)

	logger.print2("\nDone!")




if __name__ == '__main__':
	
	# gather inputs
	hex_base_gdb = r'C:\Users\KimDan\Government of Ontario\Caribou Explorer - CM1_3\Data\Analysis\Hexagon_Test\HexBase.gdb' # will have layers such as 'f_443' and 'f_816'
	out_gdb = r'C:\Users\KimDan\Government of Ontario\Caribou Explorer - CM1_3\Data\Analysis\Hexagon_Test\HexJoin.gdb' # must already exist

	neofin_path = r'C:\Users\KimDan\Government of Ontario\Caribou Explorer - CM1_3\Data\Analysis\EventLayers\Event2002to2023.gdb\NEO4\NEO_fin'
	hrv_path = r'C:\Users\KimDan\Government of Ontario\Forest Explorer - Data\D\AR\AnalysisReadyAR.gdb\Harvest\HRV_All_02_n_up'

	join_info = {
	# layer alias | path to join layer | sql select | delete these fields | output fc suffix
	'EventLayer': 	[neofin_path, None, None, 'event'],
	'Harvest':		[hrv_path, None, ['HRVNO'], 'hrv'],
	}


	mu_list = ['FC035', 'FC060', 'FC110', 'FC120', 'FC130', 'FC140', 'FC175', 'FC177', 'FC210', 'FC220',
			'FC230', 'FC280', 'FC350', 'FC360', 'FC390', 'FC406', 'FC415', 'FC421', 'FC438', 'FC443',
			'FC451', 'FC490', 'FC535', 'FC574', 'FC601', 'FC615', 'FC644', 'FC680', 'FC702', 'FC754',
			'FC780', 'FC796', 'FC816', 'FC840', 'FC889', 'FC898', 'FC930', 'FC966', 'FC994'] # 39 MUs
	mu_list = ['FC443','FC816']



	######### logfile stuff

	tool_shortname = 'CM13_03_hexagonize_all' # the output logfile will include this text in its filename.

	# importing libraries (only works if arclog.py file is located on the parent folder of this script)
	from datetime import datetime
	parent_d = os.path.split(os.path.split(__file__)[0])[0]
	sys.path.append(parent_d)
	from arclog import Print2 as p2

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
	hexagonizer(hex_base_gdb,out_gdb,join_info,mu_list)

	# finish writing the logfile
	logger.log_close()