# exports a feature class

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


def main(input_fc,output_sqlite_file,output_tablename):

	# grab all fieldnames and fieldtypes from the fc
	fields = arcpy.ListFields(input_fc)
	f_name_n_type = {f.name:f.type for f in fields}
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

	# use search cursor to loop through the data and enter the data line by line
	# OR
	# save all data into memory and do it all at once

	con.commit()
	con.close()




if __name__ == '__main__':
	input_fc = r'T:\FMP_AR_AWS\Dryden\PIAM_FC535\PIAM.gdb\t_FC535'
	output_sqlite_file = r"T:\FMP_AR_AWS\Dryden\PIAM_FC535\VolCalcPlonskis2.sqlite3" # if file already exists, this script will use the existing sqlite db
	output_tablename = "forest" # WARNING - if the table with the same name already exists, it will be deleted!
	main(input_fc,output_sqlite_file,output_tablename)