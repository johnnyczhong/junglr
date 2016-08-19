#author: johnny
#purpose: provide functions to CRUD the postgres db

import db_helper

#in: summoner id in str or int
#out: row of summoner data from sql, none if not found
def Get_Summoner_Row(summ_id, db_conn): 
    query = 'select * from player_data where summ_id = ' + str(summ_id) + ';'
    row = db_helper.Fetch(query, db_conn)
    return row

def Mass_Player_Data_Input(agg_summ_info, db_conn):
    for ids in agg_summ_info.keys():
        single_player_data = agg_summ_info[ids]
        print(Player_DB_Action(single_player_data, db_conn))

#in: first stop when getting a summoner id
#out: string specifying action taken: 'created', 'updated', 'no action'
def Player_DB_Action(hash_summ_info, db_conn):
    action = 'no action'
    summ_id = Get_Summ_ID(hash_summ_info)
    sql_row = Get_Summoner_Row(summ_id, db_conn)
    
    if not Create_Summoner_Decision(summ_id, sql_row, db_conn):
        Create_Summoner(hash_summ_info, db_conn)
        action = 'created'
    elif Update_Summoner_Decision(hash_summ_info, sql_row, db_conn):
        Update_Summoner(hash_summ_info, db_conn)
        action = 'updated'
    return action

#does player exist in database? true if yes, false if no
def Create_Summoner_Decision(summ_id, sql_row, db_conn):
    exists = False if sql_row == [] else True
    # if Get_Summoner_Row(summ_id, db_conn) == []:
    #     exists = False
    return exists

#in: dict of singular summ info
#out: true if player record created, false if not
def Create_Summoner(summ_info, db_conn):
    summ_id = str(Get_Summ_ID(summ_info))
    summ_name = str(Get_Summ_Name(summ_info))
    rev_date = str(Get_Summ_Revision_Date(summ_info))
    create_query = "insert into player_data (summ_id, summ_name, revision_date) values (%s, '%s', %s);" %(summ_id, summ_name, rev_date)
    created = db_helper.Commit(create_query, db_conn)
    return created

#in: summ info
#out: true if record updated, false if not
def Update_Summoner(summ_info, db_conn):
    summ_id = str(Get_Summ_ID(summ_info))
    summ_name = str(Get_Summ_Name(summ_info))
    rev_date = str(Get_Summ_Revision_Date(summ_info))
    update_query = "update player_data set summ_name = '%s', revision_date = %s where summ_id = %s;" %(summ_name, rev_date, summ_id)
    updated = db_helper.Commit(update_query, db_conn)
    return updated

#return: 'update' to update, 'create' to create, 'no action' if no action
def Update_Summoner_Decision(api_row, sql_row, db_conn):
    action = False
    summ_id = Get_Summ_ID(api_row)
    api_rev_date = Get_Summ_Revision_Date(api_row)

    if sql_row[0][2] < api_rev_date:
        action = True
    return action

#in: summ id
#out: true if deleted, false otherwise
def Delete_Summoner(summ_id, db_conn):
    delete_query = 'delete from player_data where summ_id = ' + str(summ_id) + ';'
    deleted = db_helper.Commit(delete_query, db_conn)
    if Get_Summoner_Row(summ_id, db_conn) == None:
        deleted = True
    return deleted

#in: summoner info hash
#out: api revision date
def Get_Summ_Revision_Date(summ_info):
    return summ_info['revisionDate']

#in: summ info hash
#out: summ id
def Get_Summ_ID(summ_info):
    return summ_info['id']

#in: summ info hash
#out: summ name
def Get_Summ_Name(summ_info):
    return summ_info['name']

