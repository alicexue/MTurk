console.log("loaded run_scenetask.js ");

// var expVariables set in HTML

var allKeyPresses = [];

var currTrialN = 0;

var origImgWidth = 256; // necessary for rescaling images
var origImgHeight = 256; // necessary for rescaling images

var stimuli = []; 
var specialKeys = [];

var expResults = [];
var allTrials = [];

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
var timer; // for between answering and maxTrialDuration

var t1, t2;
var t1_UNIX;
var t2_UNIX;
var trialTimer;
var maxTrialDuration = 3000; // in ms

var widthPercent = .45;
var rescaleHeight = false;

/*
 * Called in the HTML
*/
var nStimuli;
var nImagesLoaded = 0;
var startExperiment = function() {
	nStimuli = expVariables.length;
	drawLoadingText();
	generateOffScreenCanvases(drawStimuliToCanvas, '');
}

var drawStimuliToCanvas = function(trialVariables, trialN, canvasCtx) {
	var position = "CENTER";
	var stimulus = trialVariables['sceneStimulus'];
	var fullStimName = trialVariables['fullStimName'];
	var img = new imageStimulus(stimulus, stimFolder + fullStimName, 'NaN', widthPercent, rescaleHeight);
	img.drawImage(position, trialN, canvasCtx);
	trialStimuli = [img];
	stimuli[trialN] = trialStimuli;
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
var indoorsText;
var outdoorsText;
var drawTrialDisplay = function(trialVariables) {
	// condition is a dictionary - each key can be used to set trial conditions

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

	var scaledImgDimensions = rescaleImgSize([origImgWidth,origImgHeight], widthPercent, false);
	var scaledHeight = scaledImgDimensions[1];
	var scaledWidth = scaledImgDimensions[0];

	var indoors_key_on_left = expVariables[currTrialN]['indoorsKey'] == 'u';

	if (instructions == null) {
		if (indoors_key_on_left) {
			instructions = new textBox(instructions, "Is this an indoors or outdoors scene? Press 'u' for indoors or 'i' for outdoors.", 20, BLACK);
		} else {
			instructions = new textBox(instructions, "Is this an indoors or outdoors scene? Press 'u' for outdoors or 'i' for indoors.", 20, BLACK);
		}
	} else {
		instructions.removeText();
	}
	instructions.showText(0, canvas.height/2 - scaledHeight/2 - 10);

	if (indoorsText == null) {
		indoorsText = new textBox(indoorsText, "indoors", 20, BLACK);
	} else {
		indoorsText.removeText();
	}

	if (outdoorsText == null) {
		outdoorsText = new textBox(outdoorsText, "outdoors", 20, BLACK);
	} else {
		outdoorsText.removeText();
	}

	if (indoors_key_on_left) {
		indoorsText.showText(0 - scaledWidth/2, canvas.height/2 + scaledHeight/2 + 30);
		outdoorsText.showText(0 + scaledWidth/2, canvas.height/2 + scaledHeight/2 + 30);
	} else {
		indoorsText.showText(0 + scaledWidth/2, canvas.height/2 + scaledHeight/2 + 30);
		outdoorsText.showText(0 - scaledWidth/2, canvas.height/2 + scaledHeight/2 + 30);
	}

}

/*
 * Initializes set of trial information and adds to allTrials
 * Checks for any special key presses (associated with stimuli) and adds to specialKeys
 * Sets start time for trial
 * Sets timer for trial
*/
var pushTrialInfo = function() {
	var currTrial = new trial({'trialN':currTrialN, 'stimuli':stimuli[currTrialN], 'sceneStimulus':expVariables[currTrialN]['sceneStimulus'], 'sceneStimulusPath':expVariables[currTrialN]['fullStimName']});
	allTrials.push(currTrial);
	//console.log(currTrial)
	//console.log(allTrials)
	// send stimuli here to trialInfo, set special keys inside trialInfo

	specialKeys = ['u','i'];
	
	t1 = performance.now(); // start timer for this trial
	t1_UNIX = Date.now();
	trialTimer = setTimeout(endTrial,maxTrialDuration);
	allTrials[currTrialN].trialN = currTrialN;
	allTrials[currTrialN].trialStartTime = t1;
	allTrials[currTrialN].trialStartTime_UNIX = t1_UNIX;
}

/*
  * Checks key presses and moves to next trial
  * Checks array of special keys
  * 	- if current key pressed is in specialKey, moves to next trial
*/
var keyIsDown = false; // keep track if key is still being held down - take one key press at a time
var checkKeyPress = function(e) {
	var timePressed = e.timeStamp; // does not seem to be compatible with all browsers - may get UNIX time instead of time relative to trial start
	var timePressed_UNIX = Date.now();
	if (inConfirmation == false && keyIsDown == false && timePressed > t1 && !svg.contains(blankScreenCover)) { 
		keyIsDown = true;
		t2 = timePressed;
		t2_UNIX = timePressed_UNIX;
		// should check if timepressed is after trial starts
		if (specialKeys.indexOf(e.key) > -1 && currTrialN == allTrials.length - 1) { 
			clearTimeout(trialTimer);
			clearTimeout(confirmTimer);
			
			if (currTrialN < expVariables.length) {
				var i;
				for (i=0;i<stimuli[currTrialN].length;i++) {
					if (e.key == expVariables[currTrialN]['indoorsKey']) {
						allTrials[currTrialN].selected = "indoors";
					} else {
						allTrials[currTrialN].selected = "outdoors";
					}
				}
				allTrials[currTrialN].rt = t2 - t1;
				allTrials[currTrialN].rt_UNIX = t2_UNIX - t1_UNIX;
				allTrials[currTrialN].receivedResponse = true;
				allTrials[currTrialN].rsp = e.key;

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
	t2 = performance.now();
	t2_UNIX = Date.now();
	allTrials[currTrialN].trialEndTime = t2;
	allTrials[currTrialN].trialDuration = t2 - t1;
	allTrials[currTrialN].trialEndTime_UNIX = t2_UNIX;
	allTrials[currTrialN].trialDuration_UNIX = t2_UNIX - t1_UNIX;
	if (tooSlowText != null) {
		tooSlowText.removeText();
	}
	currTrialN+=1; // iterate to next trial
	inConfirmation = false;
	if (currTrialN < expVariables.length) { // experiment has not ended 
		drawTrialDisplay(expVariables[currTrialN]);
	} else { // experiment has ended
		instructions.removeText();
		indoorsText.removeText();
		outdoorsText.removeText();

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
var tooSlowText;
var endTrial = function() {
	t2 = performance.now();
	t2_UNIX = Date.now()
	clearTimeout(trialTimer);
	var color;
	if (allTrials[currTrialN].rsp == null || t2 - t1 > maxTrialDuration) { // did not respond
		ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
		color = RED;
		drawNextTrial = true;
		allTrials[currTrialN].selected = 'NaN';
		allTrials[currTrialN].rsp = 'NaN';
		allTrials[currTrialN].rt = 'NaN';
		allTrials[currTrialN].receivedResponse = false;

		if (tooSlowText == null) {
			tooSlowText = new textBox(tooSlowText, "Too slow!", 20, BLACK);
		} else {
			tooSlowText.removeText();
		}
		var scaledImgDimensions = rescaleImgSize([origImgWidth,origImgHeight], widthPercent, false);
		var scaledHeight = scaledImgDimensions[1];
		var scaledWidth = scaledImgDimensions[0];
		tooSlowText.showText(0, canvas.height/2);
		confirmTimer = setTimeout(nextTrial,confirmationTime);
	} else { // if responded
		color = GREEN;
		if (allTrials[currTrialN].selected == "indoors") {
			indoorsText.setColor(color);
		} else {
			outdoorsText.setColor(color);
		}
		timer = setTimeout(clearScreen, maxTrialDuration - (t2-t1));
	}	
	//console.log(allTrials[currTrialN]);
	inConfirmation = true;
	
}

var clearScreen = function() {
	ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
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
