# This script is a direct conversion of Larry's VolCalcPlonski.accdb to python.
# I didn't change any of the coefficients, so the result should be identical to that of Larry's.
# The script only works if the input data has all of the fields that PIAM has.
# The original SQL goes like this:
"""
SELECT 
tbl_plonski_metrics.METRIC, forest.POLYID, forest.HA, forest.HT, forest.STKG, forest.SC, tbl_ac.AC_5, forest.PLANFU, forest.PFT, 
([tbl_plonski_metrics].[Pw]*([forest].[Pw]/100)*[STKG]) AS M_Pw, ([tbl_plonski_metrics].[PR]*([forest].[PR]/100)*[STKG]) AS M_PR, 
([tbl_plonski_metrics].[PJ]*([forest].[PJ]/100)*[STKG]) AS M_PJ, ([tbl_plonski_metrics].[SB]*([forest].[SB]/100)*[STKG]) AS M_SB, 
([tbl_plonski_metrics].[SW]*([forest].[SW]/100)*[STKG]) AS M_SW, ([tbl_plonski_metrics].[BF]*([forest].[BF]/100)*[STKG]) AS M_BF, 
([tbl_plonski_metrics].[CE]*([forest].[CE]/100)*[STKG]) AS M_CE, ([tbl_plonski_metrics].[LA]*([forest].[LA]/100)*[STKG]) AS M_LA, 
([tbl_plonski_metrics].[HE]*([forest].[HE]/100)*[STKG]) AS M_HE, ([tbl_plonski_metrics].[CE]*([forest].[OC]/100)*[STKG]) AS M_OC, 
([tbl_plonski_metrics].[PO]*([forest].[PO]/100)*[STKG]) AS M_PO, ([tbl_plonski_metrics].[PO]*([forest].[PB]/100)*[STKG]) AS M_PB, 
([tbl_plonski_metrics].[BW]*([forest].[BW]/100)*[STKG]) AS M_BW, ([tbl_plonski_metrics].[OH]*([forest].[YB]/100)*[STKG]) AS M_YB, 
([tbl_plonski_metrics].[MH]*([forest].[MH]/100)*[STKG]) AS M_MH, ([tbl_plonski_metrics].[OH]*([forest].[MR]/100)*[STKG]) AS M_MR, 
([tbl_plonski_metrics].[OH]*(([AB]+[AW])/100)*[STKG]) AS M_AX, ([tbl_plonski_metrics].[OH]*([forest].[BD]/100)*[STKG]) AS M_BD, 
([tbl_plonski_metrics].[OH]*([forest].[BE]/100)*[STKG]) AS M_BE, ([tbl_plonski_metrics].[OH]*(([QR]+[OB]+[OW])/100)*[STKG]) AS M_QR, 
([tbl_plonski_metrics].[OH]*(([forest].[OH]+[CH]+[EX]+[IW])/100)*[STKG]) AS M_OH
FROM (forest INNER JOIN tbl_ac ON forest.AGE = tbl_ac.AGE) 
INNER JOIN tbl_plonski_metrics ON (forest.SC = tbl_plonski_metrics.SC) AND (tbl_ac.AC_5 = tbl_plonski_metrics.AC_5)
WHERE (((tbl_plonski_metrics.METRIC)='GTV') AND ((forest.POLYTYPE)='FOR'));
"""
# note that above SQL is just for your information.  It's not actually being used in this script.



import arcpy
import os, csv
import pandas as pd

man_fields=['POLYTYPE','STKG','SC','AGE', 'PW','PR','PJ','SB','SW','BF','CE','LA','HE','OC','OH','PO','PB','BW','YB','MH','MR','AB','AW','BD','BE','QR','OB','OW','CH','EX','IW']

