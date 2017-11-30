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
@app.route("/auction", methods = ["GET","POST"])
def auction():
	if 'workerID' in request.args and 'expName' in request.args:
		workerID = request.args.get('workerID')
		expName = request.args.get('expName')
		if workerID_exists(expName, workerID):
			if request.method == "GET":
				### set experiment conditions here and pass to experiment.html 
				# trialVariables should be an array of dictionaries 
				# each element of the array represents the condition for one trial
				# set the variable conditions to the array of conditions
				stimuli1 = get_stimuli()
				random.shuffle(stimuli1)

				expVariables = [] # array of dictionaries

				for i in range(0,len(stimuli1)):
					expVariables.append({"stimulus1":stimuli1[i]})

				return render_template('auction.html', expVariables=expVariables)
			else:
				subjectID = get_subjectID(expName, workerID)
				expResults = json.loads(request.form['experimentResults'])

				if not os.path.exists(expName):
					os.makedirs(expName)

				if not os.path.exists(expName + '/' + subjectID):
					os.makedirs(expName + '/' + subjectID)

				store_data(expName, expResults,'Auction',subjectID)

				return redirect(url_for('choicetask_instructions', workerID = workerID, expName = expName))
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
@app.route("/choicetask", methods = ["GET","POST"])
def choicetask():
	if 'workerID' in request.args and 'expName' in request.args:
		workerID = request.args.get('workerID')
		expName = request.args.get('expName')
		subjectID = get_subjectID(expName, workerID)
		if workerID_exists(expName, workerID):
			if request.method == "GET":
				### set experiment conditions here and pass to experiment.html 
				# trialVariables should be an array of dictionaries 
				# each element of the array represents the condition for one trial
				# set the variable conditions to the array of conditions

				stim1Bids = [];
				stim2Bids = [];

				stimBidDict = get_bid_responses(_thisDir + '/' + expName + '/' + subjectID + '/' + subjectID + '_AuctionData.csv')
				[stim1Names, stim1Bids, stim2Names, stim2Bids] = get_two_stimuli_lists(stimBidDict)

				expVariables = [] # array of dictionaries

				deltas = []
				for i in range(0,len(stim1Bids)):
					deltas.append(stim2Bids[i] - stim1Bids[i])

				for i in range(0,len(stim1Bids)):
					expVariables.append({"stimulus1":stim1Names[i],"stimulus2":stim2Names[i],"stim1Bid":stim1Bids[i],"stim2Bid":stim2Bids[i], "delta":deltas[i]})

				return render_template('choicetask.html',expVariables=expVariables)
			else:
				expResults = json.loads(request.form['experimentResults'])

				if not os.path.exists(expName):
					os.makedirs(expName)

				if not os.path.exists(expName + '/' + subjectID):
					os.makedirs(expName + '/' + subjectID)
				store_data(expName, expResults,'ChoiceTask', subjectID)

				return redirect(url_for('thankyou'))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))

"""
Auction Instructions
"""
@app.route("/auction_instructions", methods = ["GET","POST"])
def auction_instructions():
	if 'workerID' in request.args and 'expName' in request.args:
		workerID = request.args.get('workerID')
		expName = request.args.get('expName')
		if workerID_exists(expName, workerID):
			if request.method == "GET":
				return render_template('auction_instructions.html', workerID = workerID, expName = expName)
			else:
				return redirect(url_for('auction', workerID = workerID, expName = expName))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))

"""
Choice Task Instructions
"""
@app.route("/choicetask_instructions", methods = ["GET","POST"])
def choicetask_instructions():
	if 'workerID' in request.args and 'expName' in request.args:
		workerID = request.args.get('workerID')
		expName = request.args.get('expName')
		if workerID_exists(expName, workerID):
			if request.method == "GET":
				return render_template('choicetask_instructions.html', workerID = workerID, expName = expName)
			else:
				return redirect(url_for('choicetask', workerID = workerID, expName = expName))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))

"""
Consent Form (home page)
"""
@app.route("/", methods = ["GET","POST"])
def consent_form():
	if request.method == "GET":
		return render_template('consent_form.html')
	else:
		### need to change code here after testing is finished
		workerID = 'abc' + str(random.randint(1000, 10000))
		expName = 'TEST'
		store_subject_info(expName, workerID)
		return redirect(url_for('auction_instructions', workerID = workerID, expName = expName))

@app.route("/thankyou", methods = ["GET"])
def thankyou():
	return render_template('thankyou.html')

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
	app.secret_key="Don't store this on github"
	app.run(host = '0.0.0.0', port = 8000)
