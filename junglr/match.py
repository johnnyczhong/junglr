import req_builder
# used to get greatest value in dict
# import operator
import mongo_helper

matches_collection = 'matches'
summoners_collection = 'summoners'

#one match pull
#needs to be rate limited
class Match_Details():
    def __init__(self, match_id):
        self.match_id = match_id
        self.info_hash = {}
        self.info_hash_list = (
            'matchId',
            "matchCreation",
            'matchDuration',
            "season",
            "queueType",
            "region",
            "matchVersion",
            "matchType",
            "matchMode"
        )
        self.frame_job_list = (self.init_info_hash,
            self.sort_frames,
            self.create_teams,
            self.create_participants,
            self.get_participant_timelines,
            self.match_up_assignment,
            self.team_frame_calculations,
            self.set_participant_mapping,
            self.compile_team_info,
            self.push_db)
        self.no_frame_job_list = (self.init_info_hash,
            self.create_teams,
            self.create_participants,
            self.match_up_assignment,
            self.set_participant_mapping,
            self.compile_team_info,
            self.push_db)
        self.thread_actions()

    def thread_actions(self):
        self.workflow()

    def check_exists(self):
        db_conn = mongo_helper.Connection()
        check = db_conn.find(matches_collection, {'matchId': self.match_id})
        return check

    def push_db(self):
        db_conn = mongo_helper.Connection()
        db_conn.insert('matches', self.info_hash)

    def workflow(self):
        exists = self.check_exists()
        if not exists:
            response = self.pull_match_details()
            if response == 'Not Found':
                return False
            self.has_frames = self.parse_match_data()
            job_list = self.frame_job_list if self.has_frames else self.no_frame_job_list
            for jobs in job_list:
                jobs()
        return True

    def pull_match_details(self):
        r = req_builder.api_request('match_details',
                self.match_id, optional_params = {'includeTimeline': 'true'})
        api_response = r.make_request()
        self.full_match_data = api_response
        return api_response

    def parse_match_data(self):
        has_frames = False
        if 'timeline' in self.full_match_data:
            self.frames = self.full_match_data['timeline']['frames']
            self.num_frames = len(self.frames)
            has_frames = True
        self.match_duration = self.full_match_data['matchDuration']
        return has_frames

    def sort_frames(self):
        self.info_hash['events'] = []
        for f in self.frames:
            if 'events' in f:
                for e in f['events']:
                    self.info_hash['events'].append(e)

    def init_info_hash(self):
        for i in self.info_hash_list:
            self.info_hash[i] = self.full_match_data[i]
        self.info_hash['teams'] = {}

    #team 100 vs 200
    def create_teams(self):
        self.team_100 = Team('100', self.full_match_data['teams'][0])
        self.team_200 = Team('200', self.full_match_data['teams'][1])

    def create_participants(self):
        self.participants_id = self.full_match_data['participantIdentities']
        self.participants_data = self.full_match_data['participants']
        for i in range(0, 10):
            if (self.participants_data[i]['teamId'] == 100): 
                self.team_100.participants_list.append(Participant( 
                    self.participants_id[i]['player']['summonerId'], 
                    self.participants_id[i]['player']['summonerName'],
                    self.participants_data[i]))
            else: 
                self.team_200.participants_list.append(Participant( 
                    self.participants_id[i]['player']['summonerId'],
                    self.participants_id[i]['player']['summonerName'],
                    self.participants_data[i]))

    #makes it easier to determine stats based on summId
    def set_participant_mapping(self):
        participant_mapping = {}
        for i in range(5):
            p100 = self.team_100.participants_list[i]
            p200 = self.team_200.participants_list[i]
            participant_mapping[str(p100.info_hash['summId'])] = {'team': 100, 'participantId': p100.info_hash['participantId']}
            participant_mapping[str(p200.info_hash['summId'])] = {'team': 200, 'participantId': p200.info_hash['participantId']}
        self.info_hash['participantMapping'] = participant_mapping

    def get_participant_timelines(self):
        for p, q in zip(self.team_100.participants_list, self.team_200.participants_list):
            p.get_timeline_data(self.frames)
            q.get_timeline_data(self.frames)

    # could improve on alg, but n is small enough not to matter
    # logic within participant object to avoid reassigning (but doesn't really matter)
    def match_up_assignment(self):
        for i in range(0, 5):
            for j in range(0, 5):
                p100 = self.team_100.participants_list[i]
                p200 = self.team_200.participants_list[j]
                assigned = p100.assign_opponent(p200)
                if assigned:
                    p200.assign_opponent(p100)
                    if self.has_frames:
                        p100.calc_adv(p200)
                        p200.calc_adv(p100)

    # calculate 
    def team_frame_calculations(self):
        self.team_100.calc_stat_totals_per_frame(self.num_frames)
        self.team_200.calc_stat_totals_per_frame(self.num_frames)
        self.team_100.calc_stat_adv_per_frame(self.team_200)
        self.team_200.calc_stat_adv_per_frame(self.team_100)

    def compile_team_info(self):
        self.team_100.compile_participant_info()
        self.team_200.compile_participant_info()
        self.info_hash['teams']['100'] = self.team_100.info_hash
        self.info_hash['teams']['200'] = self.team_200.info_hash


