# work in progress...
# this script is ideally run on inventories after 04_transplant_event_layer.py, but should be able to run on any existing inventories
#   as long as the feature classes are named the same way (eg. FC421, Lake_Superior_Islands, etc.) and mandatory fields exists.
#   mandatory fields are those in field_types dictionary of a02_standardize_using_template.py script

owner_crosswalk ={ # in the order of most occurring to least
	'CROWN':['1'],
	'PATENT':['3','4','8'],
	'PARKS':['5','7'],
	'FN':['6'],
	'PATCRN':['2'],
	'FEDRES':['9']}


import arcpy
import os, csv
from a02_standardize_using_template import field_types as invfields_dict
invfields = list(invfields_dict.keys())

arcpy.env.overwriteOutput = True
arcpy.env.XYTolerance = "0.01 Meters" # by default, it is 0.001 meters, which can generate 1mm-wide overlaps and gaps. So 0.01m is preferred.
projfile = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"MNRLambert_d.prj") # this works for all scripts that are one folder level deep. eg. scripts/sqlite/script.py


def clean_up_tabular(input_inv_gdb,output_inv_gdb,mu_list,current_year,fix_list,step_list):

	# step A
	step = 'all_%s'%current_year
	ds = os.path.join(output_inv_gdb,step) # eg. .../AnalysisReadyInventory.gdb/a/
	a1_fc_suffix = ''
	if 'A' in step_list:
		logger.print2("\n\n#########   Step A: PREP - Copy and Add Fields  ##########\n")
		arcpy.env.workspace = input_inv_gdb
		logger.print2("Making a new Feature dataset: %s"%step)
		arcpy.Delete_management(os.path.join(output_inv_gdb,step))
		arcpy.CreateFeatureDataset_management(output_inv_gdb, step, projfile)

		for mu in mu_list:
			logger.print2("\nWorking on %s"%mu)
			out_fcname = "%s%s"%(mu,a1_fc_suffix) # eg. FC421_a_intersect
			out_fc_path = os.path.join(ds,out_fcname)

			logger.print2("\tCopying over the data from %s"%os.path.split(input_inv_gdb)[1])
			arcpy.CopyFeatures_management(in_features=mu,out_feature_class=out_fc_path)
			fields = [str(f.name).upper() for f in arcpy.ListFields(out_fc_path)] # all the fields, uppercase

			# select from event layer where INV_NAME = inventory fc name, then intersect
			logger.print2("\tAdding Fields (ORG_POLYID and ORG_OWNER)")
			arcpy.AddField_management(in_table = out_fc_path, field_name = 'ORG_POLYID', field_type = "TEXT", field_length = "35")
			arcpy.AddField_management(in_table = out_fc_path, field_name = 'ORG_OWNER', field_type = "TEXT", field_length = "5")
			# arcpy.AddField_management(in_table = out_fc_path, field_name = 'T_CHANGE', field_type = "TEXT", field_length = "255")
			logger.print2("\tDone!!")

			# temporarily add delete HORIZ field script here
			if 'HORIZ' in fields:
				logger.print2("\tDeleting Field: HORIZ")
				arcpy.management.DeleteField(out_fc_path,'HORIZ')


	# step B
	if 'B' in step_list:
		logger.print2("\n\n#########   Step B: Update / Correct values  ##########\n")
		arcpy.env.workspace = output_inv_gdb

		fix_item_list = list(fix_list.keys())

		for mu in mu_list:
			logger.print2("\nWorking on %s"%mu)
			fcname = "%s%s"%(mu,a1_fc_suffix) # eg. FC421
			# f = [str(f.name).upper() for f in arcpy.ListFields(fcname)] # all the fields, uppercase

			# work on POLYID
			i = 'POLYID' # i stands for current item
			if i in fix_item_list:
				logger.print2("\t%s: %s"%(i,fix_list[i][0]))
				f = ['OID@','POLYID','ORG_POLYID']
				with arcpy.da.UpdateCursor(fcname, f) as cursor:
					for row in cursor:
						org_polyid = row[1]
						new_polyid = row[0]
						row[2] = org_polyid
						row[1] = new_polyid
						cursor.updateRow(row)

			# work on HA
			i = 'HA' # i stands for current item
			if i in fix_item_list:
				logger.print2("\t%s: %s"%(i,fix_list[i][0]))
				f = ['SHAPE_AREA','HA']
				with arcpy.da.UpdateCursor(fcname, f) as cursor:
					for row in cursor:
						ha = round(row[0]/10000,3)
						row[1] = ha
						cursor.updateRow(row)

			# # work on POLYTYPE
			# i = 'POLYTYPE' # i stands for current item
			# if i in fix_item_list:
			# 	logger.print2("\t%s: %s"%(i,fix_list[i][0]))
			# 	counter = 0
			# 	f = ['POLYTYPE','SPCOMP','AGE']
			# 	sql = "POLYTYPE IS NULL OR POLYTYPE NOT IN ('WAT','DAL','GRS','ISL','UCL','BSH','RCK','TMS','OMS','FOR')"
			# 	with arcpy.da.UpdateCursor(fcname, f, sql) as cursor:
			# 		for row in cursor:
			# 			counter += 1
			# 			spcomp = row[1]
			# 			age = row[0]
			# 			if spcomp not in [None,''] and age not in [None,'']:
			# 				row[0] = 'FOR'
			# 			else:
			# 				row[0] = 'UCL'
			# 			cursor.updateRow(row)
			# 	if counter > 0:
			# 		logger.print2("\tFixed %s records"%counter)

			# work on SPCOMP-fix
			i = 'SPCOMP_fix' # i stands for current item
			if i in fix_item_list:
				logger.print2("\t%s: %s"%(i,fix_list[i][0]))
				counter = 0
				f = ['SPCOMP','MUNO']
				sql = "POLYTYPE = 'FOR' AND CHAR_LENGTH(SPCOMP) < 6"
				with arcpy.da.UpdateCursor(fcname, f, sql) as cursor:
					for row in cursor:
						counter += 1
						spcomp = row[0].upper()
						muno = row[1]
						if spcomp == 'BF':
							row[0] = 'BF 100'
						elif spcomp == 'G' and muno == 443:
							row[0] = 'SB  60PJ  40'
						cursor.updateRow(row)
				if counter > 0:
					logger.print2("\t\tFixed %s records"%counter)

			# work on SPCOMP-upper
			i = 'SPCOMP_upper' # i stands for current item
			if i in fix_item_list:
				logger.print2("\t%s: %s"%(i,fix_list[i][0]))
				f = ['SPCOMP','LEADSPC']
				sql = "POLYTYPE = 'FOR' AND SPCOMP IS NOT NULL AND LEADSPC IS NOT NULL"
				with arcpy.da.UpdateCursor(fcname, f, sql) as cursor:
					for row in cursor:
						row[0] = row[0].upper()
						row[1] = row[1].upper()
						cursor.updateRow(row)

			# work on YEAR_fields
			i = 'YEAR_fields' # i stands for current item
			if i in fix_item_list:
				logger.print2("\t%s: %s"%(i,fix_list[i][0]))
				counter = 0
				f = ['POLYTYPE','YRDEP','YRORG','AGE'] 
				with arcpy.da.UpdateCursor(fcname, f) as cursor:
					for row in cursor:
						polytype = row[0]
						if polytype != 'FOR':
							row[1] = None
							row[2] = None
						else:
							yrorg = row[2]
							age = row[3]
							if yrorg in [None,0] or yrorg < 1600:
								counter += 1
								if age != None and age > 0 and age < 255:
									row[2] = current_year - age
								else:
									row[2] = 1600
						cursor.updateRow(row)
				if counter > 0:
					logger.print2("\t\tFixed %s records"%counter)

			# work on AGE
			i = 'AGE' # i stands for current item
			if i in fix_item_list:
				age_cap = fix_list[i][1] # 255 but can be adjusted
				logger.print2("\t%s: %s"%(i,fix_list[i][0]))
				f = ['POLYTYPE','YRORG','AGE']
				sql = "POLYTYPE='FOR'"
				with arcpy.da.UpdateCursor(fcname, f, sql) as cursor:
					for row in cursor:
						yrorg = row[1]
						age = current_year - yrorg
						if age > age_cap:
							age = age_cap
						row[2] = age
						cursor.updateRow(row)

			# work on SOURCE
			i = 'SOURCE' # i stands for current item
			if i in fix_item_list:
				logger.print2("\t%s: %s"%(i,fix_list[i][0]))
				counter = 0
				f = ['SOURCE']
				with arcpy.da.UpdateCursor(fcname, f) as cursor:
					for row in cursor:
						counter += 1
						orig_source = row[0].upper().strip() if row[0] != None else None
						if orig_source in [None,'']:
							source = None
						elif orig_source in ['DEPUPD','FIXED','UPDDEP']:
							source = 'SUPINFO'
						elif orig_source in ['UPDFTG','EST']:
							source = 'AR_EST'
						elif orig_source in ['FIREUPD','UPDFIRE','UPDFIRE2']:
							source = 'NAT_FIRE'
						elif orig_source in ['HRV','UPDHARV']:
							source = 'AR_HRV'
						else:
							source = orig_source
							counter -= 1 # if arrived here, it didn't need fixing
						row[0] = source
						cursor.updateRow(row)
				if counter > 0:
					logger.print2("\t\tFixed %s records"%counter)

			# work on DEPTYPE
			i = 'DEPTYPE' # i stands for current item
			if i in fix_item_list:
				logger.print2("\t%s: %s"%(i,fix_list[i][0]))
				counter = 0				
				f = ['POLYTYPE','DEPTYPE','DEVSTAGE']
				with arcpy.da.UpdateCursor(fcname, f) as cursor:
					for row in cursor:
						counter += 1						
						polytype = row[0]
						orig_deptype = row[1].upper().strip() if row[1] != None else None
						devstage = row[2]
						if polytype != 'FOR' and orig_deptype != None:
							deptype = None
						elif polytype == 'FOR' and orig_deptype == 'HARV':
							deptype = 'HARVEST'
						elif polytype == 'FOR' and orig_deptype in [None,'', '-']:
							if devstage == 'DEPHARV':
								deptype = 'HARVEST'
							else:
								deptype = 'UNKNOWN'
						else:
							deptype = orig_deptype # by default (also turns them into uppercase)
							counter -= 1 # if arrived here, it didn't need fixing
						row[1] = deptype
						cursor.updateRow(row)
				if counter > 0:
					logger.print2("\t\tFixed %s records"%counter)

			# work on DEVSTAGE
			i = 'DEVSTAGE' # i stands for current item
			if i in fix_item_list:
				logger.print2("\t%s: %s"%(i,fix_list[i][0]))
				counter = 0				
				f = ['POLYTYPE','DEPTYPE','DEVSTAGE']
				with arcpy.da.UpdateCursor(fcname, f) as cursor:
					for row in cursor:
						counter += 1						
						polytype = row[0]
						deptype = row[1]
						orig_devstage = row[2].upper().strip() if row[2] != None else None
						if polytype != 'FOR' and orig_devstage != None:
							devstage = None
						elif polytype == 'FOR' and orig_devstage.startswith('FTG'):
							devstage = "EST%s"%orig_devstage[3:] # eg. ESTPLANT
						else:
							devstage = orig_devstage # by default (also turns them into uppercase)
							counter -= 1 # if arrived here, it didn't need fixing
						row[2] = devstage
						cursor.updateRow(row)
				if counter > 0:
					logger.print2("\t\tFixed %s records"%counter)

			# work on OWNER (if OWNER IS NULL, I can't fix it automatically here)
			i = 'OWNER' # i stands for current item
			if i in fix_item_list:
				null_count = 0
				logger.print2("\t%s: %s"%(i,fix_list[i][0]))
				f = ['OWNER','ORG_OWNER']
				with arcpy.da.UpdateCursor(fcname, f) as cursor:
					for row in cursor:
						orig_owner = row[0]
						owner = orig_owner
						if orig_owner == None:
							owner = None
							null_count += 1
						else:
							for new_code, old_code in owner_crosswalk.items():
								if orig_owner in old_code:
									owner = new_code
									row[1] = orig_owner
									break
						row[0] = owner
						cursor.updateRow(row)
				if null_count > 0:
					logger.print2("\t\tThere are %s records where OWNER is NULL. (fix this manually)"%null_count)

			# work on NEXTSTG
			i = 'NEXTSTG' # i stands for current item
			if i in fix_item_list:
				logger.print2("\t%s: %s"%(i,fix_list[i][0]))
				counter = 0				
				f = ['NEXTSTG']
				sql = "POLYTYPE = 'FOR'"
				with arcpy.da.UpdateCursor(fcname, f, sql) as cursor:
					for row in cursor:
						orig_nextstg = row[0].upper().strip() if row[0] != None else None
						nextstg = orig_nextstg # by default
						if orig_nextstg != None:
							if orig_nextstg in ['CLEARCUT','CONVENT','CONVENTN']:
								counter += 1
								nextstg = 'STANDARDS'
							elif orig_nextstg in ['','FTG','NA','SNGLTREE']:
								counter += 1
								nextstg = None
							elif orig_nextstg == 'BLKSTRIP':
								counter += 1
								nextstg = 'BLOCKSTRIP'
						row[0] = nextstg
						cursor.updateRow(row)
				if counter > 0:
					logger.print2("\t\tFixed %s records"%counter)

			# work on MGMTCON1
			i = 'MGMTCON1' # i stands for current item
			if i in fix_item_list:
				logger.print2("\t%s: %s"%(i,fix_list[i][0]))
				counter = 0				
				f = ['MGMTCON1','POLYTYPE']
				with arcpy.da.UpdateCursor(fcname, f, sql) as cursor:
					for row in cursor:
						orig_mgmtcon = row[0].upper().strip() if row[0] != None else None
						polytype = row[1]
						mgmtcon = orig_mgmtcon # by default
						if polytype != 'FOR':
							if orig_mgmtcon not in [None,'ISLD']:
								counter += 1
								mgmtcon = None
						elif polytype == 'FOR':
							if orig_mgmtcon in [None,'NON','UPFR','U_PF']:
								counter += 1
								mgmtcon = 'NONE'
						row[0] = mgmtcon
						cursor.updateRow(row)
				if counter > 0:
					logger.print2("\t\tFixed %s records"%counter)



