print("importing arcpy...")
import arcpy

input_inv = arcpy.GetParameterAsText(0) 
output_inv = arcpy.GetParameterAsText(1) # can be feature class or shapefile... i think


# check fields
field_list = [f.name.upper() for f in arcpy.ListFields(input_inv)]
mandatory_fields = ['OSPCOMP','USPCOMP', 'OCCLO','UCCLO']
for f in mandatory_fields:
	if f not in field_list:
		raise Exception("Cannot find %s field!!"%f)


# copy the feature class to a new location
arcpy.AddMessage("Copying %s to %s"%(input_inv,output_inv))
arcpy.CopyFeatures_management(input_inv, output_inv)

# create a new field
potential_fieldnames = ['BLND_SPC','BLND_SPC1','BLND_SPC2','BLND_SPC3','BLND_SPC4']
for newfield in potential_fieldnames:
	if newfield not in field_list:
		# create new field
		arcpy.AddMessage("Creating a new field: %s"%newfield)
		arcpy.AddField_management(output_inv,newfield,"TEXT", "", "", "200")
		fieldname = newfield
		break


# Calculate field
expression = "main( !OSPCOMP!, !USPCOMP!, !OCCLO!, !UCCLO!)"
codeblock = """
def main(ospcomp,uspcomp,occlo,ucclo):
  try:
    if ospcomp != None and uspcomp != None and occlo != None and ucclo != None:
      if len(ospcomp)%6 == 0 and len(uspcomp)%6 == 0 and occlo + ucclo > 0:
        n1 = len(ospcomp)/6
        n2 = len(uspcomp)/6

        spcList1 = [ospcomp[6*i:6*i+3].strip().upper() for i in range(n1)]
        percentList1 = [int(ospcomp[6*i+3:6*i+6].strip()) for i in range(n1)]
        spcPercentDict1 = dict(zip(spcList1,percentList1)) # this should look like {'AX':60,'CW':40}

        spcList2 = [uspcomp[6*i:6*i+3].strip().upper() for i in range(n2)]
        percentList2 = [int(uspcomp[6*i+3:6*i+6].strip()) for i in range(n2)]
        spcPercentDict2 = dict(zip(spcList2,percentList2)) # this should look like {'AX':60,'CW':40}

        blndPercentDict = {}
        allspcList = list(set(spcList1)|set(spcList2))
        for spc in allspcList:
          try:
            sp1 = spcPercentDict1[spc]
          except:
            sp1 = 0
          try:
            sp2 = spcPercentDict2[spc]
          except:
            sp2 = 0

          calc = int(round( (sp1 * float(occlo)/(occlo+ucclo)) + (sp2 * float(ucclo)/(occlo+ucclo)) ))
          if calc > 0:
            blndPercentDict[spc] = calc 

        print blndPercentDict # will look something like this: {'PR': 2, 'BF': 14, 'PW': 22, 'PT': 17, 'BW': 15, 'MR': 1, 'PJ': 7, 'SB': 22, 'PO': 1}


        # check if they add up to 100.
        blndPercentList = sorted(blndPercentDict.items(), key=lambda (k,v): (-v,k))
        print blndPercentList # [('PW', 22), ('SB', 22), ('PT', 17), ('BW', 15), ('BF', 14), ('PJ', 7), ('PR', 2), ('MR', 1), ('PO', 1)]

        sum_perc = 0
        for perc in blndPercentDict.values():
          sum_perc += perc
        if sum_perc != 100:
          if sum_perc in range(98,103): #[98, 99, 100, 101, 102]
            change_needed = 100 - sum_perc
            blndPercentList = sorted(blndPercentDict.items(), key=lambda (k,v): (-v,k))
            print blndPercentList # [('PW', 22), ('SB', 22), ('PT', 17), ('BW', 15), ('BF', 14), ('PJ', 7), ('PR', 2), ('MR', 1), ('PO', 1)]
            blndPercentDict[blndPercentList[0][0]] = blndPercentList[0][1] + change_needed
        print blndPercentDict

        # turning the result into the correct string format
        blndPercentList = sorted(blndPercentDict.items(), key=lambda (k,v): (-v,k))
        text = ''
        for item in blndPercentList:
          text += item[0].ljust(3)
          text += str(item[1]).rjust(3)
        print text
        return text

      else:
        return 'Cannot be blended'
    else:
      return 'Cannot be blended'
  except:
    return 'Cannot be blended'
"""
arcpy.AddMessage("Calculating blended scpomp...")
arcpy.CalculateField_management(output_inv, fieldname, expression, "PYTHON_9.3", codeblock)
