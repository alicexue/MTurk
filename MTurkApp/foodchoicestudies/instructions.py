from flask import Flask, render_template, request, Blueprint
from flask import redirect, url_for
from flask import jsonify
import json
import random
import csv
import os
import sys
from expInfo import *
from utils import * 
from store_data import *
from manage_subject_info import *
from expInfo import *

_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
_thisDir = os.path.abspath(os.path.join(_thisDir, os.pardir))

instructions = Blueprint('instructions', __name__)

"""
Auction Instructions
"""
@instructions.route("/auction_instructions/<expId>", methods = ["GET","POST"])
def auction_instructions(expId):
	name = 'auction'
	assignmentId = None
	if 'assignmentId' in request.args:
		assignmentId = request.args.get('assignmentId')

	if contains_necessary_args(request.args) or assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

		if workerId_exists(expId, workerId) or assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
			if request.method == "GET":
				stimuli = get_stimuli(foodStimFolder[expId],'','.bmp')
				nStim = len(stimuli)
				return render_template('foodchoicestudies/auction_instructions.html', nStim=nStim)
			else:
				if request.form['submit'] == 'Continue':
					if assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE': # if in preview
						nextTask = get_next_task(name, expTaskOrders[expId])
						return redirect(url_for(nextTask, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
					else:
						return redirect(url_for('tasks.auction', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
				else:
					return redirect(url_for('tasks.auction', demo='TRUE', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))

"""
Auction Demo Instructions
"""
@instructions.route("/auction_demo_instructions/<expId>", methods = ["GET","POST"])
def auction_demo_instructions(expId):
	name = 'auction'
	assignmentId = None

	if 'assignmentId' in request.args:
		assignmentId = request.args.get('assignmentId')

	if contains_necessary_args(request.args) or assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

		if workerId_exists(expId, workerId) or assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
			if request.method == "GET":
				stimuli = get_stimuli(foodStimFolder[expId],'','.bmp')
				nStim = len(stimuli)
				return render_template('foodchoicestudies/auction_demo_instructions.html', nStim = nStim)
			else:
				return redirect(url_for('tasks.auction', demo='TRUE', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))

"""
Auction Repeat Instructions
"""
@instructions.route("/auction_repeat_instructions/<expId>", methods = ["GET","POST"])
def auction_repeat_instructions(expId):
	name = 'auction'
	assignmentId = None
	if 'assignmentId' in request.args:
		assignmentId = request.args.get('assignmentId')
	if contains_necessary_args(request.args) or assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

		if workerId_exists(expId, workerId) or assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
			if request.method == "GET":
				stimuli = get_stimuli(foodStimFolder[expId],'','.bmp')
				nStim = len(stimuli)
				return render_template('foodchoicestudies/auction_repeat_instructions.html', nStim=nStim)
			else:
				return redirect(url_for('tasks.auction', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))

"""
Choice Task Instructions
"""
@instructions.route("/choicetask_instructions/<expId>", methods = ["GET","POST"])
def choicetask_instructions(expId):
	taskEndpoint = 'tasks.choicetask'
	taskHTML = 'foodchoicestudies/choicetask_instructions.html'
	demo = False 
	return route_for_instructions(expId, taskHTML, taskEndpoint, demo, request)

"""
Scene Choice Task Instructions
"""
@instructions.route("/scenechoicetask_instructions/<expId>", methods = ["GET","POST"])
def scenechoicetask_instructions(expId):
	taskEndpoint = 'tasks.scenechoicetask'
	taskHTML = 'foodchoicestudies/scenechoicetask_instructions.html'
	demo = False 
	return route_for_instructions(expId, taskHTML, taskEndpoint, demo, request)

"""
Scene Task Demo Instructions
"""
@instructions.route("/scenetask_demo_instructions/<expId>", methods = ["GET","POST"])
def scenetask_demo_instructions(expId):
	taskEndpoint = 'tasks.scenetask'
	taskHTML = 'foodchoicestudies/scenetask_demo_instructions.html'
	demo = True 
	return route_for_instructions(expId, taskHTML, taskEndpoint, demo, request)

"""
Scene Task Instructions
"""
@instructions.route("/scenetask_instructions/<expId>", methods = ["GET","POST"])
def scenetask_instructions(expId):
	taskEndpoint = 'tasks.scenetask'
	taskHTML = 'foodchoicestudies/scenetask_instructions.html'
	demo = False 
	return route_for_instructions(expId, taskHTML, taskEndpoint, demo, request)

"""
Choice Task Demo Instructions
"""
@instructions.route("/choicetask_demo_instructions/<expId>", methods = ["GET","POST"])
def choicetask_demo_instructions(expId):
	taskEndpoint = 'tasks.choicetask'
	taskHTML = 'foodchoicestudies/choicetask_demo_instructions.html'
	demo = True 
	return route_for_instructions(expId, taskHTML, taskEndpoint, demo, request)

"""
Scene Choice Task Demo Instructions
"""
@instructions.route("/scenechoicetask_demo_instructions/<expId>", methods = ["GET","POST"])
def scenechoicetask_demo_instructions(expId):
	taskEndpoint = 'tasks.scenechoicetask'
	taskHTML = 'foodchoicestudies/scenechoicetask_demo_instructions.html'
	demo = True 
	return route_for_instructions(expId, taskHTML, taskEndpoint, demo, request)

"""
Familiarity Task Instructions
"""
@instructions.route("/familiaritytask_instructions/<expId>", methods = ["GET","POST"])
def familiaritytask_instructions(expId):
	taskEndpoint = 'tasks.familiaritytask'
	taskHTML = 'foodchoicestudies/familiaritytask_instructions.html'
	demo = False
	return route_for_instructions(expId, taskHTML, taskEndpoint, demo, request)

"""
Renders HTML for instructions page or redirects to task based on arguments in request 
Params:
	expId (string): name of experiment
	taskHTML (string): name of HTML file for instructions page
	taskEndpoint (string): name of task route to redirect to
	demo (boolean): true if this instructions page is for a demo of the task
	request (Flask request object): checked to determine what should be returned

"""
def route_for_instructions(expId, taskHTML, taskEndpoint, demo, request):
	assignmentId = None
	if 'assignmentId' in request.args:
		assignmentId = request.args.get('assignmentId')

	if contains_necessary_args(request.args) or assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
		[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
		if workerId_exists(expId, workerId) or assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
			if request.method == "GET":
				return render_template(taskHTML, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live)
			else:
				if 'submit' in request.form.keys() and request.form['submit'] == 'Continue':
					if assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
						return redirect(url_for('accept_hit'))
					else:
						return redirect(url_for(taskEndpoint, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
				elif 'submit' in request.form.keys() and request.form['submit'] == 'Repeat Demo':
					return redirect(url_for(taskEndpoint, demo='TRUE', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
				else:
					if demo:
						demoValue = 'TRUE'
					else:
						demoValue = 'FALSE'
					return redirect(url_for(taskEndpoint, demo=demoValue, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))
