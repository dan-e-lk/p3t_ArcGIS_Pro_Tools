#-------------------------------------------------------------------------------
# Name:         SPCOMP_Parser V2
# Purpose:      This tool can be used to check the FU.
#               It makes a copy of a BMI or PCI, creates new fields for every possible species,
#               and translates the SPCOMP into species percentages.
#
# Author:      kimdan and littleto
#
# Created:     25/09/2017
# Copyright:   (c) kimdan & littleto 2017
#
#   Date        Person      Description of change
# ----------    -------     ---------------------
# 2018-03-26    littleto    Add 'SppOccurList' to list the species that actually have occurance in the
#                               inventory, and print the the ArcTool box window as a python list.
# 2018-03-26    littleto    Changes the messages to include them in a log file, and write the log file.
#                               This uses the 'print2' and 'output' functions in the 'messages' module.
#                               Add the datetime module.
# 2018-03-27    littleto    Improve robustness of the output of log to consider file geodatabases.
# 2018-03-27    littleto    Add process times for log file.
# 2018-04-17    littleto    Add species occurance counter
# 2018-04-24    littleto    Add Comments and 'SC' to underscored species in 'completeFldList' in conjunction with change to Reference.py to add 'SC': Picea Pungens or Colorada (blue) spruce.
# 2019-08-08    kimdan      Added an option to not create species fields if that species doesn't exist in the inventory
# 2025-01-10    kimdan      Script run speed is significantly faster by first exporting empty fc, populating fields, then appending original data.
#-------------------------------------------------------------------------------

import Reference as R # Reference.py should be located in the same folder as this file.
import arcpy, os
from messages import print2
from messages import output
from datetime import datetime


### setting the workspace
##arcpy.env.workspace = os.path.split(outputfc)[0]

