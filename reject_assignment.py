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

feedback = """As we stated on the consent form, "Payment will be given upon verification that the survey was completed and response accuracy verified". In this study we asked you to rate food items and then choose between the food items you rated. Response accuracy is determined by the consistency of your choices in the 2nd task with your ratings of foods in the 1st task. To complete the HIT satisfactorily, you must have responded to at least 150 trials in the choice task and have been consistent at least 55% of the time. Your responses did not meet at least one criteria, so your HIT has been rejected."""
args = ["aws", "mturk", "reject-assignment", "--assignment-id", assignmentId, "--requester-feedback", feedback]

if not live:
	args.append("--endpoint-url")
	args.append("https://mturk-requester-sandbox.us-east-1.amazonaws.com")

print args
subprocess.call(args)