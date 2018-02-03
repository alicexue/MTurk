console.log("loaded run_auction.js ");
var expVariables; 

var recordAllKeyPresses = true;
var allKeyPresses = [];

var currTrialN = 0;

var stimuli = []; 
var specialKeys = [];

var expResults = [];
var allTrials = [];

/*
  * Called from script in auction.html to initialize expVariables
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
var ctx = canvas.getContext('2d');

var svg = document.getElementById("mySVG");
svg.setAttribute("width", winWidth.toString());
svg.setAttribute("height", winHeight.toString());

var t1, t2; 
// t1: start time of trial
// t2: end time of trial

var scale;

var origImgWidth = 576; // necessary for rescaling images and positioning scale
var origImgHeight = 432; // necessary for rescaling images

var widthPercent = .80;
var rescaleHeight = true;
var stimNames = ["stimulus1"];

/*
 * Called in the HTML
*/
var nStimuli;
var nImagesLoaded = 0;
var startExperiment = function startExperiment() {
	nStimuli = expVariables.length;
	drawLoadingText();
	generateOffScreenCanvases();
}

var drawStimuliToCanvas = function drawStimuliToCanvas(trialVariables, trialN, canvasCtx) {
	var position = "CENTER";
	var stimulus1 = trialVariables['stimulus1'];
	var img1 = new imageStimulus(stimulus1, stimFolder + stimulus1 + ".bmp", 'NaN', widthPercent, rescaleHeight);
	img1.drawImage(position, trialN, canvasCtx);
	trialStimuli = [img1];
	stimuli[trialN] = trialStimuli;
}


var startFirstTrial = function startFirstTrial() {
	removeLoadingText();
	drawTrialDisplay(expVariables[currTrialN]); 
}

/*
  * Draws individual trial display
  * Updates trial information
  * Draws images for trial
  * Adds rating scale to display
  * @param {python dictionary/js object} trialVariables: has keys and values for trial parameters
*/
var instructions;
var drawTrialDisplay = function drawTrialDisplay(trialVariables) {
	// condition is a dictionary - each key can be used to set trial conditions
	ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
	var stimulus1 = trialVariables['stimulus1'];

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

	if (instructions == null) {
		instructions = new instructionsText("Rate how much you want to eat this food from 0 (least) to 10 (most).");
	} else {
		instructions.removeText();
	}
	instructions.showText(canvas.height/2 - scaledHeight/2 - 30);

	if (scale == null) { // set up scale for first trial
		scale = new ratingScale(0,10,1,.01,canvas.width/2,canvas.height/2 + scaledHeight/2 + 10, ["0", "", "", "", "", "5", "", "", "", "", "10"]);
	} else {
		scale.removeScale(); // removes current scale
	}
	scale.drawRatingScale(canvas.width/2,canvas.height/2 + scaledHeight/2 + 10); // draws/redraws scale
}


/*
 * Initializes set of trial information and adds to allTrials
 * Checks for any special key presses (associated with stimuli) and adds to specialKeys
 * Sets start time for trial
*/
var pushTrialInfo = function pushTrialInfo() {
	var currTrial = new trial(currTrialN, stimuli[currTrialN], 'NaN', ['rt','rating']);
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

	for (i=0;i<stimuli[currTrialN].length;i++) {
		allTrials[currTrialN]['stimulus' + parseInt(i+1,10)] = stimuli[currTrialN][i].id;
	}
}

/*
  * Does all clean up for trial
  * Get trial duration / reaction time
*/
var endTrial = function endTrial() {
	t2 = performance.now();
	var i;
	for (i=0;i<stimuli[currTrialN].length;i++) {
		allTrials[currTrialN]['stimulus' + parseInt(i+1,10) + 'Loaded'] = stimuli[currTrialN][i].loaded;
	}
	if (allTrials[currTrialN].results == null) { // did not respond
		drawNextTrial = true;
		allTrials[currTrialN].results.rt = t2 - t1;
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
var nextTrial = function nextTrial() {
	ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
	scale.removeScale();
	instructions.removeText();
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
var resizeWindow = function resizeWindow() {
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
