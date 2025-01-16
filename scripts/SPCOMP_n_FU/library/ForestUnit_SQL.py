#-------------------------------------------------------------------------------
# Name:        Forest Unit SQL
#
# Author:      kimdan
#
# Created:     03/11/2017
# Note:
#   This script contains SQL queries for populating standard forest units.
#   Note that the original sql has been altered in several ways:
#       1. Or and By has been replaced with _Or and _By
#       2. Ecosite has been replaced with Ecosite1.
#       3. wild card - % - has been added for ecosite sqls
#
#   Document used for these sqls are saved here:
#   \\lrcpsoprfp00001\MNR_NER\GI_MGMT\Tools\Scripts\FMPTools_2017\Landbase_SFU_Checker\Documents\FU
#
# Changes Documentation:
#   2018-01-22  littleto    Add additional options for forest unit criteria suites:
#                               - NER_Boreal_SFU_TN021
#                               - NER_Boreal_New_Revised_Regional_SFU
#
#                           *** Note:   To make available in ArcGIS Toolbox, you need to add
#                                       you need to add the Populate_ForestUnit.py typeLookup Dict key
#                                       to the forest unit type list is the toolbox properties.
#   2018-01-22  littleto    Add the replace string to incorperate "<user_defined_sfu_field_name>" for "Is
#                               Not Null" type interpretations in SQL criteria suite
#   2018-01-23  littleto    Elaborte on script comments throughout.
#
#   2022-10-19  littleto    Daniel and I have been using git for several years
#                               now, and the above comments can be cleaned up
#                               after the next commit.
#-------------------------------------------------------------------------------

# *** Ground rules when altering the SQLs below: ***
# 1. Use OSC for site class, OSTKG for stocking, and AGE for age. The end user will have an option to replace the OSC with SC.
# 2. If you add a whole new dictionary, you need to also change the Populate_ForestUnit's typeLookup dictionary (and also add the new option to the user interface)
# 3. Use _Or and _By instead of Or and By.
# 4. Do not change the official original version of SQL statements


# Original version verified by Todd Little (2022-10-19 10:28)
NER_Boreal_SFU_TN021 = {

# This is intended to be the unchanged/uninterpreted SQL criteria of Table 1
# of the NESI Technical Note TN-021.
# This dictionary should be considered immutable.
# Parton, J., S Vasiliauskas, G. Lucking, and W. R. Watt. 2006. Standard Forest
# Units for Northeastern Ontario Boreal Forests. OMNR, Northeast Science and
# Information Unit, NESI Technical Note TN-021. 23 p.

# fields required: POLYTYPE, either OSC or SC, and Age

#   |Order   |SFU        |SQL                   |SQL addition if Ecosite incorporated

    1:  ['PR1',     """ ("Pr" >= 70) And <user_defined_sfu_field_name> Is Null """, ""],
    2:  ['PW1',     """ ("Pw" + "Pr" + "Sw" + "He" >= 40 And "Pw" >= 30) And <user_defined_sfu_field_name> Is Null """, ""],
    3:  ['PRW',     """ ("Pw" + "Pr" >= 40) And <user_defined_sfu_field_name> Is Null """, ""],
    4:  ['LH1',     """ (("Ab" + "Ew" + "Pb") >= 30 Or "Pb" >=30) And <user_defined_sfu_field_name> Is Null """, ""],
    5:  ['TH1',     """ (("Ab" + "Ew" + "Pb") + "Mh" + ("_By" + "Mr") + "He" >= 30) And <user_defined_sfu_field_name> Is Null """, ""],
    6:  ['SBOG',    """ (("Sb" + "La") >= 70 And "Pw"=0 And "OSC" = 4) And <user_defined_sfu_field_name> Is Null """, ""],
    7:  ['SB1',     """ (("Sb" >= 80) And "Mh" + ("_By" + "Mr") + "Pr" = 0 And "Pw" + "Pj" <= 10) And <user_defined_sfu_field_name> Is Null """, ""],
    8:  ['PJ1',     """ (("Pj" >= 70 And "Po" + "Bw" + ("_By" + "Mr") + "Mh" + ("Ab" + "Ew" + "Pb") <= 20) Or ("Pj" >= 50 And ("Pj" + "Sb" + "Bf" + "Sw" + "He" + "Pw" + "Pr" + "Ce" + "La" >= 70) And "Age" >=120)) And <user_defined_sfu_field_name> Is Null """, ""],
    9:  ['LC1',     """ (("Sb" + "Ce" + "La" >= 80) And "Mh" + ("_By" + "Mr") +"Pr" = 0 and "Pw" + "Pj" <= 10) And <user_defined_sfu_field_name> Is Null """, ""],
    10: ['PJ2',     """ (("Pj" + "Sb" + "Pr" >= 70 Or ("Pj" + "Pr" + "Pw" >= 50 And "Pj" + "Sb" + "Bf" + "Sw" + "He" + "Pw" + "Pr" + "Ce" + "La" >=70)) And "Pj" + "Pr" + "Pw" >= "Sb") And <user_defined_sfu_field_name> Is Null """, ""],
    11: ['SP1',     """ ("Sb" + "Sw" + "Bf" + "Ce" + "La" + "Pw" + "Pj" + "Pr" + "He" >=70 And ("Bf" + "Ce" + "Sw" + "He" <= 20 Or "Pj" + "Pr" >= 30)) And <user_defined_sfu_field_name> Is Null """, ""],
    12: ['SF1',     """ ("Sb" + "Sw" + "Bf" + "Ce" + "La" + "Pw" + "Pj" + "Pr" + "He" >= 70) And <user_defined_sfu_field_name> Is Null """, ""],
    13: ['PO1',     """ ("Po" + "Bw" + "Mh" + ("_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 70 And "Po" >= 50) And <user_defined_sfu_field_name> Is Null """, ""],
    14: ['BW1',     """ ("Po" + "Bw" + "Mh" + ("_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 70) And <user_defined_sfu_field_name> Is Null """, ""],
    15: ['MW1',     """ ("Pj" + "Pr" >= 20) And <user_defined_sfu_field_name> Is Null """, ""],
    16: ['MW2',     """ ("POLYTYPE" = 'FOR') And <user_defined_sfu_field_name> Is Null """, ""]

}


# Original version verified by Todd Little (2022-10-19 10:28)
NER_Boreal_SFU = {
# tbl_lut_FU_Boreal_NER_SQLs.xlsx!NER_Boreal_SFUs_TN0xx_170607
#  This is the original Ken Lennon version of the NER Voreal revised SFUs. A version
#  of the criteria promoted by Ken for the Hearst 2017 FMP, White River 2018 FMP,
#  and the Romeo Malette 2019 FMPs, when the Provincial Ecological Land
#  Classification (ELC) ecosites are applied.

# fields required: POLYTYPE, Ecosite_GeoRangeAndNumber and either OSC or SC

#   |Order   |SFU        |SQL                   |SQL addition if Ecosite incorporated

    1:  ['PR1',     """ ("Pr" >= 70) And <user_defined_sfu_field_name> Is Null """,            ""],
    2:  ['PW1',     """ ("Pw" + "Pr" + ("Sw" + "Sx") + "He" >= 40 And "Pw" >= 30) And <user_defined_sfu_field_name> Is Null """,           ""],
    3:  ['PRW',     """ ("Pw" + "Pr" >= 40) And <user_defined_sfu_field_name> Is Null """,         ""],
    4:  ['LH1',     """ ((("Ab" + "Ew" + "Pb") >= 30 Or "Pb" >=40 )) And <user_defined_sfu_field_name> Is Null """,            """AND ("Ecosite_GeoRangeAndNumber" in ('B130', 'B131')) """],
    5:  ['TH1',     """ (("Ab" + "Ew" + "Pb") + "Mh" + ("Pl" + "_By" + "Mr") + "He" >= 30) And <user_defined_sfu_field_name> Is Null """,          ""],
    6:  ['SBOG',    """ (("Sb" + "La" + ("Ce" + "Cw") >= 70) And "OSC" = 4) And <user_defined_sfu_field_name> Is Null """,         """AND ("Ecosite_GeoRangeAndNumber" in ('B126', 'B136', 'B137'))"""],
    7:  ['SB1',     """ (("Sb" >= 70)) And <user_defined_sfu_field_name> Is Null """,          """AND "Ecosite_GeoRangeAndNumber" in ('B126', 'B127', 'B128', 'B129', 'B222', 'B223', 'B224')"""],
    8:  ['PJ1',     """ (("Pj" >= 70)) And <user_defined_sfu_field_name> Is Null """,          """AND "Ecosite_GeoRangeAndNumber" in ('B012', 'B034', 'B035', 'B049', 'B050')"""],
    9:  ['LC1',     """ ((("Ce" + "Cw") + "La" + "Sb" >= 70)) And <user_defined_sfu_field_name> Is Null """,           """AND ("Ecosite_GeoRangeAndNumber" in ('B127', 'B128', 'B129', 'B222', 'B223', 'B224'))"""],
    10: ['PJ2',     """ (("Pj" + "Sb" + "Pr" >= 70 Or ("Pj" >= 50 And "Pj" + "Sb" + "Bf" + ("Sw" + "Sx") + "He" + "Pw" + "Pr" + ("Ce" + "Cw") + "La" >=70)) And "Pj" >= "Sb") And <user_defined_sfu_field_name> Is Null """,           ""],
    11: ['SP1',     """ ("Sb" + ("Sw" + "Sx") + "Bf" + ("Ce" + "Cw") + "La" + "Pw" + "Pj" + "Pr" + "He" >=70 And ("Bf" + ("Ce" + "Cw") + "Pw" + "La" + ("Sw" + "Sx") + "He" <= 20 Or "Pj" >= 30)) And <user_defined_sfu_field_name> Is Null """,           ""],
    12: ['SF1',     """ ("Sb" + ("Sw" + "Sx") + "Bf" + ("Ce" + "Cw") + "La" + "Pw" + "Pj" + "Pr" + "He" >= 70) And <user_defined_sfu_field_name> Is Null """,          ""],
    13: ['PO1',     """ (("Po" + "Pt") + "Bw" + "Mh" + ("Pl" + "_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 70 And ("Po" + "Pt") >= 50) And <user_defined_sfu_field_name> Is Null """,          ""],
    14: ['BW1',     """ (("Po" + "Pt") + "Bw" + "Mh" + ("Pl" + "_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 70) And <user_defined_sfu_field_name> Is Null """,          ""],
    15: ['MH1',     """ ((("Bf" <= 20 And ("Sw" + "Sx") <= 20 And ("Ce" + "Cw") <= 20) And ("Po" + "Pt") + "Bw" + "Mh" + ("Pl" + "_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 50)) And <user_defined_sfu_field_name> Is Null """,           """AND ("Ecosite_GeoRangeAndNumber" in ('B016', 'B019', 'B028', 'B040', 'B043', 'B055', 'B059', 'B070', 'B076'))"""],
    16: ['MC1',     """ (("Bf" <= 20 And ("Sw" + "Sx") <= 20 And ("Ce" + "Cw") <= 20)) And <user_defined_sfu_field_name> Is Null """,           """AND ("Ecosite_GeoRangeAndNumber" in ('B012', 'B014', 'B035', 'B037', 'B050', 'B052', 'B053', 'B065', 'B067', 'B068'))"""],
    17: ['MH2',     """ (("Po" + "Pt") + "Bw" + "Mh" + ("Pl" + "_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 50) And <user_defined_sfu_field_name> Is Null """,          ""],
    18: ['MC2',     """ ("POLYTYPE" = 'FOR') And <user_defined_sfu_field_name> Is Null """,            ""]

}



