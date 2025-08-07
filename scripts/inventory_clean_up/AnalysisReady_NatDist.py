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
projfile = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"MNRLambert_d.prj")

def natdist_all(input_gdb):

	new_ds = 'All'
	new_ds_full = os.path.join(input_gdb,new_ds)
	append_base_full = os.path.join(input_gdb,orig_ds,append_base)
	append_lst = [os.path.join(input_gdb,orig_ds,i) for i in to_be_appended]
	new_fc = 'NatDist_All'
	new_fc_full = os.path.join(new_ds_full,new_fc)

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





if __name__ == '__main__':
	
	# gather inputs
	input_gdb = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\E\Natural_Disturbance\NatDist.gdb'

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
	natdist_all(input_gdb)

	# finish writing the logfile
	logger.log_close()
