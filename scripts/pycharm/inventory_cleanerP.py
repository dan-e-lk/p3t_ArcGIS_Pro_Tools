import arcpy

inputfc = r'C:\Users\kimdan\Government of Ontario\Forest Explorer - Data\ARC\FI_Analyst\FI_Analyst.gdb\t_NEBOR_FOR_over5000m2_sample_PIAM01'

print(arcpy.Describe(inputfc).path)