
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
var svg = document.getElementById("mySVG");
svg.setAttribute("width", (window.innerWidth).toString());
svg.setAttribute("height", (window.innerHeight).toString());

var confirmationTime = 500; // in ms
var confirmTimer;
//var inConfirmation = 
var ctx = document.getElementById('myCanvas').getContext('2d');


var t1, t2;
var trialTimer;
var maxTrialDuration = 400000; // in ms

var ratingScale = class ratingScale {

	constructor(min, max, tickIncrement, increment) {
		if (min >= max) {
			alert("Invalid parameters for ratingScale! min must be smaller than max");
		}
		if (tickIncrement > max - min) {
			alert("Invalid tickIncrement for ratingScale!");
		}
		if (increment > max - min) {
			alert("Invalid increment for ratingScale!");
		}
		this.ratingScale = svg;

		//this.ratingScale.setAttribute("height", (window.innerHeight/10).toString());
		this.min = min;
		this.max = max;
		this.tickIncrement = tickIncrement;
		this.increment = increment;
	}

	drawRatingScale() {
		this.drawRatingBar();
		var right = this.ratingBarX + this.ratingBarWidth;
		var left = this.ratingBarX;
		var randPos = Math.random() * (right - left) + left;
		this.drawSelector(randPos, 0, "blue");

		this.drawTickLabels();
	}

	drawRatingBar() {
		var width = window.innerWidth/2;
		var height = window.innerHeight*0.04;
		this.ratingBarWidth = width;
		this.ratingBarHeight = height;
		this.ratingBarX = window.innerWidth/2 - width/2;
		this.ratingBarY = window.innerHeight/2 + (window.innerHeight*0.35);

		var r = document.createElementNS("http://www.w3.org/2000/svg", "rect");
		r.setAttribute("onmousemove", "moveSelector(evt)")
		r.setAttribute("x", this.ratingBarX.toString());
		r.setAttribute("y", this.ratingBarY.toString());
		r.setAttribute("width", this.ratingBarWidth.toString());
		r.setAttribute("height", this.ratingBarHeight.toString());
		r.setAttribute("fill", "black");
		this.bar = r;
		this.ratingScale.appendChild(r);
	}

	drawSelector(x, y, color) {
		var width = window.innerWidth*.02;
		var height = window.innerHeight*0.04;
		this.selectorWidth = width;
		this.selectorHeight = height;
		this.selectorX = x - this.selectorWidth/2;
		this.selectorY = this.ratingBarY;

		var r = document.createElementNS("http://www.w3.org/2000/svg", "rect");
		r.setAttribute("onclick", "recordRating(evt)")
		r.setAttribute("x", this.selectorX.toString());
		r.setAttribute("y", this.selectorY.toString());
		r.setAttribute("width", this.selectorWidth.toString());
		r.setAttribute("height", this.selectorHeight.toString());
		r.setAttribute("fill", color);
		this.selector = r;
		this.ratingScale.appendChild(r);
	}

	drawTickLabels() {

		var nRatingValues = (this.max - this.min)/this.increment;
		var nScaleValues = this.ratingBarWidth/this.increment;
		var nTicks = (this.max - this.min)*this.tickIncrement;
		var i;
		var tickLabels = [];
		var fontsize = 25;
		for (i = 0; i <= nTicks; i++) {
			var label = document.createElementNS("http://www.w3.org/2000/svg", "text");
			label.setAttribute("x",((i*nScaleValues/nRatingValues)+this.ratingBarX - 10).toString());
			label.setAttribute("y",(this.ratingBarY + this.ratingBarHeight + fontsize).toString());
			label.setAttribute("font-family","Arial");
			label.setAttribute("font-size",fontsize.toString());
			label.setAttribute("fill","black");
			label.textContent = "$" + i.toString();
			tickLabels.push(label);
			this.ratingScale.appendChild(label);

		}
		this.tickLabels = tickLabels;
	}

	updateSelector(evt) {
		// OPTION 1
		var originalX = parseInt(this.selector.getAttribute("x"));
		var x = evt.clientX - originalX - this.selectorWidth/2; // why is it prevX?
		var y = 0; // relative to rating bar
		this.selector.setAttribute("transform", "translate(" + (x).toString() + "," + (y).toString() + ")");

		// OPTION 2
		//var x = evt.clientX;
		//this.selector.setAttribute("x", x.toString())
		//this.selector.setAttribute("y", y.toString())
	}

	recordRating(evt) {
		// (max-min) / increment => number of possible values
		var nRatingValues = (this.max - this.min)/this.increment;
		var nScaleValues = this.ratingBarWidth/this.increment;
		var clickX = evt.clientX;

		// mouse listener is on the selector, not the bar itself
		// so mouse can actually be clicked on a location before the bar
		// this readjusts the location of the click so it can only be at the max or min
		if (clickX < this.ratingBarX) {
			clickX = this.ratingBarX
		} else if (clickX > this.ratingBarX + this.ratingBarWidth) {
			clickX = this.ratingBarX + this.ratingBarWidth;
		}

		var rating = clickX - this.ratingBarX + this.min;
		rating = rating / nScaleValues * nRatingValues;
		rating = rating/this.increment;
		rating = Math.floor(rating);
		rating = rating*this.increment;

		console.log(rating);
		end_trial();
	}

	resetScale() {
		if (this.bar != null) {
			this.ratingScale.removeChild(this.bar);
		}
		if (this.selector != null) {
			this.ratingScale.removeChild(this.selector);
		}
		var i;
		for (i=0;i<this.tickLabels.length;i++) {
			this.ratingScale.removeChild(this.tickLabels[i]);
		}

	}
}

