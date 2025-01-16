version = '2.0'
debug = False # when debug = True, the tool won't overwrite inputfc but instead will create a copy on the default gdb

# also, it would be nice to have the script validate all the SQLs before running the full script
#
#-------------------------------------------------------------------------------
# Name:        Populate Forest Unit
# Purpose:
#
# Author:      D. Kim
# Contributer: T. Little, S. Nsiah
#
# Changes Documentation:
#   2023-09-05  D. kim      Major Update (v2 update):
#                            - The tool doesn't create copies anymore. it changes the original data
#                            - Can run and populate multiple forest unit types at once
#                            - addition of log file
#   2018-01-22  littleto    Add additional options to the typeLookup dict
#   2018-01-22  littleto    Correct the sorted order for the processing of the SQL criteria suite
#                               to "reverse = False"
#   2018-01-22  littleto    Add the replace string to incorperate "<user_defined_sfu_field_name>" for "Is
#                               Not Null" type interpretations in SQL criteria suite
#   2018-01-23  littleto    Add arc message to document script source file path for ArcMap users
#   2018-01-23  littleto    Add custom field name for AGE. Required for "NER_Boreal_SFU_TN021".
#                               - This requires update to the arguments for the "Main" function: AGEfield = "OAGE"
#                               - This required update to the ArcGIS toolbox
#   2018-01-23  littleto    Elaborte on script comments throughout.
#   2018-12-10  kimdan      replaced <user_defined_spcomp_field_name> with <user_defined_sfu_field_name>
#                           Now the tool prints out the final count of the newly created forest units, and the number of records and area for each fu.
#
#-------------------------------------------------------------------------------

import arcpy
import os, traceback
from library import ForestUnit_SQL as libSQL
from library import ForestUnit_SQL_SR_Only as libSQL_SR
from messages import print2
from messages import output
from datetime import datetime


