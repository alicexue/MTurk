from MTurkApp import app
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
from flask_core import *

_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)

repeatAuction = {'MDMMT':False, 'MDMRTS':True}
foodStimFolder = {'MDMMT':'/static/foodstim60/', 'MDMRTS':'/static/foodstim80/'}
MDMMT_taskOrder = ['auction_demo_instructions', 'auction', 'choicetask_demo_instructions', 'choicetask', 'feedback'] # order of tasks in experiment
MDMRTS_taskOrder = ['auction_demo_instructions', 'auction', 'scenetask_demo_instructions', 'scenetask', 'scenechoicetask_demo_instructions', 'scenechoicetask', 'take_break', 'scenechoicetask', 'feedback'] # order of tasks in experiment
# feedback here doesn't get applied
expTaskOrders = {'MDMMT':MDMMT_taskOrder, 'MDMRTS':MDMRTS_taskOrder} # dictionary of experiments - key is exp name, value is order of tasks

MDMMT_tasksToComplete = {'completedAuction':False, 'completedChoiceTask':False} # for manage_subject_data
MDMRTS_tasksToComplete = {'completedAuction1':False, 'completedAuction2':False, 'completeSceneTask':False, 'completedSceneChoiceTask':False} # for manage_subject_data
expTasksToComplete = {'MDMMT':MDMMT_tasksToComplete, 'MDMRTS':MDMRTS_tasksToComplete} 

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
		return redirect(url_for(firstTask, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))


