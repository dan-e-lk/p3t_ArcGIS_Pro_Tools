# for all fcs in a gdb, creates a new field and populate it with a default value
# mainly used for Tableau because tableau needs a field to join all the layers together.
import arcpy
import os

def main(gdb, new_fname, ftype, default_val=None):
	arcpy.env.workspace = gdb
	fc_lst = [os.path.join(gdb,fcname) for fcname in arcpy.ListFeatureClasses()]

	for fc in fc_lst:
		arcpy.AddMessage("Working on %s..."%fc)
		# see if the field exists already
		f_check = arcpy.ListFields(fc,new_fname)
		if len(f_check) == 0:
			arcpy.AddMessage("\tAdding a new field")
			arcpy.management.AddField(fc, new_fname, ftype)
		else:
			arcpy.AddMessage("\t%s field already exists"%new_fname)
		# populate the field with the default value
		if default_val != None:
			arcpy.AddMessage("\tPopulating the new field")
			arcpy.management.CalculateField(fc, new_fname, default_val, "PYTHON3")



if __name__ == '__main__':
	gdb = r'C:\Users\kimdan\OneDrive - Government of Ontario\_OnGoingProj\Moose_RelationalAgreement\Data\Tableau.gdb'
	new_fname = 'tableau'
	ftype = "SHORT"
	default_val = 1
	main(gdb, new_fname, ftype, default_val)