class Team():
    def __init__(self, team, stats):
        self.info_hash = stats
        self.info_hash['team'] = team
        self.info_hash['participants'] = {}
        self.participants_list = [] #list of Participant obj
        self.per_frame_stats_list = {
            'totalGoldPerFrame': 'totalGoldPerFrame',
            'xpPerFrame': 'xpPerFrame',
            'totalLevelPerFrame': 'levelPerFrame'
            }
        self.per_frame_adv_list = {
            'totalGoldAdvPerFrame': 'totalGoldPerFrame',
            'xpAdvPerFrame': 'xpPerFrame',
            'totalLevelAdvPerFrame': 'totalLevelPerFrame'
            }
        self.num_stats_list = len(self.per_frame_stats_list)

    # grabs all participant information and puts into own info_hash
    def compile_participant_info(self):
        for p in self.participants_list:
            self.info_hash['participants'][str(p.info_hash['participantId'])] = p.info_hash

    # takes stats from participants and sums them for totals
    def calc_stat_totals_per_frame(self, num_frames):
        self.num_frames = num_frames
        self.info_hash['frameData'] = {}
        for stats in self.per_frame_stats_list.keys():
            self.info_hash['frameData'][stats] = [0] * self.num_frames
        for p in self.participants_list:
            for k, v in self.per_frame_stats_list.items():
                for f in range(self.num_frames):
                    self.info_hash['frameData'][k][f] += p.info_hash['frameData'][v][f]

    # takes difference between totals for both teams
    # creates hashes mapped to arrays
    # iterates through each type of statistic
    # iterates through each fream for that statistic for self and enemy team
    def calc_stat_adv_per_frame(self, opp_team):
        frame_data = self.info_hash['frameData']
        for adv in self.per_frame_adv_list:
            frame_data[adv] = [0] * self.num_frames
        for k, v in self.per_frame_adv_list.items():
            for f in range(self.num_frames):
                frame_data[k][f] = frame_data[v][f] - opp_team.info_hash['frameData'][v][f]

class Participant():
    def __init__(self, summ_id, summ_name, stats):
        self.summ_id = summ_id
        self.summ_name = summ_name
        self.num_frames = False
        self.info_hash = stats
        self.info_hash['summId'] = summ_id
        self.info_hash['role'] = stats['timeline']['role']
        self.info_hash['lane'] = stats['timeline']['lane']

        self.per_frame_list = ('jungleMinionsKilledPerFrame',
            'totalGoldPerFrame', 
            'minionsKilledPerFrame',
            'xpPerFrame',
            'levelPerFrame')
        self.per_frame_adv_list = ('jungleMinionsAdvPerFrame',
            'goldAdvPerFrame', 
            'minionsAdvPerFrame', 
            'xpAdvPerFrame', 
            'levelAdvPerFrame')
        self.num_params = len(self.per_frame_list)

    # purpose: compile data for the player/participant at any given minute
    # in: game frame data (data snapshots per minute)
    # out: arrays of gold, jungle minions killed, and lane minions killed at
    #      any minute corresponding to the array 
    def get_timeline_data(self, frames):
        self.info_hash['frameData'] = {}
        self.num_frames = len(frames)
        frame_list = ('jungleMinionsKilled',
            'totalGold', 
            'minionsKilled',
            'xp',
            'level')
        for i in self.per_frame_list:
            self.info_hash['frameData'][i] = [0] * self.num_frames
        for f in range(self.num_frames):
            timeline_frame_data = frames[f]['participantFrames'][str(self.info_hash['participantId'])]
            for i in range(self.num_params):
                info_key, frame_key = self.per_frame_list[i], frame_list[i]
                self.info_hash['frameData'][info_key][f] = timeline_frame_data[frame_key]

    # purpose: calculate gold advantage or disadvantage per minute of game time
    # in: gold data for player and opponent gold data in array
    # out: gold adv or disadv in array at minute corresponding to the index
    def calc_adv(self, opp):
        frame_data = self.info_hash['frameData']
        for adv in self.per_frame_adv_list:
            frame_data[adv] = [0] * self.num_frames
        for n in range(self.num_frames):
            for i in range(self.num_params):
                stat = self.per_frame_list[i]
                adv = self.per_frame_adv_list[i]
                frame_data[adv][n] = frame_data[stat][n] - opp.info_hash['frameData'][stat][n]

    # purpose: determine opposing player if not already assigned
    # in: potential opponent
    # out: True if assigned, False if not
    def assign_opponent(self, opp):
        if ('opponentSummId' not in self.info_hash and
        self.info_hash['role'] == opp.info_hash['role'] and 
        self.info_hash['lane'] == opp.info_hash['lane']):
            self.info_hash['opponentSummId'] = opp.info_hash['summId']
            self.info_hash['opponentParticipantId'] = opp.info_hash['participantId']
            return True
        return False
