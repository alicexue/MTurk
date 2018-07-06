console.log("loaded run_stimchar.js ");

// var expVariables set in HTML

var recordAllKeyPresses = true;
var allKeyPresses = [];

var currTrialN = 0;

var stimuli = []; 
var specialKeys = [];

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

var origImgWidth = 600; // necessary for rescaling images and positioning scale
var origImgHeight = 600; // necessary for rescaling images

var widthPercent = .80;
var rescaleHeight = true;
var stimNames = ["stimulus"];

var questionTimer;
var questionDisplayDuration=2000;

const GREY = "#808080";

/*
 * Called in the HTML
*/
var nStimuli;
var nImagesLoaded = 0;
var startExperiment = function() {
	nStimuli = expVariables.length;
	drawLoadingText();
	generateOffScreenCanvases(drawStimuliToCanvas,'');
}

var drawStimuliToCanvas = function(trialVariables, trialN, canvasCtx) {
	var position = "CENTER";
	var stimulus = trialVariables['stimulus'];
	var fullStimName = trialVariables['fullStimName']
	var img1 = new imageStimulus(stimulus, stimFolder + fullStimName, 'NaN', widthPercent, rescaleHeight);
	img1.drawImage(position, trialN, canvasCtx);
	trialStimuli = [img1];
	stimuli[trialN] = trialStimuli;
}


var startFirstTrial = function() {
	removeLoadingText();
	drawQuestionDisplay(); 
}

/*
  * Draws individual trial display
  * Updates trial information
  * Draws images for trial
  * Adds rating scale to display
  * @param {python dictionary/js object} trialVariables: has keys and values for trial parameters
*/
var scale;
var instructions;
var leftRating;
var middleRating;
var rightRating;
var drawTrialDisplay = function() {
	trialVariables = expVariables[currTrialN];
	clearTimeout(questionTimer);
	// condition is a dictionary - each key can be used to set trial conditions
	ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
	if (question!=null) {
		question.removeText();
	}
	var stimulus = trialVariables['stimulus'];

	var trialCanvas = document.getElementById("trial"+currTrialN);
	var trialCtx = trialCanvas.getContext('2d');
	if (trialCanvas.width == canvas.width && trialCanvas.height == canvas.height) {
		ctx.drawImage(trialCanvas, 0, 0, canvas.width, canvas.height);
	} else {
		drawStimuliToCanvas(trialVariables, currTrialN, ctx)
	}

	if (allTrials.length == currTrialN) {
		pushTrialInfo();
	}

	var scaledImgDimensions = rescaleImgSize([origImgWidth,origImgHeight], widthPercent, rescaleHeight);
	var scaledHeight = scaledImgDimensions[1];

	instructionsText=trialVariables['question']
	if (instructions == null) {
		instructions = new textBox(instructions, instructionsText, 20, BLACK);
	} else {
		instructions.removeText();
	}
	instructions.setText(instructionsText);
	instructions.showText(0, canvas.height/2 - scaledHeight/2 - 30);

	if (scale == null) { // set up scale for first trial
		scale = new ratingScale(trialVariables['rs_min'],trialVariables['rs_max'],trialVariables['rs_tickIncrement'],trialVariables['rs_increment'],canvas.width/2,canvas.height/2 + scaledHeight/2 + 10, trialVariables['rs_labelNames']);
	} else {
		scale.removeScale(); // removes current scale
	}
	scale.setRatingScaleParams(trialVariables['rs_min'],trialVariables['rs_max'],trialVariables['rs_tickIncrement'],trialVariables['rs_increment'],canvas.width/2,canvas.height/2 + scaledHeight/2 + 10, trialVariables['rs_labelNames']);
	scale.drawRatingScale(canvas.width/2,canvas.height/2 + scaledHeight/2 + 10, drawIndicatorLine = true, canvas.width*3/4); // draws/redraws scale
	
	leftRatingText=trialVariables['leftRatingText']
	if (leftRating == null) {
		leftRating = new textBox(leftRating, leftRatingText, 20, BLACK);
	} else {
		leftRating.removeText();
	}
	leftRating.setText(leftRatingText);
	leftRating.showText(0 - scale.ratingBarWidth/2, canvas.height/2 + scaledHeight/2 + 65);

	middleRatingText=trialVariables['middleRatingText']
	if (middleRating == null) {
		middleRating = new textBox(middleRating, middleRatingText, 20, BLACK);
	} else {
		middleRating.removeText();
	}
	middleRating.setText(middleRatingText);
	middleRating.showText(0, canvas.height/2 + scaledHeight/2 + 65);

	rightRatingText=trialVariables['rightRatingText']
	if (rightRating == null) {
		rightRating = new textBox(rightRating, rightRatingText, 20, BLACK);
	} else {
		rightRating.removeText();
	}
	rightRating.setText(rightRatingText);
	rightRating.showText(0 + scale.ratingBarWidth/2, canvas.height/2 + scaledHeight/2 + 65);
}

