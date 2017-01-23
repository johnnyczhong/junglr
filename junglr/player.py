#prog_name: player_api.py
#purpose: player data pull from riot api

import req_builder
import operator
import config
import mongo_helper
import match
import copy as cp
import numpy as np
matches_collection = 'matches'
summoners_collection = 'summoners'

#player object
class Player():
    def __init__(self, summ_name):
        self.summ_name = ''.join(summ_name.lower().split())
        self.match_list = []
        self.player_db_row = () #named tuple
        self.current_season = config.current_season
        self.begin_time  = config.beginTime
        self.info_hash = {}
        self.db_conn = mongo_helper.Connection()

    def read(self):
        return self.db_conn.find('summoners', {'summNameLower': self.summ_name})

    # run update process in sequence
    def update(self):
        job_list = (self.set_ranked_mains,
            self.set_league,
            self.get_full_match_details,
            self.commit_db,
            self.agg_match_calculations,
            self.commit_db)
        for jobs in job_list:
            jobs()

    # commit current information in self.info_hash to database
    def commit_db(self):
        self.db_conn.update('summoners', 
            {'summId': self.info_hash['summId']}, 
            self.info_hash, 
            force = True)

    # determine ranked main champs, lanes, roles
    def set_ranked_mains(self):

        def calc_games_played(parameter):
            param_dict = {}
            for matches in self.match_list:
                param_id = matches[parameter]
                if param_id not in param_dict:
                    param_dict[param_id] = {'played': 1}
                else:
                    param_dict[param_id]['played'] += 1
            return param_dict

        def highest_freq_in_dict(freq_list):
            return max(freq_list.items(), key = operator.itemgetter(1))[0]

        def calc_main(parameter):
            param_dict = {}
            for matches in self.match_list:
                param_id = matches[parameter]
                if param_id not in param_dict:
                    param_dict[param_id] = 1
                else:
                    param_dict[param_id] = param_dict[param_id] + 1
            return param_dict

        #determines lanes played frequency and most played lane
        def calc_main_lane():
            self.lane_freq_list = calc_main('lane')
            games_played = calc_games_played('lane')
            main_lane = highest_freq_in_dict(self.lane_freq_list)
            return main_lane

        def calc_main_role():
            self.role_freq_list = calc_main('role')
            games_played = calc_games_played('role')
            main_role = highest_freq_in_dict(self.role_freq_list)
            return main_role

        #determines champ played frequency and most played champ
        def calc_main_champ():
            self.champ_id_freq_list = calc_main('champion')
            games_played = calc_games_played('champion')
            self.info_hash['champStats'] = self.keys_as_strings(games_played)
            main_champ_id = highest_freq_in_dict(self.champ_id_freq_list)
            main_champ_name = self.get_champ_name(main_champ_id)
            return main_champ_name

        #out: list of match ids
        def get_match_list():
            match_id_list = []
            for matches in self.match_list:
                match_id_list.append(matches)
            return match_id_list

        # if match_list_response:
        self.champ_id_to_name()
        self.info_hash['mainChamp'] = calc_main_champ()
        self.info_hash['mainLane'] = calc_main_lane()
        self.info_hash['mainRole'] = calc_main_role() 
        self.info_hash['matchList'] = get_match_list()

    def pull_match_list(self):
        ranked_queues = '{},{}'.format(config.ranked_solo, config.ranked_flex)
        queue_type = {
        'rankedQueues' : ranked_queues,
        'beginTime': self.begin_time
        }
        r = req_builder.api_request('match_list', self.info_hash['summId'], optional_params = queue_type)
        match_list_data = r.make_request()
        if (match_list_data != {} and 
            match_list_data['totalGames'] != 0):
            self.match_list = match_list_data['matches']
            k = 'Total_Games'
            v = match_list_data['totalGames']
            self.info_hash[k] = v
        else:
            self.match_list = None
        return match_list_data

    # determine ranked league statistics
    def set_league(self):
        r = req_builder.api_request('league_entry', self.info_hash['summId'])
        league_data_response = r.make_request()
        #if 'status' in league_data_response and league_data_response['status']['status_code'] == 404: 
        if league_data_response == 'Not Found': #404
            league_set = False
        else:
            league_data = league_data_response[str(self.info_hash['summId'])][0]
            self.info_hash['league'] = league_data['tier']
            self.info_hash['division'] = league_data['entries'][0]['division']
            league_set = True
        return league_set

    # get each match's details, rate limited
    def get_full_match_details(self):
        for m in self.info_hash['matchList']:
            match.Match_Details(m['matchId']) # self.rate_limiter)

    def update_last_modified(self):
        self.summ_db_data = self.db_conn.find('summoners', {'summId': self.info_hash['summId']})
        db_action = 'no action'
        if self.summ_db_data == None or self.summ_db_data['apiRevDate'] < self.info_hash['apiRevDate']:
            db_action = 'update'
        return db_action

    def pull_player_api_data(self):
        r = req_builder.api_request('summ_name_to_id', self.summ_name)
        api_data = r.make_request()
        if api_data != 'Not Found':
            self.info_hash['summId'] = api_data[self.summ_name]['id']
            self.info_hash['summNameLower'] = self.summ_name
            self.info_hash['summName'] = api_data[str(self.summ_name)]['name']
            self.info_hash['apiRevDate'] = api_data[self.summ_name]['revisionDate']
        return api_data

    def champ_id_to_name(self):
        self.champ_mapping = self.db_conn.find('static_data', {'document_name': 'champion_info'})

    def get_champ_name(self, champ_id):
        champ_name = self.champ_mapping[str(champ_id)]['name']
        return champ_name

    #not used currently, due to limitations of mongodb's keys
    def map_champ_freq_to_name(self, champs_played_hash):
        champ_name_freq_list = {}
        for k, v in champs_played_hash.items():
            k_name = self.get_champ_name(k)
            champ_name_freq_list[k_name] = v
        return champ_name_freq_list

    # make integer keys into string versions for mongodb
    def keys_as_strings(self, hash):
        out_hash = {}
        for k, v in hash.items():
            out_hash[str(k)] = v
        return out_hash

    # create all stat hashes for player matches
    def init_stat_hashes(self):
        categories = ('win', 'loss', 'total')
        raw = {'raw_data' : []}
        raw0 = {'raw_data': 0}
        analyzed = {'avg': 0, 'stdev': 0}

        # returns {champId: hash_type}
        # more categories later
        def init_data_hash(hash_type):
            out_hash = {}
            for c in self.info_hash['champStats'].keys():
                out_hash[c] = cp.deepcopy(hash_type)
            return out_hash

        def create_base_stats_hash(stat_hash, cats):
            base_stats = {}
            for c in cats:
                base_stats[c] = cp.deepcopy(stat_hash)
            return base_stats

        raw_data_hashes = init_data_hash(raw)
        raw_zero_hashes = init_data_hash(0)
        analyzed_hashes = init_data_hash(analyzed)
        raw_data = {'anythingGoes': raw, 'championStats': raw_data_hashes}
        calculated_data = {'anythingGoes': analyzed, 'championStats': analyzed_hashes}
        raw_zeroes = {'anythingGoes': 0, 'championStats': raw_zero_hashes}
        calc_stat_hash = self.assemble_stats_hash(calculated_data, raw_zeroes)
        raw_data_hash = self.assemble_stats_hash(raw_data, raw_zeroes)
        self.base_stats = create_base_stats_hash(calc_stat_hash, categories)
        self.base_raw_data = create_base_stats_hash(raw_data_hash, categories)

    # iterate over every match in mongodb this player was in and analyze results
    def agg_match_calculations(self):

        def get_db_match_details(match_id):
            match_details = self.db_conn.find(matches_collection, {'matchId': match_id})
            return match_details

        def get_db_match_participant_data(match_details):
            participant_location = match_details['participantMapping'][str(self.info_hash['summId'])]
            team, participant_id = str(participant_location['team']), str(participant_location['participantId'])
            participant_data = match_details['teams'][team]['participants'][participant_id]
            return participant_data

        def get_db_match_team_data(match_details):
            participant_location = match_details['participantMapping'][str(self.info_hash['summId'])]
            team = str(participant_location['team'])
            team_data = match_details['teams'][team]
            return team_data

        self.init_stat_hashes()
        for m in self.match_list:
            match_id = m['matchId']
            match_details = get_db_match_details(match_id)
            duration = match_details['matchDuration']
            participant_data = get_db_match_participant_data(match_details)
            team_data = get_db_match_team_data(match_details)
            param_dict = {}
            param_dict['champ'] = participant_data['championId']
            self.update_stats(team_data, participant_data, duration, **param_dict)
        self.recursive_hash_analysis(self.base_raw_data, self.base_stats)
        self.compile_player_stats()

    # place match analysis results into hash that will be pushed into mongodb
    def compile_player_stats(self):
        base_stats_name = 'Stats'
        self.info_hash[base_stats_name] = self.base_stats

    # walk through given match and compile data for match analysis
    def update_stats(self, team_data, participant_data, duration, **param_dict):
        frame_markers = [9, 14, 19, 24, 29, 34, 39, -1] #markers for frame data
        num_frame_markers = len(frame_markers)
        match_minutes = duration/60
        game_lengths = ('atLeast10', 'atLeast15', 'atLeast20', 'atLeast25',
            'atLeast30', 'atLeast35', 'atLeast40', 'longerThan40')
        frame_data_points = ('at10', 'at15', 'at20', 'at25', 
            'at30', 'at35', 'at40', 'atEnd',)
        wlt = 'win' if team_data['winner'] else 'loss'
        champ = str(param_dict['champ']) #champId of the game
        wl_hash, total_hash = self.base_raw_data[wlt], self.base_raw_data['total']

        # there is frame data in this match
        if 'frameData' in team_data:
            tFrameData = team_data['frameData']
            pFrameData = participant_data['frameData']
            in_hashes = (wl_hash, total_hash)

            i = 0
            while i <= 7 and match_minutes > ((frame_markers[i]) + 1):
                gl = game_lengths[i]
                fdp = frame_data_points[i]
                fm = frame_markers[i]
                for k in pFrameData.keys():
                    for h in in_hashes:
                        input_position = h['participantFrameData'][k][fdp]
                        append_data = pFrameData[k][fm]
                        input_position['championStats'][champ]['raw_data'].append(append_data)
                        input_position['anythingGoes']['raw_data'].append(append_data)
                for k in tFrameData.keys():
                    for h in in_hashes:
                        input_position = h['teamFrameData'][k][fdp]
                        append_data = tFrameData[k][fm]
                        input_position['championStats'][champ]['raw_data'].append(append_data)
                        input_position['anythingGoes']['raw_data'].append(append_data)
                for h in in_hashes:
                    input_position = h['gameDurations'][gl]
                    input_position['championStats'][champ] += 1
                    input_position['anythingGoes'] += 1
                i += 1
            for h in in_hashes:
                h['gamesPlayed']['championStats'][champ] += 1
                h['gamesPlayed']['anythingGoes'] += 1
                for keys in h['participantSummaryData'].keys():
                    input_position = h['participantSummaryData'][keys]
                    if participant_data['stats'][keys]:
                        input_position['championStats'][champ]['raw_data'].append(1)
                        input_position['anythingGoes']['raw_data'].append(1)
                    else:
                        input_position['championStats'][champ]['raw_data'].append(0)
                        input_position['anythingGoes']['raw_data'].append(0)
                for keys in h['teamSummaryData'].keys():
                    input_position = h['teamSummaryData'][keys]
                    if team_data[keys]:
                        input_position['championStats'][champ]['raw_data'].append(1)
                        input_position['anythingGoes']['raw_data'].append(1)
                    else:
                        input_position['championStats'][champ]['raw_data'].append(0)
                        input_position['anythingGoes']['raw_data'].append(0)

    # purpose: calculate avg/stdev from array. push to new array of analyzed data, forget the raw_data hash
    # go all the way down, calculate the average
    def recursive_hash_analysis(self, raw_data_hash, stats_hash):
        for k, v in raw_data_hash.items():
            if type(v) == dict:
                values = stats_hash[k]
                self.recursive_hash_analysis(v, values)
            else:
                if type(v) == int:
                    stats_hash[k] = v
                elif len(v) > 0:
                    stats_hash['avg'] = np.average(v)
                    stats_hash['stdev'] = np.std(v)
                else:
                    stats_hash['avg'] = None
                    stats_hash['stdev'] = None

    # construct each layer for mongodb
    def assemble_stats_hash(self, data_points, zeroes):
        participant_frame_data_list = ('jungleMinionsKilledPerFrame', 'totalGoldPerFrame', 
            'minionsKilledPerFrame', 'xpPerFrame', 'levelPerFrame',
            'jungleMinionsAdvPerFrame', 'goldAdvPerFrame', 'minionsAdvPerFrame', 
            'xpAdvPerFrame', 'levelAdvPerFrame',)
        team_frame_data_list = ('totalGoldPerFrame', 'xpPerFrame',
            'totalLevelPerFrame', 'totalGoldAdvPerFrame',
            'xpAdvPerFrame', 'totalLevelAdvPerFrame',)

        def init_frame_data_hash(params):
            frame_data_points = ('at10', 'at15', 'at20', 'at25',
                'at30', 'at35', 'at40', 'atEnd',)
            frame_data_at_min = {}
            for f in frame_data_points:
                frame_data_at_min[f] = cp.deepcopy(data_points)
            frame_data = {}
            for p in params:
                frame_data[p] = cp.deepcopy(frame_data_at_min)
            return frame_data

        def init_participant_summary_data():
            participant_stats_list = ('kills', 'deaths', 'assists', 'minionsKilled',
                'neutralMinionsKilled', 'wardsPlaced', 'wardsKilled',)
            participant_summary_data = {}
            for p in participant_stats_list:
                participant_summary_data[p] = cp.deepcopy(data_points)
            return participant_summary_data

        def init_team_summary_data():
            team_summary_data = {}
            team_stats_list = ('firstDragon', 'firstBaron', 
                'firstRiftHerald', 'firstTower',)
            team_frame_data = {}
            for t in team_stats_list:
                team_summary_data[t] = cp.deepcopy(data_points)
            return team_summary_data

        def init_game_lengths():
            game_lengths = ('atLeast10', 'atLeast15', 'atLeast20', 'atLeast25',
                'atLeast30', 'atLeast35', 'atLeast40', 'longerThan40')
            game_duration = {}
            for g in game_lengths:
                game_duration[g] = cp.deepcopy(zeroes)
            return game_duration

        frame_data_hash = {}
        frame_data_hash['teamFrameData'] = init_frame_data_hash(team_frame_data_list)
        frame_data_hash['participantFrameData'] = init_frame_data_hash(participant_frame_data_list)
        frame_data_hash['participantSummaryData'] = init_participant_summary_data()
        frame_data_hash['teamSummaryData'] = init_team_summary_data()
        frame_data_hash['gamesPlayed'] = cp.deepcopy(zeroes)
        frame_data_hash['gameDurations'] = init_game_lengths()
        return frame_data_hash


