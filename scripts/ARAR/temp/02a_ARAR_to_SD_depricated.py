# This tool is depricated because exporting the files to sd file doesn't work out very well.
# instead, use ARAR to geopackage.

# this tool is used to update the ARAR on AGOL. When you have a new AR Master, use 01_AR_AR.py to create ARAR.gdb. 
# Then use this script to turn it into .sd file which you can use to overwrite each of the ARAR layers already existing on AGOL
# why do this?  so I don't have to symbolize and custom label AGOL ARAR layers every time there's a new AR_Master.

# before running this tool, on your arcgis pro...
# Map Property - General - Check the box: 'Allow assignment of unique numeric IDs

# starting from ARAR (ideally run this right after running 01ARAR.py)
# 1. Simplify polygon using 5m, don't resolve errors, don't create points, set minimum area of 1ha. (rename it to Simp5m_HRV_All_02_n_up)
# 1a. Run simplify line for the road at 8m.
# 2. recalculate hectare field (km field for road)
# 2a. delete roads that are shorter than 15m (for AGOL display speed/efficiency)
# 3. Export and save as .sd.


import arcpy
import os, csv, traceback
import pandas as pd

arcpy.env.overwriteOutput = True


def ARAR_to_SD(input_arar, out_gdb, sd_output_folder):
	
	projfile = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"MNRLambert_d.prj")
	# housekeeping

	# Reference the current project and map
	aprx = arcpy.mp.ArcGISProject("CURRENT")
	m = aprx.activeMap

	# these are FCs in ARAR to be simplified
	fc_list = ['EST_Y_02_n_up','HRV_All_02_n_up','Regen_All_02_n_up','SIP_All_02_n_up','Tend_All_02_n_up','Roads_All_06_n_up']
	# for testing only:
	# fc_list = ['HRV_All_02_n_up','Roads_All_06_n_up']
	# fc_list = ['EST_Y_02_n_up']
	new_fc_list = []

	# creating new feature data set in the output gdb
	DS_name = 'agol'
	arcpy.Delete_management(DS_name)
	arcpy.CreateFeatureDataset_management(out_gdb, DS_name, projfile)
	dest_feature_ds = os.path.join(out_gdb, DS_name)

	logger.print2("\n##### ### ##    SIMPLIFY    ## ### #####\n")

	arcpy.env.workspace = input_arar
	for fc in fc_list:
		logger.print2("\nSimplifying %s"%fc)
		if 'Roads' not in fc:
			out_fc_name = 'Simp5m_%s'%fc # if you chnage this, you have to also change the lyrx file name under lyr folder
			out_fc_path = os.path.join(dest_feature_ds,out_fc_name)
			arcpy.cartography.SimplifyPolygon(
				in_features=fc,
				out_feature_class=out_fc_path,
				algorithm="POINT_REMOVE",
				tolerance="5 Meters",
				minimum_area="2000 SquareMeters", # deleting anything below 0.2ha to optimize the AGOL rendering
				error_option="NO_CHECK",
				collapsed_point_option="NO_KEEP",
				in_barriers=None)
			new_fc_list.append(out_fc_path)

		else:
			out_fc_name = 'Simp8m_%s'%fc # if you chnage this, you have to also change the lyrx file name under lyr folder
			out_fc_path = os.path.join(dest_feature_ds,out_fc_name)			
			arcpy.cartography.SimplifyLine(
				in_features=fc,
				out_feature_class=out_fc_path,
				algorithm="POINT_REMOVE",
				tolerance="8 Meters",
				error_resolving_option="FLAG_ERRORS",
				collapsed_point_option="NO_KEEP",
				error_checking_option="NO_CHECK",
				in_barriers=None,
				error_option="NO_CHECK")
			new_fc_list.append(out_fc_path)


	logger.print2("\n##### ### ##    Delete Fields & reCalc Ha&Km    ## ### #####\n")
	# delete unnecessary fields and recalculate "Hectares" or "Km"
	for fc in new_fc_list:
		logger.print2("\nWorking on %s"%fc)
		desc = arcpy.Describe(fc)
		shape = desc.shapeType # eg. Polyline, Polygon, etc.
		# delete MaxSimpTol and MinSimpTol and either InLine_FID or InPoly_FID
		if shape == 'Polyline':
			delete_fields = ['MaxSimpTol','MinSimpTol','InLine_FID']
		else:
			delete_fields = ['MaxSimpTol','MinSimpTol','InPoly_FID']
		logger.print2("\nDeleting fields: %s"%delete_fields)
		arcpy.management.DeleteField(fc, delete_fields)

		# recalculating Hactares or Km
		if shape == 'Polyline':
			# first deleting lines shorter than 15m (this will remove about 5%)
			logger.print2("\nDeleting roads shorter than 15m to optimize AGOL view...")
			counter = 0
			meter = 0
			with arcpy.da.UpdateCursor(fc, ["Shape_Length"], "Shape_Length < 15") as cursor:
				for row in cursor:
					counter += 1
					meter += row[0]
					cursor.deleteRow()

			total_km = meter/1000
			logger.print2("Deleted Roads count: %s"%counter)
			logger.print2("Deleted Roads total Km: %s"%total_km)

			# recalculating Km
			logger.print2("\nRecalculating Km...")
			arcpy.management.CalculateGeometryAttributes(fc, "Km LENGTH", length_unit="KILOMETERS", coordinate_system=projfile)

		else:
			logger.print2("\nRecalculating Hectare...")
			arcpy.management.CalculateGeometryAttributes(fc, "Hectares AREA", area_unit="HECTARES", coordinate_system=projfile)


	logger.print2("\n##### ### ##    Export as SD file    ## ### #####\n")

	# for debug only
	# logger.print2(str(new_fc_list))
	# new_fc_list = ['C:\\Users\\kimdan\\OneDrive - Government of Ontario\\_FPPS\\Projects\\AGOL_everything\\AR\\ARAR_simplified.gdb\\agol\\Simp5m_HRV_All_02_n_up', 'C:\\Users\\kimdan\\OneDrive - Government of Ontario\\_FPPS\\Projects\\AGOL_everything\\AR\\ARAR_simplified.gdb\\agol\\Simp8m_Roads_All_06_n_up']

	for fc in new_fc_list:
		# add the fc to the map
		fc_name = os.path.split(fc)[1]
		logger.print2("\nAdding %s to the active ArcGIS map"%fc_name)
		m.addDataFromPath(fc)

		# https://pro.arcgis.com/en/pro-app/latest/arcpy/sharing/featuresharingdraft-class.htm
		service_name = fc_name
		outdir = sd_output_folder
		sddraft_filename = service_name + ".sddraft"
		sddraft_output_filename = os.path.join(outdir, sddraft_filename)
		sd_filename = service_name + ".sd"
		sd_output_filename = os.path.join(outdir, sd_filename)

		# # select layer
		selected_layer = m.listLayers(fc_name)[0]

		# export as sddraft file then export as sd file
		logger.print2("Running Get Web Layer Sharing Draft")
		server_type = "HOSTING_SERVER"
		sddraft = m.getWebLayerSharingDraft(server_type, "FEATURE", service_name,[selected_layer])
		sddraft.overwriteExistingService = True

		# Create Service Definition Draft file
		logger.print2("Exporting %s to .sddraft file"%fc_name)
		sddraft.exportToSDDraft(sddraft_output_filename)

		# Stage Service
		try:
			logger.print2("Exporting %s to .sd file"%fc_name)
			arcpy.server.StageService(sddraft_output_filename, sd_output_filename) # your ArcGIS Map property must have 
		except:
			var = traceback.format_exc()
			arcpy.AddWarning(var)
			arcpy.AddWarning("\n\nIf you are getting ERROR 001272 Analyzer Error, then open Map Property - General - Check the box: 'Allow assignment of unique numeric IDs' \n\n")
			arcpy.AddWarning("Also make sure you don't already have the layers with the same name (eg. Simp5m_HRV_All_02_n_up) on Contents pane.")

	# open the output folder when done.
	os.startfile(outdir)





