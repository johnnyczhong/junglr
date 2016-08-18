#test db_interface

import config
import req_builder
import db_interface

#get player info from riot
old_summ_info = {'333035': {'profileIconId': 1112, 'revisionDate': 1, 'id': 333035, 'name': 'PinkBunnySoul', 'summonerLevel': 30}}

new_summ_info = {'333035': {'profileIconId': 1112, 'revisionDate': 1465276217000, 'id': 333035, 'name': 'PinkBunnySoul', 'summonerLevel': 30}}

#get db connection
conn = db_interface.Get_DB_Connection()

#my_summ_info = summ_info[str(config.my_summ_id)]
my_summ_info = db_interface.Parse_Dict(summ_info, str(config.my_summ_id))

try:
    #create record
    if (db_interface.Create_Summoner(old_summ_info, conn)):
        print('Create_Summoner is good!')

    #check record
    row = db_interface.Get_Summoner_Row(config.my_summ_id, conn)
    if row[2] == 1 and row != None:
        print('get summ row working!')

    #should be updated, no. return false
    if Check_Summoner_Status(row, 1, conn) == False:
        print('check summ status false working')

    #should be updated, then update. return true
    if Check_Summoner_Status(row, 1465276217000, conn) == True:
        print('check summ status true working')

    #update record
    

    #recheck record

    #delete record
    if db_interface.Delete_Summoner(config.my_summ_id, conn) == False:
    print("didn't delete!")
except:
    print('something broken!')