var moveSelector = function moveSelector(evt) {
	//console.log(evt);
	scale.updateSelector(evt);
}

var recordRating = function(evt) {
	scale.recordRating(evt);
}

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

const LEFT = 'LEFT';
const RIGHT = 'RIGHT';
const CENTER = 'CENTER';

/*
  * Draws individual trial display
  * Updates trial information
  * @param {python dictionary/js object} trialVariables: has keys and values for trial parameters
*/
var draw_trial_display = function draw(trialVariables) {
	// condition is a dictionary - each key can be used to set trial conditions
	var imgFolder = '/static/stim/';
	stimulus1 = trialVariables['stimulus1'];
	stimulus2 = trialVariables['stimulus2'];

	var img1 = new imageStimulus(stimulus1, imgFolder + stimulus1 + ".bmp", 'u');
	img1.drawImage('LEFT');
	// img.drawImage([0, 0]);

	var img2 = new imageStimulus(stimulus2, imgFolder + stimulus2 + ".bmp", 'i');
	img2.drawImage('RIGHT');

	set_confirmation_color(BLACK);

	if (scale == null) {
		scale = new ratingScale(0,3,1,.01);
	} else {
		scale.resetScale();
	}
	scale.drawRatingScale();

	stimuli = [img1, img2];

	if (allTrials.length == currTrialN) {
		push_trial_info();
	}

}

var start_experiment = function start_experiment() {
	//ctx.clearRect(0,0,canvas.width,canvas.height);
	draw_trial_display(expVariables[currTrialN]); 
}

var trialResults = class trialResults {
	constructor() {
		this.rt = 'None';
		this.rsp = 'None';
		this.selected = 'None';
	}
}

// trial class should store the stimuli array, ['trialN', 'trialStartTime', 'trialEndTime', 'stimulus', 'rsp', 'rt']
var trial = class trial {

	constructor(trialN, stimuli, maxTrialTime) {
		this.trialN = trialN;
		this.stimuli = stimuli;
		this.maxTrialTime = maxTrialTime;
		this.receivedResponse = false;
		this.results = new trialResults();
	}
}



/*
  * Class for image stimulus
  * Creates an image and assigns it an id, source, key value
  * Contains method to draw image stimulus at particular location
*/
var imageStimulus = class imageStimulus {
	/*
	  * Creates javascript image, sets id, src, key
	  * @constructor
	  * @param {string} id: identifier for stimulus 
	  *		(does not have to be unique, could be name of image)
	  * @param {string} src: location of image + image name
	  *		could be in static folder or a website
	  *		ex: '/static/stim/' + stimulusName + '.bmp'
	  * @param {string} key: key to be associated with stimulus
	  *		if you don't want a key associated with this stimulus, set key param to null
	  *		these keys are automatically registered as events when user presses them
	*/
	constructor(id, src, key) {
		this.imgObject = new Image();
		this.id = id;
		this.imgObject.setAttribute("id", id);
		this.src = src;
		this.key = key; // keyboard key for selection
		this.width = 'unknown';
		this.height = 'unknown';
	}

	// position can be a string, like the ones in get_img_position
	// OR position can be an array of the coordinates [x, y]
	// if position not a valid input, throws error

	/*
	  * Draw image on browser window
	  * @param {string or array} position: location to draw the stimulus
	  *		can be string or array of x, y coordinates
	  * 	see @get_img_position for valid string inputs
	  *		note: position of image is anchored at top left corner
	  * 	alerts browser if param position is not valid
	  *		also checks if image fails to load and records it
	*/
	drawImage(position) {
		var trialN = currTrialN;
		var imageStim = this;
		this.trialN = currTrialN;
		var img = this.imgObject;
		img.onload = function() {
			// percent of window to be width of image
			var scaledWidthPercent = 0.45;
			var scaledWidth = window.innerWidth * scaledWidthPercent;
			var scaledHeight = img.height/img.width * window.innerWidth * scaledWidthPercent;

			img.setAttribute("width",scaledWidth);
			img.setAttribute("height",scaledHeight);

			imageStim.width = scaledWidth;
			imageStim.height = scaledHeight;

			var positionCoords = get_img_position(img, position);
			if (typeof position === 'string' && positionCoords != null) {
				imageStim.positionName = position;
				imageStim.positionCoords = positionCoords;
			} else if (Array.isArray(position) && position.length == 2) {
				imageStim.positionName = '';
				positionCoords = position;
				imageStim.positionCoords = position;
			} else {
				alert('Invalid image position')
			}

			ctx.drawImage(img, positionCoords[0], positionCoords[1], scaledWidth, scaledHeight);

		};
		img.onerror = function() {
			var errorTime = performance.now();
			var errorInfo = new errorMsgInfo(img.id + ' didn\'t load', trialN, errorTime);
			expErrors.push(errorInfo)
			console.log("IMAGE DIDN\'T LOAD. Trial " + trialN + ", " + img.id);
			// send error messages back to server if image didn't load (error may come up later)
		};
		img.setAttribute("src", this.src);
	}
};


