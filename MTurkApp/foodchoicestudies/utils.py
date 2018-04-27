import os
import sys
import csv
import random
import pandas as pd
import numpy as np
from expInfo import *

_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
_parentDir = os.path.abspath(os.path.join(_thisDir, os.pardir))
dataDir = _parentDir + '/data/'

"""
Given name of current task and list of tasks, return the task that should be next
If task is final task, return 'thankyou' to route to thank you page

For example:
	x = 'auction'
	y = 'choicetask'
	z = 'hello'
	tasks = ['auction','choicetask'] 
	print get_next_task('auction', tasks) 		# return 'choicetask'
	print get_next_task('choicetask', tasks) 	# return 'thankyou'
	print get_next_task('hello', tasks) 		# return None

*** For url_for
"""
def get_next_task(currentTask, taskOrder):
	for i in range(0, len(taskOrder)):
		task = taskOrder[i]
		if currentTask == task:
			if i < len(taskOrder) - 1:
				nextTask = taskOrder[i+1]
				if nextTask == 'feedback' or nextTask == 'thankyou':
					return nextTask
				elif 'instructions' in nextTask:
					return 'instructions.' + nextTask
				else:
					return 'tasks.' + nextTask
			else:
				return 'thankyou'
	return None

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
Pair up lists of stimuli without taking bids into account
"""
def get_two_stimuli_lists_without_bids(folder, prepend, fileextension):
	stimuli1 = get_stimuli(folder, prepend, fileextension)
	random.shuffle(stimuli1)
	stimuli2 = get_stimuli(folder, prepend, fileextension)
	random.shuffle(stimuli2)
	shamBids = []
	for i in range(0,len(stimuli1)):
		shamBids.append(-1)
		if stimuli1[i] == stimuli2[i]:
			newIndex = random.randint(0,len(stimuli1)-1)
			while newIndex == i or stimuli1[newIndex] == stimuli2[newIndex]:
				newIndex = random.randint(0,len(stimuli1)-1)
			oldStimulus = stimuli2[i]
			stimuli2[i] = stimuli2[newIndex]
			stimuli2[newIndex] = oldStimulus
	return [stimuli1, shamBids, stimuli2, shamBids]

"""
Get lists of two stimuli for choice task
Stimuli are first rank ordered by bid
pairDiff determines the various differences between the indices of each pair
For each pair in pairDiff, there are unique pairings for each stimulus
Since there are 7 elements in pairDiff and 60 stimuli, there are 7 * (60/2) = 210 pairings in total
The order of the pairings is randomized so that on one trial, the first stimulus may be 2 indices apart from the second stimulus
	and then on the next trial, the first stimulus may be 10 indices apart from the second stimulus
The order of the stimuli within pairings is also randomized so that the stimulus with the higher bid 
	is randomly put on the left or the right
