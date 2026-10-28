# prerequisite:
# Must already have run SOA2_01 create base hex per MU - must already have a gdb that contains layers such as f_443_base

# expect this to take about 3 mins per FMU to run.

# workflow:
# - loop through the mu_list


# note that this script does not overwrite. You can run it on top of existing gdb and it will create only the fcs that is not already created.

import arcpy
import os

arcpy.env.overwriteOutput = True
arcpy.env.XYTolerance = "0.01 Meters" # by default, it is 0.001 meters, which can generate 1mm-wide overlaps and gaps. So 0.01m is preferred.
projfile = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"MNRLambert_d.prj") # this works for all scripts that are one folder level deep. eg. scripts/sqlite/script.py

def hexagonizer(hex_base_gdb,out_gdb,join_info,mu_list,express_run):

	arcpy.env.workspace = hex_base_gdb

	# loop through mu
	logger.print2("List of MUs:\n%s"%mu_list)
	logger.print2("List of joining fcs:\n%s"%join_info.keys())
	logger.print2("\nLooping through each MU")
	for muno_txt in mu_list:
		logger.print2("\n- Working on %s"%muno_txt)
		muno_int = int(muno_txt)

		# make a new feature dataset with MNR Lambert Conformal Conic Projection
		DS_name = 'f_%s'%muno_txt
		DS_fullpath = os.path.join(out_gdb,DS_name)
		DS_exists = False
		try:
			if arcpy.Describe(DS_fullpath).dataType.lower() == "featuredataset": DS_exists = True
		except:
			# will give OSError if the path doesn't exist.
			pass

		if DS_exists:
			logger.print2(" -- %s (feature dataset) already exists"%DS_name)
		else:
			logger.print2(" -- Generating dataset: %s..."%DS_name)
			# find the projection file location
			projfile = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"MNRLambert_d.prj")
			if not os.path.isfile(projfile):
				# if the file doesn't exist, show error
				arcpy.AddError("Can't find MNRLambert_d.prj file at the parent folder of %s"%__file__)
				raise
			arcpy.Delete_management(DS_name)
			arcpy.CreateFeatureDataset_management(out_gdb, DS_name, projfile)

		# loop through the join_info dictionary
		for layer_type, info in join_info.items():
			join_full_path = info['path']
			join_full_path = join_full_path.replace('$MUNO$',muno_txt)
			join_sql = info['sql']
			join_include_field_list = info['keepf']
			output_suffix = info['suffix']

			# prepare output fc name and path (will be used later during spatial join)
			out_fc_name = 'f_%s_%s'%(muno_txt,output_suffix)
			out_fc_fullpath = os.path.join(out_gdb,DS_name,out_fc_name)

			# only run if the output doesn't already exists.
			outfc_already_exists = arcpy.Exists(out_fc_fullpath)
			if outfc_already_exists:
				logger.print2(" -- %s already exists"%out_fc_name)
			else:
				# make feature layer with only the join_include_field_list visible. (cause deleting them later takes way too long)
				logger.print2(" -- joining [%s]"%layer_type)
				logger.print2("\tCreating a temporary layer")
				fields= arcpy.ListFields(join_full_path)
				fieldinfo = arcpy.FieldInfo()
				for field in fields:
					if field.name.upper() in join_include_field_list:
						fieldinfo.addField(field.name, field.name, "VISIBLE", "NONE")
					else:
						fieldinfo.addField(field.name, field.name, "HIDDEN", "NONE")
				# if there is an sql
				if join_sql != None:
					join_sql = join_sql.replace('$MUNO_SQL$','MUNO = %s'%muno_int)
					logger.print2("\tSelect from %s WHERE %s"%(layer_type,join_sql))				
					arcpy.management.MakeFeatureLayer(join_full_path, "join_lyr", join_sql, field_info=fieldinfo)
					num_selected = int(arcpy.management.GetCount("join_lyr")[0])
					logger.print2("\t%s records selected"%num_selected)
				else:
					arcpy.management.MakeFeatureLayer(join_full_path, "join_lyr", field_info=fieldinfo)

				# run spatial join
				target_fc = 'f_%s_base'%muno_txt # eg. f_443_base found in hex_base_gdb
				logger.print2("\tRunning Spatial Join. out_fc_name = %s"%out_fc_name)
				arcpy.analysis.SpatialJoin(target_features=target_fc, join_features="join_lyr", out_feature_class=out_fc_fullpath, join_operation="JOIN_ONE_TO_ONE", join_type="KEEP_COMMON", match_option="HAVE_THEIR_CENTER_IN")

				# delete extra fields
				if not express_run:
					delete_field_lst = ['SHAPE_AREA_1','SHAPE_LENGTH_1']
					logger.print2("\tClening up - deleting %s"%delete_field_lst)
					arcpy.management.DeleteField(out_fc_fullpath, delete_field_lst)



	logger.print2("\nDone!")



