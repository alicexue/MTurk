import pandas as pd
import csv, os, sys
import datetime

_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)

def store_subject_info(expID, workerID):
	if not os.path.exists(expID):
		os.makedirs(expID)
	csvLocation = _thisDir + '/' + expID +'/subject_worker_ids.csv'
	if not os.path.exists(csvLocation):
		newSubjectID = expID + "%04d" % (1,)
		currentTime = datetime.datetime.now()
		currentTime = currentTime.strftime("%Y-%m-%d %H:%M:%S")
		newSubject = {'subjectID':newSubjectID, 'workerID':workerID, 'timeCreated':currentTime, 'completedAuction':False, 'completedChoiceTask':False}
		new_df = pd.DataFrame(data=newSubject, index=[0])
	else:
		df = pd.read_csv(csvLocation)
		nSubjects = len(df.index)
		newSubjectID = expID + "%04d" % (nSubjects+1,)
		currentTime = datetime.datetime.now()
		currentTime = currentTime.strftime("%Y-%m-%d %H:%M:%S")
		newSubject = {'subjectID':newSubjectID, 'workerID':workerID, 'timeCreated':currentTime, 'completedAuction':False, 'completedChoiceTask':False}
		df2 = pd.DataFrame(data=newSubject, index=[0])
		new_df = pd.concat([df,df2], axis=0)
	new_df.to_csv(csvLocation,index=False)

# should assume subject did not participate before
def get_subjectID(expID, workerID):
	csvLocation = _thisDir + '/' + expID +'/subject_worker_ids.csv'
	df = pd.read_csv(csvLocation)
	subjectIDs = df.loc[df['workerID'] == workerID]['subjectID'].values
	if len(subjectIDs) > 0:
		subjectID = df.loc[df['workerID'] == workerID]['subjectID'].values[0]
		return subjectID
	else: 
		return False # workerID doesn't exist 

def workerID_exists(expID, workerID):
	subjectID = get_subjectID(expID, workerID)
	if subjectID == False:
		return False
	else:
		return True

def completed_auction(expID, workerID):
	csvLocation = _thisDir + '/' + expID +'/subject_worker_ids.csv'
	df = pd.read_csv(csvLocation)
	if workerID_exists(expID, workerID):
		completed = df.loc[df['workerID'] == workerID]['completedAuction'].values[0]
		if completed == True:
			return True
		else:
			return False
	else:
		return False

def completed_choice_task(expID, workerID):
	csvLocation = _thisDir + '/' + expID +'/subject_worker_ids.csv'
	df = pd.read_csv(csvLocation)
	if workerID_exists(expID, workerID):
		completed = df.loc[df['workerID'] == workerID]['completedChoiceTask'].values[0]
		if completed == True:
			return True
		else:
			return False
	else:
		return False

def set_completed_auction(expID, workerID, boole):
	csvLocation = _thisDir + '/' + expID +'/subject_worker_ids.csv'
	df = pd.read_csv(csvLocation)
	if workerID_exists(expID, workerID):
		idx = df[df['workerID'] == workerID].index[0]
		print df.loc[idx, 'completedAuction']
		df.loc[idx, 'completedAuction'] = boole
		print df.loc[idx, 'completedAuction']
		df.to_csv(csvLocation,index=False)

def set_completed_choice_task(expID, workerID, boole):
	csvLocation = _thisDir + '/' + expID +'/subject_worker_ids.csv'
	df = pd.read_csv(csvLocation)
	if workerID_exists(expID, workerID):
		idx = df[df['workerID'] == workerID].index[0]
		print df.loc[idx, 'completedChoiceTask']
		df.loc[idx, 'completedChoiceTask'] = boole
		print df.loc[idx, 'completedChoiceTask']
		df.to_csv(csvLocation,index=False)
