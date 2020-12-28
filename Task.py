from psychopy import visual, core, event  # import some libraries from PsychoPy
import numpy as np
import taskUtils
import constants
from pyedfread import edf
from eyetrackerFuncs import Tracker_EyeLink
import tempfile


class Task:
    def __init__(self, subject, data):
        self.subject = subject
        self.data = data
        self.clock = core.Clock()
        self.trial = self.subject.get("TrialsCompleted")
        self.trialOrder = self.subject.get("TrialOrder")
        self.condition = self.subject.get("ConditionID")
        self.eyeTracked = self.subject.get("EyeTracked")
        self.window = visual.Window(constants.MONITOR_RESOLUTION, monitor="testMonitor", units="pix")
        self.eyeTracker = Tracker_EyeLink(win=self.window,
                                          clock=self.clock,
                                          sj=subject.userInfo['ParticipantID'],
                                          saccadeSensitivity="HIGH",
                                          calibrationType='HV9',
                                          screen=constants.MONITOR_RESOLUTION,
                                          dummy=False)
        self.eyeTrackerData = {}

    def task_message(self, message):
        self.subject.append_data_field((message, self.clock.getTime()), "TaskMessages")
        if self.eyeTracker.getStatus() == "RECORDING":
            self.eyeTracker.sendMessage(message)

    def load_stimulus(self):
        taskUtils.guide_text(self.window, self.trial, self.condition)
        stimulus = visual.ImageStim(self.window, image=self.data['ImagePaths'][self.trialOrder[self.trial]], pos=[0, 100])
        aspectRatio = stimulus.size[0] / stimulus.size[1]
        stimulus.size = np.array([aspectRatio * constants.IMG_HEIGHT, constants.IMG_HEIGHT])
        stimulus.draw()
        self.window.flip()
        core.wait(constants.STIMULI_DURATION)
        event.clearEvents()

    def save_subject_data(self):
        self.subject.update(self.trial, 'TrialsCompleted')
        self.get_eyeTracker_data()
        self.subject.append(self.eyeTrackerData, 'EyeTrackerData')

    def quit_experiment(self):
        if self.eyeTracker.getStatus() == "RECORDING":
            self.eyeTracker.stopEyeTracking()
        if self.eyeTracker.getStatus() != "OFFLINE":
            self.eyeTracker.closeConnectionToEyeTracker()

        self.task_message("Observer force quit the experiment on trial %d" % self.trial)
        self.window.close()
        core.quit()
        event.clearEvents()

    def get_eyeTracker_data(self):
        self.eyeTracker.retrieveDataFile(tempfile.gettempdir() + '/trial.edf')

        samples, events, messages = edf.pread(tempfile.gettempdir() + '/trial.edf',
                                              trial_marker=b'STIMULUS PRESENTATION ROUTINE')  # trial marker here is important!
        os.remove(tempfile.gettempdir() + '/trial.edf')
        assert len(
            messages) != 0  # make sure messages were sent to edf file for timing of eye movements, this is important!!!
        start_stimulus_time = messages.loc[1, 'trialid_time']
        end_stimulus_time = messages.loc[2, 'trialid_time']
        events = events[(events['start'] > start_stimulus_time) & (events['start'] < end_stimulus_time)]
        events['start'] = self.data['stimulus_on'] + ((events['start'] - start_stimulus_time).astype('float64') / 1000)
        events['end'] = self.data['stimulus_on'] + ((events['end'] - start_stimulus_time).astype('float64') / 1000)
        start_saccade = None
        saccades = []
        all_saccades = []
        all_fixations = []

        for index, row in events.iterrows():
            if row['type'] == "fixation" and start_saccade:
                saccades.append([start_saccade, [row['gstx'], row['gsty'], row['end']]])
                all_fixations.append([row['gavx'], row['gavy'], row['start'], row['end']])
                start_saccade = None
            if row['type'] == "saccade":
                start_saccade = [row['gstx'], row['gsty'], row['end']]
                all_saccades.append([[row['gstx'], row['gsty'], row['start']],
                                     [row['genx'], row['geny'], row['end']]])
        self.eyeTrackerData['Saccades'] = saccades
        self.eyeTrackerData['AllSaccades'] = all_saccades
        self.eyeTrackerData['AllFixations'] = all_fixations

    def run_trials(self):
        n = self.trial
        for ID in self.trialOrder[n:]:
            self.task_message("Fixation loaded.")
            taskUtils.guide_text(self.window, self.trial, self.condition)
            quitExperiment = taskUtils.draw_fixation(self.window, [0, -300])
            if quitExperiment:
                self.quit_experiment()
                break

            if self.eyeTracker.getStatus() != "RECORDING":
                self.eyeTracker.startEyeTracking(self.trial, calibTrial=False)
            self.eyeTracker.resetEventQue()
            self.task_message("STIMULUS PRESENTATION ROUTINE starting.")

            self.load_stimulus()

            self.task_message("STIMULUS PRESENTATION ROUTINE ended.")
            self.eyeTracker.stopEyeTracking()

            self.trial += 1
            self.save_subject_data()
            self.window.flip()