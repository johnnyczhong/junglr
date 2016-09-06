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
from json import loads 


#could look into subclassing, but this will do for now.
class api_request():
    def __init__(self, req_type, required_param, optional_params = {}, region = 'na'):
        self.req_type = req_type
        self.required_param = str(required_param)
        self.optional_params = optional_params
        self.region = region
        self.headers = {}
        self.response_body = {}
        self.response_code = 0
        self.url = self.build_url()
        self.make_request()

    def analyze_response(self):
        

    def make_request(self):
        try:
            req = Request(self.url) #request object, create header?
            print(self.url)
            with urlopen(req) as f:
                response = api_response(f)
                self.response_body = response.body
                self.response_code = response.code
        except HTTPError as error:
            print(error)
            response = error
            self.response_code = response.code
        # except URLError as error:
        #     print('URLError occurred.')
        #     response = error
        return response
    

    # def make_request(self):
    #     req = Request(self.url) #request object, create header?
    #     print(self.url)
    #     with urlopen(req) as f:
    #         response = api_response(f)
    #         self.response_body = response.body
    #         self.response_code = response.code
    #     return response

    def build_url(self):
        url = ''
        query_string = urlencode(self.optional_params)
        champ_req = ['champ_name', 'champ_data_static']
        match_req = ['match_details', 'match_list']
        game_req = ['recent_games']
        summ_req = ['basic_summ_info', 'summ_name_to_id']
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
        return url + '?{0}&api_key={1}'.format(query_string, api_key)

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
        return url

    #lol-static-data-v1.2
    def champ_url(self):
        version = 'v1.2'
        url = 'https://global.api.pvp.net/api/lol/static-data/{0}/{1}/champion/'.format(self.region, version)
        if self.req_type == 'champ_name':
            url += self.required_param
        elif self.req_type == 'champ_data_static': 
            pass
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
        self.body = loads(resp.read().decode('utf-8'))
        self.code = resp.getcode()
        self.header = dict(resp.info())
        self.rl = rate_limited
        if self.rl:
            self.get_rate_limits()

    def get_rate_limits(self):
        rl_header = 'X-Rate-Limit-Count'
        rl_string = self.header[rl_header]
        rl_list = [x.strip().split(',') for x in (rl_string.strip().split(':'))]
        rl_short, rl_long = rl_list[0], rl_list[1]
        self.short_rate_limit = self.list_str_to_int(rl_short)
        self.long_rate_limit = self.list_str_to_int(rl_long)

    def list_str_to_int(self, str_list):
        return [int(x) for x in str_list]

    # def get_short_rate_limit(


# class Rate_Limiter_Queue():









