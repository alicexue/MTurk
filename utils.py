import os
import sys
import csv
import random
import pandas as pd

_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)

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
"""
def get_next_task(currentTask, taskOrder):
	for i in range(0, len(taskOrder)):
		task = taskOrder[i]
		if currentTask == task:
			if i < len(taskOrder) - 1:
				return taskOrder[i+1]
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
Makes experiment folder
Makes subject folder inside experiment folder
"""
def add_new_subject(expId, subjectId):
	if not os.path.exists(expId):
		os.makedirs(expId)

	if not os.path.exists(expId + '/' + subjectId):
		os.makedirs(expId + '/' + subjectId)

"""
Returns a list of all stimuli in the stim folder (assuming all the .bmp files are stimulus images)
"""
def get_stimuli(folder):
	'''
	get array of stimuli from the directory name stim
	'''
	stimuli = []
	for stimulusFile in os.listdir(_thisDir + folder):
		if stimulusFile.endswith(".bmp"): 
			stimuli.append(stimulusFile[:-4])
	return stimuli

"""
Pair up lists of stimuli without taking bids into account
"""
def get_two_stimuli_lists_without_bids(folder):
	stimuli1 = get_stimuli(folder)
	random.shuffle(stimuli1)
	stimuli2 = get_stimuli(folder)
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
def get_two_stimuli_lists(stimBidDF, folder):
	result = stimBidDF.sort_values("bid")
	result = result.reset_index(drop=True)

	pairDiff = [1, 2, 3, 6, 10, 15, 30]
	stimuli = get_stimuli(folder)
	nStim = len(stimuli)
	pairingIndices = []
	for x in pairDiff:

		stimUsed = resetStimUsed(nStim) 
		# keep track of whether stimulus has been used in a pairing for this difference already

		for i in range(0,nStim-x):
			if stimUsed[i] == False:
				pairingIndices.append([i, i+x])
				stimUsed[i] = True
				stimUsed[i+x] = True
	random.shuffle(pairingIndices) # shuffles possible pairings

	stim1Names = []
	stim2Names = []	

	stim1Bids = []
	stim2Bids = []

	for pair in pairingIndices:

		# shuffles indices within pairings
		stim1Index = random.randint(0,1)
		if stim1Index == 0:
			stim2Index = 1
		else:
			stim2Index = 0
		
		stim1Names.append(result.loc[pair[stim1Index]]['stimulus'])
		stim2Names.append(result.loc[pair[stim2Index]]['stimulus'])

		stim1Bids.append(float(result.loc[pair[stim1Index]]['bid']))
		stim2Bids.append(float(result.loc[pair[stim2Index]]['bid']))

	return [stim1Names, stim1Bids, stim2Names, stim2Bids]

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