from psychopy import visual, core, event  # import some libraries from PsychoPy
import numpy as np
import taskUtils
import constants
from pyedfread import edf
from eyetrackerFuncs import Tracker_EyeLink
import tempfile
import os
from pulse2percept.stimuli import ImageStimulus
import pulse2percept as p2p
import cv2
import time
import math
import datetime
import ast


class primaTask:
    def __init__(self, subject, data, trackEye=True):
        self.subject = subject
        self.data = data
        self.clock = core.Clock()
        self.trial = self.subject.get("TrialsCompleted")
        self.trialOrder = self.subject.get("TrialOrder")
        self.condition = self.subject.get("ConditionID")
        self.experimentType = self.subject.get("ExperimentType")
        self.eyeTracked = self.subject.get("EyeTracked")
        self.window = visual.Window(constants.MONITOR_RESOLUTION, color=(-1, -1, -1), monitor="testMonitor",
                                    units="pix")
        self.guide_text = visual.TextStim(win=self.window, name='guide_text',
                                          text=None, font='Arial',
                                          pos=(0, 200), color=constants.COLOR_WHITE,
                                          colorSpace='rgb255')
        self.trackEye = trackEye
        self.implant = p2p.implants.PRIMA40()
        self.imageStimuli = visual.ImageStim(self.window,
                                             image=None,
                                             pos=[0, 0])

        self.model = p2p.models.ScoreboardModel(xrange=(-2, 2), yrange=(-2, 2), xystep=0.02, rho=10)
        self.model.build()
        self.stimuli = None
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

    def load_pre_stimulus(self):
        if self.condition == 'Study3':
            targetWord = self.data['CompleteData'][self.trialOrder[self.trial]]['ObjectSearchExperiment']['Label']
            self.guide_text.text = targetWord
            self.guide_text.pos = (0, 300)
            self.guide_text.draw()

    def stimuli_shown(self, path):
        background = np.zeros(constants.BACKGROUND_SIZE, np.uint8)

        img = cv2.imread(path)
        H, W, C = img.shape
        start = [constants.Psych2CV[0] - int(H / 2), constants.Psych2CV[1] - int(W / 2)]

        background[start[0]:start[0] + H, start[1]:start[1] + W, :] = img

        return background

    def landoltimage(self, trialnum):
        logMAR = 1.2 - trialnum / 10
        radius_of_ring_deg = ((math.tan(1 / 12 * math.pi / 180) * 20 / 10 ** (
            -logMAR) * 304.8) / constants.PIXEL_SIZE) / 2

        Landolt_ring_outer = visual.Circle(win=self.window, name='Landolt_ring_outer',
                                           fillColor=(1.0, 1.0, 1.0),
                                           radius=radius_of_ring_deg, ori=0, pos=[0, 0], lineColor=(1.0, 1.0, 1.0),
                                           autoLog=True)
        Landolt_ring_inner = visual.Circle(win=self.window, name='Landolt_ring_inner', fillColor=(-1.0, -1.0, -1.0),
                                           radius=3 / 5 * radius_of_ring_deg, ori=0, pos=[0, 0],
                                           lineColor=(-1.0, -1.0, -1.0), autoLog=True)
        Landolt_C = visual.Rect(win=self.window, name='Landolt_C', fillColor=(-1, -1, -1),
                                lineColor=(-1, -1, -1), ori=0, pos=[-radius_of_ring_deg / 2, 0],
                                width=1.4 * (radius_of_ring_deg), height=2 / 5 * radius_of_ring_deg, autoLog=True)
        Landolt_ring_outer.draw()
        Landolt_ring_inner.draw()
        Landolt_C.draw()

    def load_prima_patch(self, location):

        H, W, C = self.stimuli.shape
        patch = self.stimuli[
                int(H / 2) - location[1] - int(constants.PRIMAXX_PATCH_SIZE / 2): int(H / 2) - location[1] + int(
                    constants.PRIMAXX_PATCH_SIZE / 2),
                int(W / 2) + location[0] - int(constants.PRIMAXX_PATCH_SIZE / 2): int(W / 2) + location[0] + int(
                    constants.PRIMAXX_PATCH_SIZE / 2)]

        if patch.any():
            a = datetime.datetime.now()
            self.implant.stim = ImageStimulus(patch)
            percept = self.model.predict_percept(self.implant).data
            b = datetime.datetime.now()
            c = b - a
            print(c.microseconds)
            percept = np.repeat(percept, 3, axis=2)
            percept = cv2.flip(percept, 0)

            patch = visual.ImageStim(self.window,
                                     image=percept,
                                     pos=[location[0], location[1]])
            patch.size = np.array([constants.PRIMAXX_PATCH_SIZE, constants.PRIMAXX_PATCH_SIZE])

            patch.draw()

    def find_closest_patch(self, location):
        locations = self.data['CompleteData'][self.trialOrder[self.trial]]["Prima"]["Patches"].keys()
        locations = np.array([ast.literal_eval(locs) for locs in locations])
        closestLocation = locations[np.argmin(np.sum((locations - location) ** 2, 1)), :]
        return list(closestLocation)

    def load_precomputed_prima_patch(self, location):

        H, W, C = self.stimuli.shape
        patch = self.stimuli[
                int(H / 2) - location[1] - int(constants.PRIMAXX_PATCH_SIZE / 2): int(H / 2) - location[1] + int(
                    constants.PRIMAXX_PATCH_SIZE / 2),
                int(W / 2) + location[0] - int(constants.PRIMAXX_PATCH_SIZE / 2): int(W / 2) + location[0] + int(
                    constants.PRIMAXX_PATCH_SIZE / 2)]

        if patch.any():
            closestLocation = self.find_closest_patch(location)
            path = self.data['CompleteData'][self.trialOrder[self.trial]]["Prima"]["Patches"][str(closestLocation)]

            self.imageStimuli.image = path
            self.imageStimuli.pos = closestLocation
            self.imageStimuli.draw()

    def load_stimulus(self):
        self.stimuli = self.stimuli_shown(self.data['ImagePaths'][self.trialOrder[self.trial]])
        stop = False

        eyePosition = [0, 0]

        flag = 0
        if self.experimentType != "BL":
            if self.trackEye:
                while not stop:
                    keys = event.getKeys()

                    eye_event = self.eyeTracker.getNextData()

                    if eye_event == constants.FIXATION_START:
                        eye_data = self.eyeTracker.getNewestSample(self.eyeTracked, (0, 0))
                        if eye_data != (-1, -1):
                            eyePosition = (int(eye_data[0] - constants.MONITOR_RESOLUTION[0] / 2),
                                           int(-eye_data[1] + constants.MONITOR_RESOLUTION[1] / 2))

                            a = datetime.datetime.now()
                            self.load_precomputed_prima_patch(eyePosition)
                            b = datetime.datetime.now()
                            c = b - a
                            print(c.microseconds)
                            self.window.flip()
                            # flag = 1

                            # if not gazeOkayRegion.contains(*eyePosition):
                            #    flag = 0

                    if len(keys):
                        if constants.EVENT_PROCEED_KEY in keys:
                            stop = True
            else:
                a = datetime.datetime.now()
                self.load_precomputed_prima_patch(eyePosition)
                b = datetime.datetime.now()
                c = b - a
                print(c.microseconds)
                self.window.flip()
                taskUtils.wait_for_user_input()
        else:
            self.imageStimuli.image = self.data['ImagePaths'][self.trialOrder[self.trial]]
            self.imageStimuli.draw()
            self.window.flip()
            taskUtils.wait_for_user_input()

        self.window.flip()

        # done = False
        # while not done:
        #   keys = event.getKeys()
        #  if constants.EVENT_PROCEED_KEY in keys:
        #     done = True
        event.clearEvents()

    def load_post_stimulus(self):

        if self.condition == 'Study2':
            self.guide_text.text = "Find the given object in the scene. Press spacebar to continue"
            if not self.subject.has("Descriptions"):
                self.subject.create("Descriptions", "Data", [])

            text = visual.TextStim(win=self.window, name='text',
                                   text=None,
                                   font='Arial',
                                   pos=(0, 0),
                                   color=constants.COLOR_WHITE, colorSpace='rgb255')
            done = False
            modify = False
            self.guide_text.text = " Enter your description below. Once done, press ENTER"
            self.guide_text.draw()
            self.window.flip()
            while not done:
                keys = event.getKeys()

                if len(keys):
                    text, done, modify = taskUtils.user_text_input_converter(keys, text, modify)
                    text.draw()
                    self.guide_text.draw()
                    self.window.flip()

            self.subject.append("Descriptions", text.text)

        elif self.condition == "Study3" or self.condition == "Study4":

            if self.condition == "Study3":
                data_type = "ObjectLocation"
                if not self.subject.has(data_type):
                    self.subject.create("ObjectLocation", "Data", [])
                self.guide_text.text = "Click on the left or right box to select the object location and press spacebar"
            else:
                data_type = "SalientLocation"
                if not self.subject.has(data_type):
                    self.subject.create("SalientLocation", "Data", [])
                self.guide_text.text = "Click on the left or right box to select the most salient location and press " \
                                       "spacebar "
            mouse = event.Mouse()
            leftRectVert = ((-100, 50), (-100, -50), (0, -50), (0, 50))
            leftRect = visual.ShapeStim(self.window, vertices=leftRectVert, lineWidth=2, lineColor="white")

            rightRectVert = ((0, 50), (0, -50), (100, -50), (100, 50))
            rightRect = visual.ShapeStim(self.window, vertices=rightRectVert, lineWidth=2, lineColor="white")

            done = False
            clicked = False
            clickedSide = ''
            while not done:
                if mouse.isPressedIn(shape=leftRect):
                    leftRect.fillColor = 'green'
                    rightRect.fillColor = None
                    clickedSide = constants.LEFT
                    clicked = True

                elif mouse.isPressedIn(shape=rightRect):
                    leftRect.fillColor = None
                    rightRect.fillColor = 'green'
                    clickedSide = constants.RIGHT
                    clicked = True

                leftRect.draw()
                rightRect.draw()
                self.guide_text.draw()
                self.window.flip()

                keys = event.getKeys()
                if constants.EVENT_PROCEED_KEY in keys and clicked:
                    done = True

            self.subject.append(data_type, clickedSide)
        event.clearEvents()

    def save_subject_data(self):

        if self.trackEye:
            self.get_eyeTracker_data()

            self.subject.append('EyeTrackData', self.eyeTrackerData.copy())

        self.subject.update('TrialsCompleted', self.trial)

    def quit_experiment(self):
        self.task_message("Observer force quit the experiment on trial %d" % (self.trial + 1))
        if self.trackEye:
            if self.eyeTracker.getStatus() == "RECORDING":
                self.eyeTracker.stopEyeTracking()
            if self.eyeTracker.getStatus() != "OFFLINE":
                self.eyeTracker.closeConnectionToEyeTracker()

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

        events['start'] = self.stimulus_off + ((events['start'] - start_stimulus_time).astype('float64') / 1000)
        events['end'] = self.stimulus_off + ((events['end'] - start_stimulus_time).astype('float64') / 1000)

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

            taskUtils.guide_text(self.window, self.trial, self.condition)
            taskUtils.draw_fixation(self.window, [0, -300])
            self.window.flip()

    def fixation_routine(self):
        fixating = False
        fixationDone = False
        event.clearEvents()
        gaze_check = False
        while not fixationDone:
            keys = event.getKeys()

            if constants.EVENT_PROCEED_KEY in keys and fixating and not gaze_check:
                fixationDone = True

            elif len(keys) > 0:
                if keys[-1] in self.action and constants.EVENT_PROCEED_KEY not in keys:
                    self.action[keys[-1]]()

            eye_data = self.eyeTracker.getNewestSample(self.eyeTracked, (0, 0))

            if eye_data != (-1, -1):
                eyePosition = (eye_data[0] - constants.MONITOR_RESOLUTION[0] / 2,
                               -eye_data[1] + constants.MONITOR_RESOLUTION[1] / 2)
                # switch to psychopy window coordinates (0,0) middle of screen

                gazeOkayRegion = visual.Circle(self.window, radius=constants.CROSS_SIZE / 2,
                                               units="pix", pos=[0, -300], lineWidth=2,
                                               lineColorSpace="rgb255", lineColor=constants.COLOR_WHITE)

                fixating = gazeOkayRegion.contains(*eyePosition)
                if len(keys) > 0:
                    if keys[-1] == constants.GAZE_CHECK_KEY:
                        gaze_check = True
                    elif keys[-1] == constants.REMOVE_GAZE_CHECK_KEY:
                        gaze_check = False
                if gaze_check:
                    taskUtils.draw_gaze(self.window, eyePosition)
            self.load_pre_stimulus()
            taskUtils.guide_text(self.window, self.trial, self.condition)
            taskUtils.draw_fixation(self.window, [0, -300])
            self.window.flip()

    def run_trials(self):
        n = self.trial
        for _ in self.trialOrder[n:]:
            event.clearEvents()
            self.task_message("Fixation loaded.")
            taskUtils.guide_text(self.window, self.trial, self.condition)

            if self.trackEye:
                if self.eyeTracker.getStatus() != "RECORDING":
                    self.eyeTracker.startEyeTracking(self.trial + 1, calibTrial=False)
                self.eyeTracker.resetEventQue()
                self.fixation_routine()
            else:
                self.load_pre_stimulus()
                taskUtils.draw_fixation(self.window, [0, -300])
                self.window.flip()
                self.action[taskUtils.wait_for_user_input()]()

            # self.forceFixateRoutine()
            self.window.flip()

            self.load_stimulus()
            self.task_message("STIMULUS PRESENTATION ROUTINE starting.")
            self.stimulus_off = self.clock.getTime()
            core.wait(constants.STIMULI_DURATION)
            self.window.flip()
            self.stimulus_on = self.clock.getTime()

            self.task_message("STIMULUS PRESENTATION ROUTINE ended.")
            if self.trackEye:
                self.eyeTracker.stopEyeTracking()

            self.trial += 1
            self.save_subject_data()
            self.load_post_stimulus()

            self.window.flip()

        self.guide_text.text = "Thank you for participating in the experiment!! :) press space bar to exit"
        self.guide_text.draw()
        self.window.flip()
        taskUtils.wait_for_user_input()
