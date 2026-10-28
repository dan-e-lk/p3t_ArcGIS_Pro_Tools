# Probably good idea to create a back up of your main sqlite3 before running all these queries.

# Do this after 03_hexagonize_all + running gdb-to-sqlite.
# No need ArcGIS to run this script.
# in the same parent forlder as db_path, you should have lut_sqlite3 - this is the look up table for SGRs and Forest Units.


import sqlite3
import os, csv


def run_sql_script_and_get_new_tables(db_path, sql_script, lut_db_fullpath):
    """Note on new_tables: If the table already exists and the sql script is DROPPING and Creating the same table again
    then this script will return empty list for "new_tables" """
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("ATTACH DATABASE ? AS lut", (lut_db_fullpath,)) #### This is needed for the join_LUT query!! 
        
        # Get tables before running script
        cursor = conn.cursor() # need cursor because I need to fetch results
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table';""")
        tables_before = {row[0] for row in cursor.fetchall()}

        try:
            print(sql_script)
            cursor.executescript(sql_script)
            conn.commit()

            # Get tables after running script
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table';
            """)
            tables_after = {row[0] for row in cursor.fetchall()}
            new_tables = tables_after - tables_before
            return {"success": True, "new_tables": list(new_tables), "message": "SQL script executed successfully."}
        except sqlite3.Error as e:
            conn.rollback()
            return {"success": False, "new_tables": [], "message": f"SQLite error: {e}"}
    except Exception as e:
        return {"success": False, "new_tables": [], "message": f"General error: {e}" }
    finally:
        if 'conn' in locals():
            conn.close()


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


def replace_in_sql_file(file_path, to_be_replaced, replace_it_with):
    """
    Reads a .sql file, replaces specified text,
    and returns the updated content as a string."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    # Replace text
    updated_content = content.replace(to_be_replaced, replace_it_with)
    return updated_content




if __name__ == '__main__':

    # workspace folder should contain the sqls as well as the 2 sqlite files: HexJoin.sqlite3 and lut.sqlite3
    workspace = r'C:\Users\KimDan\Government of Ontario\Forest Explorer - Data\E\SOA2\SOA_CC\sqlite'
    lut_db_fullpath = r"C:\Users\KimDan\Government of Ontario\Forest Explorer - Data\E\SOA2\SOA_CC\sqlite\lut.sqlite3"

    # the following files must already exist in the workspace folder
    db_name = 'soa2.sqlite3'
    # sql_scripts = ["12_HexJoin_join_LUTs.sql"]
    sql_scripts = ["10_ARI_ECONUM_to_ECOGRP.sql", "11_HexJoin_joinTables_short.sql", "12_HexJoin_join_LUTs.sql"]


    # output csv files will be saved here (directory must first exist)
    csv_folderpath = r'C:\Users\KimDan\Government of Ontario\Forest Explorer - Data\E\SOA2\SOA_CC\sqlite\csv'

    # mu to loop
    mu_list = [
        '035', '060', '110', '120', '130', '140', '175', '177', '210', '220',
        '230', '280', '350', '360', '390', '406', '415', '421', '438', '443',
        '451', '490', '535', '574', '601', '615', '644', '680', '702', '754',
        '780', '796', '816', '840', '889', '898', '930', '966', '994'] # 39 MUs
    # mu_list = ['035','210','930']


    # No need to change the following variable.
    # above sql scripts has the following mu as default. eg. 'f_816'
    # normally you don't have to chnage this unless you've edited *.sql files above.
    mu_default = 'f_035'

    ############################################################

    for mu in mu_list:
        f_mu = 'f_%s'%mu
        print("\nWorking on %s"%f_mu)

        for sql_file in sql_scripts:
            db_path = os.path.join(workspace, db_name)
            sql_file_path = os.path.join(workspace, sql_file)
            print("\t%s"%sql_file)

            # replace the mu name with what we are currently working on
            sql_script_txt = replace_in_sql_file(sql_file_path, to_be_replaced=mu_default, replace_it_with=f_mu)

            print("\t\tRunning the script")
            sql_output = run_sql_script_and_get_new_tables(db_path, sql_script_txt, lut_db_fullpath)
            if sql_output["success"]:
                print("\t\tSuccess!")
                table_name_lst = sql_output['new_tables'] # this is unreliable because if the same table already existed, you get an empty list.
                if len(table_name_lst) > 0:
                    out_tables = sql_output['new_tables']
                    print("\t\tNew Tables: %s"%out_tables)
                    # export to csv if the table name starts with 'ff_'
                    for tbl in table_name_lst:
                        if tbl.startswith('ff_') and tbl.endswith('summary'):
                            csv_filename = "%s.csv"%tbl
                            print("Exporting to %s..."%csv_filename)
                            sql_query = "SELECT * FROM %s"%tbl
                            select_n_export(db_path, csv_folderpath, csv_filename, sql_query)
                            print("\tExported successfully")
                print("\n\n")
            else:
                print("\t\t!!! SQL query failed !!!")
                print("%s"%sql_output['message'])
                raise