IMF_3E_proof_of_concept_7_spp = {
# IMF 3E Proof of concept 6 species groups (email Dave Morris 2018-05-24 10:46; attachements (3))
#  This is interpretation of the the "6 species compositional groups" from the email attachments.
#  I added a seventh group to capture pure conifer forest stands that had species not included in the "pure" originally defined by Dave Morris in his document (email Dave Morris 2018-05-24 10:46; attachements (3); 2018-06-29 1223)

# fields required: POLYTYPE, Ecosite_GeoRangeAndNumber, (STKG or OSTKG) and (OSC or SC)

#   |Order   |SFU        |SQL                   |SQL addition if Ecosite incorporated

    1:  ['Pj Pure',     """ (("Pj" + "Ps") >= 70) And <user_defined_sfu_field_name> Is Null """,              ""],
    2:  ['Spr Pure',    """ (("Sb" + "_Sc" + "Sk" + "Sn" + "Sw" + "Sx" + "La" + ("Ce" + "Cw") >= 70)) And <user_defined_sfu_field_name> Is Null """,              ""],
    3:  ['PrPw',        """ ("Pw" + "Pr" >= 40) And <user_defined_sfu_field_name> Is Null """,              ""],
    4:  ['Conf Pure',   """ (("Bf" >= 70) Or ("Ce" >= 70) Or ("Cw" >= 70) Or ("La" >= 70) Or ("Le" >= 70) Or (("Pj" + "Ps") >= 70) Or ("Pn" >= 70) Or ("Pp" >= 70) Or ("Pr" >= 70) Or ("Ps" >= 70) Or ("Pw" >= 70) Or ("Sb" >= 70) Or ("_Sc" >= 70) Or ("Sk" >= 70) Or ("Sn" >= 70) Or ("Sw" >= 70) Or ("Sx" >= 70)) And <user_defined_sfu_field_name> Is Null """,              ""],
    5:  ['Hdwd Pure',   """ (("Po" + "Pt") + "Bw" + "Mh" + ("Pl" + "_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 70) And <user_defined_sfu_field_name> Is Null """,              ""],
    6:  ['Conif Mxd',   """ (("Bf" + "Ce" + "Cw" + "La" + "Le" + ("Pj" + "Ps") + "Pn" + "Pp" + "Pr" + "Ps" + "Pw" + "Sb" + "_Sc" + "Sk" + "Sn" + "Sw" + "Sx" >= 50) And (("Bf" <= 70) And ("Ce" <= 70) And ("Cw" <= 70) And ("La" <= 70) And ("Le" <= 70) And (("Pj" + "Ps") <= 70) And ("Pn" <= 70) And ("Pp" <= 70) And ("Pr" <= 70) And ("Ps" <= 70) And ("Pw" <= 70) And ("Sb" <= 70) And ("_Sc" <= 70) And ("Sk" <= 70) And ("Sn" <= 70) And ("Sw" <= 70) And ("Sx" <= 70))) And <user_defined_sfu_field_name> Is Null """,              ""],
    7:  ['Hdwd Mxd',    """ (("Ab" + "Bc" + "Bd" + "Be" + "Bl" + "Bn" + "Bp" + "Bw" + "_By" + "Cd" + "Ct" + "Ew" + "He" + "Kk" + "Lb" + "Mh" + "Mr" + "Ms" + "Ob" + "_Or" + "Pa" + "Pb" + "Pc" + "Ph" + "Pl" + "Po" + "Pt" + "RED" + "Ss" >= 50) And (("Ab" <= 70) And ("Bc" <= 70) And ("Bd" <= 70) And ("Be" <= 70) And ("Bl" <= 70) And ("Bn" <= 70) And ("Bp" <= 70) And ("Bw" <= 70) And ("_By" <= 70) And ("Cd" <= 70) And ("Ct" <= 70) And ("Ew" <= 70) And ("He" <= 70) And ("Kk" <= 70) And ("Lb" <= 70) And ("Mh" <= 70) And ("Mr" <= 70) And ("Ms" <= 70) And ("Ob" <= 70) And ("_Or" <= 70) And ("Pa" <= 70) And ("Pb" <= 70) And ("Pc" <= 70) And ("Ph" <= 70) And ("Pl" <= 70) And ("Po" <= 70) And ("Pt" <= 70) And ("RED" <= 70) And ("Ss" <= 70))) And <user_defined_sfu_field_name> Is Null """,              ""],
    8:  ['UDF',         """ ("POLYTYPE" = 'FOR') And <user_defined_sfu_field_name> Is Null """,              ""]
}


# Original version verified by Todd Little (2022-10-19 10:28)
NER_Boreal_Revised_SFU_2019_v9 = {
# Ontario Growth and Yield Program, "NER SFU Revision project".
#
# This is intended to be the second interpretation of the Ken Lennon's and Aklilu Yietagesu's NER SFU revision paper, with the changes discussed with Dave Etheridge and John Parton
# This version also address the species codes encountered in the compiled northeastern region (NER) enhanced forest resource inventory (EFRI; aka LIO pforest).
#  Sc to Sb
#  Ps to Pj
#  Bp to Bw
#  Sn to Sw
#  Be to upland hardwoods
#  Bl to upland hardwoods
#  Add the Great Lakes St. Lawrence ELC Ecosites geographic range letter code for ecosites: "G". Peter Uhlig confirmed that for me that the numbers represent the site the letter refers
#  the plant community associations of the geographic range.
#
# Adjusted ecosite relative to and informed by 'NER_Boreal_Revised_SFU_2018_v2'
# Adjusted LH1 to ensure that '"Pb" >=40' was not overridden by the pre 'Or' statement as in TN-021
#
# Include only species identified as relevent to NER Boreal Area: ..\NER pforest only dataset\analysis_spp_reference.xlsx
#  Remove   + ("Sn")
#           + "He"
#           + "_Sc"
#           + ("Be" + "Bl")
#           + "Ps"
#           + ("Bp")
#  2018-08-08
#
#  Change LH1 "Pb" >=40 back to >=30 as in the original TN-021
#  Remove the Pb from TH1, Pb is not a shade tolerant species.
#  2018-08-16
#
#  Change the LH1 SQL back to the original from TN-021 (remove ecosite contraints), and less the extra Pb > 30 which is redundant
#  2018-08-19
#
#  Changes based on the notes from the meetings with Stan Vasiliauskas and John Parton ca 2019-09
#  2019-04-01
#  See mon-p:NER SFU revision v6:review of output using new SFUs
#  fields required: POLYTYPE, Ecosite_GeoRangeAndNumber, (STKG or OSTKG) and (OSC or SC)
#
#  Additional changes for the discussion with John Parton ca. 2019-08
#      Refer to mon-p NER SFU Revision Project review of the v7 criteria
#
#      These changes require the manipulation for the ecosite variable, so that it is infact a required parameter now.
#
#      *** Use Ecosite or "useecosite == 'true'" in Poplulate_ForestUnit.py is now required due to the format of the following SQL statements ***
#
# Changes continued from notes from the meetings with Stan Vasiliauskas and John Parton ca 2019-09, and add notes from John Parton meeting 2019-10-07
#      Refer to mon-p NER SFU Revision Project review of the v8 criteria
#
#      All relevent: Add largetooth aspen (Pl) to all criteria with Po and Pt: "Po" + "Pt" becomes "Po" + "Pt" + "Pl" (email John Parton 2019-10-11 0913)
#
#      PW1: Add alternative to the OSTKG >=0.60
#
#      LH1: Add Mr and _By to the criteria
#
#      TH1: Add He to the criteria


# fields required: POLYTYPE, Ecosite_GeoRangeAndNumber and either OSC or SC

#   |Order   |SFU        |SQL                   |SQL addition if Ecosite incorporated               | SFU Descriptive Name

    1:  ['PR1',     """ ("Pr" >= 70) And <user_defined_sfu_field_name> Is Null """,            "",            """ Red pine, plantations """],
    2:  ['PW1',     """ (("Pw" + "Pr" + "He" + ("Sw" + "Sx") >= 40 And "Pw" >= 30) And ((("Pw" + "Pr" + "_Or" + "Ow" + "He" + "Sr" + "Sw" + ("Hi" + "Hl" + "Hm" + "Hp" + "Hs"))/100) * "STKG" * 44 >= 12.0)) And <user_defined_sfu_field_name> Is Null """,           "",            """White pine, shelterwood"""],
    3:  ['PRW',     """ (("Pw" + "Pr" + "He" + ("Sw" + "Sx") >= 40) And ("Pw" + "Pr" >= 30)) And <user_defined_sfu_field_name> Is Null """,         "",            """Red and white pine"""],

    #  Note that in LH1 the ecosite is no longer in its own element of the dictionary. It is withing the primary sql element. This hasn't been done before. It is not explicit that ecosite is required for this sql set elsewhere in the script (2019-08-28)
    4:  ['LH1',     """ ((("Ab" + "Ew" + "Pb" + "Mr" + "_By") >= 30) And (("Ab" + "Ew" + "_By" >= 20) Or ("Ecosite_GeoRangeAndNumber" in ('B119', 'B120', 'B123', 'B129', 'B130', 'B131', 'B133', 'G119', 'G120', 'G123', 'G129', 'G130', 'G131', 'G133'))) Or ("Pb" >= 70)) And <user_defined_sfu_field_name> Is Null """,          "",            """Lowland Hardwood"""],


    5:  ['TH1',     """ (("Ab" + "Ew") + "Mh" + ("_By" + "Mr") + "He" >= 30) And <user_defined_sfu_field_name> Is Null """,          "",             """Tolerant Hardwoods"""],

    # Note that in SBOG the ecosite is no longer in its own element of the dictionary. It is within the primary sql element. This hasn't been done before. It is not explicit that ecosite is required for this sql set elsewhere in the script (2019-08-23)
    6:  ['SBOG',    """ (("Sb" + "La" + ("Ce" + "Cw") >= 70) And ((("OSC" = 4) And ("Ecosite_GeoRangeAndNumber" in ('B126', 'B136','B137',  'G126', 'G136', 'G137'))))) And <user_defined_sfu_field_name> Is Null """,            "",             """Black spruce, bog"""],

    # Note that SB1 Ab (black ash) is now less than 10%, and ecosite 126 is no longer an eligible ecosite.
    # Added 129 and 224 ecosites to put emphasis on the species composition and site class, when site are >80%Sb and NOT SC=4. 
    #  Preventing stands from becoming LC1. More confident the site is lowland and black spruce, but the ecosite classification was not correct. 
    #  This decision reflects the importance-confidence of species in the forest unit classification.
    7:  ['SB1',     """ ((("Sb" >= 80)) And ("Ab" <= 10)  AND "Ecosite_GeoRangeAndNumber" in ('B127', 'B128', 'B129', 'B222', 'B223', 'B224', 'G127', 'G128', 'G129', 'G222', 'G223', 'G224')) And <user_defined_sfu_field_name> Is Null """,          "",             """Black spruce, lowland"""],

    8:  ['PJ1',     """ (((("Pj" >= 70) And (("Po" + "Pt") + "Bw" + ("_By" + "Mr") + "Mh" + ("Ab" + "Ew" + "Pb") <= 20)) And "Ecosite_GeoRangeAndNumber" in ('B012', 'B033', 'B034', 'B035', 'B048', 'B049', 'B050', 'G012', 'G033', 'G034', 'G035',  'G048', 'G049', 'G050')) Or ("Pj" >= 90)) And <user_defined_sfu_field_name> Is Null """,          "",             """Jack pine, pure"""],
    9:  ['LC1',     """ ((("Ce" + "Cw") + "La" + "Sb" + "Bf" + "Sw">= 70) AND ("Ecosite_GeoRangeAndNumber" in ('B127', 'B128', 'B129', 'B222', 'B223', 'B224', 'B136', 'B137', 'G127', 'G128', 'G129', 'G222', 'G223', 'G224', 'G136', 'G137'))) And <user_defined_sfu_field_name> Is Null """,           "",            """Lowland conifer"""],
    
    # Changed Pj >= 50 to Pj >=30 (2019-12-05). See mon-p
    10: ['PJ2',     """ ((("Pj" + "Sb" + "Pr" + "Pw" >= 70) Or ("Pj" >= 30 And "Pj" + "Sb" + "Bf" + ("Sw" + "Sx") + "Pw" + "Pr" + ("Ce" + "Cw") + "La" >=70)) And (("Pj" + "Pw" + "Pr") >= ("Sb" + ("Sw" + "Sx") + ("Ce" + "Cw")))) And <user_defined_sfu_field_name> Is Null """,           "",             """Jack pine black spruce"""],
    11: ['SP1',     """ (("Sb" + ("Sw" + "Sx") + "Bf" + ("Ce" + "Cw") + "La" + "Pw" + "Pj" + "Pr" + "He">=70) And (("Bf" + ("Ce" + "Cw") + "Pw" + ("Sw" + "Sx") + "He" <= 20) Or ("Pj" + "Pr" + "La" >= 30)))  And <user_defined_sfu_field_name> Is Null """,           "",            """Spruce, upland"""],
    12: ['SF1',     """ ("Sb" + ("Sw" + "Sx") + "Bf" + ("Ce" + "Cw") + "La" + "Pw" + "Pj" + "Pr" >= 70) And <user_defined_sfu_field_name> Is Null """,          ""],
    13: ['PO1',     """ ((("Po" + "Pt" + "Pl") + "Bw" + "Mh" + ("_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 70) And (("Po" + "Pt" + "Pl" + "Pb") >= 50)) And <user_defined_sfu_field_name> Is Null """,          "",            """Poplar"""],
    14: ['BW1',     """ (("Po" + "Pt" + "Pl") + "Bw" + "Mh" + ("_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 70) And <user_defined_sfu_field_name> Is Null """,          "",            """White birch"""],
    15: ['MH1',     """ (((("Bf" <= 20 And ("Sw" + "Sx") <= 20 And ("Ce" + "Cw") <= 20) And ("Po" + "Pt" + "Pl") + "Bw" + "Mh" + ("_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 50) And ("Pj" + "Pr" <= 50 And "Pj" + "Pr" >= 20)) AND ("Ecosite_GeoRangeAndNumber" in ('B016', 'B019', 'B028', 'B040', 'B043', 'B055', 'B059', 'B070', 'B076',  'G016', 'G019', 'G028', 'G040', 'G043', 'G055', 'G059', 'G070', 'G076'))) And <user_defined_sfu_field_name> Is Null """,           "",            """Mixedwood hardwood fresh coarse"""],
    16: ['MC1',     """ ((("Bf" <= 20 And ("Sw" + "Sx") <= 20 And ("Ce" + "Cw") <= 20 And ("Pj" + "Pr" + "La") >= 20) AND ("Ecosite_GeoRangeAndNumber" in ('B012', 'B014', 'B035', 'B037', 'B038', 'B050', 'B052', 'B053', 'B065', 'B067', 'B068',  'G012', 'G014', 'G035', 'G037', 'G037', 'G050', 'G052', 'G053', 'G065', 'G067', 'G068')))  Or ("Pj" + "Pr" >= 50)) And <user_defined_sfu_field_name> Is Null """,           "",             """Mixedwood conifer fresh coarse"""],
    17: ['MH2',     """ (("Po" + "Pt" + "Pl") + "Bw" + "Mh" + ("_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 50) And <user_defined_sfu_field_name> Is Null """,          "",            """Mixedwood hardwood moist fine"""],
    18: ['MC2',     """ ("Sb" + ("Sw" + "Sx") + "Bf" + ("Ce" + "Cw") + "La" + "Pw" + "Pj" + "Pr" > 50) And <user_defined_sfu_field_name> Is Null """,          "",            """Mixedwood conifer moist fine"""],
    19: ['UDF',     """ ("POLYTYPE" = 'FOR') And <user_defined_sfu_field_name> Is Null """,            "",            """Undefined"""]

}


