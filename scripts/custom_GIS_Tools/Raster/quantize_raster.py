# there's no arcgis tool for this script yet.
# raster file usually have a huge range of values. It's nice to bin them into 20 or 30 categories.
# this script bins the raster values into a number of categories - useful for distribution assessment.


import arcpy
import os


def main(input_raster,output_raster,num_of_categ):
	arcpy.AddMessage("Working on %s..."%input_raster)
	n = num_of_categ

	# find min,max,range
	my_raster = arcpy.Raster(input_raster)
	rmin = my_raster.minimum
	rmax = my_raster.maximum
	rmean = my_raster.mean
	rrange = rmax-rmin
	factor = rrange/n
	arcpy.AddMessage("Min: %s, Max: %s, Range: %s, Mean: %s"%(rmin,rmax,rrange,rmean))

	# this process won't work if the range is smaller than the number of categories
	if n>rrange:
		arcpy.AddError("Range of your raster values are smaller than the number of categories you've entered.\n \
Run Raster Calculator and multiply your raster values by a certain number (say x100) to increase the range.")
	else:
		if n>rrange/2:
			arcpy.AddWarning("Your raster doesn't have range big enough to categorize them into %s bins. Try less number of bins"%num_of_categ)
		formula = "Int({min}+(RoundDown((x-{min})/{fact}+0.5)*{fact}))".format(min=rmin,fact=factor)
		out_int_raster = arcpy.sa.RasterCalculator([input_raster],["x"],formula)
		out_int_raster.save(output_raster)
		
		new_raster = arcpy.Raster(output_raster)
		new_mean = new_raster.mean
		arcpy.AddMessage("Original Mean: %s vs New Mean: %s"%(rmean,new_mean))
		arcpy.AddMessage("Success!\n")



if __name__ == '__main__':

	source_gdb = r'C:\Users\kimdan\Government of Ontario\Forest Data Portal - T2 FRI\Dog River -Matawin\DRM_T2_Inventory_Feb12-20220217T145602Z-002\DRM_T2_Inventory_Feb12\DRM_T2_Inventory_Rasters\DRM_T2_Inventory_Rasters.gdb'
	# raster_names = ['BasalArea','Biomass','CDHT','GTV','GMV_NL','TopHt','Stems']
	raster_names = ['CDHT','TopHt']
	# raster_names = ['BasalArea']
	target_gdb = r'C:\Users\kimdan\OneDrive - Government of Ontario\_FPPS\Projects\VolumeComparison_T2\_T2LiDAR_DRM_biggerArea\T2DRM.gdb'
	num_of_categ = 10


	prefix = "bin%s_"%num_of_categ
	for r in raster_names:
		input_raster = os.path.join(source_gdb,r)
		output_raster = os.path.join(target_gdb,prefix+r)
		main(input_raster,output_raster,num_of_categ)