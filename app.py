from flask import Flask,render_template,request,session
from flask import redirect,url_for
from flask import jsonify
import json
import random
import csv, os, sys
import ast
import socket
from utils import * # importing * allows you to use methods from utils.py without calling utils.method_name
from store_data import *
from store_subject_info import *
import pandas as pd

_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)

app = Flask(__name__)

""" 
Auction Task

Description: 
GET: Passes list of dictionaries with stimulus information to auction.html
POST: Saves auction data and stimuli to csv files, redirects to choice task

"""
@app.route("/auction/<expID>", methods = ["GET","POST"])
def auction(expID):
	if 'demo' in request.args and 'workerID' in request.args:
		if request.method == "GET" and request.args.get('demo') == 'TRUE':
			stimuli = get_stimuli('/static/stim/demo/')
			random.shuffle(stimuli)

			expVariables = [] # array of dictionaries

			for i in range(0,len(stimuli)):
				expVariables.append({"stimulus1":stimuli[i]})

			return render_template('auction.html', expVariables=expVariables, stimFolder='/static/stim/demo/')
		else:
			workerID = request.args.get('workerID')
			return redirect(url_for('auction_instructions', expID = expID, workerID = workerID))
	elif 'workerID' in request.args:
		workerID = request.args.get('workerID')

		completedAuction = completed_auction(expID, workerID)

		if workerID_exists(expID, workerID) and completedAuction == False:
			if request.method == "GET":
				### set experiment conditions here and pass to experiment.html 
				# trialVariables should be an array of dictionaries 
				# each element of the array represents the condition for one trial
				# set the variable conditions to the array of conditions
				stimuli1 = get_stimuli('/static/stim/')
				random.shuffle(stimuli1)

				expVariables = [] # array of dictionaries

				for i in range(0,len(stimuli1)):
					expVariables.append({"stimulus1":stimuli1[i]})

				return render_template('auction.html', expVariables=expVariables, stimFolder='/static/stim/')
			else:
				subjectID = get_subjectID(expID, workerID)
				expResults = json.loads(request.form['experimentResults'])

				if not os.path.exists(expID):
					os.makedirs(expID)

				if not os.path.exists(expID + '/' + subjectID):
					os.makedirs(expID + '/' + subjectID)

				store_data(expID, expResults,'Auction',subjectID)

				set_completed_auction(expID, workerID, True)

				return redirect(url_for('choicetask_demo_instructions', expID=expID, workerID = workerID))
		elif workerID_exists(expID, workerID) and completedAuction == True:
			return redirect(url_for('auction_error', expID = expID, workerID = workerID))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))

""" 
Choice Task

Description: 
GET: Retrieves stimulus ratings from auction data file, sets up stimuli for choice task
POST: Saves choice task data and stimuli to csv files, redirects to thank you page

"""
@app.route("/choicetask/<expID>", methods = ["GET","POST"])
def choicetask(expID):
	if 'demo' in request.args and 'workerID' in request.args:
		if request.method == "GET" and request.args.get('demo') == 'TRUE':
			[stim1Names, stim1Bids, stim2Names, stim2Bids] = get_two_stimuli_lists_without_bids('/static/stim/demo/')

			expVariables = [] # array of dictionaries

			deltas = []
			for i in range(0,len(stim1Bids)):
				deltas.append(stim2Bids[i] - stim1Bids[i])

			for i in range(0,len(stim1Bids)):
				expVariables.append({"stimulus1":stim1Names[i],"stimulus2":stim2Names[i],"stim1Bid":stim1Bids[i],"stim2Bid":stim2Bids[i], "delta":deltas[i]})
			return render_template('choicetask.html', expID=expID, expVariables=expVariables, stimFolder='/static/stim/demo/')
		else:
			workerID = request.args.get('workerID')
			return redirect(url_for('choicetask_instructions', expID = expID, workerID = workerID))
	elif 'workerID' in request.args:
		workerID = request.args.get('workerID')
		subjectID = get_subjectID(expID, workerID)

		completedChoiceTask = completed_choice_task(expID, workerID)

		if workerID_exists(expID, workerID) and completedChoiceTask == False:
			if request.method == "GET":
				### set experiment conditions here and pass to experiment.html 
				# trialVariables should be an array of dictionaries 
				# each element of the array represents the condition for one trial
				# set the variable conditions to the array of conditions

				stim1Bids = [];
				stim2Bids = [];

				stimBidDict = get_bid_responses(_thisDir + '/' + expID + '/' + subjectID + '/' + subjectID + '_AuctionData.csv')
				[stim1Names, stim1Bids, stim2Names, stim2Bids] = get_two_stimuli_lists(stimBidDict, '/static/stim/')

				expVariables = [] # array of dictionaries

				deltas = []
				for i in range(0,len(stim1Bids)):
					deltas.append(stim2Bids[i] - stim1Bids[i])

				for i in range(0,len(stim1Bids)):
					expVariables.append({"stimulus1":stim1Names[i],"stimulus2":stim2Names[i],"stim1Bid":stim1Bids[i],"stim2Bid":stim2Bids[i], "delta":deltas[i]})

				return render_template('choicetask.html', expID=expID, expVariables=expVariables, stimFolder='/static/stim/')
			else:
				expResults = json.loads(request.form['experimentResults'])

				if not os.path.exists(expID):
					os.makedirs(expID)

				if not os.path.exists(expID + '/' + subjectID):
					os.makedirs(expID + '/' + subjectID)
				store_data(expID, expResults,'ChoiceTask', subjectID)

				set_completed_choice_task(expID, workerID, True)

				return redirect(url_for('thankyou'))
		elif workerID_exists(expID, workerID) and completedChoiceTask == True:
			return redirect(url_for('choicetask_error', expID = expID, workerID = workerID))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))