NER_Boreal_v9_ROD2023 = {
# on Apr 2023, updates have been made to PW1 and LH1
# This SQL will use Ecosite whether you check the "Use Ecosite" checkbox or not on the ArcMap's user interface.
# Another change is that we added MWD (Balsam Fir leading Mixedwood) and changed STKG to OSTKG (if we have OSTKG then it can be replaced with STKG through the user interface)
# fields required: POLYTYPE, STKG (or OSTKG) Ecosite_GeoRangeAndNumber and either OSC or SC

#   |Order   |SFU        |SQL                   |SQL addition if Ecosite incorporated               | SFU Descriptive Name

    1:  ['PR1',     """ ("Pr" >= 70) And <user_defined_sfu_field_name> Is Null """,            "",            """ Red pine, plantations """],
    2:  ['PW1',     """ ("Pw" + "Pr" + "He" + ("Sw" + "Sx") >= 40 And "Pw" >= 30) And <user_defined_sfu_field_name> Is Null """,           "",            """White pine, shelterwood"""],
    3:  ['PRW',     """ (("Pw" + "Pr" + "He" + ("Sw" + "Sx") >= 40) And ("Pw" + "Pr" >= 30)) And <user_defined_sfu_field_name> Is Null """,         "",            """Red and white pine"""],

    #  Note that in LH1 the ecosite is no longer in its own element of the dictionary. It is withing the primary sql element. This hasn't been done before. It is not explicit that ecosite is required for this sql set elsewhere in the script (2019-08-28)
    4:  ['LH1',     """ ("Ab" + "Ew" + "_By" >= 20 AND ("Ecosite_GeoRangeAndNumber" in ('B119', 'B120', 'B123', 'B129', 'B130', 'B131', 'B133', 'G119', 'G120', 'G123', 'G129', 'G130', 'G131', 'G133'))) Or ("Pb" >= 70) And <user_defined_sfu_field_name> Is Null """,          "",            """Lowland Hardwood"""],

    5:  ['TH1',     """ (("Ab" + "Ew") + "Mh" + ("_By" + "Mr") + "He" >= 30) And <user_defined_sfu_field_name> Is Null """,          "",             """Tolerant Hardwoods"""],

    # Note that in SBOG the ecosite is no longer in its own element of the dictionary. It is within the primary sql element. This hasn't been done before. It is not explicit that ecosite is required for this sql set elsewhere in the script (2019-08-23)
    6:  ['SBOG',    """ (("Sb" + "La" + ("Ce" + "Cw") >= 70) And ((("OSC" = 4) And ("Ecosite_GeoRangeAndNumber" in ('B126', 'B136','B137',  'G126', 'G136', 'G137'))))) And <user_defined_sfu_field_name> Is Null """,            "",             """Black spruce, bog"""],

    # Note that SB1 Ab (black ash) is now less than 10%, and ecosite 126 is no longer an eligible ecosite.
    # Added 129 and 224 ecosites to put emphasis on the species composition and site class, when site are >80%Sb and NOT SC=4. 
    #  Preventing stands from becoming LC1. More confident the site is lowland and black spruce, but the ecosite classification was not correct. 
    #  This decision reflects the importance-confidence of species in the forest unit classification.
    7:  ['SB1',     """ ((("Sb" >= 80)) And ("Ab" <= 10)  AND "Ecosite_GeoRangeAndNumber" in ('B127', 'B128', 'B129', 'B222', 'B223', 'B224', 'G127', 'G128', 'G129', 'G222', 'G223', 'G224')) And <user_defined_sfu_field_name> Is Null """,          "",             """Black spruce, lowland"""],

    8:  ['PJ1',     """ (((("Pj" >= 70) And (("Po" + "Pt") + "Bw" + ("_By" + "Mr") + "Mh" + ("Ab" + "Ew" + "Pb") <= 20)) And "Ecosite_GeoRangeAndNumber" in ('B012', 'B033', 'B034', 'B035', 'B048', 'B049', 'B050', 'G012', 'G033', 'G034', 'G035',  'G048', 'G049', 'G050')) Or ("Pj" >= 90)) And <user_defined_sfu_field_name> Is Null """,          "",             """Jack pine, pure"""],
    9:  ['LC1',     """ ((("Ce" + "Cw") + "La" + "Sb" + "Bf" + "Sw">= 70) AND ("Ecosite_GeoRangeAndNumber" in ('B127', 'B128', 'B129', 'B222', 'B223', 'B224', 'B136', 'B137', 'G127', 'G128', 'G129', 'G222', 'G223', 'G224', 'G136', 'G137'))) And <user_defined_sfu_field_name> Is Null """,           "",            """Lowland conifer"""],
    
    # Changed Pj >= 50 to Pj >=30 (2019-12-05). See mon-p
    10: ['PJ2',     """ ((("Pj" + "Sb" + "Pr" + "Pw" >= 70) Or ("Pj" >= 30 And "Pj" + "Sb" + "Bf" + ("Sw" + "Sx") + "Pw" + "Pr" + ("Ce" + "Cw") + "La" >=70)) And (("Pj" + "Pw" + "Pr") >= ("Sb" + ("Sw" + "Sx") + ("Ce" + "Cw")))) And <user_defined_sfu_field_name> Is Null """,           "",             """Jack pine black spruce"""],
    11: ['SP1',     """ (("Sb" + ("Sw" + "Sx") + "Bf" + ("Ce" + "Cw") + "La" + "Pw" + "Pj" + "Pr" + "He">=70) And (("Bf" + ("Ce" + "Cw") + "Pw" + ("Sw" + "Sx") + "He" <= 20) Or ("Pj" + "Pr" + "La" >= 30)))  And <user_defined_sfu_field_name> Is Null """,           "",            """Spruce, upland"""],
    12: ['SF1',     """ ("Sb" + ("Sw" + "Sx") + "Bf" + ("Ce" + "Cw") + "La" + "Pw" + "Pj" + "Pr" >= 70) And <user_defined_sfu_field_name> Is Null """,          ""],
    13: ['PO1',     """ ((("Po" + "Pt" + "Pl") + "Bw" + "Mh" + ("_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 70) And (("Po" + "Pt" + "Pl" + "Pb") >= 50)) And <user_defined_sfu_field_name> Is Null """,          "",            """Poplar"""],
    14: ['BW1',     """ (("Po" + "Pt" + "Pl") + "Bw" + "Mh" + ("_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 70) And <user_defined_sfu_field_name> Is Null """,          "",            """White birch"""],
    15: ['MH1',     """ (((("Bf" <= 20 And ("Sw" + "Sx") <= 20 And ("Ce" + "Cw") <= 20) And ("Po" + "Pt" + "Pl") + "Bw" + "Mh" + ("_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 50) And ("Pj" + "Pr" <= 50 And "Pj" + "Pr" >= 20)) AND ("Ecosite_GeoRangeAndNumber" in ('B016', 'B019', 'B028', 'B040', 'B043', 'B055', 'B059', 'B070', 'B076',  'G016', 'G019', 'G028', 'G040', 'G043', 'G055', 'G059', 'G070', 'G076'))) And <user_defined_sfu_field_name> Is Null """,           "",            """Mixedwood hardwood fresh coarse"""],
    16: ['MC1',     """ ((("Bf" <= 20 And ("Sw" + "Sx") <= 20 And ("Ce" + "Cw") <= 20 And ("Pj" + "Pr" + "La") >= 20) AND ("Ecosite_GeoRangeAndNumber" in ('B012', 'B014', 'B035', 'B037', 'B038', 'B050', 'B052', 'B053', 'B065', 'B067', 'B068',  'G012', 'G014', 'G035', 'G037', 'G037', 'G050', 'G052', 'G053', 'G065', 'G067', 'G068')))  Or ("Pj" + "Pr" >= 50)) And <user_defined_sfu_field_name> Is Null """,           "",             """Mixedwood conifer fresh coarse"""],
    17: ['MH2',     """ (("Po" + "Pt" + "Pl") + "Bw" + "Mh" + ("_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 50) And <user_defined_sfu_field_name> Is Null """,          "",            """Mixedwood hardwood moist fine"""],
    18: ['MC2',     """ ("Sb" + ("Sw" + "Sx") + "Bf" + ("Ce" + "Cw") + "La" + "Pw" + "Pj" + "Pr" > 50) And <user_defined_sfu_field_name> Is Null """,          "",            """Mixedwood conifer moist fine"""],
    19: ['UDF',     """ ("POLYTYPE" = 'FOR') And <user_defined_sfu_field_name> Is Null """,            "",            """Undefined"""],

    22: ['SB1',     """ ("POLYTYPE" = 'FOR' And <user_defined_sfu_field_name> Is Null) """,            """OR (<user_defined_sfu_field_name> = 'SP1' AND "Ecosite_GeoRangeAndNumber" IN ('B126', 'B127', 'B128', 'B129', 'B136', 'B222', 'B223', 'B224'))"""], # The reason why I included the seemingly unnecessary first part of the SQL is because the tool has an option to NOT use Ecosite. if the user decides not to use Ecosite, only the first part of the SQL will be used and it will basically select nothing.
    23: ['LC1',     """ ("POLYTYPE" = 'FOR' And <user_defined_sfu_field_name> Is Null) """,            """OR (<user_defined_sfu_field_name> = 'SF1' AND "Ecosite_GeoRangeAndNumber" IN ('B126', 'B127', 'B128', 'B129', 'B136', 'B222', 'B223', 'B224'))"""],
    24: ['LH1',     """ (<user_defined_sfu_field_name> in ('TH1','PO1','BW1','MH1','MH2') AND "Ecosite_GeoRangeAndNumber" in ('B130','B131')) """,           ""],

    28: ['SP1',    """ (<user_defined_sfu_field_name> = 'SB1' AND "DEVSTAGE" in('NEWPLANT','ESTPLANT')) """,            ""],
    29: ['SP1',    """ (<user_defined_sfu_field_name> = 'SF1' AND "DEVSTAGE" in('NEWPLANT','ESTPLANT') AND ("Bf" + "La" <=20)) """,            ""],
}


