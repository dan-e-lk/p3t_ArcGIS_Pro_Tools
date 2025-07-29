# This cleans up the existing inventory of the gaps, self-intersects, duplicates and polygons outside MU boundary, 
# BUT doesn't actually edit the original inventory itself.

# NEED TO ADD Single to Multi at some point


# Steps:
# 	1. Run Multipart to Singlpart - then simplify 2m
# 	2. self intersect to find overlaps
# 		a. All overlaps will be used to erase the original inventory. 
# 		b. small overlaps (< 1ha) will be erased and be left as a hole for now. (don't do this)
# 		c. Large overlaps (>1ha) will be erased but will be replaced by one of the duplicate polygons (whichever polygon that has larger objectid - because it's usually the latest update)
# 	3. erase the inventory from the MU boundary layer (will use this step for flagging only. won't use it to fix the fc)
# 		a. the output will be all the hole polygons
#			Probably need to run Multi to single
# 		b. append all the holes back into the inventory
# 		c. select small holes (<5ha), then run eliminate to merge these small hole polygons with neighboring polygons.
# 		d. Any hole polygons larger than 5ha will be assigned POLYTYPE of 'GAP'. These can be looked at in the future.
# Clip the inventory using the MU boundary to clip off any edges that lies outside of the MU boundary.



import arcpy
import os, csv
import pandas as pd

arcpy.env.overwriteOutput = True
global projfile
projfile = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"MNRLambert_d.prj")

def find_all_fcs(gdb_path):
	# returns the names and full paths of all fcs inside a gdb, including ones inside datasets
	import os, arcpy
	arcpy.env.workspace = gdb_path

	# List feature classes in the root of the GDB
	all_feature_classes = arcpy.ListFeatureClasses()
	fc_names_only = all_feature_classes

	# List feature datasets
	fds_list = arcpy.ListDatasets(feature_type='feature')

	# Loop through each feature dataset and list its feature classes
	if fds_list:
		for fds in fds_list:
			fds_path = f"{gdb_path}\\{fds}"
			arcpy.env.workspace = fds_path
			fcs_in_fds = arcpy.ListFeatureClasses()
			for fc in fcs_in_fds:
				fc_names_only.append(fc)
				all_feature_classes.append(os.path.join(fds,fc)) # eg. 'INV\fc421'

	# Print all feature class names
	fc_fullpath = [os.path.join(gdb_path,i).upper() for i in all_feature_classes] # a list of full path of all fcs
	fc_names_only = [i.upper() for i in fc_names_only] # a list of names of all fcs.

	return [fc_names_only, fc_fullpath]



