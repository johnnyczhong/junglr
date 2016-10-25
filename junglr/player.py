#prog_name: player_api.py
#purpose: player data pull from riot api

import req_builder
# used to get greatest value in dict
import operator
# thread access
import threading
import config
import mongo_helper
import time
import collections
import match
import copy as cp
import numpy as np
matches_collection = 'matches'
summoners_collection = 'summoners'

#player object
class Player():
    def __init__(self, summ_name, rate_limiter):
        self.summ_name = ''.join(summ_name.lower().split())
        self.match_list = []
        self.player_db_row = () #named tuple
        self.current_season = config.current_season
        self.rate_limiter = rate_limiter
        self.info_hash = {}
        self.update_thread()

    def update_thread(self):
        t = threading.Thread(target=self.update_procedure)
        t.start()

    def update_procedure(self):
        action = self.basic_update()
        job_list = (self.set_ranked_mains, 
            self.set_league,
            self.get_full_match_details,
            self.commit_db,
            self.agg_match_calculations,
            self.commit_db)
        if action == 'update':
            for jobs in job_list:
                jobs()
            print(self.summ_name + ' done!')

    def commit_db(self):
        db_conn = mongo_helper.Connection()
        db_conn.update('summoners', 
            {'summId': self.info_hash['summId']}, 
            self.info_hash, 
            force = True)

    def set_ranked_mains(self):
        was_set = False
        match_list_response = self.pull_match_list()
        if match_list_response:
            self.champ_id_to_name()
            self.info_hash['mainChamp'] = self.calc_main_champ()
            self.info_hash['mainLane'] = self.calc_main_lane()
            self.info_hash['mainRole'] = self.calc_main_role() 
            self.info_hash['matchList'] = self.get_match_list()
            was_set = True
        return was_set

    def set_league(self):
        was_set = False
        league_data_req = self.make_rl_call(req_builder.api_request, 'league_entry', self.info_hash['summId'])
        if league_data_req != 'Not Found':
            league_data = league_data_req[str(self.info_hash['summId'])][0]
            self.info_hash['league'] = league_data['tier']
            self.info_hash['division'] = league_data['entries'][0]['division']
            was_set = True
        return was_set

    def get_full_match_details(self):
        for m in self.info_hash['matchList']:
            match.Match_Details(m['matchId'], self.rate_limiter)
        
    #makes api data pull for basic summoner info: id, revisionDate
    #compares api data and db data
    def basic_update(self):
        db_action = 'no action'
        response_code = self.pull_player_api_data()
        if response_code == 'Not Found':
            db_action = 'no action'
        else:
            db_action = self.update_last_modified()
        return db_action

    def update_last_modified(self):
        db_conn = mongo_helper.Connection()
        self.summ_db_data = db_conn.find('summoners', {'summId': self.info_hash['summId']})
        return self.create_or_update()

    def make_rl_call(self, func, *args, **kwargs):
        retry = True
        rl_message = 'Rate limit exceeded'
        while retry:
            self.rate_limiter.cv.acquire()
            self.rate_limiter.counter += 1
            self.rate_limiter.cv.wait_for(self.rate_limiter.check_lock, 10)
            api_data = func(*args, **kwargs)
            if api_data.response != 'Retry':
                retry = False
            self.rate_limiter.cv.release()
        return api_data.response

    def pull_player_api_data(self):
        api_data = self.make_rl_call(req_builder.api_request, 'summ_name_to_id', self.summ_name)
        if api_data != 'Not Found':
            self.info_hash['summId'] = api_data[self.summ_name]['id']
            self.info_hash['summNameLower'] = self.summ_name
            self.info_hash['summName'] = api_data[str(self.summ_name)]['name']
            self.info_hash['apiRevDate'] = api_data[self.summ_name]['revisionDate']
        return api_data

    def create_or_update(self):
        db_action = 'no action'
        if self.summ_db_data == None or self.summ_db_data['apiRevDate'] < self.info_hash['apiRevDate']:
            db_action = 'update'
        return db_action

    def pull_match_list(self):
        queue_type = {
        'rankedQueues' : 'TEAM_BUILDER_DRAFT_RANKED_5x5', 
        'seasons' : self.current_season
        }
        api_data = self.make_rl_call(req_builder.api_request, 'match_list', self.info_hash['summId'], optional_params = queue_type)
        match_list_data = api_data
        if (match_list_data != {} and 
            match_list_data['totalGames'] != 0):
            self.match_list = match_list_data['matches']
            k = 'Total_Games_{}'.format(queue_type['seasons'])
            v = match_list_data['totalGames']
            self.info_hash[k] = v
        else:
            self.match_list = None
        return api_data

    #out: list of match ids
    def get_match_list(self):
        match_id_list = []
        for matches in self.match_list:
            match_id_list.append(matches)
        return match_id_list

    def champ_id_to_name(self):
        db_conn = mongo_helper.Connection()
        self.champ_mapping = db_conn.find('static_data', {'document_name': 'champion_info'})

    def get_champ_name(self, champ_id):
        champ_name = self.champ_mapping[str(champ_id)]['name']
        return champ_name

    def map_champ_freq_to_name(self, champs_played_hash):
        champ_name_freq_list = {}
        for k, v in champs_played_hash.items():
            k_name = self.get_champ_name(k)
            champ_name_freq_list[k_name] = v
        return champ_name_freq_list

    def keys_as_strings(self, hash):
        out_hash = {}
        for k, v in hash.items():
            out_hash[str(k)] = v
        return out_hash

    #determines champ played frequency and most played champ
    def calc_main_champ(self):
        self.champ_id_freq_list = self.calc_main('champion')
        games_played = self.calc_games_played('champion')
        self.info_hash['champStats'] = self.keys_as_strings(games_played)
        main_champ_id = self.highest_freq_in_dict(self.champ_id_freq_list)
        main_champ_name = self.get_champ_name(main_champ_id)
        return main_champ_name

    #determines lanes played frequency and most played lane
    def calc_main_lane(self):
        self.lane_freq_list = self.calc_main('lane')
        games_played = self.calc_games_played('lane')
        self.info_hash['laneStats'] = games_played
        main_lane = self.highest_freq_in_dict(self.lane_freq_list)
        return main_lane

    def calc_main_role(self):
        self.role_freq_list = self.calc_main('role')
        games_played = self.calc_games_played('role')
        self.info_hash['roleStats'] = games_played
        main_role = self.highest_freq_in_dict(self.role_freq_list)
        return main_role

    def highest_freq_in_dict(self, freq_list):
        return max(freq_list.items(), key = operator.itemgetter(1))[0]

    def calc_main(self, parameter):
        param_dict = {}
        for matches in self.match_list:
            param_id = matches[parameter]
            if param_id not in param_dict:
                param_dict[param_id] = 1
            else:
                param_dict[param_id] = param_dict[param_id] + 1
        return param_dict

    def calc_games_played(self, parameter):
        param_dict = {}
        for matches in self.match_list:
            param_id = matches[parameter]
            if param_id not in param_dict:
                param_dict[param_id] = {'played': 1}
            else:
                param_dict[param_id]['played'] = param_dict[param_id]['played'] + 1
        return param_dict


    def init_stat_hashes(self):
        categories = ('win', 'loss', 'total')
        raw_data = {'raw_data': []}
        calculated_data = {'avg': 0, 'stdev': 0}
        calc_stat_hash = self.assemble_stats_hash(calculated_data)
        raw_data_hash = self.assemble_stats_hash(raw_data)
        self.base_stats = self.create_base_stats_hash(calc_stat_hash, categories)
        self.base_raw_data = self.create_base_stats_hash(raw_data_hash, categories)
        self.champ_stats = self.create_champ_stats_hash(calc_stat_hash, categories)
        self.champ_raw_data = self.create_champ_stats_hash(raw_data_hash, categories)

    def agg_match_calculations(self):
        self.init_stat_hashes()
        for m in self.match_list:
            match_id = m['matchId']
            match_details = self.get_db_match_details(match_id)
            duration = match_details['matchDuration']
            participant_data = self.get_db_match_participant_data(match_details)
            team_data = self.get_db_match_team_data(match_details)
            param_dict = {}
            param_dict['champ'] = participant_data['championId']
            param_dict['role'] = participant_data['lane'] #lane is an easier identifier
            self.update_stats(team_data, participant_data, duration, **param_dict)
        self.recursive_hash_analysis(self.base_raw_data, self.base_stats)
        self.recursive_hash_analysis(self.champ_raw_data, self.champ_stats)
        self.compile_player_stats()

    def compile_player_stats(self):
        base_stats_name = '{}Stats'.format(self.current_season)
        self.info_hash[base_stats_name] = self.base_stats
        self.info_hash['champ' + base_stats_name] = self.champ_stats

    # wanna walk through each match once and only once.
    def update_stats(self, team_data, participant_data, duration, **param_dict):
        frame_markers = [9, 14, 19, 24, 29, 34, 39, -1] #markers for frame data
        num_frame_markers = len(frame_markers)
        match_minutes = duration/60
        game_lengths = ('atLeast10', 'atLeast15', 'atLeast20', 'atLeast25',
            'atLeast30', 'atLeast35', 'atLeast40', 'longerThan40')
        frame_data_points = ('at10', 'at15', 'at20', 'at25', 
            'at30', 'at35', 'at40', 'atEnd',)
        wlt = 'win' if team_data['winner'] else 'loss'
        champ = str(param_dict['champ']) 
        wl_base_hash, total_base_hash = self.base_raw_data[wlt], self.base_raw_data['total'] #win/loss/total hash
        wl_champ_hash, total_champ_hash = self.champ_raw_data[wlt][champ], self.champ_raw_data['total'][champ] #win/loss/total hash for champs

        # there is frame data in this match
        if 'frameData' in team_data:
            tFrameData = team_data['frameData']
            pFrameData = participant_data['frameData']
            in_hashes = (wl_base_hash, total_base_hash,
                wl_champ_hash, total_champ_hash,)

            i = 0
            while i <= 7 and match_minutes > ((frame_markers[i]) + 1):
                gl = game_lengths[i]
                fdp = frame_data_points[i]
                fm = frame_markers[i]
                for k in pFrameData.keys():
                    for h in in_hashes:
                        h['participantFrameData'][k][fdp]['raw_data'].append(pFrameData[k][fm])
                for k in tFrameData.keys():
                    for h in in_hashes:
                        h['teamFrameData'][k][fdp]['raw_data'].append(tFrameData[k][fm])
                for h in in_hashes:
                    h['gameDurations'][gl] += 1
                i += 1
            for h in in_hashes:
                h['gamesPlayed'] += 1
                for keys in h['participantSummaryData'].keys():
                    if participant_data['stats'][keys]:
                        h['participantSummaryData'][keys]['raw_data'].append(1)
                    else:
                        h['participantSummaryData'][keys]['raw_data'].append(0)
                for keys in h['teamSummaryData'].keys():
                    if team_data[keys]:
                        h['teamSummaryData'][keys]['raw_data'].append(1)
                    else:
                        h['teamSummaryData'][keys]['raw_data'].append(0)

    # purpose: calculate avg/stdev from array. delete array after
    # should this know the structure of the hash?
    # go all the way down, calculate the average?
    def recursive_hash_analysis(self, raw_data_hash, stats_hash):
        for k, v in raw_data_hash.items():
            if type(v) == dict:
                values = stats_hash[k]
                self.recursive_hash_analysis(v, values)
            else:
                if type(v) == int:
                    stats_hash[k] += v
                elif len(v) > 0:
                    stats_hash['avg'] = np.average(v)
                    stats_hash['stdev'] = np.std(v)
                    print(str(k) + str(stats_hash))
                else:
                    stats_hash['avg'] = None
                    stats_hash['stdev'] = None


    def assemble_stats_hash(self, data_points):
        participant_frame_data_list = ('jungleMinionsKilledPerFrame', 'totalGoldPerFrame', 
            'minionsKilledPerFrame', 'xpPerFrame', 'levelPerFrame',
            'jungleMinionsAdvPerFrame', 'goldAdvPerFrame', 'minionsAdvPerFrame', 
            'xpAdvPerFrame', 'levelAdvPerFrame',)
        team_frame_data_list = ('totalGoldPerFrame', 'xpPerFrame',
            'totalLevelPerFrame', 'totalGoldAdvPerFrame',
            'xpAdvPerFrame', 'totalLevelAdvPerFrame',)
        frame_data_hash = {'gamesPlayed': 0}
        frame_data_hash['teamFrameData'] = self.init_frame_data_hash(team_frame_data_list, data_points)
        frame_data_hash['participantFrameData'] = self.init_frame_data_hash(participant_frame_data_list, data_points)
        frame_data_hash['participantSummaryData'] = self.init_participant_summary_data(data_points)
        frame_data_hash['teamSummaryData'] = self.init_team_summary_data(data_points)
        frame_data_hash['gameDurations'] = self.init_game_lengths()
        return frame_data_hash

    def get_db_match_participant_data(self, match_details):
        participant_location = match_details['participantMapping'][str(self.info_hash['summId'])]
        team, participant_id = str(participant_location['team']), str(participant_location['participantId'])
        participant_data = match_details['teams'][team]['participants'][participant_id]
        return participant_data

    def get_db_match_team_data(self, match_details):
        participant_location = match_details['participantMapping'][str(self.info_hash['summId'])]
        team = str(participant_location['team'])
        team_data = match_details['teams'][team]
        return team_data

    def get_db_match_details(self, match_id):
        db_conn = mongo_helper.Connection()
        match_details = db_conn.find(matches_collection, {'matchId': match_id})
        return match_details
            
    def create_champ_stats_hash(self, stat_hash, cats):
        # per w/l/t, per champion
        champ_stats_hash = {}
        for c in cats:
            champ_stats_hash[c] = {}
            for k in self.champ_id_freq_list.keys():
                champ_stats_hash[c][str(k)] = cp.deepcopy(stat_hash)
        return champ_stats_hash

    def create_base_stats_hash(self, stat_hash, cats):
        # per w/l/t
        base_stats = {}
        for c in cats:
            base_stats[c] = cp.deepcopy(stat_hash)
        return base_stats

    def init_participant_summary_data(self, data_points):
        participant_stats_list = ('kills', 'deaths', 'assists', 'minionsKilled',
            'neutralMinionsKilled', 'wardsPlaced', 'wardsKilled',)
        participant_summary_data = {}
        for p in participant_stats_list:
            participant_summary_data[p] = cp.deepcopy(data_points)
        return participant_summary_data

    def init_team_summary_data(self, data_points):
        team_summary_data = {}
        team_stats_list = ('firstDragon', 'firstBaron', 
            'firstRiftHerald', 'firstTower',)
        team_frame_data = {}
        for t in team_stats_list:
            team_summary_data[t] = cp.deepcopy(data_points)
        return team_summary_data

    def init_frame_data_hash(self, param_list, data_points):
        frame_data_points = ('at10', 'at15', 'at20', 'at25',
            'at30', 'at35', 'at40', 'atEnd',)
        frame_data_at_min = {}
        for f in frame_data_points:
            frame_data_at_min[f] = cp.deepcopy(data_points)
        frame_data = {}
        for p in param_list:
            frame_data[p] = cp.deepcopy(frame_data_at_min)
        return frame_data

    def init_game_lengths(self):
        game_lengths = ('atLeast10', 'atLeast15', 'atLeast20', 'atLeast25',
            'atLeast30', 'atLeast35', 'atLeast40', 'longerThan40')
        game_duration = {}
        for g in game_lengths:
            game_duration[g] = 0
        return game_duration

