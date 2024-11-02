# Incomplete!!
# Will continue after completing fc_to_sqlite tool

# This script changes the original feature class - so make sure to copy the fc over if you want to keep the original fc
# this script uses the sqlite database as well as sql files stored in the same directory.


import tempfile, os, sqlite3
import arcpy

script_dir = os.path.dirname(os.path.abspath(__file__))

def main(input_inventory):
	pass



if __name__ == '__main__':
	input_inventory = r'T:\FMP_AR_AWS\Dryden\PIAM_FC535\PIAM.gdb\t_FC535'
	main(input_inventory)