# prerequisite:
# You have the latest Analysis-Ready AR.
# Must have the hex grid for each MU. (run custom_GIS_Tools/generate_hex_for_each_polygon.py)
# H3 Hex at resolution 11 for each MU is available here: C:\Users\KimDan\Government of Ontario\Forest Explorer - Packaged_Data\Hexagon_H3\Hex_by_FMU


# workflow:
# - loop through the mu_list
# - from ARAR's HRV, select all records.
# - from hex grid, select the grid of the mu and using select by location, select the grids where it intersects (have their center in) the selected ar_hrv polygons
# - export the selected hex grid polygons - now we have the base grid!


import arcpy
import os

arcpy.env.overwriteOutput = True
arcpy.env.XYTolerance = "0.01 Meters" # by default, it is 0.001 meters, which can generate 1mm-wide overlaps and gaps. So 0.01m is preferred.
projfile = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"MNRLambert_d.prj") # this works for all scripts that are one folder level deep. eg. scripts/sqlite/script.py

def make_hex_base(hrv_path,hrv_select_sql,hex_grid_gdb,out_gdb,mu_list):

	# make a new feature dataset with MNR Lambert Conformal Conic Projection
	DS_name = "hex_base"
	logger.print2("Generating dataset: %s..."%DS_name)
	# find the projection file location
	projfile = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"MNRLambert_d.prj")
	if not os.path.isfile(projfile):
		# if the file doesn't exist, show error
		arcpy.AddError("Can't find MNRLambert_d.prj file at the parent folder of %s"%__file__)
		raise
	arcpy.Delete_management(DS_name)
	arcpy.CreateFeatureDataset_management(out_gdb, DS_name, projfile)
	logger.print2("Dataset successfully generated!")


	arcpy.env.workspace = hex_grid_gdb

	# loop through mu
	logger.print2("\nLooping through each MU")
	for mu in mu_list:
		muno_txt = mu
		muno_int = int(mu)
		hex_fc_name = 'f_%s'%muno_txt
		logger.print2("- Working on %s"%mu)

		# turn ar_hrv into a layer - then select.
		arcpy.management.MakeFeatureLayer(hrv_path, "hrv_lyr")
		sql = hrv_select_sql + " AND MUNO = %s"%muno_int
		logger.print2("\tSelect from ar_hrv WHERE %s"%(sql))
		arcpy.management.SelectLayerByAttribute("hrv_lyr", "NEW_SELECTION", sql)
		num_selected = int(arcpy.management.GetCount("hrv_lyr")[0])
		logger.print2("\t%s records selected"%num_selected)

		# turn hex grid into a layer then select by location using hrv_lyr
		arcpy.management.MakeFeatureLayer(hex_fc_name, "hex_lyr")
		logger.print2("\tSelect by location: where hex grid have center in event polygons from the selected ar_hrv")
		arcpy.management.SelectLayerByLocation(in_layer="hex_lyr", overlap_type="HAVE_THEIR_CENTER_IN", select_features='hrv_lyr', search_distance=None, selection_type="NEW_SELECTION")
		num_selected = int(arcpy.management.GetCount("hex_lyr")[0])
		logger.print2("\t%s records selected"%num_selected)

		# exporting the selected hex grid to out_gdb
		base_hex_fc_name = hex_fc_name + '_base'
		logger.print2("\tExporting the selected hex grid as %s"%base_hex_fc_name)
		base_hex_fullpath = os.path.join(out_gdb, DS_name, base_hex_fc_name)
		arcpy.conversion.ExportFeatures("hex_lyr",base_hex_fullpath)

	logger.print2("\nDone!\nYou now have hexagon grid of all the harvest polygons.\nReady to run the next script!")




if __name__ == '__main__':
	
	# gather inputs
	hrv_path = r'C:\Users\KimDan\Government of Ontario\Forest Explorer - Data\D\AR\AnalysisReadyAR.gdb\Harvest\HRV_All_02_n_up'
	hrv_select_sql = """ HARVCAT <> 'ROADROW' AND HARVMTHD <> 'THINCOM' AND SILVSYS = 'CC' """ # this is the base sql for SOA-CC 
	hex_grid_gdb = r'C:\Users\KimDan\Government of Ontario\Forest Explorer - Packaged_Data\Hexagon_H3\Hex_by_FMU\FMU_at11.gdb' 
	out_gdb = r"C:\Users\KimDan\Government of Ontario\Forest Explorer - Data\E\SOA2\SOA_CC\Hexbase_CC.gdb" # must already exist.

	mu_list = [
		'035', '060', '110', '120', '130', '140', '175', '177', '210', '220',
		'230', '280', '350', '360', '390', '406', '415', '421', '438', '443',
		'451', '490', '535', '574', '601', '615', '644', '680', '702', '754',
		'780', '796', '816', '840', '889', '898', '930', '966', '994'] # 39 MUs # Takes 23 mins to run 39MUs 

	
	# test run
	# mu_list = ['035','210','930']



	######### logfile stuff

	tool_shortname = 'SOA2_01_baseHex' # the output logfile will include this text in its filename.

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
	make_hex_base(hrv_path,hrv_select_sql,hex_grid_gdb,out_gdb,mu_list)

	# finish writing the logfile
	logger.log_close()