import pandas as pd
import csv
import os
import sys
from manage_subject_info import *
from manage_data_quality import *

"""
Creates csv file with summary statistics for each participant: 
	number of trials in choice task which they responded
	and percent consistency of responses in choice task with auction bids
"""

_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)


if len(sys.argv) < 2:
	print "Enter expId as 2nd argument"
	sys.exit()

expId = sys.argv[1]

if not os.path.exists(expId):
	print "No data has been collected for ", expId, " yet."
	sys.exit()

subjects = []

dataDir = _thisDir + '/' + expId + '/'
summaryFile = dataDir + '/' + expId + '_data_quality_summary.csv'

# assuming subject folders are of this format: expID_subjectNumber
for tmpfile in os.listdir(dataDir):
	if os.path.isdir(expId + '/' + str(tmpfile)) and tmpfile.startswith(expId + '_'):
		subjects.append(str(tmpfile))


if not os.path.exists(summaryFile):
	accuracyStats = []
	responseStats = []

	for subject in subjects:
		[percentAccuracy, nResponses] = check_subject_data(expId, subject)
		accuracyStats.append(percentAccuracy)
		responseStats.append(nResponses)

	subjectStats = {'subjectId':subjects, 'percentAccuracy':accuracyStats, 'nResponses':responseStats, 'status':'AwaitingApproval'}
	new_df = pd.DataFrame(data=subjectStats)
else:
	newSubjects = []
	accuracyStats = []
	responseStats = []

	df = pd.read_csv(summaryFile)
	subjectsWStats = df['subjectId'].values
	for subject in subjects:
		if subject not in subjectsWStats and completed_auction_subject(expId, subject):
			[percentAccuracy, nResponses] = check_subject_data(expId, subject)
			newSubjects.append(subject)
			accuracyStats.append(percentAccuracy)
			responseStats.append(nResponses)

	subjectStats = {'subjectId':newSubjects, 'percentAccuracy':accuracyStats, 'nResponses':responseStats, 'status':'AwaitingApproval'}
	df2 = pd.DataFrame(data=subjectStats)
	new_df = pd.concat([df,df2], axis=0)

new_df.to_csv(summaryFile,index=False)

