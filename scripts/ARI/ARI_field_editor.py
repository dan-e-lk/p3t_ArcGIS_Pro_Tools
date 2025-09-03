# just a quick script to add/delete fields
# this changes the input data, so use it carefully

import arcpy
import os, csv


def ari_delete_field(ari_gdb, mu_list, delete_field_list):

	arcpy.env.workspace = ari_gdb
	for mu in mu_list:
		arcpy.AddMessage("\nWorking on %s"%mu)
		fields = [f.name.upper() for f in arcpy.ListFields(mu)]
		for f_to_delete in delete_field_list:
			if f_to_delete in fields:
				arcpy.AddMessage("\tDeleting Field: %s"%f_to_delete)
				arcpy.management.DeleteField(mu,f_to_delete)



if __name__ == '__main__':
	ari_gdb = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - FRO\FRO2026\02InventoryCleanUp\ARI_base.gdb'
	mu_list = ['FC035', 'FC060', 'FC110', 'FC120', 'FC130', 'FC140', 'FC175', 'FC177', 'FC210', 'FC220',
	'FC230', 'FC280', 'FC350', 'FC360', 'FC390', 'FC406', 'FC415', 'FC421', 'FC438', 'FC443',
	'FC451', 'FC490', 'FC535', 'FC574', 'FC601', 'FC615', 'FC644', 'FC680', 'FC702', 'FC754',
	'FC780', 'FC796', 'FC816', 'FC840', 'FC889', 'FC898', 'FC930', 'FC966', 'FC994',
	'FarNorth_BerensRiver', 'FarNorth_CatLake', 'FarNorth_ConstanceL', 'FarNorth_MooseCree',
	'FarNorth_NorthCentral', 'FarNorth_Northeast', 'FarNorth_Northwest', 'FarNorth_Taash',
	'Lake_Superior_Islands', 'Lake_Nipigon_Islands', 'Park_EagleSnowshoe', 'Park_LitGrRap',
	'Park_LkSuperior', 'Park_Quetico', 'Park_WCaribou', 'Park_Wabakimi', 'Park_pukaskwa']

	delete_field_list = ['ORIG_FID']

	ari_delete_field(ari_gdb, mu_list, delete_field_list)