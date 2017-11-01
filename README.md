Amazon Mechanical Turk

Backend:
Middleware: Python
Frontend: HTML, Javascript, CSS 


Overview of folders (*) and files included:

app.py
utils.py
store_data.py
static *
	stim *
	components.js
	run_exp.js
	run_auction.js
	run_choicetask.js
	
templates *
	auction.html
	auction_instructions.html
	choicetask.html
	consent_form.html
	experiment.html
	thankyou.html
data *

File explanations:
Python files:
- app.py
	This file communicates with the backend (server side) and frontend (client side). The Flask framework to deploy the website. This file specifies routes to direct the AMT worker to. For each route, you have GET or POST methods. GET methods are for accessing the website, and POST methods are for taking information from the user (to post, there must be a <form> element inside the HTML file). Inside GET methods, you specify the HTML file that should be loaded for the given route. Inside POST methods, information from the user is received from a dictionary called request.form. Then you can reroute to another HTML file.

- utils.py
	This file contains useful methods to be implemented inside app.py. This is where experiment conditions should be set and then called upon by app.py. Already included in this file are some methods that retrieve the names of image files in a specified directory.

- store_data.py
	This file contains a method to write information to csv files. At the moment, it requires a very specific type of input. 

- components.js
	This file contains javascript classes and methods for different experiment components. In general, you should not have to make changes to this file. Instead, it should be treated like a library of code you can access from other javascript files. So far, it includes imageStimulus, ratingScale, and confirmationBox.

Javscript files:
- Notes about Javascript in general:
	- Asynchronous
	- Javascript code can essentially be organized in any way you please. As long as the javascript file is added to the HTML file, no additional code is necessary to access methods/classes in other javascript files.

- general structure of some run_task.js
	- start_experiment()
	- draw_trial_display()
	- push_trial_info()
	- checkKeyPress() (if you are taking button presses as input)
	- end_trial()
	- next_trial()
	- resizeWindow()

- run_auction.js
	Displays an image at the center of the screen and a rating scale at the bottom, which takes mouse clicks as responses.

- run_choicetask.js
	Displays two images side by side and a box at the center to indicate response accepted or no response. 

- run_exp.js

HTML files:
- Notes about HTML:
	- To add Javascript files from the static folder, use <script src="{{ url_for('static', filename='filename.js') }}"></script> 
	- I use canvas and svg to display things on the page. Each take up the entire window and overlap. The advantage this is that you can position stimuli by pixel coordinates, just like in the testing room. However, since window sizes will vary for each user, and even during an experiment, the positions you set should be relative to the height and width of the screen. I use canvas solely for loading images (drawing or writing text in canvas has very poor resolution). I use svg to draw stimuli on the screen (rating scale, confirmation box). Another advantage of using svg is that you can add listeners to svg objects, making it very easy to determine if the user's mouse is over an svg or if the user has clicked on it.

Notes:
 - When testing Javascript, you must always do a hard reset of the web page, otherwise the cached javascript file will be used 
 	- Mac: Cmd + Shift + R
 	- Windows: Control + Shift + R
 - Everything in the frontend is accessible to the user, so it is possible for a user to change the information stored in your Javascript files. 
 - 