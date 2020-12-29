# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from psychopy import gui
from Task import Task
from User import User
import json_lines
import os
import constants


def get_participant_info():
    myDlg = gui.Dlg(title="VCR Study", )
    myDlg.addText('Subject info')
    myDlg.addField('Name:')
    myDlg.addText('Experiment Info')
    myDlg.addField('Condition:', choices=["Study1",
                                          "Study2"])
    myDlg.addField('Eye Tracked:', choices=["Right",
                                            "Left"])

    ok_data = myDlg.show()  # show dialog and wait for OK or Cancel
    if myDlg.OK:  # or if ok_data is not None
        print(ok_data)
    else:
        print('user cancelled')
    return ok_data


def data_setup():
    imgsPath = []
    items = []
    with open('JSONS/eye_track_exp1.jsonl', 'rb') as f:  # opening file in binary(rb) mode
        for item in json_lines.reader(f):
            imgsPath.append(os.path.join('data/EyeTrackingExp1Images', item['img_fn']))
            items.append(item)
    return {'CompleteData': items, 'ImagePaths': imgsPath}


def print_hi():
    participantID, conditionID, eyeTracked = get_participant_info()  # opens up GUI to collect User input
    # Get the Data
    data = data_setup()
    trials = len(data['ImagePaths'])
    # Create or open subject file
    subject = User(participantID, conditionID, constants.EYE_TRACKED[eyeTracked], trials)
    # Create the task class
    task = Task(subject, data)
    # Run the task
    task.run_trials()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
