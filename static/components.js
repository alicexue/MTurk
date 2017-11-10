console.log("loaded components.js");

// trial class should store the stimuli array, ['trialN', 'trialStartTime', 'trialEndTime', 'stimulus', 'rsp', 'rt']
var trial = class trial {
	constructor(trialN, stimuli, maxTrialTime, results) {
		this.trialN = trialN;
		this.stimuli = stimuli;
		this.maxTrialTime = maxTrialTime;
		this.receivedResponse = false;
		this.results = new trialResults(results);
	}
}

/*
 * Stores trial results
*/
var trialResults = class trialResults {
	constructor(resultTypes) {
		var i;
		for (i=0;i<resultTypes.length;i++) {
			this[resultTypes[i]] = 'None';
		}
	}
}


var windowResizeInfo = class windowResizeInfo {
	constructor(time, initWidth, initHeight, finalWidth, finalHeight) {
		this.time = time;
		this.initWidth = initWidth;
		this.initHeight = initHeight;
		this.finalWidth = finalWidth;
		this.finalHeight = finalHeight;
	}
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
 *** IMAGES ***
*/
/*
  * Class for image stimulus
  * Creates an image and assigns it an id, source, key value
  * Contains method to draw image stimulus at particular location
*/
var blank;
var alertText;
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
		this.width = NaN;
		this.height = NaN;
		this.lastAlertTime = 0;
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

		this.loaded = false;

		if (typeof position === 'string') {
			this.positionName = position;
			this.positionCoords = [NaN, NaN];
		} else if (Array.isArray(position)) {
			this.positionName = '';
			this.positionCoords = position;
		}

		img.onload = function() {
			// "this" becomes img, not the object imageStimulus

			imageStim.loaded = true;

			imageStim.origWidth = img.width;
			imageStim.origHeight = img.height;

			var dimensions = rescaleImgSize([img.width,img.height]);
			var scaledWidth = dimensions[0];
			var scaledHeight = dimensions[1];

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

			if (scaledWidth < imageStim.origWidth * .40) { // if scaled image is too small
				alertSmallWindow();

			} else {
				ctx.drawImage(img, positionCoords[0], positionCoords[1], scaledWidth, scaledHeight);
			}

		};
		img.setAttribute("src", this.src);
	}

};

// dimensions is [width, height]
var rescaleImgSize = function rescaleImgSize(dimensions) {
	// percent of window to be width of image
	var width = dimensions[0];
	var height = dimensions[1];
	var scaledWidthPercent = 0.45;
	var scaledWidth = canvas.width * scaledWidthPercent;
	var scaledHeight = height/width * canvas.width * scaledWidthPercent;

	if (scaledWidth > width && scaledHeight > height) {
		console.log("did not adjust image dimensions")
		scaledWidth = width;
		scaledHeight = height;
	}

	if (scaledHeight >= canvas.height + 20) {
		var newProportion = (canvas.height * .65) / scaledHeight;
		scaledHeight = scaledHeight * newProportion;
		scaledWidth = scaledWidth * newProportion;
	}
	return [scaledWidth, scaledHeight];
}


var alertSmallWindow = function alertSmallWindow() {
	if (!svg.contains(blank)) {
		blank = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
		blank.setAttribute("x","0");
		blank.setAttribute("y","0");
		blank.setAttribute("fill","white");
		blank.setAttribute("width",(canvas.width).toString());
		blank.setAttribute("height",(canvas.height).toString());
		svg.appendChild(blank);
	}

	if (!svg.contains(alertText)) {		
		alertText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
		alertText.setAttribute("x","0");
		alertText.setAttribute("y",(canvas.height/2).toString());
		alertText.setAttribute("font-family","Arial");
		alertText.setAttribute("font-size","25");
		alertText.setAttribute("fill","black");
		alertText.textContent = "Please enlarge the window.";
		svg.appendChild(alertText);

		var textWidth = alertText.getComputedTextLength();

		if (textWidth > canvas.width) {
			svg.removeChild(alertText);
			alertText.setAttribute("textLength",canvas.width);
			alertText.setAttribute("lengthAdjust","spacingAndGlyphs");
			svg.appendChild(alertText);
		}
	}
}


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
	var padding = canvas.width * .02; // adjusts the amount of white space between two images
	var positionCoords;
	if (positionName == 'CENTER') {
		positionCoords = [canvas.width / 2 - img.width / 2, canvas.height / 2 - img.height / 2]
	} else if (positionName == 'LEFT') {
		positionCoords = [canvas.width / 2 - img.width - padding, canvas.height / 2 - img.height / 2]
	} else if (positionName == 'RIGHT') {
		positionCoords = [canvas.width / 2 + padding, canvas.height / 2 - img.height / 2]
	} else {
		return null;
	}

	if (positionCoords[0] < 0) {
		// should not be alert b/c may show up on client screen
		// either adjust size or seomthing else
		//alert('Image cut off on left edge')
	}

	if (positionCoords[1] > canvas.height) {
		// should not be alert b/c may show up on client screen
		//alert('Image cut off on right edge')
	}
	return positionCoords;
}