NER_Boreal_SRNV2023 = {
# used during SRNV project of 2023 (Sam Nsiah, Gordon Kayahara, Jen Neilson)
# based on NER_Boreal_v9_ROD2023
# addition of PRPW10

#   |Order   |SFU        |SQL                   |SQL addition if Ecosite incorporated               | SFU Descriptive Name

    1:  ['PR1',     """ ("Pr" >= 70) And <user_defined_sfu_field_name> Is Null """,            "",            """ Red pine, plantations """],
    2:  ['PW1',     """ ("Pw" + "Pr" + "He" + ("Sw" + "Sx") >= 40 And "Pw" >= 30) And <user_defined_sfu_field_name> Is Null """,           "",            """White pine, shelterwood"""],
    3:  ['PRW',     """ (("Pw" + "Pr" + "He" + ("Sw" + "Sx") >= 40) And ("Pw" + "Pr" >= 30)) And <user_defined_sfu_field_name> Is Null """,         "",            """Red and white pine"""],

    #  Note that in LH1 the ecosite is no longer in its own element of the dictionary. It is withing the primary sql element. This hasn't been done before. It is not explicit that ecosite is required for this sql set elsewhere in the script (2019-08-28)
    4:  ['LH1',     """ ("Ab" + "Ew" + "_By" >= 20 AND ("Ecosite_GeoRangeAndNumber" in ('B119', 'B120', 'B123', 'B129', 'B130', 'B131', 'B133', 'G119', 'G120', 'G123', 'G129', 'G130', 'G131', 'G133'))) Or ("Pb" >= 70) And <user_defined_sfu_field_name> Is Null """,          "",            """Lowland Hardwood"""],

    5:  ['TH1',     """ (("Ab" + "Ew") + "Mh" + ("_By" + "Mr") + "He" >= 30) And <user_defined_sfu_field_name> Is Null """,          "",             """Tolerant Hardwoods"""],

    # Note that in SBOG the ecosite is no longer in its own element of the dictionary. It is within the primary sql element. This hasn't been done before. It is not explicit that ecosite is required for this sql set elsewhere in the script (2019-08-23)
    6:  ['SBOG',    """ (("Sb" + "La" + ("Ce" + "Cw") >= 70) And ((("OSC" = 4) And ("Ecosite_GeoRangeAndNumber" in ('B126', 'B136','B137',  'G126', 'G136', 'G137'))))) And <user_defined_sfu_field_name> Is Null """,            "",             """Black spruce, bog"""],

    # Note that SB1 Ab (black ash) is now less than 10%, and ecosite 126 is no longer an eligible ecosite.
    # Added 129 and 224 ecosites to put emphasis on the species composition and site class, when site are >80%Sb and NOT SC=4. 
    #  Preventing stands from becoming LC1. More confident the site is lowland and black spruce, but the ecosite classification was not correct. 
    #  This decision reflects the importance-confidence of species in the forest unit classification.
    7:  ['SB1',     """ ((("Sb" >= 80)) And ("Ab" <= 10)  AND "Ecosite_GeoRangeAndNumber" in ('B127', 'B128', 'B129', 'B222', 'B223', 'B224', 'G127', 'G128', 'G129', 'G222', 'G223', 'G224')) And <user_defined_sfu_field_name> Is Null """,          "",             """Black spruce, lowland"""],

    8:  ['PJ1',     """ (((("Pj" >= 70) And (("Po" + "Pt") + "Bw" + ("_By" + "Mr") + "Mh" + ("Ab" + "Ew" + "Pb") <= 20)) And "Ecosite_GeoRangeAndNumber" in ('B012', 'B033', 'B034', 'B035', 'B048', 'B049', 'B050', 'G012', 'G033', 'G034', 'G035',  'G048', 'G049', 'G050')) Or ("Pj" >= 90)) And <user_defined_sfu_field_name> Is Null """,          "",             """Jack pine, pure"""],
    9:  ['LC1',     """ ((("Ce" + "Cw") + "La" + "Sb" + "Bf" + "Sw">= 70) AND ("Ecosite_GeoRangeAndNumber" in ('B127', 'B128', 'B129', 'B222', 'B223', 'B224', 'B136', 'B137', 'G127', 'G128', 'G129', 'G222', 'G223', 'G224', 'G136', 'G137'))) And <user_defined_sfu_field_name> Is Null """,           "",            """Lowland conifer"""],
    
    # Changed Pj >= 50 to Pj >=30 (2019-12-05). See mon-p
    10: ['PJ2',     """ ((("Pj" + "Sb" + "Pr" + "Pw" >= 70) Or ("Pj" >= 30 And "Pj" + "Sb" + "Bf" + ("Sw" + "Sx") + "Pw" + "Pr" + ("Ce" + "Cw") + "La" >=70)) And (("Pj" + "Pw" + "Pr") >= ("Sb" + ("Sw" + "Sx") + ("Ce" + "Cw")))) And <user_defined_sfu_field_name> Is Null """,           "",             """Jack pine black spruce"""],
    11: ['SP1',     """ (("Sb" + ("Sw" + "Sx") + "Bf" + ("Ce" + "Cw") + "La" + "Pw" + "Pj" + "Pr" + "He">=70) And (("Bf" + ("Ce" + "Cw") + "Pw" + ("Sw" + "Sx") + "He" <= 20) Or ("Pj" + "Pr" + "La" >= 30)))  And <user_defined_sfu_field_name> Is Null """,           "",            """Spruce, upland"""],
    12: ['SF1',     """ ("Sb" + ("Sw" + "Sx") + "Bf" + ("Ce" + "Cw") + "La" + "Pw" + "Pj" + "Pr" >= 70) And <user_defined_sfu_field_name> Is Null """,          ""],
    13: ['PO1',     """ ((("Po" + "Pt" + "Pl") + "Bw" + "Mh" + ("_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 70) And (("Po" + "Pt" + "Pl" + "Pb") >= 50)) And <user_defined_sfu_field_name> Is Null """,          "",            """Poplar"""],
    14: ['BW1',     """ (("Po" + "Pt" + "Pl") + "Bw" + "Mh" + ("_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 70) And <user_defined_sfu_field_name> Is Null """,          "",            """White birch"""],
    15: ['MH1',     """ (((("Bf" <= 20 And ("Sw" + "Sx") <= 20 And ("Ce" + "Cw") <= 20) And ("Po" + "Pt" + "Pl") + "Bw" + "Mh" + ("_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 50) And ("Pj" + "Pr" <= 50 And "Pj" + "Pr" >= 20)) AND ("Ecosite_GeoRangeAndNumber" in ('B016', 'B019', 'B028', 'B040', 'B043', 'B055', 'B059', 'B070', 'B076',  'G016', 'G019', 'G028', 'G040', 'G043', 'G055', 'G059', 'G070', 'G076'))) And <user_defined_sfu_field_name> Is Null """,           "",            """Mixedwood hardwood fresh coarse"""],
    16: ['MC1',     """ ((("Bf" <= 20 And ("Sw" + "Sx") <= 20 And ("Ce" + "Cw") <= 20 And ("Pj" + "Pr" + "La") >= 20) AND ("Ecosite_GeoRangeAndNumber" in ('B012', 'B014', 'B035', 'B037', 'B038', 'B050', 'B052', 'B053', 'B065', 'B067', 'B068',  'G012', 'G014', 'G035', 'G037', 'G037', 'G050', 'G052', 'G053', 'G065', 'G067', 'G068')))  Or ("Pj" + "Pr" >= 50)) And <user_defined_sfu_field_name> Is Null """,           "",             """Mixedwood conifer fresh coarse"""],
    17: ['MH2',     """ (("Po" + "Pt" + "Pl") + "Bw" + "Mh" + ("_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 50) And <user_defined_sfu_field_name> Is Null """,          "",            """Mixedwood hardwood moist fine"""],
    18: ['MC2',     """ ("Sb" + ("Sw" + "Sx") + "Bf" + ("Ce" + "Cw") + "La" + "Pw" + "Pj" + "Pr" > 50) And <user_defined_sfu_field_name> Is Null """,          "",            """Mixedwood conifer moist fine"""],
    19: ['UDF',     """ ("POLYTYPE" = 'FOR') And <user_defined_sfu_field_name> Is Null """,            "",            """Undefined"""],

    22: ['SB1',     """ ("POLYTYPE" = 'FOR' And <user_defined_sfu_field_name> Is Null) """,            """OR (<user_defined_sfu_field_name> = 'SP1' AND "Ecosite_GeoRangeAndNumber" IN ('B126', 'B127', 'B128', 'B129', 'B136', 'B222', 'B223', 'B224'))"""], # The reason why I included the seemingly unnecessary first part of the SQL is because the tool has an option to NOT use Ecosite. if the user decides not to use Ecosite, only the first part of the SQL will be used and it will basically select nothing.
    23: ['LC1',     """ ("POLYTYPE" = 'FOR' And <user_defined_sfu_field_name> Is Null) """,            """OR (<user_defined_sfu_field_name> = 'SF1' AND "Ecosite_GeoRangeAndNumber" IN ('B126', 'B127', 'B128', 'B129', 'B136', 'B222', 'B223', 'B224'))"""],
    24: ['LH1',     """ (<user_defined_sfu_field_name> in ('TH1','PO1','BW1','MH1','MH2') AND "Ecosite_GeoRangeAndNumber" in ('B130','B131')) """,           ""],

    28: ['SP1',    """ (<user_defined_sfu_field_name> = 'SB1' AND "DEVSTAGE" in('NEWPLANT','ESTPLANT')) """,            ""],
    29: ['SP1',    """ (<user_defined_sfu_field_name> = 'SF1' AND "DEVSTAGE" in('NEWPLANT','ESTPLANT') AND ("Bf" + "La" <=20)) """,            ""],

    30: ['PRPW10',   """ ("POLYTYPE" = 'FOR' AND <user_defined_sfu_field_name> not in ('PR1','PRW','PW1') AND "PR"+"PW">=10) """,            ""],
}







NER_Boreal_SRNV_SPCOMP_ONLY = {
    # a version made specifically for Quebec inventory which has different standard for ecosite and site class
    # This only uses SPCOMP (and POLYTYPE) to determine all SFU
    # SQL for SB1: changed 80 to 70
    # for SBOG, added "Sb" < 70 
#   |Order   |SFU        |SQL                   |SQL addition if Ecosite incorporated               | SFU Descriptive Name

    1:  ['PR1',     """ ("Pr" >= 70) And <user_defined_sfu_field_name> Is Null """,            "",            """ Red pine, plantations """],
    2:  ['PW1',     """ ("Pw" + "Pr" + "He" + ("Sw" + "Sx") >= 40 And "Pw" >= 30) And <user_defined_sfu_field_name> Is Null """,           "",            """White pine, shelterwood"""],
    3:  ['PRW',     """ (("Pw" + "Pr" + "He" + ("Sw" + "Sx") >= 40) And ("Pw" + "Pr" >= 30)) And <user_defined_sfu_field_name> Is Null """,         "",            """Red and white pine"""],
    4:  ['LH1',     """ "Ab" + "Ew" + "_By" >= 20 Or "Pb" >= 70 And <user_defined_sfu_field_name> Is Null """,          "",            """Lowland Hardwood"""],
    5:  ['TH1',     """ (("Ab" + "Ew") + "Mh" + ("_By" + "Mr") + "He" >= 30) And <user_defined_sfu_field_name> Is Null """,          "",             """Tolerant Hardwoods"""],
    6:  ['SBOG',    """ "Sb" + "La" + "Ce" + "Cw" >= 70 And "Sb" < 70 and <user_defined_sfu_field_name> Is Null """,            "",             """Black spruce, bog"""],
    7:  ['SB1',     """ "Sb" >= 70 And "Ab" <= 10  And <user_defined_sfu_field_name> Is Null """,          "",             """Black spruce, lowland"""],
    8:  ['PJ1',     """ (("Pj" >= 70 And "Po" + "Pt" + "Bw" + "_By" + "Mr" + "Mh" + "Ab" + "Ew" + "Pb" <= 20) Or "Pj" >= 90) And <user_defined_sfu_field_name> Is Null """,          "",             """Jack pine, pure"""],
    9:  ['LC1',     """ "Ce" + "Cw" + "La" + "Sb" + "Bf" + "Sw">= 70 And <user_defined_sfu_field_name> Is Null """,           "",            """Lowland conifer"""],
    10: ['UPCE',    """ ("Ce" + "Cw") >= 40 And <user_defined_sfu_field_name> Is Null """,           "",            """Upland Cedar"""],
    11: ['PJ2',     """ ((("Pj" + "Sb" + "Pr" + "Pw" >= 70) Or ("Pj" >= 30 And "Pj" + "Sb" + "Bf" + ("Sw" + "Sx") + "Pw" + "Pr" + ("Ce" + "Cw") + "La" >=70)) And (("Pj" + "Pw" + "Pr") >= ("Sb" + ("Sw" + "Sx") + ("Ce" + "Cw")))) And <user_defined_sfu_field_name> Is Null """,           "",             """Jack pine black spruce"""],
    12: ['SP1',     """ (("Sb" + ("Sw" + "Sx") + "Bf" + ("Ce" + "Cw") + "La" + "Pw" + "Pj" + "Pr" + "He">=70) And 
                        (("Bf" + ("Ce" + "Cw") + "Pw" + ("Sw" + "Sx") + "He" <= 20) Or ("Pj" + "Pr" + "La" >= 30)))  And <user_defined_sfu_field_name> Is Null """,           "",            """Spruce, upland"""],
    13: ['SF1',     """ ("Sb" + ("Sw" + "Sx") + "Bf" + ("Ce" + "Cw") + "La" + "Pw" + "Pj" + "Pr" >= 70) And <user_defined_sfu_field_name> Is Null """,          ""],
    14: ['PO1',     """ ((("Po" + "Pt" + "Pl") + "Bw" + "Mh" + ("_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 70) And (("Po" + "Pt" + "Pl" + "Pb") >= 50)) And <user_defined_sfu_field_name> Is Null """,          "",            """Poplar"""],
    15: ['BW1',     """ (("Po" + "Pt" + "Pl") + "Bw" + "Mh" + ("_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 70) And <user_defined_sfu_field_name> Is Null """,          "",            """White birch"""],
    16: ['MH1',     """ "Bf" <= 20 And "Sw" + "Sx" <= 20 And "Ce" + "Cw" <= 20 And "Po" + "Pt" + "Pl" + "Bw" + "Mh" + "_By" + "Mr" + "Ab" + "Ew" + "Pb" >= 50 And "Pj" + "Pr" <= 50 And "Pj" + "Pr" >= 20 And <user_defined_sfu_field_name> Is Null """,           "",            """Mixedwood hardwood fresh coarse"""],
    17: ['MC1',     """ (("Bf" <= 20 And "Sw" + "Sx" <= 20 And "Ce" + "Cw" <= 20 And "Pj" + "Pr" + "La" >= 20) Or "Pj" + "Pr" >= 50) And <user_defined_sfu_field_name> Is Null """,           "",             """Mixedwood conifer fresh coarse"""],
    18: ['MH2',     """ (("Po" + "Pt" + "Pl") + "Bw" + "Mh" + ("_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 50) And <user_defined_sfu_field_name> Is Null """,          "",            """Mixedwood hardwood moist fine"""],
    19: ['MC2',     """ ("Sb" + ("Sw" + "Sx") + "Bf" + ("Ce" + "Cw") + "La" + "Pw" + "Pj" + "Pr" > 50) And <user_defined_sfu_field_name> Is Null """,          "",            """Mixedwood conifer moist fine"""],
    20: ['UDF',     """ ("POLYTYPE" = 'FOR') And <user_defined_sfu_field_name> Is Null """,            "",            """Undefined"""],

    41: ['MH2',     """ <user_defined_sfu_field_name> = 'UDF' AND ("Po" + "Pt" + "Pl") + "Bw" + ("Mh" + "Ms" + "Mr") + "_By" + ("Ab" + "Ew" + "Pb") + "OH" > "Sb" + ("Sw" + "Sx") + "Bf" + ("Ce" + "Cw") + "La" + "Pw" + "Pj" + "Pr" + "OC" """,            ""],
    42: ['MC2',     """ <user_defined_sfu_field_name> = 'UDF' """,            ""],

}


