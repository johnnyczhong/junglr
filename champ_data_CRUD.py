#prog_name: champ_data_CRUD.py
#purpose: populate values to champ_data db

import db_helper

#workflow - update static data (champ info and stats during patch cycles)

#purpose: populate the db. builds the query
#	then populates database with most current api information
#in: champion information in hash form
#out: update the db. true if successful, false if not
def Mass_Static_Champ_DB_Init(champ_info_hash, db_conn):
	query = 'insert into champ_info (champ_id, champ_name) values '
	for keys in champ_info_hash.keys():
		champ_name = champ_info_hash[keys]
		champ_name = champ_name.replace('\'', '\'\'') #sanitize names
		query += '(%s, \'%s\'),' %(keys, champ_name)
	query = query[:-1] 
	query += ';' # replace last value to be semicolon to end query statement
	return db_helper.Commit(query, db_conn)

#def Patch_Static_Champ_DB_Update():

def Identify_New_Champs():
	current_champ_ids = List_DB_Champ_ID(db_conn).sort()
	api_champ_ids = List_Api_Champ_ID().sort()
	for ids in api_champ_ids:
		if ids not in current_champ_ids:
			
