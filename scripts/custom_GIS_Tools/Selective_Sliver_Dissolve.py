# slivers will be merged to neighboring polygon with similar attributes
version = 0.1.0

import arcpy
from datetime import datetime
import os

# my library
from messages import print_n_log


def main(inputfc, outputWS, uniq_id_fname, sliver_SQL, fields_to_match):

	starttime = datetime.now()

	# start logging
	p = print_n_log()
	p.print2("Selective Sliver Dissolve Tool v%s"%version)
	p.print2('Start of process: %(start)s.' %{'start':starttime.strftime('%Y-%m-%d %H:%M:%S')})

	arcpy.env.workspace = outputWS
	outputfc_filename = os.path.split(outputfc)[1]

	if outputWS.upper().endswith('.GDB'):
		gdbpath = outputWS
	else:
		gdbpath = os.path.split(outputWS)[0] # gdb path is used later to create log file on its parent folder
	p.print2("path to gdb: %s"%gdbpath)

	# check if the input has mandatory fields
	p.print2("Checking mandatory fields...")
	mand_fields = fields_to_match + ['SHAPE_AREA',uniq_id_fname] ################# fields_to_match must be a list of fieldnames.
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
	arcpy.MakeFeatureLayer_management(inputfc, "lyr0")
	rec_count_orig = arcpy.management.GetCount("lyr0")
	p.print2("\nTotal Number of records = %s\n"%rec_count_orig)

	# select 1st SQL
	p.print2("Running the First SQL: %s"%first_elim_SQL)
	arcpy.management.SelectLayerByAttribute("lyr0", "NEW_SELECTION", first_elim_SQL)
	rec_count_1st_select = arcpy.management.GetCount("lyr0")
	p.print2("Selected %s records out of %s"%(rec_count_1st_select,rec_count_orig,))

	output1, output2, output3 = None,None,None

	# run 1st Eliminate
	p.print2("Running the Eliminate tool the first time...")
	output1 = outputfc_filename + "_1stElim"
	arcpy.Eliminate_management("lyr0",output1,elim_by_border, exclusion_SQL)
	arcpy.MakeFeatureLayer_management(output1, "lyr1")
	rec_count_output1 = arcpy.management.GetCount("lyr1")
	p.print2("Success! Output fc feature count: %s\n\n"%rec_count_output1)




if __name__ == '__main__':

	inputfc = arcpy.GetParameterAsText(0)
	outputWS = arcpy.GetParameterAsText(1) # should be the path to an existing gdb
	uniq_id_fname = arcpy.GetParameterAsText(2) # text
	sliver_SQL = arcpy.GetParameterAsText(3) # should be an SQL that you can run on the inputfc
	fields_to_match = arcpy.GetParameterAsText(4) # list of fields in inputfc that needs to match with the sliver for the polygons to merge

	# checking the inputs - debug only
	for i in [inputfc, outputWS, uniq_id_fname, sliver_SQL, fields_to_match]:
		arcpy.AddMessage(i)

	main(inputfc, outputWS, uniq_id_fname, sliver_SQL, fields_to_match)