NWR_Boreal_SFU = {
# Northwest Region Standard Forest Units (email Rob Bowen 2018-03-29 13:00; attachements (3))
#  This is the latest information for the Northwest Region Standard forest units as of 2018-03-29 13:00.

#  fields required: POLYTYPE, Ecosite_GeoRangeAndNumber, (STKG or OSTKG) and (OSC or SC)

#   |Order   |SFU        |SQL                   |SQL addition if Ecosite incorporated               | SFU Descriptive Name

    1:  ['PwDom',  """ ("Pw" >= 40) And <user_defined_sfu_field_name> Is Null """,                                       "",     """White Pine Dominant"""],
    2:  ['PrDom',  """ ("Pr" >= 70) And <user_defined_sfu_field_name> Is Null """,                                       "",     """Red Pine Dominant"""],
    3:  ['PrwMx',  """ ("Pw" + "Pr" >= 40) And <user_defined_sfu_field_name> Is Null """,                                "",     """Red and White Pine Mix"""],
    4:  ['UplCe',  """ (((("Cw" + "Ce") >= 20) AND ("Ecosite_GeoRangeAndNumber" in ('B013', 'B036', 'B051', 'B066', 'B084', 'B100', 'B115'))) Or ((("Cw" + "Ce") >= 40 And "Bf" <= 10) And (("Pr" + "Pw" + "Pj" + "Sw" + "Bf" + "Po") >= 20) And (("Pj" + "Pr" + "Pw" + "Sb" + "Sw" + "La" + "Cw" + "Bf" + "He") >= 70) AND NOT (("Ecosite_GeoRangeAndNumber" in ('B126', 'B127', 'B128', 'B129', 'B134', 'B135', 'B136', 'B137', 'B222', 'B223', 'B224')) Or ("Ecosite_GeoRangeAndNumber" in ('B130', 'B131', 'B132', 'B133'))))) And <user_defined_sfu_field_name> Is Null  """,       "",       """Upland Cedar"""],
    5:  ['OCLow',  """ (((("Cw" + "Ce") + "La") >=50) Or ("OLEADSPC" in ('Cw', 'La'))) And <user_defined_sfu_field_name> Is Null """,                      """AND ("Ecosite_GeoRangeAndNumber" in ('B126', 'B127', 'B128', 'B129', 'B134', 'B135', 'B136', 'B137', 'B222', 'B223', 'B224')) """,       """Other Conifer Lowland"""],
    6:  ['SbLow',  """ (("Ecosite_GeoRangeAndNumber" in ('B126', 'B127', 'B128', 'B129', 'B134', 'B135', 'B136', 'B137', 'B222', 'B223', 'B224')) Or (("Ecosite_GeoRangeAndNumber" in ('B130', 'B131', 'B132', 'B133')) And (("Pr" + "Pw" + "Pj" + "Sb" + "Sw" + "La" + ("Cw" + "Ce") + "Bf") > (("Po" + "Pt") + "Bw" + ("Mh" + "Mr" + "Ms" + "Mx" + "Ob" + "_Or" + "Ox") + ("Ab" + "Ew" + "Pb"))))) And <user_defined_sfu_field_name> Is Null """,     "",     """Black Spruce Lowland"""],
    7:  ['SbSha',  """ (("Sb" >= 70) And (("Po" + "Pt") + "Bw" <=20)) And <user_defined_sfu_field_name> Is Null """,     """AND ("Ecosite_GeoRangeAndNumber" in ('B011', 'B012', 'B014', 'B015', 'B016', 'B017', 'B018', 'B019', 'B023', 'B024', 'B025', 'B026', 'B027', 'B028')) """,      """Black Spruce Shallow"""],
    8:  ['SbDee',  """ (("Sb" >= 70) And (("Po" + "Pt") + "Bw" <=20)) And <user_defined_sfu_field_name> Is Null """,     "",         """Black Spruce Deep"""],
    9:  ['PjSha',  """ ((("Pj" >= 70) And (("Po" + "Pt") + "Bw" <=20)) Or (("Pj" >= 50) And (("Po" + "Pt") + "Bw" <=20) And ("Age" >=120))) And <user_defined_sfu_field_name> Is Null """,   """AND ("Ecosite_GeoRangeAndNumber" in ('B011', 'B012', 'B014', 'B015', 'B016', 'B017', 'B018', 'B019', 'B023', 'B024', 'B025', 'B026', 'B027', 'B028')) """ ,     """Jack Pine Shallow"""],
    10: ['PjDee',  """ ((("Pj" >= 70) And (("Po" + "Pt") + "Bw" <=20)) Or (("Pj" >= 50) And (("Po" + "Pt") + "Bw" <=20) And ("Age" >=120)) Or ("Pj" >=70 AND ("Ecosite_GeoRangeAndNumber" in ('B034', 'B035')))) And <user_defined_sfu_field_name> Is Null """,   "",     """Jack Pine Deep"""],
    11: ['PoSha',  """ (("Po" + "Pt") >= 70) And <user_defined_sfu_field_name> Is Null """,      """AND ("Ecosite_GeoRangeAndNumber" in ('B011', 'B012', 'B014', 'B015', 'B016', 'B017', 'B018', 'B019', 'B023', 'B024', 'B025', 'B026', 'B027', 'B028')) """,     """Poplar Shallow"""],
    12: ['PoDee',  """ (("Po" + "Pt") >= 70) And <user_defined_sfu_field_name> Is Null """,                              "",     """Poplar Deep"""],
    13: ['BwSha',  """ (("Bw" >= 60) And (("Po" + "Pt") + "Bw" >=70)) And <user_defined_sfu_field_name> Is Null """,    """AND ("Ecosite_GeoRangeAndNumber" in ('B011', 'B012', 'B014', 'B015', 'B016', 'B017', 'B018', 'B019', 'B023', 'B024', 'B025', 'B026', 'B027', 'B028')) """,     """Birch Shallow"""],
    14: ['BwDee',  """ (("Bw" >= 60) And (("Po" + "Pt") + "Bw" >=70)) And <user_defined_sfu_field_name> Is Null """,                    "",     """Birch Deep"""],
    15: ['OthHd',  """ ((("Po" + "Pt") + "Bw" + ("Mh" + "Mr" + "Ms" + "Ob" + "_Or") + ("Ab" + "Ew" + "Pb")) >= 30) And <user_defined_sfu_field_name> Is Null """,        "",     """Other Hardwood"""],
    16: ['SbMx1',  """ ((("Pr" + "Pw" + "Pj" + "Sb" + "Sw" + "La" + ("Cw" + "Ce") + "Bf") >= 70) And ("Bf" <= 10) And (("Po" + "Pt") + "Bw" <= 20) And (("Sb" + "Sw") > "Pj") And (("Sb" + "Sw" + "Pj") >=40)) And <user_defined_sfu_field_name> Is Null """,     "",     """Black Spruce Dominant Conifer Mix"""],
    17: ['PjMx1',  """ ((("Pr" + "Pw" + "Pj" + "Sb" + "Sw" + "La" + ("Cw" + "Ce") + "Bf") >= 70) And ("Bf" <= 10) And (("Po" + "Pt") + "Bw" <= 20) And (("Sb" + "Sw") <= "Pj") And (("Sb" + "Sw" + "Pj") >=40)) And <user_defined_sfu_field_name> Is Null """,     "",     """Jack Pine Dominant Conifer Mix"""],
	18: ['BfPur',  """ ("Bf" >= 70) And <user_defined_sfu_field_name> Is Null """,                    "",     """Balsam Fir Pure"""],
	19: ['BfMx1',  """ ((("Pr" + "Pw" + "Pj" + "Sb" + "Sw" + "La" + ("Cw" + "Ce") + "Bf") >= 70) And ("Bf" > 10) And (("Bf" + "Sw") >=30)) And <user_defined_sfu_field_name> Is Null """,                    "",     """Balsam Fir Conifer Mix"""],
	20: ['HdDom',  """ ((("Po" + "Pt") + "Bw" + ("Mh" + "Mr" + "Ms" + "Mx" + "Ob" + "_Or" + "Ox") + ("Ab" + "Ew" + "Pb")) >= 70) And <user_defined_sfu_field_name> Is Null """,                    "",     """Hardwood Dominant"""],
	21: ['HdMix',  """ ((("Po" + "Pt") + "Bw" + ("Mh" + "Mr" + "Ms" + "Mx" + "Ob" + "_Or" + "Ox") + ("Ab" + "Ew" + "Pb")) >= 50) And <user_defined_sfu_field_name> Is Null """,                    "",     """Hardwood Mix"""],
	22: ['ConMx',  """ (("Pr" + "Pw" + "Pj" + "Sb" + "Sw" + "La" + ("Cw" + "Ce") + "Bf") >= 50) And <user_defined_sfu_field_name> Is Null """,                    "",     """"""],


#  : ['',       """ () And <user_defined_sfu_field_name> Is Null """,                    "",     """"""],
#  : ['UDF',    """ ("POLYTYPE" = 'FOR') And <user_defined_sfu_field_name> Is Null """,  "",     """"""],

}


