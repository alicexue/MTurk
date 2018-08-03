from flask import Flask, render_template, request, Blueprint
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
from expInfo import *

homepages = Blueprint('homepages',  __name__)

"""
Consent Form (home page)
"""
@homepages.route("/MDMRTST", methods = ["GET","POST"], endpoint="MDMRTST")
@homepages.route("/MDMRTST/consentform", methods = ["GET","POST"], endpoint="MDMRTST")
@homepages.route("/MDMRTS", methods = ["GET","POST"], endpoint="MDMRTS")
@homepages.route("/MDMMT", methods = ["GET","POST"], endpoint="MDMMT")
@homepages.route("/MDMRTS/consentform", methods = ["GET","POST"], endpoint="MDMRTS")
@homepages.route("/MDMMT/consentform", methods = ["GET","POST"], endpoint="MDMMT")
def foodchoicestudies():
	validExpId=False
	if request.path.startswith("/MDMMT"):
		expId = "MDMMT"
		consentFormPath=expId
		validExpId=True
	elif request.path.startswith("/MDMRTST"):
		expId = "MDMRTST"
		consentFormPath="MDMRTS"
		validExpId=True
	elif request.path.startswith("/MDMRTS"):
		expId = "MDMRTS"
		consentFormPath=expId
		validExpId=True
	if validExpId:
		if request.method == "GET":
			if 'preview' in request.args and request.args.get('preview') == 'True':
				return render_template('foodchoicestudies/' + consentFormPath + '_consent_form.html')
			elif 'assignmentId' in request.args and 'hitId' in request.args and request.args.get('assignmentId') == 'ASSIGNMENT_ID_NOT_AVAILABLE':
				assignmentId = request.args.get('assignmentId')
				hitId = request.args.get('hitId')
				return redirect(url_for('tasks.check_eligibility', expId=expId, assignmentId=assignmentId, hitId=hitId))
			else:
				return render_template('foodchoicestudies/' + consentFormPath + '_consent_form.html')
		else:
			if contains_necessary_args(request.args): 
				# worker accepted HIT 
				[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
				participatedInMDMMT = workerId_exists('MDMMT', workerId)
				participatedInMDMRTS = workerId_exists('MDMRTS', workerId)
				participatedInMDMRTST = workerId_exists('MDMRTST', workerId)
				if participatedInMDMMT or participatedInMDMRTS or participatedInMDMRTST:
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
			if 'instructions' in firstTask:
				firstTask = 'instructions.' + firstTask
			else:
				firstTask = 'tasks.' + firstTask
			return redirect(url_for(firstTask, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
	else:
		return render_template('404.html'), 404