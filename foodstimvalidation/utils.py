import os
import sys
import csv
import random
import pandas as pd
import numpy as np

_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
_parentDir = os.path.abspath(os.path.join(_thisDir, os.pardir))
dataDir = _parentDir + '/data/'

"""
Returns a list of all stimuli in the stim folder (assuming all the .bmp files are stimulus images)
"""
def get_stimuli(folder, prepend, fileextension):
	'''
	get array of stimuli from the directory name stim
	'''
	stimuli = []
	for stimulusFile in os.listdir(_parentDir + folder):
		if stimulusFile.endswith(fileextension): 
			stimuli.append(prepend + stimulusFile[:-4])
	return stimuli

"""
Creates list of dictionaries where each dictionary holds the variables for one trial
"""
def get_ratingtask_expVariables(expId, subjectId, demo):
	if demo == True:
		stimuli = get_stimuli('/static/foodstim80/demo/','','.bmp')
	else:
		stimuli = get_stimuli('/static/foodstim80/','','.bmp')
	random.shuffle(stimuli)

	expVariables = [] # array of dictionaries

	for i in range(0,len(stimuli)):
		question='question ' + str(i)
		leftRatingText='lowest ' + str(i)
		rightRatingText='highest ' + str(i)
		rs_min=0
		rs_max=10
		rs_tickIncrement=1
		rs_increment=0.01
		rs_labelNames=["0", "", "", "", "", "5", "", "", "", "", "10"]
		expVariables.append({'stimulus':stimuli[i], 'fullStimName':stimuli[i]+'.bmp', 'question':question, 'leftRatingText':leftRatingText, 'rightRatingText':rightRatingText, 'rs_min':rs_min, 'rs_max':rs_max, 'rs_tickIncrement':rs_tickIncrement, 'rs_increment':rs_increment, 'rs_labelNames':rs_labelNames})
	return expVariables

def get_questions():
	questions = pd.read_csv(_thisDir + '/QuestionnaireQuestions.csv')
	questions=questions['Question']
	"""
	questions = ['I plan tasks carefully.',
			'I do things without thinking.',
			'I make-up my mind quickly.',
			'I am happy-go-lucky.',
			'I don\'t \"pay attention\".',
			'I have \"racing\" thoughts.',
			'I plan trips well ahead of time.',
			'I am self controlled.',
			'I concentrate easily.',
			'I save regularly.',
			'I \"squirm\" at plays or lectures.',
			'I am a careful thinker.',
			'I plan for job security.',
			'I say things without thinking.',
			'I like to think about complex problems.',
			'I change jobs.',
			'I act \"on impulse.\"',
			'I get easily bored when solving thought problems.',
			'I act on the spur of the moment.',
			'I am a steady thinker.',
			'I change residences.',
			'I buy things on impulse.',
			'I can only think about one thing at a time.',
			'I change hobbies.',
			'I spend or charge more than I earn.',
			'I often have extraneous thoughts when thinking.',
			'I am more interested in the present than the future.',
			'I am restless at the theater or lectures.',
			'I like puzzles.',
			'I am future oriented.',
			]
	"""
	return questions

"""
Checks request.args has assignmentId, hitId, turkSubmitTo, workerId, live - all but live is passed by MTurk
live refers to whether HIT is live or in sandbox
"""
def contains_necessary_args(args):
	if 'workerId' in args and 'assignmentId' in args and 'hitId' in args and 'turkSubmitTo' in args and 'live' in args:
		return True
	else:
		return False

"""
Retrieve necessary args: assignmentId, hitId, turkSubmitTo, workerId, live
"""
def get_necessary_args(args):
	workerId = args.get('workerId')
	assignmentId = args.get('assignmentId')
	hitId = args.get('hitId')
	turkSubmitTo = args.get('turkSubmitTo')
	live = args.get('live') == "True"
	return [workerId, assignmentId, hitId, turkSubmitTo, live]