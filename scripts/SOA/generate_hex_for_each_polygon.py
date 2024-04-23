# this script is intended to generate hexagon tessellation for each FMU and cut out to the exact shape of that FMU.
# The output of this tool will always have MNR Lambert conformal conic projection
# "Generate Tesselation" is the main geoprocessing tool used

import arcpy, os

def main(in_fc,name_field,out_gdb,h3_level):
	
	arcpy.env.workspace = ws = out_gdb

	# make a new feature dataset with MNR Lambert Conformal Conic Projection
	DS_name = "mnr_lamb_H3_L%s"%h3_level
	arcpy.AddMessage("Generating dataset: %s..."%DS_name)
	# find the projection file location
	projfile = os.path.join(os.path.split(os.path.split(__file__)[0])[0],"MNRLambert_d.prj")
	if not os.path.isfile(projfile):
		# if the file doesn't exist, show error
		arcpy.AddError("Can't find MNRLambert_d.prj file at the parent folder of %s"%__file__)
		raise
	arcpy.Delete_management(DS_name)
	arcpy.CreateFeatureDataset_management(out_gdb, DS_name, projfile)
	arcpy.AddMessage("Dataset successfully generated!")
	sr = arcpy.SpatialReference(projfile) # This will be used later


	# copy the in_fc (the FMU layer) to the new DS
	arcpy.AddMessage("Copying %s to %s"%(in_fc,DS_name))
	in_fc_newname = os.path.split(in_fc)[1] + '_mnr_lamb'
	arcpy.FeatureClassToFeatureClass_conversion(in_fc, DS_name, in_fc_newname)


	# get extent for each polygons
	extent_dict = {}
	with arcpy.da.SearchCursor(in_fc_newname, ['SHAPE@',name_field]) as rows:
		for row in rows:
			name = row[1]
			extent = row[0].extent
			Xmin, Ymin, Xmax, Ymax = extent.XMin, extent.YMin, extent.XMax, extent.YMax
			extent_dict[name] = extent
			arcpy.AddMessage(name)
			arcpy.AddMessage("Xmin: %s\nYmin: %s\nXmax: %s\nYmax: %s\n"%(Xmin, Ymin, Xmax, Ymax))


	# run generate tess on each polygon, then spatial join with that polygon
	for name, ext in extent_dict.items():
		out_fc = 't_'+name
		arcpy.AddMessage("generating hexagons for %s:"%name)
		arcpy.management.GenerateTessellation(out_fc, Extent=ext, Shape_Type="H3_HEXAGON", H3_Resolution=h3_level, Spatial_Reference=sr)

		# spatial join
		arcpy.AddMessage("\trunning spatial join...")
		# make feature layer with only that polygon selected and only the name_field (FMU_CODE) visible.
		fields= arcpy.ListFields(in_fc)
		fieldinfo = arcpy.FieldInfo()
		for field in fields:
			if field.name == name_field:
				fieldinfo.addField(field.name, field.name, "VISIBLE", "NONE")
			else:
				fieldinfo.addField(field.name, field.name, "HIDDEN", "NONE")
		arcpy.management.MakeFeatureLayer(in_fc, "temp", "%s='%s'"%(name_field,name), field_info=fieldinfo)
		out_fc2 = os.path.join(out_gdb,DS_name,'f_'+name)
		arcpy.analysis.SpatialJoin(out_fc, "temp", out_fc2,"#","KEEP_COMMON","#","HAVE_THEIR_CENTER_IN")

		# clean up useless fields
		arcpy.AddMessage("\tcleaning up fields")
		useless_fields = ['Join_Count','TARGET_FID','Shape_Length_1','Shape_Area_1']
		for f in useless_fields:
			try:
				arcpy.management.DeleteField(out_fc2, f)
			except:
				pass

		# delete the temporary files
		arcpy.AddMessage("\tdeleting temp file")
		arcpy.Delete_management(out_fc)



if __name__ == '__main__':

	in_fc = r'C:\Users\kimdan\Government of Ontario\GIS Data - Documents\GDDS\GDDS-Internal-MNRF.gdb\FOREST_MANAGEMENT_UNIT' # FMU layer
	name_field = 'FMU_CODE' # A TEXT field from in_fc. the values of this field should be unique
	out_gdb = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\E\AR\SOA_hex\FMU_in_hex_L11.gdb' # this gdb must already exist
	h3_level = 11 # at lvl 11, it takes 30mins per FMU to run this tool.


	main(in_fc,name_field,out_gdb,h3_level)