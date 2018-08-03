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
			expVariables = get_ratingtask_expVariables(expId, subjectId=None, demo=True, question=oneLineInstructions, leftRatingText='', middleRatingText='', rightRatingText='', rs_min=0, rs_max=10, rs_tickIncrement=1, rs_increment=0.01, rs_labelNames=["0", "", "", "", "", "5", "", "", "", "", "10"])
			return render_template('foodchoicestudies/auction.html', expVariables=expVariables, stimFolder=foodStimFolder[expId]+'demo/')
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
				expVariables = get_ratingtask_expVariables(expId, subjectId=None, demo=False, question=oneLineInstructions, leftRatingText='', middleRatingText='', rightRatingText='', rs_min=0, rs_max=10, rs_tickIncrement=1, rs_increment=0.01, rs_labelNames=["0", "", "", "", "", "5", "", "", "", "", "10"])

				return render_template('foodchoicestudies/auction.html', expVariables=expVariables, stimFolder=foodStimFolder[expId])
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
			return redirect(url_for('tasks.repeat_error', task=name, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
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
			if assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
				return redirect(url_for('accept_hit'))
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
			return redirect(url_for('tasks.repeat_error', task=name, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
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
		participatedInMDMMT = completed_task('MDMMT', workerId, 'completedChoiceTask')
		participatedInMDMRTS = completed_task('MDMRTS', workerId, 'completedSceneChoiceTask')
		participatedInMDMRTST = completed_task('MDMRTST', workerId, 'completedSceneChoiceTask')
		if participatedInMDMMT or participatedInMDMRTS or participatedInMDMRTST:
			return render_template('return_hit.html')
		else:
			return redirect(url_for("homepages."+expId, preview='True', assignmentId=assignmentId, hitId=hitId))
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
			return redirect(url_for('tasks.repeat_error', task=name, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))

@tasks.route("/instructions_questions", methods = ["GET", "POST"])
def instructions_questions(expId):
	containsAllMTurkArgs = contains_necessary_args(request.args)
	if containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
	if request.method == "GET" and containsAllMTurkArgs:
		return render_template('foodchoicestudies/instructions_questions.html')
	elif containsAllMTurkArgs: # in request.method == "POST"
		subjectId = get_subjectId(expId, workerId)
		prevN = get_worker_notes(expId, subjectId, 'numberTimesSceneChoiceTaskInstructionsQuizWasTaken')
		if prevN == None:
			prevN = 0
		add_worker_notes(expId, workerId, 'numberTimesSceneChoiceTaskInstructionsQuizWasTaken', prevN + 1)
		keys=request.form.keys()
		if request.form['submit'] == 'Submit' and 'a1' in keys and 'a2' in keys and 'a3' in keys:
			a1 = request.form['a1']
			a2 = request.form['a2']
			a3 = request.form['a3']
			if a1 == 'D' and a2 == 'E' and a3 == 'B':
				return redirect(url_for('tasks.scenechoicetask', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		else:
			return redirect(url_for('instructions.scenechoicetask_instructions', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		return redirect(url_for('tasks.scenechoicetask',expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
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
	if expId == 'MDMRTS':
		js_task_filename = '/static/foodchoicestudies/run_scenechoicetask.js'
		nTrials = 280
	elif expId == 'MDMRTST':
		js_task_filename = '/static/foodchoicestudies/run_timed_scenechoicetask.js'
		nTrials = 320

	containsAllMTurkArgs = contains_necessary_args(request.args)

	if 'demo' in request.args and containsAllMTurkArgs:
		if request.method == "GET" and request.args.get('demo') == 'TRUE':

			expVariables = get_scenechoicetask_expVariables(expId, subjectId=None, demo=True, nTrials=nTrials)
			return render_template('foodchoicestudies/scenechoicetask.html', expId=expId, expVariables=expVariables, sceneStimFolder='/static/scenes_konk/demo/',foodStimFolder=foodStimFolder[expId]+'demo/', js_task_filename=js_task_filename)
		else:
			[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
			if assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
				return redirect(url_for('accept_hit'))
			return redirect(url_for('instructions.scenechoicetask_instructions', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	elif containsAllMTurkArgs:
		# not demo - record responses now
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
		subjectId = get_subjectId(expId, workerId)

		completedAuction = completed_task(expId, workerId, 'completedAuction2')
		completedChoiceTask = completed_task(expId, workerId, 'completedSceneChoiceTask')

		if workerId_exists(expId, workerId):
			if request.method == "GET":
				### set experiment conditions here and pass to experiment.html 
				# trialVariables should be an array of dictionaries 
				# each element of the array represents the condition for one trial
				# set the variable conditions to the array of conditions

				trialListPath = dataDir + expId + '/' + subjectId + '/' + subjectId + '_TrialList_SceneChoiceTask.csv'
				dataPath = dataDir + expId + '/' + subjectId + '/' + subjectId + '_SceneChoiceTaskData.csv'
				if os.path.exists(trialListPath and dataPath):
					trialsDf = pd.read_csv(trialListPath)
					resultsDf = pd.read_csv(dataPath)
					if len(trialsDf) <= len(resultsDf): # already completed all trials of task
						nextTask = 'instructions.familiaritytask_instructions'
						return redirect(url_for(nextTask, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
				expVariables = get_scenechoicetask_expVariables(expId, subjectId, demo=False, nTrials=nTrials)
				return render_template('foodchoicestudies/scenechoicetask.html', expId=expId, expVariables=expVariables, sceneStimFolder='/static/scenes_konk/',foodStimFolder=foodStimFolder[expId], js_task_filename=js_task_filename)
			else:
				expResults = json.loads(request.form['experimentResults'])
				filePath = dataDir + expId + '/' + subjectId + '/'
				if not os.path.exists(dataDir + expId + '/' + subjectId + '/' + subjectId + '_SceneChoiceTaskData.csv'):
					results_to_csv(expId, subjectId, filePath, 'SceneChoiceTaskData.csv', expResults, {})
					nextTask = 'tasks.take_break'
				else:
					append_results_to_csv(expId, subjectId, filePath, 'SceneChoiceTaskData.csv', expResults, {})
					set_completed_task(expId, workerId, 'completedSceneChoiceTask', True)
					nextTask = 'instructions.familiaritytask_instructions'
				return redirect(url_for(nextTask, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
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
	oneLineInstructions = "How familiar are you with this food? Rate it from 0 (never eaten before) to 10 (eaten the most)."
	containsAllMTurkArgs = contains_necessary_args(request.args)

	if containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
		if workerId_exists(expId, workerId):
			if request.method == "GET":
				### set experiment conditions here and pass to experiment.html 
				# trialVariables should be an array of dictionaries 
				# each element of the array represents the condition for one trial
				# set the variable conditions to the array of conditions
				expVariables = get_ratingtask_expVariables(expId, subjectId=None, demo=False, question=oneLineInstructions, leftRatingText='never eaten before', middleRatingText='', rightRatingText='eaten the most', rs_min=0, rs_max=10, rs_tickIncrement=1, rs_increment=0.01, rs_labelNames=["0", "", "", "", "", "5", "", "", "", "", "10"])
				return render_template('foodchoicestudies/familiaritytask.html', expVariables=expVariables, stimFolder=foodStimFolder[expId])
			else:
				subjectId = get_subjectId(expId, workerId)
				expResults = json.loads(request.form['experimentResults'])
				nextTask = get_next_task(name, expTaskOrders[expId])

				filePath = dataDir + expId + '/' + subjectId + '/'
				fileName = 'FamiliarityData.csv'
				set_completed_task(expId, workerId,'completedFamiliarityTask', True)
				results_to_csv(expId, subjectId, filePath, fileName, expResults, {})

				return redirect(url_for(nextTask, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
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
