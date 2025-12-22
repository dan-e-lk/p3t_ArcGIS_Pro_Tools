# Add WTX!!!

# this tool is used to update the ARAR on AGOL. When you have a new AR Master, use 01_AR_AR.py to create ARAR.gdb. 
# Then use this script to turn it into geopackage files which you can use to overwrite each of the ARAR layers already existing on AGOL
# why do this?  so I don't have to symbolize and custom label AGOL ARAR layers every time there's a new AR_Master.

# before running this tool, on your arcgis pro...
# Map Property - General - Check the box: 'Allow assignment of unique numeric IDs

# starting from ARAR (ideally run this right after running 01ARAR.py)
# 1. Simplify polygon using 5m, don't resolve errors, don't create points, set minimum area of 1ha. (rename it to Simp5m_HRV_All_02_n_up)
#    deleting anything below 0.2ha
# 1a. Run simplify line for the road at 8m.
# 2. recalculate hectare field (km field for road)
# 2a. delete roads that are shorter than 15m (for AGOL display speed/efficiency)
# 3. export to geopackage



import arcpy
import os, csv, traceback
import pandas as pd

arcpy.env.overwriteOutput = True
simp_poly_tol_m = 5
simp_poly_min_m2 = 2000 # anything less than this will be excluded
simp_line_tol_m = 8
simp_line_min_m = 15 # anything less than this will be excluded


