import os
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

import config
import control
import threads
import charts
import player
import requests
import junglr_helpers

# connection = pymongo.MongoClient('mongodb://junglr_user:password@localhost:27017/junglr')
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('JUNGLR_SETTINGS', silent=True)
app.config['SECRET_KEY'] = 'secretkeygoeshere'

rate_limiter = threads.rate_limiter(1, 1.2)
sorted_champ_list = junglr_helpers.get_sorted_champ_list()

@app.route('/', methods = ['POST', 'GET'])
def junglr():
	return render_template('index.html')

# from home page button?
@app.route('/process', methods = ['POST', 'GET'])
def process():
	summoner_name = request.form['username'].lower()
	summ = control.PlayerUpdater(summoner_name, rate_limiter)
	status = summ.run()
	if status == 2: # check for errors
		flash('Invalid Summoner Name!')
		goto = url_for('junglr')
	elif status == 3: # don't display charts
		flash('not enough ranked data!')
		goto = url_for('junglr')
	elif status == 0 or status == 1: # no errors
		return redirect(url_for('summoner_analysis', username = summoner_name))
	else: # unknown error?
		flash('No bueno!')
		goto = url_for('junglr')
	return redirect(goto)

@app.route('/summoner/<username>', methods = ['POST', 'GET'])
def summoner_analysis(username):
	summ_obj = check(username)
	
	#defaults
	if 'chart_appearance' not in request.args:
		chart_appearance = 'horizontal bar'
		chart_type = 'First Dragon'
		chart_wlt = 'wins'
		sc_content = 'all'
	else:
		chart_appearance = request.args['chart_appearance']
		chart_type = request.args['chart_type']
		chart_wlt = request.args['chart_wlt']
		print(request.args['sc_content'])
		sc_content = list(request.args['sc_content'])

	chart_uri = render_chart(username, 
		chart_appearance, chart_type, chart_wlt, sc_content)
	main_lane = resolve_bot_lane(summ_obj['mainLane'], 
		summ_obj['mainRole'])
	return render_template('analysis.html', 
		**summ_obj,
		main_lane = main_lane,
		champ_list = sorted_champ_list,
		graph = chart_uri)

@app.context_processor
def utility_processor():
	def render_chart(summoner_name, chart_appearance, chart_type, chart_wlt, sc_content):
		chart = charts.PlayerCharts(summoner_name)
		# return graph.firstDragon(chart_appearance, chart_type, chart_wlt).render_data_uri()
		sc_type = 'Champions'
		# sc_content = ['Vi', 'Jarvan IV', 'Volibear']
		return chart.generate_chart(chart_appearance, chart_type, sc_type, sc_content, chart_wlt).render_data_uri()
	return dict(render_chart=render_chart)

# helper functions
def resolve_bot_lane(lane, role):
	if 'BOT' not in lane:
		return lane
	else:
		if 'SUPPORT' in role:
			return 'SUPPORT'
		else:
			return 'AD CARRY'

def render_chart(summoner_name, chart_appearance, chart_type, chart_wlt, sc_content):
	chart = charts.PlayerCharts(summoner_name)
	# return graph.firstDragon(chart_appearance, chart_type, chart_wlt).render_data_uri()
	sc_type = 'Champions'
	# sc_content = ['Vi', 'Jarvan IV', 'Volibear']
	return chart.generate_chart(chart_appearance, chart_type, sc_type, sc_content, chart_wlt).render_data_uri()

def check(username):
	summ_obj = player.Player(username).read()
	if not summ_obj:
		flash('summoner not in database! enter from here.')
		return redirect(url_for('junglr'))
	else:
		return summ_obj
	
