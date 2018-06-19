import os
import sys
import csv
import random
import pandas as pd
import numpy as np

_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())

def get_trivia():
	questions = pd.read_csv(_thisDir + "/Kanga_TriviaList1.csv", usecols=['QuestionNum', 'Question', 'AnswerUse'])
	questions.columns = ['QuestionNum','Question','Answer']
	questions = questions.to_dict('records')
	random.shuffle(questions)
	return questions

def get_practice_trivia():
	questions = pd.read_csv(_thisDir + "/Kanga_PracticeQs.csv")
	questions.columns = ['QuestionNum','Question','Answer']
	questions=questions[0:3]
	questions = questions.to_dict('records')
	random.shuffle(questions)
	return questions

def get_jitter():
	#jitter = [random.uniform(0.5, 2) for i in xrange(300)]
	jitter = [random.uniform(0.5, 2) for i in xrange(400)]
	return jitter

def get_wait():
	w = np.array([4, 8, 12, 16])
	wait = np.repeat(w, 200)
	random.shuffle(wait)
	return wait

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