/*
 *** RATING SCALE ***
*/
var ratingScale = class ratingScale {
	// x is center of rating scale
	// y is top of rating scale
	constructor(min, max, tickIncrement, increment, x, y) {
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
		this.x = x;
		this.y = y;
	}

	/*
	 * Draws rating bar and selector
	*/
	drawRatingScale(x, y) {
		this.x = x;
		this.y = y;
		this.drawRatingBar(this.x, this.y);
		var right = this.ratingBarX + this.ratingBarWidth;
		var left = this.ratingBarX;

		// set initial position of selector at random
		var randPos = Math.random() * (right - left) + left; 
		this.drawSelector(randPos, 0, "blue");

		this.drawTickLabels();
	}

	/*
	 * Draws rectangle svg as rating bar
	 * Adds listener to rating bar (will call moveSelector when mouse is on top of rating bar)
	*/
	drawRatingBar(x, y) {
		this.x = x;
		this.y = y;
		var width = canvas.width/2;
		var height = canvas.height*0.04;
		this.ratingBarWidth = width;
		this.ratingBarHeight = height;
		this.ratingBarX = this.x - width/2;
		this.ratingBarY = this.y;

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

	/*
	 * Draws rectangle svg as rating bar
	*/
	drawSelector(x, y, color) {
		var width = this.ratingBarWidth*.03;
		var height = canvas.height*0.04;
		this.selectorWidth = width;
		this.selectorHeight = height;
		this.selectorX = x - this.selectorWidth/2;
		this.selectorY = this.ratingBarY;

		var r = document.createElementNS("http://www.w3.org/2000/svg", "rect");
		r.setAttribute("onclick", "getRating(evt)")
		r.setAttribute("x", this.selectorX.toString());
		r.setAttribute("y", this.selectorY.toString());
		r.setAttribute("width", this.selectorWidth.toString());
		r.setAttribute("height", this.selectorHeight.toString());
		r.setAttribute("fill", color);
		this.selector = r;
		this.ratingScale.appendChild(r);
	}

	/*
	 * Draws labels below the rating scale 
	 * Position and number of labels determined by increment, max, and min set in constructor
	*/
	drawTickLabels() {
		var nRatingValues = (this.max - this.min)/this.increment;
		var nScaleValues = this.ratingBarWidth/this.increment;
		var nTicks = (this.max - this.min)*this.tickIncrement;
		var i;
		var tickLabels = [];
		var fontSize = 25;
		for (i = 0; i <= nTicks; i++) {
			var label = document.createElementNS("http://www.w3.org/2000/svg", "text");
			var x = (i*nScaleValues/nRatingValues)+this.ratingBarX - fontSize + 5;
			var y = this.ratingBarY + this.ratingBarHeight + fontSize
			label.setAttribute("x",x.toString());
			label.setAttribute("y",y.toString());
			label.setAttribute("font-family","Arial");
			label.setAttribute("font-size",fontSize.toString() + "px");
			label.setAttribute("fill","black");
			label.textContent = "$" + i.toString();
			tickLabels.push(label);
			this.ratingScale.appendChild(label);

		}
		this.tickLabels = tickLabels;

		var bottom = y + fontSize;
		if (bottom > canvas.height) {
			alertSmallWindow();
		}
	}

	/*
	 * Reposition selector to mouse position over rating bar
	*/
	updateSelector(evt) {
		var originalX = parseInt(this.selector.getAttribute("x"));
		var x = evt.clientX - originalX - this.selectorWidth/2; 
		var y = 0; // relative to rating bar
		this.selector.setAttribute("transform", "translate(" + (x).toString() + "," + (y).toString() + ")");
	}

	/*
	 * Determine rating, set trial results, and end the trial
	*/
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

		t2 = evt.timeStamp;
		allTrials[currTrialN].results.rt = t2 - t1;
		allTrials[currTrialN].receivedResponse = true;
		allTrials[currTrialN].results.rating = rating;
		allTrials[currTrialN].trialEndTime = t2;
		allTrials[currTrialN].trialDuration = t2 - t1;
		end_trial();
	}

	/*
	 * Remove scale from 
	*/
	resetScale() {
		if (this.ratingScale.contains(this.bar)) {
			this.ratingScale.removeChild(this.bar);
		}
		if (this.ratingScale.contains(this.selector)) {
			this.ratingScale.removeChild(this.selector);
		}
		var i;
		for (i=0;i<this.tickLabels.length;i++) {
			this.ratingScale.removeChild(this.tickLabels[i]);
		}

	}
}

/*
 * Intermediary function called when mouse is over rating bar
 * Calls updateSelector for the scale
*/
var moveSelector = function moveSelector(evt) {
	scale.updateSelector(evt);
}

/*
 * Intermediary function called when mouse clicks rating bar
 * Calls recordRating for the scale
*/
var getRating = function(evt) {
	scale.recordRating(evt);
}

const BLACK = "#000000";
const RED = "#ff0000";
const GREEN = "#00cc00";
/*
 *** CONFIRMATION BOX ***
*/
var box;
/*
  * Creates an svg box at the center of the screen
  * Use case: Turns green when user responds
  * Use case: Turns red when trial timed out and no response was received
  * @param {string} color: a hex value to set the box color 
*/
var set_confirmation_color = function set_confirmation_color(color) {
	if (box!=null) {
		svg.removeChild(box);
	}
	var centerX = canvas.width / 2;
	var centerY = canvas.height / 2;

	var confirmBoxSide = canvas.width * 0.02;

	box = document.createElementNS("http://www.w3.org/2000/svg", "rect");
	box.setAttribute("x",(centerX - confirmBoxSide/2).toString());
	box.setAttribute("y",(centerY).toString());
	box.setAttribute("width",confirmBoxSide.toString());
	box.setAttribute("height",confirmBoxSide.toString());
	box.setAttribute("fill",color);
	svg.appendChild(box);
}
