# csv files has h3 hexagon's GRID_ID - e.g. '8b0ed96c0200fff'
# we can generate the centroid lat long based on this.

import pandas as pd
import h3


def add_h3_centroids_to_csv(csv_path, grid_id_fieldname):
	# read csv
	print("Running h3 centroids to csv script.")
	df = pd.read_csv(csv_path, dtype=str) # if I don't specify dtype=str, then some fieldtypes may change.

	if grid_id_fieldname not in df.columns:
		raise ValueError("the csv file does not contain the %s field. check your input for grid_id_fieldname"% grid_id_fieldname)

	# convert H3 grid ids to centroid coordinates
	df[["LAT", "LON"]] = df[grid_id_fieldname].apply(get_centroid)

	# overwrite original file
	df.to_csv(csv_path, index=False)

	print(f"Successfully updated {csv_path}!")



def get_centroid(h3_id):
	lat, lon = h3.cell_to_latlng(str(h3_id))
	return pd.Series([lat,lon])


if __name__ == '__main__':
	csv = r"C:\Users\KimDan\Government of Ontario\Caribou Explorer - CM1_3\Data\Analysis\CM13_Viz\_draftv2\data\CM1_3_Summary.csv"
	add_h3_centroids_to_csv(csv, 'GRID_ID')





# def add_h3_centroids_to_csv(csv_path, grid_id_fieldname):
# 	# read csv
# 	df = pd.read_csv(csv_path)

# 	if grid_id_fieldname not in df.columns:
# 		raise ValueError("the csv file does not contain the %s field. check your input for grid_id_fieldname"% grid_id_fieldname)

# 	# convert H3 grid ids to centroid coordinates
# 	df[["LAT", "LON"]] = df[grid_id_fieldname].apply(get_centroid)

# 	# overwrite original file
# 	df.to_csv(csv_path, index=False)

# 	print(f"Successfully updated {csv_path}!")



# def get_centroid(h3_id):
# 	lat, lon = h3.cell_to_latlng(str(h3_id))
# 	return pd.Series([lat,lon])