def clean_inv(original_inv_gdb,output_gdb,boundary_fc,para,mu_list,step_list):
	
	# check all inputs
	arcpy.env.workspace = original_inv_gdb
	# make sure all the MUs in mu_list exists
	mu_list = [i.upper() for i in mu_list]
	input_fcs = find_all_fcs(original_inv_gdb)[0] # a list of names of all fcs in uppercase
	not_found = [mu for mu in mu_list if mu not in input_fcs]
	if len(not_found) > 0:
		err1 = "\n!!! The following MUs in your list are not found in the input gdb:\n%s"%not_found
		logger.print2(err1,'warning')
		raise Exception(err1)
	# check boundary_fc
	if not arcpy.Exists(boundary_fc):
		err2 = "\n!!! the boundary_fc doesn't exist! Check this path:\n%s"%boundary_fc
		raise Exception(err2)

	# step/dataset names (this is handy when one of the steps fail and you don't want to start from the beginning)
	dsA = 'a_Multi2Single'
	dsB = 'b_Simplify'
	dsC = 'c_Intersect'
	dsD = 'd_Erase_n_append'
	dsE = 'e_Eliminate'
	dsF = 'f_clip_to_mu'

	# names of all fcs to be generated
	stepA_fcs = {mu:"%s_%s"%(mu,dsA) for mu in mu_list} # eg. {"FC421": "FC421_a_Multi2Single",...}
	stepB_fcs = {mu:"%s_%s"%(mu,dsB) for mu in mu_list}
	stepC_fcs = {mu:"%s_%s"%(mu,dsC) for mu in mu_list}
	stepD_fcs = {mu:"%s_%s"%(mu,dsD) for mu in mu_list}
	stepE_fcs = {mu:"%s_%s"%(mu,dsE) for mu in mu_list}
	stepF_fcs = {mu:"%s_%s"%(mu,dsF) for mu in mu_list}

	# Part A
	if 'A' in step_list:
		logger.print2("\n\n#########     A. Multipart to Single Part     ##########\n")
		logger.print2("Making a new Feature dataset: %s"%dsA)
		arcpy.Delete_management(os.path.join(output_gdb,dsA))
		arcpy.CreateFeatureDataset_management(output_gdb, dsA, projfile)
		dest_fd = os.path.join(output_gdb, dsA)
		for mu in mu_list:
			new_fc_name = os.path.join(dest_fd,stepA_fcs[mu]) # eg. ...gdb/a_Mutil2Single/FC421_a_Multi2Single
			logger.print2("Running Multipart to Single Part on %s"%mu)
			arcpy.management.MultipartToSinglepart(in_features=mu,out_feature_class=new_fc_name)
			logger.print2("\tDone!!")
	# at the end of A, you get inventory without any multiparts

	# change the main environment
	arcpy.env.workspace = output_gdb

	# Part B
	if 'B' in step_list:
		simp_tol = para['simp_tolerance'] # eg. '2 Meters'

		logger.print2("\n\n#########     B. Simplify Polygon (%s)     ##########\n"%simp_tol)
		logger.print2("Making a new Feature dataset: %s"%dsB)
		arcpy.Delete_management(os.path.join(output_gdb,dsB))
		arcpy.CreateFeatureDataset_management(output_gdb, dsB, projfile)
		dest_fd = os.path.join(output_gdb, dsB)

		for mu in mu_list:
			logger.print2("Running Simplify Polygon on %s"%mu)
			new_fc_name = os.path.join(dest_fd,stepB_fcs[mu])
			arcpy.cartography.SimplifyPolygon(
				in_features=stepA_fcs[mu],
				out_feature_class=new_fc_name,
				algorithm="POINT_REMOVE",
				tolerance=simp_tol,
				error_option="RESOLVE_ERRORS",
				collapsed_point_option="NO_KEEP")
			# delete unwanted fields created by simplify polygon tool
			logger.print2("\tDeleting unwanted fields created by simplify polygon tool")
			to_delete = ['ORIG_FID','InPoly_FID','SimPgnFlag','MaxSimpTol','MinSimpTol']
			arcpy.management.DeleteField(new_fc_name,to_delete)

			logger.print2("\tDone!!")
	# at the end of B, you get simplified inventory

	# Part C
	if 'C' in step_list:
		logger.print2("\n\n#########   C. Self-Intersect and Delete Identical   ##########\n")
		logger.print2("Making a new Feature dataset: %s"%dsC)
		arcpy.Delete_management(os.path.join(output_gdb,dsC))
		arcpy.CreateFeatureDataset_management(output_gdb, dsC, projfile)
		dest_fd = os.path.join(output_gdb, dsC)

		for mu in mu_list:
			new_fc_name = os.path.join(dest_fd,stepC_fcs[mu])
			logger.print2("\nRunning Intersect on %s"%mu)
			# arcpy.analysis.PairwiseIntersect(in_features=stepB_fcs[mu], out_feature_class=new_fc_name, join_attributes="ALL", cluster_tolerance=None, output_type="INPUT") # this kept failing (read-only issue)
			arcpy.analysis.Intersect(in_features=stepB_fcs[mu],out_feature_class=new_fc_name,join_attributes="ALL",cluster_tolerance=None,output_type="INPUT")

			# this creates a new field that we don't want.
			to_delete = ["FID_%s"%stepB_fcs[mu]]
			logger.print2("\tDeleting unwanted field created by intersect tool: %s"%to_delete)
			arcpy.management.DeleteField(new_fc_name,to_delete)

			logger.print2("\tDone!!")
			# delete identical (keeping the first record only)
			logger.print2("Running Delete Identical tool")
			arcpy.management.DeleteIdentical(in_dataset=new_fc_name,fields="Shape")
			logger.print2("\tDone!!")

			# analyze the intersects
			count = int(arcpy.GetCount_management(new_fc_name)[0])
			logger.print2("\tNumber of self-intersects: %s"%count)
			if count > 0:
				area_list = []
				with arcpy.da.SearchCursor(new_fc_name, ["OID@", "SHAPE@AREA"]) as cursor:
					for row in cursor:
						area = row[1]
						area_list.append(area)

				count_over_1ha = len([val for val in area_list if val >= 10000])
				count_over_20ha = len([val for val in area_list if val >= 200000])
				avg_area = round(((sum(area_list)/len(area_list))/10000),3)
				logger.print2("\tNumber of self-intersects over 1ha: %s"%count_over_1ha)
				logger.print2("\tNumber of self-intersects over 20ha: %s"%count_over_20ha)
				logger.print2("\tAverage area of self-intersects: %s ha"%avg_area)

	# at the end of C, you get only the self-intersect of that inventory. The duplicates are deleted from the self intersects.

	# Part D
	if 'D' in step_list:

		logger.print2("\n\n#########     D. Erase and Append     ##########\n")
		logger.print2("Making a new Feature dataset: %s"%dsD)
		arcpy.Delete_management(os.path.join(output_gdb,dsD))
		arcpy.CreateFeatureDataset_management(output_gdb, dsD, projfile)
		dest_fd = os.path.join(output_gdb, dsD)

		for mu in mu_list:
			new_fc_name = os.path.join(dest_fd,stepD_fcs[mu])
			logger.print2("Running Erase on %s"%mu)
			arcpy.analysis.PairwiseErase(in_features=stepB_fcs[mu],erase_features=stepC_fcs[mu],out_feature_class=new_fc_name)
			logger.print2("\tDone!!")
			logger.print2("Running Append on %s"%mu)
			arcpy.management.Append(inputs=stepC_fcs[mu],target=stepD_fcs[mu],schema_type="TEST",field_mapping=None)
			logger.print2("\tDone!!")

	
	# Part E eliminate small polys
	if 'E' in step_list:
		logger.print2("\n\n#########     E. Eliminate small polygons     ##########\n")
		elim_select_sql = para['elim_select']
		logger.print2("Elimination selection SQL:\n%s"%elim_select_sql)
		logger.print2("\nMaking a new Feature dataset: %s"%dsE)
		arcpy.Delete_management(os.path.join(output_gdb,dsE))
		arcpy.CreateFeatureDataset_management(output_gdb, dsE, projfile)
		dest_fd = os.path.join(output_gdb, dsE)

		for mu in mu_list:
			new_fc_name = os.path.join(dest_fd,stepE_fcs[mu])
			logger.print2("Running Eliminate on %s"%mu)
			orig_count = int(arcpy.GetCount_management(stepD_fcs[mu])[0])
			arcpy.MakeFeatureLayer_management(stepD_fcs[mu], "elimlayer1")
			arcpy.SelectLayerByAttribute_management("elimlayer1", "NEW_SELECTION",elim_select_sql)
			arcpy.management.Eliminate(in_features="elimlayer1",out_feature_class=new_fc_name,selection="AREA",ex_where_clause="")
			new_count = int(arcpy.GetCount_management(new_fc_name)[0])
			elim_percent = round((((orig_count - new_count) / orig_count) * 100),2)
			logger.print2("\tEliminated %s of %s (%s%%)"%(orig_count - new_count,orig_count,elim_percent))
			logger.print2("\tDone!!")


	logger.print2("\n\nNOTE that the following 'clip to MU boundary' step can be skipped. \
All it does is clipping the FCs from part E to the corresponding MU boundary.\n")

	# Part F - Clip to MU boundary
	if 'F' in step_list:
		logger.print2("\n\n#########      F. Clip to MU Boundary      ##########\n")
		logger.print2("\nMaking a new Feature dataset: %s"%dsF)
		arcpy.Delete_management(os.path.join(output_gdb,dsF))
		arcpy.CreateFeatureDataset_management(output_gdb, dsF, projfile)
		dest_fd = os.path.join(output_gdb, dsF)

		arcpy.MakeFeatureLayer_management(boundary_fc, "clip_boundary")

		for mu in mu_list:
			new_fc_name = os.path.join(dest_fd,stepF_fcs[mu])
			logger.print2("Clipping %s"%mu)
			select_sql = "UPPER(INV_NAME) LIKE '%s'"%mu.upper()
			logger.print2("\t Selecting WHERE %s"%select_sql)
			arcpy.SelectLayerByAttribute_management("clip_boundary", "NEW_SELECTION",select_sql)
			arcpy.analysis.PairwiseClip(in_features=stepE_fcs[mu],clip_features="clip_boundary",out_feature_class=new_fc_name,cluster_tolerance=None)
			logger.print2("\tDone!!")

			# repopulate HA field
			logger.print2("\tRepopulating Ha field...")
			# create Ha field if not exist
			existingFields = [str(f.name).upper() for f in arcpy.ListFields(new_fc_name)]
			if 'HA' not in existingFields:
				arcpy.AddField_management(in_table = new_fc_name, field_name = 'HA', field_type = "FLOAT")
			# calculate hectare
			with arcpy.da.UpdateCursor(new_fc_name, ["SHAPE@AREA", 'HA']) as cursor:
				for row in cursor:
					area_in_ha = round(row[0]/10000,4)
					row[1] = area_in_ha
					cursor.updateRow(row)
			logger.print2("\tDone!!")

	# open the output folder when done.
	os.startfile(os.path.split(output_gdb)[0])


