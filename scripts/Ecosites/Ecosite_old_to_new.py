# This script alters the original data!
# This script is designed for Romeo Malette inventory, so it works best on Romeo.
# Romeo inventory has "Ecosite" field that carries values such as 'NE5m' or 'NE6c'.
# This script converts those values into the new Ecosite values such as B098 and B040.
# if there are multiple "Best Fit" ecosites - eg. 'NE5m' can be 'B098' or 'B114' - the script will just pick the first one.

import os, collections
import arcpy
import Ecosite_crosswalk_dict as ecd


def main(input_inventory,ecosite_fieldname,new_ecosite_fieldname):

	# create a new text attribute(field) = new_ecosite_fieldname
	arcpy.AddMessage("\nCreating a new field: %s"%new_ecosite_fieldname)
	try:
		arcpy.management.AddField(input_inventory,new_ecosite_fieldname, "TEXT", field_length= 10)
	except:
		arcpy.AddWarning("\nFailed to create the new field. Check if '%s' field already exists!"%new_ecosite_fieldname)
		raise

	# we could use field calculator here, but I am gonna go with update cursor
	arcpy.AddMessage("\nPopulating new ecosite values to the %s field..."%new_ecosite_fieldname)
	where_sql = "%s IS NOT NULL"%ecosite_fieldname
	errors = []
	success = []
	with arcpy.da.UpdateCursor (input_inventory, [ecosite_fieldname, new_ecosite_fieldname], where_clause = where_sql) as cursor:
		for row in cursor:
			old_eco = row[0][2:].strip()
			try:
				new_eco = ecd.NER_Ecosites[old_eco][0][0]
				row[1] = new_eco
				success.append('%s => %s'%(row[0],new_eco))
			except KeyError:
				errors.append(row[0])

			# the most important line of script that I always forget
			cursor.updateRow(row)


	if len(errors) == 0:
		arcpy.AddMessage('\nAll old ecosites has been converted to the new ecosites!')
	else:
		arcpy.AddWarning("\nNot all old ecosites has been converted to the new ecosites")
		error_summary = collections.Counter(errors) # eg. Counter({'NE99': 2, 'K13': 1}) - ones that didn't show up in the ecosite crosswalk dictionary
		arcpy.AddMessage("\nCollections of errors (most common to least common):")
		for e in error_summary.most_common(): # this sorts the counter by the occurence frequency
			arcpy.AddMessage('\n%s'%e)

	if len(success) > 0:
		success_summary = collections.Counter(success)
		arcpy.AddMessage("\nCollections of successful ecosite conversions (most common to least common):")
		for suc in success_summary.most_common(): # this sorts the counter by the occurence frequency
			arcpy.AddMessage('\n%s'%suc)







if __name__ == '__main__':
	input_inventory = r'C:\Users\kimdan\Government of Ontario\Forest Data Portal - SRNV2023_INV_PREP\Daniel\temp_Romeo.gdb\romeo_malette_only'
	ecosite_fieldname = "PRI_ECO"
	new_ecosite_fieldname = "Ecosite_New"

	main(input_inventory,ecosite_fieldname,new_ecosite_fieldname)
