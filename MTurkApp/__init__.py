from flask import Flask, render_template, request, session
from flask import redirect, url_for
from flask import jsonify

app = Flask(__name__)

import MTurkApp.flask_core
import MTurkApp.flask_foodchoicestudies
import MTurkApp.flask_foodchoicestudies_instructions

"""
It is assumed that all tasks are preceded by a demo (when moving onto the next task, always reroute to a demo instructions page
- see code for clarification)

1. Define the order in which tasks are to be completed in your experiment (see MDMMT_taskOrder)
2. Add variable from step 1 to the dictionary expTaskOrders. In the key-value pair, the variable from step 1
should be the value and the experiment abbreviation/name should be the key.

Each task has 3 associated functions - suppose our task is called "auction"
	1) function that runs the task (also runs demo) (auction(expId))
	2) function for task instructions
	3) function for instructions of task's demo
	Notes:
		Each function must take expId as a parameter and each function must contain a variable that defines the name of the task

"""