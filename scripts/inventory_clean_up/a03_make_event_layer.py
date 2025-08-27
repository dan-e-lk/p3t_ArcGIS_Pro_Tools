# ready to use!
# Make event layer out of NatDist_MT_LatestOnly and Analysis-Ready AR
# references:
# https://ontariogov.sharepoint.com/sites/MNRF-PD-INT/CFLPB/CFLPB-FPPS/ForestExplorer/Shared%20Documents/ARTabularData/PIAM_Metadata.xlsx?web=1
# OneNote https://onedrive.live.com/edit.aspx?resid=206EBBE091EA63DA%2140452&migratedtospo=true&wd=target%28AR+n+INV.one%7Cb93cec30-9b1a-403e-8558-001c6233c160%2FInventory+Update+from+AR+and+NatDist%7C59b2aee0-5bfd-4b03-b5aa-914e915c9732%2F%29&wdorigin=703&wdpartid=%7B361f9d14-21db-4c53-854a-495026baf28e%7D%7B1%7D&wdsectionfileid=206ebbe091ea63da%2141564

# Requirement:
# Must first run AR_AR.py and AnalysisReady_NatDist.py


# what is event layer: it is the layer used to update out-of-date inventory data. 
#	For example, using new HRV layer, we can update YRSOURCE, YRDEP, DEVSTAGE and etc.
#	all the fields that can be potentially updated based on the latest AR or NatDist data are listed in neofields:
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

# the following fields are not updated by nat dist layer
fields_to_exclude = ['SILVSYS','SPCOMP','PLANFU','YIELD','SGR','LEADSPC']


