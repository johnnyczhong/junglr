#prog_name: initial_build.py
#purpose: to be run upon initializing database
#	populates databases with known values

import config
#import req_builder
from player_api import List_Summ_Name_to_ID, Hash_Basic_Summ_Info
from champ_api import Hash_Get_Champs_Static, Hash_Champ_ID_to_Name
from player_data_CRUD import Mass_Player_Data_Input
from champ_data_CRUD import Mass_Static_Champ_DB_Init
from db_helper import Connect

summ_name_list = [config.my_summ_name, config.tim, config.steph, config.marina]
#get list of summ_id from player names
summ_id_list = List_Summ_Name_to_ID(summ_name_list)
#get summ information
agg_summ_hash = Hash_Basic_Summ_Info(summ_id_list)

#initialize champion information
agg_champ_hash = Hash_Get_Champs_Static()
champ_hash_id_names = Hash_Champ_ID_to_Name(agg_champ_hash)

#populate database with summoner information
conn = Connect()

Mass_Player_Data_Input(agg_summ_hash, conn)
print(Mass_Static_Champ_DB_Init(champ_hash_id_names, conn))