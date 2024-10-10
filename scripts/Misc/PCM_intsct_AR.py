# intersect all pcms with ARs then merge them into one fc

import os, traceback
import arcpy


mu_list = ['035','060','067','110','120','130','140','175','177','210','220','230','280','350','360','390','405','406','415','421','438','451','490','509','535','565','601','615','644','680','702','754','780','796','815','840','853','889','898','930','965','966','994']
# mu_list = ['035','060','110','120','130','140','175','177','210','220','230','280','350','360','390','406','415','421','438','443','451','490','574','535','601','615','644','680','702','754','780','796','816','840','889','898','930','966']
# mu_list = ['035','060'] # test

ar_fc = r'C:\Users\kimdan\OneDrive - Government of Ontario\_FPPS\Projects\_Spooner_David_Peter\Reuters_AR_vs_OldGrowth\AR_vs_OldGrowth.gdb\HRV_All_2016to2020'
in_pcm_path = r'U:\Backup_data\Drive_Bak\D_Thing1\GeoData\PCM2015.gdb\PCM'
out_path = r'C:\Users\kimdan\OneDrive - Government of Ontario\_FPPS\Projects\_Spooner_David_Peter\Reuters_AR_vs_OldGrowth\AR_vs_OldGrowth.gdb'
projfile = "C:\\Users\\kimdan\\Government of Ontario\\Forest Explorer - Data\\E\\AR\\MNRLambert_d.prj"

# delete feature dataset, create feature dataset
arcpy.AddMessage("Generating new dataset...")
new_dataset = "pcm_intsct_ar"
arcpy.Delete_management(new_dataset)
arcpy.CreateFeatureDataset_management(out_path, new_dataset, projfile)


merge_fc_list = []

for mu in mu_list:
	arcpy.AddMessage("Performing intersect on mu%s..."%mu)
	in_pcm = os.path.join(in_pcm_path,"pcm"+mu)
	out_fc = os.path.join(out_path,new_dataset,"pcm"+mu+"_intsct_AR")

	try:
		arcpy.analysis.PairwiseIntersect(
		    in_features=[ar_fc,in_pcm],
		    out_feature_class=out_fc,
		    join_attributes="ALL",
		    cluster_tolerance=None,
		    output_type="INPUT"
		)
		merge_fc_list.append(out_fc)
		arcpy.AddMessage("\tDone!")
	except Exception as e:
		arcpy.AddWarning("\tError while processing mu%s"%mu)
		arcpy.AddWarning(str(e))


arcpy.AddMessage("\nMerging All...")
arcpy.management.Merge(
   	inputs=merge_fc_list,
   	output=os.path.join(out_path,"f_pcmAll_intsct_AR"),
)
arcpy.AddMessage("\tDone!")



