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
from manage_subject_info import *
import pandas as pd

_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)

app = Flask(__name__)

"""
It is assumed that all tasks are preceded by a demo (when moving onto the next task, always reroute to a demo instructions page
- see code for clarification)

1. Define the order in which tasks are to be completed in your experiment (see MDMMT_taskOrder)
2. Add variable from step 1 to the dictionary expTaskOrders. In the key-value pair, the variable from step 1
should be the value and the experiment abbreviation/name should be the key.

Each task has 3 associated functions - suppose our task is called "auction"
	1) function that runs the task (also runs demo) (auction(expId))
	2) function for task instructions
	3) function for instructions of task's demo
	Notes:
		Each function must take expId as a parameter and each function must contain a variable that defines the name of the task

"""


MDMMT_taskOrder = ['auction_demo_instructions', 'auction', 'choicetask_demo_instructions', 'choicetask', 'feedback'] # order of tasks in experiment
expTaskOrders = {'MDMMT':MDMMT_taskOrder} # dictionary of experiments - key is exp name, value is order of tasks

""" 
Auction Task

Description: 
GET: Passes list of dictionaries with stimulus information to auction.html
POST: Saves auction data and stimuli to csv files, redirects to choice task

"""
@app.route("/auction/<expId>", methods = ["GET","POST"])
def auction(expId):
	name = 'auction'
	containsAllMTurkArgs = contains_necessary_args(request.args)

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
			live = request.args.get('live') == "True"

			return redirect(url_for('auction_instructions', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	elif containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

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

				add_new_subject(expId, subjectId)
				store_data(expId, expResults,'Auction',subjectId)

				set_completed_auction(expId, workerId, True)

				nextTask = get_next_task(name, expTaskOrders[expId])
				return redirect(url_for(nextTask, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		elif workerId_exists(expId, workerId) and completedAuction == True:
			return redirect(url_for('auction_error', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
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
	name = 'choicetask'
	containsAllMTurkArgs = contains_necessary_args(request.args)

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
			[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

			return redirect(url_for('choicetask_instructions', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	elif containsAllMTurkArgs:
		# not demo - record responses now
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
		subjectId = get_subjectId(expId, workerId)

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

				add_new_subject(expId, subjectId)
				store_data(expId, expResults,'ChoiceTask', subjectId)

				set_completed_choice_task(expId, workerId, True)

				nextTask = get_next_task(name, expTaskOrders[expId])
				return redirect(url_for(nextTask, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))

		elif workerId_exists(expId, workerId) and completedChoiceTask == True:
			return redirect(url_for('choicetask_error', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))

"""
Auction Instructions
"""
@app.route("/auction_instructions/<expId>", methods = ["GET","POST"])
def auction_instructions(expId):
	name = 'auction'

	assignmentId = None
	if 'assignmentId' in request.args:
		assignmentId = request.args.get('assignmentId')

	if contains_necessary_args(request.args) or assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

		if workerId_exists(expId, workerId) or assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
			if request.method == "GET":
				return render_template('auction_instructions.html')
			else:
				if request.form['submit'] == 'Continue':
					if assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE': # if in preview
						nextTask = get_next_task(name, expTaskOrders[expId])
						return redirect(url_for(nextTask, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
					else:
						return redirect(url_for('auction', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
				else:
					return redirect(url_for('auction', demo='TRUE', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))

"""
Auction Demo Instructions
"""
@app.route("/auction_demo_instructions/<expId>", methods = ["GET","POST"])
def auction_demo_instructions(expId):
	name = 'auction'

	assignmentId = None
	if 'assignmentId' in request.args:
		assignmentId = request.args.get('assignmentId')

	if contains_necessary_args(request.args) or assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

		if workerId_exists(expId, workerId) or assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
			if request.method == "GET":
				return render_template('auction_demo_instructions.html')
			else:
				return redirect(url_for('auction', demo='TRUE', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))

"""
Choice Task Instructions
"""
@app.route("/choicetask_instructions/<expId>", methods = ["GET","POST"])
def choicetask_instructions(expId):
	name = 'choicetask'

	assignmentId = None
	if 'assignmentId' in request.args:
		assignmentId = request.args.get('assignmentId')

	if contains_necessary_args(request.args) or assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

		if workerId_exists(expId, workerId) or assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
			if request.method == "GET":
				return render_template('choicetask_instructions.html', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live)
			else:
				if request.form['submit'] == 'Continue':
					if assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
						return redirect(url_for('accept_hit'))
					else:
						return redirect(url_for('choicetask', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
				else:
					return redirect(url_for('choicetask', demo='TRUE', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))

"""
Choice Task Demo Instructions
"""
@app.route("/choicetask_demo_instructions/<expId>", methods = ["GET","POST"])
def choicetask_demo_instructions(expId):
	name = 'choicetask'

	assignmentId = None
	if 'assignmentId' in request.args:
		assignmentId = request.args.get('assignmentId')

	if contains_necessary_args(request.args) or assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':

		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

		if workerId_exists(expId, workerId) or assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
			if request.method == "GET":
				return render_template('choicetask_demo_instructions.html', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live)
			else:
				return redirect(url_for('choicetask', demo='TRUE', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))


"""
Consent Form (home page)
"""
@app.route("/MDMMT", methods = ["GET","POST"])
def MDMMT():
	expId = 'MDMMT'
	if request.method == "GET":
		if 'preview' in request.args and request.args.get('preview') == 'True':
			return render_template('consent_form.html')
		elif 'assignmentId' in request.args and 'hitId' in request.args and request.args.get('assignmentId') == 'ASSIGNMENT_ID_NOT_AVAILABLE':
			assignmentId = request.args.get('assignmentId')
			hitId = request.args.get('hitId')
			return redirect(url_for('check_eligibility', expId=expId, assignmentId=assignmentId, hitId=hitId))
		else:
			return render_template('consent_form.html')
	else:

		if contains_necessary_args(request.args): 
			# worker accepted HIT 
			[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
			if workerId_exists(expId, workerId) and completed_auction(expId, workerId) and completed_choice_task(expId, workerId):
				return render_template('return_hit.html')
			elif not workerId_exists(expId, workerId):
				store_subject_info(expId, workerId, assignmentId, hitId, turkSubmitTo) 

		elif 'assignmentId' in request.args and request.args.get('assignmentId') == 'ASSIGNMENT_ID_NOT_AVAILABLE':
			# worker previewing HIT
			workerId = 'abc' + str(random.randint(1000, 10000))
			assignmentId = request.args.get('assignmentId')
			hitId = 'hhhhh' + str(random.randint(10000, 100000))
			turkSubmitTo = 'www.calkins.psych.columbia.edu'
			live = request.args.get('live') == "True"

		else:
			# in testing - accessed site through www.calkins.psych.columbia.edu
			workerId = 'abc' + str(random.randint(1000, 10000))
			assignmentId = 'xxxxx' + str(random.randint(10000, 100000))
			hitId = 'hhhhh' + str(random.randint(10000, 100000))
			turkSubmitTo = 'www.calkins.psych.columbia.edu'
			live = False

			store_subject_info(expId, workerId, assignmentId, hitId, turkSubmitTo) 

		firstTask = expTaskOrders[expId][0]
		return redirect(url_for(firstTask, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))

@app.route("/check_eligibility/<expId>", methods = ["GET", "POST"])
def check_eligibility(expId):
	if request.method == "GET" and 'assignmentId' in request.args and 'hitId' in request.args:
		assignmentId = request.args.get('assignmentId')
		hitId = request.args.get('hitId')
		return render_template('check_eligibility.html', assignmentId=assignmentId, hitId=hitId)
	elif request.method == "POST" and 'assignmentId' in request.args and 'hitId' in request.args:
		workerId = request.form['workerId']
		assignmentId = request.args.get('assignmentId')
		hitId = request.args.get('hitId')
		if workerId_exists(expId, workerId) and completed_auction(expId, workerId) and completed_choice_task(expId, workerId):
			return render_template('return_hit.html')
		else:
			return redirect(url_for(expId, preview='True', assignmentId=assignmentId, hitId=hitId))
	else:
		return redirect(url_for('unauthorized_error'))


@app.route("/thankyou", methods = ["GET"])
def thankyou():
	name = 'thankyou'
	if 'assignmentId' in request.args:
		assignmentId = request.args.get('assignmentId')
		live = request.args.get('live')
		live = live == "True"
		return render_template('thankyou.html', assignmentId=assignmentId, live=live)
	else:
		return redirect(url_for('unauthorized_error'))

@app.route("/auction_error/<expId>", methods = ["GET", "POST"])
def auction_error(expId):
	name = 'auction'
	if contains_necessary_args(request.args):
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

		if request.method == "GET":
			return render_template('auction_error.html')
		else:
			nextTask = get_next_task(name, expTaskOrders[expId])
			return redirect(url_for(nextTask, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))

@app.route("/choicetask_error/<expId>", methods = ["GET"])
def choicetask_error(expId):
	name = 'choicetask'
	if contains_necessary_args(request.args):
		workerId = request.args.get('workerId')
		assignmentId = request.args.get('assignmentId')
		hitId = request.args.get('hitId')
		turkSubmitTo = request.args.get('turkSubmitTo')
		live = request.args.get('live') == "True"

		if request.method == "GET":
			nextTask = get_next_task(name, expTaskOrders[expId])
			return redirect(url_for(nextTask, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))

@app.route("/feedback/<expId>", methods=["GET","POST"])
def feedback(expId):
	name = 'feedback'
	if contains_necessary_args(request.args):
		workerId = request.args.get('workerId')
		assignmentId = request.args.get('assignmentId')
		hitId = request.args.get('hitId')
		turkSubmitTo = request.args.get('turkSubmitTo')
		live = request.args.get('live') == "True"
		if request.method == "GET":
			return render_template('feedback.html')
		else:
			feedback = request.form["feedback"]
			store_feedback(expId, workerId, feedback)
			return redirect(url_for('thankyou', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
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

@app.route("/dummy_MDMMT", methods = ["GET","POST"])
def dummy_MDMMT():
	expId = "MDMMT"
	if request.method == "GET" and 'assignmentId' in request.args and 'hitId' in request.args:
		assignmentId = request.args.get('assignmentId')
		hitId = request.args.get('hitId')
		return render_template('dummy_hit.html', assignmentId=assignmentId, hitId=hitId)
	elif request.method == "POST" and 'assignmentId' in request.args and 'hitId' in request.args:
		if 'workerId' in request.args:
			workerId = request.args.get('workerId')
		else:
			workerId = request.form['workerId']
		assignmentId = request.args.get('assignmentId')
		hitId = request.args.get('hitId')
		live = True
		if workerId_exists(expId, workerId):
			if 'workerId' in request.args and 'turkSubmitTo' in request.args:
				workerId = request.args.get('workerId')
				turkSubmitTo = request.args.get('turkSubmitTo')
				store_subject_info("dummyMDMMT", workerId, assignmentId, hitId, turkSubmitTo)
				return redirect(url_for('thankyou', assignmentId=assignmentId, live=live))
			else:
				return redirect(url_for('accept_hit'))
		else:
			return redirect(url_for('return_dummy_MDMMT', preview='True', assignmentId=assignmentId, hitId=hitId))
	else:
		return redirect(url_for('unauthorized_error'))

@app.route("/return_dummy_MDMMT", methods = ["GET"])
def return_dummy_MDMMT():
	return render_template('return_dummy_hit.html')

if __name__ == "__main__":
	app.debug = False
	app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
	app.run(host = '0.0.0.0', port = 8000)
