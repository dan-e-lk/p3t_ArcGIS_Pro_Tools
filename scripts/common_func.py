

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



# def quick_delete_field_not_working(inputfc, fields2delete_lst, outputfc):
# 	""" !!! This function doesn't work !!!
# 	!!! Another way to go about it is to create a new fc with only the fields to keep, then append it.
# 	!!! achieve this by select one record, export it, delete the fields, delete the one record, then append the original.
# 	When you need to delete multiple fields, hiding fields and export is often faster than deleting fields individually.
# 	inputfc and outputfc should be full paths
# 	fields2delete_lst must be a list and the values must match the fields in the inputfc
# 	"""
# 	import arcpy

# 	arcpy.management.MakeFeatureLayer(inputfc, "temp_lyr")
# 	desc = arcpy.Describe("temp_lyr")
# 	field_info = desc.fieldInfo
# 	arcpy.AddMessage(str(field_info.count))
# 	for i in range(0, field_info.count):
# 		arcpy.AddMessage("\tChecking field: %s"%field_info.getFieldName(i))
# 		if field_info.getFieldName(i) in fields2delete_lst:
# 			field_info.setVisible(i, "HIDDEN") # unfortunately even if a field is hidden, it will still export.
# 	arcpy.conversion.ExportFeatures("temp_lyr", outputfc)



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




if __name__ == '__main__':
	inputfc = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\D\AR\AR_in_hex.gdb\base\h_421_base'
	outputfc = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\D\AR\AR_in_hex.gdb\temp\test_421_base_deletedFields2'
	fields2delete_lst = ['HRV_BLOCKID','HRV_HARVCAT','HRV_SILVSYS','HRV_HARVMTHD','HRV_SGR','HRV_DSTBFU']
	quick_delete_field(inputfc, fields2delete_lst, outputfc)