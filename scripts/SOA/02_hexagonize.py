intro = """
version 1.0
How would you answer questions such as "Where are the blocks that was harvested before 2010 but didn't get EST survey yet?"
The answer is to union all HRV, RGN, EST layers (and may be SIP and TND). The issue with unioning them is the slivers.
HRV, RGN, and EST don't usually line up and when unioned together it needs to go through rigorous sliver removal process.
All the attributes also need to exist in one layer.
This script will turn all HRV since 2002 into hexagons, then turn every other layers that overlaps that area into hexagons as well.
In this script, hexagon being used are H3 lvl 11 hexagons (0.2414ha). These were pre-generated using 'generate_hex_for_each_polygon.py'.
You should run 01_AR_AR.py script prior to running this.
This script will first turn all the HRV_All_02_n_up into hexagons (should we treat CC separately? No, because sometimes CC overlaps with SH)
"""


import arcpy
import os, sys

# importing libraries I made
# importing arclog in the parent directory
parent_d = os.path.split(os.path.split(__file__)[0])[0] # bring arclog.py from the parent directory
sys.path.append(parent_d)
from arclog import Print2 as p2
# importing common_func from the parent directory
import common_func as cf


class Hexagonize:
	def __init__(self, arar_gdb_path, hexagon_gdb, arhex_gdb_path, muno, projfile, logger):
		self.logger = logger
		self.logger.print2(intro)
		self.arar_gdb_path = arar_gdb_path
		self.hexagon_gdb = hexagon_gdb # this is the hex grid
		self.muno = muno
		self.projfile = projfile
		self.arhex_gdb_path = arhex_gdb_path
		arcpy.env.workspace = self.ws = arhex_gdb_path

		# muno selection sql
		self.muno_sql = "MUNO = %s"%muno

		# temporary dataset name
		temp_ds = 'temp'
		self.logger.print2("Generating temporary dataset called 'temp'.")
		arcpy.Delete_management(temp_ds)
		arcpy.CreateFeatureDataset_management(self.arhex_gdb_path, temp_ds, self.projfile)
		self.temp_ds_path = os.path.join(arhex_gdb_path,temp_ds)

		# real work begins here:
		self.harvest() # this will be the base layer for everything so it must be run when this class initiates


	def harvest(self):
		"""This method generates both harvest hex and base hex.
		base hex is basically harvest hex without any harvest fields.
		If later I need to use all disturbances as base, I need to create a disturbance layer HRV+NatDist, then use (duplicate) this method as a template
		"""
		self.logger.print2("\n### Running method: harvest")
		self.logger.print2("\tThis method generates base hexagon (based on harv) on which all other forestry events will be spatially joined")
		# variables
		DS_name = 'harvest'
		hrv_fc_path = os.path.join(arar_gdb_path,'Harvest','HRV_All_02_n_up')
		field_prefix = 'hrv'

		# generate the main dataset
		self.logger.print2("\tGenerating dataset called '%s'."%DS_name)
		arcpy.Delete_management(DS_name)
		arcpy.CreateFeatureDataset_management(self.arhex_gdb_path, DS_name, self.projfile)

		# sort, but first select the current mu and exclude ROADROW
		temp_lyr = "hrv_mu%s"%self.muno
		# sql = self.muno_sql + " AND HARVCAT <> 'ROADROW'" # commenting this out - we need roadrow for caribou analysis
		sql = self.muno_sql
		self.logger.print2("\tSorting by AR_YEAR and selecting where %s"%sql)
		arcpy.management.MakeFeatureLayer(hrv_fc_path, temp_lyr, sql)
		# running sort
		sort_output = os.path.join(self.temp_ds_path,"t_hrv_sort_mu%s"%self.muno)
		arcpy.Sort_management(temp_lyr, sort_output, [["AR_YEAR", "DESCENDING"]])

		# spatial join
		target_fc = os.path.join(self.hexagon_gdb,'f_%s'%self.muno)
		join_fc = sort_output
		self.logger.print2("\tHexagonizing %s by spatial joining it with hex grid"%os.path.split(join_fc)[1])
		output_fc_name = 'h_%s_%s'%(self.muno, field_prefix) #eg. h_889_hrv
		output_fc_path = os.path.join(self.arhex_gdb_path,DS_name,output_fc_name) #eg. "...D\AR\AR_in_hex.gdb\harvest\h_889_hrv"
		arcpy.analysis.SpatialJoin(	target_features=target_fc,
									join_features=join_fc,
									out_feature_class=output_fc_path,
									join_operation="JOIN_ONE_TO_ONE", join_type="KEEP_COMMON", match_option="HAVE_THEIR_CENTER_IN")
		self.logger.print2("\t\tDone. Output fc name: %s"%output_fc_name)

		# attribute names - delete unnecessary ones and rename the ones that we keep.
		# remember: mandatory attribute names are stored in another python file - man_fields.py
		fnames = [f.name.upper() for f in arcpy.ListFields(output_fc_name)]
					# self.logger.print2('\tExisting Fields:\n\t%s'%fnames)
		fields2keep = mf.basic_fields + mf.hrv_keep # mf = man_fields.py file
		self.logger.print2("\tDeleting fields while keeping only these fields:\n\t%s"%fields2keep)
		arcpy.management.DeleteField(output_fc_name, fields2keep, "KEEP_FIELDS")

		self.logger.print2("\tRenaming the following fields:\n\t%s"%mf.hrv_keep)
		hrv_fields = [] # this only applies to hrv - to be used next when creating base layer
		for f in mf.hrv_keep:
			new_fname = "%s_%s"%(field_prefix.upper(), f.upper()) # giving prefix to the fieldnames. eg. HRV_DSTBFU
			arcpy.management.AlterField(output_fc_name, f, new_fname, new_fname)
			fields2keep[fields2keep.index(f)] = new_fname
			hrv_fields.append(new_fname)
		self.logger.print2("\tDone renaming fields. New fieldnames:\n\t%s\n"%fields2keep)
		###### done with harvest layer ######


		# generate base which is just the hexagon polygon without all the HRV fields.
		self.logger.print2("Generating base layer")
		DS_name = 'base'
		self.logger.print2("\tGenerating dataset called '%s'."%DS_name)
		arcpy.Delete_management(DS_name)
		arcpy.CreateFeatureDataset_management(self.arhex_gdb_path, DS_name, self.projfile)
		# generate the base by deleting HRV fields
		basefc_path = os.path.join(self.ws, DS_name, 'h_%s_base'%self.muno) #eg. D:/base/h_421_base
		hrvfc_path = output_fc_path

		self.logger.print2("\tExporting the base and deleting HRV fields")
		cf.quick_delete_field(inputfc=hrvfc_path, fields2delete_lst=hrv_fields, outputfc=basefc_path)

		# self.logger.print2("\tExporting the base: %s"%basefc_path)
		# arcpy.conversion.ExportFeatures(hrvfc_path, basefc_path)
		# self.logger.print2("\tDeleting HRV~ fields")
		# arcpy.management.DeleteField(basefc_path, hrv_fields)





	# def est(self):
	# 	# variables



	# def regen(self):
	# 	# variables


	def cleanup(self):
		# delete the temporary dataset
		pass



if __name__ == '__main__':

	# user inputs
	arar_gdb_path = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\D\AR\AnalysisReadyAR.gdb' # this is the output of the previously run AR_Ar.py script
	hexagon_gdb = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\E\AR\SOA_hex\FMU_in_hex_L11.gdb' # this is the output of the previously run 'generate_hex_for_each_poly.py'.
	arhex_gdb_path = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\D\AR\AR_in_hex.gdb' # Output gdb. this gdb must already exist. The tool will overwrite components of this gdb.
	logfile_path = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\D\AR\hexafy_log.txt' # this log file will be created
	# muno_list = [754]
	muno_list = [421]
	# muno_list = [889]

	# location of project file
	projfile = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"MNRLambert_d.prj")
	
	# start logfile
	logger = p2(logfile_path)

	# import mandatory field lists
	import man_fields as mf
	# arcpy.AddMessage(mf.hrv_keep) # testing


	# finally, running the main script
	for muno in muno_list:
		Hex = Hexagonize(arar_gdb_path, hexagon_gdb, arhex_gdb_path, muno, projfile, logger)

	logger.print2("Script complete!\nOutput gdb:\n%s"%arhex_gdb_path)

	# writing the log file
	logger.log_close()


