# This script is to be used to turn inventory data such as PCM into OLT supported shapefile (with OLT-compatible fields).

# workflow:
# 1. creates a temporary gdb in the specified output folder
# 2. creates a template fc in the temp gdb which has all the correct field for the OLT use
# 3. copies the input file over to the temp gdb (convert to fc if needed)
# 4. checks the copied input file, make sure it has correct field names.
# 5. checks the copied input file, make sure the data is good to be appended over.
# 	 field names and each record will be edited where necessary (look at create_template.py for field name correction)
# 6. append the copied input file to the template fc from step 2.
# 7. export the template fc as shapefile and delete the temporary gdb.


import modules.create_template as create_template
import modules.copy_and_clean as copy_and_clean

import os, datetime, shutil

import arcpy # this is limited to this python script. Other modules that this script calls (such as create_template) must use arcpy




def main(input_path,output_folder,owner_select):

	date_today = datetime.datetime.now().strftime('%Y-%m-%d') # eg. '2018-29-09'
	unique_suffix = datetime.datetime.now().strftime('%Y%m%d%H%M%S') # eg. '20180118152912'

	# Creating a file geodatabase in the user-specified output folder
	output_gdb = create_template.create_gdb(output_folder,unique_suffix) # eg. \\lrcpsoprfp00001\MNR_NER\GI_MGMT\Tools\Scripts\FMPTools_2017\FMP_SpatialData_Compiler\compiler_output\Compiler_Output_201801181703.gdb\bmi_201801181703
	print2('\nOutput Location: ' + str(output_gdb))


	try:
		# Creating the template feature class with all the correct fields
		template_fc = create_template.create_template(output_gdb,input_path,unique_suffix,owner_select) # this will be the full path of the template FC created.

		# copying the original data to the output location and if necessary, renaming fieldnames and editing the data itself (for example, if string value is in int field)
		temp_fc_path, rec_count = copy_and_clean.copy_and_clean(output_gdb, input_path, owner_select)

		# append
		print2('Appending the copied and cleaned data to the template fc...')
		arcpy.Append_management(inputs=temp_fc_path, target=template_fc, schema_type="NO_TEST")

		# check counts
		count_again = copy_and_clean.rec_counter(template_fc)
		if count_again == rec_count:
			print2('All (%s) records have been appended without an error.'%rec_count)
		else:
			print2('!Not all records have been appended to the OLT template feature class!\nOriginal: %s\nAppended: %s'%(rec_count,count_again), 'warning')

		# export to shp
		print2('Exporting the data to shapefile...')
		arcpy.FeatureClassToShapefile_conversion(Input_Features=template_fc, Output_Folder=output_folder)

	finally:
		# cleaning up...
		print2('Cleaning up...')
		try:
			shutil.rmtree(output_gdb)
		except:
			pass

	os.startfile(output_folder)



def print2(msg, msgtype = 'msg'):
	""" print, arcmap AddMessage and return string all in one!"""
	print(msg)
	if msgtype == 'msg':
		arcpy.AddMessage(msg)
	elif msgtype == 'warning':
		arcpy.AddWarning(msg)
	return msg





if __name__ == '__main__':
	input_path = arcpy.GetParameterAsText(0)
	output_folder = arcpy.GetParameterAsText(1)
	owner_select = arcpy.GetParameterAsText(2) # this should have a working SQL such as "OWNER in ('CROWN','PARKS')"


	main(input_path,output_folder, owner_select)