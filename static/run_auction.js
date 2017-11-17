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

/*
  * Called from script in experiment.html to initialize expVariables
  * @param {array} inputExpVariables: each element is a dictionary containing trial information
  *		elements are in the order of trials
*/
var setTrialVariables = function setTrialVariables(inputExpVariables) {
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
svg.setAttribute("width", winWidth.toString());
svg.setAttribute("height", winHeight.toString());

var t1, t2;
var trialTimer;
var maxTrialDuration = 400000; // in ms

var scale;

var origImgWidth = 576; // necessary for rescaling images and positioning scale
var origImgHeight = 432; // necessary for rescaling images

/*
 * Called in the HTML
*/
var startExperiment = function startExperiment() {
	drawTrialDisplay(expVariables[currTrialN]); 
}

/*
  * Draws individual trial display
  * Updates trial information
  * @param {python dictionary/js object} trialVariables: has keys and values for trial parameters
*/
var drawTrialDisplay = function drawTrialDisplay(trialVariables) {
	// condition is a dictionary - each key can be used to set trial conditions
	ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
	var imgFolder = '/static/stim/demo/';
	var stimulus1 = trialVariables['stimulus1'];

	console.log("Trial " + currTrialN + " " + stimulus1);

	var widthPercent = 0.80;

	var img1 = new imageStimulus(stimulus1, imgFolder + stimulus1 + ".bmp", null, widthPercent, true);
	img1.drawImage('CENTER');

	stimuli = [img1];

	if (allTrials.length == currTrialN) {
		pushTrialInfo();
	}

	var scaledImgDimensions = rescaleImgSize([origImgWidth,origImgHeight], widthPercent);
	var scaledHeight = scaledImgDimensions[1];

	if (scale == null) { // set up scale for first trial
		scale = new ratingScale(0,3,1,.01,canvas.width/2,canvas.height/2 + scaledHeight/2 + 10, ["$0", "$1", "$2", "$3"]);
	} else {
		scale.resetScale(); // removes current scale
	}
	scale.drawRatingScale(canvas.width/2,canvas.height/2 + scaledHeight/2 + 10); // draws/redraws scale
}


/*
 * Initializes set of trial information and adds to allTrials
 * Checks for any special key presses (associated with stimuli) and adds to specialKeys
 * Gets start time of trial
*/
var pushTrialInfo = function pushTrialInfo() {
	var currTrial = new trial(currTrialN, stimuli, maxTrialDuration, ['rt','rating']);
	allTrials.push(currTrial);

	// send stimuli here to trialInfo, set special keys inside trialInfo
	var i;
	for (i=0;i<stimuli.length;i++) {
		if (stimuli[i].key != null) {
			specialKeys.push(stimuli[i].key);
		}
	}

	t1 = performance.now(); // start timer for this trial
	trialTimer = setTimeout(endTrial,maxTrialDuration);

	allTrials[currTrialN].trialStartTime = t1;

	for (var i in stimuli) {
		allTrials[currTrialN]['stimulus' + parseInt(i+1,10)] = stimuli[i].id;
	}
}

/*
  * Does all clean up for trial
  * Clear trialTimer
  * Get trial duration / reaction time
*/
var endTrial = function endTrial() {
	var i;
	for (i=0;i<stimuli.length;i++) {
		allTrials[currTrialN]['stimulus' + parseInt(i+1,10) + 'Loaded'] = stimuli[i].loaded;
	}
	t2 = performance.now()
	clearTimeout(trialTimer);
	if (allTrials[currTrialN].results == null || t2 - t1 > maxTrialDuration) { // did not respond
		drawNextTrial = true;
		allTrials[currTrialN].results.rt = t2 - t1;
		allTrials[currTrialN].trialEndTime = t2;
		allTrials[currTrialN].trialDuration = t2 - t1;
	}
	nextTrial();
}

/*
  * Draws next trial 
  * Called by a timer in endTrial when maximum trial time is exceeded
  * Iterates currTrialN, clears current screen and draws next trial
  * Checks if experiment has ended (there are no more trials), and ends the experiment
*/
var nextTrial = function nextTrial() {
	ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
	scale.resetScale();
	currTrialN+=1; // iterate to next trial
	if (currTrialN < expVariables.length) {
		drawTrialDisplay(expVariables[currTrialN]);
	} else {
		var strExpResults = JSON.stringify(allTrials);
		document.getElementById('experimentResults').value = strExpResults;

		var strExpErrors = JSON.stringify(expErrors);
		document.getElementById('experimentErrors').value = strExpErrors;

		document.getElementById('exp').submit()
	}
}


/*
 * Called when change in window size is detected
 * Changes width and height of canvas and svg to that of window
 * If window was previously too small (has blank and alertText)
 * 	 then these are removed
 * Calls on drawTrialDisplay to redraw display according to new window size
*/
var resizeWindow = function resizeWindow() {
	var winWidth = window.innerWidth;
	var winHeight = window.innerHeight;
	canvas.width = winWidth;
	canvas.height = winHeight;
	ctx = document.getElementById('myCanvas').getContext('2d');
	svg.setAttribute("width", winWidth.toString());
	svg.setAttribute("height", winHeight.toString());

	// remove blanks/alert text if exist
	if (svg.contains(blank)) {
		svg.removeChild(blank);
	}
	if (svg.contains(alertText)) {
		svg.removeChild(alertText);
	}

	drawTrialDisplay(expVariables[currTrialN]);
}

window.onresize = function() {
	resizeWindow();
}
