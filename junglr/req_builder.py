# purpose: build http requests for information from main
# make call to riot api
# parse information from riot (json)
# return parsed information to main
# need something to be in the way of the player_api 

#can be separated out to import only what's necessary later
from config import api_key 
import requests
import urllib.response
import json
import time

#could look into subclassing, but this will do for now.
class api_request():
    def __init__(self, req_type, required_param, optional_params = {}, region = 'na', rate_limited = True):
        self.req_type = req_type
        self.required_param = urllib.parse.quote(str(required_param))
        self.optional_params = optional_params
        self.optional_params['api_key'] = api_key
        self.region = region
        self.header = False
        self.limits = (10, 500)
        self.rate_limited = rate_limited
        self.url = self.build_url()
        self.make_request()

    def make_request(self):
        response = requests.get(self.url, params = self.optional_params) #request object, create header?
        clean_response = self.handle_response(response)
        self.response = clean_response

    # something to analyze response and provide a standard error message?
    # actions:
    # 404: return 'Not Found'
    # 503: sleep 1s, return 'Retry'
    # 429 without 'Retry-After': sleep 1s, return 'Retry'
    # 429 with 'Retry-After': sleep for retry timer, return 'Retry'
    # 200: return response body
    # 500: return 'Server Error'?
    def handle_response(self, response):

        # returns (num_calls in 10 seconds, num_calls in 600 seconds)
        def parse_rate_limits():
            num_calls = []
            split1 = []
            split0 = response.headers['X-Rate-Limit-Count'].strip().split(',')
            for i in split0:
                split1.append(i.strip().split(':'))
            for i in split1:
                num_calls.append(i[0])
            return num_calls

        if response.status_code == 404:
            abstracted = 'Not Found' # doesn't exist
        elif response.status_code == 200:
            abstracted = response.json() # valid response, return body
            if 'X-Rate-Limit-Count' in response.headers:
                rate_limits = parse_rate_limits()
                num_rate_limits = len(rate_limits)
                for i in range(num_rate_limits):
                    if rate_limits[i] == self.limits[i]:
                        time.sleep(1) 
        elif response.status_code == 429 or response.code == 503 or response.code == 500:
            abstracted = 'Retry'
            if 'Retry-After' in response.headers:
                time.sleep(response.headers['Retry-After'] + 1) # secondary rate limiting, based off Riot API limits
                print('RATE LIMITED')
            else:
                time.sleep(1) # annoying internal server rate limiting
        return abstracted

    def build_url(self):
        url = ''
        champ_req = ['champ_name', 'champ_data_static']
        match_req = ['match_details', 'match_list']
        game_req = ['recent_games']
        summ_req = ['basic_summ_info', 'summ_name_to_id', 'summ_id_to_info']
        league_req = ['league_entry']
        if self.req_type in game_req:
            url = self.game_url()
        elif self.req_type in summ_req:
            url = self.summ_url()
        elif self.req_type in champ_req:
            url = self.champ_url()
        elif self.req_type in match_req:
            url = self.match_url()
        elif self.req_type in league_req:
            url = self.league_url()
        return url

    #game-v1.3
    def game_url(self):
        version = 'v1.3'
        url = 'https://{0}.api.pvp.net/api/lol/{0}/{1}/game/'.format(self.region, version)
        if self.req_type == 'game_req':
            url += 'by-summoner/{0}/recent'.format(self.required_param)

    #summoner-v1.4
    def summ_url(self):
        version = 'v1.4'
        url = 'https://{0}.api.pvp.net/api/lol/{0}/{1}/summoner/'.format(self.region, version)
        if self.req_type == 'basic_summ_info':
            url += self.required_param
        elif self.req_type == 'summ_name_to_id':
            url += 'by-name/{0}'.format(self.required_param)
        elif self.req_type == 'summ_id_to_info':
            url += '{0}'.format(self.required_param)
        return url

    #lol-static-data-v1.2
    def champ_url(self):
        version = 'v1.2'
        url = 'https://global.api.pvp.net/api/lol/static-data/{0}/{1}/champion/'.format(self.region, version)
        if self.req_type == 'champ_name':
            url += self.required_param
        elif self.req_type == 'champ_data_static': 
            self.rate_limited = False
        return url

    #not really related, but since the riot api has no other groupings right now, this makes sense.
    #match-v2.2 and matchlist-v2.2
    def match_url(self):
        version = 'v2.2'
        url = 'https://{0}.api.pvp.net/api/lol/{0}/{1}/'.format(self.region, version)
        if self.req_type == 'match_details':
            url += 'match/{0}'.format(self.required_param)
        elif self.req_type == 'match_list':
            url += 'matchlist/by-summoner/{0}'.format(self.required_param)
        return url

    #league-v2.5
    def league_url(self):
        version = 'v2.5'
        url = 'https://{0}.api.pvp.net/api/lol/{0}/{1}/league/'.format(self.region, version)
        if self.req_type == 'league_entry':
            url += 'by-summoner/{}/entry'.format(self.required_param)
        return url

