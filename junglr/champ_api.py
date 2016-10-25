#prog_name: champ_api.py
#purpose: pull champion data from riot api.
#	currently only the name tied to id

import req_builder
import mongo_helper

#TODO: add header request parameters to determine if need to update value
#in: none
#out: hash of all currently active champs. champ ids as keys mapped to champ names
def Hash_Get_Champs_Static():
	response = req_builder.api_request('champ_data_static', '')
	champ_hash = response.body['data']
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


def main():
	api_champ_id_to_name = (Hash_Champ_ID_to_Name(Hash_Get_Champs_Static()))
	db_conn = mongo_helper.Connection()
	db_champ_ids_list = db_conn.find('static_data', {'document_name': 'champ_list'})
	new_champs_list = {}
	if db_champ_ids_list == None:
		for k, v in api_champ_id_to_name.items():
			new_champs_list[str(k)] = {'name': v, 'id': k}
	else:
		for k, v in api_champ_id_to_name.items():
			if k not in db_champ_ids_list:
				new_champs_list[str(k)] = {'name': v, 'id': k}
	inserted = db_conn.update('static_data', {'document_name': 'champion_info'}, {'$set': new_champs_list}, force = True)
	print(inserted)

if __name__ == '__main__':
	main()