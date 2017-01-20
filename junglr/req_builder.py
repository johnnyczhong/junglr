# filename: req_builder.py

# purpose: build http requests for information from main
# make call to riot api
# parse information from riot (json)
# return parsed information to main
# need something to be in the way of the player_api 

#can be separated out to import only what's necessary later
import config
from urllib.parse import urlencode
import socket
import urllib.response
import json
from sys import getsizeof

TCP_IP = 'localhost'
TCP_PORT = 8001
BUFFER_SIZE = 4096 # 4kb

#could look into subclassing, but this will do for now.
class api_request():

    def __init__(self, req_type, required_param, optional_params = {}, region = 'na', rate_limited = True):
        self.req_type = req_type
        self.required_param = urllib.parse.quote(str(required_param))
        self.optional_params = optional_params
        self.optional_params['api_key'] = config.api_key
        self.region = region
        self.header = False
        # self.rate_limited = rate_limited
        self.url = self.build_url()
    
    def make_request(self):
        msg = str(len(self.url)) + ':' + self.url + ',' # construct netstring
        netstring = msg.encode('utf-8') # encode netstring as bytes

        # establish sockets
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(config.timeout)
        s.connect((TCP_IP, TCP_PORT))
        s.send(netstring)

        # get first chunk and figure out size of message
        bdata = s.recv(BUFFER_SIZE)
        data = bdata.decode('utf-8') # decode bytes
        size = data.split(':', 1)[0] # unpack netstring for size of incoming
        size = int(size)

        # keep receiving stream until done
        while getsizeof(bdata) < size:
            bdata += s.recv(BUFFER_SIZE)

        # close socket
        s.close()
        
        
        ddata = bdata.decode('utf-8') # decode full message
        data = ddata.split(':', 1)[1] # split and get message
        contents = json.loads(data[:-1]) # decode json, exclude trailing comma
        return contents

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
        parse = urlencode(self.optional_params)
        joined = '{}?{}'.format(url, parse)
        return joined

    #game-v1.3
    def game_url(self):
        version = 'v1.3'
        url = 'https://{0}.api.pvp.net/api/lol/{0}/{1}/game'.format(self.region, version)
        if self.req_type == 'game_req':
            url += '/by-summoner/{0}/recent'.format(self.required_param)

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

        # not really necessary to track this here
        """
        elif self.req_type == 'champ_data_static': 
            self.rate_limited = False
        """

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

