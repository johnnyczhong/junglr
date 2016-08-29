#author: johnny
#purpose: provide functions to CRUD the postgres db

import db_helper

# represents 1 player's possible interactions with the db
# possible workflows:
# 1st time: player creates record and populates tables with their information
# nth time: player updates record and updates tables
# analysis: player requests analysis of their information. in which case this would be read-only.
#	would I still need to make a call to Riot API in this case? that would mean the api_summ_info requirement
# 	would be invalid for this object.

#purpose: create, read, update, or delete basic player info from db
#	has ability to determine if 
class player_data_CRUD():
	def __init__(self, summ_id):
		self.db_conn = db_helper.Connection()
		#should this make its own db connection?
		#maybe because using the same db connection for multiple purposes may cause a conflict
		self.summ_id = summ_id
		#self.sql_row = self.Read_Summ_Row()

	def Get_Summ_ID(self):
		return self.api_summ_info['id']

	def Get_API_Revision_Date(self):
		return self.api_summ_info['revisionDate']

    #in: summ info hash
	#out: summ name
	def Get_API_Summ_Name(self):
		return self.api_summ_info['name']

	def Read_Summ_Row(self): 
		query = 'select * from player_data where summ_id = {0};'.format(self.summ_id)
		row = (self.db_conn.Fetch(query))
		return row

   	#for testing. in production, you would almost never delete a record here
   	#unless data is too much and need to purge
	#in: summ id
	#out: true if deleted, false otherwise
	def Delete_Summ_Row(self):
	    delete_query = 'delete from player_data where summ_id = {0};'.format(self.summ_id)
	    deleted = self.db_conn.Commit(delete_query)
	    if self.Read_Summ_Row() == None:
	        deleted = True
	    return deleted

	def Update_Create(self, api_summ_info):
		action = 'no action'
		self.api_summ_info = api_summ_info
		self.api_rev_date = self.Get_API_Revision_Date()
		self.summ_name = self.Get_API_Summ_Name()
		self.sql_row = self.Read_Summ_Row()

		if not self.Create_Summoner_Decision():
			self.Create_Summoner()
			action = 'create'
		elif self.Update_Summoner_Decision():
  			self.Update_Summoner()
  			action = 'update'
		return action

	def Create_Summoner_Decision(self):
		exists = False if self.sql_row == [] else True
		return exists

	#in: dict of singular summ info
	#out: true if player record created, false if not
	def Create_Summoner(self):
	    create_query = "insert into player_data (summ_id, summ_name, revision_date) values ({0}, '{1}', {2});".format(self.summ_id, self.summ_name, self.api_rev_date)
	    created = self.db_conn.Commit(create_query)
	    return created


    #return: 'update' to update, 'create' to create, 'no action' if no action
	def Update_Summoner_Decision(self):
		update = True if self.sql_row[0].revision_date < self.api_rev_date else False
		return update

	def Update_Summoner(self):
		update_query = "update player_data set summ_name = '{0}', revision_date = {1} where summ_id = {2};".format(self.summ_name, self.api_rev_date, self.summ_id)
		updated = self.db_conn.Commit(update_query)
		return updated
