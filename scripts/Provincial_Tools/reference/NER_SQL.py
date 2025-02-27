NER_Boreal_v9_ROD2023 = {
# on Apr 2023, updates have been made to PW1 and LH1
# This SQL will use Ecosite whether you check the "Use Ecosite" checkbox or not on the ArcMap's user interface.
# Another change is that we added MWD (Balsam Fir leading Mixedwood) and changed STKG to OSTKG (if we have OSTKG then it can be replaced with STKG through the user interface)
# fields required: POLYTYPE, STKG (or OSTKG) Ecosite_GeoRangeAndNumber and either OSC or SC

#   |Order   |SFU        |SQL                   |SQL addition if Ecosite incorporated               | SFU Descriptive Name

    1:  ['PR1',     """ ("PR" >= 70) AND <USER_DEFINED_SFU_FIELD_NAME> IS NULL """,            "",            """ RED PINE, PLANTATIONS """],
    2:  ['PW1',     """ ("PW" + "PR" + "HE" + ("SW" + "SX") >= 40 AND "PW" >= 30) AND <USER_DEFINED_SFU_FIELD_NAME> IS NULL """,           "",            """WHITE PINE, SHELTERWOOD"""],
    3:  ['PRW',     """ (("PW" + "PR" + "HE" + ("SW" + "SX") >= 40) AND ("PW" + "PR" >= 30)) AND <USER_DEFINED_SFU_FIELD_NAME> IS NULL """,         "",            """RED AND WHITE PINE"""],

    #  NOTE THAT IN LH1 THE ECOSITE IS NO LONGER IN ITS OWN ELEMENT OF THE DICTIONARY. IT IS WITHING THE PRIMARY SQL ELEMENT. THIS HASN'T BEEN DONE BEFORE. IT IS NOT EXPLICIT THAT ECOSITE IS REQUIRED FOR THIS SQL SET ELSEXHERE IN THE SCRIPT (2019-08-28)
    4:  ['LH1',     """ ("AB" + "EX" + "_BY" >= 20 AND ("ECOSITE_GEORANGEANDNUMBER" IN ('B119', 'B120', 'B123', 'B129', 'B130', 'B131', 'B133', 'G119', 'G120', 'G123', 'G129', 'G130', 'G131', 'G133'))) OR ("PB" >= 70) AND <USER_DEFINED_SFU_FIELD_NAME> IS NULL """,          "",            """LOWLAND HARDWOOD"""],

    5:  ['TH1',     """ (("AB" + "EX") + "MH" + ("_BY" + "MR") + "HE" >= 30) AND <USER_DEFINED_SFU_FIELD_NAME> IS NULL """,          "",             """TOLERANT HARDWOODS"""],

    # NOTE THAT IN SBOG THE ECOSITE IS NO LONGER IN ITS OWN ELEMENT OF THE DICTIONARY. IT IS WITHIN THE PRIMARY SQL ELEMENT. THIS HASN'T BEEN DONE BEFORE. IT IS NOT EXPLICIT THAT ECOSITE IS REQUIRED FOR THIS SQL SET ELSEWHERE IN THE SCRIPT (2019-08-23)
    6:  ['SBOG',    """ (("SB" + "LA" + ("CE" + "CW") >= 70) AND ((("OSC" = 4) AND ("ECOSITE_GEORANGEANDNUMBER" IN ('B126', 'B136','B137',  'G126', 'G136', 'G137'))))) AND <USER_DEFINED_SFU_FIELD_NAME> IS NULL """,            "",             """BLACK SPRUCE, BOG"""],

    # NOTE THAT SB1 AB (BLACK ASH) IS NOW LESS THAN 10%, AND ECOSITE 126 IS NO LONGER AN ELIGIBLE ECOSITE.
    # ADDED 129 AND 224 ECOSITES TO PUT EMPHASIS ON THE SPECIES COMPOSITION AND SITE CLASS, WHEN SITE ARE >80%SB AND NOT SC=4. 
    #  PREVENTING STANDS FROM BECOMING LC1. MORE CONFIDENT THE SITE IS LOWLAND AND BLACK SPRUCE, BUT THE ECOSITE CLASSIFICATION WAS NOT CORRECT. 
    #  THIS DECISION REFLECTS THE IMPORTANCE-CONFIDENCE OF SPECIES IN THE FOREST UNIT CLASSIFICATION.
    7:  ['SB1',     """ ((("SB" >= 80)) AND ("AB" <= 10)  AND "ECOSITE_GEORANGEANDNUMBER" IN ('B127', 'B128', 'B129', 'B222', 'B223', 'B224', 'G127', 'G128', 'G129', 'G222', 'G223', 'G224')) AND <USER_DEFINED_SFU_FIELD_NAME> IS NULL """,          "",             """BLACK SPRUCE, LOWLAND"""],

    8:  ['PJ1',     """ (( ( "PJ" >= 70 AND "PO" + "PT" + "BW" + "_BY" + "MR" + "MH" + "AB" + "EX" + "PB" <= 20 ) AND "ECOSITE_GEORANGEANDNUMBER" IN ('B012', 'B033', 'B034', 'B035', 'B048', 'B049', 'B050', 'G012', 'G033', 'G034', 'G035',  'G048', 'G049', 'G050')) OR ("PJ" >= 90)) AND <USER_DEFINED_SFU_FIELD_NAME> IS NULL """,          "",             """JACK PINE, PURE"""],
    9:  ['LC1',     """ ((("CE" + "CW") + "LA" + "SB" + "BF" + "SW">= 70) AND ("ECOSITE_GEORANGEANDNUMBER" IN ('B127', 'B128', 'B129', 'B222', 'B223', 'B224', 'B136', 'B137', 'G127', 'G128', 'G129', 'G222', 'G223', 'G224', 'G136', 'G137'))) AND <USER_DEFINED_SFU_FIELD_NAME> IS NULL """,           "",            """LOWLAND CONIFER"""],
    
    # CHANGED PJ >= 50 TO PJ >=30 (2019-12-05). SEE MON-P
    10: ['PJ2',     """ ((("PJ" + "SB" + "PR" + "PW" >= 70) OR ("PJ" >= 30 AND "PJ" + "SB" + "BF" + ("SW" + "SX") + "PW" + "PR" + ("CE" + "CW") + "LA" >=70)) AND (("PJ" + "PW" + "PR") >= ("SB" + ("SW" + "SX") + ("CE" + "CW")))) AND <USER_DEFINED_SFU_FIELD_NAME> IS NULL """,           "",             """JACK PINE BLACK SPRUCE"""],
    11: ['SP1',     """ (("SB" + ("SW" + "SX") + "BF" + ("CE" + "CW") + "LA" + "PW" + "PJ" + "PR" + "HE">=70) AND (("BF" + ("CE" + "CW") + "PW" + ("SW" + "SX") + "HE" <= 20) OR ("PJ" + "PR" + "LA" >= 30)))  AND <USER_DEFINED_SFU_FIELD_NAME> IS NULL """,           "",            """SPRUCE, UPLAND"""],
    12: ['SF1',     """ ("SB" + ("SW" + "SX") + "BF" + ("CE" + "CW") + "LA" + "PW" + "PJ" + "PR" >= 70) AND <USER_DEFINED_SFU_FIELD_NAME> IS NULL """,          ""],
    13: ['PO1',     """ ((("PO" + "PT" + "PL") + "BW" + "MH" + ("_BY" + "MR") + ("AB" + "EX" + "PB") >= 70) AND (("PO" + "PT" + "PL" + "PB") >= 50)) AND <USER_DEFINED_SFU_FIELD_NAME> IS NULL """,          "",            """POPLAR"""],
    14: ['BW1',     """ (("PO" + "PT" + "PL") + "BW" + "MH" + ("_BY" + "MR") + ("AB" + "EX" + "PB") >= 70) AND <USER_DEFINED_SFU_FIELD_NAME> IS NULL """,          "",            """WHITE BIRCH"""],
    15: ['MH1',     """ (((("BF" <= 20 AND ("SW" + "SX") <= 20 AND ("CE" + "CW") <= 20) AND ("PO" + "PT" + "PL") + "BW" + "MH" + ("_BY" + "MR") + ("AB" + "EX" + "PB") >= 50) AND ("PJ" + "PR" <= 50 AND "PJ" + "PR" >= 20)) AND ("ECOSITE_GEORANGEANDNUMBER" IN ('B016', 'B019', 'B028', 'B040', 'B043', 'B055', 'B059', 'B070', 'B076',  'G016', 'G019', 'G028', 'G040', 'G043', 'G055', 'G059', 'G070', 'G076'))) AND <USER_DEFINED_SFU_FIELD_NAME> IS NULL """,           "",            """MIXEDWOOD HARDWOOD FRESH COARSE"""],
    16: ['MC1',     """ ((("BF" <= 20 AND ("SW" + "SX") <= 20 AND ("CE" + "CW") <= 20 AND ("PJ" + "PR" + "LA") >= 20) AND ("ECOSITE_GEORANGEANDNUMBER" IN ('B012', 'B014', 'B035', 'B037', 'B038', 'B050', 'B052', 'B053', 'B065', 'B067', 'B068',  'G012', 'G014', 'G035', 'G037', 'G037', 'G050', 'G052', 'G053', 'G065', 'G067', 'G068')))  OR ("PJ" + "PR" >= 50)) AND <USER_DEFINED_SFU_FIELD_NAME> IS NULL """,           "",             """MIXEDWOOD CONIFER FRESH COARSE"""],
    17: ['MH2',     """ (("PO" + "PT" + "PL") + "BW" + "MH" + ("_BY" + "MR") + ("AB" + "EX" + "PB") >= 50) AND <USER_DEFINED_SFU_FIELD_NAME> IS NULL """,          "",            """MIXEDWOOD HARDWOOD MOIST FINE"""],
    18: ['MC2',     """ ("SB" + ("SW" + "SX") + "BF" + ("CE" + "CW") + "LA" + "PW" + "PJ" + "PR" > 50) AND <USER_DEFINED_SFU_FIELD_NAME> IS NULL """,          "",            """MIXEDWOOD CONIFER MOIST FINE"""],
    
    # this is unnecessary - we don't want UDF
    # 19: ['UDF',     """ ("POLYTYPE" = 'FOR') AND <USER_DEFINED_SFU_FIELD_NAME> IS NULL """,            "",            """UNDEFINED"""],

    # not using 22 to 29
    # 22: ['SB1',     """ ("POLYTYPE" = 'FOR' AND <USER_DEFINED_SFU_FIELD_NAME> IS NULL) """,            """OR (<USER_DEFINED_SFU_FIELD_NAME> = 'SP1' AND "ECOSITE_GEORANGEANDNUMBER" IN ('B126', 'B127', 'B128', 'B129', 'B136', 'B222', 'B223', 'B224'))"""], # THE REASON WHY I INCLUDED THE SEEMINGLY UNNECESSARY FIRST PART OF THE SQL IS BECAUSE THE TOOL HAS AN OPTION TO NOT USE ECOSITE. IF THE USER DECIDES NOT TO USE ECOSITE, ONLY THE FIRST PART OF THE SQL WILL BE USED AND IT WILL BASICALLY SELECT NOTHING.
    # 23: ['LC1',     """ ("POLYTYPE" = 'FOR' AND <USER_DEFINED_SFU_FIELD_NAME> IS NULL) """,            """OR (<USER_DEFINED_SFU_FIELD_NAME> = 'SF1' AND "ECOSITE_GEORANGEANDNUMBER" IN ('B126', 'B127', 'B128', 'B129', 'B136', 'B222', 'B223', 'B224'))"""],
    # 24: ['LH1',     """ (<USER_DEFINED_SFU_FIELD_NAME> IN ('TH1','PO1','BW1','MH1','MH2') AND "ECOSITE_GEORANGEANDNUMBER" IN ('B130','B131')) """,           ""],

    # 28: ['SP1',    """ (<USER_DEFINED_SFU_FIELD_NAME> = 'SB1' AND "DEVSTAGE" IN('NEXPLANT','ESTPLANT')) """,            ""],
    # 29: ['SP1',    """ (<USER_DEFINED_SFU_FIELD_NAME> = 'SF1' AND "DEVSTAGE" IN('NEXPLANT','ESTPLANT') AND ("BF" + "LA" <=20)) """,            ""],
    
    # adding this to catch all:
    41: ['MH2',     """ <user_defined_sfu_field_name> IS NULL AND ("Po" + "Pt" + "Pl") + "Bw" + ("Mh" + "Ms" + "Mr") + "_By" + ("Ab" + "Ew" + "Pb") + "OH" > "Sb" + ("Sw" + "Sx") + "Bf" + ("Ce" + "Cw") + "La" + "Pw" + "Pj" + "Pr" + "OC" """,            ""],
    42: ['MC2',     """ <user_defined_sfu_field_name> IS NULL """,            ""],
}


