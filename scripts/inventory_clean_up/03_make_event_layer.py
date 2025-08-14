# Make event layer out of NatDist_MT_LatestOnly and Analysis-Ready AR
# references:
# https://ontariogov.sharepoint.com/sites/MNRF-PD-INT/CFLPB/CFLPB-FPPS/ForestExplorer/Shared%20Documents/ARTabularData/PIAM_Metadata.xlsx?web=1
# OneNote https://onedrive.live.com/edit.aspx?resid=206EBBE091EA63DA%2140452&migratedtospo=true&wd=target%28AR+n+INV.one%7Cb93cec30-9b1a-403e-8558-001c6233c160%2FInventory+Update+from+AR+and+NatDist%7C59b2aee0-5bfd-4b03-b5aa-914e915c9732%2F%29&wdorigin=703&wdpartid=%7B361f9d14-21db-4c53-854a-495026baf28e%7D%7B1%7D&wdsectionfileid=206ebbe091ea63da%2141564

# Requirement:
# Must first run AR_AR.py and AnalysisReady_NatDist.py


# what is event layer: it is the layer used to update out-of-date inventory data. 
#	For example, using new HRV layer, we can update YRSOURCE, YRDEP, DEVSTAGE and etc.
#	all the fields that can be potentially updated based on the latest AR or NatDist data are listed in neofields:
prefix = 'NEO_'
neofields = {
	# fieldname | field type | length 		
	'YRSOURCE':	['SHORT'],
	'SOURCE':	['TEXT',	16],
	'YRDEP':	['SHORT'],
	'DEPTYPE':	['TEXT',	16],
	'DEVSTAGE':	['TEXT',	16],
	'STKG':		['FLOAT'],
	'YRORG':	['SHORT'],
	'AGE':		['SHORT'],
	'HT':		['FLOAT'],
	'CCLO':		['SHORT'],
	'SILVSYS':	['TEXT',	4],
	'SPCOMP':	['TEXT',	120],
	'PLANFU':	['TEXT',	30],
	'YIELD':	['TEXT',	20],
	'SGR':		['TEXT',	50],
	'LEADSPC':	['TEXT',	3],
}

# only used for nat dist to select and calculate field for NEO_DEPTYPE field
sql_deptype = {
	'BLOWDOWN': " NATDID = 'BLDN' ",
	'DISEASE':	" SOURCE = 'Disease' ",
	'DROUGHT': " NATDID = 'DROT' ",
	'FIRE': " SOURCE = 'FIRE' ",
	'FLOOD': " NATDID = 'FLOD' ",
	'ICE': " NATDID = 'ICED' ",
	'INSECTS': " SOURCE in ('Budworm','FTCT','OthPest') ",
	'SNOW': " NATDID = 'SNOW' "}


import arcpy
import os, csv
import pandas as pd

arcpy.env.overwriteOutput = True
arcpy.env.XYTolerance = "0.01 Meters" # by default, it is 0.001 meters, which can generate 1mm-wide overlaps and gaps. So 0.01m is preferred.
projfile = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"MNRLambert_d.prj") # this works for all scripts that are one folder level deep. eg. scripts/sqlite/script.py


