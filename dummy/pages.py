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

pages = Blueprint('pages',  __name__)

"""
Creates homepage for dummy HIT to compensate workers
Checks if workerId in URL is in the csv file dummyHIT_subjects_to_compensate.csv
"""
@pages.route("/dummyHIT", methods = ["GET","POST"])
def dummyHIT():
	_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
	_parentDir = os.path.abspath(os.path.join(_thisDir, os.pardir))
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
		### on server, os.pardir adds / to the end of the path, on local Macbook, no / is added at the end
		if _parentDir[-1] != '/':
			_parentDir += '/'
		subjects_to_compensate = []
		if os.path.exists(_parentDir + 'dummyHIT_subjects_to_compensate.csv'):
			df = pd.read_csv(_parentDir + 'dummyHIT_subjects_to_compensate.csv', encoding="utf-8-sig")
			subjects_to_compensate = df['subjectId'].values
		print subjects_to_compensate
		if len(subjects_to_compensate) > 0 and workerId in subjects_to_compensate: 
			if 'workerId' in request.args and 'turkSubmitTo' in request.args:
				workerId = request.args.get('workerId')
				turkSubmitTo = request.args.get('turkSubmitTo')
				store_subject_info("dummyHIT", workerId, [], assignmentId, hitId, turkSubmitTo) 
				return redirect(url_for('thankyou', assignmentId=assignmentId, live=live))
			else:
				return redirect(url_for('accept_hit'))
		else:
			return redirect(url_for('pages.return_dummyHIT', preview='True', assignmentId=assignmentId, hitId=hitId))
	else:
		return redirect(url_for('unauthorized_error'))

@pages.route("/return_dummyHIT", methods = ["GET"])
def return_dummyHIT():
	return render_template('return_dummy_hit.html')