/*
  * Helper for @drawImage method in @imageStimulus
  * Checks if @param position in @drawImage is valid string
  * Position parameter from @drawImage is passed here as positionName
  * If positionName is valid string, returns appropriate coordinates
  *	Alerts browser if image is cut off on left/right edges
  * @param {Image object} img: Image() instance in imageStimulus
  * @param {string} positionName: valid position name
  * 	current valid positionNames: CENTER, LEFT, RIGHT
  *	@returns array of x, y coordinates if positionName is valid string,
  * 	returns null otherwise	
*/
var get_img_position = function get_img_position(img, positionName) {
	var padding = window.innerWidth * .02; // adjusts the amount of white space between two images
	var positionCoords;
	if (positionName == 'CENTER') {
		positionCoords = [window.innerWidth / 2 - img.width / 2, canvas.height / 2 - img.height / 2]
	} else if (positionName == 'LEFT') {
		positionCoords = [window.innerWidth / 2 - img.width - padding, canvas.height / 2 - img.height / 2]
	} else if (positionName == 'RIGHT') {
		positionCoords = [window.innerWidth / 2 + padding, canvas.height / 2 - img.height / 2]
	} else {
		return null;
	}

	if (positionCoords[0] < 0) {
		// should not be alert b/c may show up on client screen
		// either adjust size or seomthing else
		//alert('Image cut off on left edge')
	}

	if (positionCoords[1] > window.innerHeight) {
		// should not be alert b/c may show up on client screen
		//alert('Image cut off on right edge')
	}
	return positionCoords;
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
			end_trial(e);
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
var end_trial = function end_trial(e) {
	if (e == null) {
		t2 = performance.now();
	} else {
		t2 = e.timeStamp;
	}
	clearTimeout(trialTimer);
	trialDuration = t2 - t1;
	allTrials[currTrialN].trialEndTime = t2;
	var color;
	if (e == null) {
		color = RED;
		drawNextTrial = true;
		allTrials[currTrialN].results.rsp = 'None';
	} else {
		allTrials[currTrialN].receivedResponse = true;
		color = GREEN;
		allTrials[currTrialN].results.rsp = e.key;
	}
	set_confirmation_color(color);
	allTrials[currTrialN].results.rt = trialDuration;
	confirmTimer = setTimeout(next_trial,confirmationTime);
}


/*
  * @constructor for storing key press information
  * @param {string} key: the key that was pressed
  * @param {int} trialN: the trial in which key was pressed
  * @param {float} timePressedExp: time key was pressed relative to experiment start 
  * @param {float} timePressedTrial: time key was pressed relative to trial start 
*/
function keyPressInfo(key,trialN,timePressedExp,timePressedTrial) {
	this.key = key,
	this.trialN = trialN,
	this.timePressedExp = timePressedExp,
	this.timePressedTrial = timePressedTrial
}

/*
  * @constructor for error message information
  * @param {string} msg: information about the error (ex: img didn\t load)
  * @param {int} trialN: the trial in which error occurred
  * @param {float} timeExp: time error was registered by browser
*/
function errorMsgInfo(msg,trialN,timeExp) {
	this.msg = msg,
	this.trialN = trialN,
	this.timeExp = timeExp
}


const BLACK = "#000000";
const RED = "#ff0000";
const GREEN = "#00cc00";
var box;
/*
  * Creates an svg box at the center of the screen
  * Use case: Turns green when user responds
  * Use case: Turns red when trial timed out and no response was received
  * @param {string} color: a hex value to change the color
*/
var set_confirmation_color = function set_confirmation_color(color) {
	if (box!=null) {
		svg.removeChild(box);
	}
	var centerX = window.innerWidth / 2;
	var centerY = window.innerHeight / 2;

	var confirmBoxSide = window.innerWidth * 0.02;

	box = document.createElementNS("http://www.w3.org/2000/svg", "rect");
	box.setAttribute("x",(centerX - confirmBoxSide/2).toString());
	box.setAttribute("y",(centerY).toString());
	box.setAttribute("width",confirmBoxSide.toString());
	box.setAttribute("height",confirmBoxSide.toString());
	box.setAttribute("fill",color);
	svg.appendChild(box);
}

var update_confirmation_color = function update_confirmation_color(color) {
	// get this??????
}


window.addEventListener("keydown", checkKeyPress);