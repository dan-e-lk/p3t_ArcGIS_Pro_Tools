# there's no arcgis tool for this script yet.
# raster file with float values must first be converted in order to run other operaions such as tabulate area or zonal statistics.
# this script turns float values into integers


import arcpy
import os


def main(input_raster,output_raster):
	arcpy.AddMessage("Working on %s..."%input_raster)
	out_int_raster = arcpy.sa.RasterCalculator([input_raster],["x"],"Int(RoundDown(x+0.5))")
	out_int_raster.save(output_raster)



if __name__ == '__main__':

	source_gdb = r'C:\Users\kimdan\Government of Ontario\Forest Data Portal - T2 FRI\Dog River -Matawin\DRM_T2_Inventory_Feb12-20220217T145602Z-002\DRM_T2_Inventory_Feb12\DRM_T2_Inventory_Rasters\DRM_T2_Inventory_Rasters.gdb'
	raster_names = ['BasalArea','Biomass','CDHT','GTV','GMV_NL','TopHt','Stems']
	target_gdb = r'C:\Users\kimdan\OneDrive - Government of Ontario\_FPPS\Projects\VolumeComparison_T2\_T2LiDAR_DRM_biggerArea\T2DRM.gdb'
	prefix = 'int_'

	for r in raster_names:
		input_raster = os.path.join(source_gdb,r)
		output_raster = os.path.join(target_gdb,prefix+r)
		main(input_raster,output_raster)