from flask import Flask, render_template, request, session
from flask import redirect, url_for
from flask import jsonify
import json
import random
import csv
import os
import sys
from utils import * 
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
@app.route("/auction/<expId>", methods = ["GET","POST"])
def auction(expId):
	containsAllMTurkArgs = contains_all_args(request.args)

	if 'demo' in request.args and containsAllMTurkArgs:
		if request.method == "GET" and request.args.get('demo') == 'TRUE':
			stimuli = get_stimuli('/static/stim/demo/')
			random.shuffle(stimuli)

			expVariables = [] # array of dictionaries

			for i in range(0,len(stimuli)):
				expVariables.append({"stimulus1":stimuli[i]})

			return render_template('auction.html', expVariables=expVariables, stimFolder='/static/stim/demo/')
		else:

			workerId = request.args.get('workerId')
			assignmentId = request.args.get('assignmentId')
			hitId = request.args.get('hitId')
			turkSubmitTo = request.args.get('turkSubmitTo')

			return redirect(url_for('auction_instructions', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo))
	elif containsAllMTurkArgs:

		workerId = request.args.get('workerId')
		assignmentId = request.args.get('assignmentId')
		hitId = request.args.get('hitId')
		turkSubmitTo = request.args.get('turkSubmitTo')

		completedAuction = completed_auction(expId, workerId)

		if workerId_exists(expId, workerId) and completedAuction == False:
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
				subjectId = get_subjectId(expId, workerId)
				expResults = json.loads(request.form['experimentResults'])

				if not os.path.exists(expId):
					os.makedirs(expId)

				if not os.path.exists(expId + '/' + subjectId):
					os.makedirs(expId + '/' + subjectId)

				store_data(expId, expResults,'Auction',subjectId)

				set_completed_auction(expId, workerId, True)

				return redirect(url_for('choicetask_demo_instructions', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo))
		elif workerId_exists(expId, workerId) and completedAuction == True:
			return redirect(url_for('auction_error', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo))
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
@app.route("/choicetask/<expId>", methods = ["GET","POST"])
def choicetask(expId):
	containsAllMTurkArgs = contains_all_args(request.args)

	if 'demo' in request.args and containsAllMTurkArgs:
		if request.method == "GET" and request.args.get('demo') == 'TRUE':
			[stim1Names, stim1Bids, stim2Names, stim2Bids] = get_two_stimuli_lists_without_bids('/static/stim/demo/')

			expVariables = [] # array of dictionaries

			deltas = []
			for i in range(0,len(stim1Bids)):
				deltas.append(stim2Bids[i] - stim1Bids[i])

			for i in range(0,len(stim1Bids)):
				expVariables.append({"stimulus1":stim1Names[i],"stimulus2":stim2Names[i],"stim1Bid":stim1Bids[i],"stim2Bid":stim2Bids[i], "delta":deltas[i]})
			return render_template('choicetask.html', expId=expId, expVariables=expVariables, stimFolder='/static/stim/demo/')
		else:

			workerId = request.args.get('workerId')
			assignmentId = request.args.get('assignmentId')
			hitId = request.args.get('hitId')
			turkSubmitTo = request.args.get('turkSubmitTo')

			return redirect(url_for('choicetask_instructions', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo))
	elif containsAllMTurkArgs:
		# not demo - record responses now
		workerId = request.args.get('workerId')
		subjectId = get_subjectId(expId, workerId)
		assignmentId = request.args.get('assignmentId')
		hitId = request.args.get('hitId')
		turkSubmitTo = request.args.get('turkSubmitTo')

		completedChoiceTask = completed_choice_task(expId, workerId)

		if workerId_exists(expId, workerId) and completedChoiceTask == False:
			if request.method == "GET":
				### set experiment conditions here and pass to experiment.html 
				# trialVariables should be an array of dictionaries 
				# each element of the array represents the condition for one trial
				# set the variable conditions to the array of conditions

				if completed_auction(expId, workerId):
					stim1Bids = [];
					stim2Bids = [];

					stimBidDict = get_bid_responses(_thisDir + '/' + expId + '/' + subjectId + '/' + subjectId + '_AuctionData.csv')
					[stim1Names, stim1Bids, stim2Names, stim2Bids] = get_two_stimuli_lists(stimBidDict, '/static/stim/')

					expVariables = [] # array of dictionaries

					deltas = []
					for i in range(0,len(stim1Bids)):
						deltas.append(stim2Bids[i] - stim1Bids[i])

					for i in range(0,len(stim1Bids)):
						expVariables.append({"stimulus1":stim1Names[i],"stimulus2":stim2Names[i],"stim1Bid":stim1Bids[i],"stim2Bid":stim2Bids[i], "delta":deltas[i]})

					return render_template('choicetask.html', expId=expId, expVariables=expVariables, stimFolder='/static/stim/')
				else:
					return redirect(url_for('unauthorized_error'))
			else:
				expResults = json.loads(request.form['experimentResults'])

				if not os.path.exists(expId):
					os.makedirs(expId)

				if not os.path.exists(expId + '/' + subjectId):
					os.makedirs(expId + '/' + subjectId)
				store_data(expId, expResults,'ChoiceTask', subjectId)

				set_completed_choice_task(expId, workerId, True)

				return redirect(url_for('thankyou', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo))
		elif workerId_exists(expId, workerId) and completedChoiceTask == True:
			return redirect(url_for('choicetask_error', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))