GLSL_SFU_SQL_V1_03_01_23 = {
# Todd and Alison fixing GLSL NER SQL stocking (from 0.30 to 30) March 1, 2023
# This is still work in progress as of Aug 2023
# I still cannot figure out where that 0.30 came from ...
# Also added an = to the PR SFU (PW <=30)
# Compared this syntax with Sam N's version"SFCOMP_AND_SFU_library_SQL_NER_GLSL_SFU_Nsiah_statement_suite_230301_1116.txt" and the only differencce is the added name of the forest unit at this point

# |Order |SFU     |SQL                   |SQL addition if Ecosite incorporated      |Official Standard Forest Unit Name

    1:  ['PR',     """ ("Pr" >= 70 and "Pw" <= 30) And <user_defined_sfu_field_name> Is Null """,     "", "Red Pine"],
    2:  ['PWUS4',  """ ("Pw" + "Pr" >= 50 and "Pw" > "Pr" and (("Pw" + "Pr") * "OSTKG" >= 30) and ("_Or"+ "Ob" +"Ow") < 20) And <user_defined_sfu_field_name> Is Null """,     "", "White Pine 4 Cut Uniform Shelterwood"],
    3:  ['PWOR',   """ (("Pw"+ "Pr" + "_Or" + "Ob" +"Ow" >= 50) and "Pw" >= ("_Or"+ "Ob" +"Ow") and ("Pw"+ "Pr" + "_Or" + "Ob" +"Ow") * "OSTKG" >= 30 and ("_Or"+ "Ob" +"Ow") >= 20) And <user_defined_sfu_field_name> Is Null """,     "", "White Pine Red Oak"],
    4:  ['PWUSC',  """ (("Pw" + "Pr" >= 30 AND ("Pw" + "Pr") * "OSTKG" >= 30 )  OR  ( ("Pw" >= "He" AND "Pw" >= "Sw") AND "Pw" > ("Ce" + "Cw") AND "Pw" >= "_Or" AND "Pw" + "Pr" >= 30 AND ("Pw"+ "Pr" + "Sw" + "He" + "_Or" + "Pj" + "Ce" +"Cw") * "OSTKG" >= 30 AND ("Pw"+ "Pr" + "Pj" + "Sw" + "Sb" + "Sr" + "Sx" + "He" + "Bf" + "Ce" + "Cw" +"La") >= 80 )) And <user_defined_sfu_field_name> Is Null """,      "", "White Pine Conifer Shelterwood"],
    5:  ['PWUSH',  """ (("Pw" >= "Pr" AND "Pw" + "Pr" >= 30 AND ("Pw" + "Pr") * "OSTKG" >= 30 )  OR  ( "Pw" >= "Pr" AND "Pw" >= "He" AND "Pw" >= "Sw" AND "Pw">("Ce" + "Cw") AND "Pw" >= "_Or" AND ("Pw" + "Pr") >= 30 AND ("Pw"+ "Pr" + "Sw" + "He" + "_Or" + "Pj" + "Ce" +"Cw") * "OSTKG" >= 30 AND ("Pw"+ "Pr" + "Pj" + "Sw" + "Sr" + "Sx" + "Sb" + "He" + "Bf" + "Ce" + "Cw" +"La")<80 )) And <user_defined_sfu_field_name> Is Null """,     "", "White Pine Hardwood Shelterwood"],
    6:  ['PWST',   """ (("Pw" + "Pr" >= 30) AND ("Pw" + "Pr" >= "He") AND ("Pw" + "Pr" >= "Sw") AND ("Pw" + "Pr" >= "Sb"+ "Sr" +"Sx") AND ("Pw" + "Pr" >= ("Ce" + "Cw")) AND ("Pw" + "Pr" >= "_OR")) And <user_defined_sfu_field_name> Is Null """,     "", "White Pine Seed Tree"],
    7:  ['PJ1',    """ (("Pj" >= 70) AND ("Mh"+ "Ab" + "Aw" + "Bd" + "Be" + "Ch" + "Ew" + "Iw" + "_OR" + "_BY" + "Ow" + "Ob" + "Po" + "Pt" + "Pb" + "Pl" + "Bw" + "Mr" + "Ms" + "Ax" + "Cb" + "Ex" + "Hi" +"Bn" <= 20)) And <user_defined_sfu_field_name> Is Null """,     "", "Jack Pine Pure"],
    8:  ['PJ2',    """ (((("Pj"+ "Sb" + "Sr" + "Sx" +"Pr" >= 70) OR (("Pj" >= 50) AND ("Pj"+ "Sb" + "Sr" + "Sx" + "Bf" + "Sw" + "He" + "Pw" + "Pr" + "Ce" + "Cw" +"La" >= 70) AND ("Bf"+ "Sw" + "He" + "Pw" + "Ce" + "Cw" +"La" <= 20))) AND ("Pj" >= "Sb"+ "Sr" +"Sx"))) And <user_defined_sfu_field_name> Is Null """,     "", "Jack Pine Conifer"],
    9:  ['HE',     """ ("He" >= 40) And <user_defined_sfu_field_name> Is Null """,     "", "Hemlock"],
    10: ['CE',     """ (("Ce" + "Cw" >= 40) AND (("Ce" + "Cw") >= "Sb"+ "Sr" + "Sx" + "La" +"Bf") AND ("Ow"+ "Ob" + "Ew" + "Iw" + "Ch" + "Mh" + "Ab" + "Aw" + "Bd" + "Be" + "_OR" + "_BY" + "Po" + "Pb" + "Pt" + "Pl" + "Bw" + "Mr" + "Ms" + "Ex" + "Cb" + "Ax" + "Hi" +"Bn"<30)) And <user_defined_sfu_field_name> Is Null """, """ AND "Ecosite_GeoRangeAndNumber" In ('G127', 'G128', 'G129', 'G222', 'G223', 'G224', 'G136', 'B127', 'B128', 'B129', 'B222', 'B223', 'B224', 'B136') """,      "", "Cedar"],
    11: ['SB',     """ (("Sb"+ "Sr" +"Sx" >= 80) AND ("Mh"+ "Aw" + "Bd" + "Be" + "Ch" + "Iw" + "_OR" + "Ow" + "Ob" + "_BY" + "Pr" + "Bn" + "Hi" +"Cb"=0) AND ("Pw" + "Pj" <= 10)) And <user_defined_sfu_field_name> Is Null """, """ and "Ecosite_GeoRangeAndNumber" In ('G127', 'G128', 'G129', 'G222', 'G223', 'G224', 'G136', 'B127', 'B128', 'B129', 'B222', 'B223', 'B224', 'B136') """,     "", "Black Spruce"],
    12: ['LC',     """ (("Sb"+ "Sx" + "Sr" + "Ce" + "Cw" +"La" >= 80) AND ("Mh"+ "Aw" + "Bd" + "Be" + "Ch" + "Iw" + "_OR" + "Ow" + "Ob" + "_BY" + "Pr" + "Cb" + "Hi" +"Bn"=0) AND ("Pw" + "Pj" <= 10))  And <user_defined_sfu_field_name> Is Null """, """AND "Ecosite_GeoRangeAndNumber" In ('G127', 'G128', 'G129', 'G222', 'G223', 'G224', 'G136', 'B127', 'B128', 'B129', 'B222', 'B223', 'B224', 'B136') """,     "", "Lowland Conifer Mixedwood"],
    13: ['SP1',    """ (("Sb"+ "Sw" + "Sr" + "Sx" + "Bf" + "Ce" + "Cw" + "La" + "Pw" + "Pj" + "Pr" +"He" >= 70) AND (("Bf"+ "Ce" + "Cw" + "Pw" + "La" + "Sw" +"He" <= 20) OR ("Pj" >= 30))) And <user_defined_sfu_field_name> Is Null """,     "", "Upland Spruce"],
    14: ['SF',     """ (("Sw"+ "Sr" + "Sb" + "Sx" + "Pw" + "Pr" + "Pj" + "Bf" + "Ce" + "Cw" + "La" +"He" >= 70)) And <user_defined_sfu_field_name> Is Null """,     "", "Spruce Fir"],
    15: ['BY',     """ ("_By" >= 40) And <user_defined_sfu_field_name> Is Null """,     "", "Yellow Birch"],
    16: ['OAK',    """ (("_OR" >= "Mh" + "Be") AND ("_OR" >= 30) AND ("_OR"+ "Mh" + "Aw" + "Ab" + "Be" + "Bd" + "_BY" + "Pw" + "Pr" + "Sw" + "He" +"Ax" >= 40)) And <user_defined_sfu_field_name> Is Null """,     "", "Red Oak"],
    17: ['HDSL2',  """ ((("Bd"+ "Aw" + "Ch" + "_OR" + "Ow" + "Ob" +"Cb" >= 30) OR (("Be"+ "_OR" + "Ow" +"Ob" >= 30) OR ("Be" >= 20)))) And <user_defined_sfu_field_name> Is Null """,     "", "Hardwood Selection South"],
    18: ['HDSL1',  """ (("Mh"+ "Aw" + "Bd" + "Be" + "Ch" + "Ew" + "Iw" + "_OR" + "_BY" + "Ow" + "Ob" + "He" + "Ex" +"Cb" >= 50) AND ("Po"+ "Pt" + "Pb" + "Pl" + "Bw" +"Bf" <= 30) AND ("OSC" <= 2)) And <user_defined_sfu_field_name> Is Null """,     "", "Hardwood Selection North"],
    19: ['LWMW',   """ (("Ce"+ "Cw" + "Ab" + "La" + "Sb" + "Ax" + "Sr" +"Sx" >= 30) AND (("Ab" + "Ax" >= 20) OR ("Ab"+ "Ax" + "Mr" + "Ms" +"_BY" >= 30))) And <user_defined_sfu_field_name> Is Null """, """AND "Ecosite_GeoRangeAndNumber" In ('G071', 'G120', 'G130', 'G131', 'G132', 'G133', 'B071', 'B120', 'B130', 'B131', 'B132', 'B133') """,     "", "Lowland Mixedwood"],
    20: ['HDUS',   """ (("Mh"+ "Aw" + "Bd" + "Be" + "Ch" + "Ew" + "Iw" + "_OR" + "_BY" + "Ow" + "Ob" + "He" + "Cb" + "Hi" + "Ex" +"Bn" >= 50)) And <user_defined_sfu_field_name> Is Null """,     "", "Hardwood Shelterwood"],
    21: ['PO',     """ (("Po"+ "Pt" + "Pb" +"Pl" >= 50) AND ("Mh"+ "Ab" + "Aw" + "Bd" + "Be" + "Ch" + "Ew" + "Iw" + "_OR" + "_BY" + "Ow" + "Ob" + "Po" + "Pb" + "Pt" + "Pl" + "Bw" + "Mr" + "Ms" + "Ax" + "Bn" + "Cb" + "Ex" +"Hi" >= 70)) And <user_defined_sfu_field_name> Is Null """,     "", "Poplar"],
    22: ['BW',     """ (("Po"+ "Pt" + "Pb" + "Pl" +"Bw" >= 50) AND ("Mh"+ "Ab" + "Aw" + "Bd" + "Be" + "Ch" + "Ew" + "Iw" + "_OR" + "_BY" + "Ow" + "Ob" + "Po" + "Pt" + "Pb" + "Pl" + "Bw" + "Mr" + "Ms" + "Ax" + "Bn" + "Cb" + "Ex" +"Hi" >= 70))  And <user_defined_sfu_field_name> Is Null """,     "", "White Birch"],
    23: ['MWUS',   """ ((("Sw"+ "Pw" + "Pr" + "Ce" + "Cw" + "Mh" + "_BY" + "Aw" + "Ch" + "Bd" + "_OR" + "Ow" + "Ob" + "Iw" + "Be" + "He" + "Cb" + "Hi" +"Bn") * "OSTKG" >= 30)) And <user_defined_sfu_field_name> Is Null """,     "", "Mixedwood Shelterwood"],
    24: ['MWD',    """ ("Pj"+ "Pw" +"Pr" >= 20) And <user_defined_sfu_field_name> Is Null """,     "", "Mixedwood Dry"],
    25: ['MWR',    """ ("POLYTYPE" = 'FOR') And <user_defined_sfu_field_name> Is Null """,     "", "Mixedwood Rich"]
}


