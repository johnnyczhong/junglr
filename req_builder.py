# purpose: build http requests for information from main
# make call to riot api
# parse information from riot (json)
# return parsed information to main

from config import api_key #can be separated out to import only what's necessary later
from urllib.request import Request, urlopen
from urllib.request import HTTPError, URLError 
from contextlib import closing
from json import loads 

#in: url request
#out: json object dict type for python
def D_Make_Request(url):
    non_json = None
    try:
        req = Request(url) #request object, create header?
        with urlopen(req) as f:
            #parse json data
            non_json = loads(f.read().decode('utf-8'))
    except HTTPError as error:
        print(error)
    except URLError as error:
        print('URLError occurred.')
    return non_json

def Build_URL(req_type, value = '', region = 'na'):
    url = ''
    if req_type == 'match_history':
        url = 'https://' + region + '.api.pvp.net/api/lol/' + region + '/v1.3/game/by-summoner/' + str(value) + '/recent?api_key=' + api_key
    elif req_type == 'champ_name':
        url = 'https://global.api.pvp.net/api/lol/static-data/' + region + '/v1.2/champion/' + str(value) + '?api_key=' + api_key 
    elif req_type == 'basic_summ_info':
        url = 'https://' + region + '.api.pvp.net/api/lol/' + region + '/v1.4/summoner/' + str(value) + '?api_key=' + api_key
    elif req_type == 'summ_name_to_id':
        url = 'https://' + region + '.api.pvp.net/api/lol/' + region + '/v1.4/summoner/by-name/' + value + '?api_key=' + api_key
    elif req_type == 'champ_name':
        url = 'https://global.api.pvp.net/api/lol/static-data/' + region + '/v1.2/champion/' + value + '?api_key=' + api_key
    elif req_type == 'champ_data_static':
        url ='https://global.api.pvp.net/api/lol/static-data/' + region + '/v1.2/champion?api_key=' + api_key
    return url













