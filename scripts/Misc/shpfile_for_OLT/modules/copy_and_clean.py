# This script copies over the user defined input file to user defined output folder.
# This script also changes field names and corrects the data if necessary.

import os, datetime

print('importing arcpy...')
import arcpy

# importing the corresponding library...
from .create_template import fields, fieldname_update

def print2(msg, msgtype = 'msg'):
	print(msg)
	if msgtype == 'msg':
		arcpy.AddMessage(msg)
	elif msgtype == 'warning':
		arcpy.AddWarning(msg)
	return msg




def copy_and_clean(output_gdb, original_file_path,owner_select):
	""" Copies the user input inventory to the user specified output location.
		Also corrects the fields (for example changes WG to LEADSPC) and checkes the record (eg. if AGE field is filled out with integers)
		to make sure the data is ready to get appended to the template feature class"""
	temp_fc_name = 'temp'
	owner_sql = owner_select

	if len(owner_sql) > 5:
		print2('Copying the original inventory (WHERE %s ) to the output location...'%owner_sql)
		arcpy.FeatureClassToFeatureClass_conversion(in_features=original_file_path, out_path=output_gdb, out_name=temp_fc_name, where_clause= owner_sql)# by default, owner_select = "OWNER in('1','5','7')"
	else:
		print2('Copying the original inventory to the output location...')
		arcpy.FeatureClassToFeatureClass_conversion(in_features=original_file_path, out_path=output_gdb, out_name=temp_fc_name)

	temp_fc_path = os.path.join(output_gdb,temp_fc_name)
	record_count = rec_counter(temp_fc_path)

	existingFields = [str(f.name).upper() for f in arcpy.ListFields(temp_fc_path)]

	# if the user's data contains old fields that needs update (such as WG), the following will update those fields
	for k,v in fieldname_update.items():
		old_field_list = v
		correct_field = k
		for existingField in existingFields:
			if correct_field not in existingFields and existingField in old_field_list:  # if the correct field already exists, no need to alter field.
				print2("Renaming the field %s to %s."%(existingField,correct_field),'warning')
				try:
					# this only works on 10.2 or above
					arcpy.AlterField_management(in_table=temp_fc_path, field=existingField, new_field_name=correct_field)
				except:
					# this will work on any arcmap version
					import alter_field2
					alter_field2.alter_field2(full_fc_path = temp_fc_path, old_field = existingField, new_field = correct_field)


	# checking non-text fields to make sure they can be turned into int or float (going through each field then each record)
	print2('Checking non-text fields to make sure they can be turned into int or float...')
	existingFields = [str(f.name).upper() for f in arcpy.ListFields(temp_fc_path)] # This line added on Oct 10 2018
	for k,v in fields.items():
		field = v[0]
		fieldtype = v[2]
		if field in existingFields:
			cursor = arcpy.da.UpdateCursor(temp_fc_path,[field])

			if fieldtype in ['SHORT','LONG']:
				for row in cursor:
					try:
						int(row[0]) # if no error, make it NULL and move to next row
					except:
						row[0] = None
					cursor.updateRow(row)

			elif fieldtype in ['FLOAT','DOUBLE']:
				for row in cursor:
					try:
						float(row[0]) # if no error, make it NULL and move to next row
					except:
						row[0] = None
					cursor.updateRow(row)
			# Delete cursor and row objects to remove locks on the data.
			del cursor





	return temp_fc_path, record_count


# The rec_counter really has nothing to do with copy and clean, but there's no good place to put this so it's here now...
def rec_counter(fc):
	count = arcpy.GetCount_management(fc)[0]
	return str(count)



# def owner_sql_converter(owner_select):
# 	"""
# 	if input = '1257', the function will return "OWNER in('1','2','5','7')"
# 	"""
# 	owner_sql = "OWNER in("	
# 	for i in owner_select:
# 		owner_sql += "'" + i + "',"
# 	owner_sql = owner_sql[:-1] # to delete the last comma.
# 	owner_sql += ")"
# 	return owner_sql




if __name__ == '__main__':
	print(owner_sql_converter('1257'))