import arcpy
import os, csv

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

	if 'NAT2' in step_list:
		# simple yet time consuming. Starting from the product of step AR1 (outAR1e), populate necessary fields for each layer.
		logger.print2("\n\n#########     NAT2. Add Inventory Fields and Populate them     ##########\n")

		logger.print2("Making a new Feature dataset: %s"%dsNAT2)
		dest_fd = os.path.join(out_event_gdb, dsNAT2)
		arcpy.Delete_management(dest_fd)
		arcpy.CreateFeatureDataset_management(out_event_gdb, dsNAT2, projfile)

		last_fc = os.path.join(out_event_gdb,dsNAT1,dsNAT1)
		out_fc = os.path.join(dest_fd,dsNAT2)
		logger.print2("\nCopying over to %s"%dsNAT2)
		arcpy.CopyFeatures_management(in_features=last_fc,out_feature_class=out_fc)

		# add fields
		logger.print2("\nAdding fields")
		for field, field_info in neofields.items():
			if field not in fields_to_exclude:
				fname = "NATD_%s"%field # eg. HRV_YRSOURCE
				logger.print2("\tAdding %s"%fname)
				ftype = field_info[0]
				if ftype == 'TEXT':
					flength = field_info[1]
					arcpy.AddField_management(in_table = out_fc, field_name = fname, field_type = ftype, field_length = "%s"%flength)		
				else: # for 'FLOAT','SHORT', etc.
					arcpy.AddField_management(in_table = out_fc, field_name = fname, field_type = ftype)
		logger.print2("\tDone!")

		# populate inventory fields
		f = [str(f.name).upper() for f in arcpy.ListFields(out_fc)] # all the fields, uppercase

		# YRSOURCE
		logger.print2("Populating the fields above...")
		natdid_deptype = {'BLDN':'BLOWDOWN', 'DROT':'DROUGHT', 'FLOD':'FLOOD', 'ICED':'ICE', 'SNOW':'SNOW'}
		with arcpy.da.UpdateCursor(out_fc, f) as cursor:
			for row in cursor:
				year = row[f.index('YEAR')]
				row[f.index('NATD_YRSOURCE')] = year
				natdid = row[f.index('NATDID')].upper()
				row[f.index('NATD_SOURCE')] = "NAT_%s"%natdid
				row[f.index('NATD_YRDEP')] = year

				# DEPTYPE
				source = row[f.index('SOURCE')].upper() # file source (budworm, fire, Disease, etc.)
				deptype = 'UNKNOWN'
				if source in ['FIRE','DISEASE']:
					deptype = source
				elif source in ['BUDWORM','FTCT','OTHPEST']:
					deptype = 'INSECTS'
				elif natdid in natdid_deptype.keys():
					deptype = natdid_deptype[natdid]
				# other exception
				elif natdid == 'SCRH':
					deptype = 'DROUGHT'
				row[f.index('NATD_DEPTYPE')] = deptype

				row[f.index('NATD_DEVSTAGE')] = 'DEPNAT'
				row[f.index('NATD_STKG')] = 0.1
				row[f.index('NATD_YRORG')] = year
				row[f.index('NATD_AGE')] = year_now - year
				row[f.index('NATD_HT')] = (year_now - year)*ht_per_year
				row[f.index('NATD_CCLO')] = 11

				cursor.updateRow(row)
		logger.print2("\tDone!")

	# use dissolve to delete fields
	if 'NAT3' in step_list:
		# simple yet time consuming. Starting from the product of step AR1 (outAR1e), populate necessary fields for each layer.
		logger.print2("\n\n#########     NAT3.  Dissolve and Eliminate    ##########\n")

		logger.print2("Making a new Feature dataset: %s"%dsNAT3)
		dest_fd = os.path.join(out_event_gdb, dsNAT3)
		arcpy.Delete_management(dest_fd)
		arcpy.CreateFeatureDataset_management(out_event_gdb, dsNAT3, projfile)

		last_fc = os.path.join(out_event_gdb,dsNAT2,dsNAT2)
		out_fc1 = os.path.join(dest_fd,"%sa_dissolv"%dsNAT3)
		out_fc2 = os.path.join(dest_fd,"NATD_fin")

		natd_fields = [str(f.name).upper() for f in arcpy.ListFields(last_fc) if f.name.startswith('NATD_')]

		# dissolve
		logger.print2("\nRunning dissolve on all NAT_ fields")
		arcpy.management.Dissolve(in_features=last_fc,out_feature_class=out_fc1,dissolve_field=natd_fields,statistics_fields=None,multi_part="SINGLE_PART")
		logger.print2("\tDone!")

		# Eliminate polys 
		logger.print2("\nRunning Eliminate anything less than %sm2"%eliminate_sqm)
		elim_select_sql = "SHAPE_AREA < %s"%eliminate_sqm
		arcpy.MakeFeatureLayer_management(out_fc1, "elimlayer1")
		arcpy.SelectLayerByAttribute_management("elimlayer1", "NEW_SELECTION",elim_select_sql)
		arcpy.management.Eliminate(in_features="elimlayer1",out_feature_class=out_fc2,selection="AREA",ex_where_clause="")

		# delete less than Xm2 (island polygons that didn't get eliminated)
		logger.print2("Deleting anything less than %sm2 (rest of the small polys that didn't get eliminated)"%eliminate_sqm)
		with arcpy.da.UpdateCursor(out_fc2,["SHAPE_AREA"],elim_select_sql) as cursor:
			for row in cursor:
				cursor.deleteRow()
		logger.print2("\nCompleted inventorifying Natural Disturbance!!")



	if 'AR1' in step_list:
		# first check if all the layers in orig_ar_layers exist
		input_fcs = common_func.find_all_fcs(in_arar_gdb)[0] # a list of names of all fcs in uppercase
		not_found = [lyr for lyr in orig_ar_layers.values() if lyr.upper() not in input_fcs]
		if len(not_found) > 0:
			err1 = "\n!!! The following feature classes are not found in the input AR gdb:\n%s"%not_found
			logger.print2(err1,'warning')
			raise Exception(err1)

		arcpy.env.workspace = in_arar_gdb
		logger.print2("\n\n##########    AR1. Select, simplify and flatten   ###########\n")
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
						silvsys = row[f.index('SILVSYS')]
						if silvsys not in ['CC','SH','SE']:
							silvsys = None
						row[f.index('%s_SILVSYS'%lyrtype)]  = silvsys
						cursor.updateRow(row)

			# DEPTYPE
			if lyrtype in ['HRV','EST']:
				logger.print2("\tPopulating DEPTYPE")		
				with arcpy.da.UpdateCursor(outAR2, f) as cursor:
					for row in cursor:
						if lyrtype == 'HRV': deptype = 'HARVEST'
						if lyrtype == 'EST': 
							ardstgrp = 	row[f.index('ARDSTGRP')]
							deptype = 'HARVEST' if ardstgrp in ['HARV','HRV','HARVEST'] else 'UNKNOWN' # if ardstgrp is NAT, leave this UNKNOWN because we will likely get it from NatDist
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
						spcomp, planfu, leadspc, ar_yield = row[f.index('SPCOMP')], row[f.index('ESTFU')], None, row[f.index('ESTYIELD')]
						if spcomp != None and len(spcomp) > 5:
							spcomp = spcomp.upper()
							leadspc  = spcomp[:3].strip()
						if planfu == None or len(planfu) < 2: planfu = None
						if ar_yield == None or ar_yield.strip() in ['-','']: ar_yield = None

						row[f.index('%s_SPCOMP'%lyrtype)]  = spcomp
						row[f.index('%s_PLANFU'%lyrtype)]  = planfu
						row[f.index('%s_LEADSPC'%lyrtype)] = leadspc
						row[f.index('%s_YIELD'%lyrtype)]  = ar_yield
						cursor.updateRow(row)

			# SGR
			if lyrtype in ['HRV','EST','SGR']:
				logger.print2("\tPopulating SGR")		
				with arcpy.da.UpdateCursor(outAR2, f) as cursor:
					for row in cursor:
						sgr = row[f.index('SGR')]
						if sgr == None or sgr.strip() in ['-','']:
							sgr = None
						else:
							sgr = sgr.strip().upper()
						row[f.index('%s_SGR'%lyrtype)] = sgr
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
							yrdep = row[f.index('YRDEP')] # some YRDEP is ridiculously old - eg. 1865
							ar_ht = row[f.index('HT')]							
							ageest = row[f.index('AGEEST')] # sometimes ageest is None
							if yrdep == None or yrdep < 1900: # if YRDEP doesn't make sense, deduce it from HT
								ageest = ar_ht/ht_per_year # if height is 9m, deduced ageest is 30years using 0.3m/year ht_per_year
								yrdep = ar_year - ageest
							yrorg = yrdep
							if ageest == None or ageest < 1: # if ageest is unknown, we calculate this
								ageest = ar_year - yrorg
							age = ageest + (year_now - ar_year) # add the difference between today's year and AR year
							# if silvsys == 'CC':
							# 	cclo = 11 
							ht = ar_ht + (age-ageest)*ht_per_year

						row[f.index('%s_STKG'%lyrtype)]  = stkg
						row[f.index('%s_YRORG'%lyrtype)]  = yrorg
						row[f.index('%s_AGE'%lyrtype)]  = age
						row[f.index('%s_CCLO'%lyrtype)]  = cclo
						row[f.index('%s_HT'%lyrtype)]  = ht
						cursor.updateRow(row)

			# YRDEP shouldn't be older than YRORG
			if lyrtype in ['EST']:
				logger.print2("\tReviewing YRDEP (YRDEP shouldn't be older than YRORG)")		
				with arcpy.da.UpdateCursor(outAR2, f) as cursor:
					for row in cursor:
						yrdep = row[f.index('%s_YRDEP'%lyrtype)]
						yrorg = row[f.index('%s_YRORG'%lyrtype)]
						if yrdep < yrorg:
							row[f.index('%s_YRDEP'%lyrtype)] = yrorg
							cursor.updateRow(row)

	if 'AR3' in step_list:
		# Simple but time consuming. union all 4 AR layers, and delete / add fields
		logger.print2("\n\n#########    AR3  Union All AR data (5mins)  ##########\n")

		# output data from AR2-1
		dsAR2_full = os.path.join(out_event_gdb, dsAR2)
		AR2_fcs_full = [os.path.join(out_event_gdb, dsAR2,"%s_%s"%(lyrtype,dsAR2)) for lyrtype in orig_ar_layers.keys()] # list of all fcs from AR2-1

		logger.print2("Making a new Feature dataset: %s"%dsAR3)
		dest_fd = os.path.join(out_event_gdb, dsAR3)
		arcpy.Delete_management(dest_fd)
		arcpy.CreateFeatureDataset_management(out_event_gdb, dsAR3, projfile)
		dest_fc = os.path.join(dest_fd,"%s_Union"%dsAR3)

		logger.print2("\nUnioning all AR data (takes about 5-10mins)")
		arcpy.analysis.Union(in_features=AR2_fcs_full,out_feature_class=dest_fc,join_attributes="ALL",cluster_tolerance=None,gaps="GAPS")
		logger.print2("\tDone!")

	if 'AR4' in step_list:
		# delete fields, add AR_ inventory fields (eg. AR_YRSOURCE)
		logger.print2("\n\n#########    AR4 Delete fields and add new ones (12mins)  ##########\n")
		
		last_fc = os.path.join(out_event_gdb, dsAR3, "%s_Union"%dsAR3)

		logger.print2("\nMaking a new Feature dataset: %s"%dsAR4)
		dest_fd = os.path.join(out_event_gdb, dsAR4)
		arcpy.Delete_management(dest_fd)
		arcpy.CreateFeatureDataset_management(out_event_gdb, dsAR4, projfile)
		dest_fc = os.path.join(dest_fd,dsAR4)

		# copy the AR3 union data over
		logger.print2("\nCopying over the data from AR3...")
		arcpy.CopyFeatures_management(in_features=last_fc,out_feature_class=dest_fc)

		# delete field
		# first make a list of fields to keep
		existingFields = [str(f.name).upper() for f in arcpy.ListFields(dest_fc)] # all the fields, uppercase
		keep_fields = [] # list of fields we want to keep - the rest should be deleted
		for lyrtype in orig_ar_layers.keys():
			for fname in neofields.keys():
				field_to_keep = "%s_%s"%(lyrtype,fname) #eg. HRV_YRDEP or SGR_YRSOURCE
				if field_to_keep in existingFields:
					keep_fields.append(field_to_keep)

		logger.print2("\nDeleting fields except these fields: (this may take over 10 mins)\n%s\n"%keep_fields)
		arcpy.management.DeleteField(dest_fc, keep_fields, "KEEP_FIELDS")
		# in the future, I should replace delete field with dissolve because it's actually faster to dissolve than delete field

		# add fields
		logger.print2("\nAdding Fields")
		for field, field_info in neofields.items():
			fname = "AR_%s"%field # eg. AR_YRSOURCE
			logger.print2("\tAdding %s"%fname)
			ftype = field_info[0]
			if ftype == 'TEXT':
				flength = field_info[1]
				arcpy.AddField_management(in_table = dest_fc, field_name = fname, field_type = ftype, field_length = "%s"%flength)		
			else: # for 'FLOAT','SHORT', etc.
				arcpy.AddField_management(in_table = dest_fc, field_name = fname, field_type = ftype)

	if 'AR5' in step_list:
		# this step significantly reduces the number of polygons we need to deal with
		logger.print2("\n\n#########    AR5. Multi to Single, then eliminate %sm2  ##########\n"%eliminate_sqm)
		
		last_fc = os.path.join(out_event_gdb, dsAR4, dsAR4)

		logger.print2("\nMaking a new Feature dataset: %s"%dsAR5)
		dest_fd = os.path.join(out_event_gdb, dsAR5)
		arcpy.Delete_management(dest_fd)
		arcpy.CreateFeatureDataset_management(out_event_gdb, dsAR5, projfile)
		dsAR5a = os.path.join(dest_fd,"%sa_M2S"%dsAR5)
		dsAR5b = os.path.join(dest_fd,"%sb_Elim"%dsAR5)

		# count before
		count_orig = int(arcpy.management.GetCount(last_fc)[0])

		# multi to single
		logger.print2("\nRunning Multipart to Single Part on %s"%last_fc)
		arcpy.management.MultipartToSinglepart(in_features=last_fc,out_feature_class=dsAR5a)

		# Eliminate polys 
		logger.print2("\nRunning Eliminate anything less than %sm2"%eliminate_sqm)
		elim_select_sql = "SHAPE_AREA < %s"%eliminate_sqm
		arcpy.MakeFeatureLayer_management(dsAR5a, "elimlayer1")
		arcpy.SelectLayerByAttribute_management("elimlayer1", "NEW_SELECTION",elim_select_sql)
		arcpy.management.Eliminate(in_features="elimlayer1",out_feature_class=dsAR5b,selection="AREA",ex_where_clause="")

		# delete less than Xm2 (island polygons that didn't get eliminated)
		logger.print2("\nDeleting anything less than %sm2 (rest of the small polys that didn't get eliminated)"%eliminate_sqm)
		with arcpy.da.UpdateCursor(dsAR5b,["SHAPE_AREA"],elim_select_sql) as cursor:
			for row in cursor:
				cursor.deleteRow()

		# count after
		count_after = int(arcpy.management.GetCount(dsAR5b)[0])
		diff = count_orig-count_after
		diff_percent = round(100*diff/count_orig,2)
		logger.print2("\nPolygons eliminated: %s - %s = %s (%s%%)"%(count_orig,count_after,diff,diff_percent))
		logger.print2("\nDone!")

	if 'AR5-2' in step_list:
		# Use the unionized data from all 4 AR layers, pick the best or the latest information to populate inventory fields
		logger.print2("\n\n#########    AR5 Part2. Generate inventory from all 4 AR layers  ##########\n")
		logger.print2("\nUse the unionized data from all 4 AR layers, pick the best or the latest information to populate inventory fields.")
		
		last_fc = os.path.join(out_event_gdb, dsAR5, "%sb_Elim"%dsAR5)
		f = [str(f.name).upper() for f in arcpy.ListFields(last_fc)] # all the fields, uppercase

		fields_by_hrv_n_est = ['YRSOURCE','SOURCE','YRDEP','SILVSYS','DEPTYPE','YRORG','AGE','HT'] # if occurs in both HRV and EST, use the latest data
		fields_by_est_only = ['SPCOMP','PLANFU','YIELD','LEADSPC']

		# 'YRSOURCE','SOURCE','YRDEP','SILVSYS','DEPTYPE','YRORG','AGE','HT'
		# Note that YRSOURCE and SOURCE won't be updated by RGN and SGR layers even though RGN changes DEVSTAGE and SGR chanages SGR
		logger.print2("\nThe following fields are dependent on EST and HRV:\n%s"%fields_by_hrv_n_est)
		logger.print2("\tUpdating the fields above using the latest information...")
		with arcpy.da.UpdateCursor(last_fc, f) as cursor:
			for row in cursor:
				for i in fields_by_hrv_n_est:
					hrv_val = row[f.index('HRV_%s'%i)] # eg. i is one of ['YRSOURCE','SOURCE','SILVSYS','DEPTYPE','AGE','HT']
					est_val = row[f.index('EST_%s'%i)]
					if hrv_val in [None,0,''] and est_val not in [None,0,'']:
						row[f.index('AR_%s'%i)] = est_val
					elif hrv_val not in [None,0,''] and est_val in [None,0,'']:
						row[f.index('AR_%s'%i)] = hrv_val
					elif hrv_val not in [None,0,''] and est_val not in [None,0,'']: # if the value exists in both HRV and EST, then use the latest value
						hrv_yr = row[f.index('HRV_YRSOURCE')]
						est_yr = row[f.index('EST_YRSOURCE')]
						if hrv_yr < est_yr:
							row[f.index('AR_%s'%i)] = est_val
						else:
							row[f.index('AR_%s'%i)] = hrv_val
					else:
						row[f.index('AR_%s'%i)] = None
				cursor.updateRow(row)
		logger.print2("\tDone!")

		# SPCOMP, PLANFU, YIELD and LEADSPC (also update YRSOURCE and SOURCE)
		logger.print2("\nThe following fields are completely dependent on EST data only:\n%s"%fields_by_est_only)
		logger.print2("\tUpdating the fields above...")
		with arcpy.da.UpdateCursor(last_fc, f) as cursor:
			for row in cursor:
				est_val_used = False
				for i in fields_by_est_only:
					est_val = row[f.index('EST_%s'%i)]
					if est_val not in [None,0,'']:
						est_val_used = True
						row[f.index('AR_%s'%i)] = est_val
				if est_val_used:
					row[f.index('AR_YRSOURCE')] = row[f.index('EST_YRSOURCE')]
					row[f.index('AR_SOURCE')] = row[f.index('EST_SOURCE')]
				cursor.updateRow(row)
		logger.print2("\tDone!")

		# DEVSTAGE
		logger.print2("\nUpdating DEVSTAGE...")
		with arcpy.da.UpdateCursor(last_fc, f) as cursor:
			for row in cursor:
				devstage = None # this should never happen. The if statements below should cover all cases
				hrv_dev = row[f.index('HRV_DEVSTAGE')]
				rgn_dev = row[f.index('RGN_DEVSTAGE')]
				est_dev = row[f.index('EST_DEVSTAGE')]
				hrv_dev = hrv_dev if len(hrv_dev)>2 else None
				rgn_dev = rgn_dev if len(rgn_dev)>2 else None
				est_dev = est_dev if len(est_dev)>2 else None
				# case 1: HRV only
				if hrv_dev != None and rgn_dev == None and est_dev == None:
					devstage = hrv_dev
				# case 2: EST only (missing RGN? we assume it was natural regen)
				elif hrv_dev == None and rgn_dev == None and est_dev != None:
					devstage = 'ESTNAT'
				# case 3: RGN only 
				elif hrv_dev == None and rgn_dev != None and est_dev == None:
					devstage = rgn_dev
				# case 4: RGN and HRV (use the latest)
				elif hrv_dev != None and rgn_dev != None and est_dev == None:
					if row[f.index('HRV_YRSOURCE')] < row[f.index('RGN_YRSOURCE')]:
						devstage = rgn_dev
					else:
						devstage = hrv_dev
				# case 5: HRV + EST (missing RGN? we assume it was natural regen)
				elif hrv_dev != None and rgn_dev == None and est_dev != None:
					devstage = 'ESTNAT'
				# case 6: RGN + EST (or when all 3 exists) (RGN will be either NEWNAT, NEWPLANT, NEWSEED)
				elif rgn_dev != None and est_dev != None:
					rgn_type = rgn_dev [3:] # NAT, PLANT, or SEED
					devstage = "EST%s"%rgn_type # ESTNAT, ESTPLANT, or ESTSEED
				row[f.index('AR_DEVSTAGE')] = devstage
				# also update YRSOURCE if we are using rgn_dev and if RGN_YRSOURCE is the latest
				if devstage == rgn_dev:
					if row[f.index('AR_YRSOURCE')] == None or row[f.index('AR_YRSOURCE')] < row[f.index('RGN_YRSOURCE')]:
						row[f.index('AR_YRSOURCE')] = row[f.index('RGN_YRSOURCE')]
				cursor.updateRow(row)
		logger.print2("\tDone!")


		# SGR
		logger.print2("\nUpdating SGR with the latest SGR value from HRV, EST and SGR...")
		with arcpy.da.UpdateCursor(last_fc, f) as cursor:
			for row in cursor:
				sgr = None # default when there's no SGR found
				hrv_val = "%s*HRV"%row[f.index('HRV_SGR')] if row[f.index('HRV_SGR')] not in ['','-'] else None
				sgr_val = "%s*SGR"%row[f.index('SGR_SGR')] if row[f.index('SGR_SGR')] not in ['','-'] else None
				est_val = "%s*EST"%row[f.index('EST_SGR')] if row[f.index('EST_SGR')] not in ['','-'] else None
				hrv_yr = row[f.index('HRV_YRSOURCE')] if hrv_val != None else 0
				sgr_yr = row[f.index('SGR_YRSOURCE')] if sgr_val != None else 0
				est_yr = row[f.index('EST_YRSOURCE')] if est_val != None else 0
				val = [hrv_val,sgr_val,est_val]
				yr = [hrv_yr,sgr_yr,est_yr]
				sgr_yr = {"%s%s"%(k,v):v for k,v in zip(val,yr) if k != None} # eg. {'PJ1-PJ1*SGR2023': 2023, ...}

				# if SGR appears in only one of them, just use that
				if len(sgr_yr) == 1:
					sgr = list(sgr_yr.keys())[0]
				# if more than one SGR, then use the latest one (complicates when two SGR appears in same year - in that case, we just pick one)
				elif len(sgr_yr) > 1:
					sorted_sgr_yr = dict(sorted(sgr_yr.items(), key=lambda item: item[1], reverse=True)) # reverse sort the sgr_yr so the latest year comes first
					sgr = list(sorted_sgr_yr.keys())[0]
				
				row[f.index('AR_SGR')] = sgr
				cursor.updateRow(row)
		logger.print2("\tDone!")

		# STKG
		logger.print2("\nUpdating STKG (Use EST's STKG or if HRV SILVSYS=CC then '0.1')")
		with arcpy.da.UpdateCursor(last_fc, f) as cursor:
			for row in cursor:
				stkg = None # default when there's no STKG update
				est_val = row[f.index('EST_STKG')] if row[f.index('EST_STKG')] not in [None,0] else 0
				hrv_val = row[f.index('HRV_STKG')] if row[f.index('HRV_STKG')] not in [None,0] else 0

				# if est stocking value exist, just use that, otherwise use hrv value only if it exists
				if est_val > 0:
					stkg = est_val
				elif hrv_val > 0:
					stkg = hrv_val

				row[f.index('AR_STKG')] = stkg
				cursor.updateRow(row)
		logger.print2("\tDone!")

		# CCLO
		logger.print2("\nUpdating CCLO (only if HRV SILVSYS=CC and AGE <= 5 then update CCLO=1)")
		with arcpy.da.UpdateCursor(last_fc, f) as cursor:
			for row in cursor:
				cclo = None # default when there's no STKG update
				if row[f.index('HRV_SILVSYS')] == 'CC':
					if row[f.index('HRV_AGE')] < 5:
						cclo = 1
				row[f.index('AR_CCLO')] = cclo
				cursor.updateRow(row)
		logger.print2("\tDone!")

	if 'AR6' in step_list:
		# this step significantly reduces the number of polygons we need to deal with
		logger.print2("\n\n#########    AR6. Finalize AR-derived Inventory  ##########\n")
		
		last_fc = os.path.join(out_event_gdb, dsAR5, "%sb_Elim"%dsAR5)

		logger.print2("\nMaking a new Feature dataset: %s"%dsAR6)
		dest_fd = os.path.join(out_event_gdb, dsAR6)
		arcpy.Delete_management(dest_fd)
		arcpy.CreateFeatureDataset_management(out_event_gdb, dsAR6, projfile)
		dsAR6a = os.path.join(dest_fd,"AR_fin")

		ar_fields = [str(f.name) for f in arcpy.ListFields(last_fc) if f.name.startswith('AR_')] # eg. AR_YRSOURCE, AR_SPCOMP...

		# dissolve
		logger.print2("\nRunning dissolve on all AR_ fields (This also significantly reduces number of polys)")
		arcpy.management.Dissolve(in_features=last_fc,out_feature_class=dsAR6a,dissolve_field=ar_fields,statistics_fields=None,multi_part="SINGLE_PART")
		logger.print2("\nCompleted inventorifying Annual Report HRV, EST, RGN, and SGR!!")