def ARAR_to_gp(input_arar, out_gdb, gp_output_folder):
	
	projfile = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"MNRLambert_d.prj")
	# housekeeping

	# Reference the current project and map
	aprx = arcpy.mp.ArcGISProject("CURRENT")
	m = aprx.activeMap
	# these are FCs in ARAR to be simplified
	fc_list = {
	'EST_Y_02_n_up':'polygon',
	'HRV_All_02_n_up':'polygon',
	'Regen_All_02_n_up':'polygon',
	'SIP_All_02_n_up':'polygon',
	'Tend_All_02_n_up':'polygon',
	'SGR_flat_08_n_up':'polygon',
	'Roads_All_06_n_up':'polyline',
	'AGG_08_n_up':'point',
	'WTX_08_n_up':'point'}

	new_fc_list = []

	# creating new feature data set in the output gdb
	DS_name = 'agol'
	arcpy.Delete_management(DS_name)
	arcpy.CreateFeatureDataset_management(out_gdb, DS_name, projfile)
	dest_feature_ds = os.path.join(out_gdb, DS_name)

	logger.print2("\n##### ### ##    SIMPLIFY    ## ### #####\n")

	arcpy.env.workspace = input_arar
	for fc, fctype in fc_list.items():
		if fctype == 'polygon':
			logger.print2("\nSimplifying %s with %sm tolerance with minimum area of %sm2."%(fc,simp_poly_tol_m,simp_poly_min_m2))
			out_fc_name = 'Simplified_%s'%fc # if you chnage this, you have to also change the lyrx file name under lyr folder
			out_fc_path = os.path.join(dest_feature_ds,out_fc_name)
			arcpy.cartography.SimplifyPolygon(
				in_features=fc,
				out_feature_class=out_fc_path,
				algorithm="POINT_REMOVE",
				tolerance="%s Meters"%simp_poly_tol_m,
				minimum_area="%s SquareMeters"%simp_poly_min_m2, # deleting anything below 0.2ha to optimize the AGOL rendering
				error_option="NO_CHECK",
				collapsed_point_option="NO_KEEP",
				in_barriers=None)
			new_fc_list.append(out_fc_path)

		elif fctype == 'polyline':
			logger.print2("\nSimplifying %s with %sm tolerance."%(fc,simp_line_tol_m))
			out_fc_name = 'Simplified_%s'%fc # if you chnage this, you have to also change the lyrx file name under lyr folder
			out_fc_path = os.path.join(dest_feature_ds,out_fc_name)			
			arcpy.cartography.SimplifyLine(
				in_features=fc,
				out_feature_class=out_fc_path,
				algorithm="POINT_REMOVE",
				tolerance="%s Meters"%simp_line_tol_m,
				error_resolving_option="FLAG_ERRORS",
				collapsed_point_option="NO_KEEP",
				error_checking_option="NO_CHECK",
				in_barriers=None,
				error_option="NO_CHECK")
			new_fc_list.append(out_fc_path)

		else:
			logger.print2("\nCopying over %s..."%fc)
			arcpy.FeatureClassToFeatureClass_conversion(fc, dest_feature_ds, fc)
			new_fc_list.append(os.path.join(dest_feature_ds,fc))



	logger.print2("\n##### ### ##    Delete Fields & reCalc Ha&Km    ## ### #####\n")
	# delete unnecessary fields and recalculate "Hectares" or "Km"
	for fc in new_fc_list:
		logger.print2("\nWorking on %s"%fc)
		desc = arcpy.Describe(fc)
		shape = desc.shapeType # eg. Polyline, Polygon, etc.
		# delete MaxSimpTol and MinSimpTol and either InLine_FID or InPoly_FID
		if shape == 'Polyline':
			delete_fields = ['MaxSimpTol','MinSimpTol','InLine_FID']
			logger.print2("\nDeleting fields: %s"%delete_fields)
			arcpy.management.DeleteField(fc, delete_fields)			
		elif shape == 'Polygon':
			delete_fields = ['MaxSimpTol','MinSimpTol','InPoly_FID']
			logger.print2("\nDeleting fields: %s"%delete_fields)
			arcpy.management.DeleteField(fc, delete_fields)

		# recalculating Hactares or Km
		if shape == 'Polyline':
			# first deleting lines shorter than 15m (this will remove about 5%)
			logger.print2("\nDeleting roads shorter than %sm to optimize AGOL view..."%simp_line_min_m)
			counter = 0
			meter = 0
			with arcpy.da.UpdateCursor(fc, ["Shape_Length"], "Shape_Length < %s"%simp_line_min_m) as cursor:
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

		elif shape == 'Polygon':
			logger.print2("\nRecalculating Hectare...")
			arcpy.management.CalculateGeometryAttributes(fc, "Hectares AREA", area_unit="HECTARES", coordinate_system=projfile)
		else:
			pass


	logger.print2("\n##### ### ##    Export as GeoPackage   ## ### #####\n")

	# for debug only
	# logger.print2(str(new_fc_list))
	# new_fc_list = ['C:\\Users\\kimdan\\OneDrive - Government of Ontario\\_FPPS\\Projects\\AGOL_everything\\AR\\ARAR_simplified.gdb\\agol\\Simp5m_HRV_All_02_n_up', 'C:\\Users\\kimdan\\OneDrive - Government of Ontario\\_FPPS\\Projects\\AGOL_everything\\AR\\ARAR_simplified.gdb\\agol\\Simp8m_Roads_All_06_n_up']

	for fc in new_fc_list:
		# create GeoPackage File
		fc_name = os.path.split(fc)[1]
		gp_filename = "%s.gpkg"%fc_name # Simp5m_SIP_All_02_n_up.gpkg
		gp_fullpath = os.path.join(gp_output_folder,gp_filename)
		logger.print2("Creating geopackage: %s"%gp_filename)
		arcpy.management.CreateSQLiteDatabase(out_database_name=gp_fullpath,spatial_type="GEOPACKAGE")

		# exporting to geopackage
		logger.print2("\tExporting %s to geopackage"%fc_name)
		arcpy.conversion.ExportFeatures(in_features=fc,out_features=os.path.join(gp_fullpath,fc_name))

	# open the output folder when done.
	os.startfile(gp_output_folder)





if __name__ == '__main__':
	
	# gather inputs
	input_arar = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\D\AR\AnalysisReadyAR.gdb'
	out_gdb = r'C:\Users\KimDan\OneDrive - Government of Ontario\_FPPS\Projects\AGOL_everything\AR\ARAR_Simplified.gdb' # this gdb can be empty, but must already exist
	gp_output_folder = r'C:\Users\kimdan\OneDrive - Government of Ontario\_FPPS\Projects\AGOL_everything\AR\arar_to_gp_output'

	######### logfile stuff

	tool_shortname = 'ARAR2GPK' # the output logfile will include this text in its filename.

	# importing libraries (only works if arclog.py file is located on the parent folder of this script)
	from datetime import datetime
	parent_d = os.path.split(os.path.split(__file__)[0])[0]
	sys.path.append(parent_d)
	from arclog import Print2 as p2

	# find full path where the logfile will be written
	folder_path = gp_output_folder
	outfile = tool_shortname + '-LOG_' + datetime.now().strftime('%Y%m%d_%H%M') + '.txt'
	logfile_path = os.path.join(folder_path,outfile)

	# importing arclog in the parent directory
	logger = p2(logfile_path)

	##########

	# run the main function(s)
	ARAR_to_gp(input_arar, out_gdb, gp_output_folder)

	# finish writing the logfile
	logger.log_close()