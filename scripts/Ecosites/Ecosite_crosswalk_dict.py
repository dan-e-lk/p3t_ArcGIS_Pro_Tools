# based on Lalonde et all 2012 FEC-ELC-Crosswalk

NER_Ecosites = {
	# Old	# New Best Fit  		# Good Fit							# Poor fit
	'1p':	[['B012'], 				['B034', 'B035'], 					['B024', 'B049', 'B050']],
	'1r':	[['B014','B016'], 		[],									['B037', 'B040', 'B052', 'B055', 'B101', 'B104']],
	'2':	[['B034','B049'],		[],									[]],
	'3':	[['B055'], 				['B040', 'B050'], 					['B035', 'B065', 'B070']],
	'4':	[['B034', 'B049'], 		['B065'], 							['B035', 'B050']],
	'5f':	[['B082', 'B098'], 		['B083', 'B099', 'B114'],			[]],
	'5m':	[['B098', 'B114'], 		['B049', 'B050', 'B065', 'B099'],	[]],
	'6f':	[['B083'], 				['B088', 'B099', 'B104', 'B114', 'B119'],	[]],
	'6m':	[['B104'], 				[], 								['B050', 'B055', 'B065', 'B070', 'B099', 'B114', 'B119']],
	'6c':	[['B040', 'B055'], 		[], 								['B035', 'B050', 'B065', 'B070']],
	'7f':	[['B088'], 				['B085', 'B101', 'B104', 'B116', 'B119'],	[]],
	'7m':	[['B104'], 				['B085', 'B119'], 					['B052', 'B055', 'B067', 'B070', 'B101', 'B116']],
	'7c':	[['B055'], 				['B040', 'B070'], 					['B037', 'B052', 'B067']],
	'8':	[['B222'], 				['B065', 'B114', 'B223'],			[]],
	'9p':	[['B223'], 				['B065', 'B114', 'B224'],			[]],
	'9r':	[['B224'], 				['B066', 'B115', 'B116', 'B223'], 	['B067', 'B130']],
	'10':	[['B130'], 				['B070', 'B071', 'B119', 'B120'], 	['B065', 'B114', 'B223']],
	'11':	[['B127'], 				[], 								['B128']],
	'12':	[['B128'],				['B127'],							[]],
	'13p':	[['B129'],				['B128'],							[]],
	'13r':	[['B129'],				[],									[]],
	'14':	[['B137'],				['B136'],							['B126']],
	'15':	[['B058', 'B107'], 		['B055', 'B104'], 					['B018', 'B042', 'B070', 'B074', 'B119', 'B123']],
	'16':	[['B055', 'B104'], 		['B058', 'B119'], 					['B016', 'B070', 'B107']],
	'17':	[['B058','B107'],		[],									[]],
	'18':	[['B033', 'B048'], 		['B011'], 							['B012', 'B035', 'B050']],
	'19':	[['B039'], 				['B054'], 							['B033', 'B040', 'B048', 'B055']],
	'20':	[['B054', 'B103'], 		['B055', 'B104'], 					['B039', 'B040', 'B069', 'B070', 'B118', 'B119']],
	'21':	[['B054'], 				['B048', 'B055'], 					['B011', 'B015', 'B016', 'B064', 'B069', 'B070', 'B097', 'B103', 'B104']],

}


if __name__ == '__main__':

	for k, v in NER_Ecosites.items():
		print(k,v[0],v[1],v[2])
	print(NER_Ecosites['abc'])