# based on Lalonde et all 2012 FEC-ELC-Crosswalk

NER_Ecosites = {
	# Old	# New		# Notes							
	'1p':	['',		'NoEcosite, PJ2'],
	'1r':	['B016',	'B016, MC1'],
	'2':	['',		'NoEcosite, MH1'],
	'3':	['B055',	'B055, MH1'],
	'4':	['',		'NoEcosite, PJ2'],
	'5f':	['',		'NoEcosite, SP1'],
	'5m':	['',		'NoEcosite, MC2'],
	'6f':	['',		'NoEcosite, MH2'],
	'6m':	['',		'NoEcosite, MH2'],
	'6c':	['B040',	'B040, MH1'],
	'7f':	['',		'NoEcosite, MH2'],
	'7m':	['',		'NoEcosite, MH2'],
	'7c':	['B055',	'B055, MH1'],
	'8':	['B065',	'B065, SP1 transitional site type w some characteristics of SB1'],
	'9p':	['B065',	'B065, SP1 transitional site type w some characteristics of SB1'],
	'9r':	['B115',	'B115, SP1 transitional site type w some characteristics of SB1'],
	'10':	['',		'NoEcosite, MH2'],
	'11':	['B127',	'B127, SB1'],
	'12':	['B128',	'B128, SB1'],
	'13p':	['B129',	'B129, either SB1 or LC1'],
	'13r':	['B129',	'B129, likely LC1'],
	'14':	['B137',	'B137, BOG'],
	'15':	['',		'NoEcosite, likely TH1 - MR leading'],
	'16':	['',		'NoEcosite, likely TH1 - BY leading'],
	'17':	['',		'NoEcosite, likely TH1 - MH leading'],
	'18':	['',		'NoEcosite, likely PRW'],
	'19':	['',		'NoEcosite, likely PRW or PW1'],
	'20':	['B055',	'B055, likely PRW or MH1'],
	'21':	['B055',	'B055, likely PRW or MC1']
}


if __name__ == '__main__':

	for k, v in NER_Ecosites.items():
		print(k,v[0],v[1])
	print(NER_Ecosites['abc'])