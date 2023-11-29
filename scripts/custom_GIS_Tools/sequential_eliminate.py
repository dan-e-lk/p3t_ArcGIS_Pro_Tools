version = '0.1.0'
# The basis of this tool is Eliminate tool from ArcGIS Pro which requires Advanced license

import arcpy
from datetime import datetime
import os

# my library
from messages import print_n_log


def main(inputfc, outputfc, elim_by_border, first_elim_SQL, second_elim_SQL, third_elim_SQL, exclusion_SQL):

	starttime = datetime.now()

	# start logging
	p = print_n_log()
	p.print2("Sequential Eliminate Tool v%s"%version)
	p.print2('Start of process: %(start)s.' %{'start':starttime.strftime('%Y-%m-%d %H:%M:%S')})

	# warning
	p.print2("\nNOTE: This tool won't run if you don't have the ADVANCED license!\n", do_not_log = True)

	# get path to the gdb or the feature dataset
	fcpath = arcpy.Describe(outputfc).path # should give full path but not including the fc name
	arcpy.env.workspace = fcpath
	outputfc_filename = os.path.split(outputfc)[1]

	if fcpath.upper().endswith('.GDB'):
		gdbpath = fcpath
	else:
		gdbpath = os.path.split(fcpath)[0] # gdb path is used later to create log file on its parent folder
	p.print2("path to gdb: %s"%gdbpath)

	# check if the input has mandatory fields
	p.print2("Checking mandatory fields...")
	mand_fields = ['SHAPE_AREA','AREA_OVER_LENG']
	existingFields = [str(f.name).upper() for f in arcpy.ListFields(inputfc)]
	for mf in mand_fields:
		if mf in existingFields:
			pass
		else:
			msg = "%s field is missing!"%mf
			arcpy.AddWarning(msg)
			raise Exception(msg)
	p.print2("All mandatory fields are there.")

	# create 1st temporary layer
	arcpy.MakeFeatureLayer_management(inputfc, "lyr1")
	rec_count_orig = arcpy.management.GetCount("lyr1")
	p.print2("\nTotal Number of records = %s\n"%rec_count_orig)

	# select 1st SQL
	p.print2("Running the First SQL: %s"%first_elim_SQL)
	arcpy.management.SelectLayerByAttribute("lyr1", "NEW_SELECTION", first_elim_SQL)
	rec_count_1st_select = arcpy.management.GetCount("lyr1")
	p.print2("Selected %s records out of %s"%(rec_count_1st_select,rec_count_orig,))

	# run 1st Eliminate
	arcpy.Eliminate_management("lyr1",outputfc_filename+"_1",elim_by_border, exclusion_SQL)




if __name__ == '__main__':

	inputfc = arcpy.GetParameterAsText(0)
	outputfc = arcpy.GetParameterAsText(1)
	elim_by_border = arcpy.GetParameterAsText(2)
	first_elim_SQL = arcpy.GetParameterAsText(3)
	second_elim_SQL = arcpy.GetParameterAsText(4)
	third_elim_SQL = arcpy.GetParameterAsText(5)
	exclusion_SQL = arcpy.GetParameterAsText(6)

	elim_by_border = "LENGTH" if elim_by_border == 'true' else "AREA"

	main(inputfc, outputfc, elim_by_border, first_elim_SQL, second_elim_SQL, third_elim_SQL, exclusion_SQL)