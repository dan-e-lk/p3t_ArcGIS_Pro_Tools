#-------------------------------------------------------------------------------
# Name:        Populate SI
# Date Created: 2021 11 16
#
# Author:      kimdan
#
# Workflow:
#   1. copies the input fc to the output location (selecting only where POLYTYPE = FOR)
#   2. If SI field already exists, rename it to SI_Origin
#   3. create a new text field "SI"
#   3. Select using user-specified SQL and populate the new field with the user-specified values.
#   4. Note that SQL2 will over-ride SQL1 and SQL3 will over-ride SQL2 and so on.
#
# Note:
#
#-------------------------------------------------------------------------------

import arcpy
import os, re


def main(inputfc, outputfc, newfieldname, Value1, SQL1, Value2, SQL2, Value3, SQL3, Value4, SQL4, Value5, SQL5, Value6, SQL6, Value7, SQL7, Value8, SQL8):

    newfieldname = 'SI'

    # Values and SQLs
    val_list = [Value1,Value2,Value3,Value4,Value5,Value6,Value7,Value8]
    SQL_list = [SQL1,SQL2,SQL3,SQL4,SQL5,SQL6,SQL7,SQL8]

    sql_dict = {}
    for num, val in enumerate(val_list):
        if val != '':
            if SQL_list[num] != '':
                try:
                    sql_dict[num + 1] = [val, SQL_list[num]] # for example, sql_dict would look like {1: ['HVHC', " CE + HE + BF + SW ......."], 2: ['HVLC', " CE + BF + ...." ]}
                except:
                    pass

    arcpy.AddMessage("\nUser SQL inputs as follows:\n%s"%sql_dict)

    ##### done with examining inputs.



    existingFields = [str(f.name).upper() for f in arcpy.ListFields(inputfc)]

    if 'POLYTYPE' not in existingFields:
        arcpy.AddError("\nPOLYTYPE field does not exist in your input data.\n")
        raise Exception("POLYTYPE field not found in the input table.")

    # Copy the feature class to the ouput location
    arcpy.AddMessage("\nCopying the input the the output location (only those records with POLYTYPE = FOR will be copied over) ...")
    outpath = os.path.split(outputfc)[0]
    outname = os.path.split(outputfc)[1]
    expression = """ "POLYTYPE" = 'FOR' """
    arcpy.FeatureClassToFeatureClass_conversion(inputfc,outpath,outname,expression)

    # if SI field aleady exists, rename it to SI_Origin
    if newfieldname in existingFields:
        arcpy.AddMessage("%s field already exists. The program will rename current SI with SI_ORIGIN"%newfieldname)
        if newfieldname + '_ORIGIN' not in existingFields:
            arcpy.management.AlterField(in_table=outputfc, field='SI', new_field_name=newfieldname+'_ORIGIN')


    # create a temporary layer file - this layer will be used for selecting and calculating field until finally being exported to a real feature class.
    arcpy.AddMessage("\nCreating a temporary layer...")
    arcpy.MakeFeatureLayer_management(outputfc,"templyr")


    # create the SI field
    arcpy.AddMessage("Creating a new field: %s"%newfieldname)
    arcpy.AddField_management(in_table = "templyr", field_name = newfieldname, field_type = "TEXT", field_length = "50")


    # select by attribute and calculate field
    arcpy.AddMessage("Selecting and calculating %s field..."%newfieldname)
    for k, v in sql_dict.items():

        value = v[0] # for example, 'HVHC'
        sql = v[1] # for example,  " CE + HE + BF + SW .. > 50"


        # Select and calcualte field
        arcpy.AddMessage("\n%s. Calculating %s: %s"%(k, value, sql))

        try:
            arcpy.SelectLayerByAttribute_management("templyr", "NEW_SELECTION", sql)
        except:
            arcpy.AddError("\nERROR while calculating %s.\nPlease double check the following SQL:\n%s"%(value, sql))
            raise Exception("\nCheck your SQLs and try again.")

        arcpy.CalculateField_management("templyr", newfieldname, "'" + value + "'", "PYTHON_9.3")

    # clear selection
    arcpy.SelectLayerByAttribute_management("templyr", "CLEAR_SELECTION")






if __name__ == '__main__':
    # some of these fields are optional. when the user leaves it blank, it will come out as a blank string: ''
    inputfc = arcpy.GetParameterAsText(0)             # toolbox input feature class
    outputfc = arcpy.GetParameterAsText(1)            # toolbox output feature class
    newfieldname = str(arcpy.GetParameterAsText(2))   # 'SI'
    Value1= str(arcpy.GetParameterAsText(3))  
    SQL1 = str(arcpy.GetParameterAsText(4))   
    Value2= str(arcpy.GetParameterAsText(5))  
    SQL2 = str(arcpy.GetParameterAsText(6))   
    Value3= str(arcpy.GetParameterAsText(7))  
    SQL3 = str(arcpy.GetParameterAsText(8))   
    Value4= str(arcpy.GetParameterAsText(9))  
    SQL4 = str(arcpy.GetParameterAsText(10))  
    Value5= str(arcpy.GetParameterAsText(11))          
    SQL5 = str(arcpy.GetParameterAsText(12))
    Value6= str(arcpy.GetParameterAsText(13))          
    SQL6 = str(arcpy.GetParameterAsText(14))
    Value7= str(arcpy.GetParameterAsText(15))          
    SQL7 = str(arcpy.GetParameterAsText(16))
    Value8= str(arcpy.GetParameterAsText(17))          
    SQL8 = str(arcpy.GetParameterAsText(18))        

    # arcpy.AddMessage('%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n'%(inputfc, outputfc, newfieldname, Value1, SQL1, Value2, SQL2, Value3, SQL3, Value4, SQL4, Value5, SQL5))

    main(inputfc, outputfc, newfieldname, Value1, SQL1, Value2, SQL2, Value3, SQL3, Value4, SQL4, Value5, SQL5, Value6, SQL6, Value7, SQL7, Value8, SQL8)