NER_Boreal_SRNV2023_UPCE = {
# used during SRNV project of 2023 (Sam Nsiah, Gordon Kayahara, Jen Neilson)
# based on NER_Boreal_SRNV2023 which was based on NER_Boreal_v9_ROD2023
# addition of UPCE (upland cedar) forest unit

#   |Order   |SFU        |SQL                   |SQL addition if Ecosite incorporated               | SFU Descriptive Name

    1:  ['PR1',     """ ("Pr" >= 70) And <user_defined_sfu_field_name> Is Null """,            "",            """ Red pine, plantations """],
    2:  ['PW1',     """ ("Pw" + "Pr" + "He" + ("Sw" + "Sx") >= 40 And "Pw" >= 30) And <user_defined_sfu_field_name> Is Null """,           "",            """White pine, shelterwood"""],
    3:  ['PRW',     """ (("Pw" + "Pr" + "He" + ("Sw" + "Sx") >= 40) And ("Pw" + "Pr" >= 30)) And <user_defined_sfu_field_name> Is Null """,         "",            """Red and white pine"""],
    4:  ['LH1',     """ ("Ab" + "Ew" + "_By" >= 20 AND ("Ecosite_GeoRangeAndNumber" in ('B119', 'B120', 'B123', 'B129', 'B130', 'B131', 'B133', 'G119', 'G120', 'G123', 'G129', 'G130', 'G131', 'G133'))) Or ("Pb" >= 70) And <user_defined_sfu_field_name> Is Null """,          "",            """Lowland Hardwood"""],
    5:  ['TH1',     """ (("Ab" + "Ew") + "Mh" + ("_By" + "Mr") + "He" >= 30) And <user_defined_sfu_field_name> Is Null """,          "",             """Tolerant Hardwoods"""],
    6:  ['SBOG',    """ (("Sb" + "La" + ("Ce" + "Cw") >= 70) And ((("OSC" = 4) And ("Ecosite_GeoRangeAndNumber" in ('B126', 'B136','B137',  'G126', 'G136', 'G137'))))) And <user_defined_sfu_field_name> Is Null """,            "",             """Black spruce, bog"""],
    7:  ['SB1',     """ ((("Sb" >= 80)) And ("Ab" <= 10)  AND "Ecosite_GeoRangeAndNumber" in ('B127', 'B128', 'B129', 'B222', 'B223', 'B224', 'G127', 'G128', 'G129', 'G222', 'G223', 'G224')) And <user_defined_sfu_field_name> Is Null """,          "",             """Black spruce, lowland"""],
    8:  ['PJ1',     """ (((("Pj" >= 70) And (("Po" + "Pt") + "Bw" + ("_By" + "Mr") + "Mh" + ("Ab" + "Ew" + "Pb") <= 20)) And "Ecosite_GeoRangeAndNumber" in ('B012', 'B033', 'B034', 'B035', 'B048', 'B049', 'B050', 'G012', 'G033', 'G034', 'G035',  'G048', 'G049', 'G050')) Or ("Pj" >= 90)) And <user_defined_sfu_field_name> Is Null """,          "",             """Jack pine, pure"""],
    9:  ['LC1',     """ ((("Ce" + "Cw") + "La" + "Sb" + "Bf" + "Sw">= 70) AND ("Ecosite_GeoRangeAndNumber" in ('B127', 'B128', 'B129', 'B222', 'B223', 'B224', 'B136', 'B137', 'G127', 'G128', 'G129', 'G222', 'G223', 'G224', 'G136', 'G137'))) And <user_defined_sfu_field_name> Is Null """,           "",            """Lowland conifer"""],

    # addtion of UPCE
    10: ['UPCE',    """ ("Ce" + "Cw") >= 40 And <user_defined_sfu_field_name> Is Null """,           "",            """Upland Cedar"""],

    11: ['PJ2',     """ ((("Pj" + "Sb" + "Pr" + "Pw" >= 70) Or ("Pj" >= 30 And "Pj" + "Sb" + "Bf" + ("Sw" + "Sx") + "Pw" + "Pr" + ("Ce" + "Cw") + "La" >=70)) And (("Pj" + "Pw" + "Pr") >= ("Sb" + ("Sw" + "Sx") + ("Ce" + "Cw")))) And <user_defined_sfu_field_name> Is Null """,           "",             """Jack pine black spruce"""],
    12: ['SP1',     """ (("Sb" + ("Sw" + "Sx") + "Bf" + ("Ce" + "Cw") + "La" + "Pw" + "Pj" + "Pr" + "He">=70) And (("Bf" + ("Ce" + "Cw") + "Pw" + ("Sw" + "Sx") + "He" <= 20) Or ("Pj" + "Pr" + "La" >= 30)))  And <user_defined_sfu_field_name> Is Null """,           "",            """Spruce, upland"""],
    13: ['SF1',     """ ("Sb" + ("Sw" + "Sx") + "Bf" + ("Ce" + "Cw") + "La" + "Pw" + "Pj" + "Pr" >= 70) And <user_defined_sfu_field_name> Is Null """,          ""],
    14: ['PO1',     """ ((("Po" + "Pt" + "Pl") + "Bw" + "Mh" + ("_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 70) And (("Po" + "Pt" + "Pl" + "Pb") >= 50)) And <user_defined_sfu_field_name> Is Null """,          "",            """Poplar"""],
    15: ['BW1',     """ (("Po" + "Pt" + "Pl") + "Bw" + "Mh" + ("_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 70) And <user_defined_sfu_field_name> Is Null """,          "",            """White birch"""],
    16: ['MH1',     """ (((("Bf" <= 20 And ("Sw" + "Sx") <= 20 And ("Ce" + "Cw") <= 20) And ("Po" + "Pt" + "Pl") + "Bw" + "Mh" + ("_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 50) And ("Pj" + "Pr" <= 50 And "Pj" + "Pr" >= 20)) AND ("Ecosite_GeoRangeAndNumber" in ('B016', 'B019', 'B028', 'B040', 'B043', 'B055', 'B059', 'B070', 'B076',  'G016', 'G019', 'G028', 'G040', 'G043', 'G055', 'G059', 'G070', 'G076'))) And <user_defined_sfu_field_name> Is Null """,           "",            """Mixedwood hardwood fresh coarse"""],
    17: ['MC1',     """ ((("Bf" <= 20 And ("Sw" + "Sx") <= 20 And ("Ce" + "Cw") <= 20 And ("Pj" + "Pr" + "La") >= 20) AND ("Ecosite_GeoRangeAndNumber" in ('B012', 'B014', 'B035', 'B037', 'B038', 'B050', 'B052', 'B053', 'B065', 'B067', 'B068',  'G012', 'G014', 'G035', 'G037', 'G037', 'G050', 'G052', 'G053', 'G065', 'G067', 'G068')))  Or ("Pj" + "Pr" >= 50)) And <user_defined_sfu_field_name> Is Null """,           "",             """Mixedwood conifer fresh coarse"""],
    18: ['MH2',     """ (("Po" + "Pt" + "Pl") + "Bw" + "Mh" + ("_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 50) And <user_defined_sfu_field_name> Is Null """,          "",            """Mixedwood hardwood moist fine"""],
    19: ['MC2',     """ ("Sb" + ("Sw" + "Sx") + "Bf" + ("Ce" + "Cw") + "La" + "Pw" + "Pj" + "Pr" > 50) And <user_defined_sfu_field_name> Is Null """,          "",            """Mixedwood conifer moist fine"""],
    20: ['UDF',     """ ("POLYTYPE" = 'FOR') And <user_defined_sfu_field_name> Is Null """,            "",            """Undefined"""],

    22: ['SB1',     """ ("POLYTYPE" = 'FOR' And <user_defined_sfu_field_name> Is Null) """,            """OR (<user_defined_sfu_field_name> = 'SP1' AND "Ecosite_GeoRangeAndNumber" IN ('B126', 'B127', 'B128', 'B129', 'B136', 'B222', 'B223', 'B224'))"""], # The reason why I included the seemingly unnecessary first part of the SQL is because the tool has an option to NOT use Ecosite. if the user decides not to use Ecosite, only the first part of the SQL will be used and it will basically select nothing.
    23: ['LC1',     """ ("POLYTYPE" = 'FOR' And <user_defined_sfu_field_name> Is Null) """,            """OR (<user_defined_sfu_field_name> = 'SF1' AND "Ecosite_GeoRangeAndNumber" IN ('B126', 'B127', 'B128', 'B129', 'B136', 'B222', 'B223', 'B224'))"""],
    24: ['LH1',     """ (<user_defined_sfu_field_name> in ('TH1','PO1','BW1','MH1','MH2') AND "Ecosite_GeoRangeAndNumber" in ('B130','B131')) """,           ""],
    28: ['SP1',     """ (<user_defined_sfu_field_name> = 'SB1' AND "DEVSTAGE" in('NEWPLANT','ESTPLANT')) """,            ""],
    29: ['SP1',     """ (<user_defined_sfu_field_name> = 'SF1' AND "DEVSTAGE" in('NEWPLANT','ESTPLANT') AND ("Bf" + "La" <=20)) """,            ""],
    # 30: ['PRPW10',  """ ("POLYTYPE" = 'FOR' AND <user_defined_sfu_field_name> not in ('PR1','PRW','PW1') AND "PR"+"PW">=10) """,            ""],

    # added by Daniel to make sure there's no UDF (most UDFs happens in Algoma, NS and Sudbury, and they comprise less than 0.1% of the record count)
    # in English, for any UDFs, if combination of hardwood is greater than combination of conifers - it goes to MH2.  Otherwise, the rest goes to MC2
    41: ['MH2',     """ <user_defined_sfu_field_name> = 'UDF' AND ("Po" + "Pt" + "Pl") + "Bw" + ("Mh" + "Ms" + "Mr") + "_By" + ("Ab" + "Ew" + "Pb") + "OH" > "Sb" + ("Sw" + "Sx") + "Bf" + ("Ce" + "Cw") + "La" + "Pw" + "Pj" + "Pr" + "OC" """,            ""],
    42: ['MC2',     """ <user_defined_sfu_field_name> = 'UDF' """,            ""],
}



# NER_Boreal_SRNV2024_depricated = {
# # depricated because this creates too much LH1
# # Removed other refinements
# #   |Order   |SFU        |SQL                   |SQL addition if Ecosite incorporated               | SFU Descriptive Name
#     1:  ['PRW',     """ (("Pw" + "Pr" + "He" + ("Sw" + "Sx") >= 40) And ("Pw" + "Pr" >= 30)) And <user_defined_sfu_field_name> Is Null """,         "",            """Red and white pine"""],
#     2:  ['LH1',     """ ((("Ab" + "Ew" + "Pb" + "Mr" + "_By") >= 30) And (("Ab" + "Ew" + "_By" >= 20 OR "Ecosite_GeoRangeAndNumber" in ('B119', 'B120', 'B123', 'B129', 'B130', 'B131', 'B133', 'G119', 'G120', 'G123', 'G129', 'G130', 'G131', 'G133')) Or ("Pb" >= 70))) And <user_defined_sfu_field_name> Is Null """,          "",            """Lowland Hardwood"""],
#     3:  ['TH1',     """ (("Ab" + "Ew") + "Mh" + ("_By" + "Mr") + "He" >= 30) And <user_defined_sfu_field_name> Is Null """,          "",             """Tolerant Hardwoods"""],
#     4:  ['SBOG',    """ (("Sb" + "La" + ("Ce" + "Cw") >= 70) And ((("OSC" = 4) And ("Ecosite_GeoRangeAndNumber" in ('B126', 'B136','B137',  'G126', 'G136', 'G137'))))) And <user_defined_sfu_field_name> Is Null """,            "",             """Black spruce, bog"""],
#     5:  ['SB1',     """ (("Sb" >= 80 And "Ab" <= 10) OR (("Sb">=70) AND "Ecosite_GeoRangeAndNumber" in ('B127', 'B128', 'B129', 'B222', 'B223', 'B224', 'G127', 'G128', 'G129', 'G222', 'G223', 'G224'))) And <user_defined_sfu_field_name> Is Null """,          "",             """Black spruce, lowland"""],
#     6:  ['PJ1',     """ (("Pj" >= 70) And (("Po" + "Pt") + "Bw" + ("_By" + "Mr") + "Mh" + ("Ab" + "Ew" + "Pb") <= 20)) And <user_defined_sfu_field_name> Is Null """,          "",             """Jack pine, pure"""],
#     7:  ['LC1',     """ ((("Ce" + "Cw") + "La" + "Sb" + "Bf" + "Sw">= 70) AND ("Ecosite_GeoRangeAndNumber" in ('B127', 'B128', 'B129', 'B222', 'B223', 'B224', 'B136', 'B137', 'G127', 'G128', 'G129', 'G222', 'G223', 'G224', 'G136', 'G137'))) And <user_defined_sfu_field_name> Is Null """,           "",            """Lowland conifer"""],
#     8: ['UPCE',    """ ("Ce" + "Cw") >= 40 And <user_defined_sfu_field_name> Is Null """,           "",            """Upland Cedar"""],
#     9: ['PJ2',     """ ((("Pj" + "Sb" + "Pr" + "Pw" >= 70) Or ("Pj" >= 30 And "Pj" + "Sb" + "Bf" + ("Sw" + "Sx") + "Pw" + "Pr" + ("Ce" + "Cw") + "La" >=70)) And (("Pj" + "Pw" + "Pr") >= ("Sb" + ("Sw" + "Sx") + ("Ce" + "Cw")))) And <user_defined_sfu_field_name> Is Null """,           "",             """Jack pine black spruce"""],
#     10: ['SP1',     """ (("Sb" + ("Sw" + "Sx") + "Bf" + ("Ce" + "Cw") + "La" + "Pw" + "Pj" + "Pr" + "He">=70) And (("Bf" + ("Ce" + "Cw") + "Pw" + ("Sw" + "Sx") + "He" <= 20) Or ("Pj" + "Pr" + "La" >= 30)))  And <user_defined_sfu_field_name> Is Null """,           "",            """Spruce, upland"""],
#     11: ['SF1',     """ ("Sb" + ("Sw" + "Sx") + "Bf" + ("Ce" + "Cw") + "La" + "Pw" + "Pj" + "Pr" >= 70) And <user_defined_sfu_field_name> Is Null """,          ""],
#     12: ['PO1',     """ ((("Po" + "Pt" + "Pl") + "Bw" + "Mh" + ("_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 70) And (("Po" + "Pt" + "Pl" + "Pb") >= 50)) And <user_defined_sfu_field_name> Is Null """,          "",            """Poplar"""],
#     13: ['BW1',     """ (("Po" + "Pt" + "Pl") + "Bw" + "Mh" + ("_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 70) And <user_defined_sfu_field_name> Is Null """,          "",            """White birch"""],
#     14: ['MH1',     """ (((("Bf" <= 20 And ("Sw" + "Sx") <= 20 And ("Ce" + "Cw") <= 20) And ("Po" + "Pt" + "Pl") + "Bw" + "Mh" + ("_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 50) And ("Pj" + "Pr" <= 50 And "Pj" + "Pr" >= 20)) AND ("Ecosite_GeoRangeAndNumber" in ('B016', 'B019', 'B028', 'B040', 'B043', 'B055', 'B059', 'B070', 'B076',  'G016', 'G019', 'G028', 'G040', 'G043', 'G055', 'G059', 'G070', 'G076'))) And <user_defined_sfu_field_name> Is Null """,           "",            """Mixedwood hardwood fresh coarse"""],
#     15: ['MC1',     """ ((("Bf" <= 20 And ("Sw" + "Sx") <= 20 And ("Ce" + "Cw") <= 20 And ("Pj" + "Pr" + "La") >= 20) AND ("Ecosite_GeoRangeAndNumber" in ('B012', 'B014', 'B035', 'B037', 'B038', 'B050', 'B052', 'B053', 'B065', 'B067', 'B068',  'G012', 'G014', 'G035', 'G037', 'G037', 'G050', 'G052', 'G053', 'G065', 'G067', 'G068')))  Or ("Pj" + "Pr" >= 50)) And <user_defined_sfu_field_name> Is Null """,           "",             """Mixedwood conifer fresh coarse"""],
#     16: ['MH2',     """ (("Po" + "Pt" + "Pl") + "Bw" + "Mh" + ("_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 50) And <user_defined_sfu_field_name> Is Null """,          "",            """Mixedwood hardwood moist fine"""],
#     17: ['MC2',     """ ("Sb" + ("Sw" + "Sx") + "Bf" + ("Ce" + "Cw") + "La" + "Pw" + "Pj" + "Pr" > 50) And <user_defined_sfu_field_name> Is Null """,          "",            """Mixedwood conifer moist fine"""],
#     18: ['UDF',     """ ("POLYTYPE" = 'FOR') And <user_defined_sfu_field_name> Is Null """,            "",            """Undefined"""],

