# ready to use!
# aka INV_CLEANER_02
# check if the outcome of the 01 tool has all the standard field.
# copy the template - rename it to something like FC035_standardf
# this is mostly just a simple check and append tool, 
# BUT in the future, when using a T2 inventory, I will need to modify this script.

field_types = {
	'ARI_ID': ['SmallInteger','Integer'], # not a mandatory field - will be populated
	'POLYID': ['String'],
	'POLYTYPE': ['String'],
	'OWNER': ['String'],
	'YRSOURCE': ['SmallInteger','Integer'],
	'SOURCE': ['String'],
	'FORMOD': ['String'],
	'DEVSTAGE': ['String'],
	'YRDEP': ['SmallInteger','Integer'],
	'DEPTYPE': ['String'],
	'INCIDSPC': ['String'],
	'VERT': ['String'],
	'HORIZ': ['String'],
	'PRI_ECO': ['String'],
	'ACCESS1': ['String'],
	'MGMTCON1': ['String'],
	'STORY': ['String'], # not a mandatory field, but will be appended if values are available
	'YRORG': ['SmallInteger','Integer'],
	'LEADSPC': ['String'],
	'SPCOMP': ['String'],
	'AGE': ['SmallInteger','Integer'],
	'HT': ['Single','Double'],
	'CCLO': ['SmallInteger','Integer'],
	'STKG': ['Single','Double'],
	'SC': ['SmallInteger','Integer'],
	'MANAGED': ['String'],
	'SMZ': ['String'],
	'OMZ': ['String'],
	'PLANFU': ['String'],
	'AU': ['String'],
	'AVAIL': ['String'],
	'SILVSYS': ['String'],
	'NEXTSTG': ['String'],
	'YIELD': ['String'],
	'SGR': ['String'],
	'HA': ['Single','Double'], # not a mandatory field - will be populated
	'MUNO': ['SmallInteger','Integer'],	# not a mandatory field - will be populated
	}


non_mand_fields = ['ARI_ID','STORY','HA','MUNO']
mand_fields = [f for f in field_types.keys() if f not in non_mand_fields]


import arcpy
import os
arcpy.env.overwriteOutput = True
projfile = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"MNRLambert_d.prj")



def clean_inv02(input_clean01_inv,output_gdb,ARI_template,boundary_fc,mu_list,fc_suffix,step_list):
	
	# make sure all the MUs in mu_list exists
	last_mu_list = [f"{mu}{fc_suffix}".upper() for mu in mu_list]
	input_fcs = common_func.find_all_fcs(input_clean01_inv)[0] # a list of names of all fcs in uppercase
	not_found = [mu for mu in last_mu_list if mu not in input_fcs]
	if len(not_found) > 0:
		err1 = "\n!!! The following MUs in your list are not found in the input gdb:\n%s"%not_found
		logger.print2(err1,'w')
		raise Exception(err1)

	# check the input fields - see if it has all the necessary fields.
	if 'Check_field' in step_list:
		arcpy.env.workspace = input_clean01_inv	
		logger.print2("\nChecking fields...\nThe following fields should already exist in your input inventory:\n%s"%mand_fields)
		error_dict = {fc:[] for fc in last_mu_list}
		error_num = 0
		for fc in last_mu_list:
			logger.print2("\nChecking Field name and type of %s"%fc)
			existingFields = [str(f.name).upper() for f in arcpy.ListFields(fc)]
			missing_mf = list(set(mand_fields) - set(existingFields))
			existing_mf = list(set(mand_fields) & set(existingFields))
			if len(missing_mf) > 0:
				error_num += 1
				error_msg = "Missing %s"%missing_mf
				error_dict[fc].append(error_msg)
				logger.print2("\n\t%s"%error_msg, 'w')

			# check field types - just for text fields
			existing_field_n_types = {f.name.upper():f.type for f in arcpy.ListFields(fc) if f.name.upper() in existing_mf}
			for fname, ftype in existing_field_n_types.items():
				if ftype not in field_types[fname]:
					error_num += 1
					error_msg = "Wrong field type on %s: %s instead of %s"%(fname,ftype,field_types[fname])
					error_dict[fc].append(error_msg)
					logger.print2("\n\t%s"%error_msg, 'w')
		# logger.print2(str(error_dict))

	# check boundary_fc
	if not arcpy.Exists(boundary_fc):
		err2 = "\n!!! the boundary_fc doesn't exist! Check this path:\n%s"%boundary_fc
		raise Exception(err2)
	# grab the tabular info of boundary_fc in pandas df
	boundary_df = common_func.fc_to_pandas(boundary_fc)

	# step/dataset names (this is handy when one of the steps fail and you don't want to start from the beginning)
	dsG = 'g_standardfield' # if you change this, you must also change para variable of 04 script
	# dsG = 'test_standardfield'

	# names of all fcs to be generated
	stepG_fcs = {mu:"%s_%s"%(mu,dsG) for mu in mu_list} # eg. {"FC421": "FC421_g_standardfield",...}


	# Part G
	# copy the ARI template - rename it to something like FC035_g_standardf
	# append last fc to the new template
	# populate ARI_ID, MUNO and HA
	if 'G' in step_list:
		logger.print2("\n\n#########   G. Standardize fields using template  ##########\n")
		logger.print2("Making a new Feature dataset: %s"%dsG)
		arcpy.Delete_management(os.path.join(output_gdb,dsG))
		arcpy.CreateFeatureDataset_management(output_gdb, dsG, projfile)
		dest_fd = os.path.join(output_gdb, dsG)

		for index, mu in enumerate(mu_list):
			logger.print2("Working on %s"%mu)
			new_fc_name = os.path.join(dest_fd,stepG_fcs[mu])

			logger.print2("\tCopying and renaming the empty ARI template fc")
			arcpy.CopyFeatures_management(in_features=ARI_template,out_feature_class=new_fc_name)

			logger.print2("\tAppending %s to %s"%(mu,stepG_fcs[mu]))
			app_out = arcpy.management.Append(inputs=last_mu_list[index], target=new_fc_name, schema_type="NO_TEST")
			append_count = int(app_out.getOutput("appended_row_count"))
			logger.print2("\t\t%s records appended"%append_count)
			if append_count < 1:
				logger.print2("!!!!!!!!!!   Something went wrong   !!!!!!!!!!",'w')
				logger.print2("\n\tTry manually appending %s. It's likely cuased by mismatch of field length on one of the text fields\n"%mu)

			# find MUNO
			muno = 0
			filtered_df = boundary_df[boundary_df["INV_NAME"].str.upper()==mu.upper()] # for example, WHERE INV_NAME = 'fc780' but without case sensitivity
			try:
				muno = filtered_df["FMU_CODE"].tolist()[0] # this errors out (IndexError) if the above df filter didn't yield any result
				logger.print2("\tMUNO = %s"%muno)
			except IndexError:
				logger.print2("\t!!! Cannot find MUNO of %s\nCheck boundary_fc and make sure INV_NAME has a value '%s'"%(mu,mu),'w')
				logger.print2("\tThe script will fill out the MUNO as 0 for now...")

			# populate ARI_ID, Ha and MUNO
			muno = int(muno)
			logger.print2("\tPopulating ARI_ID, Ha and MUNO")
			with arcpy.da.UpdateCursor(new_fc_name, ['OID@','ARI_ID','MUNO','HA','SHAPE@AREA']) as cursor:
				for row in cursor:
					oid = row[0]
					ha = row[-1]/10000
					row[1] = oid
					row[2] = muno
					row[3] = ha
					cursor.updateRow(row)	

			logger.print2("\tDone!!")







