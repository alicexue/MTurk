import pandas as pd
import csv, os, sys
import datetime

_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)

def store_subject_info(expName, workerID):
	if not os.path.exists(expName):
		os.makedirs(expName)
	csvLocation = _thisDir + '/' + expName +'/subject_worker_ids.csv'
	if not os.path.exists(csvLocation):
		newSubjectID = expName + "%05d" % (1,)
		currentTime = datetime.datetime.now()
		currentTime = currentTime.strftime("%Y-%m-%d %H:%M:%S")
		newSubject = {'subjectID':newSubjectID, 'workerID':workerID, 'timeCreated':currentTime}
		new_df = pd.DataFrame(data=newSubject, index=[0])
	else:
		df = pd.read_csv(csvLocation)
		nSubjects = len(df.index)
		newSubjectID = expName + "%05d" % (nSubjects+1,)
		currentTime = datetime.datetime.now()
		currentTime = currentTime.strftime("%Y-%m-%d %H:%M:%S")
		newSubject = {'subjectID':newSubjectID, 'workerID':workerID, 'timeCreated':currentTime}
		df2 = pd.DataFrame(data=newSubject, index=[0])
		new_df = pd.concat([df,df2], axis=0)
	new_df.to_csv(csvLocation,index=False)

# should assume subject did not participate before
def get_subjectID(expName, workerID):
	csvLocation = _thisDir + '/' + expName +'/subject_worker_ids.csv'
	df = pd.read_csv(csvLocation)
	subjectID = df.loc[df['workerID'] == workerID]['subjectID'].values[0]
	return subjectID