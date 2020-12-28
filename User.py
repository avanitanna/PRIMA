import os
import json
import numpy as np
import constants
from collections.abc import Mapping


class User:
    def __init__(self, participantID, conditionID, eyeTracked=constants.EYE_TRACKED['right'], TotalTrials=None):
        self.userInfo = {'ParticipantID': participantID,
                         'ConditionID': conditionID,
                         'Data': {'TotalTrials': TotalTrials,
                                  'TrialOrder': [],
                                  'TrialsCompleted': 0,
                                  'TaskMessages': [],
                                  'EyeTrackData': {'EyeTracked': eyeTracked,
                                                   'Saccades': [],
                                                   'AllSaccades': [],
                                                   'AllFixations': []}},
                         }
        self.userDataPath = None
        self.dataExists = False
        self.load_data()

    def data_dir(self):
        rootDataDirName = os.path.join(os.getcwd(),
                                       'SubjectData',
                                       self.userInfo['ParticipantID'],
                                       self.userInfo['ConditionID'])
        if not os.path.exists(rootDataDirName):
            os.makedirs(rootDataDirName)
        return rootDataDirName

    def load_data(self):
        rootDataDirName = self.data_dir()
        self.userDataPath = os.path.join(rootDataDirName, 'data.json')
        if os.path.exists(self.userDataPath):
            with open(self.userDataPath) as jsonFile:
                self.userInfo['Data'] = json.load(jsonFile)
            self.dataExists = True
        else:
            if self.userInfo['Data']['TotalTrials'] is not None:
                self.userInfo['Data']['TrialOrder'] = np.random.permutation(
                    self.userInfo['Data']['TotalTrials']).tolist()
            else:
                print("User data does not exist. Please provide the total number of trials in the experiment while "
                      "initiating User class")

    def save_data(self):
        print(self.userDataPath)
        with open(self.userDataPath, 'w') as filePath:
            json.dump(self.userInfo['Data'], filePath)

    def get(self, field):
        data = self.data_recursion(field, action=constants.GET)
        if data:
            return data

        print("The given field does not exist")

    def update(self, field, value):
        self.userInfo["Data"] = self.data_recursion(field, action=constants.UPDATE, value=value)
        self.save_data()

    def append(self, field, value):
        self.userInfo["Data"] = self.data_recursion(field, action=constants.APPEND, value=value)
        self.save_data()

    def data_recursion(self, field, action, value=None, data=None):
        if data is None:
            data = self.userInfo['Data']
        for key in data:
            if isinstance(data[key], Mapping):
                if action == constants.GET:
                    self.data_recursion(field, action, data=data[key])
                else:
                    data[key] = self.data_recursion(field, action, value=value, data=data[key])
            elif key == field:
                if action == constants.GET:
                    return data[key]
                elif action == constants.UPDATE:
                    data[key] = value
                elif action == constants.APPEND:
                    if not isinstance(data[key], Mapping):
                        data[key].append(value)
                    else:
                        for item in value:
                            data[key][item].append(value[item])

        if action is not constants.GET:
            return data
        else:
            return False
