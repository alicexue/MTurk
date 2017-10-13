from flask import Flask,render_template,request,session
from flask import redirect,url_for
from psychopy import data
import json
import random
import csv, os, sys
import ast
from utils import * # importing * allows you to use methods from utils.py without calling utils.method_name
import store_data

_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)

app = Flask(__name__)

@app.route("/experiment", methods = ["GET","POST"])
def experiment():
	if request.method == "GET":
		### set experiment conditions here and pass to experiment.html 
		# trialVariables should be an array of dictionaries 
		# each element of the array represents the condition for one trial
		# set the variable conditions to the array of conditions
		stimuli1 = get_stimuli()
		stimuli2 = get_stimuli()
		random.shuffle(stimuli1)
		random.shuffle(stimuli2)

		expVariables = [] # array of dictionaries

		for i in range(0,len(stimuli1)):
			expVariables.append({"stimulus1":stimuli1[i]})
			#expVariables.append({"stimulus1":stimuli1[i],'stimulus2':stimuli2[i]})

		return render_template('experiment.html',expVariables=expVariables)
	else:
		expResults = json.loads(request.form['experimentResults'])
		expErrors = json.loads(request.form['experimentErrors'])

		store_data.organize_data(expResults, 'auction_data.csv', 'auction_stimuli.csv');

		return redirect(url_for('thankyou'))

@app.route("/auction", methods = ["GET","POST"])
def auction():
	if request.method == "GET":
		### set experiment conditions here and pass to experiment.html 
		# trialVariables should be an array of dictionaries 
		# each element of the array represents the condition for one trial
		# set the variable conditions to the array of conditions
		stimuli1 = get_stimuli()
		random.shuffle(stimuli1)

		expVariables = [] # array of dictionaries

		for i in range(0,len(stimuli1)):
			expVariables.append({"stimulus1":stimuli1[i]})

		return render_template('auction.html',expVariables=expVariables)
	else:
		expResults = json.loads(request.form['experimentResults'])
		expErrors = json.loads(request.form['experimentErrors'])
		
		store_data.organize_data(expResults, 'choice_data.csv', 'choice_stimuli.csv');
		
		return redirect(url_for('choicetask'))


@app.route("/choicetask", methods = ["GET","POST"])
def choicetask():
	if request.method == "GET":
		### set experiment conditions here and pass to experiment.html 
		# trialVariables should be an array of dictionaries 
		# each element of the array represents the condition for one trial
		# set the variable conditions to the array of conditions
		stimuli1 = get_stimuli()
		random.shuffle(stimuli1)
		stimuli2 = get_stimuli()
		random.shuffle(stimuli2)

		stim1Bids = [];
		stim2Bids = [];

		stimBidDict = get_bid_responses(_thisDir + '/data/auction_data.csv')

		for stim in stimuli1:
			stim1Bids.append(stimBidDict[stim]);

		for stim in stimuli2:
			stim2Bids.append(stimBidDict[stim]);

		expVariables = [] # array of dictionaries

		for i in range(0,len(stimuli1)):
			expVariables.append({"stimulus1":stimuli1[i],"stimulus2":stimuli2[i],"stim1Bid":stim1Bids[i],"stim2Bid":stim2Bids[i]})

		return render_template('choicetask.html',expVariables=expVariables)
	else:
		expResults = json.loads(request.form['experimentResults'])
		expErrors = json.loads(request.form['experimentErrors'])
		keys = expResults[0].keys()

		if not os.path.exists('data'):
			os.makedirs('data')

		header = []
		stimuliHeader = []
		for key in keys:
			if key == 'results':
				resultKeys = expResults[0]['results'].keys()
				for resultKey in resultKeys:
					header.append(resultKey)

			elif key != 'stimuli':
				header.append(key)
			else:
				stimuli = expResults[0]['stimuli']
				stimulusKeys = expResults[0]['stimuli'][0].keys()
				for i in range(0,len(stimuli)):
					for stimulusKey in stimulusKeys:
						stimuliHeader.append('stimulus'+str(i+1)+'_'+stimulusKey)

		allTrialOutput = []
		allStimuliInfo = []
		for trial in expResults:
			trialOutput = []
			stimuliInfo = []
			for key in keys:
				if key == 'results':
					results = trial['results']
					for resultKey in results:
						trialOutput.append(str(results[resultKey]))

				elif key != 'stimuli':
					trialOutput.append(str(trial[key]))
				else:
					stimuli = trial['stimuli']
					for i in range(0,len(stimuli)):
						stimulus = stimuli[i]
						for stimulusKey in stimulusKeys:
							stimuliInfo.append(str(stimulus[stimulusKey]))
			allTrialOutput.append(trialOutput)
			allStimuliInfo.append(stimuliInfo)

		with open(_thisDir + '/data/' + 'test_data.csv', 'wb') as csvfile:
			writer = csv.writer(csvfile)
			writer.writerow(header)

			for trial in allTrialOutput:
				writer.writerow(trial)

		with open(_thisDir + '/data/' + 'test_data_stimuli.csv', 'wb') as csvfile:
			writer = csv.writer(csvfile)
			writer.writerow(stimuliHeader)

			for trialStimuli in allStimuliInfo:
				writer.writerow(trialStimuli)

		return redirect(url_for('thankyou'))

@app.route("/", methods = ["GET","POST"])
def instructions():
	if request.method == "GET":
		return render_template('instructions.html')
	else:
		return redirect(url_for('auction'))

@app.route("/thankyou", methods = ["GET"])
def thankyou():
	return render_template('thankyou.html')

if __name__ == "__main__":
	app.debug = True
	app.secret_key="Don't store this on github"
	app.run(host = '0.0.0.0', port = 8000, threaded=True)
