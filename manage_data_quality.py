import pandas as pd
import csv
import os
import sys

# data_quality_summary.csv is internally maintained, not related to the MTurk side

_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)

# double check if this code is right
def check_subject_data(expId, subjectId):
	subjectFolder = _thisDir + '/' + expId + '/' + subjectId + '/'

	auctionFile = subjectFolder + subjectId + '_AuctionData.csv'
	choiceFile = subjectFolder + subjectId + '_ChoiceTaskData.csv'

	"""
	if os.path.exists(auctionFile):
		auctionData = pd.read_csv(auctionFile)
		print auctionData
	"""

	if os.path.exists(choiceFile):
		choiceData = pd.read_csv(choiceFile)

		receivedResponseClmn = choiceData['receivedResponse']

		# where stimulus 1 would be correct (consistent) choice
		stim1CorrectRsp = choiceData['stimulus1Bid'] > choiceData['stimulus2Bid']

		choices = choiceData['selected'] == choiceData['stimulus1']

		consistentRsps = stim1CorrectRsp == choices
		consistentRsps = consistentRsps[receivedResponseClmn == True]

		consistency = round(consistentRsps.mean(), 3)
		
		nResponses = receivedResponseClmn.sum()

		return [consistency, nResponses]
	return [0, 0]

def get_assignment_status(expId, subjectId):
	summaryFile = _thisDir + '/' + expId + '/' + expId + '_data_quality_summary.csv'
	if os.path.exists(summaryFile):
		df = pd.read_csv(summaryFile)
		status = df.loc[df["subjectId"] == subjectId]["status"].values
		if len(status) > 0:
			return status[0]
		else: 
			return False 
	else:
		return False

def update_assignment_status(expId, subjectId, status):
	summaryFile = _thisDir + '/' + expId + '/' + expId + '_data_quality_summary.csv'
	if os.path.exists(summaryFile):
		df = pd.read_csv(summaryFile)
		idx = df[df['subjectId'] == subjectId].index[0]
		df.loc[idx, 'status'] = status
		df.to_csv(summaryFile,index=False)

