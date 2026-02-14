# T1 inventory comes in in different path, projection and fc names.
# need to somehow export them to a single dataset of MNR Lambert.
# output filenames will be FC000 where 000 is the orignal MUNO (at the time of T1 inventory, not the latest MUNO)
# Also adding fields and populating them: (ORIG_MUNO, MUNO, INV_YEAR)

# layers excluded: Lake Sup Islands, All the parks.

# To supplement this script, this is what's Manually done:
# deleted extra buffer polygons (POLYTYPE = 'XXX' or polygons in the great lakes). For example in Bancroft Minden and French Severn.





import arcpy
import os, traceback

# Check the base_path and info before running.
base_path = r'C:\Users\KimDan\Government of Ontario\Forest Explorer - Data\D\FRI\FRI_T1'

info = {
#orig MUNO  MUNO   INV_YEAR   PATH (download from GeoHub, then unzipped)
	'754': ['754', 2012, 	r'7ef7f1e9-6db6-4f56-86d4-cd7f2cb9c82a-NiF\Contract Year - 2012\NiF-754-3D.gdb\Nipissing_Dataset\Nipissing_Forest_3D'],
	'110': ['110', 2011, 	r'pp_FRI_FIMv2_AbitibiRiver_2011_2D\pp_FRI_FIMv2_AbitibiRiver_2011_2D.gdb\eFRI\Polygon_Forest_Updated24072018'],
	'615': ['615', 2013, 	r'pp_FRI_FIMv2_AlgomaForest_2013_2D\pp_FRI_FIMv2_AlgomaForest_2013_2D.gdb\Algoma_2D\Algoma_Forest_2D'],
	'451': ['451', 2011, 	r'pp_FRI_FIMv2_AlgonquinPark_2011_2D\pp_FRI_FIMv2_AlgonquinPark_2011_2D.gdb\Algonquin_eFRI\Polygon_Forest_2D'],
	'220': ['220', 2008, 	r'pp_FRI_FIMv2_BancroftMindenForest_2008_2D\pp_FRI_FIMv2_BancroftMindenForest_2008_2D.gdb\Bancroft\Ban_Mind_FRI'], # BMF had a extra buffer polygon. I deleted this manually.
	'035': ['035', 2015, 	r'pp_FRI_FIMv2_BlackSpruceForest_2015_2D\pp_FRI_FIMv2_BlackSpruceForest_2015_2D.gdb\BlackSpruce2D\FOREST_2D'],
	'175': ['175', 2012, 	r'pp_FRI_FIMv2_CaribouForest_(175)_2012_2D\pp_FRI_FIMv2_CaribouForest_(175)_2012_2D.gdb\CA_Final_2D\Polygon_Forest'],
	'405': ['406', 2010, 	r'pp_FRI_FIMv2_CrossrouteForest_2D_2010\pp_FRI_FIMv2_CrossrouteForest_2D_2010.gdb\Crossroute\Crossroute_Forest'],
	'177': ['177', 2012, 	r'pp_FRI_FIMv2_Dogriver_MatawinForest_2012_2D\pp_FRI_FIMv2_Dogriver_MatawinForest_2012_2D.gdb\DR_Matawin_FRI\Polygon_Forest'],
	'535': ['535', 2015, 	r'pp_FRI_FIMv2_DrydenForest_2015_2D\pp_FRI_FIMv2_DrydenFoest_2015_2D.gdb\Dryden_FRI\Polygon_Forest_2D'],
	'230': ['230', 2013, 	r'pp_FRI_FIMv2_EnglishRiverForest_2013_2D\pp_FRI_FIMv2_EnglishRiverForest_2013_2D.gdb\eFRI_English_River\Polygon_Forest_Trim'],
	'360': ['360', 2011, 	r'pp_FRI_FIMv2_FrenchSevernForest_2011_2D\pp_FRI_FIMv2_FrenchSevernForest_2011_2D.gdb\French_Severn_Dataset\French_Severn_Forest'], # deleted extra polygon in the Lake Huron
	'438': ['438', 2012, 	r'pp_FRI_FIMv2_GordenCosensForest_2012_2D\pp_FRI_FIMv2_GordenCosensForest_2012_2D.gdb\GCF_eFRI\Polygon_Forest'],
	'601': ['601', 2007, 	r'pp_FRI_FIMv2_HearstForest_2007_2D\pp_FRI_FIMv2_HearstForest_2007_2D.gdb\Hrst_eFRI\Polygon_Forest'],
	'644': ['644', 2015, r'pp_FRI_FIMv2_KenoraForest_(644)_2015_2D\pp_FRI_FIMv2_KenoraForest_(644)_2015_2D.gdb\Kenora_eFRI\Polygon_Forest_Kenora_2D'],
	'702': ['702', 2015, r'pp_FRI_FIMv2_LacSeulForest_2015_2D\pp_FRI_FIMv2_LacSeulForest_2015_2D.gdb\Lac_Seul_2D\Lac_Seul_Forest_2D'],
	'796': ['796', 2009, r'pp_FRI_FIMv2_LakeHeadForest_(796)_2009_2D\pp_FRI_FIMv2_LakeHeadForest_(796)_2009_2D.gdb\LAKEHEAD_2D\LAKEHEAD_FOREST'],
	'815': ['999', 2014, r'pp_FRI_FIMv2_LakeNipigonForest_2014_2D\pp_FRI_FIMv2_LakeNipigonForest_2014_2D.gdb\LakeNipigon2D\LakeNipForest'],
	'565': ['574', 2014, r'pp_FRI_FIMv2_MagpieForest(565)_2014_2D\pp_FRI_FIMv2_MagpieForest(565)_2014_2D.gdb\Magpie_2D\Pforest_2D'],
	'966': ['966', 2008, r'pp_FRI_FIMv2_MarathomBlock_2008_2D\pp_FRI_FIMv2_MarathomBlock_2008_2D.gdb\Marathon_Block\Marathon_Block'],
	'509': ['574', 2015, r'pp_FRI_FIMv2_Martel_Forest(509)_2015_2D\pp_FRI_FIMv2_Martel_Forest(509)_2015_2D.gdb\MAR_FRI\MAR_FRI_2D'],
	'140': ['140', 2014, r'pp_FRI_FIMv2_MazinawLanark_Forest_(140)_2014_2D\pp_FRI_FIMv2_MazinawLanark_Forest_(140)_2014_2D.gdb\Mazinaw2D\forest_2D'],
	'390': ['390', 2014, r'pp_FRI_FIMv2_Nagagami_Forest(390)_2014_2D\pp_FRI_FIMv2_Nagagami_Forest(390)_2014_2D.gdb\Nagagami_eFRI\NagInv_Version3'],
	'680': ['680', 2013, r'pp_FRI_FIMv2_NorthShore_Forest_(630)_2013_2D\pp_FRI_FIMv2_NorthShore_Forest_(630)_2013_2D.gdb\Northshore_2D\Northshore_2D'],
	'415': ['415', 2010, r'pp_FRI_FIMv2_Ogoki_Forest_(796)_2010_2D\pp_FRI_FIMv2_Ogoki_Forest_(796)_2010_2D.gdb\Ogoki_FRI_2D\Polygon_Forest_2D'],
	'421': ['421', 2011, r'pp_FRI_FIMv2_PinelandForest(421)_2011_2D\pp_FRI_FIMv2_PinelandForest(421)_2011_2D.gdb\Pineland_Forest\Pineland_eFRI'],
	'840': ['840', 2010, r'pp_FRI_FIMv2_RedLakeForest_2010_2D\pp_FRI_FIMv2_RedLakeForest_2010_2D.gdb\REDLAKE_2D\Redlake'],
	'853': ['406', 2013, r'pp_FRI_FIMv2_SapaweForest(853)_2013_2D\pp_FRI_FIMv2_SapaweForest(853)_2013_2D.gdb\Sapawe_eFRI\Sapawe_Pforest_noER_noCR'],
	'210': ['210', 2013, r'pp_FRI_FIMv2_SpanishForest(210)_2013_2D\pp_FRI_FIMv2_SpanishForest(210)_2013_2D.gdb\Spanish_Forest\SpanishForest_2D'],
	'889': ['889', 2013, r'pp_FRI_FIMv2_SudburyForest(889)_2013_2D\pp_FRI_FIMv2_SudburyForest(889)_2013_2D.gdb\Sudbury_forest\Sudbury_Forest2D'],
	'898': ['898', 2013, r'pp_FRI_FIMv2_TemagamiForest(898)_2013_2D\pp_FRI_FIMv2_TemagamiForest(898)_2013_2D.gdb\Temagami\Temagami'],
	'280': ['280', 2014, r'pp_FRI_FIMv2_TimiskamingForest(280)_2014_2D\pp_FRI_FIMv2_TimiskamingForest(280)_2014_2D.gdb\Timiskaming_FRI\Polygon_Forest_2D'],
	'120': ['120', 2013, r'pp_FRI_FIMv2_TroutLakeForest(120)_2013_2D\pp_FRI_FIMv2_TroutLakeForest(120)_2013_2D.gdb\Trout_Lake_eFRI\Polygon_Forest_13082016'],
	'130': ['130', 2010, r'pp_FRI_FIMv2_WabigoonForest(130)_2010_2D\pp_FRI_FIMv2_WabigoonForest(130)_2010_2D.gdb\WABIGOON_2D\Wabigoon_2D'],
	'490': ['490', 2008, r'pp_FRI_FIMv2_WhiskeyJack_2008_2D\pp_FRI_FIMv2_WhiskeyJack_2008_2D.gdb\WhiskeyJack_Forest\Pforest2D'],
	'060': ['060', 2010, r'pp_FRI_FIMv2_WhiteRiverForest_2010_2D\pp_FRI_FIMv2_WhiteRiverForest_2010_2D.gdb\WhiteRiver_eFRI\Polygon_Forest'],
}



