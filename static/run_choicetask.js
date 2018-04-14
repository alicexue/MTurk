console.log("loaded run_choicetask.js ");
var expVariables; 

var allKeyPresses = [];

var currTrialN = 0;

var origImgWidth = 576; // necessary for rescaling images
var origImgHeight = 432; // necessary for rescaling images

var stimuli = []; 
var specialKeys = [];

var expResults = [];
var allTrials = [];

/*
  * Called from script in choicetask.html to initialize expVariables
  * @param {array} inputExpVariables: each element is a dictionary containing trial information
  *		elements are in the order of trials
*/
var setTrialVariables = function(inputExpVariables) {
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
var inConfirmation = false;

var t1, t2;
var t1_UNIX;
var t2_UNIX;
var trialTimer;
var maxTrialDuration = 4000; // in ms


var widthPercent = .45;
var rescaleHeight = false;

/*
 * Called in the HTML
*/
var nStimuli;
var nImagesLoaded = 0;
var startExperiment = function() {
	nStimuli = expVariables.length * 2;
	drawLoadingText();
	generateOffScreenCanvases();
}

var drawStimuliToCanvas = function(trialVariables, trialN, canvasCtx) {
	var stimulus1 = trialVariables['stimulus1'];
	var stimulus2 = trialVariables['stimulus2'];
	var stim1Bid = trialVariables['stim1Bid'];
	var stim2Bid = trialVariables['stim2Bid'];
	
	var img1 = new imageStimulus(stimulus1, stimFolder + stimulus1 + ".bmp", 'u', widthPercent, false);
	img1.drawImage('LEFT', trialN, canvasCtx);
	img1.bid = stim1Bid;

	var img2 = new imageStimulus(stimulus2, stimFolder + stimulus2 + ".bmp", 'i', widthPercent, false);
	img2.drawImage('RIGHT', trialN, canvasCtx);
	img2.bid = stim2Bid;
	
	stimuli[trialN] = [img1, img2];
}

var startFirstTrial = function() {
	removeLoadingText();
	drawTrialDisplay(expVariables[currTrialN]); 
}

/*
  * Draws individual trial display
  * Updates trial information
  * Draws images for trial
  * Adds confirmation box to trial display
  * @param {python dictionary/js object} trialVariables: has keys and values for trial parameters
*/
var instructions;
var drawTrialDisplay = function(trialVariables) {
	// condition is a dictionary - each key can be used to set trial conditions

	var stim1Bid = trialVariables['stim1Bid'];
	var stim2Bid = trialVariables['stim2Bid'];
	var delta = trialVariables['delta']; // right bid - left bid

	//console.log("Trial " + currTrialN + " " + stimulus1 + " " + stim1Bid.toString() + ", " + stimulus2 + " " + stim2Bid.toString());

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

	allTrials[currTrialN]['stimulus1Bid'] = stim1Bid;
	allTrials[currTrialN]['stimulus2Bid'] = stim2Bid;

	allTrials[currTrialN]['delta'] = delta;

	setConfirmationColor(BLACK);

	var scaledImgDimensions = rescaleImgSize([origImgWidth,origImgHeight], widthPercent, false);
	var scaledHeight = scaledImgDimensions[1];

	if (instructions == null) {
		instructions = new instructionsText("Which food do you like more? Press 'u' for the one on the left or 'i' for the one on the right.");
	} else {
		instructions.removeText();
	}
	instructions.showText(canvas.height/2 - scaledHeight/2 - 10);
}

/*
 * Initializes set of trial information and adds to allTrials
 * Checks for any special key presses (associated with stimuli) and adds to specialKeys
 * Sets start time for trial
 * Sets timer for trial
*/
var pushTrialInfo = function() {
	var currTrial = new trial(currTrialN, stimuli[currTrialN], maxTrialDuration, ['rt','rsp','selected']);
	allTrials.push(currTrial);
	//console.log(currTrial)
	//console.log(allTrials)
	// send stimuli here to trialInfo, set special keys inside trialInfo

	specialKeys = [];
	var i;
	for (i = 0; i < stimuli[currTrialN].length; i++) { 
		allTrials[currTrialN]['stimulus' + parseInt(i+1,10)] = stimuli[currTrialN][i].id;
		if (stimuli[currTrialN][i].key != null) {
			specialKeys.push(stimuli[currTrialN][i].key);

		}
	}
	
	t1 = performance.now(); // start timer for this trial
	t1_UNIX = Date.now();
	trialTimer = setTimeout(endTrial,maxTrialDuration);
	allTrials[currTrialN].trialN = currTrialN;
	allTrials[currTrialN].trialStartTime = t1;
}

/*
  * Checks key presses and moves to next trial
  * Checks array of special keys
  * 	- if current key pressed is in specialKey, moves to next trial
*/
var keyIsDown = false; // keep track if key is still being held down - take one key press at a time
var checkKeyPress = function(e) {
	//var timePressed = e.timeStamp; // does not seem to be compatible with all browsers - may get UNIX time instead of time relative to trial start
	console.log(performance.now());
	var timePressed = performance.now();
	var timePressed_UNIX = Date.now();

	if (inConfirmation == false && keyIsDown == false && timePressed > t1 && !svg.contains(blankScreenCover)) { 
		keyIsDown = true;
		t2 = timePressed;
		t2_UNIX = timePressed_UNIX;
		console.log(e.timeStamp - t1);
		console.log(t2 - t1);
		console.log(t2_UNIX - t1_UNIX);
		// should check if timepressed is after trial starts
		if (specialKeys.indexOf(e.key) > -1 && currTrialN == allTrials.length - 1) { 
			clearTimeout(trialTimer);
			clearTimeout(confirmTimer);
			
			if (currTrialN < expVariables.length) {
				var i;
				for (i=0;i<stimuli[currTrialN].length;i++) {
					if (e.key == stimuli[currTrialN][i].key) {
						allTrials[currTrialN].results.selected = stimuli[currTrialN][i].id;
					} else {
					}
				}
				allTrials[currTrialN].results.rt = t2 - t1;
				allTrials[currTrialN].receivedResponse = true;
				allTrials[currTrialN].results.rsp = e.key;
				allTrials[currTrialN].trialEndTime = t2;
				allTrials[currTrialN].trialDuration = t2 - t1;
				endTrial();
			}
		}
	}
}

var setKeyUp = function(e) {
	keyIsDown = false;
}

/*
  * Called by a timer in endTrial 
  * Clears canvas, removes scale
  * Iterates currTrialN by 1, clears current screen and calls drawTrialDisplay for next trial
  * Checks if experiment has ended (there are no more trials), and ends the experiment
*/
var nextTrial = function() {
	ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
	if (svg.contains(confirmationBox)) {
		svg.removeChild(confirmationBox);
	}
	currTrialN+=1; // iterate to next trial
	inConfirmation = false;
	if (currTrialN < expVariables.length) { // experiment has not ended 
		drawTrialDisplay(expVariables[currTrialN]);
	} else { // experiment has ended
		instructions.removeText();

		var strExpResults = JSON.stringify(allTrials);
		document.getElementById('experimentResults').value = strExpResults;

		drawLoadingText();

		document.getElementById('exp').submit()
	}
}

/*
  * Does all clean up for trial
  * Clears trialTimer
  * Get trial duration / reaction time
  * Changes color of confirmation box
  * Sets timer for confirmation and iterates to next trial at the end of confirmation
*/
var endTrial = function() {
	t2 = performance.now();
	t2_UNIX = Date.now()
	clearTimeout(trialTimer);
	var i;
	for (i=0;i<stimuli[currTrialN].length;i++) {
		allTrials[currTrialN]['stimulus' + parseInt(i+1,10) +'Loaded'] = stimuli[currTrialN][i].loaded;
	}
	var color;
	if (allTrials[currTrialN].results == null || t2 - t1 > maxTrialDuration) { // did not respond
		color = RED;
		drawNextTrial = true;
		allTrials[currTrialN].results.selected = 'NaN';
		allTrials[currTrialN].results.rsp = 'NaN';
		allTrials[currTrialN].results.rt = t2 - t1;
		allTrials[currTrialN].trialEndTime = t2;
		allTrials[currTrialN].trialDuration = t2 - t1;
	} else {
		color = GREEN;
	}
	console.log(allTrials[currTrialN]);
	setConfirmationColor(color);
	inConfirmation = true;
	confirmTimer = setTimeout(nextTrial,confirmationTime);
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
	svg.setAttribute("width", (winWidth).toString());
	svg.setAttribute("height", (winHeight).toString());
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
window.addEventListener("keypress", checkKeyPress);
window.addEventListener("keyup", setKeyUp);
