from flask import Flask, render_template, request, session, Blueprint
from flask import redirect, url_for
from flask import jsonify
import json
import random
import csv
import os
import sys
import pandas as pd
import datetime
from utils import * 
from store_data import *
from manage_subject_info import *

expId='Kanga'

curiosity_tasks = Blueprint('curiosity_tasks',  __name__, url_prefix='/Kanga')

_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
_parentDir = os.path.abspath(os.path.join(_thisDir, os.pardir))
dataDir = _parentDir + '/data/'

expTasksToComplete={'completedKangaTask':False}

@curiosity_tasks.route("", methods = ["GET","POST"])
@curiosity_tasks.route("/consent_form", methods = ["GET","POST"])
def consent_form():
	if request.method == "GET":
		#if 'preview' in request.args and request.args.get('preview') == 'True':
		return render_template('kangacuriositytask/consent_form.html')
	else:
		if contains_necessary_args(request.args): 
			# worker accepted HIT 
			[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
			if workerId_exists(expId, workerId) and (completed_task(expId, workerId, 'completedKangaTask')):
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
		return redirect(url_for('.full_instructions', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))

@curiosity_tasks.route("/full_instructions", methods = ["GET","POST"])
def full_instructions():
	containsAllMTurkArgs = contains_necessary_args(request.args)
	if containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
	if request.method == "GET" and containsAllMTurkArgs:
		return render_template('kangacuriositytask/full_instructions.html')
	elif containsAllMTurkArgs:
		return redirect(url_for('.kanga_task',demo='True', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))

@curiosity_tasks.route("/main_task_instructions", methods = ["GET","POST"])
def main_task_instructions():
	containsAllMTurkArgs = contains_necessary_args(request.args)
	if containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
	if request.method == "GET" and containsAllMTurkArgs:
		return render_template('kangacuriositytask/main_task_instructions.html')
	elif containsAllMTurkArgs:
		return redirect(url_for('.kanga_task',expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))

@curiosity_tasks.route("/task", methods = ["GET","POST"])
def kanga_task():
	containsAllMTurkArgs = contains_necessary_args(request.args)
	if containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
	if request.method == "GET" and containsAllMTurkArgs:
		stimuli = get_trivia()
		if 'demo' in request.args and request.args.get('demo') == 'True':
			stimuli=get_practice_trivia()
		jitters = get_jitter()
		waits = get_wait()
		for i in range(0,len(stimuli)):
			trial = stimuli[i]
			trial['C_Wait'] = waits[i]
			trial['jitter'] = jitters[i]
		return render_template('kangacuriositytask/kanga.html', expVariables = stimuli)
	elif containsAllMTurkArgs: # request.method == "POST"
		if 'demo' in request.args and request.args.get('demo') == 'True':
			[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
			if assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
				return redirect(url_for('accept_hit'))
			return redirect(url_for('.main_task_instructions', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		else:
			subjectId = get_subjectId(expId, workerId)
			expResults = json.loads(request.form['experimentResults'])
			filePath = dataDir + expId + '/' + subjectId + '/'
			set_completed_task(expId, workerId, 'completedKangaTask', True)
			results_to_csv(expId, subjectId, filePath, 'CuriosityTaskResults.csv', expResults, {})
			return redirect(url_for('.rating_task',expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))

@curiosity_tasks.route("/rating_task", methods = ["GET","POST"])
def rating_task():
	containsAllMTurkArgs = contains_necessary_args(request.args)

	if 'demo' in request.args and containsAllMTurkArgs:
		if request.method == "GET" and request.args.get('demo') == 'True':
			subjectId = get_subjectId(expId, workerId)
			expVariables = get_ratingtask_expVariables(subjectId)
			return render_template('kangacuriositytask/rating_task.html', demo='True',expVariables=expVariables)
		else:
			[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
			if assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
				return redirect(url_for('accept_hit'))
			return redirect(url_for('.ratingtask_instructions', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	elif containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

		if workerId_exists(expId, workerId):
			if request.method == "GET":
				subjectId = get_subjectId(expId, workerId)
				expVariables = get_ratingtask_expVariables(subjectId)

				return render_template('kangacuriositytask/rating_task.html', demo='False', expVariables=expVariables)
			else:
				subjectId = get_subjectId(expId, workerId)
				filePath = dataDir + expId + '/' + subjectId + '/'

				set_completed_task(expId, workerId, 'completedRatingsTask', True)

				expResults = json.loads(request.form['experimentResults'])

				correctFormat = True
				condensedExpResults = []
				for i in range(0,len(expResults)):
					if i%2 == 0: # question
						trial = {}
						trial['trialN']=i/2
						trial['QuestionNum']=expResults[i]['QuestionNum']
						trial['Question']=expResults[i]['Question']
						trial['Answer']=expResults[i]['Answer']
						trial['QuestionRating']=expResults[i]['rating']
					else: # answer
						if trial['Answer'] == expResults[i]['Answer']:
							trial['AnswerRating']=expResults[i]['rating']
							condensedExpResults.append(trial)
						else:
							correctFormat = False 
				if correctFormat:
					results_to_csv(expId, subjectId, filePath, 'RatingsResults.csv', condensedExpResults, {})
				else: # raw results
					results_to_csv(expId, subjectId, filePath, 'RawRatingsResults.csv', expResults, {})

				return redirect(url_for('curiosity_tasks.demographicq', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))


@curiosity_tasks.route("/demographicq", methods = ["GET", "POST"])
def demographicq():
	info=get_demographicq()
	instructions='Please answer each question as accurately as possible.'
	containsAllMTurkArgs = contains_necessary_args(request.args)
	if containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
	if request.method == "GET" and containsAllMTurkArgs:
		options=info[-1][info[-1].keys()[0]]
		widthPercent=10
		return render_template('kangacuriositytask/demographicq.html', info=info, instructions=instructions, widthPercent=widthPercent)
	elif containsAllMTurkArgs: # in request.method == "POST"
		subjectId = get_subjectId(expId, workerId)
		q_and_a = [] # list of dictionaries where questions are keys and answers are values
		nQuestions = len(info) 
		for i in range(0,nQuestions):
			tmp = {}
			tmp['questionN'] = i+1
			tmp['question'] = request.form['q'+str(i+1)]
			tmp['answer'] = request.form['a'+str(i+1)] # set keys and values in dictionary
			q_and_a.append(tmp)

		filePath = dataDir + expId + '/' + subjectId + '/'

		set_completed_task(expId, workerId, 'completedQuestionnaire', True)
		results_to_csv(expId, subjectId, filePath, 'DemographicQuestionnaire.csv', q_and_a, {})

		return redirect(url_for('curiosity_tasks.questionnaire', n=1, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))


@curiosity_tasks.route("/questionnaire/<n>", methods = ["GET", "POST"])
def questionnaire(n):
	n = int(n)
	if n in questionnaire_dict.keys():
		info=get_questionnaire(n)
		instructions=get_questionnaire_instructions(n)
		containsAllMTurkArgs = contains_necessary_args(request.args)
		if containsAllMTurkArgs:
			[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
		if request.method == "GET" and containsAllMTurkArgs:
			options=info[0][info[0].keys()[0]]
			widthPercent=70.0/len(options)
			return render_template('kangacuriositytask/questionnaire.html', info=info, instructions=instructions, widthPercent=widthPercent)
		elif containsAllMTurkArgs: # in request.method == "POST"
			subjectId = get_subjectId(expId, workerId)
			q_and_a = [] # list of dictionaries where questions are keys and answers are values
			nQuestions = len(info) 
			for i in range(0,nQuestions):
				tmp = {}
				tmp['questionN'] = i+1
				tmp['question'] = request.form['q'+str(i+1)]
				tmp['answer'] = request.form['a'+str(i+1)] # set keys and values in dictionary
				q_and_a.append(tmp)

			filePath = dataDir + expId + '/' + subjectId + '/'

			set_completed_task(expId, workerId, 'completedQuestionnaire', True)
			results_to_csv(expId, subjectId, filePath, questionnaire_dict[n]+'.csv', q_and_a, {})

			if n < len(questionnaire_dict.keys()):
				return redirect(url_for('curiosity_tasks.questionnaire', n=n+1, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
			else:
				return redirect(url_for('thankyou',expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		else:
			return redirect(url_for('unauthorized_error'))
	return redirect(url_for('page_not_found'))

@curiosity_tasks.route("/memory_test", methods = ["GET","POST"])
def memory_test():
	containsAllMTurkArgs = contains_necessary_args(request.args)
	if containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
	if request.method == "GET" and containsAllMTurkArgs:

		subjectId = get_subjectId(expId, workerId)
		kangaresults = os.path.join(dataDir,'Kanga',subjectId,subjectId+'_CuriosityTaskResults.csv')
		ratingresults = os.path.join(dataDir,'Kanga',subjectId,subjectId+'_RatingsResults.csv')
		questions = []
		if os.path.exists(kangaresults) and os.path.exists(ratingresults):
			df1 = pd.read_csv(kangaresults)
			df2 = pd.read_csv(ratingresults)
			questions += df1.loc[df1['C_SWK']=='W']['Question'].values.tolist()
			questions += df2['Question'].values.tolist()
		random.shuffle(questions)
		expVariables = []
		for q in questions:
			expVariables.append({'Question':q})
		expVariables
		return render_template('kangacuriositytask/memory_test.html', expVariables = expVariables)
	elif containsAllMTurkArgs: # request.method == "POST"
		if 'demo' in request.args and request.args.get('demo') == 'True':
			[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
			if assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
				return redirect(url_for('accept_hit'))
			return redirect(url_for('thankyou', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		else:
			subjectId = get_subjectId(expId, workerId)
			expResults = json.loads(request.form['experimentResults'])
			print expResults
			filePath = dataDir + expId + '/' + subjectId + '/'
			set_completed_task(expId, workerId, 'completedMemoryTask', True)
			results_to_csv(expId, subjectId, filePath, 'MemoryTestResults.csv', expResults, {})
			return redirect(url_for('thankyou',expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))
