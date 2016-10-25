# purpose: build http requests for information from main
# make call to riot api
# parse information from riot (json)
# return parsed information to main
# need something to be in the way of the player_api 

#can be separated out to import only what's necessary later
from config import api_key 
from urllib.request import Request, urlopen
from urllib.request import HTTPError, URLError
from urllib.parse import urlencode
import urllib.response
import json
import time

#could look into subclassing, but this will do for now.
class api_request():
    def __init__(self, req_type, required_param, optional_params = {}, region = 'na', rate_limited = True):
        self.req_type = req_type
        self.required_param = urllib.parse.quote(str(required_param))
        self.optional_params = optional_params
        self.region = region
        self.header = False
        self.rate_limited = rate_limited
        self.url = self.build_url()
        self.make_request()

    def make_request(self):
        try:
            req = Request(self.url) #request object, create header?
            with urlopen(req) as f:
                response = api_response(f, self.rate_limited)
        except HTTPError as error:
            response = api_response(error, self.rate_limited)
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
        if response.code == 404:
            abstracted = 'Not Found' # doesn't exist
        elif response.code == 200:
            abstracted = response.body # valid response, return body
        elif response.code == 429 or response.code == 503 or response.code == 500:
            abstracted = 'Retry'
            if response.retry_after:
                time.sleep(response.retry_after + 1) # actual rate limiting
                print('RATE LIMITED')
            else:
                time.sleep(1) # annoying internal server rate limiting
        return abstracted

    def build_url(self):
        url = ''
        query_string = urlencode(self.optional_params)
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
        url = url + '?{0}&api_key={1}'.format(query_string, api_key)
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


#used to parse the rate limit returned in the riot api response header: 'X-Rate-Limit-Count'
#example: 'X-Rate-Limit-Count: 1:10,1:600'

# used to handle response from http request
class api_response():
    def __init__(self, resp, rate_limited = True):
        self.body = json.loads(resp.read().decode('utf-8'))
        self.code = resp.getcode()
        print(self.code)
        self.header = dict(resp.info())
        self.retry_after = False
        self.rl = rate_limited
        rl_header = 'X-Rate-Limit-Count'
        if rl_header in self.header:
            print(self.header[rl_header])

    def get_rate_limits(self):
        
        rl_string = self.header[rl_header]
        rl_list = rl_string.strip().split(',')
        self.short_rate_limit = rl_list[0].strip().split(':')
        self.long_rate_limit = rl_list[1].strip().split(':')
        print(self.short_rate_limit, self.long_rate_limit)
        if 'Retry-After' in self.header:
            self.retry_after = self.header['Retry-After']
            print(self.retry_after)








