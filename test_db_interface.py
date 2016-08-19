#test db_interface

import config
import req_builder
import db_interface
import db_helper

#get player info from riot
old = {'333035': {'profileIconId': 1112, 'revisionDate': 1, 'id': 333035, 'name': 'PinkBunnySoul', 'summonerLevel': 30}}

new = {'333035': {'profileIconId': 1112, 'revisionDate': 1465276217000, 'id': 333035, 'name': 'PinkBunnySoul', 'summonerLevel': 30}}

#get db connection
conn = db_helper.Connect()

#my_summ_info = summ_info[str(config.my_summ_id)]
old_summ_info = old[str(config.my_summ_id)]
new_summ_info = new[str(config.my_summ_id)]

    #create record
if (db_interface.Create_Summoner(old_summ_info, conn)):
    print('Create_Summoner is good!')

#check record
row1 = db_interface.Get_Summoner_Row(config.my_summ_id, conn)
print(row1)
if row1[0][2] == 1:
    print('get summ row working!')

#should be updated, no. return false
if db_interface.Update_Summoner_Decision(row1[0][2], 1, conn) == False:
    print('check summ status false working')

#should be updated, then update. return true
if db_interface.Update_Summoner_Decision(row1[0][2], 1465276217000, conn) == True:
    print('check summ status true working')

#update record
if db_interface.Update_Summoner(new_summ_info, conn) == True:
    print('summ updated!')

#recheck record
row2 = db_interface.Get_Summoner_Row(config.my_summ_id, conn)
if row2[0][2] == 1465276217000:
    print('summ status updated and checked')

#delete record
if db_interface.Delete_Summoner(config.my_summ_id, conn) == True:
    print("summoner deleted")