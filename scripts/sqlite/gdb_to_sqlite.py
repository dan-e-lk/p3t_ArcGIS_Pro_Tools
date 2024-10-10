# incomplete!!!!

# turns all fcs in the gdb into tables in sqlite
# only works on polygon, polyline, point and table fc
# does not keep the relationship information (may be something to work on later)

import sqlite3
import arcpy

def main(input_gdb,output_folder):
	pass


if __name__ == '__main__':
	# input_gdb = arcpy.GetParameterAsText(0)
	# output_folder = arcpy.GetParameterAsText(1)

	input_gdb = r'C:\Users\kimdan\OneDrive - Government of Ontario\_FPPS\Projects\JustinGaudon\Clupa_foraging.gdb'
	output_folder = r'C:\Users\kimdan\OneDrive - Government of Ontario\_FPPS\Projects\JustinGaudon\sqlite'

	main(input_gdb,output_folder)