#functions to populate the database with player information
#test some work flows

import req_builder
import config
import db_interface

summ_name_list = [config.my_summ_name, config.tim, config.steph, config.marina]

#get list of summ_id from player names
summ_id_list = req_builder.List_Summ_Name_to_ID(summ_name_list)

#get summ information
agg_summ_hash = req_builder.Hash_Basic_Summ_Info(summ_id_list)

#populate database with summoner information
conn = db_interface.db_helper.Connect()

for ids in agg_summ_hash:
	if db_interface.Update_Summoner_Decision(agg_summ_hash, conn):
		db_interface.Update_Summoner(agg_summ_hash[ids], conn)