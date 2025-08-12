# you can run this any time when you have NatDist.gdb. You don't have to run other clean-up tools before you run this one.
# this script merges all nat dist polygons into one and creates a new fc called 'NatDist_All' - aka analysis-ready NatDist

# Natural Disturbance roll-up has a number of polygon feature classes and they share common fields:
common_fields = ['NATDID','YEAR','DAMAGE','HA']

# The goal of this script is to append all the following natural disturbance layers into a single feature class (and save it in the same database)
orig_ds = 'Damage' # dataset name
append_base = "Budworm" # copy this to the new dataset and append the following to this append_base
to_be_appended = ['Disease','FIRE','FTCT','OthPest','Weather']


import arcpy
import os

arcpy.env.overwriteOutput = True
arcpy.env.XYTolerance = "0.01 Meters"
projfile = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"MNRLambert_d.prj")

def analysis_ready_NatDist(input_gdb,step_list):

	new_ds = 'All'
	new_ds_full = os.path.join(input_gdb,new_ds)
	append_base_full = os.path.join(input_gdb,orig_ds,append_base)
	append_lst = [os.path.join(input_gdb,orig_ds,i) for i in to_be_appended]
	new_fc = 'NatDist_AllPoly'
	new_fc_full = os.path.join(new_ds_full,new_fc)


	if 'A' in step_list:

		logger.print2("\n\n#########    A. Appending all Nat Dist layers   ##########\n")
		# generate new, or replace existing dataset named 'All'
		logger.print2("\nGenerating a new dataset: %s"%new_ds)
		arcpy.Delete_management(new_ds_full)
		arcpy.CreateFeatureDataset_management(input_gdb, new_ds, projfile)

		# Order of things:
		# copy append_base_full and paste/rename it to new_fc_full (count number of records)
		# create a new field - 'SOURCE' and populate it with 'Budworm'
		# loop through append_lst - append - then select where SOURCE IS NULL and populate it with the source layer name
		# count append numbers and catch errors.

		# copy append_base_full and paste/rename it to new_fc_full (count number of records)
		counter = {natdist:0 for natdist in to_be_appended} # eg. {'FIRE':0, 'Disease':0, ...}
		logger.print2("\nCopying and renaming the %s to %s"%(append_base,new_fc))
		arcpy.CopyFeatures_management(in_features=append_base_full,out_feature_class=new_fc_full)
		count_orig = int(arcpy.management.GetCount(new_fc_full)[0])
		counter[append_base] = count_orig # eg. {'Budworm': 105292, 'FIRE':0, 'Disease':0, ...}

		# create a new field - 'SOURCE' and populate it with 'Budworm'
		source_field = 'SOURCE'
		logger.print2("\nCreating a new field: %s"%source_field)
		arcpy.AddField_management(in_table = new_fc_full, field_name = source_field, field_type = "TEXT", field_length = "25")
		logger.print2("\tPopulating %s with '%s'"%(source_field,append_base))
		with arcpy.da.UpdateCursor(new_fc_full, [source_field]) as cursor:
			for row in cursor:
				row[0] = append_base
				cursor.updateRow(row)

		# loop through append_lst - append - then select where SOURCE IS NULL and populate it with the source layer name
		for index, fc in enumerate(append_lst):
			source = to_be_appended[index] # eg. Disease
			logger.print2("\nAppending %s to %s"%(source,new_fc))

			# append
			app_out = arcpy.management.Append(inputs=fc, target=new_fc_full, schema_type="NO_TEST")
			append_count = int(app_out.getOutput("appended_row_count"))
			counter[source] = append_count
			logger.print2("\t%s records appended"%append_count)

			# select where SOURCE IS NULL and populate it with the source layer name, for example 'Disease'
			logger.print2("\tPopulating %s with '%s'"%(source_field,source))
			arcpy.management.MakeFeatureLayer(new_fc_full, "temp_lyr")
			sql = "%s IS NULL"%source_field
			arcpy.management.SelectLayerByAttribute("temp_lyr", "NEW_SELECTION", sql)
			num_selected = int(arcpy.management.GetCount("temp_lyr")[0])
			# count append numbers and catch errors.
			if num_selected != append_count:
				raise Exception("appended %s records but only %s records where %s"%(append_count,num_selected,sql))
			arcpy.management.CalculateField("temp_lyr", source_field, "'%s'"%source)


		# report summary of record counts
		logger.print2("\nAll Done!\nHere's the summary of number of appended records:")
		for natd, count in counter.items():
			logger.print2("\n%s: %s"%(natd,count))



	if 'B' in step_list:
		logger.print2("\n\n#########     B. Latest Mortality-level Only     ##########\n")
		
		dsTemp = 'Temp'
		dsTemp_full = os.path.join(input_gdb,dsTemp)

		# work on temporary dataset
		logger.print2("\nGenerating a new dataset: %s"%dsTemp)
		arcpy.Delete_management(dsTemp_full)
		arcpy.CreateFeatureDataset_management(input_gdb, dsTemp, projfile)

		# select where DAMAGE = 'MT' and copy over
		expr = "DAMAGE = 'MT'"
		temp01 = os.path.join(dsTemp_full,'t1_MT')
		logger.print2("\tSelecting where %s and copying over to the Temp dataset"%expr)
		arcpy.conversion.ExportFeatures(new_fc_full, temp01, expr) # arcgis pro 3.3 and above

		# self-intersect
		logger.print2("\tSelf-intersecting %s"%os.path.split(temp01)[1])
		temp02 = os.path.join(dsTemp_full,'t2_intersect')
		arcpy.analysis.Intersect(in_features=[temp01],out_feature_class=temp02,join_attributes="ALL",cluster_tolerance=None,output_type="INPUT")

		# sort and delete identical
		logger.print2("\tSorting %s by Year (descending)"%os.path.split(temp02)[1])
		temp03 = os.path.join(dsTemp_full,'t3_sort_n_deleteIdentical')
		arcpy.management.Sort(in_dataset=temp02,out_dataset=temp03,sort_field="Year DESCENDING")

		logger.print2("\tDeleting Identical Shapes on %s"%os.path.split(temp03)[1])
		arcpy.management.DeleteIdentical(in_dataset=temp03,fields="Shape",xy_tolerance=None,z_tolerance=0)

		# erase temp03 from temp01
		temp04 = os.path.join(dsTemp_full,'t4_replace')
		logger.print2("\tErasing %s from %s"%(os.path.split(temp03)[1], os.path.split(temp01)[1]))
		arcpy.analysis.PairwiseErase(in_features=temp01,erase_features=temp03,out_feature_class=temp04)

		# append temp03 to temp04
		logger.print2("\tAppending %s to %s"%(os.path.split(temp03)[1], os.path.split(temp04)[1]))
		app_out = arcpy.management.Append(inputs=temp03, target=temp04, schema_type="NO_TEST")
		append_count = int(app_out.getOutput("appended_row_count"))
		logger.print2("\t\tAppended %s records"%append_count)

		# dissolve
		logger.print2("\tDissolving %s"%os.path.split(temp04)[1])
		temp05 = os.path.join(dsTemp_full,'t5_dislv')
		arcpy.management.Dissolve(in_features=temp04,out_feature_class=temp05,dissolve_field="Damage;SOURCE;NatDID;Year",multi_part="SINGLE_PART")		

		# eliminate - final step, so create a new dataset
		dsB = 'MT_flat_latest'
		dsB_full = os.path.join(input_gdb,dsB)
		min_area = 5000 #m2
		logger.print2("\nGenerating a new dataset: %s"%dsB)
		arcpy.Delete_management(dsB_full)
		arcpy.CreateFeatureDataset_management(input_gdb, dsB, projfile)

		out_fc = os.path.join(dsB_full,"NatDist_MT_LatestOnly")
		logger.print2("\tRunning Eliminate (<%sm2)"%min_area)
		orig_count = int(arcpy.GetCount_management(temp05)[0])
		arcpy.MakeFeatureLayer_management(temp05, "elimlayer1")
		arcpy.SelectLayerByAttribute_management("elimlayer1", "NEW_SELECTION","SHAPE_AREA < %s"%min_area)
		arcpy.management.Eliminate(in_features="elimlayer1",out_feature_class=out_fc,selection="LENGTH")
		new_count = int(arcpy.GetCount_management(out_fc)[0])
		elim_percent = round((((orig_count - new_count) / orig_count) * 100),2)
		logger.print2("\t\tEliminated %s of %s (%s%%)"%(orig_count - new_count,orig_count,elim_percent))
		logger.print2("\tDone!!")



		# If not debug - delete the temporarly workspace
		logger.print2("\n\nCleaning up temporary dataset...")
		arcpy.Delete_management(dsTemp_full)
		logger.print2("\tDone!!")





if __name__ == '__main__':
	
	# gather inputs
	input_gdb = arcpy.GetParameterAsText(0)
	step_list = ['A','B'] # 
	# step_list = ['B']

	######### logfile stuff

	tool_shortname = 'AnalysisReadyNatDist' # the output logfile will include this text in its filename.

	# importing libraries (only works if arclog.py file is located on the parent folder of this script)
	from datetime import datetime
	parent_d = os.path.split(os.path.split(__file__)[0])[0]
	sys.path.append(parent_d)
	from arclog import Print2 as p2

	# find full path where the logfile will be written
	folder_path = arcpy.Describe(input_gdb).path
	while arcpy.Describe(folder_path).dataType != 'Folder':
		folder_path = os.path.split(folder_path)[0]
	outfile = os.path.split(input_gdb)[1] + '_' + tool_shortname + '-LOG_' + datetime.now().strftime('%Y%m%d_%H%M') + '.txt'
	logfile_path = os.path.join(folder_path,outfile)

	# importing arclog in the parent directory
	logger = p2(logfile_path)

	##########

	# run the main function(s)
	analysis_ready_NatDist(input_gdb,step_list)

	# finish writing the logfile
	logger.log_close()
