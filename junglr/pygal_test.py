import pygal
import mongo_helper

def champ_id_to_name(conn, champ_id):
	champ_mapping = conn.find('static_data', {'document_name': 'champion_info'})
	champ_name = champ_mapping[str(champ_id)]['name']
	return champ_name

conn = mongo_helper.Connection()
summ = conn.find('summoners', {'summNameLower': 'pinkbunnysoul'})
line_chart = pygal.HorizontalBar()
line_chart.title = 'First Dragon Percentages'
champions = summ['SEASON2016Stats']['total']['teamSummaryData']['firstDragon']['championStats'].keys()
win = {'name': 'win', 'stats': []}
loss = {'name': 'loss', 'stats': []}
total = {'name': 'total', 'stats': []}
categories = (win, loss, total)
for c in categories:
	c_name = c['name']
	champ_stats = summ['SEASON2016Stats'][c_name]['teamSummaryData']['firstDragon']['championStats']
	for champs in champions:
		c['stats'].append(champ_stats[champs]['avg'])
for c in categories:
	line_chart.add(c['name'], c['stats'])
champ_names = []
for ids in champions:
	champ_names.append(champ_id_to_name(conn, ids))
line_chart.x_labels = champ_names
line_chart.render_to_file('test.svg')