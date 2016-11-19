import player

class PlayerUpdater():
    def __init__(self, summ_name, rate_limiter):
        self.player = player.Player(summ_name)
        self.player.rate_limiter = rate_limiter
        # self.rate_limiter = rate_limiter

    def run(self):
        # 0 - is valid, needs updating
        # 1 - is valid, does not need to be updated
        # 2 - invalid summoner name
        # 3 - not enough ranked data
        action = 2
        valid = (self.player.pull_player_api_data() != 'Not Found')
        if valid:
            needs_update = (self.player.update_last_modified() == 'update')
            has_ranked_data = self.player.pull_match_list()
            enough_data = self.enough_data()
            if needs_update and has_ranked_data: #make pull, but maybe not enough data
                self.player.update()
                action = 0 
            elif not has_ranked_data or not enough_data: # doesn't have any ranked matches
                action = 3
            else: # no update needed
                action = 1
        else: # invalid summoner id
            action = 2
        return action

    def enough_data(self):
        db_obj = self.player.read()
        return False if 'league' not in db_obj else True
            
    def update_and_read(self):
        self.run()
        return self.read()