# the goal is to create a script similar to fc_to_sqlite.py except it turns fc into geopackage.
# https://gis.stackexchange.com/questions/487258/converting-geodatabase-into-geopackage-using-arcgis-pro
# combination of Create SQLite Workspace tool and Copy tool.

def main():
	pass

if __name__ == '__main__':
	input_fc = arcpy.GetParameterAsText(0)