def main(inputfc, forestunittype, typeLookup, OSCfield = "OSC", OSTKGfield = "OSTKG", useecosite = 'false', AGEfield = "OAGE"):

    # start logging
    starttime = datetime.now()
    msg = print2('Start of process: %(start)s.' %{'start':starttime.strftime('%Y-%m-%d %H:%M:%S')})

    # during debug, the tool will create a copy of the inventory instead of overwriting existing fc
    if debug:
        msg += print2("**DEBUG MODE**\nCopying the input to the output location...")
        desc = arcpy.Describe(inputfc)
        outpath = desc.path
        msg += print2("outpath: %s"%outpath)
        outname = os.path.split(inputfc)[1] + "_" + rand_alphanum_gen(4)
        arcpy.FeatureClassToFeatureClass_conversion(inputfc,outpath,outname)
        inputfc = os.path.join(outpath,outname)
        msg += print2("output file saved here: %s"%inputfc)

    # Documents the location of the __Main__ file.
    msg += print2("Populate Forest Unit version %s"%version)
    msg += print2("Script source: " + os.path.abspath(__file__))

    # get forest unit type list
    forestunittype_lst = forestunittype.replace("'","").split(";") # eg. ['NER Boreal SFU TN021', 'NER Boreal SFU', 'Eco3E Seven Spc Groups']
    msg += print2("\nForest Unit Type Used: %s"%forestunittype_lst)

    # examining existing fields - Need POLYTYPE field and at least one of SC or OSC field
    msg += print2("Checking if the input file has the mandatory fields: POLYTYPE and (OSC or SC).")
    existingFields = [str(f.name).upper() for f in arcpy.ListFields(inputfc)]

    if 'POLYTYPE' not in existingFields:
        arcpy.AddError("\nPOLYTYPE field does not exist in your input data.\n")
        raise Exception("POLYTYPE field not found in the input table.")

    # If ecosite incorporated, add a field to templyr and populate it with the portion of the ecoiste used in the sql
    if useecosite == 'true':
        if 'PRI_ECO' in existingFields:
            ecositeField = "PRI_ECO"
        elif 'ECOSITE1' in existingFields:
            ecositeField = "ECOSITE1"
        else:
            arcpy.AddError("\nECOSITE1 or PRI_ECO field does not exist in your input data.\n")
            raise Exception("ECOSITE1 or PRI_ECO field not found in the input table.")

        newEcoField = 'Ecosite_GeoRangeAndNumber'
        if newEcoField.upper() not in existingFields:
            arcpy.MakeFeatureLayer_management(inputfc,"templyr_eco")
            msg += print2("Populating Ecosite_GeoRangeAndNumber Field...")
            arcpy.AddField_management(in_table = "templyr_eco", field_name = newEcoField, field_type = "TEXT", field_length = "10")
            arcpy.SelectLayerByAttribute_management("templyr_eco", "NEW_SELECTION", ' "' + ecositeField + '" IS NOT NULL ')
            arcpy.CalculateField_management("templyr_eco", newEcoField, "!" + ecositeField + "![:4]", "PYTHON_9.3")
        else:
            msg += print2("Ecosite_GeoRangeAndNumber field already exists. Will use the existing Ecosite_GeoRangeAndNumber values.")
    else:
        msg += print2("\n WARNING: Some FU SQLs works only if you check the 'Use Ecosite' box!\n")


    # create a temporary layer file - this layer will be used for selecting and calculating field until finally being exported to a real feature class.
    msg += print2("Creating a temporary layer...")
    arcpy.MakeFeatureLayer_management(inputfc,"templyr")


    # looping through different forest unit types
    summary = {k:'Successfully Run!' for k in forestunittype_lst}
    for fu_type in forestunittype_lst:
        msg += print2("\n    ###############    \nWorking on %s"%fu_type)
        try:
            fuType_dict = eval(typeLookup[fu_type])

            # new in 2019
            if fu_type == "NER Boreal SFU":
                if 'DEVSTAGE' not in existingFields:
                    arcpy.AddError("\nDEVSTAGE field is required to populate NER Boreal SFU. \n")
                    raise Exception("DEVSTAGE field is required to populate NER Boreal SFU.")

            # create a new field
            # the name should be the same as the type of the standard forest unit
            newSFU_Field = fu_type.replace(" ","_")
            if useecosite == 'true': newSFU_Field = newSFU_Field + "_wEco" # used to be + "_withEcosite"
            # if the field already exists, then put random suffix
            if newSFU_Field.upper() in existingFields:
                random_suffix = rand_alphanum_gen(4)
                msg += print2("\n%s field already exists."%newSFU_Field,'warning')
                newSFU_Field = '%s_%s'%(newSFU_Field, random_suffix)
                msg += print2("\nInstead of overwriting values in this field, will create a new field called %s"%newSFU_Field,'warning')

            msg += print2("Creating a new field: %s"%newSFU_Field)
            arcpy.AddField_management(in_table = "templyr", field_name = newSFU_Field, field_type = "TEXT", field_length = "10")
            existingFields.append(newSFU_Field)



            # select by attribute and calculate field
            msg += print2("Selecting and calculating field...")
            for k, v in sorted(fuType_dict.items(),reverse = False): ## without sorted function, the order will be incorrect.

                # if useecosite is True, incorporate ecosite in the SQL
                if useecosite == 'false':
                    sql = v[1]
                else:
                    sql = v[1] + v[2]

                # if the SQL contains the string "<user_defined_sfu_field_name>" replace it with the user-defined field name in the SQL criteria.
                sql = sql.replace("<user_defined_sfu_field_name>","\"" + newSFU_Field + "\"")

                # if custom field names are used for AGE
                if AGEfield not in [None,'AGE','']:
                    sql = sql.replace('"AGE"', '"' + AGEfield + '"')

                # if custom field names are used for OSC and OSTKG
                if OSCfield not in [None,'OSC','']:
                    sql = sql.replace('"OSC"', '"' + OSCfield + '"')
                if OSTKGfield not in [None,'OSTKG','']:
                    sql = sql.replace('"OSTKG"', '"' + OSTKGfield + '"')

                # new in Apr 2019
                if fu_type == "NER Boreal SFU SubAU" and "LEADSPC" not in existingFields:
                    if "OLEADSPC" in existingFields:
                        sql = sql.replace('LEADSPC', 'OLEADSPC')

                # Select and calcualte field
                msg += print2("%s - SQL used:  %s"%(v[0],sql))
                try:
                    arcpy.SelectLayerByAttribute_management("templyr", "NEW_SELECTION", sql)
                except:
                    arcpy.AddError("\nThere was an error during Select By Attribute process. Make sure that you've run the SPCOMP Parser previous to running this tool.\n")
                    raise Exception("There was an error during Select By Attribute process. Make sure that you've run the SPCOMP Parser previous to running this tool.")            

                # quick count
                selection_count = arcpy.GetCount_management("templyr")
                msg += print2('%s - records selected: %s\n'%(v[0], selection_count))

                # populating the new forest unit
                arcpy.CalculateField_management("templyr", newSFU_Field, "'" + v[0] + "'", "PYTHON_9.3")

            # clear selection
            arcpy.SelectLayerByAttribute_management("templyr", "CLEAR_SELECTION")

            # final count and area
            msg += print2('Summarizing the results...')
            sfu_set = set([v[0] for k, v in fuType_dict.items()]) # using set because some sfu such as LH1 is calculated more than once in Boreal SFU.
            summary_dict = {}
            for sfu in sfu_set:
                sql = '"' + newSFU_Field + '" = ' + "'" + sfu + "'"
                count = 0
                area = 0.0

                with arcpy.da.SearchCursor("templyr",["Shape_Area"],sql) as cursor:
                    for row in cursor:
                        count += 1
                        area += row[0]

                summary_dict[sfu] = [count, int(area)]

            # printing out the final count
            msg += print2('SFU, Count, Area')
            for k,v in summary_dict.items():
                msg += print2('%s, %s, %s'%(k,v[0],v[1]))

            # clear selection
            arcpy.SelectLayerByAttribute_management("templyr", "CLEAR_SELECTION")

            msg += print2("\nExamine the %s field to see the new forest units generated by this tool.\n"%newSFU_Field)

        except:
            # if any error encountered, log it, but MOVE ON
            var = traceback.format_exc()
            msg += print2(var,'warning')
            summary[fu_type] = 'Failed! Scroll up to see error/warning messages'

    # add summary messages
    msg += print2("\n\nSUMMARY:")
    for k,v in summary.items():
            msg += print2("%s - %s"%(k,v))
    msg += print2("\n")

    # Write 'msg' the log file to the output folder
    ## Create the output path, considering whether or not the feature class is in a file geodatabase folder or not.
    desc = arcpy.Describe(inputfc)
    folder_path = desc.path 
    while arcpy.Describe(folder_path).dataType != 'Folder':
        folder_path = os.path.split(folder_path)[0]
    ## Create the output file name for the log
    outfile = os.path.split(inputfc)[1] + '_FU-log_' + datetime.now().strftime('%Y_%m_%d_%H%M') + '.txt'
    # Create the log file.
    output(folder_path, outfile, msg)