"""
Consent Form (home page)
"""
@app.route("/MDMRTS", methods = ["GET","POST"])
def MDMRTS():
	expId = 'MDMRTS'
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
		return redirect(url_for(firstTask, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))

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
			stimuli = get_stimuli(foodStimFolder[expId]+'demo/','','.bmp')
			random.shuffle(stimuli)

			expVariables = [] # array of dictionaries

			for i in range(0,len(stimuli)):
				expVariables.append({"stimulus1":stimuli[i], "fullStimName":stimuli[i]+".bmp"})

			return render_template('auction.html', expVariables=expVariables, stimFolder=foodStimFolder[expId]+'demo/')
		else:

			workerId = request.args.get('workerId')
			assignmentId = request.args.get('assignmentId')
			hitId = request.args.get('hitId')
			turkSubmitTo = request.args.get('turkSubmitTo')
			live = request.args.get('live') == "True"

			return redirect(url_for('auction_instructions', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	elif containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

		completedAuction = completed_task(expId, workerId,'completedAuction') or completed_task(expId, workerId,'completedAuction1')

		if workerId_exists(expId, workerId) and (completedAuction == False or repeatAuction[expId] == True):
			if request.method == "GET":
				### set experiment conditions here and pass to experiment.html 
				# trialVariables should be an array of dictionaries 
				# each element of the array represents the condition for one trial
				# set the variable conditions to the array of conditions
				stimuli = get_stimuli(foodStimFolder[expId],'','.bmp')
				random.shuffle(stimuli)

				expVariables = [] # array of dictionaries

				for i in range(0,len(stimuli)):
					expVariables.append({"stimulus":stimuli[i], "fullStimName":stimuli[i]+".bmp"})

				return render_template('auction.html', expVariables=expVariables, stimFolder=foodStimFolder[expId])
			else:
				subjectId = get_subjectId(expId, workerId)
				expResults = json.loads(request.form['experimentResults'])
				nextTask = get_next_task(name, expTaskOrders[expId])

				filePath = _thisDir + '/data/' + expId + '/' + subjectId + '/'
				if completedAuction == False and repeatAuction[expId] == True:
					auctionFileName = 'AuctionData1.csv'
					nextTask = 'auction_repeat_instructions'
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
@app.route("/choicetask/<expId>", methods = ["GET","POST"])
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
			return render_template('choicetask.html', expId=expId, expVariables=expVariables, stimFolder=foodStimFolder[expId]+'demo/')
		else:
			[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

			return redirect(url_for('choicetask_instructions', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
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
					stimBidDict = get_bid_responses(_thisDir + '/data/' + expId + '/' + subjectId + '/' + subjectId + auctionFileName)
					[stim1Names, stim1Bids, stim2Names, stim2Bids] = get_two_stimuli_lists(stimBidDict, foodStimFolder[expId], '', '.bmp')
					expVariables = [] # array of dictionaries

					deltas = []
					for i in range(0,len(stim1Bids)):
						deltas.append(stim2Bids[i] - stim1Bids[i])

					for i in range(0,len(stim1Bids)):
						expVariables.append({"stimulus1":stim1Names[i],"stimulus2":stim2Names[i],"stim1Bid":stim1Bids[i],"stim2Bid":stim2Bids[i], "delta":deltas[i], "fullStim1Name":stim1Names[i]+".bmp", "fullStim2Name":stim2Names[i]+".bmp"})

					return render_template('choicetask.html', expId=expId, expVariables=expVariables, stimFolder=foodStimFolder[expId])
				else:
					return redirect(url_for('unauthorized_error'))
			else:
				expResults = json.loads(request.form['experimentResults'])
				filePath = _thisDir + '/data/' + expId + '/' + subjectId + '/'
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
		if workerId_exists(expId, workerId) and completed_task(expId, workerId, 'completedAuction') and completed_choice_task(expId, workerId, 'completedChoiceTask'):
			return render_template('return_hit.html')
		else:
			return redirect(url_for(expId, preview='True', assignmentId=assignmentId, hitId=hitId))
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

@app.route("/repeat_error/<expId>/<task>", methods = ["GET", "POST"])
def repeat_error(expId, task):
	if contains_necessary_args(request.args):
		workerId = request.args.get('workerId')
		assignmentId = request.args.get('assignmentId')
		hitId = request.args.get('hitId')
		turkSubmitTo = request.args.get('turkSubmitTo')
		live = request.args.get('live') == "True"

		if request.method == "GET":
			return render_template('repeat_error.html')
		else:
			nextTask = get_next_task(task, expTaskOrders[expId])
			return redirect(url_for(nextTask, taskName=task, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))

@app.route("/take_break/<expId>", methods = ["GET", "POST"])
def take_break(expId):
	task = "take_break"
	if contains_necessary_args(request.args):
		workerId = request.args.get('workerId')
		assignmentId = request.args.get('assignmentId')
		hitId = request.args.get('hitId')
		turkSubmitTo = request.args.get('turkSubmitTo')
		live = request.args.get('live') == "True"

		if request.method == "GET":
			return render_template('break.html')
		else:
			nextTask = get_next_task(task, expTaskOrders[expId])
			return redirect(url_for(nextTask, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))

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
				store_subject_info("dummyMDMMT", workerId, expTasksToComplete["MDMMT"], assignmentId, hitId, turkSubmitTo) 
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

""" 
Scene Task

Description: 
GET: Passes list of dictionaries with stimulus information to auction.html
POST: Saves auction data and stimuli to csv files, redirects to choice task

"""
@app.route("/scenetask/<expId>", methods = ["GET","POST"])
def scenetask(expId):
	### need to adjust complete auction stuff
	name = 'scenetask'
	containsAllMTurkArgs = contains_necessary_args(request.args)

	if 'demo' in request.args and containsAllMTurkArgs:
		indoor_folders = ['library-68']
		outdoor_folders = ['woods-68']
		if request.method == "GET" and request.args.get('demo') == 'TRUE':
			[stim1Names, stim1Bids, stim2Names, stim2Bids] = get_two_stimuli_lists_without_bids(foodStimFolder[expId]+'demo/', '', '.bmp')
			indoor_stimuli = []
			outdoor_stimuli = []
			for folder in indoor_folders:
				indoor_stimuli += get_stimuli('/static/scenes_konk/demo/indoor/' + folder + '/', 'indoor/' + folder + '/', '.jpg')
			for folder in outdoor_folders:
				outdoor_stimuli += get_stimuli('/static/scenes_konk/demo/outdoor/' + folder + '/', 'outdoor/' + folder + '/', '.jpg')
			sceneStimuli = indoor_stimuli + outdoor_stimuli
			random.shuffle(sceneStimuli)

			expVariables = []
			
			indoorsKey = "u"
			outdoorsKey = "i"

			expVariables = [] # array of dictionaries

			for i in range(0,len(sceneStimuli)):
				stimulus = sceneStimuli[i]
				index = stimulus.find('/')
				stimulusType = stimulus[0:index] # indoor / outdoor
				expVariables.append({"sceneStimulus":stimulusType, "fullStimName":stimulus+".jpg", "indoorsKey":indoorsKey, "outdoorsKey":outdoorsKey})

			return render_template('scenetask.html', expVariables=expVariables, stimFolder='/static/scenes_konk/demo/')
		else:

			workerId = request.args.get('workerId')
			assignmentId = request.args.get('assignmentId')
			hitId = request.args.get('hitId')
			turkSubmitTo = request.args.get('turkSubmitTo')
			live = request.args.get('live') == "True"

			return redirect(url_for('scenetask_instructions', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	elif containsAllMTurkArgs:
		indoor_folders = ['bathroom-68','bedroom-68','classroom-68','conferenceroom-68','diningroom-68','empty-68','gym-68','hairsalon-68']
		outdoor_folders = ['beach-68','campsite-68','canyon-68','countryroad-68','field-68','garden-68','golfcourse-68','mountainwhite-68']
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

		completedAuction = completed_task(expId, workerId, 'completedAuction')

		if workerId_exists(expId, workerId) and (completedAuction == False or repeatAuction[expId] == True):
			if request.method == "GET":
				### set experiment conditions here and pass to experiment.html 
				# trialVariables should be an array of dictionaries 
				# each element of the array represents the condition for one trial
				# set the variable conditions to the array of conditions
				indoor_stimuli = []
				outdoor_stimuli = []

				for folder in indoor_folders:
					indoor_stimuli += get_stimuli('/static/scenes_konk/indoor/' + folder + '/', 'indoor/' + folder + '/', '.jpg')
				for folder in outdoor_folders:
					outdoor_stimuli += get_stimuli('/static/scenes_konk/outdoor/' + folder + '/', 'outdoor/' + folder + '/', '.jpg')

				# pick 3 indoor and 3 outdoor stimuli for subject to be familiarized to
				f_indoor_stimuli = []
				while len(f_indoor_stimuli) != 3:
					r = random.randrange(len(indoor_stimuli))
					if indoor_stimuli[r] not in f_indoor_stimuli:
						f_indoor_stimuli.append(indoor_stimuli[r])
				f_outdoor_stimuli = []
				while len(f_outdoor_stimuli) != 3:
					r = random.randrange(len(outdoor_stimuli))
					if outdoor_stimuli[r] not in f_outdoor_stimuli:
						f_outdoor_stimuli.append(outdoor_stimuli[r])
				
				f_stimuli = f_indoor_stimuli + f_outdoor_stimuli

				random.shuffle(f_stimuli)

				stimuli = []

				for i in range(0, 4): # 4 repeats of stimuli
					random.shuffle(f_stimuli)
					stimuli += f_stimuli

				subjectId = get_subjectId(expId, workerId)
				index = subjectId.find('_')
				subjectN = int(subjectId[index+1:])
				
				if (subjectN%2==0):
					indoorsKey = "u"
					outdoorsKey = "i"
				else:
					indoorsKey = "i"
					outdoorsKey = "u"

				expVariables = [] # array of dictionaries

				for i in range(0,len(stimuli)):
					stimulus = stimuli[i]
					index = stimulus.find('/')
					stimulusType = stimulus[0:index] # indoor / outdoor
					expVariables.append({"sceneStimulus":stimulusType, "fullStimName":stimulus+".jpg", "indoorsKey":indoorsKey, "outdoorsKey":outdoorsKey})

				return render_template('scenetask.html', expVariables=expVariables, stimFolder='/static/scenes_konk/')
			else:
				subjectId = get_subjectId(expId, workerId)
				expResults = json.loads(request.form['experimentResults'])
				nextTask = get_next_task(name, expTaskOrders[expId])

				filePath = _thisDir + '/data/' + expId + '/' + subjectId + '/'
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
@app.route("/scenechoicetask/<expId>", methods = ["GET","POST"])
def scenechoicetask(expId):
	name = 'scenechoicetask'

	containsAllMTurkArgs = contains_necessary_args(request.args)

	if 'demo' in request.args and containsAllMTurkArgs:
		indoor_folders = ['library-68']
		outdoor_folders = ['woods-68']
		if request.method == "GET" and request.args.get('demo') == 'TRUE':
			[stim1Names, stim1Bids, stim2Names, stim2Bids] = get_two_stimuli_lists_without_bids(foodStimFolder[expId]+'demo/', '', '.bmp')
			indoor_stimuli = []
			outdoor_stimuli = []
			for folder in indoor_folders:
				indoor_stimuli += get_stimuli('/static/scenes_konk/demo/indoor/' + folder + '/', 'indoor/' + folder + '/', '.jpg')
			for folder in outdoor_folders:
				outdoor_stimuli += get_stimuli('/static/scenes_konk/demo/outdoor/' + folder + '/', 'outdoor/' + folder + '/', '.jpg')
			sceneStimuli = indoor_stimuli + outdoor_stimuli
			random.shuffle(sceneStimuli)

			expVariables = [] # array of dictionaries

			deltas = []
			for i in range(0,len(sceneStimuli)):
				deltas.append(stim2Bids[i] - stim1Bids[i])

			for i in range(0,len(sceneStimuli)):
				sceneStimulus = sceneStimuli[i]
				index = sceneStimulus.find('/')
				stimulusType = sceneStimulus[0:index] # indoor / outdoor
				if (i%2==0):
					sceneStimulusStatus = 'novel'
				else:
					sceneStimulusStatus = 'familiar'
				expVariables.append({"sceneStimulus":stimulusType, "stimulus1":stim1Names[i],"stimulus2":stim2Names[i],"stim1Bid":stim1Bids[i],"stim2Bid":stim2Bids[i], "delta":deltas[i], "fullSceneStimName":sceneStimulus+".jpg", "fullStim1Name":stim1Names[i]+".bmp", "fullStim2Name":stim2Names[i]+".bmp","sceneStimulusStatus":sceneStimulusStatus})
			return render_template('scenechoicetask.html', expId=expId, expVariables=expVariables, sceneStimFolder='/static/scenes_konk/demo/',foodStimFolder=foodStimFolder[expId]+'demo/')
		else:
			[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

			return redirect(url_for('scenechoicetask_instructions', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	elif containsAllMTurkArgs:
		indoor_folders = ['bathroom-68','bedroom-68','classroom-68','conferenceroom-68','diningroom-68','empty-68','gym-68','hairsalon-68']
		outdoor_folders = ['beach-68','campsite-68','canyon-68','countryroad-68','field-68','garden-68','golfcourse-68','mountainwhite-68']
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

					if not os.path.exists(_thisDir + '/data/' + expId + '/' + subjectId + '/' + subjectId + '_TrialList_SceneChoiceTask.csv'):
						## subject hasn't done any portion of the Choice Scene Task yet

						auctionFileName = '_AuctionData2.csv'
						stimBidDict = get_bid_responses(_thisDir + '/data/' + expId + '/' + subjectId + '/' + subjectId + auctionFileName)
						#[stim1Names, stim1Bids, stim2Names, stim2Bids] = get_two_stimuli_lists(stimBidDict, foodStimFolder[expId], '', '.bmp')
						indoor_stimuli = []
						outdoor_stimuli = []
						for folder in indoor_folders:
							indoor_stimuli += get_stimuli('/static/scenes_konk/indoor/' + folder + '/', 'indoor/' + folder + '/', '.jpg')
						for folder in outdoor_folders:
							outdoor_stimuli += get_stimuli('/static/scenes_konk/outdoor/' + folder + '/', 'outdoor/' + folder + '/', '.jpg')

						familiarStim = get_familiar_stimuli(_thisDir + '/data/' + expId + '/' + subjectId + '/' + subjectId + '_SceneTask.csv', 'sceneStimulusPath')
						familiar_indoor_stimuli = familiarStim['indoor']
						familiar_outdoor_stimuli = familiarStim['outdoor']

						shuffledDf = get_scene_food_stimuli(stimBidDict, familiar_indoor_stimuli, familiar_outdoor_stimuli, indoor_stimuli, outdoor_stimuli, foodStimFolder[expId], '', '.bmp')
						
						shuffledDf.to_csv(_thisDir + '/data/' + expId + '/' + subjectId + '/' + subjectId + '_TrialList_SceneChoiceTask.csv', index=False)
						shuffledDf = shuffledDf[0:len(shuffledDf)/2]

					else:
						shuffledDf = pd.read_csv(_thisDir + '/data/' + expId + '/' + subjectId + '/' + subjectId + '_TrialList_SceneChoiceTask.csv')
						shuffledDf = shuffledDf[len(shuffledDf)/2:]

					stim1Names = shuffledDf['stimulus1'].values
					stim2Names = shuffledDf['stimulus2'].values
					stim1Bids = shuffledDf['stim1Bid'].values
					stim2Bids = shuffledDf['stim2Bid'].values
					sceneStimuli = shuffledDf['sceneStimulus'].values
					sceneStimuliStatus = shuffledDf['sceneStimulusFamiliarity'].values 

					expVariables = [] # array of dictionaries

					deltas = []
					for i in range(0,len(stim1Bids)):
						deltas.append(stim2Bids[i] - stim1Bids[i])

					for i in range(0,len(stim1Bids)):
						sceneStimulus = sceneStimuli[i]
						index = sceneStimulus.find('/')
						stimulusType = sceneStimulus[0:index] # indoor / outdoor
						expVariables.append({"sceneStimulus":stimulusType, "stimulus1":stim1Names[i],"stimulus2":stim2Names[i],"stim1Bid":stim1Bids[i],"stim2Bid":stim2Bids[i], "delta":deltas[i], "fullSceneStimName":sceneStimulus+".jpg", "fullStim1Name":stim1Names[i]+".bmp", "fullStim2Name":stim2Names[i]+".bmp","sceneStimulusStatus":sceneStimuliStatus[i]})

					return render_template('scenechoicetask.html', expId=expId, expVariables=expVariables, sceneStimFolder='/static/scenes_konk/',foodStimFolder=foodStimFolder[expId])
				else:
					return redirect(url_for('unauthorized_error'))
			else:
				expResults = json.loads(request.form['experimentResults'])
				filePath = _thisDir + '/data/' + expId + '/' + subjectId + '/'
				if not os.path.exists(_thisDir + '/data/' + expId + '/' + subjectId + '/' + subjectId + '_SceneChoiceTaskData.csv'):
					results_to_csv(expId, subjectId, filePath, 'SceneChoiceTaskData.csv', expResults, {})
					nextTask = get_next_task(name, expTaskOrders[expId])
				else:
					append_results_to_csv(expId, subjectId, filePath, 'SceneChoiceTaskData.csv', expResults, {})
					set_completed_task(expId, workerId, 'completedSceneChoiceTask', True)
					nextTask = 'feedback'
				
				return redirect(url_for(nextTask, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))

		elif workerId_exists(expId, workerId) and completedChoiceTask == True:
			return redirect(url_for('repeat_error', task=name, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))
