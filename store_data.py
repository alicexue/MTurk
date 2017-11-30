import os, sys
import csv
import pandas as pd

_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)

def store_data(expName, expResults, taskName, subjectID):
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

		trial.update(results)
		trial.update({'subjectID':subjectID})
		
		stimuli.update({'subjectID':subjectID})

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

	csvLocation = _thisDir + '/' + expName + '/' + subjectID + '/' + subjectID + '_'+ taskName +'Data.csv'
	dataDF.to_csv(csvLocation,index=False)

	csvLocation = _thisDir + '/' + expName + '/' + subjectID + '/' + subjectID + '_'+ taskName +'Stimuli.csv'
	stimDF.to_csv(csvLocation,index=False)