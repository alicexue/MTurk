import os, sys
import csv

_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)

def get_stimuli():
	'''
	get array of stimuli from the directory name stim
	'''
	stimuli = []
	for stimulusFile in os.listdir(_thisDir + '/static/stim/demo/'):
		if stimulusFile.endswith(".bmp"): 
			stimuli.append(stimulusFile[:-4])
	return stimuli


def get_bid_responses(csv_name):
	'''
	from a csv file generated by the auction task, generate a dictionary of the stimuli and the participant's bids
	'''
	with open(csv_name, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter='\t', quotechar='|')
		stimBidDict = {}
		rowN = 0
		stimIndex = 0
		bidIndex = 0
		for row in reader:
			variables = row[0].split(',')
			if rowN == 0:
				varN = 0
				stimIndex = variables.index('stimulus0')
				bidIndex = variables.index('rsp')
			else:
				stimulus = variables[stimIndex]
				bid = variables[bidIndex]
				stimBidDict[stimulus] = float(bid)
			rowN+=1
	return stimBidDict