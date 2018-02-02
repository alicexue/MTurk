import pandas as pd
import csv
import os
import sys
import datetime

# Methods to manage EXPID_subject_assignment_info.csv and EXPID_subject_worker_ids.csv inside experiment folder

_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)

def store_subject_info(expId, workerId, assignmentId, hitId, turkSubmitTo):
	if not os.path.exists(expId):
		os.makedirs(expId)
	# store subjectId and other relevant subject info, except workerId
	csvLocation = _thisDir + '/' + expId +'/' + expId + '_subject_assignment_info.csv'
	if not os.path.exists(csvLocation):
		newSubjectId = expId + "_%04d" % (1,)
		currentTime = datetime.datetime.now()
		currentTime = currentTime.strftime("%Y-%m-%d %H:%M:%S")
		newSubject = {'subjectId':newSubjectId, 'assignmentId':assignmentId, 'hitId':hitId, 'turkSubmitTo':turkSubmitTo, 'timestamp':currentTime, 'completedAuction':False, 'completedChoiceTask':False}
		new_df = pd.DataFrame(data=newSubject, index=[0])
	else:
		df = pd.read_csv(csvLocation)
		nSubjects = len(df.index)
		newSubjectId = expId + "_%04d" % (nSubjects+1,)
		currentTime = datetime.datetime.now()
		currentTime = currentTime.strftime("%Y-%m-%d %H:%M:%S")
		newSubject = {'subjectId':newSubjectId, 'assignmentId':assignmentId, 'hitId':hitId, 'turkSubmitTo':turkSubmitTo, 'timestamp':currentTime, 'completedAuction':False, 'completedChoiceTask':False}
		df2 = pd.DataFrame(data=newSubject, index=[0])
		new_df = pd.concat([df,df2], axis=0)
	new_df.to_csv(csvLocation,index=False)

	# store subjectId and workerId
	csvLocation = _thisDir + '/' + expId +'/' + expId + '_subject_worker_ids.csv'
	newSubject = {'expId':expId, 'workerId':workerId, 'timestamp':currentTime}
	if not os.path.exists(csvLocation):
		new_df = pd.DataFrame(data=newSubject, index=[0])
	else:
		df = pd.read_csv(csvLocation)
		df2 = pd.DataFrame(data=newSubject, index=[0])
		new_df = pd.concat([df,df2], axis=0)
	new_df.to_csv(csvLocation,index=False)


def get_timestamp(expId, workerId):
	csvLocation = _thisDir + '/' + expId +'/' + expId + '_subject_worker_ids.csv'
	if os.path.exists(csvLocation):
		df = pd.read_csv(csvLocation)
		timestamps = df.loc[df['workerId'] == workerId]['timestamp'].values
		if len(timestamps) > 0:
			return timestamps[0]
		else: 
			return False 

# should assume subject did not participate before
def get_subjectId(expId, workerId):
	csvLocation = _thisDir + '/' + expId +'/' + expId + '_subject_assignment_info.csv'
	if os.path.exists(csvLocation):
		df = pd.read_csv(csvLocation)
		timestamp = get_timestamp(expId, workerId)
		if timestamp != False:
			subjectIds = df.loc[df['timestamp'] == timestamp]['subjectId'].values
			if len(subjectIds) > 0:
				return subjectIds[0]
			else: 
				return False 
		else:
			return False
	else:
		return False

def get_assignmentId(expId, subjectId):
	csvLocation = _thisDir + '/' + expId +'/' + expId + '_subject_assignment_info.csv'
	if os.path.exists(csvLocation):
		df = pd.read_csv(csvLocation)
		assignmentIds = df.loc[df['subjectId'] == subjectId]['assignmentId'].values
		if len(assignmentIds) > 0:
			assignmentId = assignmentIds[0]
			return assignmentId
		else: 
			return False # assignmentId doesn't exist
	else:
		return False

def get_turkSubmitTo(expId, subjectId):
	csvLocation = _thisDir + '/' + expId +'/' + expId + '_subject_assignment_info.csv'
	if os.path.exists(csvLocation):
		df = pd.read_csv(csvLocation)
		turkSubmitTo = df.loc[df['subjectId'] == subjectId]['turkSubmitTo'].values
		if len(turkSubmitTo) > 0:
			return turkSubmitTo[0]
		else: 
			return False # assignmentId doesn't exist
	else:
		return False

def workerId_exists(expId, workerId):
	subjectId = get_subjectId(expId, workerId)
	if subjectId == False:
		return False
	else:
		return True

def completed_auction(expId, workerId):
	csvLocation = _thisDir + '/' + expId +'/' + expId + '_subject_assignment_info.csv'
	if os.path.exists(csvLocation):
		df = pd.read_csv(csvLocation)
		if workerId_exists(expId, workerId):
			subjectId = get_subjectId(expId, workerId)
			completed = df.loc[df['subjectId'] == subjectId]['completedAuction'].values[0]
			if completed == True:
				return True
			else:
				return False
		else:
			return False
	else:
		return False

def completed_choice_task(expId, workerId):
	csvLocation = _thisDir + '/' + expId +'/' + expId + '_subject_assignment_info.csv'
	if os.path.exists(csvLocation):
		df = pd.read_csv(csvLocation)
		if workerId_exists(expId, workerId):
			subjectId = get_subjectId(expId, workerId)
			completed = df.loc[df['subjectId'] == subjectId]['completedChoiceTask'].values[0]
			if completed == True:
				return True
			else:
				return False
		else:
			return False
	else:
		return False

def set_completed_auction(expId, workerId, boole):
	csvLocation = _thisDir + '/' + expId +'/' + expId + '_subject_assignment_info.csv'
	if os.path.exists(csvLocation):
		df = pd.read_csv(csvLocation)
		if workerId_exists(expId, workerId):
			subjectId = get_subjectId(expId, workerId)
			idx = df[df['subjectId'] == subjectId].index[0]
			df.loc[idx, 'completedAuction'] = boole
			df.to_csv(csvLocation,index=False)

def set_completed_choice_task(expId, workerId, boole):
	csvLocation = _thisDir + '/' + expId +'/' + expId + '_subject_assignment_info.csv'
	df = pd.read_csv(csvLocation)
	if os.path.exists(csvLocation):
		if workerId_exists(expId, workerId):
			subjectId = get_subjectId(expId, workerId)
			idx = df[df['subjectId'] ==subjectId].index[0]
			df.loc[idx, 'completedChoiceTask'] = boole
			df.to_csv(csvLocation,index=False)

def store_feedback(expId, workerId, feedback):
	csvLocation = _thisDir + '/' + expId +'/' + expId + '_subject_feedback.csv'
	if workerId_exists(expId, workerId):
		subjectId = get_subjectId(expId, workerId)
		newData = {'expId':expId, 'subjectId':subjectId, 'feedback':feedback}
		if not os.path.exists(csvLocation):
			new_df = pd.DataFrame(data=newData, index=[0])
		else:
			df = pd.read_csv(csvLocation)
			df2 = pd.DataFrame(data=newData, index=[0])
			new_df = pd.concat([df,df2], axis=0)
		new_df.to_csv(csvLocation,index=False)
