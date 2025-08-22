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
from a03_make_event_layer import neofields

arcpy.env.overwriteOutput = True
arcpy.env.XYTolerance = "0.01 Meters" # by default, it is 0.001 meters, which can generate 1mm-wide overlaps and gaps. So 0.01m is preferred.
projfile = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"MNRLambert_d.prj") # this works for all scripts that are one folder level deep. eg. scripts/sqlite/script.py


def make_event_layer(in_arar_gdb, in_natdist_gdb, out_event_gdb, boundary_fc, time_range, year_now, para, step_list):

	# these are the layers from in_arar_gdb that will be used to build event layer
	orig_ar_layers = {'HRV':'HRV_All_02_n_up','EST':'EST_Y_02_n_up','RGN':'Regen_All_02_n_up','SGR':'SGR_Flat'}
	# orig_ar_layers = {'EST':'EST_Y_02_n_up','RGN':'Regen_All_02_n_up','SGR':'SGR_Flat'}
	# this layer should be found in in_natdist_gdb
	orig_natdist_layer = 'NatDist_MT_LatestOnly'
	logger.print2("Time Range Used:\n%s"%time_range)

	# parameters
	ht_per_year = para['ht_per_year']
	simplify_meter = para['simplify_meters']
	eliminate_sqm = para['eliminate_sqm']

	# common variables
	dsAR1,dsAR2,dsAR3,dsAR4,dsAR5,dsAR6 = 'AR1','AR2','AR3','AR4','AR5','AR6'
	dsNAT1,dsNAT2,dsNAT3 = 'NAT1','NAT2','NAT3'
	dsNEO1, dsNEO2, dsNEO3, dsNEO4 = 'NEO1','NEO2','NEO3','NEO4'

	if 'NAT1' in step_list:
		# this one is easy. Just need to select and copy over to the new dataset because it's already flat
		arcpy.env.workspace = in_natdist_gdb
		natdist_fc_name = 'NatDist_MT_LatestOnly'

		logger.print2("\n\n#########   NAT1. Select and Copy NatDist_MT_LatestOnly  ##########\n")
		logger.print2("Making a new Feature dataset: %s"%dsNAT1)
		arcpy.Delete_management(os.path.join(out_event_gdb,dsNAT1))
		arcpy.CreateFeatureDataset_management(out_event_gdb, dsNAT1, projfile)
		dest_fd = os.path.join(out_event_gdb, dsNAT1)

		# select
		select_sql = time_range['NAT']
		logger.print2("\tSelecting where %s"%select_sql)
		arcpy.management.MakeFeatureLayer(natdist_fc_name, "temp_lyr")
		arcpy.management.SelectLayerByAttribute("temp_lyr", "NEW_SELECTION", select_sql)
		num_selected = int(arcpy.management.GetCount("temp_lyr")[0])
		logger.print2("\tSelected %s records"%num_selected)

		# copy
		logger.print2("\tCopying over the selected records")
		outNAT1 = os.path.join(dest_fd,"%s"%dsNAT1)
		arcpy.CopyFeatures_management(in_features="temp_lyr",out_feature_class=outNAT1)
		logger.print2("\tDone!")










if __name__ == '__main__':
	
	# gather inputs
	in_arar_gdb = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\D\AR\AnalysisReadyAR.gdb' # the outcome of AR_AR.py
	in_natdist_gdb = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\E\Natural_Disturbance\NatDist.gdb' # after running AnalysisReady_NatDist.py
	out_event_gdb = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - FRO\FRO2026\02InventoryCleanUp\EventLayer.gdb' # this must already exist - it can be just an empty gdb with whatever name you want
	boundary_fc = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\D\GeoData\PIAMMar2024.gdb\FMU_FN_PARK_Boundary_Simp2m' # only used on later steps (NEO3)
	time_range = {
	'HRV': "AR_YEAR >= 2015",
	'RGN': "AR_YEAR >= 2010", # only affects devstage. without RGN, we can't figure out if devstage is ESTNAT or ESTPLANT
	'EST': "AR_YEAR >= 2015",
	'SGR': "AR_YEAR >= 2015",
	'NAT': "YEAR >= 2015 AND SOURCE in ('FIRE','Weather')", # do fire and weather only because insect damage doesn't necessarily kill all the trees.
	# 'NAT': "YEAR >= 2015",
	} # 
	year_now = 2025 # used to re-calculate age
	para = {
	'ht_per_year': 0.3,
	'simplify_meters': 2,
	'eliminate_sqm': 500, # should be greater than 200
	}
	# step_list: we don't have time to run everything again when something goes wrong. if your AR2 fails, you can fix the bug and run it again start AR2 without running AR1
	# previous step should've been run before running the step that comes after.
	# for example, AR2-1 can run on its own if you've previously completed AR1 and AR2
	step_list = 'ALL'
	step_list = ['AR5','AR5-2','AR6','NEO1','NEO2','NEO3','NEO4']

	if step_list == 'ALL':
		step_list = ['NAT1','NAT2','NAT3','AR1','AR2','AR2-1','AR3','AR4','AR5','AR5-2','AR6','NEO1','NEO2','NEO3','NEO4']


	######### logfile stuff

	tool_shortname = 'Transplant_Event_Layer' # the output logfile will include this text in its filename.

	# importing libraries (only works if arclog.py file is located on the parent folder of this script)
	from datetime import datetime
	parent_d = os.path.split(os.path.split(__file__)[0])[0]
	sys.path.append(parent_d)
	from arclog import Print2 as p2
	import common_func

	# find full path where the logfile will be written
	folder_path = arcpy.Describe(out_event_gdb).path
	while arcpy.Describe(folder_path).dataType != 'Folder':
		folder_path = os.path.split(folder_path)[0]
	outfile = os.path.split(out_event_gdb)[1] + '_' + tool_shortname + '-LOG_' + datetime.now().strftime('%Y%m%d_%H%M') + '.txt'
	logfile_path = os.path.join(folder_path,outfile)

	# importing arclog in the parent directory
	logger = p2(logfile_path)

	##########

	# run the main function(s)
	make_event_layer(in_arar_gdb, in_natdist_gdb, out_event_gdb, boundary_fc, time_range, year_now, para, step_list)

	# finish writing the logfile
	logger.log_close()