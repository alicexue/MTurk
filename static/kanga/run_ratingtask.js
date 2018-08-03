console.log("loaded run_ratingtask.js ");
const GREY = "#999999";

// var expVariables set in HTML

var recordAllKeyPresses = true;
var allKeyPresses = [];

var currTrialN = 0;

var expResults = [];
var allTrials = [];

// canvas is the drawing platform on which stimuli are draw
var canvas = document.getElementById("myCanvas");
// set canvas width and height to that of browser window (inner excludes bookmarks bar, etc.)
var winWidth = window.innerWidth;
var winHeight = window.innerHeight;
canvas.width = winWidth;
canvas.height = winHeight;
var ctx = canvas.getContext('2d');

var svg = document.getElementById("mySVG");
svg.setAttribute("width", winWidth.toString());
svg.setAttribute("height", winHeight.toString());

var t1, t2; 
// t1: start time of trial
// t2: end time of trial
var t1_UNIX;

var scale;

var origImgWidth = 576; // necessary for rescaling images and positioning scale
var origImgHeight = 432; // necessary for rescaling images

var widthPercent = .80;
var rescaleHeight = true;
var stimNames = ["stimulus"];

/*
 * Called in the HTML
*/
var nStimuli;
var nImagesLoaded = 0;
var startExperiment = function() {
	document.body.style.backgroundColor = GREY;
	startFirstTrial();
}

var startFirstTrial = function() {
	removeLoadingText();
	drawTrialDisplay(expVariables[currTrialN]); 
}

var inTextDisplay = false;
var inRatingDisplay = false;

var showTextDisplayTimer;
var displayTime=2000;

/*
  * Draws individual trial display
  * Updates trial information
  * Draws images for trial
  * Adds rating scale to display
  * @param {python dictionary/js object} trialVariables: has keys and values for trial parameters
*/
var instructions;
var textToRate;

var drawTrialDisplay = function(trialVariables) {
	if (trialVariables['TrialType'] == 'RateQuestion') {
		drawRatingDisplay(trialVariables);
	} else {
		drawTextDisplay(trialVariables);
	} 
}

var drawRatingDisplay = function(trialVariables) {
	// condition is a dictionary - each key can be used to set trial conditions
	inTextDisplay=false;
	inRatingDisplay=true;
	console.log(expVariables[currTrialN])
	ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
	if (allTrials.length == currTrialN) {
		pushTrialInfo();
	}

	var instructionsText;
	if (trialVariables['TrialType'] == 'RateQuestion') {
		instructionsText='Please rate how curious you are about the answer to this question:'
	} else {
		instructionsText='Please rate how satisfied you are with the answer.'
	}

	if (instructions == null) {
		instructions = new textBox(instructions, instructionsText, 22, BLACK);
	} else {
		instructions.removeText();
	}
	instructions.setText(instructionsText);
	instructions.showText(0, canvas.height/2 - 60);
	instructions.textObj.setAttribute("font-family","Gill Sans");

	var text;
	if (trialVariables['TrialType'] == 'RateQuestion') {
		text=trialVariables['Question']
		if (textToRate == null) {
			textToRate = new textBox(textToRate, text, 24, BLACK);
		} else {
			textToRate.removeText();
		}
		textToRate.setText(text);
		textToRate.showText(0, canvas.height/2 - 30);
		textToRate.textObj.setAttribute("font-family","Gill Sans");
	}

	if (scale == null) { // set up scale for first trial
		scale = new ratingScale(trialVariables['rs_min'],trialVariables['rs_max'],trialVariables['rs_tickIncrement'],trialVariables['rs_increment'],canvas.width/2,canvas.height/2 + 20, trialVariables['rs_labelNames']);
	} else {
		scale.removeScale(); // removes current scale
	}
	scale.setRatingScaleParams(trialVariables['rs_min'],trialVariables['rs_max'],trialVariables['rs_tickIncrement'],trialVariables['rs_increment'],canvas.width/2,canvas.height/2 + 20, trialVariables['rs_labelNames']);
	scale.drawRatingScale(canvas.width/2,canvas.height/2 + 20); // draws/redraws scale
	for (i=0;i<scale.tickLabels.length;i++) {
		var label = scale.tickLabels[i];
		console.log(scale.tickLabels);
		console.log(label);
		label.setAttribute("font-family","Gill Sans");
	}
}