def plonski(inputfc, metrics, add_extra_field):
	
	# loading csv files to memory
	logger.print2("Here are mandatory fields your inventory must have in order for this tool to run properly:\n%s\n"%man_fields)
	logger.print2("loading csv files...")
	tbl_ac = 'tbl_ac.csv'
	parent_folder = os.path.split(__file__)[0]
	l_tbl_ac = list(csv.DictReader(open(os.path.join(parent_folder,tbl_ac))))

	tbl_plonski = 'tbl_plonski_metrics.csv'
	df = pd.read_csv(tbl_plonski)

	# check fields / rec count
	existingFields = [str(f.name).upper() for f in arcpy.ListFields(inputfc)]
	for f in man_fields:
		if f not in existingFields:
			logger.print2("!!!! Missing field: %s"%f,'w')
			raise Exception("!!!! Missing field: %s"%f)
	count_orig = int(arcpy.management.GetCount(inputfc)[0])
	logger.print2("input fc record count: %s"%count_orig)

	# get oid field
	oid_fieldname = arcpy.Describe(inputfc).OIDFieldName
	useful_fields = [oid_fieldname] + man_fields # this will include existing field plus new fields
	man_fields.append(oid_fieldname) # only includes existing mandatory fields

	# adding AC_5 field if not exist
	new_fname = 'AC_5'
	logger.print2("Adding a new field: %s"%new_fname)
	if new_fname not in existingFields:
		arcpy.AddField_management(in_table = inputfc, field_name = new_fname, field_type = "SHORT")
	else:
		logger.print2("\t%s already exists"%new_fname)
	useful_fields.append(new_fname)

	# calculate AC_5 using the tbl_ac.csv
	f = ['POLYTYPE','AGE','AC_5']
	logger.print2("Populating AC_5 (age class by 5 years) field...\n")
	with arcpy.da.UpdateCursor(inputfc, f, "POLYTYPE='FOR'") as cursor:
		for row in cursor:
			age = row[1]
			if age == None: age = 0
			if age > 250: age = 250
			for i in l_tbl_ac:
				if int(i['AGE']) == age:
					ac_5 = int(i['AC_5'])
					break
			row[2] = ac_5
			cursor.updateRow(row)


	# adding metric fields
	prefix = 'PLONSKI_'
	for metric in metrics:
		new_fname = prefix+metric # 'PLONSK_GTV'
		logger.print2("Adding a new field: %s"%new_fname)
		if new_fname not in existingFields:
			arcpy.AddField_management(in_table = inputfc, field_name = new_fname, field_type = "FLOAT")
		else:
			logger.print2("\t%s already exists"%new_fname)
		useful_fields.append(new_fname)

		if add_extra_field: # these fields includes extra information and will be useful when checking each metrics
			extra_fname = new_fname + '_EXTRA'
			if extra_fname not in existingFields:
				logger.print2("Adding a new field: %s"%extra_fname)
				arcpy.AddField_management(in_table = inputfc, field_name = extra_fname, field_type = "TEXT", field_length = "800")
			useful_fields.append(extra_fname)


	# turn the plonski metrics table into pandas dataframe before working on the next part


	# calculate metrics
	f = useful_fields # man fields plus new fields
	error_count = 0
	spc_metrics = {'M_'+i:0 for i in ['PW','PR','PJ','SB','SW','BF','CE','LA','HE','OC','PO','PB','BW','YB','MH','MR','AX','BD','BE','QR','OH']} # metric (eg. GTV) for each species group
	for metric in metrics:
		logger.print2("\nCalculating and populating %s for all records..."%metric)
		metric_fname = 'PLONSKI_'+metric
		if add_extra_field:
			extra_metric_fname = metric_fname + '_EXTRA'
		with arcpy.da.UpdateCursor(inputfc, f, "POLYTYPE='FOR'") as cursor:
			for row in cursor:
				oid = row[0]
				ac_5 = row[f.index('AC_5')]
				sc = row[f.index('SC')]
				stkg = row[f.index('STKG')]

				m = spc_metrics.copy()
				coef = df[(df.METRIC == metric)&(df.AC_5==ac_5)&(df.SC==sc)] # this is the record in plonski table that matches with current record's AGE and SC
				m['M_PW'] = coef.Pw.values[0]*row[f.index('PW')]*stkg/100
				m['M_PR'] = coef.Pr.values[0]*row[f.index('PR')]*stkg/100
				m['M_PJ'] = coef.Pj.values[0]*row[f.index('PJ')]*stkg/100
				m['M_SB'] = coef.Sb.values[0]*row[f.index('SB')]*stkg/100
				m['M_SW'] = coef.Sw.values[0]*row[f.index('SW')]*stkg/100
				m['M_BF'] = coef.Bf.values[0]*row[f.index('BF')]*stkg/100
				m['M_CE'] = coef.Ce.values[0]*row[f.index('CE')]*stkg/100
				m['M_LA'] = coef.La.values[0]*row[f.index('LA')]*stkg/100
				m['M_HE'] = coef.He.values[0]*row[f.index('HE')]*stkg/100
				m['M_CE'] = coef.Ce.values[0]*row[f.index('CE')]*stkg/100
				m['M_OC'] = coef.Ce.values[0]*row[f.index('OC')]*stkg/100
				m['M_PO'] = coef.Po.values[0]*row[f.index('PO')]*stkg/100
				m['M_PB'] = coef.Po.values[0]*row[f.index('PB')]*stkg/100
				m['M_BW'] = coef.Bw.values[0]*row[f.index('BW')]*stkg/100
				m['M_YB'] = coef.OH.values[0]*row[f.index('YB')]*stkg/100
				m['M_MH'] = coef.Mh.values[0]*row[f.index('MH')]*stkg/100
				m['M_MR'] = coef.OH.values[0]*row[f.index('MR')]*stkg/100
				AB = row[f.index('AB')]
				AW = row[f.index('AW')]
				m['M_AX'] = coef.OH.values[0]*(AB+AW)*stkg/100
				m['M_BD'] = coef.OH.values[0]*row[f.index('BD')]*stkg/100
				m['M_BE'] = coef.OH.values[0]*row[f.index('BE')]*stkg/100
				QR = row[f.index('QR')]
				OB = row[f.index('OB')]
				OW = row[f.index('OW')]
				m['M_QR'] = coef.OH.values[0]*(QR+OB+OW)*stkg/100
				OH = row[f.index('OH')]
				CH = row[f.index('CH')]
				EX = row[f.index('EX')]
				IW = row[f.index('IW')]
				m['M_OH'] = coef.OH.values[0]*(OH+CH+EX+IW)*stkg/100

				metric_value = sum(m.values())
				row[f.index(metric_fname)] = metric_value

				if add_extra_field:
					row[f.index(extra_metric_fname)] = str(m)

				cursor.updateRow(row)




if __name__ == '__main__':
	
	# gather inputs
	inputfc = arcpy.GetParameterAsText(0)
	metrics = arcpy.GetParameterAsText(1) # can pick multiple from 'BA','GTV','MAI','NMV','STEMS','DBH','CAI'. eg. GTV;BA;STEMS
	debug = arcpy.GetParameterAsText(2) # true or false

	metrics = list(set(metrics.split(';'))) # eg. ['BA','GTV',NMV']
	add_extra_field = True if debug == 'true' else False

	######### logfile stuff

	tool_shortname = 'Plonski2PIAM' # the output logfile will include this text in its filename.

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

	logger.print2("Input Parameters:\n%s\n%s\n%s\n\n"%(inputfc,metrics,add_extra_field))
	# run the main function(s)
	plonski(inputfc, metrics, add_extra_field)

	# finish writing the logfile
	logger.log_close()