The array returned contains lists of the stimuli names and their respective bids
"""
def get_two_stimuli_lists(stimBidDF, folder, prepend, fileextension):
	result = stimBidDF.sort_values("bid")
	result = result.reset_index(drop=True)

	if len(stimBidDF) == 60:
		pairDiff = [1, 2, 3, 6, 10, 15, 30]
	elif len(stimBidDF) == 80:
		pairDiff = [1, 2, 5, 8, 10, 20, 40] # could be any combo of 1, 2, 4, 5, 8, 10, 20, 40
	stimuli = get_stimuli(folder, prepend, fileextension)
	
	nStim = len(stimuli)
	pairingIndices = get_pairingIndices(pairDiff, nStim)
	df = get_stimulus_pairings(result, pairingIndices)
	shuffledDf = df.sample(frac=1)
	stim1Names = shuffledDf['stimulus1'].values
	stim2Names = shuffledDf['stimulus2'].values
	stim1Bids = shuffledDf['stim1Bid'].values
	stim2Bids = shuffledDf['stim2Bid'].values
	return [stim1Names, stim1Bids, stim2Names, stim2Bids]

"""
Helper method used in get_two_stimuli_lists to get list of pairings of stimuli
"""
def get_pairingIndices(pairDiff, nStim):

	pairingIndices = []
	for x in pairDiff:
		stimUsed = resetStimUsed(nStim) # keep track of whether stimulus has been used in a pairing for this difference already
		for i in range(0,nStim-x):
			if stimUsed[i] == False:
				pairingIndices.append([i, i+x])
				stimUsed[i] = True
				stimUsed[i+x] = True
	return pairingIndices

"""
Helper method used in get_two_stimuli_lists to get dictionary of pairings of stimuli and their rank bid differences
"""
def get_stimulus_pairings(result, pairingIndices):
	dfList = []
	for pair in pairingIndices:
		trialStim = {}
		# shuffles indices within pairings
		stim1Index = random.randint(0,1)
		if stim1Index == 0:
			stim2Index = 1
		else:
			stim2Index = 0
		stimulus1 = result.loc[pair[stim1Index]]['stimulus']
		stimulus2 = result.loc[pair[stim2Index]]['stimulus']
		stim1Bid = float(result.loc[pair[stim1Index]]['bid'])
		stim2Bid = float(result.loc[pair[stim2Index]]['bid'])
		
		trialStim['bidRankDifference'] = pair[1] - pair[0]
		trialStim['stimulus1'] = stimulus1
		trialStim['stimulus2'] = stimulus2
		trialStim['stim1Bid'] = stim1Bid
		trialStim['stim2Bid'] = stim2Bid

		dfList.append(trialStim)
	df = pd.DataFrame(dfList)
	return df


def get_scene_food_stimuli(stimBidDF, familiar_indoor_stimuli, familiar_outdoor_stimuli, indoor_stimuli, outdoor_stimuli, folder, prepend, fileextension):
	result = stimBidDF.sort_values("bid")
	result = result.reset_index(drop=True)

	if len(stimBidDF) == 60:
		pairDiff = [1, 2, 3, 6, 10, 15, 30]
	elif len(stimBidDF) == 80:
		pairDiff = [1, 2, 5, 8, 10, 20, 40] # could be any combo of 1, 2, 4, 5, 8, 10, 20, 40
	stimuli = get_stimuli(folder, prepend, fileextension)
	
	nStim = len(stimuli)
	pairingIndices = get_pairingIndices(pairDiff, nStim)
	df = get_stimulus_pairings(result, pairingIndices)

	random.shuffle(indoor_stimuli)
	random.shuffle(outdoor_stimuli)

	alternatingSceneStimuli = []
	sceneStimuliStatus = []
	j = 0
	k = 0
	print indoor_stimuli
	for stimulus in familiar_indoor_stimuli:
		indoor_stimuli.remove(stimulus[:-4])
	for stimulus in familiar_outdoor_stimuli:
		outdoor_stimuli.remove(stimulus[:-4])


	for i in range(0, len(indoor_stimuli)):
		# add novel stimuli
		alternatingSceneStimuli.append(indoor_stimuli[i])
		sceneStimuliStatus.append('novel')
		alternatingSceneStimuli.append(outdoor_stimuli[i])
		sceneStimuliStatus.append('novel')
		# add familiar stimuli
		alternatingSceneStimuli.append(familiar_indoor_stimuli[j][:-4])
		sceneStimuliStatus.append('familiar')
		alternatingSceneStimuli.append(familiar_outdoor_stimuli[j][:-4])
		sceneStimuliStatus.append('familiar')

		if (j==2): 
			random.shuffle(familiar_indoor_stimuli)
			random.shuffle(familiar_outdoor_stimuli)
			j = 0
		else:
			j+=1
	df.loc[:,'sceneStimulusFamiliarity'] = sceneStimuliStatus
	df.loc[:,'sceneStimulus'] = alternatingSceneStimuli
	df.loc[:,'delta'] = df['stim2Bid'] - df['stim1Bid']

	shuffledList = df.T.to_dict().values()
	random.shuffle(shuffledList)

	shuffledDf = pd.DataFrame(data=shuffledList)
	shuffledDf = shuffledDf.reset_index()
	return shuffledDf

"""
fileName: name of file to read 
stimulusName: name of familiar stimulus
"""
def get_familiar_stimuli(filePath, stimulusName):
	if os.path.exists(filePath):
		df = pd.read_csv(filePath)
		inFamiliarRows = df.loc[df['sceneStimulus'] == 'indoor']
		outFamiliarRows = df.loc[df['sceneStimulus'] == 'outdoor']
		indoorStim = np.unique(inFamiliarRows[stimulusName].values)
		outdoorStim = np.unique(outFamiliarRows[stimulusName].values)
		return {'indoor':indoorStim, 'outdoor':outdoorStim}
	else:
		return {}

"""
Helper method for get_two_stimuli_lists
Returns a dictionary with keys from 0 to nStim-1, with each value as false
"""
def resetStimUsed(nStim):
	stimUsed = {}
	for i in range(0,nStim):
		stimUsed[i] = False
	return stimUsed

"""
Returns a dictionary of the stimuli as keys and their bids as values
csv_name is the location + name of the csv file where the bids are located
The csv must have the stimulus name in a column with the heading "stimulus1"
	the bid must be in a column with the heading "rating"
