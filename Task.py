from psychopy import visual, core, event  # import some libraries from PsychoPy
import numpy as np
import taskUtils
import constants
from pyedfread import edf
from eyetrackerFuncs import Tracker_EyeLink
import tempfile
import os


class Task:
    def __init__(self, subject, data, trackEye=True):
        self.subject = subject
        self.data = data
        self.clock = core.Clock()
        self.trial = self.subject.get("TrialsCompleted")
        self.trialOrder = self.subject.get("TrialOrder")
        self.condition = self.subject.get("ConditionID")
        self.eyeTracked = self.subject.get("EyeTracked")
        self.window = visual.Window(constants.MONITOR_RESOLUTION, monitor="testMonitor", units="pix")
        self.trackEye = trackEye
        self.action = {constants.QUIT_EXPERIMENT_KEY: self.quit_experiment,
                       constants.RECALIBRATE_KEY: self.recalibrate,
                       constants.EVENT_PROCEED_KEY: self.proceed}
        if self.trackEye:
            self.eyeTracker = Tracker_EyeLink(win=self.window,
                                              clock=self.clock,
                                              sj=subject.userInfo['ParticipantID'],
                                              saccadeSensitivity="HIGH",
                                              calibrationType='HV9',
                                              screen=constants.MONITOR_RESOLUTION,
                                              dummy=False)

            self.eyeTrackerData = {}

    def task_message(self, message):
        self.subject.append("TaskMessages", (message, self.clock.getTime()))
        if self.trackEye and self.eyeTracker.getStatus() == "RECORDING":
            self.eyeTracker.sendMessage(message)

    def load_stimulus(self):
        taskUtils.guide_text(self.window, self.trial, self.condition)
        stimulus = visual.ImageStim(self.window,
                                    image=self.data['ImagePaths'][self.trialOrder[self.trial]],
                                    pos=[constants.IMAGE_X_DISPLACEMENT, constants.IMAGE_Y_DISPLACEMENT])
        aspectRatio = stimulus.size[0] / stimulus.size[1]
        stimulus.size = np.array([aspectRatio * constants.IMG_HEIGHT, constants.IMG_HEIGHT])
        stimulus.draw()
        self.window.flip()
        core.wait(constants.STIMULI_DURATION)
        self.window.flip()
        event.clearEvents()

    def save_subject_data(self):
        self.subject.update('TrialsCompleted', self.trial)
        if self.trackEye:
            self.get_eyeTracker_data()
            print(self.eyeTrackerData)
            self.subject.append('EyeTrackData', self.eyeTrackerData.copy())

    def quit_experiment(self):
        if self.trackEye:
            if self.eyeTracker.getStatus() == "RECORDING":
                self.eyeTracker.stopEyeTracking()
            if self.eyeTracker.getStatus() != "OFFLINE":
                self.eyeTracker.closeConnectionToEyeTracker()

        self.task_message("Observer force quit the experiment on trial %d" % self.trial)
        self.window.close()
        core.quit()
        event.clearEvents()

    def recalibrate(self):
        if self.eyeTracker.getStatus() == "RECORDING":
            self.eyeTracker.stopEyeTracking()
        self.eyeTracker.startEyeTracking(0, calibTrial=True)
        self.task_message("Observer recalibrated.")
        event.clearEvents()

    def proceed(self):
        pass

    def get_eyeTracker_data(self):
        self.eyeTracker.retrieveDataFile(tempfile.gettempdir() + '/trial.edf')

        samples, events, messages = edf.pread(tempfile.gettempdir() + '/trial.edf',
                                              trial_marker=b'STIMULUS PRESENTATION ROUTINE')  # trial marker here is
        # important!
        os.remove(tempfile.gettempdir() + '/trial.edf')

        assert len(
            messages) != 0  # make sure messages were sent to edf file for timing of eye movements, this is important!!!
        start_stimulus_time = messages.loc[1, 'trialid_time']
        end_stimulus_time = messages.loc[2, 'trialid_time']

        events = events[(events['start'] > start_stimulus_time) & (events['start'] < end_stimulus_time)]

        events['start'] = self.stimulus_on + ((events['start'] - start_stimulus_time).astype('float64') / 1000)
        events['end'] = self.stimulus_on + ((events['end'] - start_stimulus_time).astype('float64') / 1000)

        start_saccade = None
        saccades = []
        all_saccades = []
        all_fixations = []

        for index, row in events.iterrows():
            if row['type'] == "fixation" and start_saccade:
                saccades.append([start_saccade, [row['gstx'], row['gsty'], row['end']]])
                all_fixations.append([row['gavx'], row['gavy'], row['start'], row['end']])
                start_saccade = None
                print("serg")
            if row['type'] == "saccade":
                start_saccade = [row['gstx'], row['gsty'], row['end']]
                all_saccades.append([[row['gstx'], row['gsty'], row['start']],
                                     [row['genx'], row['geny'], row['end']]])
                print("sereeg")

        self.eyeTrackerData['Saccades'] = saccades
        self.eyeTrackerData['AllSaccades'] = all_saccades
        self.eyeTrackerData['AllFixations'] = all_fixations

    def forceFixateRoutine(self):
        fixationStarted = False
        fixationDone = False
        fixationStartTime = None
        event.clearEvents()
        while not fixationDone:
            keys = event.getKeys()
            if len(keys) > 0:
                if keys[-1] in self.action:
                    self.action[keys[-1]]()

            eye_data = self.eyeTracker.getNewestSample(self.eyeTracked, (0, 0))
            #print(eye_data)
            if eye_data != (-1, -1):
                eyePosition = (eye_data[0] - constants.MONITOR_RESOLUTION[0] / 2,
                               -eye_data[1] + constants.MONITOR_RESOLUTION[1] / 2)
                # switch to psychopy window coordinates (0,0) middle of screen

                gazeOkayRegion = visual.Circle(self.window, radius=constants.CROSS_SIZE / 2,
                                               units="pix", pos=[0, -300], lineWidth=2,
                                               lineColorSpace="rgb255", lineColor=constants.COLOR_WHITE)

                fixating = gazeOkayRegion.contains(*eyePosition)

                if fixating:
                    if not fixationStarted:
                        fixationStarted = True
                        fixationStartTime = self.clock.getTime()
                    fixationDuration = self.clock.getTime() - fixationStartTime
                    if fixationDuration >= constants.FIXATION_DURATION:
                        fixationDone = True
                else:
                    fixationStarted = False


                taskUtils.draw_gaze(self.window, eyePosition)

                print(eyePosition)
            taskUtils.guide_text(self.window, self.trial, self.condition)
            taskUtils.draw_fixation(self.window, [0, -300])
            self.window.flip()

    def run_trials(self):
        n = self.trial
        for _ in self.trialOrder[n:]:
            self.task_message("Fixation loaded.")
            taskUtils.guide_text(self.window, self.trial, self.condition)
            #taskUtils.draw_fixation(self.window, [0, -300])


            #self.action[taskUtils.wait_for_user_input()]()

            if self.trackEye:
                if self.eyeTracker.getStatus() != "RECORDING":
                    self.eyeTracker.startEyeTracking(self.trial, calibTrial=False)
                self.eyeTracker.resetEventQue()
            self.forceFixateRoutine()
            self.window.flip()
            self.task_message("STIMULUS PRESENTATION ROUTINE starting.")

            self.stimulus_off = self.clock.getTime()
            self.load_stimulus()
            self.stimulus_on = self.clock.getTime()

            self.task_message("STIMULUS PRESENTATION ROUTINE ended.")
            if self.trackEye:
                self.eyeTracker.stopEyeTracking()

            self.trial += 1
            self.save_subject_data()

            self.window.flip()
