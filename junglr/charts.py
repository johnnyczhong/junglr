# name: charts.py
# author: johnny zhong
# purpose: create pygal charts for display

import pygal
import mongo_helper
import player

season = 'SEASON2016Stats'

class PlayerCharts():
	def __init__(self, summ_name_lower):
		self.conn = mongo_helper.Connection()
		self.summ = self.conn.find('summoners', {'summNameLower': summ_name_lower})
		self.map_champs()

	# purpose: generate and return a completed chart of requested data
	# handle different selection criteria by querying the correct content
	def firstTower(self, chart, sc_type, sc_list, wlt):
		chart.title = 'First Tower %'
		if sc_type.lower() == 'champions':
			sc = 'championStats'
		for outcomes in wlt:
			outcome_name = outcomes['name']
			stats = self.summ[season][outcome_name]['teamSummaryData']['firstTower'][sc]
			for items in sc_list:
				outcomes['stats'].append(stats[items]['avg'])
		for outcomes in wlt:
			chart.add(outcomes['name'], outcomes['stats'])
		if sc_type.lower() == 'champions':
			champ_names = self.champ_id_list_to_name(sc_list)
			chart.x_labels = champ_names # add in ordered format, but based on what?
		return chart

	#win/loss/total for firstDragon per champion
	def firstDragon(self, chart, sc_type, sc_list, wlt):
		chart.title = 'First Dragon Percentages'
		print(sc_list)
		if sc_type.lower() == 'champions':
			sc = 'championStats'
		for outcomes in wlt:
			outcome_name = outcomes['name']
			stats = self.summ[season][outcome_name]['teamSummaryData']['firstDragon'][sc]
			for items in sc_list:
				outcomes['stats'].append(stats[items]['avg'])
		for outcomes in wlt:
			chart.add(outcomes['name'], outcomes['stats'])
		if sc_type.lower() == 'champions':
			champ_names = self.champ_id_list_to_name(sc_list)
			chart.x_labels = champ_names # add in ordered format, but based on what?
		return chart


	def goldAdv(self, chart, sc_type, sc_list, wlt):
		frame_data_points = ('at10', 'at15', 'at20', 'at25',
			'at30', 'at35', 'at40', 'atEnd',)
		chart.title = 'Gold Adv By The Minute'
		if sc_type.lower() == 'champions':
			sc = 'championStats'
		for outcomes in wlt:
			outcome_name = outcomes['name']
			stats = self.summ[season][outcome_name]['participantFrameData']['goldAdvPerFrame']
			for f in frame_data_points:
				for items in sc_list:
					outcomes['stats'].append(stats[f][sc][items]['avg'])
		for outcomes in wlt:
			chart.add(outcomes['name'], outcomes['stats'])
		if sc_type.lower() == 'champions':
			champ_names = self.champ_id_list_to_name(sc_list)
			chart.x_labels = frame_data_points # add in ordered format, but based on what?
		return chart


	def champs_in_question(self, champ_list):
		if 'all' in champ_list:
			return self.summ[season]['total']['gamesPlayed']['championStats'].keys()
		else:
			c = [self.champ_name_to_id(x) for x in champ_list]
			return c


	# sc - selection criteria
	def get_selection_criteria_list(self, sc_type, sc_contents):
		if sc_type.lower() == 'champions':
			# sc_list = self.champ_name_list_to_id(sc_contents)
			sc_list = self.champs_in_question(sc_contents)
		elif sc_type.lower() == 'roles':
			pass
		return sc_list


	def get_data(self, chart_type):
		chart_type = chart_type.lower()
		functions_menu = {
			'gold advantage': self.goldAdv,
			'first dragon': self.firstDragon,
			'first tower': self.firstTower,
		}
		return functions_menu[chart_type]


	def generate_chart(self, chart_appearance, chart_type, sc_type, sc_contents, wlt):
		chart = self.pick_pygal(chart_appearance)
		chart_function = self.get_data(chart_type)
		sc_list = self.get_selection_criteria_list(sc_type, sc_contents)
		wlt_hash = self.get_wlt(wlt)
		return chart_function(chart, sc_type, sc_list, wlt_hash)


	# what type of chart?
	def pick_pygal(self, chart_appearance):
		chart_appearance = chart_appearance.strip().lower()
		charts = {
			'horizontal bar': pygal.HorizontalBar,
			'bar': pygal.Bar
		}
		return charts[chart_appearance]()


	def get_wlt(self, wlt):
		wlt = wlt.lower()
		win = {'name': 'win', 'stats': []}
		loss = {'name': 'loss', 'stats': []}
		total = {'name': 'total', 'stats': []}
		result = {
			'losses': (loss,),
			'wins': (win,),
			'total': (total,),
			'wins and losses': (win, loss,),
			'all': (win, loss, total,)
		}
		return result[wlt]


	# assuming known values
	def champ_name_to_id(self, champ_name):
		for v in self.champ_mapping.values():
			if v['name'] == champ_name:
				return str(v['id'])

	def champ_name_list_to_id(self, champ_list):
		print(champ_list)
		champ_ids = []
		for names in champ_list:
			champ_ids.append(self.champ_name_to_id(names))
		return champ_ids

	def champ_id_list_to_name(self, champ_list):
		champ_names = []
		for ids in champ_list:
			champ_names.append(self.champ_id_to_name(ids))
		return champ_names

	def champ_id_to_name(self, champ_id):
		champ_name = self.champ_mapping[str(champ_id)]['name']
		return champ_name

	def map_champs(self):
		self.champ_mapping = self.conn.find('static_data', {'document_name': 'champion_info'})
		del self.champ_mapping['document_name']
		del self.champ_mapping['_id']

