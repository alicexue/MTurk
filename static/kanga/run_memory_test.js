console.log("loaded kanga.js ");
const WHITE = "#ffffff";
const GREY = "#999999";
const LIGHTBLUE = "#99ccff";

// var expVariables set in HTML
var currTrialN = 0;

var allTrials = [];

/* DISPLAY */

/* TIMING */
var t1, t2;

/*
 * Called in the HTML
*/
var endExperiment = false;
var startExperiment = function() {
	document.body.style.backgroundColor = GREY;
	drawTriviaDisplay(expVariables[currTrialN]); 
}

/*
  * Draws individual trial display
  * Updates trial information
  * Draws images for trial
  * @param {python dictionary/js object} trialVariables: has keys and values for trial parameters
*/
var drawTriviaDisplay = function(trialVariables) {
	question = trialVariables['Question']

	if (allTrials.length == currTrialN) {
		pushTrialInfo();
	}
	allTrials[currTrialN]['Question'] = question;

	var fontSize = window.innerWidth * 0.03;

	var questionText = document.getElementById('html_text'); 
	questionText.innerHTML = question;
	questionText.style.fontFamily = "Gill Sans";
	questionText.style.fontSize = "xx-large";
	questionText.style.paddingTop = (window.innerWidth/2 - window.innerHeight/2).toString() + "px";
	questionText.style.lineHeight = "1.2";
}

/*
 * Initializes set of trial information and adds to allTrials
 * Checks for any special key presses (associated with stimuli) and adds to specialKeys
 * Sets start time for trial
 * Sets timer for trial
*/
var pushTrialInfo = function() {
	trialVariables = expVariables[currTrialN];
	trialVariables['C_Trial'] = currTrialN;
	var currTrial = new trial(trialVariables);
	allTrials.push(currTrial);
	
	t1 = performance.now(); // start timer for this trial
	allTrials[currTrialN].C_QPresent = t1;
}

var registerResponse = function() {
	var inputBox = document.getElementById('response');
	var response = inputBox.value;
	if (response != '') {
		inputBox.value = '';
		allTrials[currTrialN]['Response'] = response;
		nextTrial();
	}
}

/*
  * Clears canvas, removes scale
  * Iterates currTrialN by 1, clears current screen and calls drawTrialDisplay for next trial
  * Checks if experiment has ended (there are no more trials), and ends the experiment
*/
var nextTrial = function() {
	allTrials[currTrialN].C_TrialEnd = performance.now();
	currTrialN+=1; // iterate to next trial
	// double check performance.now()
	if (endExperiment || performance.now() > maxExperimentDuration || currTrialN >= expVariables.length) {
		var strExpResults = JSON.stringify(allTrials);
		document.getElementById('experimentResults').value = strExpResults;
		console.log(strExpResults);

		drawLoadingText();

		document.getElementById('exp').submit()
	} else { // experiment has not ended 
		drawTriviaDisplay(expVariables[currTrialN]);
	} 
}

var keyIsDown = false; // keep track if key is still being held down - take one key press at a time
var checkKeyPress = function(e) {
	var timePressed = e.timeStamp; // does not seem to be compatible with all browsers - may get UNIX time instead of time relative to trial start
	var timePressed_UNIX = Date.now();
	if (keyIsDown == false && timePressed > t1) { 
		keyIsDown = true;
		t2 = timePressed;
		t2_UNIX = timePressed_UNIX;
		// should check if timepressed is after trial starts
		if (e.key=='Enter' && currTrialN == allTrials.length - 1) { 
			if (currTrialN < expVariables.length) {
				allTrials[currTrialN].rt = t2 - t1;
				allTrials[currTrialN].rt_UNIX = t2_UNIX - t1_UNIX;
				allTrials[currTrialN].receivedResponse = true;
				allTrials[currTrialN].rsp = e.key;

				registerResponse();
				console.log('registering response');
			}
		}
	}
}

var setKeyUp = function(e) {
	keyIsDown = false;
}

/*
 * Called when change in window size is detected
 * Changes width and height of canvas and svg to that of window
 * If window was previously too small (has blankScreenCover and alertText)
 * 	 then these are removed
 * Calls on drawTrialDisplay to redraw display according to new window size
*/
var resizeWindow = function() {
	var winWidth = window.innerWidth;
	var winHeight = window.innerHeight;
	drawTriviaDisplay(expVariables[currTrialN]);
}

window.onresize = function() {
	resizeWindow();
}

window.addEventListener("keypress", checkKeyPress);
