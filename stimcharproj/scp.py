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

subsetExpIds=["SCP-12","SCP-13","SCP-14","SCP-15","SCP-16","SCP-23","SCP-24","SCP-25","SCP-26","SCP-34","SCP-35","SCP-36","SCP-45","SCP-46","SCP-56"]

refItemDict={"SCP-12":"Pretzels", "SCP-13":"Pretzels", "SCP-14":"baked potato", "SCP-15":"saltines", "SCP-16":"Pretzels", "SCP-23":"air popcorn", "SCP-24":"baked potato", "SCP-25":"saltines", "SCP-26":"ritz", "SCP-34":"baked potato", "SCP-35":"saltines", "SCP-36":"ritz", "SCP-45":"saltines", "SCP-46":"baked potato", "SCP-56":"saltines"}

scp = Blueprint('scp',  __name__, url_prefix='/SCP/<expId>')

_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
_parentDir = os.path.abspath(os.path.join(_thisDir, os.pardir))
dataDir = _parentDir + '/data/'

expTasksToComplete={'completedRatingsTask':False,'completedChoiceTask':False,'completedTFEQr18':False,'completedEAT26':False,'completedDemographicQuestionnaire':False}

@scp.route("/", methods = ["GET","POST"])
@scp.route("/consent_form", methods = ["GET","POST"])
def consent_form(expId):
	if expId in subsetExpIds:
		if request.method == "GET":
			#if 'preview' in request.args and request.args.get('preview') == 'True':
			return render_template('stimcharproj/consent_form.html')
		else:
			if contains_necessary_args(request.args): 
				# worker accepted HIT 
				[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
				participatedInPreviousOrSameHIT=False
				for exp in subsetExpIds:
					if workerId_exists(exp, workerId) and completed_task(exp, workerId, 'completedTFEQr18'):
						participatedInPreviousOrSameHIT=True
				if participatedInPreviousOrSameHIT:
					return render_template('return_hit.html')
				elif not workerId_exists(expId, workerId):
					store_subject_info(expId, workerId, expTasksToComplete, assignmentId, hitId, turkSubmitTo) 
				"""
				if request.args.get('assignmentId') == 'ASSIGNMENT_ID_NOT_AVAILABLE':
					return redirect(url_for('.ratingtask_demo_instructions', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
				else:
					return redirect(url_for('.ratehunger', num=1, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
				"""
			elif 'assignmentId' in request.args and request.args.get('assignmentId') == 'ASSIGNMENT_ID_NOT_AVAILABLE':
				# worker previewing HIT
				workerId = 'testWorker' + str(random.randint(1000, 10000))
				assignmentId = request.args.get('assignmentId')
				hitId = 'testHIT' + str(random.randint(10000, 100000))
				turkSubmitTo = 'www.calkins.psych.columbia.edu'
				live = request.args.get('live') == "True"
				#return redirect(url_for('.ratingtask_demo_instructions', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
			else:
				# in testing - accessed site through www.calkins.psych.columbia.edu
				workerId = 'testWorker' + str(random.randint(1000, 10000))
				assignmentId = 'testAssignment' + str(random.randint(10000, 100000))
				hitId = 'testHIT' + str(random.randint(10000, 100000))
				turkSubmitTo = 'www.calkins.psych.columbia.edu'
				live = False
				store_subject_info(expId, workerId, expTasksToComplete, assignmentId, hitId, turkSubmitTo) 
				#return redirect(url_for('.ratehunger', num=1, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
			return redirect(url_for('.intro', num=1, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))

@scp.route("/intro", methods = ["GET","POST"])
def intro(expId):
	containsAllMTurkArgs = contains_necessary_args(request.args)
	if containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
	if request.method == "GET" and containsAllMTurkArgs:
		return render_template('stimcharproj/intro.html')
	elif containsAllMTurkArgs:
		if request.args.get('assignmentId') == 'ASSIGNMENT_ID_NOT_AVAILABLE':
			return redirect(url_for('.ratingtask_demo_instructions', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		else:
			return redirect(url_for('.ratehunger',num=1,expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))

@scp.route("/ratehunger/<num>", methods = ["GET","POST"])
def ratehunger(expId,num):
	containsAllMTurkArgs = contains_necessary_args(request.args)
	if containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
	if request.method == "GET" and containsAllMTurkArgs:
		return render_template('stimcharproj/ratehunger.html')
	elif containsAllMTurkArgs:
		subjectId = get_subjectId(expId, workerId)
		filePath = dataDir + expId + '/' + subjectId + '/'
		hungerRatingResults=json.loads(request.form['hungerRatingResults'])
		results_to_csv(expId, subjectId, filePath, 'HungerRating' + str(num) + '.csv', hungerRatingResults, {})
		if num == str(1):
			return redirect(url_for('.ratingtask_demo_instructions', demo=True,expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		else:
			return redirect(url_for('.TFEQr18', demo=True,expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))

@scp.route("/ratingtask_demo_instructions", methods = ["GET","POST"])
def ratingtask_demo_instructions(expId):
	foodStimFolder='/static/stimcharproj/'+expId+'/'
	containsAllMTurkArgs = contains_necessary_args(request.args)
	if containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
	if request.method == "GET" and containsAllMTurkArgs:
		foodStimFolder = foodStimFolder + 'demo/'
		demo_stimuli = get_stimuli(foodStimFolder,'','.jpg')
		refItem=foodStimFolder+demo_stimuli[0]+'.jpg'
		return render_template('stimcharproj/ratingtask_demo_instructions.html', refItem=refItem)
	elif containsAllMTurkArgs:
		return redirect(url_for('.ratingtask', demo=True,expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))

@scp.route("/ratingtask_instructions", methods = ["GET","POST"])
def ratingtask_instructions(expId):
	foodStimFolder='/static/stimcharproj/'+expId+'/'
	containsAllMTurkArgs = contains_necessary_args(request.args)
	if containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
	if request.method == "GET" and containsAllMTurkArgs:
		demo_stimuli = get_stimuli(foodStimFolder + 'demo/','','.jpg')
		refItem=foodStimFolder+'demo/'+demo_stimuli[0]+'.jpg'
		return render_template('stimcharproj/ratingtask_instructions.html', refItem=refItem)
	elif containsAllMTurkArgs:
		return redirect(url_for('.ratingtask',expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))

@scp.route("/ratingtask", methods = ["GET","POST"])
def ratingtask(expId):
	foodStimFolder='/static/stimcharproj/'+expId+'/'
	oneLineInstructions = "Rate how much you want to eat this food from 0 (least) to 10 (most)."
	containsAllMTurkArgs = contains_necessary_args(request.args)

	if 'demo' in request.args and containsAllMTurkArgs:
		if request.method == "GET" and request.args.get('demo') == 'True':
			expVariables = get_ratingtask_expVariables(stimFolder=foodStimFolder+'demo/',demo=True)
			expVariables=expVariables[:6] # only first 2 questions - 3 stim per q
			return render_template('stimcharproj/ratingtask.html', demo='True',expVariables=expVariables, stimFolder=foodStimFolder+'demo/')
		else:
			[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
			if assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
				return redirect(url_for('accept_hit'))
			return redirect(url_for('.ratingtask_instructions', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	elif containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

		if workerId_exists(expId, workerId):
			if request.method == "GET":
				### set experiment conditions here and pass to experiment.html 
				# trialVariables should be an array of dictionaries 
				# each element of the array represents the condition for one trial
				# set the variable conditions to the array of conditions
				expVariables = get_ratingtask_expVariables(stimFolder=foodStimFolder,demo=False)

				return render_template('stimcharproj/ratingtask.html', demo='False', expVariables=expVariables, stimFolder=foodStimFolder)
			else:
				subjectId = get_subjectId(expId, workerId)
				filePath = dataDir + expId + '/' + subjectId + '/'

				expResults = json.loads(request.form['experimentResults'])
				set_completed_task(expId, workerId, 'completedRatingsTask', True)
				results_to_csv(expId, subjectId, filePath, 'RatingsResults.csv', expResults, {})

				return redirect(url_for('.choicetask_demo_instructions', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))

@scp.route("/choicetask_demo_instructions", methods = ["GET","POST"])
def choicetask_demo_instructions(expId):
	foodStimFolder='/static/stimcharproj/'+expId+'/'
	containsAllMTurkArgs = contains_necessary_args(request.args)
	if containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
	if request.method == "GET" and containsAllMTurkArgs:
		foodStimFolder = foodStimFolder + 'demo/'
		stimuli = get_stimuli(foodStimFolder,'','.jpg')
		refItem=stimuli[0]
		refItem=foodStimFolder+refItem+'.jpg'
		return render_template('stimcharproj/choicetask_demo_instructions.html', refItem=refItem)
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
def choicetask_instructions(expId):
	foodStimFolder='/static/stimcharproj/'+expId+'/'
	containsAllMTurkArgs = contains_necessary_args(request.args)
	if containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
	if request.method == "GET" and containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
		subjectId = get_subjectId(expId, workerId)
		defaultRefItem=refItemDict[expId]
		refItem = get_reference_item(expId,subjectId,defaultRefItem)
		stimuli = get_stimuli(foodStimFolder,'','.jpg')
		stimuli.remove(refItem)
		random.shuffle(stimuli)
		secondItem = stimuli[0]
		refItem=foodStimFolder+refItem+'.jpg'
		secondItem=foodStimFolder+secondItem+'.jpg'
		return render_template('stimcharproj/choicetask_instructions.html', refItem=refItem)
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
def choicetask(expId):
	foodStimFolder='/static/stimcharproj/'+expId+'/'
	name = 'choicetask'
	containsAllMTurkArgs = contains_necessary_args(request.args)

	if 'demo' in request.args and containsAllMTurkArgs:
		if request.method == "GET" and request.args.get('demo') == 'True':
			expVariables = get_choicetask_expVariables(expId, '', foodStimFolder+'demo/', defaultRefItem=refItemDict[expId],demo=True)
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

				expVariables = get_choicetask_expVariables(expId, subjectId, foodStimFolder, defaultRefItem=refItemDict[expId], demo=False)
				return render_template('stimcharproj/choicetask.html', expId=expId, expVariables=expVariables, stimFolder=foodStimFolder)
			else:
				expResults = json.loads(request.form['experimentResults'])
				filePath = dataDir + expId + '/' + subjectId + '/'
				results_to_csv(expId, subjectId, filePath, 'ChoiceTaskData.csv', expResults, {})

				set_completed_task(expId, workerId, 'completedChoiceTask', True)

				return redirect(url_for('.ratehunger', num=2, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))


@scp.route("/TFEQr18", methods = ["GET", "POST"])
def TFEQr18(expId):
	questions, option1, option2, option3, option4=get_TFEQr18()
	containsAllMTurkArgs = contains_necessary_args(request.args)
	if containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
	if request.method == "GET" and containsAllMTurkArgs:
		return render_template('stimcharproj/TFEQr18.html', questions=questions, option1=option1, option2=option2, option3=option3, option4=option4)
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
		set_completed_task(expId, workerId, 'completedTFEQr18', True)
		results_to_csv(expId, subjectId, filePath, 'TFEQr18.csv', q_and_a, {})
		return redirect(url_for('.EAT26',expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))

@scp.route("/EAT26", methods = ["GET", "POST"])
def EAT26(expId):
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

		set_completed_task(expId, workerId, 'completedEAT26', True)
		results_to_csv(expId, subjectId, filePath, 'EAT26.csv', q_and_a, {})
		return redirect(url_for('.demographicq',expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))

@scp.route("/demographicq", methods = ["GET", "POST"])
def demographicq(expId):
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
		return redirect(url_for('.debrief',expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))

@scp.route("/debrief", methods = ["GET","POST"])
def debrief(expId):
	containsAllMTurkArgs = contains_necessary_args(request.args)
	if containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
	if request.method == "GET" and containsAllMTurkArgs:
		return render_template('stimcharproj/debrief.html')
	elif containsAllMTurkArgs:
		return redirect(url_for('.resources',expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))

@scp.route("/resources", methods = ["GET","POST"])
def resources(expId):
	containsAllMTurkArgs = contains_necessary_args(request.args)
	if containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
	if request.method == "GET" and containsAllMTurkArgs:
		return render_template('stimcharproj/resources.html')
	elif containsAllMTurkArgs:
		return redirect(url_for('feedback',expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))
