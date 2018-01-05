import pandas as pd
import csv
import os
import sys
import datetime

_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)

def store_subject_info(expId, workerId, assignmentId, hitId, turkSubmitTo):
	if not os.path.exists(expId):
		os.makedirs(expId)
	csvLocation = _thisDir + '/' + expId +'/subject_worker_ids.csv'
	if not os.path.exists(csvLocation):
		newSubjectId = expId + "_%04d" % (1,)
		currentTime = datetime.datetime.now()
		currentTime = currentTime.strftime("%Y-%m-%d %H:%M:%S")
		newSubject = {'subjectId':newSubjectId, 'workerId':workerId, 'assignmentId':assignmentId, 'hitId':hitId, 'turkSubmitTo':turkSubmitTo, 'timeCreated':currentTime, 'completedAuction':False, 'completedChoiceTask':False}
		new_df = pd.DataFrame(data=newSubject, index=[0])
	else:
		df = pd.read_csv(csvLocation)
		nSubjects = len(df.index)
		newSubjectId = expId + "_%04d" % (nSubjects+1,)
		currentTime = datetime.datetime.now()
		currentTime = currentTime.strftime("%Y-%m-%d %H:%M:%S")
		newSubject = {'subjectId':newSubjectId, 'workerId':workerId, 'assignmentId':assignmentId, 'hitId':hitId, 'turkSubmitTo':turkSubmitTo, 'timeCreated':currentTime, 'completedAuction':False, 'completedChoiceTask':False}
		df2 = pd.DataFrame(data=newSubject, index=[0])
		new_df = pd.concat([df,df2], axis=0)
	new_df.to_csv(csvLocation,index=False)

# should assume subject did not participate before
def get_subjectId(expId, workerId):
	csvLocation = _thisDir + '/' + expId +'/subject_worker_ids.csv'
	df = pd.read_csv(csvLocation)
	subjectIds = df.loc[df['workerId'] == workerId]['subjectId'].values
	if len(subjectIds) > 0:
		subjectId = df.loc[df['workerId'] == workerId]['subjectId'].values[0]
		return subjectId
	else: 
		return False # workerId doesn't exist 

def workerId_exists(expId, workerId):
	subjectId = get_subjectId(expId, workerId)
	if subjectId == False:
		return False
	else:
		return True

def completed_auction(expId, workerId):
	csvLocation = _thisDir + '/' + expId +'/subject_worker_ids.csv'
	df = pd.read_csv(csvLocation)
	if workerId_exists(expId, workerId):
		completed = df.loc[df['workerId'] == workerId]['completedAuction'].values[0]
		if completed == True:
			return True
		else:
			return False
	else:
		return False

def completed_choice_task(expId, workerId):
	csvLocation = _thisDir + '/' + expId +'/subject_worker_ids.csv'
	df = pd.read_csv(csvLocation)
	if workerId_exists(expId, workerId):
		completed = df.loc[df['workerId'] == workerId]['completedChoiceTask'].values[0]
		if completed == True:
			return True
		else:
			return False
	else:
		return False

def set_completed_auction(expId, workerId, boole):
	csvLocation = _thisDir + '/' + expId +'/subject_worker_ids.csv'
	df = pd.read_csv(csvLocation)
	if workerId_exists(expId, workerId):
		idx = df[df['workerId'] == workerId].index[0]
		df.loc[idx, 'completedAuction'] = boole
		df.to_csv(csvLocation,index=False)

def set_completed_choice_task(expId, workerId, boole):
	csvLocation = _thisDir + '/' + expId +'/subject_worker_ids.csv'
	df = pd.read_csv(csvLocation)
	if workerId_exists(expId, workerId):
		idx = df[df['workerId'] == workerId].index[0]
		df.loc[idx, 'completedChoiceTask'] = boole
		df.to_csv(csvLocation,index=False)