#     19: ['SP1',     """ (<user_defined_sfu_field_name> = 'SB1' AND "DEVSTAGE" in('NEWPLANT','ESTPLANT')) """,            ""],
#     20: ['SP1',     """ (<user_defined_sfu_field_name> = 'SF1' AND "DEVSTAGE" in('NEWPLANT','ESTPLANT') AND ("Bf" + "La" <=20)) """,            ""],
#     # added to make sure there's no UDF (most UDFs happens in Algoma, NS and Sudbury, and they comprise less than 0.1% of the record count)
#     # in English, for any UDFs, if combination of hardwood is greater than combination of conifers - it goes to MH2.  Otherwise, the rest goes to MC2
#     21: ['MH2',     """ <user_defined_sfu_field_name> = 'UDF' AND ("Po" + "Pt" + "Pl") + "Bw" + ("Mh" + "Ms" + "Mr") + "_By" + ("Ab" + "Ew" + "Pb") + "OH" > "Sb" + ("Sw" + "Sx") + "Bf" + ("Ce" + "Cw") + "La" + "Pw" + "Pj" + "Pr" + "OC" """,            ""],
#     22: ['MC2',     """ <user_defined_sfu_field_name> = 'UDF' """,            ""],
# }


NER_Boreal_SRNV2024 = {
# revised on May 13, 2024
# Changes from SRNV2023:
# SB1 revised to include Sb1>80 or SB>70 plus ecosite
# LH1 - removed BY and MR
# PJ queries - removed ecosite factors
# Removed some refinements that comes after UDF

#   |Order   |SFU        |SQL                   |SQL addition if Ecosite incorporated               | SFU Descriptive Name
    1:  ['PR1',     """ ("Pr" >= 70) And <user_defined_sfu_field_name> Is Null """,            "",            """ Red pine, plantations """],
    2:  ['PW1',     """ ("Pw" + "Pr" + "He" + ("Sw" + "Sx") >= 40 And "Pw" >= 30) And <user_defined_sfu_field_name> Is Null """,           "",            """White pine, shelterwood"""],
    3:  ['PRW',     """ (("Pw" + "Pr" + "He" + ("Sw" + "Sx") >= 40) And ("Pw" + "Pr" >= 30)) And <user_defined_sfu_field_name> Is Null """,         "",            """Red and white pine"""],
    4:  ['LH1',     """ (("Ab" + "Ew" >= 20 AND "Ecosite_GeoRangeAndNumber" in ('B119', 'B120', 'B123', 'B129', 'B130', 'B131', 'B133', 'G119', 'G120', 'G123', 'G129', 'G130', 'G131', 'G133')) Or "Pb" >= 70) And <user_defined_sfu_field_name> Is Null """,          "",            """Lowland Hardwood"""],
    5:  ['TH1',     """ (("Ab" + "Ew") + "Mh" + ("_By" + "Mr") + "He" >= 30) And <user_defined_sfu_field_name> Is Null """,          "",             """Tolerant Hardwoods"""],
    6:  ['SBOG',    """ (("Sb" + "La" + ("Ce" + "Cw") >= 70) And ((("OSC" = 4) And ("Ecosite_GeoRangeAndNumber" in ('B126', 'B136','B137',  'G126', 'G136', 'G137'))))) And <user_defined_sfu_field_name> Is Null """,            "",             """Black spruce, bog"""],
    7:  ['SB1',     """ (("Sb" >= 80 And "Ab" <= 10) OR (("Sb">=70) AND "Ecosite_GeoRangeAndNumber" in ('B127', 'B128', 'B129', 'B222', 'B223', 'B224', 'G127', 'G128', 'G129', 'G222', 'G223', 'G224'))) And <user_defined_sfu_field_name> Is Null """,          "",             """Black spruce, lowland"""],
    8:  ['PJ1',     """ (("Pj" >= 70) And (("Po" + "Pt") + "Bw" + ("_By" + "Mr") + "Mh" + ("Ab" + "Ew" + "Pb") <= 20)) And <user_defined_sfu_field_name> Is Null """,          "",             """Jack pine, pure"""],
    9:  ['LC1',     """ ((("Ce" + "Cw") + "La" + "Sb" + "Bf" + "Sw">= 70) AND ("Ecosite_GeoRangeAndNumber" in ('B127', 'B128', 'B129', 'B222', 'B223', 'B224', 'B136', 'B137', 'G127', 'G128', 'G129', 'G222', 'G223', 'G224', 'G136', 'G137'))) And <user_defined_sfu_field_name> Is Null """,           "",            """Lowland conifer"""],
    10: ['UPCE',    """ ("Ce" + "Cw") >= 40 And <user_defined_sfu_field_name> Is Null """,           "",            """Upland Cedar"""],
    11: ['PJ2',     """ ((("Pj" + "Sb" + "Pr" + "Pw" >= 70) Or ("Pj" >= 30 And "Pj" + "Sb" + "Bf" + ("Sw" + "Sx") + "Pw" + "Pr" + ("Ce" + "Cw") + "La" >=70)) And (("Pj" + "Pw" + "Pr") >= ("Sb" + ("Sw" + "Sx") + ("Ce" + "Cw")))) And <user_defined_sfu_field_name> Is Null """,           "",             """Jack pine black spruce"""],
    12: ['SP1',     """ (("Sb" + ("Sw" + "Sx") + "Bf" + ("Ce" + "Cw") + "La" + "Pw" + "Pj" + "Pr" + "He">=70) And (("Bf" + ("Ce" + "Cw") + "Pw" + ("Sw" + "Sx") + "He" <= 20) Or ("Pj" + "Pr" + "La" >= 30)))  And <user_defined_sfu_field_name> Is Null """,           "",            """Spruce, upland"""],
    13: ['SF1',     """ ("Sb" + ("Sw" + "Sx") + "Bf" + ("Ce" + "Cw") + "La" + "Pw" + "Pj" + "Pr" >= 70) And <user_defined_sfu_field_name> Is Null """,          ""],
    14: ['PO1',     """ ((("Po" + "Pt" + "Pl") + "Bw" + "Mh" + ("_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 70) And (("Po" + "Pt" + "Pl" + "Pb") >= 50)) And <user_defined_sfu_field_name> Is Null """,          "",            """Poplar"""],
    15: ['BW1',     """ (("Po" + "Pt" + "Pl") + "Bw" + "Mh" + ("_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 70) And <user_defined_sfu_field_name> Is Null """,          "",            """White birch"""],
    16: ['MH1',     """ (((("Bf" <= 20 And ("Sw" + "Sx") <= 20 And ("Ce" + "Cw") <= 20) And ("Po" + "Pt" + "Pl") + "Bw" + "Mh" + ("_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 50) And ("Pj" + "Pr" <= 50 And "Pj" + "Pr" >= 20)) AND ("Ecosite_GeoRangeAndNumber" in ('B016', 'B019', 'B028', 'B040', 'B043', 'B055', 'B059', 'B070', 'B076',  'G016', 'G019', 'G028', 'G040', 'G043', 'G055', 'G059', 'G070', 'G076'))) And <user_defined_sfu_field_name> Is Null """,           "",            """Mixedwood hardwood fresh coarse"""],
    17: ['MC1',     """ ((("Bf" <= 20 And ("Sw" + "Sx") <= 20 And ("Ce" + "Cw") <= 20 And ("Pj" + "Pr" + "La") >= 20) AND ("Ecosite_GeoRangeAndNumber" in ('B012', 'B014', 'B035', 'B037', 'B038', 'B050', 'B052', 'B053', 'B065', 'B067', 'B068',  'G012', 'G014', 'G035', 'G037', 'G037', 'G050', 'G052', 'G053', 'G065', 'G067', 'G068')))  Or ("Pj" + "Pr" >= 50)) And <user_defined_sfu_field_name> Is Null """,           "",             """Mixedwood conifer fresh coarse"""],
    18: ['MH2',     """ (("Po" + "Pt" + "Pl") + "Bw" + "Mh" + ("_By" + "Mr") + ("Ab" + "Ew" + "Pb") >= 50) And <user_defined_sfu_field_name> Is Null """,          "",            """Mixedwood hardwood moist fine"""],
    19: ['MC2',     """ ("Sb" + ("Sw" + "Sx") + "Bf" + ("Ce" + "Cw") + "La" + "Pw" + "Pj" + "Pr" > 50) And <user_defined_sfu_field_name> Is Null """,          "",            """Mixedwood conifer moist fine"""],
    20: ['UDF',     """ ("POLYTYPE" = 'FOR') And <user_defined_sfu_field_name> Is Null """,            "",            """Undefined"""],

    21: ['SP1',     """ (<user_defined_sfu_field_name> = 'SB1' AND "DEVSTAGE" in('NEWPLANT','ESTPLANT')) """,            ""],
    22: ['SP1',     """ (<user_defined_sfu_field_name> = 'SF1' AND "DEVSTAGE" in('NEWPLANT','ESTPLANT') AND ("Bf" + "La" <=20)) """,            ""],
    # added to make sure there's no UDF (most UDFs happens in Algoma, NS and Sudbury, and they comprise less than 0.1% of the record count)
    # in English, for any UDFs, if combination of hardwood is greater than combination of conifers - it goes to MH2.  Otherwise, the rest goes to MC2
    23: ['MH2',     """ <user_defined_sfu_field_name> = 'UDF' AND ("Po" + "Pt" + "Pl") + "Bw" + ("Mh" + "Ms" + "Mr") + "_By" + ("Ab" + "Ew" + "Pb") + "OH" > "Sb" + ("Sw" + "Sx") + "Bf" + ("Ce" + "Cw") + "La" + "Pw" + "Pj" + "Pr" + "OC" """,            ""],
    24: ['MC2',     """ <user_defined_sfu_field_name> = 'UDF' """,            ""],
}



if __name__ == '__main__':
    for k,v in NER_Boreal_SRNV2024.items():
        sql = v[1]
        sql = sql.replace("<user_defined_sfu_field_name>","SFU")
        sql = sql.replace("Ecosite_GeoRangeAndNumber","EcoNum")
        print("%s: %s"%(v[0],sql))
