# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from psychopy import gui, visual, core, event
from Task import Task
from User import User
import json_lines
import os
import numpy as np


def get_participant_info():
    myDlg = gui.Dlg(title="VCR Study", )
    myDlg.addText('Subject info')
    myDlg.addField('Name:')
    myDlg.addText('Experiment Info')
    myDlg.addField('Condition:', choices=["Study1",
                                          "Study2"]
                   )
    ok_data = myDlg.show()  # show dialog and wait for OK or Cancel
    if myDlg.OK:  # or if ok_data is not None
        print(ok_data)
    else:
        print('user cancelled')
    return ok_data


def data_setup():
    imgsPath = []
    items = []
    with open('JSONS/Imgs_for_eyeTrackingExp1.jsonl', 'rb') as f:  # opening file in binary(rb) mode
        for item in json_lines.reader(f):
            imgsPath.append(os.path.join('data/EyeTrackingExp1Images', item['img_fn']))
            items.append(item)
    return {'CompleteData': items, 'ImagePaths': imgsPath}


def print_hi(name):
    participantID, conditionID = get_participant_info()  # opens up GUI to collect User input
    # Get the Data
    data = data_setup()
    trials = len(data['ImagePaths'])
    # Create or open subject file
    subject = User(participantID, conditionID, trials)
    # Create the task class
    task = Task(subject, data)
    # Run the task
    task.run_trials()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
