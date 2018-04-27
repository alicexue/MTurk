from flask import Flask, render_template, request, Blueprint
from flask import redirect, url_for
from flask import jsonify
import json
import random
import csv
import os
import sys
import pandas as pd
from utils import * 
from store_data import *
from manage_subject_info import *
from expInfo import *

tasks = Blueprint('tasks',  __name__, url_prefix='/<expId>')

_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
_parentDir = os.path.abspath(os.path.join(_thisDir, os.pardir))
dataDir = _parentDir + '/data/'

"""
Consent Form (home page)
"""
@tasks.route("/", methods = ["GET","POST"])
def expHome(expId):
	if expId not in expTaskOrders.keys():
		return render_template('404.html'), 404
	if request.method == "GET":
		if 'preview' in request.args and request.args.get('preview') == 'True':
			return render_template('foodchoicestudies/consent_form.html')
		elif 'assignmentId' in request.args and 'hitId' in request.args and request.args.get('assignmentId') == 'ASSIGNMENT_ID_NOT_AVAILABLE':
			assignmentId = request.args.get('assignmentId')
			hitId = request.args.get('hitId')
			return redirect(url_for('check_eligibility', expId=expId, assignmentId=assignmentId, hitId=hitId))
		else:
			return render_template('foodchoicestudies/consent_form.html')
	else:

		if contains_necessary_args(request.args): 
			# worker accepted HIT 
			[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
			if workerId_exists(expId, workerId) and completed_task(expId, workerId, 'completedAuction') and completed_choice_task(expId, workerId, 'completedChoiceTask'):
				return render_template('return_hit.html')
			elif not workerId_exists(expId, workerId):
				store_subject_info(expId, workerId, expTasksToComplete[expId], assignmentId, hitId, turkSubmitTo) 

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

			store_subject_info(expId, workerId, expTasksToComplete[expId], assignmentId, hitId, turkSubmitTo) 

		firstTask = expTaskOrders[expId][0]
		if 'instructions' in firstTask:
			firstTask = 'instructions.' + firstTask
		else:
			firstTask = 'tasks.' + firstTask
		return redirect(url_for(firstTask, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))

""" 
Auction Task

Description: 
GET: Passes list of dictionaries with stimulus information to auction.html
POST: Saves auction data and stimuli to csv files, redirects to choice task

"""
@tasks.route("/auction", methods = ["GET","POST"])
def auction(expId):
	name = 'auction'
	oneLineInstructions = "Rate how much you want to eat this food from 0 (least) to 10 (most)."
	containsAllMTurkArgs = contains_necessary_args(request.args)

	if 'demo' in request.args and containsAllMTurkArgs:
		if request.method == "GET" and request.args.get('demo') == 'TRUE':
			expVariables = get_ratingtask_expVariables(expId, subjectId=None, demo=True)
			return render_template('foodchoicestudies/auction.html', expVariables=expVariables, stimFolder=foodStimFolder[expId]+'demo/', instructions=oneLineInstructions)
		else:
			[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)	

			return redirect(url_for('instructions.auction_instructions', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	elif containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

		completedAuction = completed_task(expId, workerId,'completedAuction') or completed_task(expId, workerId,'completedAuction1')

		if workerId_exists(expId, workerId) and (completedAuction == False or repeatAuction[expId] == True):
			if request.method == "GET":
				### set experiment conditions here and pass to experiment.html 
				# trialVariables should be an array of dictionaries 
				# each element of the array represents the condition for one trial
				# set the variable conditions to the array of conditions
				expVariables = get_ratingtask_expVariables(expId, subjectId=None, demo=False)

				return render_template('foodchoicestudies/auction.html', expVariables=expVariables, stimFolder=foodStimFolder[expId], instructions=oneLineInstructions)
			else:
				subjectId = get_subjectId(expId, workerId)
				expResults = json.loads(request.form['experimentResults'])
				nextTask = get_next_task(name, expTaskOrders[expId])

				filePath = dataDir + expId + '/' + subjectId + '/'
				if completedAuction == False and repeatAuction[expId] == True:
					auctionFileName = 'AuctionData1.csv'
					nextTask = 'instructions.auction_repeat_instructions'
					set_completed_task(expId, workerId,'completedAuction1', True)
				elif completedAuction == True and repeatAuction[expId] == True:
					auctionFileName = 'AuctionData2.csv'
					set_completed_task(expId, workerId,'completedAuction2', True)
				else:
					auctionFileName = 'AuctionData.csv'
					set_completed_task(expId, workerId,'completedAuction', True)
				results_to_csv(expId, subjectId, filePath, auctionFileName, expResults, {})

				return redirect(url_for(nextTask, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		elif workerId_exists(expId, workerId) and completedAuction == True:
			return redirect(url_for('repeat_error', task=name, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
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
@tasks.route("/choicetask", methods = ["GET","POST"])
def choicetask(expId):
	name = 'choicetask'
	containsAllMTurkArgs = contains_necessary_args(request.args)

	if 'demo' in request.args and containsAllMTurkArgs:
		if request.method == "GET" and request.args.get('demo') == 'TRUE':
			[stim1Names, stim1Bids, stim2Names, stim2Bids] = get_two_stimuli_lists_without_bids(foodStimFolder[expId]+'demo/', '', '.bmp')
			expVariables = [] # array of dictionaries

			deltas = []
			for i in range(0,len(stim1Bids)):
				deltas.append(stim2Bids[i] - stim1Bids[i])

			for i in range(0,len(stim1Bids)):
				expVariables.append({"stimulus1":stim1Names[i],"stimulus2":stim2Names[i],"stim1Bid":stim1Bids[i],"stim2Bid":stim2Bids[i], "delta":deltas[i], "fullStim1Name":stim1Names[i]+".bmp", "fullStim2Name":stim2Names[i]+".bmp"})
			return render_template('foodchoicestudies/choicetask.html', expId=expId, expVariables=expVariables, stimFolder=foodStimFolder[expId]+'demo/')
		else:
			[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

			return redirect(url_for('instructions.choicetask_instructions', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	elif containsAllMTurkArgs:
		# not demo - record responses now
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
		subjectId = get_subjectId(expId, workerId)

		completedAuction = completed_task(expId, workerId, 'completedAuction')
		completedChoiceTask = completed_task(expId, workerId, 'completedChoiceTask')

		if workerId_exists(expId, workerId) and completedChoiceTask == False:
			if request.method == "GET":
				### set experiment conditions here and pass to experiment.html 
				# trialVariables should be an array of dictionaries 
				# each element of the array represents the condition for one trial
				# set the variable conditions to the array of conditions

				if completed_task(expId, workerId, 'completedAuction'):
					stim1Bids = [];
					stim2Bids = [];

					if completedAuction == True and repeatAuction[expId] == True:
						auctionFileName = '_AuctionData2.csv'
					else:
						auctionFileName = '_AuctionData.csv'
					stimBidDict = get_bid_responses(dataDir + expId + '/' + subjectId + '/' + subjectId + auctionFileName)
					[stim1Names, stim1Bids, stim2Names, stim2Bids] = get_two_stimuli_lists(stimBidDict, foodStimFolder[expId], '', '.bmp')
					expVariables = [] # array of dictionaries

					deltas = []
					for i in range(0,len(stim1Bids)):
						deltas.append(stim2Bids[i] - stim1Bids[i])

					for i in range(0,len(stim1Bids)):
						expVariables.append({"stimulus1":stim1Names[i],"stimulus2":stim2Names[i],"stim1Bid":stim1Bids[i],"stim2Bid":stim2Bids[i], "delta":deltas[i], "fullStim1Name":stim1Names[i]+".bmp", "fullStim2Name":stim2Names[i]+".bmp"})

					return render_template('foodchoicestudies/choicetask.html', expId=expId, expVariables=expVariables, stimFolder=foodStimFolder[expId])
				else:
					return redirect(url_for('unauthorized_error'))
			else:
				expResults = json.loads(request.form['experimentResults'])
				filePath = dataDir + expId + '/' + subjectId + '/'
				results_to_csv(expId, subjectId, filePath, 'ChoiceTaskData.csv', expResults, {})

				set_completed_task(expId, workerId, 'completedChoiceTask', True)

				nextTask = get_next_task(name, expTaskOrders[expId])
				return redirect(url_for(nextTask, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))

		elif workerId_exists(expId, workerId) and completedChoiceTask == True:
			return redirect(url_for('repeat_error', task=name, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))

@tasks.route("/check_eligibility", methods = ["GET", "POST"])
def check_eligibility(expId):
	if request.method == "GET" and 'assignmentId' in request.args and 'hitId' in request.args:
		assignmentId = request.args.get('assignmentId')
		hitId = request.args.get('hitId')
		return render_template('check_eligibility.html', assignmentId=assignmentId, hitId=hitId)
	elif request.method == "POST" and 'assignmentId' in request.args and 'hitId' in request.args:
		workerId = request.form['workerId']
		assignmentId = request.args.get('assignmentId')
		hitId = request.args.get('hitId')
		if workerId_exists(expId, workerId) and completed_task(expId, workerId, 'completedAuction') and completed_choice_task(expId, workerId, 'completedChoiceTask'):
			return render_template('return_hit.html')
		else:
			return redirect(url_for(expId, preview='True', assignmentId=assignmentId, hitId=hitId))
	else:
		return redirect(url_for('unauthorized_error'))

@tasks.route("/auction_error", methods = ["GET", "POST"])
def auction_error(expId):
	name = 'auction'
	if contains_necessary_args(request.args):
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

		if request.method == "GET":
			return render_template('foodchoicestudies/auction_error.html')
		else:
			nextTask = get_next_task(name, expTaskOrders[expId])
			return redirect(url_for(nextTask, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))

"""
@tasks.route("/dummy_MDMMT", methods = ["GET","POST"])
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
				store_subject_info("dummyMDMMT", workerId, expTasksToComplete["MDMMT"], assignmentId, hitId, turkSubmitTo) 
				return redirect(url_for('thankyou', assignmentId=assignmentId, live=live))
			else:
				return redirect(url_for('accept_hit'))
		else:
			return redirect(url_for('return_dummy_MDMMT', preview='True', assignmentId=assignmentId, hitId=hitId))
	else:
		return redirect(url_for('unauthorized_error'))

@tasks.route("/return_dummy_MDMMT", methods = ["GET"])
def return_dummy_MDMMT():
	return render_template('return_dummy_hit.html')
"""


""" 
Scene Task

Description: 
GET: Passes list of dictionaries with stimulus information to auction.html
POST: Saves auction data and stimuli to csv files, redirects to choice task

"""
@tasks.route("/scenetask", methods = ["GET","POST"])
def scenetask(expId):
	### need to adjust complete auction stuff
	name = 'scenetask'
	containsAllMTurkArgs = contains_necessary_args(request.args)

	if 'demo' in request.args and containsAllMTurkArgs:
		if request.method == "GET" and request.args.get('demo') == 'TRUE':
			expVariables = get_scenetask_expVariables(expId, subjectId=None, demo=True)
			return render_template('foodchoicestudies/scenetask.html', expVariables=expVariables, stimFolder='/static/scenes_konk/demo/')
		else:
			[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
			return redirect(url_for('instructions.scenetask_instructions', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	elif containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

		completedAuction = completed_task(expId, workerId, 'completedAuction')

		if workerId_exists(expId, workerId) and (completedAuction == False or repeatAuction[expId] == True):
			subjectId = get_subjectId(expId, workerId)
			if request.method == "GET":
				expVariables = get_scenetask_expVariables(expId, subjectId=subjectId, demo=False)
				return render_template('foodchoicestudies/scenetask.html', expVariables=expVariables, stimFolder='/static/scenes_konk/')
			else:
				expResults = json.loads(request.form['experimentResults'])
				nextTask = get_next_task(name, expTaskOrders[expId])

				filePath = dataDir + expId + '/' + subjectId + '/'
				results_to_csv(expId, subjectId, filePath, 'SceneTask.csv', expResults, {})

				set_completed_task(expId, workerId, 'completedSceneTask', True)

				return redirect(url_for(nextTask, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		elif workerId_exists(expId, workerId) and completedAuction == True:
			### need to modify this!!!
			return redirect(url_for('repeat_error', task=name, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))

""" 
Scene and Choice Task

Description: 
GET: Retrieves stimulus ratings from auction data file, sets up stimuli for choice task
POST: Saves choice task data and stimuli to csv files, redirects to thank you page

"""
@tasks.route("/scenechoicetask", methods = ["GET","POST"])
def scenechoicetask(expId):
	name = 'scenechoicetask'

	containsAllMTurkArgs = contains_necessary_args(request.args)

	if 'demo' in request.args and containsAllMTurkArgs:
		if request.method == "GET" and request.args.get('demo') == 'TRUE':

			expVariables = get_scenechoicetask_expVariables(expId, subjectId=None, demo=True)
			return render_template('foodchoicestudies/scenechoicetask.html', expId=expId, expVariables=expVariables, sceneStimFolder='/static/scenes_konk/demo/',foodStimFolder=foodStimFolder[expId]+'demo/')
		else:
			[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

			return redirect(url_for('instructions.scenechoicetask_instructions', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	elif containsAllMTurkArgs:
		# not demo - record responses now
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
		subjectId = get_subjectId(expId, workerId)

		completedAuction = completed_task(expId, workerId, 'completedAuction2')
		completedChoiceTask = completed_task(expId, workerId, 'completedSceneChoiceTask')

		if workerId_exists(expId, workerId) and completedChoiceTask == False:
			if request.method == "GET":
				### set experiment conditions here and pass to experiment.html 
				# trialVariables should be an array of dictionaries 
				# each element of the array represents the condition for one trial
				# set the variable conditions to the array of conditions

				if completed_task(expId, workerId, 'completedAuction2'):

					expVariables = get_scenechoicetask_expVariables(expId, subjectId, demo=False)
					return render_template('foodchoicestudies/scenechoicetask.html', expId=expId, expVariables=expVariables, sceneStimFolder='/static/scenes_konk/',foodStimFolder=foodStimFolder[expId])
				else:
					return redirect(url_for('unauthorized_error'))
			else:
				expResults = json.loads(request.form['experimentResults'])
				filePath = dataDir + expId + '/' + subjectId + '/'
				if not os.path.exists(dataDir + expId + '/' + subjectId + '/' + subjectId + '_SceneChoiceTaskData.csv'):
					results_to_csv(expId, subjectId, filePath, 'SceneChoiceTaskData.csv', expResults, {})
					nextTask = get_next_task(name, expTaskOrders[expId])
				else:
					append_results_to_csv(expId, subjectId, filePath, 'SceneChoiceTaskData.csv', expResults, {})
					set_completed_task(expId, workerId, 'completedSceneChoiceTask', True)
					nextTask = 'instructions.familiaritytask_instructions'
				
				return redirect(url_for(nextTask, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))

		elif workerId_exists(expId, workerId) and completedChoiceTask == True:
			return redirect(url_for('tasks.repeat_error', task=name, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))


""" 
Familiarity Task
"""
@tasks.route("/familiaritytask", methods = ["GET","POST"])
def familiaritytask(expId):
	name = 'familiaritytask'
	oneLineInstructions = "How familiar are you with this food? Rate it from 0 (never eaten before) to 10 (eat a few times a week)."
	containsAllMTurkArgs = contains_necessary_args(request.args)

	if containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

		completedFamiliarityTask = completed_task(expId, workerId,'completedFamiliarityTask') 

		if workerId_exists(expId, workerId) and completedFamiliarityTask == False:
			if request.method == "GET":
				### set experiment conditions here and pass to experiment.html 
				# trialVariables should be an array of dictionaries 
				# each element of the array represents the condition for one trial
				# set the variable conditions to the array of conditions
				expVariables = get_ratingtask_expVariables(expId, subjectId=None, demo=False)

				return render_template('foodchoicestudies/familiaritytask.html', expVariables=expVariables, stimFolder=foodStimFolder[expId], instructions=oneLineInstructions)
			else:
				subjectId = get_subjectId(expId, workerId)
				expResults = json.loads(request.form['experimentResults'])
				nextTask = get_next_task(name, expTaskOrders[expId])

				filePath = dataDir + expId + '/' + subjectId + '/'
				fileName = 'FamiliarityData.csv'
				set_completed_task(expId, workerId,'completedFamiliarityTask', True)
				results_to_csv(expId, subjectId, filePath, fileName, expResults, {})

				return redirect(url_for(nextTask, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		elif workerId_exists(expId, workerId) and completedFamiliarityTask == True:
			return redirect(url_for('tasks.repeat_error', task=name, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))

@tasks.route("/repeat_error/<task>", methods = ["GET", "POST"])
def repeat_error(expId, task):
	if contains_necessary_args(request.args):
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

		if request.method == "GET":
			return render_template('repeat_error.html')
		else:
			nextTask = get_next_task(task, expTaskOrders[expId])
			return redirect(url_for(nextTask, taskName=task, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))

@tasks.route("/take_break", methods = ["GET", "POST"])
def take_break(expId):
	task = "take_break"
	if contains_necessary_args(request.args):
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

		if request.method == "GET":
			return render_template('break.html')
		else:
			nextTask = get_next_task(task, expTaskOrders[expId])
			return redirect(url_for(nextTask, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))
