import os, sys
import csv
import pandas as pd
import datetime

_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)

def store_data(expID, expResults, taskName, subjectID):
	dataDF = None
	stimDF = None
	for i in range(0,len(expResults)):
		trial = expResults[i]
		stimuli = trial.pop('stimuli', None) # stimuli is array

		tmpStimuli = {}
		for j in range(0, len(stimuli)):
			stimulusInfo = stimuli[j]
			keys = stimulusInfo.keys()
			for key in keys:
				value = str(stimulusInfo[key]) # lists will be separated into multiple rows in df
				tmpStimuli.update({'stimulus' + str(j+1) + '_' + key:value})
		stimuli = tmpStimuli

		results = trial.pop('results', None)

		currentTime = datetime.datetime.now()
		currentTime = currentTime.strftime("%Y-%m-%d %H:%M:%S")

		trial.update(results)
		trial.update({'subjectID':subjectID, 'date':currentTime})
		
		stimuli.update({'subjectID':subjectID, 'date':currentTime})

		if i == 0:
			trialDataDF = pd.DataFrame(data=trial, index=[0])
			dataDF = trialDataDF

			trialStimDF = pd.DataFrame(data=stimuli, index=[0])
			stimDF = trialStimDF
		else:
			trialDataDF = pd.DataFrame(data=trial, index=[i+1])
			dataDF = pd.concat([dataDF,trialDataDF], axis=0)

			trialStimDF = pd.DataFrame(data=stimuli, index=[i+1])
			stimDF = pd.concat([stimDF,trialStimDF], axis=0)

	dataFileLocation = _thisDir + '/' + expID + '/' + subjectID + '/' + subjectID + '_'+ taskName +'Data'

	stimFileLocation = _thisDir + '/' + expID + '/' + subjectID + '/' + subjectID + '_'+ taskName +'Stimuli'

	newDataFileName = dataFileLocation
	newStimFileName = stimFileLocation

	# prevent overwriting existing data files - append a version number at end of name
	# to prevent infinite while loop, will stop after 10 cycles and just append current date
	i = 1;
	while (os.path.exists(newDataFileName + '.csv') and i < 11): 
		newDataFileName = dataFileLocation + '_' + "%02d" % (i,)
		newStimFileName = stimFileLocation + '_' + "%02d" % (i,)
		i+=1

	if i >= 11:
		currentTime = datetime.datetime.now()
		currentTime = currentTime.strftime("%Y_%m_%d_%H_%M_%S")
		newDataFileName = dataFileLocation + currentTime
		newStimFileName = stimFileLocation + currentTime

	dataDF.to_csv(newDataFileName + '.csv', index=False)
	stimDF.to_csv(newStimFileName + '.csv', index=False)
		