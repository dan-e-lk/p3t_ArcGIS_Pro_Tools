# Just need to append a bunch of PIAMs together

import arcpy
import os

group_dict = {
	'GLSL': ['140','210','220','360','451','615','680','754','780','889','898'], # based on the sqls used
	'NEBOR': ['060','110','280','390','421','438','574','601','930'],
	'NWBOR': ['035','120','130','175','177','230','350','406','415','443','490','535','644','702','796','816','840','966','994'],
}

projfile = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"MNRLambert_d.prj")


def main(piam_path, new_gdb, group, suffix, sql):

	muno_list = group_dict[group]
	new_fc_name = "%s_%s"%(group,suffix)
	new_fc_fullpath = os.path.join(new_gdb,group,new_fc_name)

	# creating (replacing existing) dataset
	arcpy.Delete_management(group)
	arcpy.CreateFeatureDataset_management(new_gdb, group, projfile)

	# copy the template over
	arcpy.AddMessage("Copying over template...")
	template_fc = os.path.join(piam_path, 'template')
	arcpy.conversion.FeatureClassToFeatureClass(template_fc, new_gdb+"\\"+group, new_fc_name)

	# append
	for muno in muno_list:
		in_fc = 'FC%s'%muno
		in_fc_fullpath = os.path.join(piam_path,'INV',in_fc)
		arcpy.AddMessage("Appending %s"%in_fc)
		if sql == None:
			arcpy.management.Append(in_fc_fullpath, new_fc_fullpath, "NO_TEST")
		else:
			arcpy.AddMessage("\tSelecting where %s"%sql)
			arcpy.management.MakeFeatureLayer(in_fc_fullpath, "temp_lyr")
			arcpy.management.SelectLayerByAttribute("temp_lyr", "NEW_SELECTION", sql)
			arcpy.management.Append("temp_lyr", new_fc_fullpath, "NO_TEST")




if __name__ == '__main__':

	piam_path = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\D\GeoData\PIAMMar2024.gdb' # 'template' fc should be included in this gdb
	new_gdb = r'T:\FMP_AR_AWS\PIAM_Roll-up\PIAM_Merge.gdb' # must already exist
	group = 'NWBOR' # must match group_dict.  This will also be the name of the dataset
	suffix = 'FOR_over_5000m2' # to name the new fc. no special character here!
	sql = "POLYTYPE='FOR' AND HA>0.5" # put None if no selection


	main(piam_path, new_gdb, group, suffix, sql)