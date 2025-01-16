version = 'beta'
#-------------------------------------------------------------------------------
# Name:         SPCOMP_Builder
# Purpose:      This tool can be used to if you have species composition parsed 
#               out to individual attributes in your inventory, and you need to create and 
#               populate the SPCOMP attribute by merging those individual species attributes.
#
# Author:      Daniel Kim
#
# Created:     2019/06/18
# Copyright:   Ministry of Natural Resources and Forestry
#
#-------------------------------------------------------------------------------

# In your original inventory, if you have an attribute representing the percent BY, OR or SC, those fields must be named as _BY, _OR, and _SC.
# POLYTYPE is a mandatory field.
# the parsed species attributes can have values in percentage (30, 45, etc) or in ratio (0.3, 0.45, etc.)

import Reference as R # Reference.py should be located in the same folder as this file.
import arcpy, os
from messages import print2
from messages import output
from datetime import datetime

def rand_alphanum_gen(length):
    """
    Generates a random string (with specified length) that consists of A-Z and 0-9.
    """
    import random, string
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(length))

def dict_2_spcomp(spc_dict):
    """ converts {'AB': 60, '_BY': 40} into "AB  60BY  40"
        also validates if the numbers adds up to 100 by returning value sum.
    """

    # first replace _BY with BY
    spcs = spc_dict.keys()
    if '_BY' in spcs: spc_dict['BY'] = spc_dict.pop('_BY')
    if 'YB' in spcs: spc_dict['BY'] = spc_dict.pop('YB')    
    if '_OR' in spcs: spc_dict['OR'] = spc_dict.pop('_OR')
    if 'RO' in spcs: spc_dict['OR'] = spc_dict.pop('RO')
    if '_SC' in spcs: spc_dict['SC'] = spc_dict.pop('_SC')
    if 'CS' in spcs: spc_dict['SC'] = spc_dict.pop('CS')

    # check if they add up to 100
    value_sum = 0
    for value in spc_dict.values():
        value_sum += value

    # sort
    sorted_spc_dict = sorted(spc_dict.items(), key=lambda kv: kv[1], reverse=True) # this will return [('PJ', 50), ('SW', 30), ('SB', 20)]

    # put them together
    spcomp_str = ''
    for pair in sorted_spc_dict:
        spcomp_str += str(pair[0]).ljust(3)
        spcomp_str += str(pair[1]).rjust(3)

    return [spcomp_str, value_sum]


def spBuild(inputfc,outputfc, parsed_spc_in_ratio):
    # # Mark start time
    # starttime = datetime.now()
    # msg = print2('Start of process: %(start)s.' %{'start':starttime.strftime('%Y-%m-%d %H:%M:%S')})

    # New SPCOMP field name
    suffix = rand_alphanum_gen(3)
    spcomp = "SPCOMP_" + suffix  
    spcomp_check = spcomp + "_CHK"

    # Copy the input bmi to the location of choice
    msg = print2("Making a copy of the input feature class... \n\tInput: %(infc)s\n\tOutput: %(outfc)s"%{'infc':inputfc, 'outfc':outputfc})
    arcpy.FeatureClassToFeatureClass_conversion(in_features=inputfc, out_path=os.path.split(outputfc)[0], out_name=os.path.split(outputfc)[1])

    # Creating new fields
    msg += print2("Creating new fields...")
    arcpy.AddField_management(outputfc, spcomp, "TEXT", field_length=200) # tech spec says 120, but putting 200 just in case...
    arcpy.AddField_management(in_table = outputfc, field_name = spcomp_check, field_type = "SHORT")

    # Create a complete list of species and the corresponding list of field names
    completeSpList = R.SpcListInterp + R.SpcListOther # this is our complete species list.
    completeSpList.sort()

    existingFields = [str(f.name).upper() for f in arcpy.ListFields(outputfc)] # these are the existing fields in the input fc

    odd_field_names = ['_BY','_OR','_SC','YB','RO','CS']
    completeFldList = completeSpList + odd_field_names
    # ignore SC because it's used for site class
    completeFldList.pop(completeFldList.index('SC'))

    # locating all the parsed species attribute names
    existingspc = list(set(existingFields)&set(completeFldList))

    # populating spcomp
    msg += print2("Populating %s..."%spcomp)
    error_count = 0
    fields = existingspc + [spcomp, spcomp_check] # we add these two attributes because we need to edit them.
    with arcpy.da.UpdateCursor(outputfc, fields, '''"POLYTYPE" = 'FOR' ''') as cursor:
        for row in cursor:
            spc_dict = {}
            for i,v in enumerate(row):
                if parsed_spc_in_ratio and v > 0 and v <= 1:
                    spc_dict[fields[i]] = int(round(v*100))
                elif not parsed_spc_in_ratio and v > 0 and v <= 100:
                    spc_dict[fields[i]] = int(round(v))
            spcomp_txt, spcomp_sum = dict_2_spcomp(spc_dict)
            # msg += print2('%s\n%s\n%s'%(spc_dict,spcomp_txt,spcomp_sum))
            row[fields.index(spcomp)] = spcomp_txt
            row[fields.index(spcomp_check)] = spcomp_sum

            cursor.updateRow(row)

            if spcomp_sum != 100:
                error_count += 1

    if error_count == 0:
        msg += print2("\nAll SPCOMP adds up to 100")
    else:
        msg += print2("There are %s records where POLYTYPE = 'FOR' and SPCOMP does not add up to 100"%error_count, 'warning')

    msg += print2("\nThe name of the new SPCOMP field is %s\n"%spcomp)



if __name__ == '__main__':
    arcinputfc = arcpy.GetParameterAsText(0) # this should be bmi or pci
    arcoutputfc = arcpy.GetParameterAsText(1) # where to save your work (feature class)
    parsed_spc_in_ratio = arcpy.GetParameterAsText(2) # "false" if species values are in tens (30, 40, 50...), "true" if values are in ratio (0.1, 0.2, 0.3...)

    parsed_spc_in_ratio = True if parsed_spc_in_ratio == 'true' else False

    spBuild(arcinputfc,arcoutputfc, parsed_spc_in_ratio)