# run mulitple SQLs on any sqlite database to grab what we need for tableau
# no need arcpy here.


# Workflow
# you have sqlite files
# using db browser, build your select queries to select what you need
# use the select queries as input and it will output the result in csv files. This circumvents having to build views or extra tables on your sqlite file - keeping your original db clean.


import sqlite3
import csv, os



def select_n_export(sqldb, csv_folderpath, csv_filename, sql_query):

    # print("\nConnecting to ARI sqlite3 database")
    conn = sqlite3.connect(sqldb)
    cursor = conn.cursor()

    print("\n\n##### Executing sql query to generate %s:\n%s"%(csv_filename,sql_query))
    cursor.execute(sql_query)

    results = cursor.fetchall()
    count = len(results)
    print("\tSQL query returned %s rows"%count)

    if count > 0:
        print("Writing the csv file: %s"%csv_filename)
        csv_fullpath = os.path.join(csv_folderpath,csv_filename)

        with open(csv_fullpath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([i[0] for i in cursor.description])
            writer.writerows(results)
        print("Done!")
    else:
        print("!!! No result returned. Check your SQL query!")

    conn.close()




if __name__ == '__main__':

    # full path to the sqlite3 database
    ARI =       r'C:\Users\KimDan\Government of Ontario\Forest Explorer - FRO\FRO2026\Data\sqlite\ARI_base.sqlite3'
    ARI_wFU =   r'C:\Users\KimDan\Government of Ontario\Forest Explorer - FRO\FRO2026\Data\sqlite\ARI_wFU.sqlite3'
    ARI_wVol =  r"C:\Users\KimDan\Government of Ontario\Forest Explorer - FRO\FRO2026\Data\sqlite\ARI_wVOL_CAI.sqlite"
    ARI_wVol_FN = r"C:\Users\KimDan\Government of Ontario\Forest Explorer - FRO\FRO2026\Data\sqlite\FN_wVOL.sqlite3"
    fe = r"C:\Users\KimDan\Government of Ontario\Forest Explorer - Data\D\FE_Remake\data_n_script\forest_explorer.db"

    # csv_folderpath = r'C:\Users\KimDan\OneDrive - Government of Ontario\_FPPS\Projects\_Spooner_David_Peter\CommercialThinning_20260723'
    csv_folderpath = r'C:\Users\KimDan\OneDrive - Government of Ontario\_FPPS\Projects\AmandaMcLachlan\PermetToRemove\vol'

    queries = {
#     '0': [fe, csv_folderpath, 'TND_Summary_2002-2024.csv',
# """
# SELECT a.TRTMTHD1, a.AR_YEAR, b.FMU_CODE, SUM(a.Hectares) AS HA, b.FMU_NAME
# FROM SRC_AR_TEND_ALL_02_N_UP a
# LEFT JOIN ref_FMU_FN_PARK_Boundary b
# ON a.MUNO = b.FMU_NUM
# GROUP BY a.TRTMTHD1, a.AR_YEAR, a.MUNO
# """],
#     '1': [fe, csv_folderpath, 'HRV_Summary_2002-2024.csv',
# """
# SELECT a.HARVMTHD, a.AR_YEAR, b.FMU_CODE, b.FMU_NAME, SUM(a.HECTARES) AS HA
# FROM SRC_AR_HRV_ALL_02_N_UP a
# LEFT JOIN ref_FMU_FN_PARK_Boundary b
# ON a.MUNO = b.FMU_NUM
# GROUP BY a.HARVMTHD, a.AR_YEAR, b.FMU_CODE, b.FMU_NAME
# """],
#     '2': [fe, csv_folderpath, 'SIP_Summary_2002-2024.csv',
# """
# SELECT a.TRTMTHD1, a.AR_YEAR, b.FMU_CODE, b.FMU_NAME, SUM(a.HECTARES) AS HA
# FROM SRC_AR_SIP_ALL_02_N_UP a
# LEFT JOIN ref_FMU_FN_PARK_Boundary b
# ON a.MUNO = b.FMU_NUM
# GROUP BY a.TRTMTHD1, a.AR_YEAR, b.FMU_CODE, b.FMU_NAME
# """],
#     '3': [fe, csv_folderpath, 'SCT_Summary_2002-2024.csv',
# """
# SELECT a.SLASHPIL, a.AR_YEAR, b.FMU_CODE, b.FMU_NAME || ' (' || b.FMU_CODE || ')' AS MU, SUM(a.KM) AS KM
# FROM AR_SCT a
# LEFT JOIN ref_FMU_FN_PARK_Boundary b
# ON a.MUNO = b.FMU_NUM
# WHERE a.SLASHPIL = 'Y'
# GROUP BY a.SLASHPIL, a.AR_YEAR, b.FMU_CODE, b.FMU_NAME
# """],
    '3': [ARI_wVol, csv_folderpath, 'raw_Vol_bin_Area_GLSL.csv',
"""
SELECT
    CASE
        WHEN NMV < 20 OR NMV IS NULL THEN '0-20'
        WHEN NMV < 40  THEN '20-40'
        WHEN NMV < 60  THEN '40-60'
        WHEN NMV < 80  THEN '60-80'
        WHEN NMV < 100 THEN '80-100'
        WHEN NMV < 120 THEN '100-120'
        WHEN NMV < 140 THEN '120-140'
        WHEN NMV < 160 THEN '140-160'
        WHEN NMV < 180 THEN '160-180'
        WHEN NMV < 200 THEN '180-200'
        WHEN NMV < 220 THEN '200-220'
        WHEN NMV < 240 THEN '220-240'
        ELSE '240+'
    END AS NMV_Bin20, 
    AC20, a.MUNO, SUM(Ha) AS Area_ha, COUNT(Ha) AS PolygonCount, 'GLSL' AS REGION_NAME
FROM FOR_ALL_wVol a
LEFT JOIN MU_Boundary2 b
ON a.MUNO = b.FMU_NUM
WHERE a.OWNER = 'CROWN' AND b.SFU_REGION = 'GLSL'
GROUP BY NMV_Bin20, AC20, a.MUNO
ORDER BY MIN(NMV);
"""],
    '4': [ARI_wVol, csv_folderpath, 'raw_Vol_bin_Area_BOR.csv',
"""
SELECT
    CASE
        WHEN NMV < 20 OR NMV IS NULL THEN '0-20'
        WHEN NMV < 40  THEN '20-40'
        WHEN NMV < 60  THEN '40-60'
        WHEN NMV < 80  THEN '60-80'
        WHEN NMV < 100 THEN '80-100'
        WHEN NMV < 120 THEN '100-120'
        WHEN NMV < 140 THEN '120-140'
        WHEN NMV < 160 THEN '140-160'
        WHEN NMV < 180 THEN '160-180'
        WHEN NMV < 200 THEN '180-200'
        WHEN NMV < 220 THEN '200-220'
        WHEN NMV < 240 THEN '220-240'
        ELSE '240+'
    END AS NMV_Bin20, 
    AC20, a.MUNO, SUM(Ha) AS Area_ha, COUNT(Ha) AS PolygonCount, 'BOR' AS REGION_NAME
FROM FOR_ALL_wVol a
LEFT JOIN MU_Boundary2 b
ON a.MUNO = b.FMU_NUM
WHERE a.OWNER = 'CROWN' AND b.SFU_REGION in ('NEBOR','NWBOR')
GROUP BY NMV_Bin20, AC20, a.MUNO
ORDER BY MIN(NMV);
"""],
    '5': [ARI_wVol_FN, csv_folderpath, 'raw_Vol_bin_Area_FN.csv',
"""
SELECT
    CASE
        WHEN NMV < 20 OR NMV IS NULL THEN '0-20'
        WHEN NMV < 40  THEN '20-40'
        WHEN NMV < 60  THEN '40-60'
        WHEN NMV < 80  THEN '60-80'
        WHEN NMV < 100 THEN '80-100'
        WHEN NMV < 120 THEN '100-120'
        WHEN NMV < 140 THEN '120-140'
        WHEN NMV < 160 THEN '140-160'
        WHEN NMV < 180 THEN '160-180'
        WHEN NMV < 200 THEN '180-200'
        WHEN NMV < 220 THEN '200-220'
        WHEN NMV < 240 THEN '220-240'
        ELSE '240+'
    END AS NMV_Bin20, 
    AC20, MUNO, SUM(Ha) AS Area_ha, COUNT(Ha) AS PolygonCount, 'FN' AS REGION_NAME
FROM FN_wVol
WHERE OWNER = 'CROWN'
GROUP BY NMV_Bin20, AC20, MUNO
ORDER BY MIN(NMV);
"""],
    }




    for name, q in queries.items():
        select_n_export(q[0],q[1],q[2],q[3])

