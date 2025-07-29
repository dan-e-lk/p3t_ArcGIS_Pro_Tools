# this script is great to clip all your PIAM inventory data (except for the parks) to their corresponding FMU boundary layer from LIO.
# it also runs Erase on FMU boundary layer using your inventory - what's left of erase is the gaps in your inventory where there is no data.


import arcpy, os


def clip_to_FMU(input_PIAM_gdb,LIO_FMU,FMU_CODE_field,out_gdb,fmu_code_list_override, find_gap):
	
	DS_name = "clip_to_fmu"
	make_a_new_dataset(out_gdb, DS_name)

	if find_gap:
		erase_DS_name = "erase_to_find_gap"
		make_a_new_dataset(out_gdb, erase_DS_name)

	# get the list of fmu_code from LIO_FMU layer
	fmu_code_list = []
	if fmu_code_list_override != None:
		fmu_code_list = fmu_code_list_override
		arcpy.AddMessage("This tool will only work on the following FMUs: %s"%fmu_code_list)
	else:
		with arcpy.da.SearchCursor(LIO_FMU, [FMU_CODE_field]) as rows:
			for row in rows:
				fmu_code_value = row[0]
				fmu_code_list.append(fmu_code_value)
		arcpy.AddMessage("List of FMU_CODE found in %s:"%LIO_FMU)
		arcpy.AddMessage(str(fmu_code_list))

	# run clip
	for fmu_code in fmu_code_list:
		arcpy.AddMessage("\nClipping %s..."%fmu_code)
		# 1. in feature
		in_features = os.path.join(input_PIAM_gdb,'INV',"FC%s"%fmu_code) # this layer will be clipped
		# 2. clip feature is a selected FMU from LIO_FMU layer
		where_clause = "%s = '%s'"%(FMU_CODE_field,fmu_code)
		clip_features = "current_fmu_boundary"
		arcpy.management.MakeFeatureLayer(LIO_FMU, clip_features, where_clause)
		# 3. out feature
		out_feature_class = os.path.join(out_gdb,DS_name,"FC%s_Clipped"%fmu_code)
		arcpy.analysis.Clip(in_features, clip_features, out_feature_class)
		arcpy.AddMessage("Done.")

		# finding gap
		if find_gap:
			arcpy.AddMessage("\nErasing %s..."%fmu_code)
			# input feature is the current fmu boundary
			erase_input_fc = clip_features
			# erase fc is the PIAM inventory data
			erase_fc = in_features
			# out feature
			erase_out_fc = os.path.join(out_gdb,erase_DS_name,"FC%s_gaps"%fmu_code)
			arcpy.analysis.Erase(erase_input_fc,erase_fc,erase_out_fc)
			arcpy.AddMessage("Done.")



def make_a_new_dataset(out_gdb, DS_name):
	""" use this to create a new dataset for an existing gdb.
	"""
	arcpy.env.workspace = out_gdb
	# make a new feature dataset with MNR Lambert Conformal Conic Projection
	arcpy.AddMessage("Generating dataset: %s..."%DS_name)
	# find the projection file location
	projfile = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"MNRLambert_d.prj")
	if not os.path.isfile(projfile):
		# if the file doesn't exist, show error
		arcpy.AddError("Can't find MNRLambert_d.prj file at the parent folder of %s"%__file__)
		raise
	arcpy.Delete_management(DS_name)
	arcpy.CreateFeatureDataset_management(out_gdb, DS_name, projfile)
	arcpy.AddMessage("Dataset successfully generated!")




if __name__ == '__main__':

	input_PIAM_gdb = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\D\GeoData\PIAMMar2024.gdb' # where the original PIAM layers are stored
	LIO_FMU = r'U:\Backup_data\GDDS_backup\GDDS_202409\GDDS-Internal-MNRF.gdb\FOREST_MANAGEMENT_UNIT' # this has to have FMU_CODE field populated
	FMU_CODE_field = 'FMU_CODE' # A TEXT field from LIO FMU boundary layer.
	out_gdb = r'C:\Users\kimdan\OneDrive - Government of Ontario\_FPPS\Projects\_inventory_cleanup\s01_clip_to_fmu.gdb' # this gdb must already exist
	fmu_code_list_override = None # leave this to None if you want to include all FMUs. if you want specific fmus only, give it a list of fmu codes.
	find_gap = True

	clip_to_FMU(input_PIAM_gdb,LIO_FMU,FMU_CODE_field,out_gdb,fmu_code_list_override, find_gap)