var removeTrialDisplay = function() {
	ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
	if (instructions != null) {
		instructions.removeText();
	}
	if (scale!=null) {
		scale.removeScale();
	}
	if (leftRating != null) {
		leftRating.removeText();
	}
	if (middleRating != null) {
		middleRating.removeText();
	}
	if (rightRating != null) {
		rightRating.removeText();
	}
}

var question;
var drawQuestionDisplay = function() {
	if (currTrialN == 0 || (currTrialN - 1 > 0 && expVariables[currTrialN]['question'] != expVariables[currTrialN-1]['question'])) { // question is the same as the one on the previous trial
		removeTrialDisplay();
		trialVariables = expVariables[currTrialN];
		instructionsText=trialVariables['question']
		if (question == null) {
			question = new textBox(question, instructionsText, 25, BLACK);
		} else {
			question.removeText();
		}
		question.setText(instructionsText);
		question.showText(0, canvas.height/2);
		questionTimer = setTimeout(drawTrialDisplay,questionDisplayDuration);
	} else {
		drawTrialDisplay(expVariables[currTrialN]);
	}
}

/*
 * Initializes set of trial information and adds to allTrials
 * Checks for any special key presses (associated with stimuli) and adds to specialKeys
 * Sets start time for trial
*/
var pushTrialInfo = function() {
	var currTrial = new trial({'trialN':currTrialN, 'stimuli':stimuli[currTrialN], 'question':expVariables[currTrialN]['question'], 'minPossibleRating':expVariables[currTrialN]['rs_min'], 'maxPossibleRating':expVariables[currTrialN]['rs_max'], 'minRatingText':expVariables[currTrialN]['leftRatingText'], 'midRatingText':expVariables[currTrialN]['middleRatingText'], 'maxRatingText':expVariables[currTrialN]['rightRatingText']});
	allTrials.push(currTrial);

	// send stimuli here to trialInfo, set special keys inside trialInfo
	var i;
	for (i=0;i<stimuli[currTrialN].length;i++) {
		if (stimuli[currTrialN][i].key != 'NaN') {
			specialKeys.push(stimuli[currTrialN][i].key);
		}
	}
	t1 = performance.now(); // start timer for this trial

	allTrials[currTrialN].trialStartTime = t1;

	allTrials[currTrialN]['stimulus'] = stimuli[currTrialN][0].id;
}

/*
  * Does all clean up for trial
  * Get trial duration / reaction time
*/
var endTrial = function() {
	t2 = performance.now();
	var i;
	for (i=0;i<stimuli[currTrialN].length;i++) {
		allTrials[currTrialN]['stimulus' + parseInt(i+1,10) + 'Loaded'] = stimuli[currTrialN][i].loaded;
	}
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
	leftRating.removeText();
	middleRating.removeText();
	rightRating.removeText();
	currTrialN+=1; // iterate to next trial
	if (currTrialN < expVariables.length) {
		drawQuestionDisplay();
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

	drawQuestionDisplay();
}

window.onresize = function() {
	resizeWindow();
}
