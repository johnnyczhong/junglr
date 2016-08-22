#prog_name: player_api.py
#purpose: player data pull from riot api

from req_builder import D_Make_Request
from req_builder import Build_URL

#in: list summ_name
#out: list summ_ID
def List_Summ_Name_to_ID(summ_name_list):
    summ_info_string = ','.join(summ_name_list)
    req = Build_URL('summ_name_to_id', summ_info_string)
    player_info = D_Make_Request(req)
    summ_id_list = []
    for summ_name in summ_name_list:
        summ_id_list.append(player_info[summ_name]['id'])
    return summ_id_list

#in: list of summ_id
#out: hash of summoner info
def Hash_Basic_Summ_Info(summ_id):
    str_summ_id = [str(i) for i in summ_id]
    str_csv_summ_id = ','.join(str_summ_id)
    req = Build_URL('basic_summ_info', str_csv_summ_id)
    hash_summ_info = D_Make_Request(req)
    return hash_summ_info
    

#in: summ name
#out: match history
def Get_Match_History(summ_ID):
    #player_ID = Int_Summ_Name_to_ID(summ_name)
    req = Build_URL('match_history', summ_ID)
    return D_Make_Request(req)

#in: summ_info hash
#out: revision date
def Summ_Last_Updated(agg_summ_info, summ_id):
    single_summ_info = agg_summ_info[summ_id]
    return single_summ_info['revisionDate']
