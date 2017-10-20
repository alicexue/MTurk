console.log("loaded run_auction.js");
var expVariables; 

var recordAllKeyPresses = true;
var allKeyPresses = [];

var currTrialN = 0;

var stimuli = []; // keep track of stimuli to be display on one trial
var specialKeys = [];

var expResults = [];
var allTrials = [];

var expErrors = [];



window.onload = get_ip;
var get_ip = function get_ip(e) {
	console.log("hello")
	$.getJSON("https://api.ipify.org/?format=json", function(e) {
	    console.log(e.ip);
	});
}


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
var winWidth = window.innerWidth;
var winHeight = window.innerHeight;
canvas.width = winWidth;
canvas.height = winHeight;
var ctx = document.getElementById('myCanvas').getContext('2d');

var svg = document.getElementById("mySVG");
svg.setAttribute("width", (winWidth).toString());
svg.setAttribute("height", (winHeight).toString());

var needToResizeWindow = false;

window.onresize = function() {
	resizeWindow();
}

var resizeWindow = function resizeWindow() {
	var winWidth = window.innerWidth;
	var winHeight = window.innerHeight;
	canvas.width = winWidth;
	canvas.height = winHeight;
	ctx = document.getElementById('myCanvas').getContext('2d');
	svg.setAttribute("width", (winWidth).toString());
	svg.setAttribute("height", (winHeight).toString());
	draw_trial_display(expVariables[currTrialN]);
}

var confirmationTime = 500; // in ms
var confirmTimer;

var t1, t2;
var trialTimer;
var maxTrialDuration = 400000; // in ms

var scale;

var push_trial_info = function push_trial_info() {
	var currTrial = new trial(currTrialN, stimuli, maxTrialDuration, ['rt','rsp']);
	allTrials.push(currTrial);

	console.log(currTrial)
	console.log(allTrials)

	// send stimuli here to trialInfo, set special keys inside trialInfo

	for (var i in stimuli) {
		if (stimuli[i].key != null) {
			specialKeys.push(stimuli[i].key);

		}
	}

	t1 = performance.now(); // start timer for this trial
	trialTimer = setTimeout(end_trial,maxTrialDuration);

	allTrials[currTrialN].trialStartTime = t1;

	for (var i in stimuli) {
		allTrials[currTrialN]['stimulus' + parseInt(i+1,10)] = stimuli[i].id;
	}
	
}

/*
  * Draws individual trial display
  * Updates trial information
  * @param {python dictionary/js object} trialVariables: has keys and values for trial parameters
*/
var draw_trial_display = function draw_trial_display(trialVariables) {
	// condition is a dictionary - each key can be used to set trial conditions

	/*
	if (needToResizeWindow) {
		resizeWindow();
	}
	*/

	var imgFolder = '/static/stim/demo/';
	var stimulus1 = trialVariables['stimulus1'];

	console.log("Trial " + currTrialN + " " + stimulus1);

	var img1 = new imageStimulus(stimulus1, imgFolder + stimulus1 + ".bmp", null);
	img1.drawImage('CENTER');

	stimuli = [img1];

	if (allTrials.length == currTrialN) {
		push_trial_info();
	}

	if (scale == null) { // set up scale for first trial
		scale = new ratingScale(0,3,1,.01);
	} else {
		scale.resetScale(); // removes current scale
	}
	scale.drawRatingScale(); // draws/redraws scale
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
			allTrials[currTrialN].receivedResponse = true;
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

/*
  * Does all clean up for trial
  * Clear trialTimer
  * Get trial duration / reaction time
  * Changes color of confirmation box
  * Sets timer for confirmation and iterates to next trial at the end of confirmation
*/
var end_trial = function end_trial() {
	var i;
	for (i=0;i<stimuli.length;i++) {
		allTrials[currTrialN]['stimulus' + parseInt(i+1,10) + 'Loaded'] = stimuli[i].loaded;
	}

	var color;
	clearTimeout(trialTimer);
	if (allTrials[currTrialN].results == null) { // did not respond
		t2 = performance.now();
		drawNextTrial = true;
		allTrials[currTrialN].results.rsp = 'None';
		allTrials[currTrialN].results.rt = t2 - t1;
		allTrials[currTrialN].trialEndTime = t2;
		allTrials[currTrialN].trialDuration = t2 - t1;
	}
	confirmTimer = setTimeout(next_trial,confirmationTime);
}


window.addEventListener("keydown", checkKeyPress);