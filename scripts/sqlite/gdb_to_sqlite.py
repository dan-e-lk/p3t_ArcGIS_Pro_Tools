# This script is an extension of the fc_to_sqlite.py.
# The script turns all fcs in the gdb into tables in sqlite. Yes, including the ones inside datasets.
# does not keep the relationship information (may be something to work on later)



import os, sqlite3
import arcpy

from fc_to_sqlite import fc_to_sqlite, fieldtype_map


def gdb_to_sqlite(input_gdb,output_sqlite_file,add_shapetype_suffix):
	
	arcpy.env.workspace = input_gdb
	# take care of the tables first
	tables = arcpy.ListTables()

	# Initialize a dictionary # eg. {'fcname': ['(type)table','(new table name)fcname'],...}
	desc_dict = {tbl_name:(['Table',tbl_name+"_Table"] if add_shapetype_suffix else ['Table',tbl_name]) for tbl_name in tables}

	# for the feature classes, there may be ones inside datasets
	# List all feature datasets
	datasets = arcpy.ListDatasets(feature_type='feature') or []
	# Include standalone feature classes by adding an empty string
	datasets = [''] + datasets
	# Initialize a list to hold all feature classes
	all_fcs = []

	for ds in datasets:
		fcs = arcpy.ListFeatureClasses(feature_dataset=ds)
		if fcs:
			for fc in fcs:
	            # Construct the full path and add to the list
				full_path = os.path.join(arcpy.env.workspace, ds, fc) if ds else os.path.join(arcpy.env.workspace, fc)
				all_fcs.append(full_path)

	# identify what type of fc is for each fc.
	for fc in all_fcs:
		desc = arcpy.Describe(fc)
		fc_name = desc.name
		fc_shapetype = desc.shapetype # Polygon, Polyline, Point, Multipoint or MultiPatch

		desc_dict[fc_name] = [fc_shapetype, "%s_%s"%(fc_name,fc_shapetype)] if add_shapetype_suffix else [fc_shapetype, fc_name]

	# just messaging
	fc_count = len(desc_dict)
	arcpy.AddMessage("List of feature classes and tables found (total %s found):"%fc_count)
	for input_fc, type_n_newname in desc_dict.items():
		arcpy.AddMessage("%s\t%s"%(type_n_newname[0],input_fc))

	# put together the variables and run the fc_to_sqlite
	progress = 0
	for input_fc, type_n_newname in desc_dict.items():
		progress += 1
		newname = type_n_newname[1]
		arcpy.AddMessage("\nExporting %s to %s (%s of %s)"%(input_fc,output_sqlite_file,progress,fc_count))
		fc_to_sqlite(input_fc,output_sqlite_file,newname)





if __name__ == '__main__':

	# input_gdb = r'C:\Users\kimdan\OneDrive - Government of Ontario\_FPPS\Projects\JustinGaudon\Clupa_foraging.gdb'
	# output_sqlite_file = r'T:\T\temp\clupa.sqlite3' # this will be created if doesn't already exist. if already exists, the tables will be overwritten
	# add_shapetype_suffix = False # adds the shapetype (polygon, table, polyline) at the end of the newly created table names

	input_gdb = arcpy.GetParameterAsText(0)
	output_sqlite_file = arcpy.GetParameterAsText(1)
	add_suffix = arcpy.GetParameterAsText(2) # adds the shapetype (polygon, table, polyline) at the end of the newly created table names	
	add_shapetype_suffix = True if add_suffix == 'true' else False

	gdb_to_sqlite(input_gdb,output_sqlite_file,add_shapetype_suffix)

	# a bonus - open folder containing the sqlite3 file
	try:
		import subprocess
		subprocess.Popen(f'explorer /select,"{output_sqlite_file}"')
	except:
		pass
