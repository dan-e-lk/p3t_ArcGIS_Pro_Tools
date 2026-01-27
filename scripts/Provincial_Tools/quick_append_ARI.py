# Just need to append a bunch of ARIs together

import arcpy
import os

group_dict = {
"GLSL": [
	"FC780", "FC451", "FC220", "FC615", "FC889", "FC754", "FC360",
	"FC680", "FC210", "FC140", "FC898", "Park_LkSuperior"],
"NEBOR": [
	"FC421", "FC438", "FC930", "FC280", "FC060", "FC601", "FC390",
	"FC574", "FC110", "Park_pukaskwa"],
"NWBOR": [
	"FC177", "FC350", "FC535", "FC120", "FC035", "FC816", "FC840",
	"FC406", "FC415", "FC175", "FC796", "FC230", "FC443", "FC644",
	"FC490", "FC130", "FC994", "FC702", "FC966", "Park_Quetico",
	"Park_Wabakimi", "Park_WCaribou", "Lake_Nipigon_Islands",
	"Park_EagleSnowshoe"]
	}


projfile = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"MNRLambert_d.prj")


def main(ari_path, new_gdb, group, suffix, sql):

	arcpy.AddMessage("\nWorking on %s"%group)
	muno_list = group_dict[group]
	new_fc_name = "%s_%s"%(group,suffix)
	new_fc_fullpath = os.path.join(new_gdb,group,new_fc_name)

	# creating (replacing existing) dataset
	arcpy.Delete_management(group)
	arcpy.CreateFeatureDataset_management(new_gdb, group, projfile)

	# copy the template over
	arcpy.AddMessage("Copying over template...")
	template_fc = os.path.join(ari_path, muno_list[0]) # just pick the first fc from the list
	# Make a feature layer
	arcpy.management.MakeFeatureLayer(template_fc, "temp_layer")
	# Apply a selection that returns zero records (e.g., impossible condition)
	arcpy.management.SelectLayerByAttribute("temp_layer", "NEW_SELECTION", "1=0")
	arcpy.management.CopyFeatures("temp_layer", new_fc_fullpath)


	# append
	for in_fc in muno_list:
		in_fc_fullpath = os.path.join(ari_path,in_fc)
		arcpy.AddMessage("Appending %s"%in_fc)
		if sql == None:
			arcpy.management.Append(in_fc_fullpath, new_fc_fullpath, "NO_TEST")
		else:
			arcpy.AddMessage("\tSelecting where %s"%sql)
			arcpy.management.MakeFeatureLayer(in_fc_fullpath, "temp_lyr")
			arcpy.management.SelectLayerByAttribute("temp_lyr", "NEW_SELECTION", sql)
			arcpy.AddMessage("\tAppending...")
			arcpy.management.Append("temp_lyr", new_fc_fullpath, "NO_TEST")




if __name__ == '__main__':

	ari_path = r'C:\Users\KimDan\Government of Ontario\Forest Explorer - FRO\FRO2026\02InventoryCleanUp\ARI_wFU.gdb' # 'template' fc should be included in this gdb
	new_gdb = r'C:\Users\KimDan\Government of Ontario\Forest Explorer - FRO\FRO2026\02InventoryCleanUp\ARI_base_meged.gdb' # must already exist
	# suffix = 'FOR' # to name the new fc. no special character here!
	suffix = '' # name the new fc. no special character here.
	# sql = "POLYTYPE='FOR'" # put None if no selection
	sql = None # put None if no selection

	for group in group_dict.keys():
		main(ari_path, new_gdb, group, suffix, sql)