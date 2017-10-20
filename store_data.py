import os, sys
import csv

_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)

def organize_data(expResults, data_csv_name, stimuli_csv_name):
	if not os.path.exists('data'):
		os.makedirs('data')

	keys = expResults[0].keys()
	keys = list(reversed(keys))
	header = []
	stimuliHeader = []
	for key in keys:
		if key == 'results':
			resultKeys = expResults[0]['results'].keys()
			resultKeys = list(reversed(resultKeys))
			for resultKey in resultKeys:
				header.append(resultKey)

		elif key != 'stimuli':
			header.append(key)
		else:
			stimuli = expResults[0]['stimuli']
			stimulusKeys = expResults[0]['stimuli'][0].keys()
			stimulusKeys = list(reversed(stimulusKeys))
			for i in range(0,len(stimuli)):
				for stimulusKey in stimulusKeys:
					stimuliHeader.append('stimulus'+str(i+1)+'_'+stimulusKey)

	allTrialOutput = []
	allStimuliInfo = []
	for trial in expResults:
		trialOutput = []
		stimuliInfo = []
		for key in keys:
			if key == 'results':
				results = trial['results']
				for resultKey in results:
					trialOutput.append(str(results[resultKey]))

			elif key != 'stimuli':
				trialOutput.append(str(trial[key]))
			else:
				stimuli = trial['stimuli']
				for i in range(0,len(stimuli)):
					stimulus = stimuli[i]
					for stimulusKey in stimulusKeys:
						stimuliInfo.append(str(stimulus[stimulusKey]))
		allTrialOutput.append(trialOutput)
		allStimuliInfo.append(stimuliInfo)

	with open(_thisDir + '/data/' + data_csv_name, 'wb') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(header)

		for trial in allTrialOutput:
			writer.writerow(trial)

	with open(_thisDir + '/data/' + stimuli_csv_name, 'wb') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(stimuliHeader)

		for trialStimuli in allStimuliInfo:
			writer.writerow(trialStimuli)