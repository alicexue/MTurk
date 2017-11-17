from flask import Flask,render_template,request,session
from flask import redirect,url_for
from flask import jsonify
import json
import random
import csv, os, sys
import ast
import socket
from utils import * # importing * allows you to use methods from utils.py without calling utils.method_name
import store_data

_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)

app = Flask(__name__)

@app.route("/experiment", methods = ["GET","POST"])
def experiment():
	if request.method == "GET":
		### set experiment conditions here and pass to experiment.html 
		# trialVariables should be an array of dictionaries 
		# each element of the array represents the condition for one trial
		# set the variable conditions to the array of conditions
		stimuli1 = get_stimuli()
		stimuli2 = get_stimuli()
		random.shuffle(stimuli1)
		random.shuffle(stimuli2)

		expVariables = [] # array of dictionaries

		for i in range(0,len(stimuli1)):
			expVariables.append({"stimulus1":stimuli1[i]})
			#expVariables.append({"stimulus1":stimuli1[i],'stimulus2':stimuli2[i]})

		return render_template('experiment.html',expVariables=expVariables)
	else:
		expResults = json.loads(request.form['experimentResults'])
		expErrors = json.loads(request.form['experimentErrors'])

		store_data.organize_data(expResults, 'exp_data.csv', 'exp_stimuli.csv');

		return redirect(url_for('thankyou'))

""" 
Auction Task

Description: 
GET: Passes list of dictionaries with stimulus information to auction.html
POST: Saves auction data and stimuli to csv files, redirects to choice task

"""
@app.route("/auction", methods = ["GET","POST"])
def auction():
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

		return render_template('auction.html',expVariables=expVariables)
	else:
		expResults = json.loads(request.form['experimentResults'])
		expErrors = json.loads(request.form['experimentErrors'])
		
		if not os.path.exists('data'):
			os.makedirs('data')

		with open(_thisDir + '/data/' + 'auction_data.txt', 'w') as jsonfile:
			json.dump(request.form['experimentResults'], jsonfile)

		store_data.organize_data(expResults, 'auction_data.csv', 'auction_stimuli.csv')
		
		return redirect(url_for('choicetask_instructions'))

""" 
Choice Task

Description: 
GET: Retrieves stimulus ratings from auction data file, sets up stimuli for choice task
POST: Saves choice task data and stimuli to csv files, redirects to thank you page

"""
@app.route("/choicetask", methods = ["GET","POST"])
def choicetask():
	if request.method == "GET":
		### set experiment conditions here and pass to experiment.html 
		# trialVariables should be an array of dictionaries 
		# each element of the array represents the condition for one trial
		# set the variable conditions to the array of conditions

		stimuli = get_two_stimuli_lists()

		stim1Bids = [];
		stim2Bids = [];

		stimBidDict = get_bid_responses(_thisDir + '/data/auction_data.csv')

		for stimPair in stimuli:
			stim1Bids.append(stimBidDict[stimPair[0]])
			stim2Bids.append(stimBidDict[stimPair[1]])

		expVariables = [] # array of dictionaries

		for i in range(0,len(stimuli)):
			expVariables.append({"stimulus1":stimuli[i][0],"stimulus2":stimuli[i][1],"stim1Bid":stim1Bids[i],"stim2Bid":stim2Bids[i]})

		return render_template('choicetask.html',expVariables=expVariables)
	else:
		expResults = json.loads(request.form['experimentResults'])
		expErrors = json.loads(request.form['experimentErrors'])
		
		if not os.path.exists('data'):
			os.makedirs('data')

		with open(_thisDir + '/data/' + 'choice_data.txt', 'w') as jsonfile:
			json.dump(request.form['experimentResults'], jsonfile)

		store_data.organize_data(expResults, 'choice_data.csv', 'choice_stimuli.csv');
		
		return redirect(url_for('thankyou'))

"""
Auction Instructions
"""
@app.route("/auction_instructions", methods = ["GET","POST"])
def auction_instructions():
	if request.method == "GET":
		return render_template('auction_instructions.html')
	else:
		return redirect(url_for('auction'))

"""
Choice Task Instructions
"""
@app.route("/choicetask_instructions", methods = ["GET","POST"])
def choicetask_instructions():
	if request.method == "GET":
		return render_template('choicetask_instructions.html')
	else:
		return redirect(url_for('choicetask'))

"""
Consent Form (home page)
"""
@app.route("/", methods = ["GET","POST"])
def consent_form():
	if request.method == "GET":
		return render_template('consent_form.html')
	else:
		return redirect(url_for('auction_instructions'))

@app.route("/thankyou", methods = ["GET"])
def thankyou():
	return render_template('thankyou.html')

if __name__ == "__main__":
	app.debug = True
	app.secret_key="Don't store this on github"
	app.run(host = '0.0.0.0', port = 8000)
