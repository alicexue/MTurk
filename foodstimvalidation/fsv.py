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

expId='FSV'

fsv = Blueprint('fsv',  __name__, url_prefix='/FSV')

_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
_parentDir = os.path.abspath(os.path.join(_thisDir, os.pardir))
dataDir = _parentDir + '/data/'

expTasksToComplete={'completedRatingsTask':False,'completedSurvey':False}

@fsv.route("", methods = ["GET","POST"])
@fsv.route("/consent_form", methods = ["GET","POST"])
def consent_form():
	if request.method == "GET":
		#if 'preview' in request.args and request.args.get('preview') == 'True':
		return render_template('foodstimvalidation/consent_form.html')
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

@fsv.route("/ratingtask_demo_instructions", methods = ["GET","POST"])
def ratingtask_demo_instructions():
	containsAllMTurkArgs = contains_necessary_args(request.args)
	if containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
	if request.method == "GET" and containsAllMTurkArgs:
		return render_template('foodstimvalidation/ratingtask_demo_instructions.html')
	elif containsAllMTurkArgs:
		return redirect(url_for('.ratingtask',demo='True',expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))

@fsv.route("/ratingtask_instructions", methods = ["GET","POST"])
def ratingtask_instructions():
	containsAllMTurkArgs = contains_necessary_args(request.args)
	if containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
	if request.method == "GET" and containsAllMTurkArgs:
		return render_template('foodstimvalidation/ratingtask_instructions.html')
	elif containsAllMTurkArgs:
		return redirect(url_for('.ratingtask',expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))

@fsv.route("/ratingtask", methods = ["GET","POST"])
def ratingtask():
	oneLineInstructions = "Rate how much you want to eat this food from 0 (least) to 10 (most)."
	containsAllMTurkArgs = contains_necessary_args(request.args)

	if 'demo' in request.args and containsAllMTurkArgs:
		if request.method == "GET" and request.args.get('demo') == 'True':
			expVariables = get_ratingtask_expVariables(expId, subjectId=None, demo=True)
			return render_template('foodstimvalidation/ratingtask.html', expVariables=expVariables, stimFolder='/static/foodstim80/demo/')
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
				expVariables = get_ratingtask_expVariables(expId, subjectId=None, demo=False)

				return render_template('foodstimvalidation/ratingtask.html', expVariables=expVariables, stimFolder='/static/foodstim80/')
			else:
				subjectId = get_subjectId(expId, workerId)
				expResults = json.loads(request.form['experimentResults'])
				filePath = dataDir + expId + '/' + subjectId + '/'
				results_to_csv(expId, subjectId, filePath, 'results.csv', expResults, {})

				return redirect(url_for('.questionnaire', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))

@fsv.route("/questionnaire", methods = ["GET", "POST"])
def questionnaire():
	questions = get_questions()
	containsAllMTurkArgs = contains_necessary_args(request.args)
	if containsAllMTurkArgs:
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
	if request.method == "GET" and containsAllMTurkArgs:
		return render_template('foodstimvalidation/questionnaire.html', questions=questions)
	elif containsAllMTurkArgs: # in request.method == "POST"
		subjectId = get_subjectId(expId, workerId)
		
		q_and_a = [] # list of dictionaries where questions are keys and answers are values
		for i in range(0,len(questions)):
			tmp = {}
			tmp['question'] = questions[i]
			tmp['answer'] = request.form['a'+str(i+1)] # set keys and values in dictionary
			q_and_a.append(tmp)

		filePath = dataDir + expId + '/' + subjectId + '/'
		results_to_csv(expId, subjectId, filePath, 'questionnaireResults.csv', q_and_a, {})
		return redirect(url_for('thankyou',expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return redirect(url_for('unauthorized_error'))
