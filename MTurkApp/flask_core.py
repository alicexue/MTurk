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

_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)

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
