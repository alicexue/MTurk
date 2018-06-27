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

expId='SCP'
foodStimFolder='/static/foodstim2/'

scp = Blueprint('scp',  __name__, url_prefix='/SCP')

_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
_parentDir = os.path.abspath(os.path.join(_thisDir, os.pardir))
dataDir = _parentDir + '/data/'

expTasksToComplete={'completedRatingsTask':False,'completedChoiceTask':False,'completedTREQr18':False,'completedEAT26':False}

@scp.route("", methods = ["GET","POST"])
@scp.route("/consent_form", methods = ["GET","POST"])
def consent_form():
	if request.method == "GET":
		#if 'preview' in request.args and request.args.get('preview') == 'True':
		return render_template('stimcharproj/consent_form.html')
	else:
		if contains_necessary_args(request.args): 
			# worker accepted HIT 
			[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
			if workerId_exists(expId, workerId) and (completed_task(expId, workerId, 'completedRatingsTask')):
				return render_template('return_hit.html')
			elif not workerId_exists(expId, workerId):
				store_subject_info(expId, workerId, expTasksToComplete, assignmentId, hitId, turkSubmitTo) 
		elif 'assignmentId' in request.args and request.args.get('assignmentId') == 'ASSIGNMENT_ID_NOT_AVAILABLE':
			# worker previewing HIT
			workerId = 'testWorker' + str(random.randint(1000, 10000))
			assignmentId = request.args.get('assignmentId')
			hitId = 'testHIT' + str(random.randint(10000, 100000))
			turkSubmitTo = 'www.calkins.psych.columbia.edu'
			live = request.args.get('live') == "True"

		else:
			# in testing - accessed site through www.calkins.psych.columbia.edu
			workerId = 'testWorker' + str(random.randint(1000, 10000))
			assignmentId = 'testAssignment' + str(random.randint(10000, 100000))
			hitId = 'testHIT' + str(random.randint(10000, 100000))
			turkSubmitTo = 'www.calkins.psych.columbia.edu'
			live = False
			store_subject_info(expId, workerId, expTasksToComplete, assignmentId, hitId, turkSubmitTo) 
		return redirect(url_for('.ratingtask_demo_instructions', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))

@scp.route("/ratingtask_demo_instructions", methods = ["GET","POST"])
def ratingtask_demo_instructions():
	containsAllMTurkArgs = contains_necessary_args(request.args)
	if containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
	if request.method == "GET" and containsAllMTurkArgs:
		return render_template('stimcharproj/ratingtask_demo_instructions.html')
	elif containsAllMTurkArgs:
		return redirect(url_for('.ratingtask',demo=True,expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))

@scp.route("/ratingtask_instructions", methods = ["GET","POST"])
def ratingtask_instructions():
	containsAllMTurkArgs = contains_necessary_args(request.args)
	if containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
	if request.method == "GET" and containsAllMTurkArgs:
		return render_template('stimcharproj/ratingtask_instructions.html')
	elif containsAllMTurkArgs:
		return redirect(url_for('.ratingtask',expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))

@scp.route("/ratingtask", methods = ["GET","POST"])
def ratingtask():
	oneLineInstructions = "Rate how much you want to eat this food from 0 (least) to 10 (most)."
	containsAllMTurkArgs = contains_necessary_args(request.args)

	if 'demo' in request.args and containsAllMTurkArgs:
		if request.method == "GET" and request.args.get('demo') == 'True':
			expVariables = get_ratingtask_expVariables(stimFolder='/static/foodstim2/demo/',demo=True)
			return render_template('stimcharproj/ratingtask.html', demo='True',expVariables=expVariables, stimFolder='/static/foodstim2/demo/')
		else:
			[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
			"""
			if assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
				return redirect(url_for('accept_hit'))
			"""
			return redirect(url_for('.ratingtask_instructions', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	elif containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

		if workerId_exists(expId, workerId):
			if request.method == "GET":
				### set experiment conditions here and pass to experiment.html 
				# trialVariables should be an array of dictionaries 
				# each element of the array represents the condition for one trial
				# set the variable conditions to the array of conditions
				expVariables = get_ratingtask_expVariables(stimFolder='/static/foodstim2/',demo=False)

				return render_template('stimcharproj/ratingtask.html', demo='False', expVariables=expVariables, stimFolder='/static/foodstim2/')
			else:
				subjectId = get_subjectId(expId, workerId)

				filePath = dataDir + expId + '/' + subjectId + '/'

				hungerRatingResults=json.loads(request.form['hungerRatingResults'])
				results_to_csv(expId, subjectId, filePath, 'HungerRating1.csv', hungerRatingResults, {})

				expResults = json.loads(request.form['experimentResults'])
				set_completed_task(expId, workerId, 'completedRatingsTask', True)
				results_to_csv(expId, subjectId, filePath, 'RatingsResults.csv', expResults, {})

				return redirect(url_for('.choicetask_demo_instructions', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))

@scp.route("/choicetask_demo_instructions", methods = ["GET","POST"])
def choicetask_demo_instructions():
	containsAllMTurkArgs = contains_necessary_args(request.args)
	if containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
	if request.method == "GET" and containsAllMTurkArgs:
		return render_template('stimcharproj/choicetask_demo_instructions.html')
	elif containsAllMTurkArgs:
		if 'submit' in request.form.keys() and request.form['submit'] == 'Continue':
			return redirect(url_for('.choicetask', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		elif 'submit' in request.form.keys() and request.form['submit'] == 'Repeat Demo':
			return redirect(url_for('.choicetask', demo=True, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		else:
			return redirect(url_for('.choicetask', demo=True, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))

@scp.route("/choicetask_instructions", methods = ["GET","POST"])
def choicetask_instructions():
	containsAllMTurkArgs = contains_necessary_args(request.args)
	if containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
	if request.method == "GET" and containsAllMTurkArgs:
		return render_template('stimcharproj/choicetask_instructions.html')
	elif containsAllMTurkArgs:
		if 'submit' in request.form.keys() and request.form['submit'] == 'Continue':
			return redirect(url_for('.choicetask', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		elif 'submit' in request.form.keys() and request.form['submit'] == 'Repeat Demo':
			return redirect(url_for('.choicetask', demo=True, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		else:
			return redirect(url_for('.choicetask', demo=False, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))

@scp.route("/choicetask", methods = ["GET","POST"])
def choicetask():
	name = 'choicetask'
	containsAllMTurkArgs = contains_necessary_args(request.args)

	if 'demo' in request.args and containsAllMTurkArgs:
		if request.method == "GET" and request.args.get('demo') == 'True':
			[stim1Names, stim1Bids, stim2Names, stim2Bids] = get_two_stimuli_lists_without_bids(foodStimFolder+'demo/', '', '.bmp')
			expVariables = [] # array of dictionaries

			deltas = []
			for i in range(0,len(stim1Bids)):
				deltas.append(stim2Bids[i] - stim1Bids[i])

			for i in range(0,len(stim1Bids)):
				expVariables.append({"stimulus1":stim1Names[i],"stimulus2":stim2Names[i],"stim1Bid":stim1Bids[i],"stim2Bid":stim2Bids[i], "delta":deltas[i], "fullStim1Name":stim1Names[i]+".bmp", "fullStim2Name":stim2Names[i]+".bmp"})
			return render_template('stimcharproj/choicetask.html', expId=expId, expVariables=expVariables, stimFolder=foodStimFolder+'demo/')
		else:
			[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
			if assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
				return redirect(url_for('accept_hit'))
			return redirect(url_for('.choicetask_instructions', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	elif containsAllMTurkArgs:
		# not demo - record responses now
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
		subjectId = get_subjectId(expId, workerId)

		completedRatingsTask= completed_task(expId, workerId, 'completedRatingsTask')
		completedChoiceTask = completed_task(expId, workerId, 'completedChoiceTask')

		if workerId_exists(expId, workerId):
			if request.method == "GET":
				### set experiment conditions here and pass to experiment.html 
				# trialVariables should be an array of dictionaries 
				# each element of the array represents the condition for one trial
				# set the variable conditions to the array of conditions

				stim1Bids = [];
				stim2Bids = [];

				ratingsResultsFileName = '_RatingsResults.csv'
				stimBidDict = get_bid_responses(dataDir + expId + '/' + subjectId + '/' + subjectId + ratingsResultsFileName)
				[stim1Names, stim1Bids, stim2Names, stim2Bids] = get_two_stimuli_lists(stimBidDict, foodStimFolder, '', '.bmp')
				expVariables = [] # array of dictionaries

				deltas = []
				for i in range(0,len(stim1Bids)):
					deltas.append(stim2Bids[i] - stim1Bids[i])

				for i in range(0,len(stim1Bids)):
					expVariables.append({"stimulus1":stim1Names[i],"stimulus2":stim2Names[i],"stim1Bid":stim1Bids[i],"stim2Bid":stim2Bids[i], "delta":deltas[i], "fullStim1Name":stim1Names[i]+".bmp", "fullStim2Name":stim2Names[i]+".bmp"})

				return render_template('stimcharproj/choicetask.html', expId=expId, expVariables=expVariables, stimFolder=foodStimFolder)
			else:
				expResults = json.loads(request.form['experimentResults'])
				filePath = dataDir + expId + '/' + subjectId + '/'
				results_to_csv(expId, subjectId, filePath, 'ChoiceTaskData.csv', expResults, {})

				set_completed_task(expId, workerId, 'completedChoiceTask', True)

				return redirect(url_for('.demographicq', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))

@scp.route("/demographicq", methods = ["GET", "POST"])
def demographicq():
	info=get_demographicq()
	containsAllMTurkArgs = contains_necessary_args(request.args)
	if containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
	if request.method == "GET" and containsAllMTurkArgs:
		return render_template('stimcharproj/demographicq.html', info=info)
	elif containsAllMTurkArgs: # in request.method == "POST"
		subjectId = get_subjectId(expId, workerId)
		q_and_a = [] # list of dictionaries where questions are keys and answers are values
		nQuestions = len(info) 
		for i in range(0,nQuestions):
			question = request.form['q'+str(i+1)]
			tmp={}
			if 'height' in question:
				answer1 = request.form['a'+str(i+1)+'_1'] + 'ft'
				answer2 = request.form['a'+str(i+1)+'_2'] + 'in'
				answer = answer1 + ' ' + answer2
			elif 'weight' in question:
				answer = request.form['a'+str(i+1)] + 'lbs'
			else: 
				answer = request.form['a'+str(i+1)]
			tmp['question'] = question
			tmp['answer'] = answer
			q_and_a.append(tmp)

		filePath = dataDir + expId + '/' + subjectId + '/'
		set_completed_task(expId, workerId, 'completedDemographicQuestionnaire', True)
		results_to_csv(expId, subjectId, filePath, 'DemographicAnswers.csv', q_and_a, {})
		return redirect(url_for('.TREQr18',expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))


@scp.route("/TREQr18", methods = ["GET", "POST"])
def TREQr18():
	questions, option1, option2, option3, option4=get_TREQr18()
	containsAllMTurkArgs = contains_necessary_args(request.args)
	if containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
	if request.method == "GET" and containsAllMTurkArgs:
		return render_template('stimcharproj/TREQ-r18.html', questions=questions, option1=option1, option2=option2, option3=option3, option4=option4)
	elif containsAllMTurkArgs: # in request.method == "POST"
		subjectId = get_subjectId(expId, workerId)
		q_and_a = [] # list of dictionaries where questions are keys and answers are values
		nQuestions = len(questions) + 1 # there's an additional Q at the end (1-8)
		for i in range(0,nQuestions):
			tmp = {}
			tmp['questionN'] = i+1
			tmp['question'] = request.form['q'+str(i+1)]
			tmp['answer'] = request.form['a'+str(i+1)] # set keys and values in dictionary
			q_and_a.append(tmp)

		filePath = dataDir + expId + '/' + subjectId + '/'
		set_completed_task(expId, workerId, 'completedTREQ-r18', True)
		results_to_csv(expId, subjectId, filePath, 'TREQ-r18.csv', q_and_a, {})
		return redirect(url_for('.EAT26',expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))

@scp.route("/EAT26", methods = ["GET", "POST"])
def EAT26():
	questions, option1, option2, option3, option4, option5, option6 =get_EAT26()
	containsAllMTurkArgs = contains_necessary_args(request.args)
	if containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
	if request.method == "GET" and containsAllMTurkArgs:
		return render_template('stimcharproj/EAT26.html', questions=questions, option1=option1, option2=option2, option3=option3, option4=option4, option5=option5, option6=option6)
	elif containsAllMTurkArgs: # in request.method == "POST"
		subjectId = get_subjectId(expId, workerId)
		q_and_a = [] # list of dictionaries where questions are keys and answers are values
		nQuestions = len(questions) + 1 # there's an additional Q at the end (yes/no)
		for i in range(0,nQuestions):
			tmp = {}
			tmp['questionN'] = i+1
			tmp['question'] = request.form['q'+str(i+1)]
			tmp['answer'] = request.form['a'+str(i+1)] # set keys and values in dictionary
			q_and_a.append(tmp)

		filePath = dataDir + expId + '/' + subjectId + '/'

		hungerRatingResults=json.loads(request.form['hungerRatingResults'])
		results_to_csv(expId, subjectId, filePath, 'HungerRating2.csv', hungerRatingResults, {})

		set_completed_task(expId, workerId, 'completedEAT26', True)
		results_to_csv(expId, subjectId, filePath, 'EAT26.csv', q_and_a, {})
		return redirect(url_for('.debrief',expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))

@scp.route("/debrief", methods = ["GET","POST"])
def debrief():
	containsAllMTurkArgs = contains_necessary_args(request.args)
	if containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
	if request.method == "GET" and containsAllMTurkArgs:
		return render_template('stimcharproj/debrief.html')
	elif containsAllMTurkArgs:
		return redirect(url_for('feedback',expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))
