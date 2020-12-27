import os
import json
import numpy as np


class User:
    def __init__(self, participantID, conditionID, TotalTrials=None):
        self.userInfo = {'ParticipantID': participantID,
                         'ConditionID': conditionID,
                         'Data': {'TotalTrials': TotalTrials,
                                  'TrialOrder': [],
                                  'TrialsCompleted': 0,
                                  'TaskMessages': [],
                                  'EyeTrackData': {'Saccades': [],
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

    def update_data_field(self, data, fieldName):
        self.userInfo['Data'][fieldName] = data
        self.save_data()

    def append_data_field(self, data, fieldName):
        self.userInfo['Data'][fieldName].append(data)
        self.save_data()

    def get_trial_number(self):
        return self.userInfo['Data']['TrialsCompleted']

    def get_trial_order(self):
        return self.userInfo['Data']['TrialOrder']

    def get_condition(self):
        return self.userInfo['ConditionID']