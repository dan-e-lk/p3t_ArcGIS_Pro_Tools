# after running the 01_clip_to_FMU.py, we found numerous gaps by erasing the PIAM from FMU boundaries.
# the results can be found here:
# C:\Users\kimdan\OneDrive - Government of Ontario\_FPPS\Projects\_inventory_cleanup\s01_clip_to_fmu.gdb

# this script attempts to fix these gaps in the following ways:
# For each FMU:
# 	1. If the PCM can fill some of these gaps, it's good.
#		Use intersect to intersect corresponding PCM with PIAM.
# 	2. Elif it overlaps with Water:
#		intersect the remaining gaps with OHN water
#		merge the output with the template, so all the fields
# 	3. Small gaps - use selective dissolve tool to dissolve into neighboring polygon.
# 	4. Other gaps - we may need to artificially generate fake data


def main():
	pass


if __name__ == '__main__':
	main()