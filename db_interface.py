#author: johnny
#purpose: provide functions to CRUD the postgres db

from pgdb import connect

# init connect with db
def DB_Connect():
    connection = connect(database='johnny', host='localhost:5432', user='johnny')
    db_cursor = connection.cursor()
    return db_cursor

#in: summoner id
#out: boolean if player info needs to be updated
#purpose: carries out action based on if player should be updated
def Determine_Player_Status(summ_id, api_revision_date):
    tb = 'player_data'
    do_update = True
    #see if player exists
    query = 'select 1 from ' + tb + ' where player_id = ' + str(summ_id)
    #connect to db
    db_cursor = DB_Connect()
    db_cursor.execute(query)
    row = db_cursor.fetchone()

    #if summoner not found, create record
    if row == None:
        do_update = Create_Player(summ_id, summ_name, api_revision_date)
    #if revision_date is current (no change) row[2] is revision_date
    elif row[2] <= api_revision_date:
        do_update = False
    #otherwise, update database
    else:
        do_update = Update_Player(summ_id, summ_name, api_revision_date)

    return do_update

#insert_query = 'insert into ' + tb + ' values ' + 
