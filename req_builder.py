# author: johnny
# purpose: build http requests for information from main
# make call to riot api
# parse information from riot (json)
# return parsed information to main

import config #can be separated out to import only what's necessary later
import urllib.request
import json

#in: summ_name
#out: summ_ID
def Int_Summ_Name_to_ID(summ_name):
    req = Build_URL('summ_name_to_id', summ_name)
    player_info = D_Make_Request(req)
    return player_info[summ_name]['id']

#in: summ_id
#out: hash of summoner info
def Hash_Basic_Summ_Info(summ_id):
    req = Build_URL('basic_summ_info', summ_id)
    

#in: summ name
#out: match history
def Get_Match_History(summ_ID):
    #player_ID = Int_Summ_Name_to_ID(summ_name)
    req = Build_URL('match_history', summ_ID)
    return D_Make_Request(req)

#in: champ ID
#out: champ name
def S_CID_to_CName(champ_ID):
    req = Build_URL('champ_name', champ_ID) 
    champ_name = (D_Make_Request(req))['name']
    return champ_name

#in: url request
#out: json object dict type for python
def D_Make_Request(url):
    try:
        with urllib.request.urlopen(url) as f:
            non_json = json.loads(f.read().decode('utf-8'))
    except urllib.error.HTTPError as error:
        print(error)
    except urllib.error.URLError:
        print('URLError occurred.')
    #else:
    #    non_json = None
    return non_json

def Build_URL(req_type, value, region = 'na'):
    url = ''
    if req_type == 'match_history':
        url = 'https://' + region + '.api.pvp.net/api/lol/' + region + '/v1.3/game/by-summoner/' + str(value) + '/recent?api_key=' + config.api_key
    elif req_type == 'champ_name':
        url = 'https://global.api.pvp.net/api/lol/static-data/' + region + '/v1.2/champion/' + str(value) + '?api_key=' + config.api_key 
    elif req_type == 'basic_summ_info':
        url = 'https://' + region + '.api.pvp.net/api/lol/' + region + '/v1.4/summoner/' summ_id + '?api_key=' + config.api_key
    elif req_type == 'summ_name_to_id':
        url = 'https://' + region + '.api.pvp.net/api/lol/' + region + '/v1.4/summoner/by-name/' + value + '?api_key=' + config.api_key














