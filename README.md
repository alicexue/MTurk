# Web App to Run Studies on Amazon Mechanical Turk

One study is up and running [here](http://calkins.psych.columbia.edu/MDMMT).

This web app uses the Flask framework. All of the middleware is in python. 

Studies are run in the browser with Javascript. HTML canvases are used to display images while svg elements are used for text and interactive components. 

Data files are stored using python pandas as csv files.

## References
Javascript references:
[Javascript](https://developer.mozilla.org/en-US/docs/Web/JavaScript)

Flask references:
[Flask blueprints](http://flask.pocoo.org/docs/1.0/blueprints/) and [structure](http://exploreflask.readthedocs.io/en/latest/blueprints.html#where-do-you-put-them)

MTurk references:
[MTurk Concepts](https://docs.aws.amazon.com/AWSMechTurk/latest/RequesterUI/mechanical-turk-concepts.html)
[AWS MTurk Commands](https://docs.aws.amazon.com/cli/latest/reference/mturk/index.html#cli-aws-mturk)
[FAQ](https://requester.mturk.com/help/faq)
[HIT Lifecycle](https://blog.mturk.com/overview-lifecycle-of-a-hit-e6956b4f3bb1)

Other MTurk references:
[Code samples for creating external HIT](https://github.com/aws-samples/mturk-code-samples)


## Get the task running in Javascript first:
- See the sample javascript experiment.
- Javascript files are stored in the static directory, as are images.
- I use the HTML canvas element to display images. Text can be displayed as an HTML or svg element (see textBox in components.js). "Buttons" on the screen and rating scales can be created using svg (see components.js)

## HTML
- All HTML files are stored in the templates directory. 
- Some project-specific html files are in their own folder in the templates directory.
- To render an HTML file in a project specific folder, use something like this: 'foodchoicestudies/auction.html'

## Add the task as a blueprint to the python code:
1. Create a new directory under MTurk
2. Add an empty __init__.py file to that directory. This allows the directory to be recognized by python as a package. 
3. Add your flask/python files to that directory.
4. Create a blueprint by making the following changes
For tasks.py, for example, you would add the line 
tasks = Blueprint('tasks',  __name__, url_prefix='/<expId>')
The routes should look like @tasks.route("/auction", methods = ["GET","POST"]) instead of @app.route("/auction", methods = ["GET","POST"])
Specifying the url_prefix makes the url /<expId>/auction instead of just /auction
5. In app.py, add and register your Blueprint. For example - 
from foodchoicestudies.tasks import tasks 
app = Flask(__name__)
app.register_blueprint(tasks)

## Notes on MTurk:
- MTurk passes workerId, assignmentId, hitId, and turkSubmitTo as arguments in the URL. I also pass live to see if the current HIT is the in the sandbox or not. (Note: These arguments are all passed as strings, not booleans.)

## Uploading to the server:
1. Get access to the server
2. Make sure everything works locally when you run python app.py
3. Make sure app.debug is set to False, not True
4. When live=True in the URL, make sure that the URL is https://www.mturk.com/mturk/externalSubmit and not https://workersandbox.mturk.com/mturk/externalSubmit (the former URL is for submitting real HITs while the latter URL is for submitting HITs in the sandbox)
5. Upload all the files to the server - don't overwrite the data folder! The MTurk files are located at /projectAlice/MTurk
6. Restart the server 

## Working with MTurk:
1. Add yourself as an aws user under the lab account, link [here](https://console.aws.amazon.com/iam/home?#/users)
- This allows you to create HITs, approve and reject assignments, etc.
2. Install [AWS Command Line Interface](https://docs.aws.amazon.com/cli/latest/userguide/installing.html)
3. [Configure](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html) your settings with your credentials

## Creating HITs and Testing in the MTurk Sandbox:
- You can use create_hit.py to create a live HIT or a HIT in the sandbox. You can do testing in the sandbox and see what the preview looks like to the worker, make sure that everything works, etc.
- create_hit.py lists some worker qualifications. You can remove or add qualifications. See [this](https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMechanicalTurkRequester/Concepts_QualificationsArticle.html) and [this](https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_QualificationDataStructureArticle.html) for reference
- create_hit.py uses my_external_question.xml. See [this](https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_ExternalQuestionArticle.html) for more information. Note that my_external_question.xml is changed by create_hit.py and passes /<expId>?live=True or /<expId>?live=False as the url, depending on the parameters, assuming that the home page for the study is at /<expId> The element ExternalURL is the url for the webpage that is embedded in MTurk for the HIT. FrameHeight, in pixels, refers to how tall the frame should be. 

## Running a live HIT:
- Keep in mind that you can run a small sample first and then increase the number of assignments for the HIT (although you should start at a minimum of 10 - if you start with <10 assignments for a HIT, Amazon won't let you increase the number of assignments to >10 because of their 20% fee for HITs with >10 assignments).
- Make sure to monitor the email account in case workers run into any issues. 

## Payment:
- Payment for an assignment is detailed in create_hit.py
- Go [here](https://requester.mturk.com/account) to add money for prepaid HITs
- Pricing details are [here](https://requester.mturk.com/pricing)

## Approving and rejecting assignments:
- To approve or reject individual assignments, you can use approve_assignment.py and reject_assignment.py
- retrieve_and_approve_hits.py approves all assignments that have not yet been reviewed 
- get_assignments_to_reject.py is an example script that does preliminary analysis of each subject's data and checks whether the subject's assignment should be rejected or not.

## Setting up a dummy HIT:
- To compensate workers who were unable to be paid through MTurk (if there's a server error, for example), you can set up a dummy HIT. Overwrite the first column of worker IDs in dummyHIT_subjects_to_compensate.csv with a list of workers IDs for workers you need to compensate. Go through create_dummy_hit.py to set the payment amount, description, etc. 

## After running an MTurk study:
- Back up all of your data
- Make sure that on the server, *_subject_worker_ids.csv gets saved as a password protected file.
--- 1. Open the csv file in Microsoft Excel
--- 2. Go to File -> Passwords... and set a password for the file. (Write the password down somewhere! You can't recover it.)

