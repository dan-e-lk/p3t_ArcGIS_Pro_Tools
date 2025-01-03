# Caribou habitat classification tool - based on the Boreal Landscape Guide (2014)
# The input inventory must have SFU field with its values matching the SFU column in habitat_classification.csv saved in the same folder as this script.

import arcpy
import os, csv


def chc(inputfc, include_summary):
	
	# loading habitat_classification.csv to memory
	tbl_chc = 'habitat_classification.csv'
	parent_folder = os.path.split(__file__)[0]
	chc_sqls = list(csv.DictReader(open(os.path.join(parent_folder,tbl_chc))))
	logger.print2("\nhabitat_classification.csv:")
	logger.print2(chc_sqls)
	# eg. [{'BLG REGIONAL FU': 'BFDOM', 'SFU': 'BFPUR', 'REGION': 'NWR', 'WINTER USABLE': '', 'WINTER PREFERRED': '', 'REFUGE': '61', 'WINTER SUITABLE': '', 'MATURE CONIFER': ''},...]

	# check if SFU field exists
	existingFields = [str(f.name).upper() for f in arcpy.ListFields(inputfc)]
	if 'SFU' not in existingFields or 'AGE' not in existingFields:
		logger.print2("SFU and/or AGE field not found!",'w')
		raise

	# summarize inputfc
	if include_summary:
		logger.print2("\nSummarizing the input fc...")
		tot_count=0
		tot_area_ha=0
		SFU_area = {} # {'SB1': 23441.31, 'BW1': 34423.22 }
		with arcpy.da.SearchCursor(inputfc, ["SFU","SHAPE@"], where_clause="SFU IS NOT NULL AND SFU NOT IN ('','-')") as cursor:
			for row in cursor:
				sfu = row[0]
				tot_count += 1
				area_ha = row[-1].getArea(method="GEODESIC", units="HECTARES")
				tot_area_ha += area_ha
				try:
					SFU_area[sfu] += area_ha
				except:
					SFU_area[sfu] = area_ha

		logger.print2("\nInput fc Total Count where SFU values present:\n%s"%tot_count)
		logger.print2("\nInput fc Total Area where SFU values present (ha):\n%s"%round(tot_area_ha,2))
		logger.print2("\nSFU, Area(ha)")
		for sfu, area in SFU_area.items():
			logger.print2("%s, %s"%(sfu,round(area,2)))


	# creating a new field
	fname_CHC = "CARIB_HAB_CLS"
	logger.print2("\n\nCreating a new field called %s..."%fname_CHC)
	arcpy.management.AddField(inputfc, fname_CHC, "TEXT", field_length = 30)

	# calculate field
	categories = ['REFUGE','WINTER USABLE','WINTER PREFERRED','WINTER SUITABLE', 'MATURE CONIFER'] # must be in this order
	for sfu_criteria in chc_sqls:
		this_sfu = sfu_criteria['SFU'] # eg. 'BFPUR'
		logger.print2("\nWorking on %s..."%this_sfu)
		for cat in categories:
			if sfu_criteria[cat] != '':
				min_age = int(sfu_criteria[cat])
				this_sql = "SFU='%s' and AGE >= %s"%(this_sfu,min_age)
				logger.print2("\tApplying %s SQL: %s"%(cat, this_sql))
				arcpy.MakeFeatureLayer_management(inputfc, "lyr", where_clause = this_sql)
				selection_count = int(arcpy.management.GetCount("lyr")[0]) # arcpy's GetCount returns string instead of number. That's just Genius.
				if selection_count > 0:
					logger.print2("\t\t%s records found. Calculating field..."%selection_count)
					arcpy.management.CalculateField("lyr", fname_CHC, "'%s'"%cat)
				else:
					logger.print2("\t\t0 record found. Moving on.")


	# summarize resulting values
	if include_summary:
		logger.print2("\n\nSummarizing the result...")
		chc_area = {} # {'REFUGE': 23441.31, 'WINTER USABLE': 34423.22... }
		with arcpy.da.SearchCursor(inputfc, [fname_CHC,"SHAPE@"], where_clause="%s IS NOT NULL"%fname_CHC) as cursor:
			for row in cursor:
				chc = row[0]
				tot_count += 1
				area_ha = row[-1].getArea(method="GEODESIC", units="HECTARES")
				tot_area_ha += area_ha
				try:
					chc_area[chc] += area_ha
				except:
					chc_area[chc] = area_ha

		chc_area_tot = sum(chc_area.values())
		logger.print2("\nTotal Area where habitat cateory values populated (ha):\n%s"%round(chc_area_tot,2))
		logger.print2("\nArea where habitat category values are populated vs area where SFU is populated:\n%s%%"%round(chc_area_tot*100/tot_area_ha,2))
		logger.print2("\nCaribou Habitat, Area(ha)")
		for chc, area in chc_area.items():
			logger.print2("%s, %s"%(chc,round(area,2)))



if __name__ == '__main__':
	
	# gather inputs
	inputfc = arcpy.GetParameterAsText(0) # must have 'SFU' field. The tool modifies the input by adding a new field.
	include_summary = arcpy.GetParameterAsText(1) # 'true' or 'false'
	include_summary = True if include_summary == 'true' else False

	######### logfile stuff

	tool_shortname = 'CaribouHab' # the output logfile will include this text in its filename.

	# importing libraries (only works if arclog.py file is located on the parent folder of this script)
	from datetime import datetime
	parent_d = os.path.split(os.path.split(__file__)[0])[0]
	sys.path.append(parent_d)
	from arclog import Print2 as p2

	# find full path where the logfile will be written
	folder_path = arcpy.Describe(inputfc).path
	while arcpy.Describe(folder_path).dataType != 'Folder':
		folder_path = os.path.split(folder_path)[0]
	outfile = os.path.split(inputfc)[1] + '_' + tool_shortname + '-LOG_' + datetime.now().strftime('%Y%m%d_%H%M') + '.txt'
	logfile_path = os.path.join(folder_path,outfile)

	# importing arclog in the parent directory
	logger = p2(logfile_path)

	##########

	# run the main function
	chc(inputfc, include_summary)

	# finish writing the logfile
	logger.log_close()