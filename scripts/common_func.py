# How to use these functions from scripts inside other folders:

# parent_d = os.path.split(os.path.split(__file__)[0])[0] # depends on how deep in the folder structure your main script is at.
# sys.path.append(parent_d)
# import common_func




def quick_delete_field(inputfc, fields2delete_lst, outputfc):
	"""
	select zero record from input, export, delete the fields, then append the original records
	inputfc and outputfc should be full paths
	fields2delete_lst must be a list and the values must match the fields in the inputfc
	"""
	import arcpy
	# select zero record and export
	arcpy.management.MakeFeatureLayer(inputfc, "temp_lyr")
	arcpy.management.SelectLayerByAttribute("temp_lyr", "NEW_SELECTION", "OBJECTID IS NULL")
	# export
	arcpy.conversion.ExportFeatures("temp_lyr", outputfc)
	# delete fields
	arcpy.management.DeleteField(outputfc, fields2delete_lst)
	# append
	arcpy.management.Append(inputfc, outputfc, "NO_TEST")




def get_gdb_path(input_table):
	'''Return the Geodatabase path from the input table or feature class.
	'''
	import os
	p_dir = os.path.dirname(input_table) # returns parent directory
	p_p_dir = os.path.dirname(p_dir) # returns parent of parent directory (in the case of dataset)
	if p_dir.upper().endswith('.GDB'):
		return p_dir
	elif p_p_dir.upper().endswith('.GDB'):
		return p_p_dir
	else:
		raise Exception("Can't find the geodatabase path of %s"%input_table)


def find_all_fcs(gdb_path):
	# returns the names and full paths of all fcs inside a gdb, including ones inside datasets
	# !!!! Warning, this method resets the arcpy env workspace!!!
	import os, arcpy
	arcpy.env.workspace = gdb_path

	# List feature classes in the root of the GDB
	all_feature_classes = arcpy.ListFeatureClasses()
	fc_names_only = all_feature_classes

	# List feature datasets
	fds_list = arcpy.ListDatasets(feature_type='feature')

	# Loop through each feature dataset and list its feature classes
	if fds_list:
		for fds in fds_list:
			fds_path = f"{gdb_path}\\{fds}"
			arcpy.env.workspace = fds_path
			fcs_in_fds = arcpy.ListFeatureClasses()
			for fc in fcs_in_fds:
				fc_names_only.append(fc)
				all_feature_classes.append(os.path.join(fds,fc)) # eg. 'INV\fc421'

	# Print all feature class names
	fc_fullpath = [os.path.join(gdb_path,i).upper() for i in all_feature_classes] # a list of full path of all fcs
	fc_names_only = [i.upper() for i in fc_names_only] # a list of names of all fcs.

	return [fc_names_only, fc_fullpath]


def fc_to_pandas(input_fc):
	"""Quick transform from feature class to pandas dataframe. !! Tabular data only !!"""
	import arcpy
	import pandas as pd

	# List all fields except geometry
	fields = [f.name for f in arcpy.ListFields(input_fc) if f.type != 'Geometry']
	# This excludes geometry fields. If you want geometry (e.g., coordinates), you can include "SHAPE@" or "SHAPE@XY" in the cursor.

	# Use SearchCursor to extract rows
	with arcpy.da.SearchCursor(input_fc, fields) as cursor:
		data = [row for row in cursor]

	# Create DataFrame
	df = pd.DataFrame(data, columns=fields)
	# You can save the DataFrame to CSV using df.to_csv("output.csv", index=False).

	return df




if __name__ == '__main__':
	inputfc = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\D\AR\AR_in_hex.gdb\base\h_421_base'
	outputfc = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\D\AR\AR_in_hex.gdb\temp\test_421_base_deletedFields2'
	fields2delete_lst = ['HRV_BLOCKID','HRV_HARVCAT','HRV_SILVSYS','HRV_HARVMTHD','HRV_SGR','HRV_DSTBFU']
	quick_delete_field(inputfc, fields2delete_lst, outputfc)