###################################################################
# At this point, the final 'AR_fin' and 'NATD_fin' are the final products of the above scripts.
# these two layers contain inventory fields but prefixed with AR_ and NATD_ respectively
# Next step is to union the two layers, grabbing the latest and best information from both, and save them in NEO_ inventory fields.

	if 'NEO1' in step_list:
		logger.print2("\n\n#########    NEO1. Union AR and NATD INV and add NEO_ fields ##########\n")
		
		arcpy.env.workspace = out_event_gdb
		ar_fc = 'AR_fin'
		natd_fc = 'NATD_fin'

		logger.print2("\nMaking a new Feature dataset: %s"%dsNEO1)
		dest_fd = os.path.join(out_event_gdb, dsNEO1)
		arcpy.Delete_management(dest_fd)
		arcpy.CreateFeatureDataset_management(out_event_gdb, dsNEO1, projfile)
		NEO1fc = os.path.join(dest_fd,"%sa_union"%dsNEO1)

		logger.print2("\nUnioning AR_fin and NATD_fin... (this might take a few minutes)")
		arcpy.analysis.Union(in_features=[ar_fc,natd_fc],out_feature_class=NEO1fc,join_attributes="ALL",cluster_tolerance=None,gaps="GAPS")
		logger.print2("\tDone!")

		logger.print2("\nAdding NEO_ inventory fields")
		for field, field_info in neofields.items():
			fname = "NEO_%s"%field # eg. NEO_YRSOURCE
			logger.print2("\tAdding %s"%fname)
			ftype = field_info[0]
			if ftype == 'TEXT':
				flength = field_info[1]
				arcpy.AddField_management(in_table = NEO1fc, field_name = fname, field_type = ftype, field_length = "%s"%flength)		
			else: # for 'FLOAT','SHORT', etc.
				arcpy.AddField_management(in_table = NEO1fc, field_name = fname, field_type = ftype)
		logger.print2("\tDone!")


	if 'NEO2' in step_list:
		logger.print2("\n\n#########    NEO2. Populate NEO_ inventory fields ##########\n")
		
		last_fc = os.path.join(out_event_gdb,dsNEO1,"%sa_union"%dsNEO1)

		logger.print2("\nMaking a new Feature dataset: %s"%dsNEO2)
		dest_fd = os.path.join(out_event_gdb, dsNEO2)
		arcpy.Delete_management(dest_fd)
		arcpy.CreateFeatureDataset_management(out_event_gdb, dsNEO2, projfile)
		NEO2fc = os.path.join(dest_fd,dsNEO2)

		logger.print2("\nCopying over to %s dataset"%dsNEO2)
		arcpy.CopyFeatures_management(in_features=last_fc,out_feature_class=NEO2fc)

		# get fieldnames
		f = [str(f.name).upper() for f in arcpy.ListFields(NEO2fc)] # that is all fieldnames
		ar_fields = [i for i in f if i.startswith('AR_')]
		natd_fields = [i for i in f if i.startswith('NATD_')]

		# First, select where only AR data exists and populate NEO fields with that
		ar_only_sql = "FID_NATD_fin = -1"
		logger.print2("\nUpdating NEO_ fields where only AR data exists")
		with arcpy.da.UpdateCursor(NEO2fc, f, ar_only_sql) as cursor:
			for row in cursor:
				for ar_f in ar_fields:
					neo_f = "NEO_%s"%ar_f[3:]
					row[f.index(neo_f)] = row[f.index(ar_f)]
				cursor.updateRow(row)
		logger.print2("\tDone!")

		# Secondly, select where only NATD data exists and populate NEO fields with that
		natd_only_sql = "FID_AR_fin = -1"
		logger.print2("\nUpdating NEO_ fields where only NATD data exists")
		with arcpy.da.UpdateCursor(NEO2fc, f, natd_only_sql) as cursor:
			for row in cursor:
				for natd_f in natd_fields:
					neo_f = "NEO_%s"%natd_f[5:]
					row[f.index(neo_f)] = row[f.index(natd_f)]
				cursor.updateRow(row)
		logger.print2("\tDone!")

		# lastly, where the two intersect
		ar_natd_overlap_sql = "FID_AR_fin > -1 AND FID_NATD_fin > -1"
		ar_only_fields = ['SILVSYS','SPCOMP','PLANFU','YIELD','SGR','LEADSPC'] # these fields will be updated only from AR fields
		latest_only_fields = ['SOURCE','YRDEP','DEVSTAGE','STKG','YRORG','AGE','HT','CCLO','DEPTYPE']
		logger.print2("\nUpdating rest of the NEO_ fields")
		with arcpy.da.UpdateCursor(NEO2fc, f, ar_natd_overlap_sql) as cursor:
			for row in cursor:
				ar_yrsource = row[f.index('AR_YRSOURCE')] if row[f.index('AR_YRSOURCE')] != None else 0
				natd_yrsource = row[f.index('NATD_YRSOURCE')] if row[f.index('NATD_YRSOURCE')] != None else 0
				if ar_yrsource == 0 and natd_yrsource == 0:
					# this is a special case where only SGR values exists (AR_SGR)
					yrsource = None # don't update yrsource
					row[f.index('NEO_SGR')] = row[f.index('AR_SGR')]
				# case where AR data is more recent
				elif ar_yrsource > natd_yrsource: 
					yrsource = ar_yrsource
					for field in latest_only_fields:
						ar_val = row[f.index('AR_%s'%field)]
						if ar_val != None:
							row[f.index('NEO_%s'%field)] = ar_val
						else:
							row[f.index('NEO_%s'%field)] = row[f.index('NATD_%s'%field)]
				# case where NATD data is more recent
				elif ar_yrsource <= natd_yrsource: # if both AR event and NATD event happens on the same year, NATD trumps
					yrsource = natd_yrsource
					for field in latest_only_fields:
						natd_val = row[f.index('NATD_%s'%field)]
						if natd_val != None:
							row[f.index('NEO_%s'%field)] = natd_val
						else:
							row[f.index('NEO_%s'%field)] = row[f.index('AR_%s'%field)]

				# the following fields will completely dependent on AR_ fields whether AR_YRSOURCE is the latest or not
				for field in ar_only_fields:
					row[f.index('NEO_%s'%field)] = row[f.index('AR_%s'%field)]

				# deptype is also a special one. if the latest AR_DEPTYPE is 'UNKNOWN', use NATD_DEPTYPE
				if ar_yrsource >= natd_yrsource:
					if row[f.index('AR_DEPTYPE')] == 'UNKNOWN' and row[f.index('NATD_DEPTYPE')] not in [None,'']:
						row[f.index('NEO_DEPTYPE')] = row[f.index('NATD_DEPTYPE')]

				row[f.index('NEO_YRSOURCE')] = yrsource
				cursor.updateRow(row)
		logger.print2("\tDone!")


	# I could've done this for all previous steps...
	last_fc = os.path.join(out_event_gdb,dsNEO2,dsNEO2)
	dest_fd = os.path.join(out_event_gdb, dsNEO3)
	NEO3fc = os.path.join(dest_fd,dsNEO3)
	if 'NEO3' in step_list:
		logger.print2("\n\n#########     NEO3. Union with MU Boundary    ##########\n")

		logger.print2("\nMaking a new Feature dataset: %s"%dsNEO3)
		arcpy.Delete_management(dest_fd)
		arcpy.CreateFeatureDataset_management(out_event_gdb, dsNEO3, projfile)

		logger.print2("\nUnioning with MU Boundary fc...")
		arcpy.analysis.Union(in_features=[last_fc,boundary_fc],out_feature_class=NEO3fc,join_attributes="ALL",cluster_tolerance=None,gaps="GAPS")
		logger.print2("\tDone!")

		logger.print2("\nDeleting empty polygons generated by the Union tool")
		with arcpy.da.UpdateCursor(NEO3fc, ['FID_NEO2'], "FID_NEO2 = -1") as cursor:
			for row in cursor:
				cursor.deleteRow()
	### NOTE THAT THE ABOVE STEP COULD CREATE SELF-INTERSECTS: this can be dealt with during the last clean-up stage.

	# next step
	last_fc = NEO3fc
	dest_fd = os.path.join(out_event_gdb, dsNEO4)
	NEO4fc_a = os.path.join(dest_fd,"%sa_dislv"%dsNEO4)
	NEO4fc_b = os.path.join(dest_fd,"NEO_fin")
	if 'NEO4' in step_list:
		logger.print2("\n\n#########     NEO4. Dissolve, Multi to Single and Eliminate    ##########\n")

		logger.print2("\nMaking a new Feature dataset: %s"%dsNEO4)
		arcpy.Delete_management(dest_fd)
		arcpy.CreateFeatureDataset_management(out_event_gdb, dsNEO4, projfile)

		logger.print2("\nRunning Dissolve (and deleting unnecessary fields)...")
		keep_fields = [f.name for f in arcpy.ListFields(last_fc) if f.name.startswith("NEO_")]
		keep_fields.append("INV_NAME")
		arcpy.management.Dissolve(in_features=last_fc,out_feature_class=NEO4fc_a,dissolve_field=keep_fields,statistics_fields=None,multi_part="SINGLE_PART")

		# do I need to do multi to single after that dissolve? - the answer is NO! Dissolve with single part setting does that for me.

		# Eliminate polys 
		logger.print2("\nRunning Eliminate anything less than %sm2"%eliminate_sqm)
		elim_select_sql = "SHAPE_AREA < %s"%eliminate_sqm
		arcpy.MakeFeatureLayer_management(NEO4fc_a, "elimlayer1")
		arcpy.SelectLayerByAttribute_management("elimlayer1", "NEW_SELECTION",elim_select_sql)
		arcpy.management.Eliminate(in_features="elimlayer1",out_feature_class=NEO4fc_b,selection="AREA",ex_where_clause="")

		# delete less than Xm2 (island polygons that didn't get eliminated)
		logger.print2("\nDeleting anything less than %sm2 (rest of the small polys that didn't get eliminated)"%eliminate_sqm)
		with arcpy.da.UpdateCursor(NEO4fc_b,["SHAPE_AREA"],elim_select_sql) as cursor:
			for row in cursor:
				cursor.deleteRow()
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
	step_list = ['NEO4']

	if step_list == 'ALL':
		step_list = ['NAT1','NAT2','NAT3','AR1','AR2','AR2-1','AR3','AR4','AR5','AR5-2','AR6','NEO1','NEO2','NEO3','NEO4']


	######### logfile stuff

	tool_shortname = '03Make_Event_Layer' # the output logfile will include this text in its filename.

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