# this is probably a one-time code for analyzing RAP data.  RAP 

code = """{'PJ': {'mean': 67.5894, 'stdv': 26.5842, 'ci': 7.8054, 'upper_ci': 75.3948, 'lower_ci': 59.784, 'n': 47, 'confidence': 0.95}, 
'PO': {'mean': 18.2872, 'stdv': 26.5533, 'ci': 7.7963, 'upper_ci': 26.0835, 'lower_ci': 10.4909, 'n': 47, 'confidence': 0.95}, 
'SX': {'mean': 9.8426, 'stdv': 9.5505, 'ci': 2.8041, 'upper_ci': 12.6467, 'lower_ci': 7.0385, 'n': 47, 'confidence': 0.95}, 
'LA': {'mean': 1.2277, 'stdv': 4.3174, 'ci': 1.2676, 'upper_ci': 2.4953, 'lower_ci': -0.0399, 'n': 47, 'confidence': 0.95}, 
'BF': {'mean': 0.7319, 'stdv': 2.5876, 'ci': 0.7597, 'upper_ci': 1.4916, 'lower_ci': -0.0278, 'n': 47, 'confidence': 0.95}, 
'BW': {'mean': 2.3298, 'stdv': 14.589, 'ci': 4.2835, 'upper_ci': 6.6133, 'lower_ci': -1.9537, 'n': 47, 'confidence': 0.95}}"""

# turn this into something like "PJ  70PO  20SX  10"
# use this as calculated field, using code block

def to_spcomp(code):
	# get the numbers for each species
	code_d = eval(code)
	spc_dict = {k:v['mean'] for k, v in code_d.items()} # eg. {'PJ': 67.5894, 'PO': 18.2872, 'SX': 9.8426, 'LA': 1.2277, 'BF': 0.7319, 'BW': 2.3298}
	print(spc_dict)

	# make it add to 100
	# 1. add the numbers that are less than 5.0
	# 2. divide that number by the major species (>=5%)
	# 3. add that number to each major species percentage
	minority_sum = sum([v for k,v in spc_dict.items() if v<5.0])
	num_of_majority = len([k for k,v in spc_dict.items() if v>=5.0])
	increment = minority_sum/num_of_majority
	# print(increment)

	new_spc_dict = {k:int(round(v+increment)) for k, v in spc_dict.items() if v>=5.0}
	# print(new_spc_dict)

	# turn this into "PJ  70PO  20SX  10" format
	spcomp_txt = ''
	for k,v in new_spc_dict.items():
		if v==100:
			spcomp_txt += '%s %s'%(k,v)
		elif v >= 10:
			spcomp_txt += '%s  %s'%(k,v)
		else:
			spcomp_txt += '%s   %s'%(k,v)

	return spcomp_txt


print(to_spcomp(code))
