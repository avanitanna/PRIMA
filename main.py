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
    myDlg.addField('Condition:', choices=["Study1",
                                          "Study2"])
    myDlg.addField('Experiment Type:', choices=["BL",
                                                "OM",
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
                paths = []
                for img in item["img_fn"]:

                    paths.append(os.path.join('data', 'Landolt_C', img))
                items.append(item)
                imgsPath.append(paths)


    elif experimentType == 'test':
        mainFileName = 'test.jsonl'
        with open(os.path.join('JSONS', mainFileName), 'rb') as f:  # opening file in binary(rb) mode
            for item in json_lines.reader(f):
                imgsPath.append(os.path.join('data', 'test', item['Baseline']))
                items.append(item)
    else:
        mainFileName = 'practice.jsonl'

        with open(os.path.join('JSONS',  mainFileName), 'rb') as f:  # opening file in binary(rb) mode
            for item in json_lines.reader(f):
                imgsPath.append(os.path.join('data', 'EyeTrackingExp1Images', item['img_fn']))
                items.append(item)

    return {'CompleteData': items, 'ImagePaths': imgsPath}


def print_hi():
    participantID, conditionID, experimentType, eyeTracked = get_participant_info()  # opens up GUI to collect User input
    # Get the Data
    data = data_setup(conditionID, experimentType)
    #data = [None]*12
    trials = len(data['ImagePaths'])
    #trials = len(data)
    # Create or open subject file
    subject = User(participantID, conditionID, experimentType, constants.EYE_TRACKED[eyeTracked], trials)
    # Create the task class
    task = primaTask(subject, data, trackEye=False)
    # Run the task
    task.run_trials()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
