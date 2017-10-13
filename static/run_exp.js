console.log("run_exp.js");
var expVariables; 

var recordAllKeyPresses = true;
var allKeyPresses = [];

var currTrialN = 0;

var stimuli = []; // keep track of stimuli to be display on one trial
var specialKeys = [];

var expResults = [];
var allTrials = [];
//var trialResults = {};

var expErrors = [];

/*
  * Called from script in experiment.html to initialize expVariables
  * @param {array} inputExpVariables: each element is a dictionary containing trial information
  *		elements are in the order of trials
*/
var set_trial_variables = function set(inputExpVariables) {
	expVariables = inputExpVariables
}

// canvas is the drawing platform on which stimuli are draw
var canvas = document.getElementById("myCanvas");
// set canvas width and height to that of browser window (inner excludes bookmarks bar, etc.)
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
var ctx = document.getElementById('myCanvas').getContext('2d');

var svg = document.getElementById("mySVG");
svg.setAttribute("width", (window.innerWidth).toString());
svg.setAttribute("height", (window.innerHeight).toString());

var confirmationTime = 500; // in ms
var confirmTimer;

var t1, t2;
var trialTimer;
var maxTrialDuration = 400000; // in ms

var scale;

var push_trial_info = function push_trial_info() {
	var currTrial = new trial(currTrialN, stimuli, maxTrialDuration);
	allTrials.push(currTrial);

	// send stimuli here to trialInfo, set special keys inside trialInfo

	for (var i in stimuli) {
		allTrials[currTrialN]['stimulus' + i] = stimuli[i].id;
		if (stimuli[i].key != null) {
			specialKeys.push(stimuli[i].key);

		}
	}

	console.log("Trial " + currTrialN + " " + stimulus1 + ", " + stimulus2);
	t1 = performance.now(); // start timer for this trial
	trialTimer = setTimeout(end_trial,maxTrialDuration);
	allTrials[currTrialN].trialN = currTrialN;
	allTrials[currTrialN].trialStartTime = t1;
}

/*
  * Draws individual trial display
  * Updates trial information
  * @param {python dictionary/js object} trialVariables: has keys and values for trial parameters
*/
var draw_trial_display = function draw(trialVariables) {
	// condition is a dictionary - each key can be used to set trial conditions
	var imgFolder = '/static/stim/demo/';
	stimulus1 = trialVariables['stimulus1'];
	stimulus2 = trialVariables['stimulus2'];

	var img1 = new imageStimulus(stimulus1, imgFolder + stimulus1 + ".bmp", 'u');
	img1.drawImage('LEFT');
	// img.drawImage([0, 0]);

	var img2 = new imageStimulus(stimulus2, imgFolder + stimulus2 + ".bmp", 'i');
	img2.drawImage('RIGHT');

	set_confirmation_color(BLACK);

	if (scale == null) { // set up scale for first trial
		scale = new ratingScale(0,3,1,.01);
	} else {
		scale.resetScale(); // removes current scale
	}
	scale.drawRatingScale(); // draws/redraws scale

	stimuli = [img1, img2];

	if (allTrials.length == currTrialN) {
		push_trial_info();
	}

}

var start_experiment = function start_experiment() {
	//ctx.clearRect(0,0,canvas.width,canvas.height);
	draw_trial_display(expVariables[currTrialN]); 
}

/*
  * Checks key presses and moves to next trial
  * If recordAllKeyPresses is true, gets and stores key press information
  * Checks array of special keys
  * 	- if current key pressed is in specialKey, moves to next trial
*/
var checkKeyPress = function(e) {
	var timePressed = e.timeStamp;
	t2 = timePressed;
	// should check if timepressed is after trial starts
	if (specialKeys.indexOf(e.key) > -1 && currTrialN == allTrials.length - 1) { 
		clearTimeout(trialTimer);
		clearTimeout(confirmTimer);
		// see http://keycode.info/ for key codes
		if (currTrialN < expVariables.length) {
			for (var i in stimuli) {
				if (e.key == stimuli[i].key) {
					allTrials[currTrialN].results.selected = stimuli[i].id;
				} 
			}
			allTrials[currTrialN].results.rt = t2 - t1;
			allTrials[currTrialN].results.receivedResponse = true;
			allTrials[currTrialN].results.rsp = e.key;
			allTrials[currTrialN].trialEndTime = t2;
			end_trial();
		}
	}
	// record all key presses if true
	if (recordAllKeyPresses) {
		var keyPressData = new keyPressInfo(e.key, currTrialN, timePressed, timePressed-t1);
		allKeyPresses.push(keyPressData);
	}
}

/*
  * Draws next trial 
  * Called by a timer in end_trial when maximum trial time is exceeded
  * Iterates currTrialN, clears current screen and draws next trial
  * Checks if experiment has ended (there are no more trials), and ends the experiment
*/
var next_trial = function next_trial() {
	currTrialN+=1; // iterate to next trial
	ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
	if (currTrialN < expVariables.length) {
		draw_trial_display(expVariables[currTrialN]);
	} else {
		
		var strExpResults = JSON.stringify(allTrials);
		document.getElementById('experimentResults').value = strExpResults;

		var strExpErrors = JSON.stringify(expErrors);
		document.getElementById('experimentErrors').value = strExpErrors;

		document.getElementById('exp').submit()
	}
}

// FOR BUTTON PRESSES
/*
  * Does all clean up for trial
  * Clear trialTimer
  * Get trial duration / reaction time
  * Changes color of confirmation box
  * Sets timer for confirmation and iterates to next trial at the end of confirmation
*/
var end_trial = function end_trial() {
	var color;
	clearTimeout(trialTimer);
	if (allTrials[currTrialN].results == null) {
		t2 = performance.now();
		color = RED;
		drawNextTrial = true;
		allTrials[currTrialN].results.rsp = 'None';
		allTrials[currTrialN].results.rt = t2 - t1;
		allTrials[currTrialN].trialEndTime = t2;
	} else {
		color = GREEN;
	}
	set_confirmation_color(color);
	confirmTimer = setTimeout(next_trial,confirmationTime);
}


window.addEventListener("keydown", checkKeyPress);