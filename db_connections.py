#author: johnny
#purpose: provide functions to CRUD the postgres db

from db_helper import Connection, Query

# represents 1 player's possible interactions with the db
# possible workflows:
# 1st time: player creates record and populates tables with their information
# nth time: player updates record and updates tables
# analysis: player requests analysis of their information. in which case this would be read-only.
#	would I still need to make a call to Riot API in this case? that would mean the api_summ_info requirement
# 	would be invalid for this object.

#purpose: create, read, update, or delete basic player info from db
#	has ability to determine if 
class Player_Data_CRUD():
	def __init__(self, summ_id):
		self.db_conn = Connection()
		self.summ_id = summ_id
		self.table_affected = 'player_data'

	#read action for summoner data
	def read_summ_row(self): 
		action = 'select'
		where_hash = {'summ_id' : self.summ_id}
		select_query = Query(action, self.table_affected, where = where_hash)
		row = (self.db_conn.Execute_Query(select_query.statement))
		return row

   	#for testing. in production, you would almost never delete a record here
   	#unless data is too much and need to purge
	#in: summ id
	#out: true if deleted, false otherwise
	def Delete_Summ_Row(self):
	    #delete_query = 'delete from player_data where summ_id = {0};'.format(self.summ_id)
	    action = 'delete'
	    where_hash = {'summ_id' : self.summ_id}
	    delete_query = Query(action, self.table_affected, where = where_hash)
	    deleted = self.db_conn.Execute_Query(delete_query.statement)
	    if self.read_summ_row() == None:
	        deleted = True
	    return deleted

	#in: dict of singular summ info
	#out: true if player record created, false if not
	def create_summoner(self, summ_name, api_rev_date):
	    action = 'insert'
	    subject_hash = {'summ_id' : self.summ_id, 'summ_name' : summ_name, 'revision_date' : api_rev_date}
	    create_query = Query(action, self.table_affected, subject = subject_hash)
	    created = self.db_conn.Execute_Query(create_query.statement)
	    return created

	def update_summoner(self, summ_name, api_rev_date):
		action = 'update'
		subject_hash = {'summ_name' : summ_name, 'revision_date' : api_rev_date}
		where_hash = {'summ_id' : self.summ_id}
		update_query = Query(action, self.table_affected, where = where_hash, subject = subject_hash)
		updated = self.db_conn.Execute_Query(update_query.statement)
		return updated

	def add_Mains(self, main_lane, main_champ, main_role):
		action = 'update'
		subject_hash = {'main_champ' : main_champ, 'main_lane' : main_lane, 'main_role' : main_role}
		where_hash = {'summ_id' : self.summ_id}
		add_query = Query(action, self.table_affected, where = where_hash, subject = subject_hash)
		added = self.db_conn.Execute_Query(add_query.statement)
		return added

	def add_League(self, league, division):
		action = 'update'
		subject_hash = {'league' : league, 'division' : division}
		where_hash = {'summ_id' : self.summ_id}
		add_query = Query(action, self.table_affected, where = where_hash, subject = subject_hash)
		added = self.db_conn.Execute_Query(add_query.statement)
		return added

class Champ_Data_CRUD():
	def __init__(self):
		self.db_conn = Connection()
		self.table_affected = 'champ_data'

	def champ_id_to_name(self, champ_id):
		action = 'select'
		where_hash = {'champ_id' : champ_id}
		select_query = Query(action, self.table_affected, where = where_hash)
		champ_name = (self.db_conn.Execute_Query(select_query.statement))[0].champ_name
		return champ_name