"""
def get_bid_responses(csv_name):
	'''
	from a csv file generated by the auction task, generate a dictionary of the stimuli and the participant's bids
	'''
	df = pd.read_csv(csv_name)
	stim = df.loc[:,'stimulus1']
	bids = df.loc[:,'rating']
	stimBidDF = pd.concat([bids,stim],axis=1)
	stimBidDF = stimBidDF.rename(index=str, columns={"rating": "bid", "stimulus1": "stimulus"})
	return stimBidDF


def get_ratingtask_expVariables(expId, subjectId, demo):
	if demo == True:
		stimuli = get_stimuli(foodStimFolder[expId]+'demo/','','.bmp')
	else:
		stimuli = get_stimuli(foodStimFolder[expId],'','.bmp')
	random.shuffle(stimuli)

	expVariables = [] # array of dictionaries

	for i in range(0,len(stimuli)):
		expVariables.append({"stimulus":stimuli[i], "fullStimName":stimuli[i]+".bmp"})
	return expVariables

def get_scenetask_expVariables(expId, subjectId, demo):
	if demo == True:
		indoor_folders = ['library-68']
		outdoor_folders = ['woods-68']
		[stim1Names, stim1Bids, stim2Names, stim2Bids] = get_two_stimuli_lists_without_bids(foodStimFolder[expId]+'demo/', '', '.bmp')
		indoor_stimuli = []
		outdoor_stimuli = []
		for folder in indoor_folders:
			indoor_stimuli += get_stimuli('/static/scenes_konk/demo/indoor/' + folder + '/', 'indoor/' + folder + '/', '.jpg')
		for folder in outdoor_folders:
			outdoor_stimuli += get_stimuli('/static/scenes_konk/demo/outdoor/' + folder + '/', 'outdoor/' + folder + '/', '.jpg')
		sceneStimuli = indoor_stimuli + outdoor_stimuli
		random.shuffle(sceneStimuli)

		expVariables = []
		
		indoorsKey = "u"
		outdoorsKey = "i"

		expVariables = [] # array of dictionaries

		for i in range(0,len(sceneStimuli)):
			stimulus = sceneStimuli[i]
			index = stimulus.find('/')
			stimulusType = stimulus[0:index] # indoor / outdoor
			expVariables.append({"sceneStimulus":stimulusType, "fullStimName":stimulus+".jpg", "indoorsKey":indoorsKey, "outdoorsKey":outdoorsKey})
	else:
		indoor_folders = ['bathroom-68','bedroom-68','classroom-68','conferenceroom-68','diningroom-68','empty-68','gym-68','hairsalon-68']
		outdoor_folders = ['beach-68','campsite-68','canyon-68','countryroad-68','field-68','garden-68','golfcourse-68','mountainwhite-68']
		### set experiment conditions here and pass to experiment.html 
		# trialVariables should be an array of dictionaries 
		# each element of the array represents the condition for one trial
		# set the variable conditions to the array of conditions
		indoor_stimuli = []
		outdoor_stimuli = []

		for folder in indoor_folders:
			indoor_stimuli += get_stimuli('/static/scenes_konk/indoor/' + folder + '/', 'indoor/' + folder + '/', '.jpg')
		for folder in outdoor_folders:
			outdoor_stimuli += get_stimuli('/static/scenes_konk/outdoor/' + folder + '/', 'outdoor/' + folder + '/', '.jpg')

		# pick 3 indoor and 3 outdoor stimuli for subject to be familiarized to
		f_indoor_stimuli = []
		while len(f_indoor_stimuli) != 3:
			r = random.randrange(len(indoor_stimuli))
			if indoor_stimuli[r] not in f_indoor_stimuli:
				f_indoor_stimuli.append(indoor_stimuli[r])
		f_outdoor_stimuli = []
		while len(f_outdoor_stimuli) != 3:
			r = random.randrange(len(outdoor_stimuli))
			if outdoor_stimuli[r] not in f_outdoor_stimuli:
				f_outdoor_stimuli.append(outdoor_stimuli[r])
		
		f_stimuli = f_indoor_stimuli + f_outdoor_stimuli

		random.shuffle(f_stimuli)

		stimuli = []

		for i in range(0, 4): # 4 repeats of stimuli
			random.shuffle(f_stimuli)
			stimuli += f_stimuli

		index = subjectId.find('_')
		subjectN = int(subjectId[index+1:])
		
		if (subjectN%2==0):
			indoorsKey = "u"
			outdoorsKey = "i"
		else:
			indoorsKey = "i"
			outdoorsKey = "u"

		expVariables = [] # array of dictionaries

		for i in range(0,len(stimuli)):
			stimulus = stimuli[i]
			index = stimulus.find('/')
			stimulusType = stimulus[0:index] # indoor / outdoor
			expVariables.append({"sceneStimulus":stimulusType, "fullStimName":stimulus+".jpg", "indoorsKey":indoorsKey, "outdoorsKey":outdoorsKey})
	return expVariables

def get_scenechoicetask_expVariables(expId, subjectId, demo):
	if demo == True:
		indoor_folders = ['library-68']
		outdoor_folders = ['woods-68']
		[stim1Names, stim1Bids, stim2Names, stim2Bids] = get_two_stimuli_lists_without_bids(foodStimFolder[expId]+'demo/', '', '.bmp')
		indoor_stimuli = []
		outdoor_stimuli = []
		for folder in indoor_folders:
			indoor_stimuli += get_stimuli('/static/scenes_konk/demo/indoor/' + folder + '/', 'indoor/' + folder + '/', '.jpg')
		for folder in outdoor_folders:
			outdoor_stimuli += get_stimuli('/static/scenes_konk/demo/outdoor/' + folder + '/', 'outdoor/' + folder + '/', '.jpg')
		sceneStimuli = indoor_stimuli + outdoor_stimuli
		random.shuffle(sceneStimuli)

		expVariables = [] # array of dictionaries

		deltas = []
		for i in range(0,len(sceneStimuli)):
			deltas.append(stim2Bids[i] - stim1Bids[i])

		for i in range(0,len(sceneStimuli)):
			sceneStimulus = sceneStimuli[i]
			index = sceneStimulus.find('/')
			stimulusType = sceneStimulus[0:index] # indoor / outdoor
			if (i%2==0):
				sceneStimulusStatus = 'novel'
			else:
				sceneStimulusStatus = 'familiar'
			expVariables.append({"sceneStimulus":stimulusType, "stimulus1":stim1Names[i],"stimulus2":stim2Names[i],"stim1Bid":stim1Bids[i],"stim2Bid":stim2Bids[i], "delta":deltas[i], "fullSceneStimName":sceneStimulus+".jpg", "fullStim1Name":stim1Names[i]+".bmp", "fullStim2Name":stim2Names[i]+".bmp","sceneStimulusStatus":sceneStimulusStatus})
	else:
		indoor_folders = ['bathroom-68','bedroom-68','classroom-68','conferenceroom-68','diningroom-68','empty-68','gym-68','hairsalon-68']
		outdoor_folders = ['beach-68','campsite-68','canyon-68','countryroad-68','field-68','garden-68','golfcourse-68','mountainwhite-68']
		if not os.path.exists(dataDir + expId + '/' + subjectId + '/' + subjectId + '_TrialList_SceneChoiceTask.csv'):
			## subject hasn't done any portion of the Choice Scene Task yet

			auctionFileName = '_AuctionData2.csv'
			stimBidDict = get_bid_responses(dataDir + expId + '/' + subjectId + '/' + subjectId + auctionFileName)
			#[stim1Names, stim1Bids, stim2Names, stim2Bids] = get_two_stimuli_lists(stimBidDict, foodStimFolder[expId], '', '.bmp')
			indoor_stimuli = []
			outdoor_stimuli = []
			for folder in indoor_folders:
				indoor_stimuli += get_stimuli('/static/scenes_konk/indoor/' + folder + '/', 'indoor/' + folder + '/', '.jpg')
			for folder in outdoor_folders:
				outdoor_stimuli += get_stimuli('/static/scenes_konk/outdoor/' + folder + '/', 'outdoor/' + folder + '/', '.jpg')

			familiarStim = get_familiar_stimuli(dataDir + expId + '/' + subjectId + '/' + subjectId + '_SceneTask.csv', 'sceneStimulusPath')
			familiar_indoor_stimuli = familiarStim['indoor']
			familiar_outdoor_stimuli = familiarStim['outdoor']

			shuffledDf = get_scene_food_stimuli(stimBidDict, familiar_indoor_stimuli, familiar_outdoor_stimuli, indoor_stimuli, outdoor_stimuli, foodStimFolder[expId], '', '.bmp')
			
			shuffledDf.to_csv(dataDir + expId + '/' + subjectId + '/' + subjectId + '_TrialList_SceneChoiceTask.csv', index=False)
			shuffledDf = shuffledDf[0:len(shuffledDf)/2]

		else:
			shuffledDf = pd.read_csv(dataDir + expId + '/' + subjectId + '/' + subjectId + '_TrialList_SceneChoiceTask.csv')
			shuffledDf = shuffledDf[len(shuffledDf)/2:]

		stim1Names = shuffledDf['stimulus1'].values
		stim2Names = shuffledDf['stimulus2'].values
		stim1Bids = shuffledDf['stim1Bid'].values
		stim2Bids = shuffledDf['stim2Bid'].values
		sceneStimuli = shuffledDf['sceneStimulus'].values
		sceneStimuliStatus = shuffledDf['sceneStimulusFamiliarity'].values 

		expVariables = [] # array of dictionaries

		deltas = []
		for i in range(0,len(stim1Bids)):
			deltas.append(stim2Bids[i] - stim1Bids[i])

		for i in range(0,len(stim1Bids)):
			sceneStimulus = sceneStimuli[i]
			index = sceneStimulus.find('/')
			stimulusType = sceneStimulus[0:index] # indoor / outdoor
			expVariables.append({"sceneStimulus":stimulusType, "stimulus1":stim1Names[i],"stimulus2":stim2Names[i],"stim1Bid":stim1Bids[i],"stim2Bid":stim2Bids[i], "delta":deltas[i], "fullSceneStimName":sceneStimulus+".jpg", "fullStim1Name":stim1Names[i]+".bmp", "fullStim2Name":stim2Names[i]+".bmp","sceneStimulusStatus":sceneStimuliStatus[i]})
	return expVariables
