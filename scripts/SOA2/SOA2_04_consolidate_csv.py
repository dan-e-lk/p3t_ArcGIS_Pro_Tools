version = '1a'
"""
Created on Thu Nov 28 15:52:24 2019
Modified on Jul 14, 2026.

@author: kimdan
"""
# future update: run Generate LatLon before running Consolidate csv.

# The beauty of this script is that it will find all the common fields in csv files and you have option to end up with only the common fields.


# This script doesn't really require arcpy. arcpy is only being used for User Interface portion.

import csv, datetime, os
try:
	import arcpy
except:
	pass

def merge_all_csv(csv_list, output_folder, just_common_fields = False):
	"""
	Merges all input csv files into one csv file.
	Assumes the first row of each csv files contains the fieldnames.
	Creates a new field if a new fieldname appears on the next csv file.
	fieldnames doesn't have to be case sensitive.
	"""
	file_fieldname = 'File_Origin_' # a new field of this name will be created to store the original file name. This can be modified.
	msg = ''
	all_records = [] # list of dictionaries. eg [{'ID': 201, 'MEAN': 4.33}, {'ID': 331, 'MEAN': 7.13}]
	fields_dict = {} # {filename: {a, set, of, fields}}
	count_all = 0

	record_counter = {}
	for csvfile in csv_list:
		msg += print2(csvfile)
		csv_dict = csv.DictReader(open(csvfile))
		dict_list = []
		count = 0

		csvfile_name = os.path.split(csvfile)[1]
		for record in csv_dict:
			# add the filename to each record
			record[file_fieldname] = csvfile_name
			# edit all the fieldnames to uppercase
			dict_list.append({k.upper(): v for k, v in record.items()})
			count += 1

		if count > 0:
			all_records += dict_list
			record_counter[csvfile] = count
			count_all += count

			# grab list of fieldnames
			fieldnames = [fieldname for fieldname in dict_list[0].keys()]

			# add the fieldnames to unique fields set - will only be added if the fieldname doesn't already exist in the set.
			fields_dict[csvfile] = set(fieldnames)

			msg += print2('fieldnames: %s'%fieldnames)
			msg += print2('Number of records: %s\n'%count)
		else:
			msg += print2('\n!!!!Number of records: %s\n\tSkipping This file!!\n\n'%count)

	# get common fields of all files AND get a list of all unique fields
	list_of_sets_of_fields = [fields for fields in fields_dict.values()]
	common_fields = set.intersection(*list_of_sets_of_fields)
	all_fields = set.union(*list_of_sets_of_fields)

	msg += print2('List of Common Fields:\n%s\n\nList of All Fields:\n%s\n'%(common_fields, all_fields))

	# whether to use common fields or all fields...
	fields = list(common_fields) if just_common_fields else list(all_fields)

	# create the consolidated csv file and readme file
	yearmonthdate = datetime.datetime.now().strftime('%Y%m%d')
	new_csv_name = 'consolidated_on_'+ yearmonthdate + '.csv'
	new_csv_path = os.path.join(output_folder,new_csv_name)
	new_txt_name = 'consolidated_on_'+ yearmonthdate + '.txt'
	new_txt_path = os.path.join(output_folder,new_txt_name)

	with open(new_csv_path,  "w", newline="", encoding="utf-8") as csvfile:
		# well, dict writer doesn't work unless all your csvs have exact same fieldnames. so we will do it the hard way.
		writer = csv.writer(csvfile, delimiter=',', quotechar='"')
		writer.writerow(fields)
		count_again = 0		
		for record in all_records:
			row = []
			for f in fields:
				try:
					row.append(record[f])
				except:
					row.append('')
			writer.writerow(row)
			count_again += 1


	msg += print2('\nRecords %s of %s has been consolidated.'%(count_again,count_all))

	# write the logfile
	with open(new_txt_path, 'w') as logfile:
		logfile.write(msg)

	os.startfile(output_folder)

		
def find_all_csv(folder):
	"""
	finds all csv files within the specified folder. Won't go into subfolders though.
	"""
	import glob

	files = [file for file in glob.glob(folder + "\\*.csv")]
	print('Found the following csv files:')
	for f in files:
		print(f)
	print('Total number of csv files: %s\n'%len(files))
	return files


def print2(msg, msgtype = 'msg'):
	""" print, arcmap AddMessage and return string all in one!"""
	try:
		if msgtype == 'msg':
			arcpy.AddMessage(msg)
		elif msgtype == 'warning':
			arcpy.AddWarning(msg)
	except:
		print(msg)
	return msg + '\n'



if __name__ == '__main__':

	#################   User Inputs   ###################################

	# path to the folder where csv files are stored (csv files in the subfolders will not be consolidated)
	csvfolder = r'C:\Users\KimDan\Government of Ontario\Forest Explorer - Data\E\SOA2\SOA_CC\sqlite\csv'

	# path to the folder where you want the final csv product to be stored (directory must first exist)
	output_folder = r'C:\Users\KimDan\Government of Ontario\Forest Explorer - Data\E\SOA2\SOA_CC\sqlite\csv\consolidated'

	#####################################################################

	csv_list = find_all_csv(csvfolder)
	merge_all_csv(csv_list, output_folder, just_common_fields = True)


