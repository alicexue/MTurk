import os
import sys
import csv
import random
import pandas as pd
import numpy as np

_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
_parentDir = os.path.abspath(os.path.join(_thisDir, os.pardir))
dataDir = _parentDir + '/data/'

def get_trivia():
	questions = pd.read_csv(_thisDir + "/Kanga_TriviaList1.csv", usecols=['QuestionNum', 'Question', 'AnswerUse'])
	questions.columns = ['QuestionNum','Question','Answer']
	questions = questions.to_dict('records')
	random.shuffle(questions)
	return questions

def get_trivia_questions():
	questions = pd.read_csv(_thisDir + "/Kanga_TriviaList1.csv", usecols=['QuestionNum', 'Question', 'AnswerUse'])
	questions.columns = ['QuestionNum','Question','Answer']
	return questions['Question'].values

def get_trivia_as_dicts():
	questions = pd.read_csv(_thisDir + "/Kanga_TriviaList1.csv", usecols=['QuestionNum', 'Question', 'AnswerUse'])
	questions.columns = ['QuestionNum','Question','Answer']
	keys = questions['Question'].values
	values = questions['Answer'].values
	dictionary1 = dict(zip(keys, values))
	keys = questions['Question'].values
	values = questions['QuestionNum'].values
	dictionary2 = dict(zip(keys, values))
	return dictionary1, dictionary2

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

def get_questions_used_in_task(subjectId):
	datafile = os.path.join(dataDir,'Kanga',subjectId,subjectId+'_results.csv')
	if os.path.exists(datafile):
		df=pd.read_csv(datafile)
		questions = df['Question'].values
		return questions
	print "File not found"
	return None

def get_unused_questions(subjectId):
	all_questions=get_trivia_questions()
	old_questions=get_questions_used_in_task(subjectId)
	random.shuffle(all_questions)
	unused_questions=[]
	i=0
	j=0
	while i < 10: # there are hundreds of questions, so should not be an infinite loop
		q = all_questions[j]
		if q not in old_questions:
			unused_questions.append(q)
			i+=1
		j+=1
	random.shuffle(unused_questions)
	return unused_questions

def get_ratingtask_expVariables(subjectId):
	trivia_dict,trivia_qnum_dict=get_trivia_as_dicts()
	unused_q=get_unused_questions(subjectId)
	expVariables = []
	rs_min=0
	rs_max=100
	rs_tickIncrement=25
	rs_increment=1
	rs_labelNames=["0", "25", "50", "75", "100"]
	for q in unused_q:
		trial={}
		trial['TrialType']='RateQuestion'
		trial['Question']=q
		answer=trivia_dict[q]
		trial['Answer']=answer
		qnum=trivia_qnum_dict[q]
		trial['QuestionNum']=qnum
		trial['rs_min']=rs_min
		trial['rs_max']=rs_max
		trial['rs_tickIncrement']=rs_tickIncrement
		trial['rs_increment']=rs_increment
		trial['rs_labelNames']=rs_labelNames
		expVariables.append(trial)

		trial={}
		trial['TrialType']='RateAnswer'
		trial['Question']=q
		answer=trivia_dict[q]
		trial['Answer']=answer
		qnum=trivia_qnum_dict[q]
		trial['QuestionNum']=qnum
		trial['rs_min']=rs_min
		trial['rs_max']=rs_max
		trial['rs_tickIncrement']=rs_tickIncrement
		trial['rs_increment']=rs_increment
		trial['rs_labelNames']=rs_labelNames
		expVariables.append(trial)
	return expVariables

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
