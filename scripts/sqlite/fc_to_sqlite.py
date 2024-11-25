# exports a feature class to a table in SQLite3 database.
# you can export it to an existing sqlite3 database OR create a new sqlite3 database.
# if you are exporting it to an existing database, note that 
# 	if the name of the new table you are about to create already exists, your new table will replace (delete) the existing table.

import os, sqlite3
import arcpy


# ESRI field.type to sqlite field type:
# anything that doesn't match will be turned to TEXT
fieldtype_map = {
	"OID": "INTEGER",
	"Integer": "INTEGER",
	"String": "TEXT",
	"SmallInteger": "INTEGER",
	"BigInteger": "INTEGER",
	"Double": "REAL",
	"Single": "REAL"
}


def fc_to_sqlite(input_fc,output_sqlite_file,output_tablename):

	# grab all fieldnames and fieldtypes from the fc
	fields = arcpy.ListFields(input_fc)
	f_name_n_type = {f.name:f.type for f in fields if f.name.upper() not in ['SHAPE']} # removing Shape field. add more field to remove if you want.
	# for fname, ftype in f_name_n_type.items():
	# 	arcpy.AddMessage("%s\t\t:%s"%(fname,ftype))

	# map ESRI fieldtype and Sqlite3 fieldtypes
	f_name_n_type2 = {}
	for fname, ftype in f_name_n_type.items():

		try:
			new_ftype = fieldtype_map[ftype]
		except KeyError:
			new_ftype = "TEXT" # TEXT by default
		f_name_n_type2[fname] = new_ftype
	# for fname, ftype in f_name_n_type2.items():
	# 	arcpy.AddMessage("%s\t\t:%s"%(fname,ftype))

	# create a new table in the sqlite database - delete and replace if one already exists
	# write SQL first
	create_t_sql = "CREATE TABLE %s ("%output_tablename
	for fname, ftype in f_name_n_type2.items():
		create_t_sql += " %s %s,"%(fname,ftype)
	create_t_sql = create_t_sql[:-1] # delete the trailing comma
	create_t_sql += ");"

	# open existing (or create new then open) sqlite file
	con = sqlite3.connect(output_sqlite_file)
	cur = con.cursor()

	delete_t_sql = "DROP TABLE IF EXISTS %s;"%output_tablename
	cur.execute(delete_t_sql)

	arcpy.AddMessage("Creating a new table: %s"%output_tablename)
	arcpy.AddMessage(create_t_sql)
	cur.execute(create_t_sql)

	# save all data into memory and make a giant single SQL query
	# INSERT INTO tablename (column1,column2 ,..)
	# VALUES ( value1,	value2 ,...), ( value1,	value2 ,...)....;
	# skip this if there are no records
	rec_count = int(arcpy.management.GetCount(input_fc)[0])
	arcpy.AddMessage("Record count: %s"%rec_count)
	if rec_count > 0:
		arcpy.AddMessage("Generating INSERT Query...")
		insert_sql = "INSERT INTO %s ("%output_tablename

		fname_list = list(f_name_n_type2.keys())
		for fname in fname_list:
			insert_sql += "%s,"%fname
		insert_sql = insert_sql[:-1] # delete trailing comma

		insert_sql += ") VALUES "
		with arcpy.da.SearchCursor(input_fc, fname_list) as cursor:
			for row in cursor:
				row_values_sql = "("
				for i, fname in enumerate(fname_list):
					if row[i] == None:
						row_values_sql += "null,"
					elif f_name_n_type2[fname] == "TEXT": # if it's text, you gotta wrap it
						text_value = str(row[i]).replace("'","''") # replace apostrophe with double apostrophe for text handling
						row_values_sql += "'%s',"%text_value
					else:
						row_values_sql += "%s,"%row[i]
				row_values_sql = row_values_sql[:-1] # delete trailing comma
				row_values_sql += ")," # eg. "(value1,value2,...),"
				insert_sql += row_values_sql

		insert_sql = insert_sql[:-1] # delete trailing comma
		insert_sql += ";"

		arcpy.AddMessage("Executing INSERT Query...")
		# arcpy.AddMessage(insert_sql)
		cur.execute(insert_sql)
		del insert_sql

	con.commit()
	con.close()




if __name__ == '__main__':
	# this is the original input
	# input_fc = r'T:\FMP_AR_AWS\Dryden\PIAM_FC535\PIAM.gdb\t_FC535_4k_records'
	# output_sqlite_file = r"T:\FMP_AR_AWS\Dryden\PIAM_FC535\VolCalcPlonskisNew.sqlite3" # if file already exists, this script will use the existing sqlite db
	# output_tablename = "forest_add" # WARNING - if the table with the same name already exists, it will be deleted!

	# modified input using ArcGIS Pro GUI
	input_fc = arcpy.GetParameterAsText(0)
	new_or_existing = arcpy.GetParameterAsText(1) # if file already exists, this script will use the existing sqlite db
	output_tablename = arcpy.GetParameterAsText(4) # WARNING - if the table with the same name already exists, it will be deleted!

	if new_or_existing == 'Create a new sqlite3 file':
		output_sqlite_file = arcpy.GetParameterAsText(2)
	else:
		output_sqlite_file = arcpy.GetParameterAsText(3)

	fc_to_sqlite(input_fc,output_sqlite_file,output_tablename)



	# a bonus - open folder containing the sqlite3 file
	try:
		import subprocess
		subprocess.Popen(f'explorer /select,"{output_sqlite_file}"')
	except:
		pass
