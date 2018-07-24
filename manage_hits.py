import subprocess
import sys
import time

# reference: https://docs.aws.amazon.com/cli/latest/reference/mturk/index.html#cli-aws-mturk

instructions = """ 
OPTIONS:
(1) list all HITs:\n
\t 2nd arg: live or sandbox\n
\t 3rd arg: list_hits (Note underscore not hyphen)\n
(2) perform operation on HIT:\n 
\t2nd arg: live or sandbox\n
\t3rd arg: HIT id\n
\t4th arg: 'list_asgmts' or 'expire' or 'delete'
"""

args = ["aws", "mturk"]

if len(sys.argv) == 3:
	if sys.argv[2] == "list_hits":
		if sys.argv[1] == "live":
			endpoint = []
		elif sys.argv[1] == "sandbox":
			endpoint = ["--endpoint-url", "https://mturk-requester-sandbox.us-east-1.amazonaws.com"]
		else:
			print "Invalid args"
			print instructions
			sys.exit()
		args.append("list-hits")
		args.append("--output")
		args.append("table")
		args.append("--max-results")
		args.append("20")
		args.append("--query")
		args.append('HITs[].{"1. HITId": HITId, "2. Title": Title, "3. Status":HITStatus, "4. Creation": CreationTime, "5. Expiration": Expiration, "6. MaxAsgmts": MaxAssignments, "7. #AsgmtAvail" : NumberOfAssignmentsAvailable, "8. #AsgmtReviewed": NumberOfAssignmentsCompleted}')
		args+=endpoint
		print "\nCurrent UNIX time: ", time.time()
		print "Note: By default the table only prints the 20 most recent HITs"
		subprocess.call(args)
		sys.exit()
	else:
		print "Invalid arguments"
		print instructions
		sys.exit()
	
if len(sys.argv) < 4:
	print "Not enough arguments"
	print instructions
	sys.exit()

if sys.argv[1] != "live" and sys.argv[1] != "sandbox":
	print "2nd arg must be live or sandbox"
	sys.exit()

live = sys.argv[1] == "live"
hit_id = sys.argv[2] 
op_request = sys.argv[3]

if op_request == "expire":
	operation = "update-expiration-for-hit"
elif op_request == "delete":
	operation = "delete-hit"
elif op_request == "list_asgmts":
	operation = "list-assignments-for-hit"
else:
	print "Invalid op_request argument"
	print instructions
	sys.exit()

args.append(operation)
args.append("--hit-id")
args.append(hit_id)

if op_request == "expire":
	args.append("--expire-at")
	args.append("0")
elif op_request == "list_asgmts":
	args.append("--query")
	args.append("Assignments[].{AssignmentId: AssignmentId, Status: AssignmentStatus, WorkerId: WorkerId}")
	args.append("--output")
	args.append("table")
	args.append("--max-results")
	args.append("200")

if not live:
	args.append("--endpoint-url")
	args.append("https://mturk-requester-sandbox.us-east-1.amazonaws.com")

print args
subprocess.call(args)
