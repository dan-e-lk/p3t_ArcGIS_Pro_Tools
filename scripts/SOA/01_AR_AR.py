intro = """
version 1.0
AR_Master has many separate components. This script merges same type of activies together into one feature class. 
for example, all harvests 02 and greater into one feature class
Not all types of activities are included in this script.
	the script will append on FTG, RGN, and HRV.
	the script does not touch SIP, Roads and TND at the moment."""


import arcpy
import os, sys

class Ar_ar:
	def __init__(self, ar_master_path, arar_gdb_path, projfile, logger):
		self.logger = logger
		self.logger.print2(intro)
		self.ar_master_path = ar_master_path
		self.arar_gdb_path = arar_gdb_path
		self.projfile = projfile
		arcpy.env.workspace = ws = arar_gdb_path

	def harvest(self):
		# variables
		DS_name = "Harvest" # try to stick to the same DS name as the AR Master
		template = 'Harvest/Harvest_CC17'
		append_lst = [os.path.join(ar_master_path,DS_name,i) for i in ['Harvest_CC02','Harvest_SE02','Harvest_SE17','Harvest_SH02','Harvest_SH17']]
		new_fc_name = 'HRV_All_02_n_up' # if you change this, it will mess up the next script

		# create feature dataset
		self.logger.print2("\n## Working on %s"%DS_name)
		self.logger.print2("\tMaking new Feature dataset: %s"%DS_name)
		arcpy.Delete_management(DS_name)
		arcpy.CreateFeatureDataset_management(self.arar_gdb_path, DS_name, self.projfile)
		dest_feature_dataset = os.path.join(self.arar_gdb_path, DS_name)

		# start copying over the template
		harv_temp_path = os.path.join(self.ar_master_path,template)
		self.logger.print2("\tCopying over %s..."%template)
		arcpy.FeatureClassToFeatureClass_conversion(harv_temp_path, dest_feature_dataset, new_fc_name)

		# append all other ones to the new_fc_name. (do it on the Pro first then grab the python snippet)
		self.logger.print2("\tAppending the following FCs:\n%s"%append_lst)
		ap_input = ''
		for fc in append_lst:
			ap_input += "%s;"%fc
		arcpy.management.Append(inputs=ap_input, target=new_fc_name, schema_type="NO_TEST")
		self.logger.print2("\t%s complete!"%DS_name)


	def est(self):
		# variables
		DS_name = "EST" # try to stick to the same DS name as the AR Master
		template = 'FTG/FTGESTy17'
		append_lst = [os.path.join(ar_master_path,'FTG',i) for i in ['FTGy02','FTGy08']] # **
		new_fc_name = 'EST_Y_02_n_up'
		note = """
		Remember:
		These fields didn't exist before 2017: SILVSYS, AGEEST, TARGETYD, ESTYIELD, DENSITY
		The script renamed FTG to ESTIND and FTGFU to ESTFU to follow the 2018 tech spec.
		"""
		self.logger.print2(note)

		# create feature dataset
		self.logger.print2("\n## Working on %s"%DS_name)
		self.logger.print2("\tMaking new Feature dataset: %s"%DS_name)
		arcpy.Delete_management(DS_name)
		arcpy.CreateFeatureDataset_management(self.arar_gdb_path, DS_name, self.projfile)
		dest_feature_dataset = os.path.join(self.arar_gdb_path, DS_name)

		# start copying over the template
		harv_temp_path = os.path.join(self.ar_master_path,template)
		self.logger.print2("\tCopying over %s..."%template)
		arcpy.FeatureClassToFeatureClass_conversion(harv_temp_path, dest_feature_dataset, new_fc_name)

		# append all other ones to the new_fc_name. (do it on the Pro first then grab the python snippet)
		self.logger.print2("\tAppending the following FCs:\n%s"%append_lst)
		ap_input = ''
		for fc in append_lst:
			ap_input += "%s;"%fc
		arcpy.management.Append(inputs=ap_input, target=new_fc_name, schema_type="NO_TEST")

		# rename - alter field
		self.logger.print2("\tRenaming fields")
		arcpy.management.AlterField(new_fc_name, 'FTG', 'ESTIND')
		arcpy.management.AlterField(new_fc_name, 'FTGFU', 'ESTFU')

		self.logger.print2("\t%s complete!"%DS_name)


	def regen(self):
		# variables
		DS_name = "Regen" # try to stick to the same DS name as the AR Master
		template = 'Regen/Regen_Plant'
		append_lst = [os.path.join(ar_master_path,DS_name,i) for i in ['Regen_Seed','Regen_Natural']]
		new_fc_name = 'Regen_All_02_n_up'
		note = """
		Remember:
		SEED and PLANT may occur more than once. Refer to the ~*2 fields such as AR_YEAR2, SP12, SP22 for those second occurances.
		"""
		self.logger.print2(note)

		# create feature dataset
		self.logger.print2("\n## Working on %s"%DS_name)
		self.logger.print2("\tMaking new Feature dataset: %s"%DS_name)
		arcpy.Delete_management(DS_name)
		arcpy.CreateFeatureDataset_management(self.arar_gdb_path, DS_name, self.projfile)
		dest_feature_dataset = os.path.join(self.arar_gdb_path, DS_name)

		# start copying over the template
		harv_temp_path = os.path.join(self.ar_master_path,template)
		self.logger.print2("\tCopying over %s..."%template)
		arcpy.FeatureClassToFeatureClass_conversion(harv_temp_path, dest_feature_dataset, new_fc_name)

		# append all other ones to the new_fc_name. (do it on the Pro first then grab the python snippet)
		self.logger.print2("\tAppending the following FCs:\n%s"%append_lst)
		ap_input = ''
		for fc in append_lst:
			ap_input += "%s;"%fc
		arcpy.management.Append(inputs=ap_input, target=new_fc_name, schema_type="NO_TEST")

		self.logger.print2("\t%s complete!"%DS_name)


	def tending(self):
		# variables
		DS_name = "Tend" # try to stick to the same DS name as the AR Master
		template = 'Tend/Tend_ChemA'
		append_lst = [os.path.join(ar_master_path,DS_name,i) for i in ['Tend_Prot','Tend_ManImpThin','Tend_ChemG17','Tend_ChemG','Tend_ChemA17']]
		new_fc_name = 'Tend_All_02_n_up'
		note = """
		Remember:
		Tending events may occur more than once. Refer to the ~*2 fields such as TRTMTHD2, TRTCAT2, etc. for those second (and third) occurances.
		"""
		self.logger.print2(note)

		# create feature dataset
		self.logger.print2("\n## Working on %s"%DS_name)
		self.logger.print2("\tMaking new Feature dataset: %s"%DS_name)
		arcpy.Delete_management(DS_name)
		arcpy.CreateFeatureDataset_management(self.arar_gdb_path, DS_name, self.projfile)
		dest_feature_dataset = os.path.join(self.arar_gdb_path, DS_name)

		# start copying over the template
		harv_temp_path = os.path.join(self.ar_master_path,template)
		self.logger.print2("\tCopying over %s..."%template)
		arcpy.FeatureClassToFeatureClass_conversion(harv_temp_path, dest_feature_dataset, new_fc_name)

		# append all other ones to the new_fc_name. (do it on the Pro first then grab the python snippet)
		self.logger.print2("\tAppending the following FCs:\n%s"%append_lst)
		ap_input = ''
		for fc in append_lst:
			ap_input += "%s;"%fc
		arcpy.management.Append(inputs=ap_input, target=new_fc_name, schema_type="NO_TEST")

		self.logger.print2("\t%s complete!"%DS_name)


	def sip(self):
		# variables
		DS_name = "SIP" # try to stick to the same DS name as the AR Master
		template = 'SIP/SIP_Chem'
		append_lst = [os.path.join(ar_master_path,DS_name,i) for i in ['SIP_Mech','SIP_PB']]
		new_fc_name = 'SIP_All_02_n_up'
		note = """
		Remember:
		Prescribed Burn layer has a lot of small circles 78m2 and 155m2 in size.
		So if you use eliminate, then you will lose a lot of records.
		Mechanical Site Prep layer usually has the most records (~80k).
		"""
		self.logger.print2(note)

		# create feature dataset
		self.logger.print2("\n## Working on %s"%DS_name)
		self.logger.print2("\tMaking new Feature dataset: %s"%DS_name)
		arcpy.Delete_management(DS_name)
		arcpy.CreateFeatureDataset_management(self.arar_gdb_path, DS_name, self.projfile)
		dest_feature_dataset = os.path.join(self.arar_gdb_path, DS_name)

		# start copying over the template
		harv_temp_path = os.path.join(self.ar_master_path,template)
		self.logger.print2("\tCopying over %s..."%template)
		arcpy.FeatureClassToFeatureClass_conversion(harv_temp_path, dest_feature_dataset, new_fc_name)

		# append all other ones to the new_fc_name. (do it on the Pro first then grab the python snippet)
		self.logger.print2("\tAppending the following FCs:\n%s"%append_lst)
		ap_input = ''
		for fc in append_lst:
			ap_input += "%s;"%fc
		arcpy.management.Append(inputs=ap_input, target=new_fc_name, schema_type="NO_TEST")

		self.logger.print2("\t%s complete!"%DS_name)


if __name__ == '__main__':

	# user inputs
	ar_master_path = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\D\AR\AR_Master.gdb'
	arar_gdb_path = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\D\AR\AnalysisReadyAR.gdb' # this is the output - it must already exist
	projfile = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"MNRLambert_d.prj")

	# logfile stuff
	# importing arclog in the parent directory
	parent_d = os.path.split(os.path.split(__file__)[0])[0]
	sys.path.append(parent_d)
	from arclog import Print2 as p2
	logfile_path = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\D\AR\ar_ar_log.txt'
	logger = p2(logfile_path)


	# running class Ar_ar
	ar = Ar_ar(ar_master_path,arar_gdb_path,projfile, logger)

	#### below: you can comment out the ones that you don't need to run
	## Rolling up all fcs in the same category into a single fc.
	# ar.harvest()
	# ar.est()
	# ar.regen()
	# ar.tending()
	ar.sip()

	# writing the log file
	logger.log_close()


