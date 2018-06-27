import os
import sys
import csv
import random
import unicodedata
import pandas as pd
import numpy as np

_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
_parentDir = os.path.abspath(os.path.join(_thisDir, os.pardir))
dataDir = _parentDir + '/data/'

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

def get_foodq():
	info = pd.read_csv(_thisDir + '/FoodQuestions.csv')
	questions=info['Question']
	leftText=info['LeftText']
	middleText=info['MiddleText']
	rightText=info['RightText']
	new_info=[]
	for i in range(0,len(questions)):
		q = questions[i]
		l=leftText[i]
		if type(l) == float:
			l=''
		m=middleText[i]
		if type(m) == float:
			m=''
		r=rightText[i]
		if type(r) == float:
			r=''
		new_info.append({'question':q,'leftText':l,'middleText':m,'rightText':r})
	return new_info

"""
Creates list of dictionaries where each dictionary holds the variables for one trial
"""
def get_ratingtask_expVariables(stimFolder, demo):
	stimuli = get_stimuli(stimFolder,'','.bmp')
	random.shuffle(stimuli)

	expVariables = [] # array of dictionaries

	foodq = get_foodq()

	for i in range(0,len(stimuli)):
		for j in range(0, len(foodq)):
			question = foodq[j]['question']
			leftRatingText = foodq[j]['leftText']
			middleRatingText = foodq[j]['middleText']
			rightRatingText = foodq[j]['rightText']
			rs_min=0
			rs_max=10
			rs_tickIncrement=1
			rs_increment=0.01
			rs_labelNames=["0", "", "", "", "", "5", "", "", "", "", "10"]
			expVariables.append({'stimulus':stimuli[i], 'fullStimName':stimuli[i]+'.bmp', 'question':question, 'leftRatingText':leftRatingText, 'middleRatingText':middleRatingText, 'rightRatingText':rightRatingText, 'rs_min':rs_min, 'rs_max':rs_max, 'rs_tickIncrement':rs_tickIncrement, 'rs_increment':rs_increment, 'rs_labelNames':rs_labelNames})
	return expVariables

"""
Get demographic questions
Returns dictionary with keys as index of question
Values are dictionaries with questions as keys and the values are a list of options
"""
def get_demographicq():
	info = pd.read_csv(_thisDir + '/DemographicQuestions.csv')
	questions=info['Question']
	info=info.set_index('Question')
	new_info=[]
	for j in range(0,len(questions)):
		q = questions[j]
		tmp=info.loc[q].values
		options=[]
		for i in tmp:
			if type(i) != float: # remove nan values
				options.append(i)
		new_info.append({q:options})
	return new_info

def get_TREQr18():
	info = pd.read_csv(_thisDir + '/TREQ-r18.csv')
	questions=info['Question']
	option1=info['Option1']
	option2=info['Option2']
	option3=info['Option3']
	option4=info['Option4']
	return questions, option1, option2, option3, option4

def get_EAT26():
	info = pd.read_csv(_thisDir + '/EAT26.csv')
	questions=info['Question']
	option1=info['Option1']
	option2=info['Option2']
	option3=info['Option3']
	option4=info['Option4']
	option5=info['Option5']
	option6=info['Option6']
	return questions, option1, option2, option3, option4, option5, option6

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
	df = df.loc[df['question']=='How TASTY is this food?']
	stim = df.loc[:,'stimulus1']
	bids = df.loc[:,'rating']
	stimBidDF = pd.concat([bids,stim],axis=1)
	stimBidDF = stimBidDF.rename(index=str, columns={"rating": "bid", "stimulus1": "stimulus"})
	return stimBidDF

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

	if len(stimBidDF) == 2:
		pairDiff = [1, 2]

	if len(stimBidDF) == 60:
		pairDiff = [1, 2, 3, 6, 10, 15, 30]
	elif len(stimBidDF) == 80:
		pairDiff = [1, 2, 5, 8, 10, 20, 40] # could be any combo of 1, 2, 4, 5, 8, 10, 20, 40
	else: ##### change later
		pairDiff = [1, 2]
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