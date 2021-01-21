import os
import json
import numpy as np
import constants
from collections.abc import Mapping


class User:
    def __init__(self, participantID, conditionID, eyeTracked=None, TotalTrials=None):
        self.userInfo = {'ParticipantID': participantID,
                         'ConditionID': conditionID,

                         'Data': {'TotalTrials': TotalTrials,
                                  'TrialOrder': [],
                                  'TrialsCompleted': 0,
                                  'TaskMessages': [],
                                  'EyeTrackData': []},
                         'EyeTracked': eyeTracked
                         }
        self.userDataPath = None
        self.dataExists = False
        self.load_data()

        if eyeTracked is not None:
            self.update("EyeTracked", eyeTracked)

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
                self.userInfo = json.load(jsonFile)
            self.dataExists = True
        else:
            if self.userInfo['Data']['TotalTrials'] is not None:
                self.userInfo['Data']['TrialOrder'] = np.random.permutation(
                    self.userInfo['Data']['TotalTrials']).tolist()
                self.save_data()
            else:
                print("User data does not exist. Please provide the total number of trials in the experiment while "
                      "initiating User class")

    def save_data(self):
        with open(self.userDataPath, 'w') as filePath:
            json.dump(self.userInfo, filePath)

    def has(self, field):
        _, success = self.data_recursion(field, action=constants.GET)
        return success

    def get(self, field, parentField=None):
        data = None
        if parentField is not None:
            data, success = self.data_recursion(parentField, action=constants.GET)
            if not success:
                print("The given parent field does not exist")
                return None

        data, success = self.data_recursion(field, data=data, action=constants.GET)
        if success:
            return data

        print("The given field does not exist")
        return None

    def update(self, field, value, parentField=None):
        data = None
        if parentField is not None:
            data, success = self.data_recursion(parentField, action=constants.GET)
            if not success:
                print("The given parent field does not exist")
                return
            data, success = self.data_recursion(field, action=constants.UPDATE, value=value, data=data)
            if not success:
                print("The given field does not exist in the parent field")
                return
            self.update(parentField, data)
        else:
            data, success = self.data_recursion(field, action=constants.UPDATE, value=value)
            if success:
                self.userInfo = data
                self.save_data()
            else:
                print("The given field does not exist")

    def append(self, field, value, parentField=None):
        data = None
        if parentField is not None:
            data, success = self.data_recursion(parentField, action=constants.GET)
            if not success:
                print("The given parent field does not exist")
                return
            data, success = self.data_recursion(field, action=constants.APPEND, value=value, data=data)
            if not success:
                print("The given field does not exist in the parent field")
                return
            self.update(parentField, data)
        else:
            data, success = self.data_recursion(field, action=constants.APPEND, value=value)
            if success:
                self.userInfo = data
                self.save_data()
            else:
                print("The given field does not exist")

    def create(self, field, parentField, value=[]):
        data, success = self.data_recursion(parentField, action=constants.GET)
        print(parentField)
        if not success:
            print("The given parent field does not exist")
            return
        if isinstance(data, Mapping):
            if field not in data:
                data[field] = value
                self.update(parentField, data)
            else:
                print("Field already exists in parent field")
        else:
            print("Parent field is not a dictionary")
            return

    def data_recursion(self, field, action, value=None, data=None):
        success = False
        if data is None:
            data = self.userInfo

        for key in data:

            if key == field:
                success = True
                if action == constants.GET:
                    return data[key], success
                elif action == constants.UPDATE:
                    data[key] = value
                elif action == constants.APPEND:
                    if not isinstance(data[key], Mapping):
                        data[key].append(value)
                    else:
                        for item in value:
                            data[key][item].append(value[item])
                return data, success

            elif isinstance(data[key], Mapping):
                if action == constants.GET:
                    Data, success = self.data_recursion(field, action, data=data[key])
                    if success:
                        return Data, success
                else:
                    data[key], success = self.data_recursion(field, action, value=value, data=data[key])
                    if success:
                        return data, success

        return data, success
