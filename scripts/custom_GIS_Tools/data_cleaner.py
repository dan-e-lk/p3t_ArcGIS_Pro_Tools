# Originally scripted to clean SPCOMP95
# Can be used to clean any polygon feature class
# This is not designed to be a comprehensive cleaner tool for a particular inventory, but it is designed to be used on almost any polygon data, and deisgned to be batch run if needed.
# The users should modify the eliminate tool selection sql to fit their needs

# Workflow:
# 1. Export to a new MNR Lambert dataset thereby reprojecting it to MNR Lambert
# 2. Repair Geometry
# 3. Multipart to Singlepart
# 3-1. Optional - delete extra small polygons.
# 4. SimplifyPolygon
# 5. Eliminate - 3 times, sequentially
# 6. Final output

# The final output will have the same name as the original input with suffix '_clean'. This was done to make the batch run easy.


import arcpy
import os

arcpy.env.overwriteOutput = True
arcpy.env.XYTolerance = "0.01 Meters" # by default, it is 0.001 meters, which can generate 1mm-wide overlaps and gaps. So 0.01m is preferred.
projfile = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"MNRLambert_d.prj") # this works for all scripts that are one folder level deep. eg. scripts/sqlite/script.py

def cleaner(inputfc,output_gdb,delete_XS_poly,simp_tolerance,silver_sql1,silver_sql2,silver_sql3,delete_temp):

	input_val = [inputfc,output_gdb,delete_XS_poly,simp_tolerance,silver_sql1,silver_sql2,silver_sql3,delete_temp]
	logger.print2("\n\n#################     Polygon Cleaner    ###################\n\nInputs: %s"%input_val)

	# check inputs
	simp_tolerance = int(simp_tolerance)
	if simp_tolerance < 1 or simp_tolerance > 30:
		logger.print2("INVALID simplify polygon tolerance value.\n\tValue entered: %s"%simp_tolerance,'warning')

	orig_fcname = os.path.split(inputfc)[1]
	logger.print2("\nWorking on %s"%orig_fcname)
	temp_ds_name = 'temp'
	logger.print2("Making a temporary dataset")
	arcpy.Delete_management(os.path.join(output_gdb,temp_ds_name))
	arcpy.CreateFeatureDataset_management(output_gdb, temp_ds_name, projfile)
	temp_fd = os.path.join(output_gdb, temp_ds_name)

	# copy over - to correct projection
	logger.print2("\nCopying the input over to the new dataset, thereby reprojecting it to MNR Lambert...")
	out_fcname = orig_fcname + '_01RepairGeom'
	out_fcpath = os.path.join(temp_fd,out_fcname)
	arcpy.CopyFeatures_management(in_features=inputfc,out_feature_class=out_fcpath)

	# Repair geom
	logger.print2("\nRepairing Geometry...")
	arcpy.management.RepairGeometry(in_features=out_fcpath,delete_null="DELETE_NULL",validation_method="OGC")

	# Multipart to Singlepart
	logger.print2("\nRunning Multipart to Single Part...")
	in_fcpath = out_fcpath
	out_fcname = orig_fcname + '_02Multi2Single'
	out_fcpath = os.path.join(temp_fd,out_fcname)
	arcpy.management.MultipartToSinglepart(in_features=in_fcpath,out_feature_class=out_fcpath)

	# Delete extra-small polygons
	if delete_XS_poly != None:
		logger.print2("\nDeleting polygons less than %s sqm..."%delete_XS_poly)
		XS_sql = "SHAPE_AREA < %s"%delete_XS_poly 
		orig_count = int(arcpy.GetCount_management(out_fcpath)[0])
		arcpy.MakeFeatureLayer_management(out_fcpath, "templayer")
		arcpy.SelectLayerByAttribute_management("templayer","NEW_SELECTION",XS_sql)
		select_count = int(arcpy.GetCount_management("templayer")[0])
		logger.print2("\tDeleting %s out of %s records."%(select_count,orig_count))
		arcpy.management.DeleteFeatures("templayer")

	# Simplify Polygon
	logger.print2("\nRunning Simplify Polygon (Point Remove @ %sm tolerance)..."%simp_tolerance)
	in_fcpath = out_fcpath
	out_fcname = orig_fcname + '_03SimplifyPoly'
	out_fcpath = os.path.join(temp_fd,out_fcname)
	arcpy.cartography.SimplifyPolygon(
		in_features=in_fcpath,
		out_feature_class=out_fcpath,
		algorithm="POINT_REMOVE",
		tolerance="%s Meters"%simp_tolerance,
		error_option="NO_CHECK", # error_option="NO_CHECK" is faster than "RESOLVE_ERRORS" and should still be okay as long as repair geometry later
		collapsed_point_option="NO_KEEP")
	# delete unnecessary fields
	logger.print2("\tDeleting unwanted fields created by simplify polygon tool")
	to_delete = ['ORIG_FID','InPoly_FID','MaxSimpTol','MinSimpTol']
	arcpy.management.DeleteField(out_fcpath,to_delete)

	# Repair geom
	logger.print2("\nRepairing Geometry...")
	arcpy.management.RepairGeometry(in_features=out_fcpath,delete_null="DELETE_NULL",validation_method="OGC")

	# Sequential Eliminate (eliminate a number of times)
	logger.print2("\nRunning Eliminate...")
	# 1st run (mandatory)
	in_fcpath = out_fcpath
	out_fcname = orig_fcname + '_04Elim1'
	out_fcpath = os.path.join(temp_fd,out_fcname)
	out_fcpath = eliminator(in_fcpath,out_fcpath,silver_sql1)
	# 2nd run (optional)
	if silver_sql2 != None:
		in_fcpath = out_fcpath
		out_fcname = orig_fcname + '_04Elim2'
		out_fcpath = os.path.join(temp_fd,out_fcname)
		out_fcpath = eliminator(in_fcpath,out_fcpath,silver_sql2)		
	# 3rd run (optional)
	if silver_sql3 != None:
		in_fcpath = out_fcpath
		out_fcname = orig_fcname + '_04Elim3'
		out_fcpath = os.path.join(temp_fd,out_fcname)
		out_fcpath = eliminator(in_fcpath,out_fcpath,silver_sql3)


	# Export the final output
	in_fcpath = out_fcpath
	out_fcname = orig_fcname + '_clean'
	out_fcpath = os.path.join(output_gdb,out_fcname)
	logger.print2("\nExporting the final output feature class: %s"%out_fcname)
	arcpy.CopyFeatures_management(in_features=in_fcpath,out_feature_class=out_fcpath)

	# run repair geo again just for good measure
	logger.print2("\nRepairing Geometry...")
	arcpy.management.RepairGeometry(in_features=out_fcpath,delete_null="DELETE_NULL",validation_method="OGC")

	if delete_temp:
		logger.print2("\nDeleting the temporary dataset")
		arcpy.Delete_management(os.path.join(output_gdb,temp_ds_name))

	logger.print2("\nDone!!!!\nHere are other things you could also do:\n\tDissolve, RemoveDuplicates, Find and remove self intersects...")




