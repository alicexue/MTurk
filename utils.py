import os, sys

_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)

def get_stimuli():
	'''
	get array of stimuli from the directory name stim
	'''
	stimuli = []
	for stimulusFile in os.listdir(_thisDir + '/static/stim/demo/'):
		if stimulusFile.endswith(".bmp"): 
			stimuli.append(stimulusFile[:-4])
	return stimuli