"""
Auction Instructions
"""
@app.route("/auction_instructions/<expID>", methods = ["GET","POST"])
def auction_instructions(expID):
	if 'workerID' in request.args:
		workerID = request.args.get('workerID')
		if workerID_exists(expID, workerID):
			if request.method == "GET":
				return render_template('auction_instructions.html', workerID = workerID)
			else:
				return redirect(url_for('auction', expID = expID, workerID = workerID))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))

"""
Auction Demo Instructions
"""
@app.route("/auction_demo_instructions/<expID>", methods = ["GET","POST"])
def auction_demo_instructions(expID):
	if 'workerID' in request.args:
		workerID = request.args.get('workerID')
		if workerID_exists(expID, workerID):
			if request.method == "GET":
				return render_template('auction_demo_instructions.html', workerID = workerID)
			else:
				return redirect(url_for('auction', expID = expID, workerID = workerID, demo = 'TRUE'))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))

"""
Choice Task Instructions
"""
@app.route("/choicetask_instructions/<expID>", methods = ["GET","POST"])
def choicetask_instructions(expID):
	if 'workerID' in request.args:
		workerID = request.args.get('workerID')
		if workerID_exists(expID, workerID):
			if request.method == "GET":
				return render_template('choicetask_instructions.html', expID = expID, workerID = workerID)
			else:
				return redirect(url_for('choicetask', expID = expID, workerID = workerID))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))

"""
Choice Task Demo Instructions
"""
@app.route("/choicetask_demo_instructions/<expID>", methods = ["GET","POST"])
def choicetask_demo_instructions(expID):
	if 'workerID' in request.args:
		workerID = request.args.get('workerID')
		if workerID_exists(expID, workerID):
			if request.method == "GET":
				return render_template('choicetask_demo_instructions.html', expID = expID, workerID = workerID)
			else:
				return redirect(url_for('choicetask', expID = expID, workerID = workerID, demo = 'TRUE'))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))


"""
Consent Form (home page)
"""
@app.route("/MDMMT", methods = ["GET","POST"])
def MDMMT():
	if request.method == "GET":
		return render_template('consent_form.html')
	else:
		### need to change code here after testing is finished
		workerID = 'abc' + str(random.randint(1000, 10000))
		expID = 'MDMMT'
		store_subject_info(expID, workerID)
		return redirect(url_for('auction_demo_instructions', expID = expID, workerID = workerID, demo = 'TRUE'))

@app.route("/thankyou", methods = ["GET"])
def thankyou():
	return render_template('thankyou.html')

@app.route("/auction_error/<expID>", methods = ["GET", "POST"])
def auction_error(expID):
	if 'workerID' in request.args:
		workerID = request.args.get('workerID')
		if request.method == "GET":
			return render_template('auction_error.html')
		else:
			return redirect(url_for('choicetask', expID = expID, workerID = workerID, demo = 'TRUE'))
	else:
		return redirect(url_for('unauthorized_error'))

@app.route("/choicetask_error/<expID>", methods = ["GET"])
def choicetask_error(expID):
	if 'workerID' in request.args:
		workerID = request.args.get('workerID')
		return render_template('choicetask_error.html')
	else:
		return redirect(url_for('unauthorized_error'))

@app.route("/unauthorized_error", methods = ["GET"])
def unauthorized_error():
	return render_template('unauthorized_error.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

if __name__ == "__main__":
	app.debug = False
	app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)
