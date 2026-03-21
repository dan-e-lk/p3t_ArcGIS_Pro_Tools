# replacement for alter field tool which only exists in arcmap 10.2 and up.
# will fail if try to change primary key field.

import arcpy

def alter_field2(full_fc_path, old_field, new_field):
	""" Changes the field name. This tool is for versions before Arc 10.2.
		If you have Arc 10.2 or above, use Alter Field tool instead"""
	fc = full_fc_path

	# simple check. The old field must exist in the fc and the new field must not exist in the fc.
	oldfields = [str(f.name).upper() for f in arcpy.ListFields(fc)]
	if old_field.upper() not in oldfields or new_field.upper() in oldfields:
		raise Exception('Invalid parameter - old field must exist in the original fc and the new field must not exist in the original fc')


	# creating a dictionary of existing field names to field length and type.
	fields = {str(f.name):[str(f.length), str(f.type)] for f in arcpy.ListFields(fc)}

	# it really pisses me off that ArcMap is using two sets of fieldtype names. sometimes they call it String, sometimes they call it TEXT.
	fieldtype_map = {	'String': 		'TEXT',
						'SmallInteger': 'SHORT',
						'Integer':		'LONG',
						'Single':		'FLOAT'	}
	
	fieldtype = fields[old_field][1]
	try:
		fieldtype = fieldtype_map[fieldtype]
	except KeyError:
		pass
	if fieldtype == 'TEXT':
		fieldlength = fields[old_field][0]
	else:
		fieldlength = ''

	arcpy.AddField_management(in_table=fc, field_name=new_field, field_type=fieldtype, field_precision="", field_scale="", field_length=fieldlength)
	arcpy.CalculateField_management(in_table=fc, field=new_field, expression="!" + old_field + "!", expression_type="PYTHON")
	arcpy.DeleteField_management(in_table=fc, drop_field=old_field)


def print2(msg, msgtype = 'msg'):
	print(msg)
	if msgtype == 'msg':
		arcpy.AddMessage(msg)
	elif msgtype == 'warning':
		arcpy.AddWarning(msg)
	return msg


if __name__ == '__main__':
	full_fc_path = r'\\lrcpsoprfp00001\MNR_NER\GI_MGMT\Tools\Scripts\FMPTools_2017\FMP_SpatialData_Compiler\compiler_output\Compiler_Output_201801240952.gdb\temp_testoutput'
	old_field = 'GEOGNUM'
	new_field = 'GEOGNUM_testing2'
	alter_field2(full_fc_path, old_field, new_field)