arcpy.env.overwriteOutput = True
arcpy.env.XYTolerance = "0.01 Meters" # by default, it is 0.001 meters, which can generate 1mm-wide overlaps and gaps. So 0.01m is preferred.
projfile = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"MNRLambert_d.prj") # this works for all scripts that are one folder level deep. eg. scripts/sqlite/script.py


def t1_assemble(out_gdb):
	
	# Make a new dataset if necessary (Not gonna overwrite it)
	DS_name = 'MNR_Lamb'
	DS_fullpath = os.path.join(out_gdb,DS_name)
	DS_exists = False
	try:
		if arcpy.Describe(DS_fullpath).dataType.lower() == "featuredataset": DS_exists = True
	except:
		# will give OSError if the path doesn't exist.
		pass
	if DS_exists:
		logger.print2(" -- %s (feature dataset) already exists"%DS_name)
	else:
		logger.print2(" -- Generating dataset: %s..."%DS_name)
		# find the projection file location
		projfile = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"MNRLambert_d.prj")
		if not os.path.isfile(projfile):
			# if the file doesn't exist, show error
			arcpy.AddError("Can't find MNRLambert_d.prj file at the parent folder of %s"%__file__)
			raise
		arcpy.Delete_management(DS_name)
		arcpy.CreateFeatureDataset_management(out_gdb, DS_name, projfile)


	# loop through the info dictionary
	for orig_MUNO, i in info.items():
		new_MUNO = i[0]
		inv_year = i[1]
		orig_fc_fullpath = os.path.join(base_path,i[2])

		# export the fcs to the new dataset. renaming it based on the orig_muno
		# cannot use CopyFeatures because of the projection difference
		out_fc_name = 'FC%s'%orig_MUNO
		out_fc_fullpath = os.path.join(DS_fullpath,out_fc_name)
		if arcpy.Exists(out_fc_fullpath):
			logger.print2("%s Already Exists"%out_fc_name)
		else:
			logger.print2("\n\nCopying '%s' to the output gdb as '%s'"%(os.path.split(orig_fc_fullpath)[1],out_fc_name))
			arcpy.conversion.FeatureClassToFeatureClass(in_features=orig_fc_fullpath, out_path=DS_fullpath, out_name=out_fc_name)


		# add fields
		try:
			logger.print2("\tAdding Fields: ORIG_MUNO, MUNO, INV_YEAR")
			arcpy.AddField_management(in_table = out_fc_fullpath, field_name = 'ORIG_MUNO', field_type = "TEXT", field_length = "10")
			arcpy.AddField_management(in_table = out_fc_fullpath, field_name = 'MUNO', field_type = "TEXT", field_length = "10")
			arcpy.AddField_management(in_table = out_fc_fullpath, field_name = 'INV_YEAR', field_type = "SHORT")

			# calculating fields
			logger.print2("\tFilling out newly aded fields:\n\t\tORIG_MUNO: %s\n\t\tMUNO: %s\n\t\tINV_YEAR: %s"%(orig_MUNO,new_MUNO,inv_year))
			arcpy.management.CalculateField(out_fc_fullpath, 'ORIG_MUNO', "'%s'"%orig_MUNO)
			arcpy.management.CalculateField(out_fc_fullpath, 'MUNO', "'%s'"%new_MUNO)
			arcpy.management.CalculateField(out_fc_fullpath, 'INV_YEAR', "%s"%inv_year)


		except Exception:
			# if failes, delete the out_fc_fullpath.
			logger.print2("Something went wrong. Deleting the last feature class (%s) so you can start fresh."%os.path.split(out_fc_fullpath)[1],'w')
			arcpy.management.Delete(out_fc_fullpath)
			# print out the error
			arcpy.AddError(traceback.format_exc())



if __name__ == '__main__':

	# check the the base_path variable
	# output gdb (must already exist)
	out_gdb = r"C:\Users\KimDan\Government of Ontario\Forest Explorer - Data\D\FRI\FRI_T1\T1_raw.gdb"


	######### logfile stuff

	tool_shortname = 'T1_inv_assemble' # the output logfile will include this text in its filename.

	# importing libraries (only works if arclog.py file is located on the parent folder of this script)
	from datetime import datetime
	parent_d = os.path.split(os.path.split(__file__)[0])[0]
	sys.path.append(parent_d)
	from arclog import Print2 as p2

	# find full path where the logfile will be written
	folder_path = arcpy.Describe(out_gdb).path
	while arcpy.Describe(folder_path).dataType != 'Folder':
		folder_path = os.path.split(folder_path)[0]
	outfile = os.path.split(out_gdb)[1] + '_' + tool_shortname + '-LOG_' + datetime.now().strftime('%Y%m%d_%H%M') + '.txt'
	logfile_path = os.path.join(folder_path,outfile)

	# importing arclog in the parent directory
	logger = p2(logfile_path)

	##########

	# run the main function(s)
	t1_assemble(out_gdb)

	# finish writing the logfile
	logger.log_close()


