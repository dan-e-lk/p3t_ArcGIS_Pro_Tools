# incomplete!!

# starting from ARAR (ideally run this right after running 01ARAR.py)
# 1. Simplify polygon using 5m, don't resolve errors, don't create points, set minimum area of 1ha. (rename it to Simp5m_HRV_All_02_n_up)
# 1a. Run simplify line for the road at 8m.
# 2. recalculate hectare field (km field for road)
# 3. Update the symbology by importing layer files located in C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\ARC
# 4. Run "Share As Web Layer" tool and save as .sd.


import arcpy
import os, csv
import pandas as pd


def ARAR_to_SD(input_arar, out_gdb):
	
	projfile = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"MNRLambert_d.prj")
	# housekeeping

	# Reference the current project and map
	aprx = arcpy.mp.ArcGISProject("CURRENT")
	map = aprx.activeMap

	# creating new feature data set in the output gdb
	DS_name = 'agol'
	arcpy.Delete_management(DS_name)
	arcpy.CreateFeatureDataset_management(out_gdb, DS_name, projfile)
	dest_feature_ds = os.path.join(out_gdb, DS_name)

	# these are FCs in ARAR to be simplified
	fc_list = ['EST_Y_02_n_up','HRV_All_02_n_up','Regen_All_02_n_up','SIP_All_02_n_up','Tend_All_02_n_up','Roads_All_06_n_up']
	# for testing only:
	fc_list = ['HRV_All_02_n_up','Roads_All_06_n_up']
	# fc_list = ['Roads_All_06_n_up']
	new_fc_list = []

	logger.print2("\n##### ### ##    SIMPLIFY    ## ### #####\n")

	arcpy.env.workspace = input_arar
	for fc in fc_list:
		logger.print2("\nSimplifying %s"%fc)
		if 'Roads' not in fc:
			out_fc_name = 'Simp5m_%s'%fc
			out_fc_path = os.path.join(dest_feature_ds,out_fc_name)
			arcpy.cartography.SimplifyPolygon(
				in_features=fc,
				out_feature_class=out_fc_path,
				algorithm="POINT_REMOVE",
				tolerance="5 Meters",
				minimum_area="10000 SquareMeters",
				error_option="NO_CHECK",
				collapsed_point_option="NO_KEEP",
				in_barriers=None)
			new_fc_list.append(out_fc_path)

		else:
			out_fc_name = 'Simp8m_%s'%fc
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

			logger.print2("Deleted Roads count: %s"%counter)
			logger.print2("Deleted Roads total Km: %s"%(meter/1000))

			# recalculating Km
			logger.print2("\nRecalculating Km...")
			arcpy.management.CalculateGeometryAttributes(fc, "Km LENGTH", length_unit="KILOMETERS", coordinate_system=projfile)

		else:
			logger.print2("\nRecalculating Hectare...")
			arcpy.management.CalculateGeometryAttributes(fc, "Hectares AREA", area_unit="HECTARES", coordinate_system=projfile)


	# apply layerfiles (first need to get the path to lyr folder, then match the fc name to the lyr file name to apply layers, then add to dataframe)



	# arcpy.MakeFeatureLayer_management(in_features = fc, out_layer = lyrname)
	# arcpy.ApplySymbologyFromLayer_management(in_layer = lyrname, in_symbology_layer = template_lyr)


	# Add the output feature class to the map
	# map.addDataFromPath(fc)










	# here are some lines I write all the time:
	# existingFields = [str(f.name).upper() for f in arcpy.ListFields(inputfc)]
	# oid_fieldname = arcpy.Describe(inputfc).OIDFieldName
	# count_orig = int(arcpy.management.GetCount(inputfc)[0])
	# arcpy.AddField_management(in_table = outputfc, field_name = check_field, field_type = "TEXT", field_length = "120")
	# arcpy.FeatureClassToFeatureClass_conversion(in_features=inputfc, out_path=os.path.split(outputfc)[0], out_name=os.path.split(outputfc)[1], where_clause=select_none_sql)
	# with arcpy.da.UpdateCursor(inputfc, existingFields) as cursor:
	# 	for row in cursor:
	# 		row[1] = 4
	# 		cursor.updateRow(row)	

	# # Make Layer, Select, and Calculate Field
	# arcpy.management.MakeFeatureLayer(inputfc, "temp_lyr")
	# arcpy.management.SelectLayerByAttribute("temp_lyr", "NEW_SELECTION", "")
	# num_selected = int(arcpy.management.GetCount("temp_lyr")[0])
	# arcpy.management.CalculateField("temp_lyr", fieldName, expression, code_block=code_block)


if __name__ == '__main__':
	
	# gather inputs
	input_arar = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\D\AR\AnalysisReadyAR.gdb'
	out_gdb = r'C:\Users\kimdan\OneDrive - Government of Ontario\_FPPS\Projects\AGOL_everything\AR\ARAR_simplified.gdb' # this gdb can be empty, but must already exist

	######### logfile stuff

	tool_shortname = 'ARAR2SD' # the output logfile will include this text in its filename.

	# importing libraries (only works if arclog.py file is located on the parent folder of this script)
	from datetime import datetime
	parent_d = os.path.split(os.path.split(__file__)[0])[0]
	sys.path.append(parent_d)
	from arclog import Print2 as p2

	# find full path where the logfile will be written
	folder_path = arcpy.Describe(input_arar).path
	while arcpy.Describe(folder_path).dataType != 'Folder':
		folder_path = os.path.split(folder_path)[0]
	outfile = tool_shortname + '-LOG_' + datetime.now().strftime('%Y%m%d_%H%M') + '.txt'
	logfile_path = os.path.join(folder_path,outfile)

	# importing arclog in the parent directory
	logger = p2(logfile_path)

	##########

	# run the main function(s)
	ARAR_to_SD(input_arar, out_gdb)

	# finish writing the logfile
	logger.log_close()