def make_event_layer(in_arar_gdb, in_natdist_gdb, out_event_gdb, time_range, year_now, para, step_list):

	# these are the layers from in_arar_gdb that will be used to build event layer
	orig_ar_layers = {'HRV':'HRV_All_02_n_up','EST':'EST_Y_02_n_up','RGN':'Regen_All_02_n_up','SGR':'SGR_Flat'}
	# this layer should be found in in_natdist_gdb
	orig_natdist_layer = 'NatDist_MT_LatestOnly'
	logger.print2("Time Range Used:\n%s"%time_range)

	# parameters
	ht_per_year = para['ht_per_year']
	simplify_meter = para['simplify_meters']
	eliminate_sqm = para['eliminate_sqm']

	# common variables
	dsAR1 = 'AR1' # name of the dataset generated/deleted
	dsNAT1 = 'NAT1'
	dsAR2 = 'AR2'


	if 'AR1' in step_list:
		# first check if all the layers in orig_ar_layers exist
		input_fcs = common_func.find_all_fcs(in_arar_gdb)[0] # a list of names of all fcs in uppercase
		not_found = [lyr for lyr in orig_ar_layers.values() if lyr.upper() not in input_fcs]
		if len(not_found) > 0:
			err1 = "\n!!! The following feature classes are not found in the input AR gdb:\n%s"%not_found
			logger.print2(err1,'warning')
			raise Exception(err1)

		arcpy.env.workspace = in_arar_gdb
		logger.print2("\n\n#########   AR1. Select, simplify and flatten  ##########\n")
		logger.print2("Making a new Feature dataset: %s"%dsAR1)
		arcpy.Delete_management(os.path.join(out_event_gdb,dsAR1))
		arcpy.CreateFeatureDataset_management(out_event_gdb, dsAR1, projfile)
		dest_fd = os.path.join(out_event_gdb, dsAR1)

		for lyrtype, lyrname in orig_ar_layers.items():
			logger.print2("\nWorking on %s"%lyrtype)
			
			# select
			select_sql = time_range[lyrtype]
			logger.print2("\tSelecting where %s"%select_sql)
			arcpy.management.MakeFeatureLayer(lyrname, "temp_lyr")
			arcpy.management.SelectLayerByAttribute("temp_lyr", "NEW_SELECTION", select_sql)
			num_selected = int(arcpy.management.GetCount("temp_lyr")[0])
			logger.print2("\tSelected %s records"%num_selected)

			logger.print2("\tCopying over the selected records")
			outAR1 = os.path.join(dest_fd,"%s_%s"%(lyrtype,dsAR1))
			arcpy.CopyFeatures_management(in_features="temp_lyr",out_feature_class=outAR1)

			# simplify
			logger.print2("\tSimplifying by %sm"%simplify_meter)
			outAR1a = os.path.join(dest_fd,"%s_%sa"%(lyrtype,dsAR1))
			arcpy.cartography.SimplifyPolygon(
				in_features=outAR1,
				out_feature_class=outAR1a,
				algorithm="POINT_REMOVE",
				tolerance="%s Meters"%simplify_meter,
				# error_option="RESOLVE_ERRORS",
				error_option="NO_CHECK",
				collapsed_point_option="NO_KEEP")
			logger.print2("\t\tDeleting unwanted fields created by simplify polygon tool")
			to_delete = ['ORIG_FID','InPoly_FID','SimPgnFlag','MaxSimpTol','MinSimpTol']
			arcpy.management.DeleteField(outAR1a,to_delete)

			# self-intersect
			logger.print2("\tSelf-intersecting %s"%os.path.split(outAR1a)[1])
			outAR1b = os.path.join(dest_fd,"%s_%sb_self_intersect"%(lyrtype,dsAR1))
			# arcpy.analysis.Intersect(in_features=[outAR1a],out_feature_class=outAR1b,join_attributes="ALL",cluster_tolerance=None,output_type="INPUT")
			arcpy.analysis.PairwiseIntersect(in_features=[outAR1a],out_feature_class=outAR1b,join_attributes="ALL",cluster_tolerance=None,output_type="INPUT")
			d_field = "FID_%s_%sa"%(dsAR1,lyrtype)
			logger.print2("\t\tDeleting unwanted %s field created by Pairwise Intersect tool"%d_field)
			to_delete = [d_field]
			arcpy.management.DeleteField(outAR1b,to_delete)


			# count if there are any self-intersects
			rec_count = int(arcpy.GetCount_management(outAR1b)[0])
			logger.print2("\t\tNumber of self-intersects: %s"%rec_count)

			outAR1c = os.path.join(dest_fd,"%s_%sc_sort"%(lyrtype,dsAR1))
			outAR1d = os.path.join(dest_fd,"%s_%sd_erase_n_append"%(lyrtype,dsAR1))
			outAR1e = os.path.join(dest_fd,"%s_%se_elim"%(lyrtype,dsAR1)) # if you change this, you need to change AR2
			if num_selected == 0: # if no self-intersect...
				logger.print2("\tCopying and renaming the fc")
				arcpy.CopyFeatures_management(in_features=outAR1a,out_feature_class=outAR1d)

			else:
				# sort and delete identical
				logger.print2("\tSorting %s by AR_Year (descending)"%os.path.split(outAR1b)[1])
				arcpy.management.Sort(in_dataset=outAR1b,out_dataset=outAR1c,sort_field="AR_YEAR DESCENDING")

				logger.print2("\tDeleting Identical Shapes on %s"%os.path.split(outAR1c)[1])
				arcpy.management.DeleteIdentical(in_dataset=outAR1c,fields="Shape",xy_tolerance=None,z_tolerance=0)

				# erase outAR1c from outAR1a
				logger.print2("\tErasing %s from %s"%(os.path.split(outAR1c)[1], os.path.split(outAR1a)[1]))
				arcpy.analysis.PairwiseErase(in_features=outAR1a,erase_features=outAR1c,out_feature_class=outAR1d)

				# append outAR1c to outAR1d
				logger.print2("\tAppending %s to %s"%(os.path.split(outAR1c)[1], os.path.split(outAR1d)[1]))
				app_out = arcpy.management.Append(inputs=outAR1c, target=outAR1d, schema_type="NO_TEST")
				append_count = int(app_out.getOutput("appended_row_count"))
				logger.print2("\t\tAppended %s records"%append_count)

				logger.print2("\tRepairing Geometry")
				arcpy.management.RepairGeometry(in_features=outAR1d,delete_null="DELETE_NULL",validation_method="ESRI")

			# eliminate small polys from outAR1d
			logger.print2("\tRunning Eliminate")
			elim_select_sql = "SHAPE_AREA < %s"%eliminate_sqm # 500m
			logger.print2("\t\tEliminating polygons where %s"%elim_select_sql)
			arcpy.MakeFeatureLayer_management(outAR1d, "elimlayer1")
			arcpy.SelectLayerByAttribute_management("elimlayer1", "NEW_SELECTION",elim_select_sql)
			arcpy.management.Eliminate(in_features="elimlayer1",out_feature_class=outAR1e,selection="AREA",ex_where_clause="")
			logger.print2("\tDone!")


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


	if 'AR2' in step_list:
		# simple yet time consuming. Starting from the product of step AR1 (outAR1e), populate necessary fields for each layer.
		logger.print2("\n\n#########     AR2. Add Inventory Fields     ##########\n")

		logger.print2("Making a new Feature dataset: %s"%dsAR2)
		dest_fd = os.path.join(out_event_gdb, dsAR2)
		arcpy.Delete_management(dest_fd)
		arcpy.CreateFeatureDataset_management(out_event_gdb, dsAR2, projfile)

		for lyrtype in orig_ar_layers.keys(): # Looping through ['HRV','EST','RGN','SGR']
			dsAR1_fullpath = os.path.join(out_event_gdb, dsAR1) # dsAR1 is just "AR1"
			outAR1e = os.path.join(dsAR1_fullpath,"%s_%se_elim"%(lyrtype,dsAR1)) # same as the last output of AR1
			
			# copy over the output fc from the last step
			logger.print2("\tCopying over %s from the last step"%lyrtype)
			outAR2 = os.path.join(dest_fd,"%s_%s"%(lyrtype,dsAR2)) # eg. ...gdb/AR2/HRV_AR2
			arcpy.CopyFeatures_management(in_features=outAR1e,out_feature_class=outAR2)
			
			logger.print2("\tAdding fields to %s"%os.path.split(outAR2)[1])

			# for HRV and EST, create all new fields
			if lyrtype in ['HRV','EST']:
				for field, field_info in neofields.items():
					fname = "%s_%s"%(lyrtype,field) # eg. HRV_YRSOURCE
					logger.print2("\t\tAdding %s"%fname)
					ftype = field_info[0]
					if ftype == 'TEXT':
						flength = field_info[1]
						arcpy.AddField_management(in_table = outAR2, field_name = fname, field_type = ftype, field_length = "%s"%flength)		
					else: # for 'FLOAT','SHORT', etc.
						arcpy.AddField_management(in_table = outAR2, field_name = fname, field_type = ftype)

			# for RGN and SGR, just add YRSOURCE, DEVSTAGE and SGR
			if lyrtype in ['RGN','SGR']:
				for field, field_info in neofields.items():
					if field in ['YRSOURCE','DEVSTAGE','SGR']:
						fname = "%s_%s"%(lyrtype,field) # eg. RGN_YRSOURCE
						logger.print2("\t\tAdding %s"%fname)
						ftype = field_info[0]
						if ftype == 'TEXT':
							flength = field_info[1]
							arcpy.AddField_management(in_table = outAR2, field_name = fname, field_type = ftype, field_length = "%s"%flength)		
						else: # for 'FLOAT','SHORT', etc.
							arcpy.AddField_management(in_table = outAR2, field_name = fname, field_type = ftype)			

		logger.print2("\tDone!")


	if 'AR2-1' in step_list:
		# This is the complex part. Populating inventory fields such as "HRV_SILVSYS" based on AR data
		logger.print2("\n\n#########   AR2 Part 2. Populate Inventory Fields   ##########\n")

		# Looping through ['HRV','EST','RGN','SGR']
		for lyrtype in orig_ar_layers.keys(): 
			logger.print2("\nWorking on %s"%lyrtype)
			dest_fd = os.path.join(out_event_gdb, dsAR2)
			outAR2 = os.path.join(dest_fd,"%s_%s"%(lyrtype,dsAR2)) # eg. ...gdb/AR2/HRV_AR2, same fc as step AR1

			f = [str(f.name).upper() for f in arcpy.ListFields(outAR2)] # all the fields, uppercase

			# YRSOURCE
			logger.print2("\tPopulating YRSOURCE")
			with arcpy.da.UpdateCursor(outAR2, f) as cursor:
				for row in cursor:
					row[f.index('%s_YRSOURCE'%lyrtype)] = row[f.index('AR_YEAR')]
					cursor.updateRow(row)

			# SOURCE
			if lyrtype in ['HRV','EST']:
				logger.print2("\tPopulating SOURCE")		
				with arcpy.da.UpdateCursor(outAR2, f) as cursor:
					for row in cursor:
						row[f.index('%s_SOURCE'%lyrtype)] = lyrtype # SOURCE = 'HRV' for HRV data
						cursor.updateRow(row)

			# YRDEP
			if lyrtype in ['HRV','EST']:
				logger.print2("\tPopulating YRDEP")		
				with arcpy.da.UpdateCursor(outAR2, f) as cursor:
					for row in cursor:
						if lyrtype == 'HRV': yrdep = row[f.index('AR_YEAR')]
						if lyrtype == 'EST': yrdep = row[f.index('YRDEP')]
						row[f.index('%s_YRDEP'%lyrtype)]  = yrdep
						cursor.updateRow(row)

			# SILVSYS
			if lyrtype in ['HRV','EST']:
				logger.print2("\tPopulating SILVSYS")		
				with arcpy.da.UpdateCursor(outAR2, f) as cursor:
					for row in cursor:
						row[f.index('%s_SILVSYS'%lyrtype)]  = row[f.index('SILVSYS')]
						cursor.updateRow(row)

			# DEPTYPE
			if lyrtype in ['HRV','EST']:
				logger.print2("\tPopulating DEPTYPE")		
				with arcpy.da.UpdateCursor(outAR2, f) as cursor:
					for row in cursor:
						if lyrtype == 'HRV': deptype = 'HARVEST'
						if lyrtype == 'EST': 
							ardstgrp = 	row[f.index('ARDSTGRP')]
							deptype = 'HARVEST' if ardstgrp == 'HRV' else 'UNKNOWN' # if ardstgrp is NAT, leave this UNKNOWN because we will likely get it from NatDist
						row[f.index('%s_DEPTYPE'%lyrtype)]  = deptype
						cursor.updateRow(row)

			# DEVSTAGE
			if lyrtype in ['HRV','EST','RGN']:
				logger.print2("\tPopulating DEVSTAGE")		
				with arcpy.da.UpdateCursor(outAR2, f) as cursor:
					for row in cursor:
						if lyrtype == 'HRV':
							devstage = 'DEPHARV' # by default
							if row[f.index('SILVSYS')] == 'SE':
								devstage = 'SELECT'
							if row[f.index('SILVSYS')] == 'SH':
								mgmtstg = row[f.index('MGMTSTG')] # most likely SEEDCUT, LASTCUT, FIRSTCUT...
								if mgmtstg != None and len(mgmtstg) > 3: # it could be blank, null or '-', in which case it's just the default 'DEPHARV'
									devstage = mgmtstg
						if lyrtype == 'EST':
							# DEVSTAGE should be either ESTNAT, ESTSEED or ESTPLANT, but just based on EST layer, we don't know which one. Will just put EST but if it overlaps with RGN we can figure this out
							devstage = 'EST'
						if lyrtype == 'RGN':
							devstage = 'NEWNAT' # by default
							trtmthd = row[f.index('TRTMTHD1')] # should be one of ['CLAAG','HARP','NATURAL','PLANT','SCARIFY','SEED','SEEDCUT','SEEDSIP','SEEDTREE','STRIPCUT']
							if trtmthd != None: trtmthd = trtmthd.upper()
							if trtmthd in ['CLAAG','HARP','NATURAL','SCARIFY','STRIPCUT']: devstage = 'NEWNAT'
							if trtmthd in ['PLANT']: devstage = 'NEWPLANT'
							if trtmthd in ['SEED','SEEDSIP']: devstage = 'NEWSEED'
							if trtmthd in ['SEEDCUT','SEEDTREE']: devstage = trtmthd # these are types of natural regen but has their place in DEVSTAGE

						row[f.index('%s_DEVSTAGE'%lyrtype)]  = devstage
						cursor.updateRow(row)

			# SPCOMP, PLANFU, LEADSPC, YIELD - we only get this from EST
			if lyrtype in ['EST']:
				logger.print2("\tPopulating SPCOMP, PLANFU, LEADSPC and YIELD")		
				with arcpy.da.UpdateCursor(outAR2, f) as cursor:
					for row in cursor:
						spcomp = row[f.index('SPCOMP')]
						if spcomp != None and len(spcomp) > 5:
							spcomp = spcomp.upper()
							row[f.index('%s_SPCOMP'%lyrtype)]  = spcomp
							row[f.index('%s_LEADSPC'%lyrtype)]  = spcomp[:3].strip()
						row[f.index('%s_PLANFU'%lyrtype)]  = row[f.index('ESTFU')]
						row[f.index('%s_YIELD'%lyrtype)]  = row[f.index('ESTYIELD')]
						cursor.updateRow(row)

			# SGR
			if lyrtype in ['HRV','EST','SGR']:
				logger.print2("\tPopulating SGR")		
				with arcpy.da.UpdateCursor(outAR2, f) as cursor:
					for row in cursor:
						row[f.index('%s_SGR'%lyrtype)] = row[f.index('SGR')]
						cursor.updateRow(row)

			# STKG, YRORG, AGE, CCLO, HT - doing these together because of the interdependency
			if lyrtype in ['HRV','EST']:
				logger.print2("\tPopulating STKG, YRORG, AGE, CCLO, and HT")		
				with arcpy.da.UpdateCursor(outAR2, f) as cursor:
					for row in cursor:
						stkg,yrorg,age,cclo,ht = None,None,None,None,None # default
						silvsys = row[f.index('SILVSYS')]
						ar_year = row[f.index('AR_YEAR')]
						if lyrtype == 'HRV':
							stkg = 0.1 if silvsys == 'CC' else None
							mgmtstg = row[f.index('MGMTSTG')]
							if silvsys == 'CC' or mgmtstg == 'LASTCUT': # if it's clearcut or lastcut, then yrdep = yrorg
								yrorg = ar_year
							if yrorg != None:
								age = year_now - yrorg
							if silvsys == 'CC':
								cclo = 1 # !!!! some may disagree with this, but I think it's better to have cclo = 1 than 80 when it's right after clearcut
							if age != None:
								ht = age * ht_per_year # age times 0.3
						if lyrtype == 'EST':
							stkg = row[f.index('STKG')]
							yrorg = row[f.index('YRDEP')]
							ageest = row[f.index('AGEEST')]
							age = ageest + (year_now - ar_year) # add the difference between today's year and AR year
							if silvsys == 'CC':
								cclo = 11 # !!!! some may disagree with this, but I think it's better to have cclo = 11 than 80 when it's only few years after clearcut
							ht = row[f.index('HT')]
							ht = ht + (age-ageest)*ht_per_year

						row[f.index('%s_STKG'%lyrtype)]  = stkg
						row[f.index('%s_YRORG'%lyrtype)]  = yrorg
						row[f.index('%s_AGE'%lyrtype)]  = age
						row[f.index('%s_CCLO'%lyrtype)]  = cclo
						row[f.index('%s_HT'%lyrtype)]  = ht
						cursor.updateRow(row)




	# # loading csv to list of dictionary
	# tbl_chc = 'habitat_classification.csv'
	# parent_folder = os.path.split(__file__)[0]
	# l_tbl_chc = list(csv.DictReader(open(os.path.join(parent_folder,tbl_chc))))
	# logger.print2(tbl_chc)

	# # loading csv to pandas dataframe
	# tbl_plonski = 'tbl_plonski_metrics.csv'
	# df = pd.read_csv(tbl_plonski, na_filter=False) # if you don't disable na_filter, then it will change 'NA' 'N/A','null' into 'nan'
	# # https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html

	# # see if a fc is polygon or polyline
	# desc = arcpy.Describe(fc)
	# shape = desc.shapeType # eg. Polyline, Polygon, etc.

	# # here are some lines I write all the time:
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
	in_arar_gdb = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\D\AR\AnalysisReadyAR.gdb' # the outcome of AR_AR.py
	in_natdist_gdb = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\E\Natural_Disturbance\NatDist.gdb' # after running AnalysisReady_NatDist.py
	out_event_gdb = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - FRO\FRO2026\02InventoryCleanUp\EventLayer.gdb' # this must already exist - it can be just an empty gdb with whatever name you want
	time_range = {
	'HRV': "AR_YEAR >= 2015",
	'RGN': "AR_YEAR >= 2015", # only affects devstage. without RGN, we can't figure out if devstage is ESTNAT or ESTPLANT
	'EST': "AR_YEAR >= 2015",
	'SGR': "AR_YEAR >= 2015",
	'NAT': "YEAR >= 2015",
	} # 
	year_now = 2025 # used to re-calculate age
	para = {
	'ht_per_year': 0.3,
	'simplify_meters': 2,
	'eliminate_sqm': 500,
	}
	step_list = ['AR1','NAT1','AR2']
	step_list = ['AR2-1']


	######### logfile stuff

	tool_shortname = 'Make_Event_Layer' # the output logfile will include this text in its filename.

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
	make_event_layer(in_arar_gdb, in_natdist_gdb, out_event_gdb, time_range, year_now, para, step_list)

	# finish writing the logfile
	logger.log_close()