if __name__ == '__main__':
	
	# gather inputs
	input_inv_gdb = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - FRO\FRO2026\02InventoryCleanUp\Transplant_event.gdb' # output gdb must already exist and should contain feature classes in mu_list
	output_inv_gdb = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - FRO\FRO2026\02InventoryCleanUp\a05_clean_up_tabular.gdb' # must already exists. This is test
	# output_inv_gdb = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - FRO\FRO2026\02InventoryCleanUp\ARI_base.gdb' # must already exists. This is final
	current_year = 2025

	# mu_list values must be identical to the feature class names within PIAM.gdb (upper/lower case doesn't matter)
	mu_list = ['FC035', 'FC060', 'FC110', 'FC120', 'FC130', 'FC140', 'FC175', 'FC177', 'FC210', 'FC220',
			'FC230', 'FC280', 'FC350', 'FC360', 'FC390', 'FC406', 'FC415', 'FC421', 'FC438', 'FC443',
			'FC451', 'FC490', 'FC535', 'FC574', 'FC601', 'FC615', 'FC644', 'FC680', 'FC702', 'FC754',
			'FC780', 'FC796', 'FC816', 'FC840', 'FC889', 'FC898', 'FC930', 'FC966', 'FC994',
			'FarNorth_BerensRiver', 'FarNorth_CatLake', 'FarNorth_ConstanceL', 'FarNorth_MooseCree',
			'FarNorth_NorthCentral', 'FarNorth_Northeast', 'FarNorth_Northwest', 'FarNorth_Taash',
			'Lake_Superior_Islands', 'Lake_Nipigon_Islands', 'Park_EagleSnowshoe', 'Park_LitGrRap',
			'Park_LkSuperior', 'Park_Quetico', 'Park_WCaribou', 'Park_Wabakimi', 'Park_pukaskwa']
	mu_list = ['FC680','FC443','Lake_Superior_Islands'] # testing

	fix_list ={
	# fix item | Description 					| parameters if any
	'POLYID':	["POLYID values must be unique. Keep the original POLYID values in ORG_POLYID and repopulate POLYID with OBJECTID."], 
	'HA': ["Recalculating HA field"],
	# 'POLYTYPE':	["POLYTYPE must not be null. If NULL, check SPCOMP and AGE. If both populated, POLYTYPE='FOR' else 'UCL'"], # don't do this - if POLYTYPE is NULL, figure out what polytype it is (likely WAT)
	'SPCOMP_fix':	["FC175 has SPCOMP of 'Bf' and FC443 has SPCOMP of 'g'. Fixing these..."],
	'SPCOMP_upper':	["Turn all SPCOMP and LEADSPC values to upper character"],
	'YEAR_fields':	["YRDEP and YRORG values should be null when POLYTYPE<>FOR. YRORG should be greater than 1600 when POLYTYPE=FOR"],
	'AGE': ["AGE will be recalculated based on YRORG and will be capped at 255",255], # do this after fixing YRORG
	'SOURCE': ["SOURCE values will be recategorized, cleaned and capitalized."],
	'DEPTYPE': ["DEPTYPE should be NULL for non FOR polygons, and shouldn't be NULL,'', nor '-' for FOR polygons. DEPTYPE should be HARVEST when DEVSTAGE=DEPHARV"],
	'DEVSTAGE': ["DEVSTAGE should be NULL for non FOR polygons. DEVSTAGE of FTG~ should be changed to EST~"],
	'OWNER': ["Owner values are no longer numbers. Updating this to 2024 tech spec. Keeping the old OWNER value under ORIG_OWNER field."],
	'NEXTSTG': ["Cleaning up NEXTSTG. CONVENT is now STANDARDS"],
	'MGMTCON1': ["Cleaning up MGMTCON1. When POLYTYPE isn't FOR, it should be ISLD or NULL. When FOR, it should follow the coding scheme"],
	}

	# VERT and other OLT fields...
	# ARI_ID
	# AGE CLASS fields (add it at the next script)

	# step A is prep (copying over so this script doesn't overwrite the original. step B is fixing what's on the fix_list
	step_list = 'ALL'
	# step_list = ['B']

	if step_list == 'ALL':
		step_list = ['A','B']




	######### logfile stuff

	tool_shortname = '05CleanUp_Tabular' # the output logfile will include this text in its filename.

	# importing libraries (only works if arclog.py file is located on the parent folder of this script)
	from datetime import datetime
	parent_d = os.path.split(os.path.split(__file__)[0])[0]
	sys.path.append(parent_d)
	from arclog import Print2 as p2
	import common_func

	# find full path where the logfile will be written
	folder_path = arcpy.Describe(output_inv_gdb).path
	while arcpy.Describe(folder_path).dataType != 'Folder':
		folder_path = os.path.split(folder_path)[0]
	outfile = os.path.split(output_inv_gdb)[1] + '_' + tool_shortname + '-LOG_' + datetime.now().strftime('%Y%m%d_%H%M') + '.txt'
	logfile_path = os.path.join(folder_path,outfile)

	# importing arclog in the parent directory
	logger = p2(logfile_path)

	##########

	# run the main function(s)
	clean_up_tabular(input_inv_gdb,output_inv_gdb,mu_list,current_year,fix_list,step_list)

	# finish writing the logfile
	logger.log_close()