def eliminator(in_fcpath, out_fcpath, elim_select_sql):
	# runs eliminate tool if the sql query selected non-zero records.
	# also reports number of records eliminated.
	logger.print2("\tRunning Eliminate on %s (merge to largest area)"%os.path.split(in_fcpath)[1])
	logger.print2("\t\tSelect SQL: %s"%elim_select_sql)
	orig_count = int(arcpy.GetCount_management(in_fcpath)[0])
	arcpy.MakeFeatureLayer_management(in_fcpath, "elimlayer1")
	arcpy.SelectLayerByAttribute_management("elimlayer1", "NEW_SELECTION",elim_select_sql)
	select_count = int(arcpy.GetCount_management("elimlayer1")[0])
	if select_count > 0:
		logger.print2("\t\tSelected %s records"%select_count)
		arcpy.management.Eliminate(in_features="elimlayer1",out_feature_class=out_fcpath,selection="AREA",ex_where_clause="")
		new_count = int(arcpy.GetCount_management(out_fcpath)[0])
		elim_percent = round((((orig_count - new_count) / orig_count) * 100),2)
		logger.print2("\t\tEliminated %s of %s (%s%%)"%(orig_count - new_count,orig_count,elim_percent))
	else:
		logger.print2("\t\tThe SQL selected zero record. Nothing to eliminate.")
		out_fcpath = in_fcpath
	return out_fcpath




if __name__ == '__main__':
	
	# gather inputs
	inputfc = arcpy.GetParameterAsText(0) # feature class or feature layer
	output_gdb = arcpy.GetParameterAsText(1)
	delete_XS_poly = arcpy.GetParameterAsText(2) # area in m2 of the polygons that you want to just delete (not eliminate). default = 0.1
	delete_XS_poly = None if delete_XS_poly == '' else float(delete_XS_poly)

	simp_tolerance = arcpy.GetParameterAsText(3) # must be whole number, cannot be left blank. eg. 2

	silver_sql1 = arcpy.GetParameterAsText(4) # eg. "Shape_Area < 100"
	silver_sql2 = arcpy.GetParameterAsText(5) # Optional. eg. "Shape_Area < 500"
	silver_sql2 = None if silver_sql2 == '' else silver_sql2
	silver_sql3 = arcpy.GetParameterAsText(6) # Optional. eg. "Shape_Area < 5000 AND (4 * 3.14159265 * Shape_Area) / (Shape_Length * Shape_Length) < 0.1"
	silver_sql3 = None if silver_sql3 == '' else silver_sql3

	delete_temp = arcpy.GetParameterAsText(7) # 'true' or 'false'
	delete_temp = True if delete_temp == 'true' else False


	######### logfile stuff

	tool_shortname = 'DataCleaner' # the output logfile will include this text in its filename.

	# importing libraries (only works if arclog.py file is located on the parent folder of this script)
	from datetime import datetime
	parent_d = os.path.split(os.path.split(__file__)[0])[0]
	sys.path.append(parent_d)
	from arclog import Print2 as p2

	# find full path where the logfile will be written
	folder_path = arcpy.Describe(output_gdb).path
	while arcpy.Describe(folder_path).dataType != 'Folder':
		folder_path = os.path.split(folder_path)[0]
	outfile = os.path.split(output_gdb)[1] + '_' + tool_shortname + '-LOG_' + datetime.now().strftime('%Y%m%d_%H%M') + '.txt'
	logfile_path = os.path.join(folder_path,outfile)

	# importing arclog in the parent directory
	logger = p2(logfile_path)

	##########

	# run the main function(s)
	cleaner(inputfc,output_gdb,delete_XS_poly,simp_tolerance,silver_sql1,silver_sql2,silver_sql3,delete_temp)

	# finish writing the logfile
	logger.log_close()