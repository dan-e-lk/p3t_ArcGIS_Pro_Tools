
IMPORTANT NOTE: if you are using the tool on BMIs that uses the new tech spec, you must first delete all the overstorey fields before running the tool.
This is because OLT only looks at overstorey fields (i.e. OHT) and completely ignores management fields. (i.e. HT)  So we have to ‘trick’ the OLT by populating overstorey fields with management fields.
The new OLT coming out in 2019 will use the management fields so this tool won’t be needed then.


The tool’s been constantly changing so I couldn’t keep up with the description, but here’s one:

The tool will create a temporary blank feature class with the following fields:

['POLYID',		25,			'TEXT'],
['POLYTYPE',	3,			'TEXT'],
['OWNER',		1,			'TEXT'],
['DEVSTAGE',	8,			'TEXT'],
['YRDEP',		4,			'SHORT'],
['OYRORG',		4,			'SHORT'],				
['OSPCOMP',		120,		'TEXT'],
['OLEADSPC',	3,			'TEXT'],
['OAGE',		3,			'SHORT'],
['OHT',			4,			'FLOAT'],
['OCCLO',		3,			'SHORT'],
['OSC',			1,			'SHORT'],
['UYRORG',		4,			'SHORT'],
['USPCOMP',		120,		'TEXT'],
['ULEADSPC',	3,			'TEXT'],
['UAGE',		3,			'SHORT'],
['UHT',			4,			'FLOAT'],
['UCCLO',		3,			'SHORT'],
['USTKG',		4,			'FLOAT'],
['USC',			1,			'SHORT'],
['INCIDSPC',	3,			'TEXT'],
['VERT',		2,			'TEXT'],
['HORIZ',		2,			'TEXT'],
['PRI_ECO',		13,			'TEXT'],
['SEC_ECO',		13,			'TEXT'],
['STKG',		4,			'FLOAT'],
['PLANFU',		15,			'TEXT'],	
['AU',			15,			'TEXT'],

Then, the tool will append the input BMI to this temporary feature class. For example, the values from INCIDSPC from the original bmi will be transferred to INCIDSPC in this temporary feature class.

If the tool cannot find the same fieldname to transfer data, it will look for an alternative field and will try to bring the data from alternative field to the field in the temporary feature class.
For example, if your original bmi doesn’t have OAGE, it will look for AGE field and will transfer the values from AGE to the OAGE field in the temporary feature class.
Below is how the tool maps those alternative fields:

 field  |   		alternative fields
'OYRORG':		['YRORG'],
'OSPCOMP':		['SPCOMP'],
'OLEADSPC':		['LEADSPC'],   # used to be ['WG']
'OAGE':			['AGE'],
'OHT':			['HT'],
'OCCLO':		['CCLO'],
'OSC':			['SC'],

Finally the tool will export the temporary feature class to a shapefile – that’s your output of the tool.

IMPORTANT NOTE: if you are using the tool on BMIs that uses the new tech spec, you must first delete all the overstorey fields before running the tool.
This is because OLT only looks at overstorey fields (i.e. OHT) and completely ignores management fields. (i.e. HT)  So we have to ‘trick’ the OLT by populating overstorey fields with management fields.
The new OLT coming out in 2019 will use the management fields so this tool won’t be needed then.
