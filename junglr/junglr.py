import os
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify

import config
import control
import threads
import charts
import player
import requests
import junglr_helpers
import json

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('JUNGLR_SETTINGS', silent=True)
app.config['SECRET_KEY'] = 'secretkeygoeshere'

rate_limiter = threads.rate_limiter(10, 10)
# rate_limiter.start()
# sorted_champ_list = junglr_helpers.get_sorted_champ_list()

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
	if username.startswith('{'):
		return draw_chart()
	summ_obj = check(username)
	main_lane = resolve_bot_lane(summ_obj['mainLane'], 
		summ_obj['mainRole'])
	sorted_champ_list = charts.PlayerCharts(username).get_sorted_champ_list()
	return render_template('analysis.html', main_lane = main_lane, champ_list = sorted_champ_list, **summ_obj)

@app.route('/contact', methods = ['GET'])
def contact():
	return render_template('contact.html')

@app.route('/about', methods = ['GET'])
def about():
	return render_template('about.html')

@app.route('/draw_chart', methods = ['POST'])
def draw_chart():
	try:
		chart_info = request.json['info']
		print(chart_info)
		summoner_name = chart_info['summoner_name']
		chart_appearance = chart_info['chart_appearance']
		chart_season = chart_info['chart_season']
		chart_type = chart_info['chart_type']
		chart_wlt = chart_info['chart_wlt']
		sc_content = chart_info['sc_content']
		if type(chart_info['sc_content']) != list:
			sc_content = [chart_info['sc_content']]
		sc_type = 'Champions'

		print('drawing chart')

		chart = charts.PlayerCharts(summoner_name)
		chart_object = chart.generate_chart(chart_appearance, chart_season, chart_type, sc_type, sc_content, chart_wlt).render_data_uri()
		return chart_object
	except Exception as e:
		print('WHAT THE HELL JUST HAPPENED?!')
		print(str(e))
		return jsonify(status='ERROR',message=str(e))

# helper functions
def resolve_bot_lane(lane, role):
	if 'BOT' not in lane:
		return lane
	else:
		if 'SUPPORT' in role:
			return 'SUPPORT'
		else:
			return 'AD CARRY'

def check(username):
	summ_obj = player.Player(username).read()
	if not summ_obj:
		flash('summoner not in database! enter from here.')
		return redirect(url_for('junglr'))
	else:
		return summ_obj

def render_chart(summoner_name, chart_appearance, chart_type, chart_wlt, sc_content):
	sc_type = 'Champions'
	chart = charts.PlayerCharts(summoner_name)
	return chart.generate_chart(chart_appearance, chart_type, sc_type, sc_content, chart_wlt).render_data_uri()

if __name__ == "__main__":
    application.run(host='0.0.0.0')
	
