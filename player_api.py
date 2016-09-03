#prog_name: player_api.py
#purpose: player data pull from riot api

from req_builder import api_request
from operator import itemgetter
from db_connections import Player_Data_CRUD, Champ_Data_CRUD

#player object
#used to map information to database
#call methods to populate values
#make decisions regarding pulling and pushing data
#all api calls need to be 1 call for easier tracking, unless absolutely necessary.
class Player():
    def __init__(self, summ_name):
        self.summ_name = summ_name.lower()
        self.summ_id = -1
        self.summ_api_data = {}
        self.api_rev_date = -1
        self.match_list = []
        self.main_champ_id = -1
        self.main_champ_name = ''
        self.main_lane = ''
        self.main_role = ''
        self.player_db_conn = Player_Data_CRUD(self.summ_id)
        self.player_db_row = () #named tuple
        self.api_calls = 0

    def get_summ_id(self):
        return self.summ_id

    def get_summ_api_data(self):
        return self.summ_api_data

    def get_api_rev_date(self):
        return self.api_rev_date

    def pull_player_api_data(self):
        req = api_request('summ_name_to_id', self.summ_name)
        player_info = req.make_request()
        summ_id = player_info[self.summ_name]['id']
        revision_date = player_info[self.summ_name]['revisionDate']
        self.summ_id = summ_id
        self.summ_api_data = player_info[str(self.summ_name)]
        self.api_rev_date = revision_date
        self.api_calls += 1

    def pull_match_list(self):
        opt_params = {
        'rankedQueues' : 'TEAM_BUILDER_DRAFT_RANKED_5x5', 
        'seasons' : 'SEASON2016'
        }
        self.match_list_data = Player_Matches(self.summ_id, optional_api_params = opt_params)
        self.api_calls += 1

    def set_ranked_mains(self):
        self.pull_match_list()
        self.main_champ_id = self.match_list_data.calc_main_champ()
        self.set_main_champ_name()
        self.main_lane = self.match_list_data.calc_main_lane()
        self.main_role = self.match_list_data.calc_main_role()

    #should the player object be pushing database updates?
    # i guess? it seems like the main driver for interactions is the player object
    # as it is also the main focus and is used to populate all other databases.

    def set_league(self):
        req = api_request('league_entry', self.summ_id)
        league_data = (req.make_request())[str(self.summ_id)][0]
        self.league = league_data['tier']
        self.division = league_data['entries'][0]['division']
        self.api_calls += 1

    def pull_update(self):
        self.set_ranked_mains()
        self.set_league()
        
    def push_db_update(self):
        self.player_db_conn.add_Mains(self.main_lane, self.main_champ_name, self.main_role)
        self.player_db_conn.add_League(self.league, self.division)

    def data_is_current(self):
        action = 'no action'
        self.player_db_row = self.player_db_conn.read_summ_row()

        if not self.needs_create(): #creates summoner row in player_data table
            self.player_db_conn.create_summoner(self.summ_name, self.api_rev_date)
            action = 'create'
        elif self.needs_update(): #updates summoner row in player_data table
            self.player_db_conn.update_summoner(self.summ_name, self.api_rev_date)
            action = 'update'
        return action

    def needs_create(self):
        exists = False if self.player_db_row == [] else True
        return exists

    def needs_update(self):
        update = True if self.player_db_row[0].revision_date < self.api_rev_date else False
        return update

    #want to put this through a rate limiter queue first
    # def pull_api_data(self, api_req):
    #     return api_req.make_request() #actually gets put into a queue.

    def set_main_champ_name(self):
        champ_name = Champ_Data_CRUD().champ_id_to_name(self.main_champ_id)
        self.main_champ_name = champ_name


class Player_Matches():
    def __init__(self, summ_id, optional_api_params = {}):
        self.summ_id = summ_id
        #out: list of hash objects with some information provided
        #TODO: begin_time and end_time
        self.match_list_basics = self.pull_match_list(optional_api_params)
        self.match_id_list = []
        self.champ_freq_list = []
        self.lane_freq_list = []
        self.role_freq_list = []
        self.others_ids = []

    #game-v1.3 api endpoint
    #pulls the same/similar data as provided by post-match screen
    #return: list and some basic match information
    # def get_recent_match_data(self):

    #gets list of matches as specified by optional params
    #decorator to add specifity to matches retrieved?
    def pull_match_list(self, optional_api_params):
        req = api_request('match_list', self.summ_id, optional_params = optional_api_params)
        response = req.make_request()
        return response['matches']

    #out: list of match ids
    def get_match_id_list(self):
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
    # TODO:
    # def allies_and_opponents(self):
    #     others_ids_string = ','.join(self.others_ids)
    #     req = api_request('basic_summ_info', others_ids_string)
    #     others_info = req.make_request()
    #     return others_info


class Match_Details():
    def __init__(self, match_id):
        self.match_id = match_id
        # straight riot api data pull
        self.details = self.pull_match_details()

    def pull_match_details(self):
        req = api_request('match_details', self.match_id)
        return req.make_request()








