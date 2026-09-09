import arcpy
print(arcpy.GetInstallInfo())

# testing copilot

def clip_inventory_to_aoi(inventory_fc, aoi_fc, output_fc):
    """
    Clips the inventory feature class to the area of interest (AOI) feature class.

    Parameters:
    inventory_fc (str): The path to the inventory feature class.
    aoi_fc (str): The path to the area of interest feature class.
    output_fc (str): The path where the clipped output feature class will be saved.

    Returns:
    None
    """
    try:
        # Perform the clip operation
        arcpy.Clip_analysis(inventory_fc, aoi_fc, output_fc)
        print(f"Successfully clipped {inventory_fc} to {aoi_fc}. Output saved at {output_fc}.")
    except Exception as e:
        print(f"An error occurred: {e}")