def rand_alphanum_gen(length):
    """
    Generates a random string (with specified length) that consists of A-Z and 0-9.
    """
    import random, string
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(length))




if __name__ == '__main__':
    arcinputfc = arcpy.GetParameterAsText(0)                # toolbox input feature class
    arcforestunittype = str(arcpy.GetParameterAsText(1))    # selection of the forest unit SQL criteria suite (see "typeLookup" above) eg. 'NER Boreal SFU TN021';'NER Boreal SFU'
    arcOSCfield = str(arcpy.GetParameterAsText(2)).upper()        # selection of a custom site class field from the input feature class
    arcOSTKGfield = str(arcpy.GetParameterAsText(3)).upper()        # optional: not mandatory if boreal SFU. selection of a custom stocking field from the input feature class
    arcuseecosite = str(arcpy.GetParameterAsText(4))        # use the parameter type "boolean" in arc tool - it will give 'true' or 'false'
    try:
        arcAGEfield = str(arcpy.GetParameterAsText(5)).upper()          # optional: selection of a custom age field from the input feature class
    except:
        raise Exception("You may not be using the most recent version of the tool. Try restarting your ArcMap to load the most recent version.")



    # based on forest unit type, different SQL dictionary will be used
    typeLookup = {"NER Boreal SFU TN021"                   : "libSQL.NER_Boreal_SFU_TN021",                   # Original official version
                  "NER Boreal SFU"                         : "libSQL.NER_Boreal_SFU",                         # Original official version
                  "NER Boreal Revised SFU 2019 v9"         : "libSQL.NER_Boreal_Revised_SFU_2019_v9",         # Growth and Yield Program, NER SFU revision project (Todd Little, John Parton)
                  "NER_Boreal_v9_ROD2023"                  : "libSQL.NER_Boreal_v9_ROD2023",                  # Sam's version 2023
                  "NER_Boreal_SRNV2024"                    : "libSQL.NER_Boreal_SRNV2024",                    
                  "NER_Boreal_SRNV2023_UPCE"               : "libSQL.NER_Boreal_SRNV2023_UPCE",               # addtion of upland cedar UPCE (2023-09)
                  "NER_Boreal_SRNV_SPCOMP_ONLY"            : "libSQL.NER_Boreal_SRNV_SPCOMP_ONLY",            # almost same as v9 but only uses SPCOMP (doesn't use ecosite)
                  "SR GLSL LG SFU"                         : "libSQL_SR.SR_GLSL_LG_SFU",                      # added in 2023 by Glen Watt. Matches the SQL in Kun's tool
                  "GLSL SFU SQL v1"                        : "libSQL.GLSL_SFU_SQL_V1_03_01_23"                # This is the starting point for the ROD GY GLSL SFU revision project task team
                  }



    main(arcinputfc, arcforestunittype, typeLookup, arcOSCfield, arcOSTKGfield, arcuseecosite, arcAGEfield)