def spParse(inputfc,outputfc,spfield,create_all_spcfields = True):
    # Mark start time
    starttime = datetime.now()
    msg = print2('Start of process: %(start)s.' %{'start':starttime.strftime('%Y-%m-%d %H:%M:%S')})

    # Copy the input bmi to the location of choice
    msg += print2("Making a copy of the input feature class... \n\tInput: %(infc)s\n\tOutput: %(outfc)s\n\tSpecies field: %(species_field)s" %{'infc':inputfc, 'outfc':outputfc, 'species_field':spfield})
    oid_fieldname = arcpy.Describe(inputfc).OIDFieldName
    select_none_sql = "%s<0"%oid_fieldname # "OBJECTID < 0" will select zero records # new in v2
    # copy input to output - note that zero record are copied over. This will significantly speed up the AddField process
    arcpy.FeatureClassToFeatureClass_conversion(in_features=inputfc, out_path=os.path.split(outputfc)[0], out_name=os.path.split(outputfc)[1], where_clause=select_none_sql)

    existingFields = [str(f.name).upper() for f in arcpy.ListFields(outputfc)]

    # Create a complete list of species and the corresponding list of field names
    completeSpList = R.SpcListInterp + R.SpcListOther # this is our complete species list.
    completeSpList.sort()

    # the following code block is used to generate the list of fields which will be created in the next portion of the script.
    if not create_all_spcfields:
        import re
        msg += print2("Creating the list of existing species by going through all %s values..."%spfield)
        full_spcomp = []
        with arcpy.da.SearchCursor(inputfc, [spfield]) as cursor:
            for row in cursor:
                if row[0] not in [None, '']:
                    s1 = row[0].upper()
                    s2 = re.sub(r'[^A-Z]+', r' ', s1) # strip all text except A-Z
                    full_spcomp.append(s1) # e.g. 'CE    PJ'

        splist2search = list(completeSpList) # starts with complete list and the list will get smaller as we find existing species.
        existing_splist = []
        for spcomp in full_spcomp:
            for s in splist2search:
                if s in spcomp:
                    existing_splist.append(s)
                    splist2search.pop(splist2search.index(s))

        del full_spcomp
        existing_splist.sort()
        completeFldList = list(existing_splist)
        msg += print2("existing species list: %s"%completeFldList)

    else: # create all possible species fields
        completeFldList = list(completeSpList) #  this will clone the list

    # replaces some items in completeFldList because some of the species names are reserved names in ArcMap.
    for name in ['BY','OR','SC']:
        if name in completeFldList:
            completeFldList[completeFldList.index(name)] = '_' + name  # so 'BY' is replaced by '_BY'

    # creating fields
    for sp in completeFldList:
        if sp not in existingFields:
            msg += print2("Creating a new field: %s"%sp)
            arcpy.AddField_management(in_table = outputfc, field_name = sp, field_type = "SHORT")
        else:
            msg += print2("Creating a new field: %s - field already exists!"%sp)

    completeSpcFldList = completeFldList[:] # .copy() doesn't work in python2

    # Creating other fields
    check_field = 'SPC_Check'
    completeFldList.append(check_field)
    if check_field not in existingFields:
        msg += print2("Creating a new field: %s"%check_field)
        arcpy.AddField_management(in_table = outputfc, field_name = check_field, field_type = "TEXT", field_length = "150")
    completeFldList.append(spfield)


    # append the input records to the currently empty outputfc # new in v2
    recordCount = int(arcpy.management.GetCount(inputfc)[0])
    msg += print2("\n\nAppending %s records from input to output feature class."%recordCount)
    arcpy.management.Append([inputfc], outputfc, "NO_TEST")

    # populate zeros for all the newly created fields
    msg += print2("Populating the newly created fields with default zero...")
    with arcpy.da.UpdateCursor(outputfc, completeSpcFldList) as cursor:
        for row in cursor:
            for i in range(len(completeSpcFldList)):
                row[i] = 0
            cursor.updateRow(row)  ## Now all the newly populated fields are zero by default


    # Record the complete list of species
    msg += print2("\nThe complete list of all FRI tech spec species:\n%s" %completeSpList)  ## Print the unique list of species with occurances in the inventory.
    msg += print2("**Note that the field names for BY, OR and SC are _BY, _OR and _SC.")

    SppOccurSet = set()    ## Create a set to contain a unique list of species with occurances in the inventory.
    SppOccurDict = dict()   ## Create a dictionary to contain a count of the species occurances in the inventory.

    sppErrorCount = 0  ## If the spcomp value is invalid, count them.
    recordCount = 0 ## just to count the number of records
    spcompPopulCount = 0  ## number of records with spcomp value populated.

    print2("\nPopulating species fields with percentage values...")
    f = completeFldList
    with arcpy.da.UpdateCursor(outputfc, f) as cursor:
        for row in cursor:
            recordCount += 1

            if row[f.index(spfield)] not in [None, '', ' ']: ## if SPCOMP field is none, the spcVal function won't work
                spcompPopulCount += 1
                ValResult = R.spcVal(row[f.index(spfield)],spfield) ## ValResult example: ["Pass", {'AX':60,'CW':40}]
            
                if ValResult[0] != "Error":
                    for k, v in ValResult[1].items():
                        k = str(k) ## we don't want unicode
                        try:
                            row[f.index(k)] = v ## for example, k = 'AX' and v = 60
                        except:
                            row[f.index("_" + k)] = v ## for field names such as _BY

                        SppOccurSet.add(k)         ## Once the species code and value 'passes' add that species to the species occurance list.

                        if k in SppOccurDict: # modified to work in python 3
                            SppOccurDict[k] += 1    ## Once the species code and value 'passes; add that species to the speciec orrurance list and increment count by one.
                        else:
                            SppOccurDict[k] = 1

                    row[f.index(check_field)] = "Pass"

                else:
                    sppErrorCount += 1
                    row[f.index(check_field)] = "%s: %s"%(ValResult[0], ValResult[1])
            cursor.updateRow(row)

    # list of species with occurrences
    SppOccurList = list(SppOccurSet)
    SppOccurList.sort()
    msg += print2("\nThe list of %s species with occurrences in the inventory:\n%s" %(spfield,SppOccurList))   ## Print the unique list of species with occurrences in the inventory.


    # table of spc and its occurrences
    if len(SppOccurDict) > 0:
        SppOccrCsv = '%s Species,Occurences'%spfield
        # for spc, occ in sorted(SppOccurDict.items(), key=lambda (k,v): (v,k), reverse=True): # sort by the order of most commonly occurred to least. failed with python3
        for spc, occ in sorted(SppOccurDict.items(), key=lambda item: item[1], reverse=True): # updated for python3
            SppOccrCsv += '\n' + spc + ',' + str(occ)
        SppOccrCsv += '\n'
        msg += print2("\nThe list of species with occurrences in the inventory:\n%s" %SppOccrCsv)   ## Print the table of species and occurrences in the inventory.


    # Report errors
    msg += print2("Total Number of Records: %s"%recordCount)
    msg += print2("Number of records with %s populated: %s"%(spfield,spcompPopulCount))
    if sppErrorCount > 0:
        msg += print2("Number of errors found in %s field: %s"%(spfield,sppErrorCount),  msgtype = 'warning')


    # Mark end time
    endtime = datetime.now()
    msg += print2('End of process: %(end)s.' %{'end':endtime.strftime('%Y-%m-%d %H:%M:%S')})
    msg += print2('Duration of process: %(duration)s seconds.' %{'duration':(endtime - starttime).total_seconds()})


    # Write 'msg' the log file to the output folder
    ## Create the output path, considering whether or not the feature class is in a file geodatabase folder or not.
    ## folder path contining the workspace
    folder_path = outputfc
    while arcpy.Describe(folder_path).dataType != 'Folder':
        folder_path = os.path.split(folder_path)[0]

    ## Create the output file name for the log
    outfile = os.path.split(outputfc)[1] + '_SPC-log_' + datetime.now().strftime('%Y_%m_%d_%H%M') + '.txt'


    # Create the log file.
    output(folder_path, outfile, msg)

if __name__ == '__main__':
    arcinputfc = arcpy.GetParameterAsText(0) # this should be bmi or pci
    arcoutputfc = arcpy.GetParameterAsText(1) # where to save your work
    arcspfield = arcpy.GetParameterAsText(2) 
    arc_create_all_spcfields = arcpy.GetParameterAsText(3) # it will generate strings 'true' or 'false'

    arc_create_all_spcfields = True if arc_create_all_spcfields == 'true' else False

    spParse(arcinputfc,arcoutputfc,arcspfield, create_all_spcfields = arc_create_all_spcfields)




