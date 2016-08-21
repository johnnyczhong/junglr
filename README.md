# junglr
## info to make you a better jungler

### todo:
- [x] Make a git
- [ ] Establish at least 3 db tables
    - [x] name - player_data: pk - summ_id | summ_name, revision date
    - [x] name - champ_info: pk - champ_id | champ_name
    - [ ] name - s2016_player_match_champ_stats: pks - match_id, summ_id | role, champ_id, gold_at_10m, gold_at_20m
    - [ ] name - s2016_player_char_stats_avg: pks - summ_id, champ_id, role | gold_10_min, gold_20_min
    - [ ] figure out normalization!!!!
- [ ] Write api calls
- [ ] What's a jungler? (determined by role declaration)
- [ ] Gather metrics (win/loss, player rank, etc)
- [ ] This is how the jungler do. (pathing, decisions, etc.)

### hopes and dreams:
- [ ] A heatmap would be nice
- [x] host on AWS
- [ ] frontend website

## technologies involved:
python 3.5
postgreSQL
pandas (not yet used)
AWS
