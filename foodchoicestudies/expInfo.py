repeatAuction = {'MDMMT':False, 'MDMRTS':True}
foodStimFolder = {'MDMMT':'/static/foodstim60/', 'MDMRTS':'/static/foodstim80/'}
MDMMT_taskOrder = ['auction_demo_instructions', 'auction', 'choicetask_demo_instructions', 'choicetask', 'feedback'] # order of tasks in experiment
MDMRTS_taskOrder = ['auction_demo_instructions', 'auction', 'scenetask_demo_instructions', 'scenetask', 'scenechoicetask_demo_instructions', 'scenechoicetask', 'take_break', 'scenechoicetask', 'familiaritytask_instructions', 'familiaritytask', 'feedback'] # order of tasks in experiment
# feedback here doesn't get applied
expTaskOrders = {'MDMMT':MDMMT_taskOrder, 'MDMRTS':MDMRTS_taskOrder} # dictionary of experiments - key is exp name, value is order of tasks

MDMMT_tasksToComplete = {'completedAuction':False, 'completedChoiceTask':False} # for manage_subject_data
MDMRTS_tasksToComplete = {'completedAuction1':False, 'completedAuction2':False, 'completeSceneTask':False, 'completedSceneChoiceTask':False, 'completedFamiliarityTask':False} # for manage_subject_data
expTasksToComplete = {'MDMMT':MDMMT_tasksToComplete, 'MDMRTS':MDMRTS_tasksToComplete} 