import pandas as pd
import csv
import os
import sys
import subprocess
from manage_subject_info import *
from manage_data_quality import *

"""
	Get list of assignments that don't meet criteria and reject
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

dataDir = _thisDir + '/' + expId + '/'
summaryFile = dataDir + '/' + expId + '_data_quality_summary.csv'

minAccuracy = .55
minResponses = 150

subprocess.call(["python", "check_data_quality.py", expId])

df = pd.read_csv(summaryFile)
notMeetAccuracy = df.loc[df['percentAccuracy'] < minAccuracy]['subjectId']
notMeetMinRsps = df.loc[df['nResponses'] < minResponses]['subjectId']

subjectIdsToReject = []
assignmentIdsToReject = []
turkSubmitLinks = []
for subjectId in notMeetAccuracy:
	if subjectId not in subjectIdsToReject:
		subjectIdsToReject.append(subjectId)
		asgmtId = get_assignmentId(expId, subjectId)
		assignmentIdsToReject.append(asgmtId)
		link = get_turkSubmitTo(expId, subjectId)
		turkSubmitLinks.append(link)

for subjectId in notMeetMinRsps:
	if subjectId not in subjectIdsToReject:
		subjectIdsToReject.append(subjectId)
		asgmtId = get_assignmentId(expId, subjectId)
		assignmentIdsToReject.append(asgmtId)
		link = get_turkSubmitTo(expId, subjectId)
		turkSubmitLinks.append(link)

print subjectIdsToReject
print assignmentIdsToReject

print "Number of Assignments to Reject:", len(assignmentIdsToReject)

response = ""
while (response != "y" and response != "n"):
	response = raw_input("Do you want to reject all assignments now? (y/n)\n")
	if response == "y":
		counter = 0
		for i in range(0,len(assignmentIdsToReject)):
			assignmentId = assignmentIdsToReject[i]
			subjectId = subjectIdsToReject[i]
			submitLink = turkSubmitLinks[i]

			if submitLink == "https://www.mturk.com/mturk" or submitLink == "https://workersandbox.mturk.com/mturk":
				if submitLink == "https://www.mturk.com/mturk":
					liveArg = "live"
				else:
					liveArg = "sandbox"
				args = ["python", "reject_assignment.py", liveArg, assignmentId]
				subprocess.call(args)
				update_assignment_status(expId, subjectId, "Rejected")	
				counter+=1
		print "Number of assignments rejected:", counter
