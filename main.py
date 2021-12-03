# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from psychopy import gui
from primaTask import primaTask
from User import User
import json_lines
import os
import constants


def get_participant_info():
    myDlg = gui.Dlg(title="VCR Study", )
    myDlg.addText('Subject info')
    myDlg.addField('Name:')
    myDlg.addText('Experiment Info')
    myDlg.addField('Condition:', choices=["Study1"])
    myDlg.addField('Experiment Type:', choices=["BL",
                                                "PRIMA40",
                                                "PRIMA55",
                                                "PRIMA75",
                                                "PRIMA100",
                                                "Practice",
                                                "test"])
    myDlg.addField('Eye Tracked:', choices=["Left",
                                            "Right"])

    ok_data = myDlg.show()  # show dialog and wait for OK or Cancel
    if myDlg.OK:  # or if ok_data is not None
        print(ok_data)
    else:
        print('user cancelled')
    return ok_data


def data_setup(conditionID, experimentType):
    imgsPath = []
    items = []
    if experimentType == 'BL':
        mainFileName = 'LandoltLibrary.jsonl'

        with open(os.path.join('JSONS', mainFileName), 'rb') as f:  # opening file in binary(rb) mode
            for item in json_lines.reader(f):
                imgsPath.append(os.path.join('data', 'Landolt_C_New_0', item['img_fn']))
                items.append(item)

    elif experimentType == 'PRIMA40':
        mainFileName = 'LandoltLibrary_withPrimaPatches_1.jsonl'

        with open(os.path.join('JSONS', mainFileName), 'rb') as f:  # opening file in binary(rb) mode
            for item in json_lines.reader(f):
                imgsPath.append(os.path.join('data', 'Landolt_C_New_1', item['img_fn']))
                items.append(item)

    elif experimentType == 'PRIMA55':
        mainFileName = 'LandoltLibrary_withPrimaPatches_2.jsonl'

        with open(os.path.join('JSONS', mainFileName), 'rb') as f:  # opening file in binary(rb) mode
            for item in json_lines.reader(f):
                imgsPath.append(os.path.join('data', 'Landolt_C_New_2', item['img_fn']))
                items.append(item)

    elif experimentType == 'PRIMA75':
        mainFileName = 'LandoltLibrary_withPrimaPatches_3.jsonl'

        with open(os.path.join('JSONS', mainFileName), 'rb') as f:  # opening file in binary(rb) mode
            for item in json_lines.reader(f):
                imgsPath.append(os.path.join('data', 'Landolt_C_New_3', item['img_fn']))
                items.append(item)

    elif experimentType == 'PRIMA100':
        mainFileName = 'LandoltLibrary_withPrimaPatches_4.jsonl'

        with open(os.path.join('JSONS', mainFileName), 'rb') as f:  # opening file in binary(rb) mode
            for item in json_lines.reader(f):
                imgsPath.append(os.path.join('data', 'Landolt_C_New_4', item['img_fn']))
                items.append(item)

    elif experimentType == 'test':
        mainFileName = 'test.jsonl'
        with open(os.path.join('JSONS', mainFileName), 'rb') as f:  # opening file in binary(rb) mode
            for item in json_lines.reader(f):
                imgsPath.append(os.path.join('data', 'test', item['Baseline']))
                items.append(item)
    else:
        mainFileName = 'practice.jsonl'

        with open(os.path.join('JSONS', mainFileName), 'rb') as f:  # opening file in binary(rb) mode
            for item in json_lines.reader(f):
                imgsPath.append(os.path.join('data', 'EyeTrackingExp1Images', item['img_fn']))
                items.append(item)

    return {'CompleteData': items, 'ImagePaths': imgsPath}


def print_hi():
    participantID, conditionID, experimentType, eyeTracked = get_participant_info()  # opens up GUI to collect User input
    # Get the Data
    data = data_setup(conditionID, experimentType)
    # data = [None]*12
    trials = len(data['ImagePaths'])
    # trials = len(data)
    # Create or open subject file
    subject = User(participantID, conditionID, experimentType, constants.EYE_TRACKED[eyeTracked], trials,
                   RandomizeTrials=False)
    # Create the task class
    task = primaTask(subject, data)
    # Run the task
    task.run_trials()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
