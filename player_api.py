#prog_name: player_api.py
#purpose: player data pull from riot api

from req_builder import api_request
from operator import itemgetter
from db_connections import Player_Data_CRUD, Champ_Data_CRUD

#player object
#used to map information to database
#call methods to populate values
class Player():
    def __init__(self, summ_name):
        self.summ_name = summ_name.lower()
        self.summ_id = self.summ_name_to_id()
        self.summ_api_data = self.get_api_data()
        self.api_revision_date = self.get_api_revision_date()

    #given summoner name, determine summoner id
    def summ_name_to_id(self):
        req = api_request('summ_name_to_id', self.summ_name)
        player_info = req.make_request()
        summ_id = player_info[self.summ_name]['id']
        return summ_id

    def get_api_data(self):
        req = api_request('basic_summ_info', self.summ_id)
        player_info = req.make_request()
        return player_info[str(self.summ_id)]

    #with summoner id retrieved, determine last api revision date (date updated)
    def get_api_revision_date(self):
        revision_date = self.summ_api_data['revisionDate']
        return revision_date

    def get_match_list(self):
        opt_params = {'rankedQueues' : 'TEAM_BUILDER_DRAFT_RANKED_5x5', 'seasons' : 'SEASON2016'}
        self.ranked_match_list_data = Player_Matches(self.summ_id, optional_api_params = opt_params)

    def get_ranked_mains(self):
        self.get_match_list()
        self.main_champ_id = self.ranked_match_list_data.calc_main_champ()
        self.main_lane = self.ranked_match_list_data.calc_main_lane()
        self.main_role = self.ranked_match_list_data.calc_main_role()

    #should the player object be pushing database updates?
    # i guess? it seems like the main driver for interactions is the player object
    # as it is also the main focus and is used to populate all other databases.

    def get_league(self):
        req = api_request('league_entry', self.summ_id)
        league_data = (req.make_request())[str(self.summ_id)][0]
        self.league = league_data['tier']
        self.division = league_data['entries'][0]['division']

    def push_update(self):
        player_db_conn = Player_Data_CRUD(self.summ_id)
        if (player_db_conn.Update_Create(self.summ_api_data) != 'no action'):
            self.get_ranked_mains()
            player_db_conn.Add_Mains(self.main_lane, self.get_champ_name(), self.main_role)
            self.get_league()
            player_db_conn.Add_League(self.league, self.division)

    #want to put this through a rate limiter queue first
    # def pull_api_data(self, api_req):
    #     return api_req.make_request() #actually gets put into a queue.

    def get_champ_name(self):
        champ_name = Champ_Data_CRUD().champ_id_to_name(self.main_champ_id)
        return champ_name


class Player_Matches():
    def __init__(self, summ_id, optional_api_params = {}):
        self.summ_id = summ_id
        #out: list of hash objects with some information provided
        #TODO: begin_time and end_time
        self.match_list_basics = self.get_match_list(optional_api_params)

    #game-v1.3 api endpoint
    #pulls the same/similar data as provided by post-match screen
    #return: list and some basic match information
    # def get_recent_match_data(self):

    #gets list of matches as specified by optional params
    #decorator to add specifity to matches retrieved?
    def get_match_list(self, optional_api_params):
        req = api_request('match_list', self.summ_id, optional_params = optional_api_params)
        response = req.make_request()
        return response['matches']

    #out: list of match ids
    def get_match_id_list(self):
        self.match_id_list = []
        for matches in self.match_list_basics:
            self.match_id_list.append(matches['id'])

    #determines champ played frequency and most played champ
    def calc_main_champ(self):
        self.champ_freq_list = self.calc_main('champion')
        main_champ_id = self.highest_freq_in_dict(self.champ_freq_list)
        return main_champ_id

    #determines lanes played frequency and most played lane
    def calc_main_lane(self):
        self.lane_freq_list = self.calc_main('lane')
        main_lane = self.highest_freq_in_dict(self.lane_freq_list)
        return main_lane

    def calc_main_role(self):
        self.role_freq_list = self.calc_main('role')
        main_role = self.highest_freq_in_dict(self.role_freq_list)
        return main_role

    def highest_freq_in_dict(self, freq_list):
        return max(freq_list.items(), key = itemgetter(1))[0]

    def calc_main(self, parameter):
        param_dict = {}
        for matches in self.match_list_basics:
            param_id = matches[parameter]
            if param_id not in param_dict:
                param_dict[param_id] = 1
            else:
                param_dict[param_id] = param_dict[param_id] + 1
        return param_dict

    # def player_match_stats(self):
    #     #TODO: make match data object for each match

    #returns hash of summoner information, namely {id: id, name, revisionDate}
    def allies_and_opponents(self):
        others_ids_string = ','.join(self.others_ids)
        req = api_request('basic_summ_info', others_ids_string)
        others_info = req.make_request()
        return others_info


class Match_Details():
    def __init__(self, match_id):
        self.match_id = match_id
        # straight riot api data pull
        self.details = self.get_match_details()

    def get_match_details(self):
        req = api_request('match_details', self.match_id)
        return req.make_request()


# player make match list - representing aggregate player information (that can be obtained via match list)
    # match list object represents aggregate match statistics that can only be obtained via the match details
    # match list with function calc champ main returns value to player object 
    # match list make match data objects
        # match data object has data members for statistics in a single match

# user make request to site, request added to queue
# 
# init queue
# queue is evaluated
# user inputs summoner name - requests added to queue
# 






