# prerequisite:
# Must already have run 02 create base hex per MU - must already have a gdb that contains layers such as f_443_base


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
	for mu in mu_list:
		muno_txt = mu[2:] # eg. when mu = 'FC040', then muno_txt = '040'
		logger.print2("\n- Working on %s"%mu)

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
	hex_base_gdb = r'C:\Users\KimDan\Government of Ontario\Caribou Explorer - CM1_3\Data\Analysis\Hexagon_Test\HexBase.gdb' # will have layers such as 'f_443' and 'f_816'
	out_gdb = r'C:\Users\KimDan\Government of Ontario\Caribou Explorer - CM1_3\Data\Analysis\Hexagon_Test\HexJoin.gdb' # must already exist
	ARAR_path = r'C:\Users\KimDan\Government of Ontario\Forest Explorer - Data\D\AR\AnalysisReadyAR.gdb'
	ARI_path = r'C:\Users\KimDan\Government of Ontario\Forest Explorer - FRO\FRO2026\02InventoryCleanUp\ARI_wFU.gdb'

	join_info = {
	'EventLayer': 	{'path':r'C:\Users\KimDan\Government of Ontario\Caribou Explorer - CM1_3\Data\Analysis\EventLayers\Event2002to2023.gdb\NEO4\NEO_fin',
					'fcname': None, # only if your 'path' is a gdb
					'sql': None, 
					'keepf': ['NEO_YRSOURCE', 'NEO_SOURCE', 'NEO_YRDEP', 'NEO_DEPTYPE', 'NEO_DEVSTAGE', 'NEO_STKG', 'NEO_YRORG', 'NEO_AGE', 'NEO_CCLO', 'NEO_SILVSYS', 'NEO_SPCOMP', 'NEO_PLANFU', 'NEO_YIELD', 'NEO_SGR', 'NEO_LEADSPC'], 
					'suffix':'event',
					},

	'Backcast':		{'path': r'C:\Users\KimDan\Government of Ontario\Caribou Explorer - CM1_3\Data\INV\backcast.gdb\MU$MUNO$', # $MUNO$ will be replaced by one of the items in the mu_list variable below (replaced by numbers - without the 'FC')
	 				'sql': None,
	 				'keepf': ['EVENT_LOG', 'ECONUM', 'LGAGE_2002', 'LGFU_GLSL_2002', 'LGFU_NER_2002', 'LGFU_NWR_2002','LGAGE_2023', 'LGFU_GLSL_2023', 'LGFU_NER_2023', 'LGFU_NWR_2023'],
	 				'suffix':'backcast',
	 				},

	'CaribRange':	{'path': r'C:\Users\KimDan\Government of Ontario\Forest Explorer - Data\D\GeoData\Caribou2024\Caribou20240426.gdb\CRB_Ranges_ALL', 
	 				'sql': None,
	 				'keepf': ['RANGE_NAME','RANGE_TYPE'],
	 				'suffix':'range',
	 				},	 	

	'spcomp95':		{'path': r'C:\Users\KimDan\Government of Ontario\Caribou Explorer - CM1_3\Data\Analysis\SpComp95\SPCOMP95_mod_v2026.gdb\SPCOMP95_wSFU', 
	 				'sql': None,
	 				'keepf': ['SPCOMP','SFU_REGION','ECONUM','SFU','PFT','LGFU'],
	 				'suffix':'spc95',
	 				},

	'Harvest':		{'path': os.path.join(ARAR_path,'Harvest','HRV_All_02_n_up'),
	 				'sql': None,
	 				'keepf': ['GRID_ID', 'FMU_CODE', 'BLOCKID', 'HARVCAT', 'SILVSYS', 'HARVMTHD', 'MGMTSTG', 'ESTAREA', 'SGR', 'DSTBFU', 'TARGETFU', 'TARGETYD', 'TRIAL', 'LOGMTHD', 'AR_YEAR'],
	 				'suffix':'hrv',
	 				},

	'Regen':		{'path': os.path.join(ARAR_path,'Regen','Regen_All_02_n_up'),
	 				'sql': None,
	 				'keepf': ['ESTAREA', 'AR_YEAR', 'SP1', 'SP2', 'TRTMTHD1', 'TRTCAT1', 'PLANTNO', 'ESTAREA2', 'AR_YEAR2', 'SP12', 'SP22'],
	 				'suffix':'rgn',
	 				},

	'EST':			{'path': os.path.join(ARAR_path,'EST','EST_Y_02_n_up'),
	 				'sql': None,
	 				'keepf': ['ARDSTGRP', 'SILVSYS', 'AGEEST', 'YRDEP', 'DSTBFU', 'SGR', 'TARGETFU', 'TARGETYD', 'ESTFU', 'ESTYIELD', 'SPCOMP', 'HT', 'DENSITY', 'STKG', 'AR_YEAR'],
	 				'suffix':'est',
	 				},

	'SGR':			{'path': os.path.join(ARAR_path,'SGR','SGR_08_n_up'),
	 				'sql': None,
	 				'keepf': ['AR_YEAR', 'SGR','TARGETFU','TARGETYD'],
	 				'suffix':'sgr',
	 				},

	'TND':			{'path': os.path.join(ARAR_path,'Tend','Tend_All_02_n_up'),
	 				'sql': None,
	 				'keepf': ['TRTMTHD1', 'TRTCAT1', 'PRODTYPE', 'RATE_AI', 'APPNUM', 'AR_YEAR',],
	 				'suffix':'tnd',
	 				},

	'SIP':			{'path': os.path.join(ARAR_path,'SIP','SIP_All_02_n_up'),
	 				'sql': None,
	 				'keepf': ['TRTMTHD1', 'TRTCAT1', 'PRODTYPE', 'RATE_AI', 'APPNUM', 'AR_YEAR'],
	 				'suffix':'sip',
	 				},

	'ARI25':		{'path': os.path.join(ARI_path,'FC$MUNO$'),
	 				'sql': "POLYTYPE = 'FOR'",
	 				'keepf': ['YRSOURCE','SOURCE','DEVSTAGE','YRDEP','SILVSYS','DEPTYPE','YRORG','LEADSPC','SPCOMP','AGE','HT','CCLO','STKG','SC','PLANFU','SGR','SFU','LGFU','PFT'],
	 				'suffix':'ARI25',
	 				},	 				
	}

	# add 2011 FRI T1
	# add KMB stuff as they come in
	# add RAP?



	mu_list = ['FC035', 'FC060', 'FC110', 'FC120', 'FC130', 'FC140', 'FC175', 'FC177', 'FC210', 'FC220',
			'FC230', 'FC280', 'FC350', 'FC360', 'FC390', 'FC406', 'FC415', 'FC421', 'FC438', 'FC443',
			'FC451', 'FC490', 'FC535', 'FC574', 'FC601', 'FC615', 'FC644', 'FC680', 'FC702', 'FC754',
			'FC780', 'FC796', 'FC816', 'FC840', 'FC889', 'FC898', 'FC930', 'FC966', 'FC994'] # 39 MUs
	mu_list = ['FC443','FC816']

	express_run = False



	######### logfile stuff

	tool_shortname = 'CM13_03_hexagonize_all' # the output logfile will include this text in its filename.

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