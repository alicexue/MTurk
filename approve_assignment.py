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

feedback = "Thank you for completing this HIT!"
args = ["aws", "mturk", "approve-assignment", "--assignment-id", assignmentId, "--requester-feedback", feedback]

if not live:
	args.append("--endpoint-url")
	args.append("https://mturk-requester-sandbox.us-east-1.amazonaws.com")

subprocess.call(args)