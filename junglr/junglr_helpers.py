#junglr_helpers.py

import mongo_helper

def get_sorted_champ_list():
	champ_list = []
	conn = mongo_helper.Connection()
	champ_mapping = conn.find('static_data', {'document_name': 'champion_info'})
	# remove the mongo defining params
	del champ_mapping['document_name']
	del champ_mapping['_id']
	# make list for champ names
	for v in champ_mapping.values():
		champ_list.append(v['name'])
	# sort list and return
	champ_list.sort()
	return champ_list