if __name__ == '__main__':
	
	# gather inputs
	hex_base_gdb = r'C:\Users\KimDan\Government of Ontario\Forest Explorer - Data\E\SOA2\SOA_CC\Hexbase_CC.gdb' # output from 02 script run. will have layers such as 'f_443' and 'f_816'
	out_gdb = r'C:\Users\KimDan\Government of Ontario\Forest Explorer - Data\E\SOA2\SOA_CC\SOA2_CC.gdb' # must already exist as an empty gdb

	# probably leave these as is
	ARAR_path = r'C:\Users\KimDan\Government of Ontario\Forest Explorer - Data\D\AR\AnalysisReadyAR.gdb'
	ARI_path = r'C:\Users\KimDan\Government of Ontario\Forest Explorer - FRO\FRO2026\02InventoryCleanUp\ARI_wFU.gdb'

	join_info = {

	# 'Region':		{'path': r'C:\Users\KimDan\Government of Ontario\Forest Explorer - Data\D\GeoData\FMU_FN_PARK_Boundary.gdb\MNR_Lamb\FMU_FN_PARK_Boundary_Simp2m',
	#  				'sql': "MFZ = 'Y'",
	#  				'keepf': ['LG_REGION','SFU_REGION'], # SFU_REGION exists in spcomp95
	#  				'suffix':'region',
	#  				},

	'Harvest':		{'path': os.path.join(ARAR_path,'Harvest','HRV_All_02_n_up'),
	 				'sql': "HARVCAT <> 'ROADROW' AND HARVMTHD <> 'THINCOM' AND SILVSYS = 'CC' AND $MUNO_SQL$",
	 				'keepf': ['BLOCKID', 'HARVCAT', 'SILVSYS', 'SGR', 'DSTBFU', 'TARGETFU', 'AR_YEAR','HARVMTHD'],
	 				'suffix':'hrv',
	 				},

	'Regen':		{'path': os.path.join(ARAR_path,'Regen','Regen_All_02_n_up'),
	 				'sql': '$MUNO_SQL$',
	 				'keepf': ['AR_YEAR', 'SP1', 'SP2', 'TRTMTHD1', 'TRTCAT1'],
	 				'suffix':'rgn',
	 				},

	'EST':			{'path': os.path.join(ARAR_path,'EST','EST_Y_02_n_up'),
	 				'sql': '$MUNO_SQL$',
	 				'keepf': ['ARDSTGRP', 'SILVSYS', 'AGEEST', 'YRDEP', 'DSTBFU', 'SGR', 'TARGETFU', 'TARGETYD', 'ESTFU', 'ESTYIELD', 'SPCOMP', 'HT', 'DENSITY', 'STKG', 'AR_YEAR'],
	 				'suffix':'est',
	 				},

	'SGR':			{'path': os.path.join(ARAR_path,'SGR','SGR_08_n_up'), 
	 				'sql': '$MUNO_SQL$',
	 				'keepf': ['AR_YEAR', 'SGR','TARGETFU','TARGETYD'],
	 				'suffix':'sgr',
	 				},

	'TND':			{'path': os.path.join(ARAR_path,'Tend','Tend_All_02_n_up'),
	 				'sql': '$MUNO_SQL$',
	 				'keepf': ['TRTMTHD1', 'TRTCAT1', 'PRODTYPE', 'RATE_AI', 'APPNUM', 'AR_YEAR',],
	 				'suffix':'tnd',
	 				},

	'SIP':			{'path': os.path.join(ARAR_path,'SIP','SIP_All_02_n_up'),
	 				'sql': '$MUNO_SQL$',
	 				'keepf': ['TRTMTHD1', 'TRTCAT1', 'PRODTYPE', 'RATE_AI', 'APPNUM', 'AR_YEAR'],
	 				'suffix':'sip',
	 				},

	'ARI25':		{'path': os.path.join(ARI_path,'FC$MUNO$'),
	 				'sql': "POLYTYPE = 'FOR'",
	 				# 'keepf': ['YRSOURCE','SOURCE','DEVSTAGE','YRDEP','SILVSYS','DEPTYPE','YRORG','LEADSPC','SPCOMP','AGE','HT','CCLO','STKG','SC','PLANFU','SGR','SFU','LGFU','PFT','ECONUM'],
	 				'keepf': ['ECONUM'],
	 				'suffix':'ARI25',
	 				},
	}



	mu_list = [
		'035', '060', '110', '120', '130', '140', '175', '177', '210', '220',
		'230', '280', '350', '360', '390', '406', '415', '421', '438', '443',
		'451', '490', '535', '574', '601', '615', '644', '680', '702', '754',
		'780', '796', '816', '840', '889', '898', '930', '966', '994'] # 39 MUs

	express_run = False # express run = don't delete extra fields. This is because ESRI takes forever to delete a field.



	######### logfile stuff

	tool_shortname = 'SOA2_02_hexagonize_all' # the output logfile will include this text in its filename.

	# importing libraries (only works if arclog.py file is located on the parent folder of this script)
	from datetime import datetime
	parent_d = os.path.split(os.path.split(__file__)[0])[0]
	sys.path.append(parent_d)
	from arclog import Print2 as p2

	# find full path where the logfile will be written
	folder_path = arcpy.Describe(out_gdb).path
	while arcpy.Describe(folder_path).dataType != 'Folder':
		folder_path = os.path.split(folder_path)[0]
	outfile = os.path.split(out_gdb)[1] + '_' + tool_shortname + '-LOG_' + datetime.now().strftime('%Y%m%d_%H%M') + '.txt'
	logfile_path = os.path.join(folder_path,outfile)

	# importing arclog in the parent directory
	logger = p2(logfile_path)

	##########

	# run the main function(s)
	hexagonizer(hex_base_gdb,out_gdb,join_info,mu_list,express_run)

	# finish writing the logfile
	logger.log_close()