if __name__ == '__main__':
	
	# gather inputs
	# inputfc = arcpy.GetParameterAsText(0)
	original_inv_gdb = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\D\GeoData\PIAMMar2024.gdb'# eg. PIAM (this tool doesn't alter this input)
	output_gdb = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - FRO\FRO2026\02InventoryCleanUp\InvCleaner01.gdb' # must already exist - will be overwritten
	boundary_fc = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\D\GeoData\PIAMMar2024.gdb\FMU_FN_PARK_Boundary_Simp2m' # Only used in Part F. FMU, FN, Park boundary layer. Should have INV_NAME field
	
	para = {
	'simp_tolerance': '2 Meters',
	'elim_select': "SHAPE_AREA < 500 OR (POLYTYPE='FOR' AND SHAPE_AREA < 1000)"
	}
	mu_list = ['fc421'] # this must be identical to the feature class names within PIAM.gdb (upper/lower case doesn't matter)
	mu_list = [
	'FC035', 'FC060', 'FC110', 'FC120', 'FC130', 'FC140', 'FC175', 'FC177', 'FC210', 'FC220',
	'FC230', 'FC280', 'FC350', 'FC360', 'FC390', 'FC406', 'FC415', 'FC421', 'FC438', 'FC443',
	'FC451', 'FC490', 'FC535', 'FC574', 'FC601', 'FC615', 'FC644', 'FC680', 'FC702', 'FC754',
	'FC780', 'FC796', 'FC816', 'FC840', 'FC889', 'FC898', 'FC930', 'FC966', 'FC994',
	'FarNorth_BerensRiver', 'FarNorth_CatLake', 'FarNorth_ConstanceL', 'FarNorth_MooseCree',
	'FarNorth_NorthCentral', 'FarNorth_Northeast', 'FarNorth_Northwest', 'FarNorth_Taash',
	'Lake Superior_Islands', 'Lake_Nipigon_Islands', 'Park_EagleSnowshoe', 'Park_LitGrRap',
	'Park_LkSuperior', 'Park_Quetico', 'Park_WCaribou', 'Park_Wabakimi', 'Park_pukaskwa']

	step_list = ['A','B','C','D','E','F'] # Unless you are debugging the tool, all the steps should be run. 
	# step_list = ['F'] # Unless you are debugging the tool, all the steps should be run. 
	# when debugging, if the tool failed at step C, you can start from step C by deletling A and B from the list.


	######### logfile stuff

	tool_shortname = 'INV_CLEANER_01' # the output logfile will include this text in its filename.

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
	clean_inv(original_inv_gdb,output_gdb,boundary_fc,para,mu_list,step_list)

	# finish writing the logfile
	logger.log_close()