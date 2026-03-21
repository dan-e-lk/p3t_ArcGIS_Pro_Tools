# This script is originally a part of the FMP_SpatialData_Compiler tool

import os, datetime

print('importing arcpy...')
import arcpy

def print2(msg, msgtype = 'msg'):
	print(msg)
	if msgtype == 'msg':
		arcpy.AddMessage(msg)
	elif msgtype == 'warning':
		arcpy.AddWarning(msg)

#			  order	|	  field 	|	length 	| field type
# These fields doesn't have to exist in your inventory data. 
fields = {
				1:		['POLYID',		25,			'TEXT'],
				2:		['POLYTYPE',	3,			'TEXT'],
				3:		['OWNER',		10,			'TEXT'],
				7: 		['DEVSTAGE',	8,			'TEXT'],
				8:		['YRDEP',		4,			'SHORT'],
				10:		['OYRORG',		4,			'SHORT'],				
				11:		['OSPCOMP',		120,		'TEXT'],
				12:		['OLEADSPC',	3,			'TEXT'],
				13:		['OAGE',		3,			'SHORT'],
				14:		['OHT',			4,			'FLOAT'],
				15:		['OCCLO',		3,			'SHORT'],
				# 16:		['OSTKG',		4,			'FLOAT'], OLT will use OSTKG
				17:		['OSC',			1,			'SHORT'],
				18:		['UYRORG',		4,			'SHORT'],
				19:		['USPCOMP',		120,		'TEXT'],
				20:		['ULEADSPC',	3,			'TEXT'],
				21:		['UAGE',		3,			'SHORT'],
				22:		['UHT',			4,			'FLOAT'],
				23:		['UCCLO',		3,			'SHORT'],
				24:		['USTKG',		4,			'FLOAT'],
				25:		['USC',			1,			'SHORT'],
				26:		['INCIDSPC',	3,			'TEXT'],
				27:		['VERT',		2,			'TEXT'],
				28:		['HORIZ',		2,			'TEXT'],
				29:		['PRI_ECO',		13,			'TEXT'],
				30:		['SEC_ECO',		13,			'TEXT'],
				31:		['STKG',		4,			'FLOAT'],
				32:		['PLANFU',		15,			'TEXT'],	# PLANFU field has been added on Sept 2018 to enable more option in OLT.
				34:		['AU',			15,			'TEXT'],	# AU field has been added 
				} 




# if the new field does not exist in the old inventory, it will look for the corresponding old field and change the name of the old field into the new one.
fieldname_update = {
	
	# new field  |   old fields
	'OYRORG':		['YRORG'],
	'OSPCOMP':		['SPCOMP'],
	'OLEADSPC':		['LEADSPC'], # used to be ['WG']
	'OAGE':			['AGE'],
	'OHT':			['HT'],
	'OCCLO':		['CCLO'],
	# 'OSTKG':		['STKG'], OLT doesn't use OSTKG
	'OSC':			['SC'],
}





def create_template(outputgdb, input_path, unique_suffix, owner_select):
	""" Creates a new polygon feature class in the path outputgdb (must already have the gdb created) 
		with the fields described in fields dictionary above.
		It returns the full path of the FC created
		"""



	fcname = os.path.split(input_path)[1].replace('.','_')
	new_fcname = fcname + '_' + unique_suffix[:12] # for example, 'MU615_20BMI00_201806291324'
	print2('\ncreating a new template FC: %s'%new_fcname)

	# arcpy.CreateFeatureclass_management(out_path=outputgdb, out_name=new_fcname, geometry_type="POLYGON", spatial_reference="PROJCS['MNR_Lambert_Conformal_Conic',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',930000.0],PARAMETER['False_Northing',6430000.0],PARAMETER['Central_Meridian',-85.0],PARAMETER['Standard_Parallel_1',44.5],PARAMETER['Standard_Parallel_2',53.5],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]];-35121300 -18032700 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision")
	sr = "PROJCS['MNR_Lambert_Conformal_Conic',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',930000.0],PARAMETER['False_Northing',6430000.0],PARAMETER['Central_Meridian',-85.0],PARAMETER['Standard_Parallel_1',44.5],PARAMETER['Standard_Parallel_2',53.5],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]];-35121300 -18032700 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision"
	arcpy.management.CreateFeatureclass(
	out_path=outputgdb,
	out_name=new_fcname,
	geometry_type="POLYGON",
	template="",                # will be quicker if I have a template
	has_m="DISABLED",
	has_z="DISABLED",
	spatial_reference=sr)

#	txt_fc = os.path.join(outputgdb,txt_fcname)
	actual_fc = os.path.join(outputgdb,new_fcname)

	fieldDict = fields


	# # creating all-text fields
	# for k,v in sorted(fieldDict.items()):
	# 	print('Adding Field - %s'%v)
	# 	arcpy.AddField_management(in_table=txt_fc, field_name=v[0], field_type="TEXT", field_precision="", field_scale="", field_length=str(v[1]))


	# creating fields with correct field types
	for k,v in sorted(fieldDict.items()):
		#print2('Adding Field - %s'%v)
		fieldtype = v[2]
		if fieldtype == 'TEXT':
			fieldlength = str(v[1])
		else:
			fieldlength = ""
		print2('Adding Field: %s'%v[0])
		arcpy.management.AddField(in_table=actual_fc, field_name=v[0], field_type=fieldtype, field_length=fieldlength)


	return actual_fc # this would be the full path of newly created feature class.




def create_gdb(output_folder, unique_suffix):
	"""This will create a new unique file geodatabase within the output_folder"""

	print2('executing create_gdb function...')
	out_gdb_name = 'TemporaryOutput_' + unique_suffix

	arcpy.CreateFileGDB_management(out_folder_path=output_folder, out_name=out_gdb_name, out_version="CURRENT")

	out_gdb_path = os.path.join(output_folder,out_gdb_name + '.gdb')
	return out_gdb_path






if __name__ == '__main__':
	gdb = r'\\lrcpsoprfp00001\MNR_NER\GI_MGMT\Tools\Scripts\FMPTools_2017\FMP_SpatialData_Compiler\compiler_output\temp_201801181536.gdb'
	create_template(gdb)

	# create_gdb(r'\\lrcpsoprfp00001\MNR_NER\GI_MGMT\Tools\Scripts\FMPTools_2017\FMP_SpatialData_Compiler\compiler_output')