var drawTextDisplay = function(trialVariables) {
	inRatingDisplay=false;
	inTextDisplay=true;
	ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);

	var text;
	if (trialVariables['TrialType'] == 'RateQuestion') {
		text=trialVariables['Question']
	} else {
		text=trialVariables['Answer']
	}

	if (textToRate == null) {
		textToRate = new textBox(textToRate, text, 22, BLACK);
	} else {
		textToRate.removeText();
	}
	textToRate.setText(text);
	textToRate.showText(0, canvas.height/2 - 30);
	textToRate.textObj.setAttribute("font-family","Gill Sans");

	showTextDisplayTimer = setTimeout( function() {
		inTextDisplay = false;
		textToRate.removeText();
		drawRatingDisplay(trialVariables);
	}, displayTime);
}

/*
 * Initializes set of trial information and adds to allTrials
 * Checks for any special key presses (associated with stimuli) and adds to specialKeys
 * Sets start time for trial
*/
var pushTrialInfo = function() {
	var currTrial = new trial({'trialN':currTrialN, 'Question':expVariables[currTrialN]['Question'], 'QuestionNum':expVariables[currTrialN]['QuestionNum'], 'Answer':expVariables[currTrialN]['Answer'], 'TrialType':expVariables[currTrialN]['TrialType']});
	allTrials.push(currTrial);

	t1 = performance.now(); // start timer for this trial
	t1_UNIX = Date.now();

	allTrials[currTrialN].trialStartTime = t1;
	allTrials[currTrialN].trialStartTime_UNIX = t1_UNIX;
}

/*
  * Does all clean up for trial
  * Get trial duration / reaction time
*/
var endTrial = function() {
	t2 = performance.now();
	var i;
	if (allTrials[currTrialN].rating == null) { // did not respond
		drawNextTrial = true;
		allTrials[currTrialN].rt = t2 - t1; 
		allTrials[currTrialN].receivedResponse = false;
		allTrials[currTrialN].rating = 'NaN';
		allTrials[currTrialN].trialEndTime = t2;
		allTrials[currTrialN].trialDuration = t2 - t1;
	}
	nextTrial();
}

/*
  * Clears canvas, removes scale
  * Iterates currTrialN by 1, clears current screen and calls drawTrialDisplay for next trial
  * Checks if experiment has ended (there are no more trials), and ends the experiment
*/
var nextTrial = function() {
	ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
	scale.removeScale();
	instructions.removeText();
	textToRate.removeText();
	currTrialN+=1; // iterate to next trial
	if (currTrialN < expVariables.length) {
		drawTrialDisplay(expVariables[currTrialN]);
	} else {
		var strExpResults = JSON.stringify(allTrials);
		document.getElementById('experimentResults').value = strExpResults;

		drawLoadingText();

		document.getElementById('exp').submit()
	}
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
	canvas.width = winWidth;
	canvas.height = winHeight;
	ctx = document.getElementById('myCanvas').getContext('2d');
	svg.setAttribute("width", winWidth.toString());
	svg.setAttribute("height", winHeight.toString());

	// remove blanks/alert text if exist
	if (svg.contains(blankScreenCover)) {
		svg.removeChild(blankScreenCover);
	}
	if (svg.contains(alertText)) {
		svg.removeChild(alertText);
	}

	drawTrialDisplay(expVariables[currTrialN]);
}

window.onresize = function() {
	resizeWindow();
}
