import sys
import subprocess

#python reject_assignments.py sandbox assignmentId

if len(sys.argv) < 3:
	print "2nd arg: live or sandbox"
	print "3rd arg: assignmentId"
	sys.exit()

if sys.argv[1] != "live" and sys.argv[1] != "sandbox":
	print "2nd arg must be live or sandbox"
	sys.exit()

live = sys.argv[1] == "live"
assignmentId = sys.argv[2]

feedback = """As we stated on the consent form, 'Compensation is contingent upon response completion. You are required to complete at least 90% of the task or the HIT will be rejected and you will not receive compensation. To be specific, we will check if responses were made during the task and ensure that a response was made on at least 90% of trials.' According to our records, you did not make any responses in 2 of the tasks in this study, so we have rejected your assignment. Please email us if you believe this is a mistake."""
args = ["aws", "mturk", "reject-assignment", "--assignment-id", assignmentId, "--requester-feedback", feedback]

if not live:
	args.append("--endpoint-url")
	args.append("https://mturk-requester-sandbox.us-east-1.amazonaws.com")

subprocess.call(args)