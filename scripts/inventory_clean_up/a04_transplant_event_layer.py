# ready to use!
# !!!! future fixes: if in step A, there's no intersect, the rest of the scripts should be skipped.

# now that we have event layer - which is basically updated inventory field values based on AR and NatDist - we need to update our latest inventory
# requirements:
# You must first run 02 and 03 scripts before running this script

# these are the steps:
# - loop through the inventory (output of the 02 script)
# - for each inventory, select from the event layer where INV_NAME = inventory name, and run intersect.
# - the intersect will have original inventory fields and NEO_ fields.
#   Where NEO_ fields aren't null, use the value from NEO_ fields and rewrite the corresponding inventory fields.
# - delete all the NEO_ fields (and also INV_NAME field that originated from boundary_fc)


import arcpy
import os, csv
from a02_standardize_using_template import field_types as invfields_dict
from a03_make_event_layer import neofields
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

			# intersect
			arcpy.analysis.PairwiseIntersect(in_features=[mu_fcname, "temp_lyr"],out_feature_class=out_fc_path,join_attributes="ALL",output_type="INPUT")
			logger.print2("\t\tDone")

			# update values
			logger.print2("\tUpdating existing fields (POLYTYPE = FOR) with values from NEO_ fields")
			f = [str(f.name).upper() for f in arcpy.ListFields(out_fc_path)] # that is all fieldnames
			with arcpy.da.UpdateCursor(out_fc_path, f, "POLYTYPE = 'FOR'") as cursor:
				for row in cursor:
					# loop through fields that can be updated
					for neofield in neofields:
						new_value = row[f.index("NEO_%s"%neofield)]
						if new_value != None:
							row[f.index(neofield)] = new_value
					cursor.updateRow(row)
			logger.print2("\t\tDone")

			# dissolve
			out_dislv_fc = os.path.join(ds,"%s%s"%(mu,a2_fc_suffix)) # eg. ...gdb/a/FC421_a_dislv
			logger.print2("\tRunning Dissolve (and deleting unnecessary fields)...")
			stat_fields = ['ARI_ID','POLYID','HA']
			keep_fields = [f for f in invfields if f not in stat_fields]
			stat_fields_wStat = [['ARI_ID','FIRST'],['POLYID','FIRST'],['HA','SUM']]
			arcpy.management.Dissolve(in_features=out_fc_path,out_feature_class=out_dislv_fc,dissolve_field=keep_fields,statistics_fields=stat_fields_wStat,multi_part="SINGLE_PART")
			# dissolve created fields like "FIRST_ARI_ID" and "SUM_HA". turning these back to ARI_ID and HA
			logger.print2("\tAlter Fields (renaming stat fields back to the original field name)")
			for i in stat_fields_wStat:
				orig_fname = "%s_%s"%(i[1],i[0]) # eg. "FIRST_POLYID"
				new_fname = i[0] # eg. POLYID
				arcpy.management.AlterField(in_table=out_dislv_fc,field=orig_fname,new_field_name=new_fname,new_field_alias=new_fname)
			logger.print2("\t\tDone")

			# eliminate
			out_elim_fc = os.path.join(ds,"%s%s"%(mu,a3_fc_suffix))
			logger.print2("\tRunning Eliminate where %s"%elim_select)
			arcpy.MakeFeatureLayer_management(out_dislv_fc, "elimlayer1")
			arcpy.SelectLayerByAttribute_management("elimlayer1", "NEW_SELECTION",elim_select)
			select_count = int(arcpy.GetCount_management("elimlayer1")[0])
			if select_count > 0:
				logger.print2("\t\tSelected %s records"%select_count)
				arcpy.management.Eliminate(in_features="elimlayer1",out_feature_class=out_elim_fc,selection="AREA",ex_where_clause="")
			else:
				logger.print2("\t\tNothing to eliminate. Just copying the data over")
				arcpy.CopyFeatures_management(in_features="elimlayer1",out_feature_class=out_elim_fc)
			logger.print2("\t\tDone")


	# step B delete identical
	step = 'b'
	last_ds = ds
	ds = os.path.join(output_ARAR_gdb,step)
	b1_fc_suffix = "_%s1_delete_ident"%step
	if 'B' in step_list:
		logger.print2("\n\n#########   Step B. Delete Identical  ##########\n")
		logger.print2("Making a new Feature dataset: %s"%step)
		arcpy.Delete_management(os.path.join(output_ARAR_gdb,step))
		arcpy.CreateFeatureDataset_management(output_ARAR_gdb, step, projfile)

		for mu in mu_list:
			logger.print2("\nWorking on %s"%mu)
			last_fc = os.path.join(last_ds,"%s%s"%(mu,a3_fc_suffix))
			out_fc_path1 = os.path.join(ds,"%s%s"%(mu,b1_fc_suffix))

			# sort
			logger.print2("\tSorting by YRSOURCE (descending)")
			arcpy.management.Sort(in_dataset=last_fc,out_dataset=out_fc_path1,sort_field="YRSOURCE DESCENDING")

			# delete identical
			logger.print2("\tDeleting Identical Shapes.")
			arcpy.management.DeleteIdentical(in_dataset=out_fc_path1,fields="Shape")
			logger.print2("\t\tDone")


	# step C erase and append
	step = 'c'
	last_ds = ds
	ds = os.path.join(output_ARAR_gdb,step)
	# c1_fc_suffix = "_%s1_erase_n_append"%step
	c1_fc_suffix = ""
	if 'C' in step_list:
		logger.print2("\n\n#########   Step C. Erase and append  ##########\n")
		arcpy.env.workspace = clean02_inv_gdb
		logger.print2("Making a new Feature dataset: %s"%step)
		arcpy.Delete_management(os.path.join(output_ARAR_gdb,step))
		arcpy.CreateFeatureDataset_management(output_ARAR_gdb, step, projfile)

		for mu in mu_list:
			logger.print2("\nWorking on %s"%mu)
			last_fc = os.path.join(last_ds,"%s%s"%(mu,b1_fc_suffix))
			mu_fcname = "%s%s"%(mu,clean_inv_suffix)
			out_fc_path1 = os.path.join(ds,"%s%s"%(mu,c1_fc_suffix))

			# erase from original inv
			logger.print2("\tErasing %s from %s"%(os.path.split(last_fc)[1], mu_fcname))
			arcpy.analysis.PairwiseErase(in_features=mu_fcname,erase_features=last_fc,out_feature_class=out_fc_path1)

			# append to the original inv
			logger.print2("\tAppending %s to %s"%(os.path.split(last_fc)[1], os.path.split(out_fc_path1)[1]))
			app_out = arcpy.management.Append(inputs=last_fc, target=out_fc_path1, schema_type="NO_TEST")
			append_count = int(app_out.getOutput("appended_row_count"))
			logger.print2("\t\tAppended %s records"%append_count)
			logger.print2("\t\tDone")





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

	tool_shortname = 'Transplant_Event_Layer' # the output logfile will include this text in its filename.

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