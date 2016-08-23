#prog_name: champ_api.py
#purpose: pull champion data from riot api.
#	currently only the name tied to id

from req_builder import D_Make_Request
from req_builder import Build_URL



#TODO: add header request parameters to determine if need to update value
#in: none
#out: hash of all currently active champs. champ ids as keys mapped to champ names
def Hash_Get_Champs_Static():
	req = Build_URL('champ_data_static')
	response = D_Make_Request(req)
	champ_hash = response['data']
	return champ_hash

#in: aggregate champion name information
#out: hash that can be used to populate champion database
def Hash_Champ_ID_to_Name(champ_hash):
	champ_ids_to_names = {}
	for names in champ_hash.keys():
		champ_data = champ_hash[names]
		champ_id = champ_data['id']	
		champ_name = champ_data['name']
		champ_ids_to_names[champ_id] = champ_name
	return champ_ids_to_names

#in: champ ID
#out: champ info
def Hash_Get_Single_Champ_Info(champ_id):
	req = Build_URL('champ_name', champ_id) 
	response = D_Make_Request(req)
	return response

#in: champ ID
#out: champ info
def S_CID_to_CName(champ_info):
    return champ_info['name']