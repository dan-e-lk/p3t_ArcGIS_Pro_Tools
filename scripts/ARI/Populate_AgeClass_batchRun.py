# Create AC5, AC10, AC20 fields - then populate them using AGE values

import arcpy
import os, csv
import pandas as pd

age_class_tbl_csv = 'age_class_table.csv'

def populate_ac(input_fc,ac_fields):


	# loading csv to pandas dataframe
	df = pd.read_csv(age_class_tbl_csv, na_filter=False) # if you don't disable na_filter, then it will change 'NA' 'N/A','null' into 'nan'
	# print(df)
	existing_fields = [f.name.upper() for f in arcpy.ListFields(input_fc)]

	for ac in ac_fields:
		arcpy.AddMessage("\nWorking on %s - %s"%(ac,input_fc))
		if ac not in existing_fields:
			arcpy.AddMessage("Adding field: %s"%ac)
			arcpy.AddField_management(in_table = input_fc, field_name = ac, field_type = "TEXT", field_length = "7")

		# populate values
		arcpy.AddMessage("Populating field: %s"%ac)
		fail_count = 0
		f = ['AGE',ac]
		sql = "POLYTYPE = 'FOR' AND AGE IS NOT NULL AND AGE >= 0"
		with arcpy.da.UpdateCursor(input_fc, f, sql) as cursor:
			for row in cursor:
				age = row[0]
				if age > 260 and age != 999:
					age = 260
				try:
					ac_val = df.loc[df['AGE']==age, ac].values[0] # should return one AC value # eg. '000-005'
					row[1] = ac_val
					cursor.updateRow(row)
				except:
					fail_count += 1
		if fail_count > 0:
			arcpy.AddWarning("Could not populate %s for all records. Number of fails: %s"%(ac,fail_count))
		else:
			arcpy.AddMessage("All %s successfully populated!"%ac)



if __name__ == '__main__':

	mu_list = ['FC035', 'FC060', 'FC110', 'FC120', 'FC130', 'FC140', 'FC175', 'FC177', 'FC210', 'FC220',
	'FC230', 'FC280', 'FC350', 'FC360', 'FC390', 'FC406', 'FC415', 'FC421', 'FC438', 'FC443',
	'FC451', 'FC490', 'FC535', 'FC574', 'FC601', 'FC615', 'FC644', 'FC680', 'FC702', 'FC754',
	'FC780', 'FC796', 'FC816', 'FC840', 'FC889', 'FC898', 'FC930', 'FC966', 'FC994',
	'FarNorth_BerensRiver', 'FarNorth_CatLake', 'FarNorth_ConstanceL', 'FarNorth_MooseCree',
	'FarNorth_NorthCentral', 'FarNorth_Northeast', 'FarNorth_Northwest', 'FarNorth_Taash',
	'Lake_Superior_Islands', 'Lake_Nipigon_Islands', 'Park_EagleSnowshoe', 'Park_LitGrRap',
	'Park_LkSuperior', 'Park_Quetico', 'Park_WCaribou', 'Park_Wabakimi', 'Park_pukaskwa']

	ac_fields = ['AC5','AC10','AC20']

	input_ari = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - FRO\FRO2026\02InventoryCleanUp\ARI_wFU.gdb'
	arcpy.env.workspace = input_ari

	for mu in mu_list:
		input_fc = mu
		populate_ac(input_fc,ac_fields)