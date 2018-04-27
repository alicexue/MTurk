import pandas as pd
import csv
import os
import sys
import subprocess
from manage_subject_info import *
from manage_data_quality import *

"""
	Get list of assignments that meet criteria - FOR DUMMY HIT
"""
_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)

if len(sys.argv) < 3:
	print "Enter expId as 2nd argument"
	print "Enter dummy expID as 3rd argument"
	sys.exit()

expId = sys.argv[1]
dummyExpId = sys.argv[2]

if not os.path.exists(expId):
	print "No data has been collected for", expId, "yet."
	sys.exit()

dataDir = _thisDir + '/' + expId + '/'
summaryFile = dataDir + '/' + expId + '_data_quality_summary.csv'

df = pd.read_csv(summaryFile)
subjectsWStats = df['subjectId'].values

subjectIds = []
workerIds = []
completedAuction = []
completedChoice = []
consistencyData = []
nRspsData = []

for subjectId in subjectsWStats:
	workerId = get_workerId(expId, subjectId)
	subjectIds.append(subjectId)
	workerIds.append(workerId)
	completedAuction.append(completed_auction(expId, workerId))
	completedChoice.append(completed_choice_task(expId, workerId))
	[consistency, nResponses] = check_subject_data(expId, subjectId)
	consistencyData.append(consistency)
	nRspsData.append(nResponses)

subjectInfo = {"subject":subjectIds, "workerId":workerIds,"completedAuction":completedAuction,"completedChoice":completedChoice,"consistency":consistencyData,"nResponses":nRspsData}
subjectDF = pd.DataFrame(data=subjectInfo)

print "Number of subjects:", len(subjectDF)
subjectsToApprove = subjectDF.loc[(subjectDF['consistency'] >= .55) & (subjectDF['nResponses'] >= 150)]

print "Number of subjects to approve:", len(subjectsToApprove['workerId'].values)
print subjectsToApprove[['workerId','consistency','nResponses']]

subjectsToReject = subjectDF.loc[(subjectDF['consistency'] < .55) | (subjectDF['nResponses'] < 150)]
print "Number of subjects to reject:", len(subjectsToReject['workerId'].values)
print subjectsToReject[['workerId','consistency','nResponses']]

response = ""
while (response != "y" and response != "n"):
	response = raw_input("Do you want to reject those assignments now? (y/n)\n")
	if response == "y":
		counter = 0
		workerIdsToReject = subjectsToReject['workerId'].values
		for i in range(0,len(workerIdsToReject)):
			workerId = workerIdsToReject[i]
			dummySubjectId = get_subjectId(dummyExpId, workerId)
			dummyAssignmentId = get_assignmentId(dummyExpId, dummySubjectId)
			dummyTurkSubmitTo = get_turkSubmitTo(dummyExpId, dummySubjectId)
			print "To reject - worker:", workerId, "\tassignment:", dummyAssignmentId
			if dummyTurkSubmitTo == "https://www.mturk.com" or dummyTurkSubmitTo == "https://workersandbox.mturk.com":
				if dummyTurkSubmitTo == "https://www.mturk.com":
					liveArg = "live"
				else:
					liveArg = "sandbox"
				args = ["python", "reject_assignment.py", liveArg, dummyAssignmentId]
				subprocess.call(args)
				counter+=1
		print "Number of assignments rejected:", counter

response = ""
while (response != "y" and response != "n"):
	response = raw_input("Do you want to approve those assignments now? (y/n)\n")
	if response == "y":
		counter = 0
		workerIdsToApprove = subjectsToApprove['workerId'].values
		for i in range(0,len(workerIdsToApprove)):
			workerId = workerIdsToApprove[i]
			dummySubjectId = get_subjectId(dummyExpId, workerId)
			dummyAssignmentId = get_assignmentId(dummyExpId, dummySubjectId)
			dummyTurkSubmitTo = get_turkSubmitTo(dummyExpId, dummySubjectId)
			print "To approve - worker:", workerId, "\tassignment:", dummyAssignmentId
			if dummyTurkSubmitTo == "https://www.mturk.com" or dummyTurkSubmitTo == "https://workersandbox.mturk.com":
				if dummyTurkSubmitTo == "https://www.mturk.com":
					liveArg = "live"
				else:
					liveArg = "sandbox"
				args = ["python", "approve_assignment.py", liveArg, dummyAssignmentId]
				subprocess.call(args)
				counter+=1
		print "Number of assignments approved:", counter

