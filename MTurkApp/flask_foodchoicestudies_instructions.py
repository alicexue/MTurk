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
from flask_foodchoicestudies import *

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
				stimuli = get_stimuli(foodStimFolder[expId],'','.bmp')
				nStim = len(stimuli)
				return render_template('auction_instructions.html', nStim=nStim)
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
				stimuli = get_stimuli(foodStimFolder[expId],'','.bmp')
				nStim = len(stimuli)
				return render_template('auction_demo_instructions.html', nStim = nStim)
			else:
				return redirect(url_for('auction', demo='TRUE', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
		else:
			return redirect(url_for('unauthorized_error'))
	else:
		return redirect(url_for('unauthorized_error'))

"""
Auction Repeat Instructions
"""
@app.route("/auction_repeat_instructions/<expId>", methods = ["GET","POST"])
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
				return render_template('auction_repeat_instructions.html', nStim=nStim)
			else:
				return redirect(url_for('auction', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
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
	taskHTML = 'choicetask_instructions.html'
	demo = False 
	return route_for_instructions(expId, taskHTML, name, demo, request)

"""
Scene Choice Task Instructions
"""
@app.route("/scenechoicetask_instructions/<expId>", methods = ["GET","POST"])
def scenechoicetask_instructions(expId):
	name = 'scenechoicetask'
	taskHTML = 'scenechoicetask_instructions.html'
	demo = False 
	return route_for_instructions(expId, taskHTML, name, demo, request)

"""
Scene Task Demo Instructions
"""
@app.route("/scenetask_demo_instructions/<expId>", methods = ["GET","POST"])
def scenetask_demo_instructions(expId):
	name = 'scenetask'
	taskHTML = 'scenetask_demo_instructions.html'
	demo = True 
	return route_for_instructions(expId, taskHTML, name, demo, request)

"""
Scene Task Instructions
"""
@app.route("/scenetask_instructions/<expId>", methods = ["GET","POST"])
def scenetask_instructions(expId):
	name = 'scenetask'
	taskHTML = 'scenetask_instructions.html'
	demo = False 
	return route_for_instructions(expId, taskHTML, name, demo, request)

"""
Choice Task Demo Instructions
"""
@app.route("/choicetask_demo_instructions/<expId>", methods = ["GET","POST"])
def choicetask_demo_instructions(expId):
	name = 'choicetask'
	taskHTML = 'choicetask_demo_instructions.html'
	demo = True 
	return route_for_instructions(expId, taskHTML, name, demo, request)

"""
Scene Choice Task Demo Instructions
"""
@app.route("/scenechoicetask_demo_instructions/<expId>", methods = ["GET","POST"])
def scenechoicetask_demo_instructions(expId):
	name = 'scenechoicetask'
	taskHTML = 'scenechoicetask_demo_instructions.html'
	demo = True 
	return route_for_instructions(expId, taskHTML, name, demo, request)

"""
Familiarity Task Instructions
"""
@app.route("/familiaritytask_instructions/<expId>", methods = ["GET","POST"])
def familiaritytask_instructions(expId):
	name = 'familiaritytask'
	taskHTML = 'familiaritytask_instructions.html'
	demo = False
	return route_for_instructions(expId, taskHTML, name, demo, request)

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