if __name__ == '__main__':
	
	# gather inputs
	input_arar = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\D\AR\AnalysisReadyAR.gdb'
	out_gdb = r'C:\Users\kimdan\OneDrive - Government of Ontario\_FPPS\Projects\AGOL_everything\AR\ARAR_simplified2.gdb' # this gdb can be empty, but must already exist
	sd_output_folder = r'C:\Users\kimdan\OneDrive - Government of Ontario\_FPPS\Projects\AGOL_everything\AR\arar_to_sd_output'

	######### logfile stuff

	tool_shortname = 'ARAR2SD' # the output logfile will include this text in its filename.

	# importing libraries (only works if arclog.py file is located on the parent folder of this script)
	from datetime import datetime
	parent_d = os.path.split(os.path.split(__file__)[0])[0]
	sys.path.append(parent_d)
	from arclog import Print2 as p2

	# find full path where the logfile will be written
	folder_path = sd_output_folder
	outfile = tool_shortname + '-LOG_' + datetime.now().strftime('%Y%m%d_%H%M') + '.txt'
	logfile_path = os.path.join(folder_path,outfile)

	# importing arclog in the parent directory
	logger = p2(logfile_path)

	##########

	# run the main function(s)
	ARAR_to_SD(input_arar, out_gdb, sd_output_folder)

	# finish writing the logfile
	logger.log_close()