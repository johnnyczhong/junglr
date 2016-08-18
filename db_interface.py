#author: johnny
#purpose: provide functions to CRUD the postgres db

import db_helper

#in: hash of summoner info (id, name, rev_date)
#out: boolean if player info needs to be updated
#purpose: carries out action based on if player should be updated
def Get_Summoner_Row(summ_id, db_conn): #optional param of db_cursor?
    tb = 'player_data'
    query = 'select * from player_data where summ_id = ' + str(summ_id) + ';'
    row = db_helper.Fetch(db_conn, query)
    return row

#in: dict of singular summ info
#out: true if player record created, false if not
def Create_Summoner(summ_info, db_conn):
    created = False
    summ_id = str(summ_info['id'])
    summ_name = str(summ_info['name'])
    rev_date = str(summ_info['revisionDate'])

    create_query = "insert into player_data (summ_id, summ_name, revision_date) values (%s, '%s', %s);" %(summ_id, summ_name, rev_date)
    created = db_helper.Commit(db_conn, create_query)
    return created

#in: summ info
#out: true if record updated, false if not
def Update_Summoner(summ_info, db_conn):
    summ_id = str(summ_info['id'])
    summ_name = str(summ_info['name'])
    rev_date = str(summ_info['revisionDate'])
    update_query = "update player_data set summ_name = '%s', revision_date = %s where summ_id = %s;" %(summ_name, rev_date, summ_id)
    updated = db_helper.Commit(db_conn, update_query)
    return updated

#in: summ id
#out: true if deleted, false otherwise
def Delete_Summoner(summ_id, db_conn):
    delete_query = 'delete from player_data where summ_id = ' + str(summ_id) + ';'
    deleted = db_helper.Commit(db_conn, delete_query)
    if Get_Summoner_Row(summ_id, db_conn) == None:
        deleted = True
    return deleted

#return: true if summ was updated or created, false if no change
def Check_Summoner_Status(row, api_revision_date, db_conn):
    do_update = True

    if row == None:
        do_update = Create_Summoner(summ_info, db_conn)
    elif row[2] <= api_revision_date:
        do_update = False
    else:
        do_update = Update_Summoner(summ_info, db_conn)
    return do_update
