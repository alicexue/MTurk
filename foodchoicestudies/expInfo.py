repeatAuction = {'MDMMT':False, 'MDMRTS':True, 'MDMRTST':True}
foodStimFolder = {'MDMMT':'/static/foodstim60/', 'MDMRTS':'/static/foodstim80/', 'MDMRTST':'/static/foodstim80/'}
MDMMT_taskOrder = ['auction_demo_instructions', 'auction', 'choicetask_demo_instructions', 'choicetask', 'feedback'] # order of tasks in experiment
MDMRTS_taskOrder = ['auction_demo_instructions', 'auction', 'scenetask_demo_instructions', 'scenetask', 'scenechoicetask_demo_instructions', 'scenechoicetask', 'take_break', 'scenechoicetask', 'familiaritytask_instructions', 'familiaritytask', 'feedback'] # order of tasks in experiment
MDMRTST_taskOrder = ['auction_demo_instructions', 'auction', 'scenetask_demo_instructions', 'scenetask', 'scenechoicetask_demo_instructions', 'scenechoicetask', 'take_break', 'scenechoicetask', 'familiaritytask_instructions', 'familiaritytask', 'feedback'] # order of tasks in experiment
# feedback here doesn't get applied
expTaskOrders = {'MDMMT':MDMMT_taskOrder, 'MDMRTS':MDMRTS_taskOrder, 'MDMRTST':MDMRTST_taskOrder} # dictionary of experiments - key is exp name, value is order of tasks

MDMMT_tasksToComplete = {'completedAuction':False, 'completedChoiceTask':False} # for manage_subject_data
MDMRTS_tasksToComplete = {'completedAuction1':False, 'completedAuction2':False, 'completedSceneTask':False, 'completedSceneChoiceTask':False, 'completedFamiliarityTask':False} # for manage_subject_data
MDMRTST_tasksToComplete = {'completedAuction1':False, 'completedAuction2':False, 'completedSceneTask':False, 'completedSceneChoiceTask':False, 'numberTimesSceneChoiceTaskInstructionsQuizWasTaken':0} # for manage_subject_data
expTasksToComplete = {'MDMMT':MDMMT_tasksToComplete, 'MDMRTS':MDMRTS_tasksToComplete, 'MDMRTST':MDMRTST_tasksToComplete} 