"""
Auction Instructions
"""
@app.route("/auction_instructions/<expId>", methods = ["GET","POST"])
def auction_instructions(expId):
	if contains_all_args(request.args):

		workerId = request.args.get('workerId')
		assignmentId = request.args.get('assignmentId')
		hitId = request.args.get('hitId')
		turkSubmitTo = request.args.get('turkSubmitTo')

		if workerId_exists(expId, workerId):
			if request.method == "GET":
				return render_template('auction_instructions.html')
			else:
				if request.form['submit'] == 'Continue':
					return redirect(url_for('auction', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo))
				else:
					return redirect(url_for('auction', demo='TRUE', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))

"""
Auction Demo Instructions
"""
@app.route("/auction_demo_instructions/<expId>", methods = ["GET","POST"])
def auction_demo_instructions(expId):
	if 'assignmentId' in request.args and request.args.get('assignmentId') == 'ASSIGNMENT_ID_NOT_AVAILABLE':
		redirect(url_for('accept_hit'))
	elif contains_all_args(request.args) and request.args.get('assignmentId') != 'ASSIGNMENT_ID_NOT_AVAILABLE':

		workerId = request.args.get('workerId')
		assignmentId = request.args.get('assignmentId')
		hitId = request.args.get('hitId')
		turkSubmitTo = request.args.get('turkSubmitTo')

		if workerId_exists(expId, workerId):
			if request.method == "GET":
				return render_template('auction_demo_instructions.html')
			else:
				return redirect(url_for('auction', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, demo='TRUE'))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))

"""
Choice Task Instructions
"""
@app.route("/choicetask_instructions/<expId>", methods = ["GET","POST"])
def choicetask_instructions(expId):
	if contains_all_args(request.args):

		workerId = request.args.get('workerId')
		assignmentId = request.args.get('assignmentId')
		hitId = request.args.get('hitId')
		turkSubmitTo = request.args.get('turkSubmitTo')

		if workerId_exists(expId, workerId):
			if request.method == "GET":
				return render_template('choicetask_instructions.html', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo)
			else:
				if request.form['submit'] == 'Continue':
					return redirect(url_for('choicetask', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo))
				else:
					return redirect(url_for('choicetask', demo='TRUE', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))

"""
Choice Task Demo Instructions
"""
@app.route("/choicetask_demo_instructions/<expId>", methods = ["GET","POST"])
def choicetask_demo_instructions(expId):
	if contains_all_args(request.args):

		workerId = request.args.get('workerId')
		assignmentId = request.args.get('assignmentId')
		hitId = request.args.get('hitId')
		turkSubmitTo = request.args.get('turkSubmitTo')

		if workerId_exists(expId, workerId):
			if request.method == "GET":
				return render_template('choicetask_demo_instructions.html', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo)
			else:
				return redirect(url_for('choicetask', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, demo='TRUE'))
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
		expId = 'MDMMT'
		workerId = 'abc' + str(random.randint(1000, 10000))
		assignmentId = 'xxxxx' + str(random.randint(10000, 100000))
		hitId = 'hhhhh' + str(random.randint(10000, 100000))
		turkSubmitTo = 'www.mturk.com'
		store_subject_info(expId, workerId, assignmentId, hitId, turkSubmitTo)
		return redirect(url_for('auction_demo_instructions', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, demo='TRUE'))

@app.route("/thankyou", methods = ["GET"])
def thankyou():
	return render_template('thankyou.html')

@app.route("/auction_error/<expId>", methods = ["GET", "POST"])
def auction_error(expId):
	if contains_all_args(request.args):
		workerId = request.args.get('workerId')
		assignmentId = request.args.get('assignmentId')
		hitId = request.args.get('hitId')
		turkSubmitTo = request.args.get('turkSubmitTo')

		if request.method == "GET":
			return render_template('auction_error.html')
		else:
			return redirect(url_for('choicetask_demo_instructions', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, demo='TRUE'))
	else:
		return redirect(url_for('unauthorized_error'))

@app.route("/choicetask_error/<expId>", methods = ["GET"])
def choicetask_error(expId):
	if contains_all_args(request.args):
		workerId = request.args.get('workerId')
		assignmentId = request.args.get('assignmentId')
		hitId = request.args.get('hitId')
		turkSubmitTo = request.args.get('turkSubmitTo')

		if request.method == "GET":
			return redirect(url_for('thankyou', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, demo='TRUE'))
	else:
		return redirect(url_for('unauthorized_error'))

@app.route("/unauthorized_error", methods = ["GET"])
def unauthorized_error():
	return render_template('unauthorized_error.html')

@app.route("/accept_hit", methods = ["GET"])
def accept_hit():
	return render_template('accept_hit.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

if __name__ == "__main__":
	app.debug = False
	app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
	app.run(host = '0.0.0.0', port = 8000)