if __name__ == '__main__':
	
	# gather inputs
	# input_clean01_inv = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - FRO\FRO2026\02InventoryCleanUp\InvCleaner01_test.gdb' # path to cleaner 01 output gdb
	input_clean01_inv = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - FRO\FRO2026\02InventoryCleanUp\InvCleaner01_fin.gdb' # path to cleaner 01 output gdb
	ARI_template = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - FRO\FRO2026\02InventoryCleanUp\AnalysisReadyInventory.gdb\ARI_Template'
	# ARI_template = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\D\GeoData\PIAMMar2024.gdb\ARI_template' # back up copy

	output_gdb = input_clean01_inv # output gdb must already exist. output gdb can be same as input

	boundary_fc = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\D\GeoData\PIAMMar2024.gdb\FMU_FN_PARK_Boundary_Simp2m'

	# mu_list = ['FC421'] # this must be identical to the feature class names within PIAM.gdb (upper/lower case doesn't matter)
	mu_list = ['FC035', 'FC060', 'FC110', 'FC120', 'FC130', 'FC140', 'FC175', 'FC177', 'FC210', 'FC220',
			'FC230', 'FC280', 'FC350', 'FC360', 'FC390', 'FC406', 'FC415', 'FC421', 'FC438', 'FC443',
			'FC451', 'FC490', 'FC535', 'FC574', 'FC601', 'FC615', 'FC644', 'FC680', 'FC702', 'FC754',
			'FC780', 'FC796', 'FC816', 'FC840', 'FC889', 'FC898', 'FC930', 'FC966', 'FC994',
			'FarNorth_BerensRiver', 'FarNorth_CatLake', 'FarNorth_ConstanceL', 'FarNorth_MooseCree',
			'FarNorth_NorthCentral', 'FarNorth_Northeast', 'FarNorth_Northwest', 'FarNorth_Taash',
			'Lake_Superior_Islands', 'Lake_Nipigon_Islands', 'Park_EagleSnowshoe', 'Park_LitGrRap',
			'Park_LkSuperior', 'Park_Quetico', 'Park_WCaribou', 'Park_Wabakimi', 'Park_pukaskwa'] # cleanup 02 - should take about 15mins to run everything
	# mu_list = ['FC490','FC702']

	fc_suffix = '_f_clip_to_mu' # depends on cleaner 01 tool output. suffix of the step F output FC names

	step_list = ['Check_field','G'] # First, run 'Check_field' only, then if everything's good, run step G
	# step_list = ['Check_field']

	######### logfile stuff

	tool_shortname = 'INV_CLEANER_02' # the output logfile will include this text in its filename.

	# importing libraries (only works if arclog.py file is located on the parent folder of this script)
	from datetime import datetime
	parent_d = os.path.split(os.path.split(__file__)[0])[0]
	sys.path.append(parent_d)
	from arclog import Print2 as p2
	import common_func

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
	clean_inv02(input_clean01_inv,output_gdb,ARI_template,boundary_fc,mu_list,fc_suffix,step_list)

	# finish writing the logfile
	logger.log_close()