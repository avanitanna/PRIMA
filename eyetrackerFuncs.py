# EyeLinkForPsychopyInSUPA.py
#
# Copyright (C) 2011 Wing (Wei-Ying Chen)  modified from pylink ATI and open source code
# Modified by Chris Fajou, pre-April 2015.
# Provides a standard set of functions for using an eye tracker that allows experiment code to be simple and tracker agnostic.( For EyeLink1000)

import pylink
from pylink import getEYELINK
from EyeLinkGraphics import EyeLinkGraphics
import sys, os, gc
from psychopy import visual, info, misc, monitors, event, core
from numpy import array, hstack

#RIGHT_EYE = 1
#LEFT_EYE = 0
#BINOCULAR = 2
HIGH = 1
LOW = 0
WHITE = (255, 255, 255)
GRAY = GREY = (128, 128, 128)
BLACK = (0, 0, 0)
spath = os.path.dirname(sys.argv[0])
if len(spath) != 0: os.chdir(spath)

class Tracker_EyeLink():
    def __init__(self, win, clock, sj="TEST", saccadeSensitivity=LOW, calibrationType='HV9',
                 calibrationTargetColor=WHITE, calibrationBgColor=BLACK, CalibrationSounds=False, screen=(1024, 768),
                 dummy=False):
        '''win: psychopy visual window used for the experiment
          clock: psychopy time clock recording time for whole experiment
          sj: Subject identifier string (affects EDF filename)
          saccadeSensitivity:
            HIGH: Pursuit and neurological work
            LOW:  Cognitive research
          calibrationType:
            H3: Horizontal 3-point
            HV3: 3-point calibration, poor linearization
            HV5: 5-point calibration, poor at corners
            HV9: 9-point calibration, best overall
        calibrationTargetColor and calibrationBgColor:
            RGB tuple, i.e., (255,0,0) for Red
            One of: BLACK, WHITE, GRAY
        calibrationSounds:
            True: enable feedback sounds when calibrating'''

        self.dummy = dummy
        self.win = win
        if self.dummy:
            return

        self.edfFileName = str(sj) + ".EDF"  # Subject name only can put 8 characters
        print("Connecting to eyetracker.")
        self.tracker = pylink.EyeLink()
        self.timeCorrection = clock.getTime() - getEYELINK().trackerTime()
        print("Loading custom graphics")
        # Initializes Experiment Graphics
        # genv = EyeLinkCoreGraphicsPsychopy(self.tracker, win, screen)
        self.genv = EyeLinkGraphics(getEYELINK(), win)
        pylink.openGraphicsEx(self.genv)
        # opendatafile
        # getEYELINK().openDataFile(self.edfFileName)

        # EyeLink Tracker Configuration
        pylink.flushGetkeyQueue();  # Initializes the key queue used by getkey(). It may be called at any time to get rid any of old keys from the queue.
        getEYELINK().setOfflineMode();  # Places EyeLink tracker in off-line (idle) mode. Wait till the tracker has finished the mode transition
        getEYELINK().sendCommand("screen_pixel_coords =  0 0 %d %d" % (tuple(screen)))
        getEYELINK().setCalibrationType(calibrationType)
        getEYELINK().sendCommand(
            "driftcorrect_cr_disable=OFF")  # CF - OFF: turns on drift CORRECT; AUTO: Turns on drift CHECK; ON: Turns off both
        # self.tracker.sendCommand("generate_default_targets = NO")
        # self.tracker.sendCommand("calibration_targets = 512,384 512,417 512,351 402,384 622,384 402,417 622,417 402,351 622,351")
        # self.tracker.sendCommand("validation_targets = 512,384 512,417 512,351 402,384 622,384 402,417 622,417 402,351 622,351")

        getEYELINK().sendMessage("DISPLAY_COORDS  0 0 %d %d" % (tuple(screen)))
        eyelink_ver = getEYELINK().getTrackerVersion()

        if eyelink_ver == 3:
            tvstr = getEYELINK().getTrackerVersionString()
            vindex = tvstr.find("EYELINK CL")
            tracker_software_ver = int(float(tvstr[(vindex + len("EYELINK CL")):].strip()))
        else:
            tracker_software_ver = 0
        if eyelink_ver >= 2:
            getEYELINK().sendCommand("select_parser_configuration %d" % 0)
        else:
            if saccadeSensitivity == HIGH:
                svt, sat = 22, 5000
            else:
                svt, sat = 30, 9500
            getEYELINK().sendCommand("saccade_velocity_threshold = %d" % svt)
            getEYELINK().sendCommand("saccade_acceleration_threshold = %d" % sat)
        if eyelink_ver == 2:  # turn off scenelink camera stuff
            getEYELINK().sendCommand("scene_camera_gazemap = NO")

        # set EDF file contents
        getEYELINK().setFileEventFilter("LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON")
        if tracker_software_ver >= 4:
            getEYELINK().setFileSampleFilter("LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS,HTARGET")
        else:
            getEYELINK().setFileSampleFilter("LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS")

        # set link data (used for gaze cursor)
        getEYELINK().setLinkEventFilter("LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON")
        if tracker_software_ver >= 4:
            getEYELINK().setLinkSampleFilter("LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,HTARGET")
        else:
            getEYELINK().setLinkSampleFilter("LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS")

        # self.tracker.setAcceptTargetFixationButton(1) # This programs a specific button for use in drift correction.

        # Set the calibration settings:
        # pylink.setCalibrationColors(WHITE, BLACK) # Sets the calibration target and background color(foreground_color, background_color)
        if CalibrationSounds:
            pylink.setCalibrationSounds("", "", "")
            pylink.setDriftCorrectSounds("", "off", "off")
        else:
            pylink.setCalibrationSounds("off", "off", "off")
            pylink.setDriftCorrectSounds("off", "off", "off")

        # while len(event.getKeys()) == 0:
        #     1

        print("Beginning tracker setup")
        getEYELINK().doTrackerSetup(width=screen[0], height=screen[1])

    def sendMessage(self, msg):
        '''Record a message to the tracker'''
        # print(msg)
        getEYELINK().sendMessage(msg)

    def sendCommand(self, msg):
        '''Send command to the tracker'''
        # print(msg)
        getEYELINK().sendCommand(msg)

    def resetEventQue(self):
        '''Reset the eyetracker event cue
            usage: use this prior to a loop calling recordFixation() so
            that old fixations or other events are cleared from the
            buffer.'''
        getEYELINK().resetData()

    def getFloatData(self):
        if self.dummy:
            return 0
        getEYELINK().getFloatData()

    def getStatus(self):
        """Return the status of the connection to the eye tracker"""
        if getEYELINK().breakPressed():
            return ("ABORT_EXPT")
        if getEYELINK().escapePressed():
            return ("SKIP_TRIAL")
        if getEYELINK().isRecording() == 0:
            return ("RECORDING")
        if getEYELINK().isConnected():
            return ("ONLINE")
        else:
            return ("OFFLINE")
        return ("UNKNOWN STATUS: " + str(getEYELINK().getStatus()))

    def startEyeTracking(self, trial, calibTrial):# widthPix, heightPix):

        if calibTrial:
            cond = "Test/Calibration Trial"
        else:
            cond = "Non-test/no calibration trial"

        if self.dummy:
            if calibTrial:
                event.waitKeys(keyList=['escape'])
            return

        # Set up each trial with the eye tracker

        message = "record_status_message 'Trial %d %s'" % (trial + 1, cond)
        getEYELINK().sendCommand(message)
        msg = "TRIALID %s" % trial
        getEYELINK().sendMessage(msg)
        # The following does drift correction at the begin of each trial
        if calibTrial:  # Does drift correction and handles the re-do camera setup situations
            pylink.openGraphicsEx(self.genv)
            self.genv.clear_cal_display()
            self.genv.draw_menu_screen()
            getEYELINK().doTrackerSetup()
            # while True:
            # try:
            #     # self.tracker.draw_calibration_screen()
            #     error = getEYELINK().doDriftCorrect(widthPix / 2, heightPix / 2, 1,
            #                                         1)  # 0: the fixation target must be drawn by the user
            #     if error != 27:
            #         # self.tracker.applyDriftCorrect
            #         break
            #     else:
            #         getEYELINK().doTrackerSetup()
            # except:
            #     print("Exception")
            #     break
        # self.tracker.sendCommand('start_drift_correction DATA =1 1 1 1') #CF - start drift correct??
        # self.tracker.applyDriftCorrect() #CF - added to actually correct for drift
        getEYELINK().setOfflineMode()  # CF adds this to stop skipping trials due to not recording
        pylink.msecDelay(50)

        if trial > 0:
            getEYELINK().openDataFile(self.edfFileName)
        error = getEYELINK().startRecording(1, 1, 1,
                                            1)  # start to recording (File_samples, File_events, Link_samples, Link_events); if 1, writes something to EDF file. If 0, disables something recording.
        if error: return error;
        pylink.beginRealTimeMode(100)

        # pylink.getEYELINK().waitForBlockStart(100, 1, 1)
        # pylink.getEYELINK().sendMessage("EYE_USED 1 RIGHT")

    def stopEyeTracking(self):

        if self.dummy:
            return

        # Ends recording: adds 100 msec of data to catch final events
        pylink.endRealTimeMode()
        pylink.pumpDelay(100)
        getEYELINK().stopRecording()

    def retrieveDataFile(self, fileName=None):
        if not self.dummy:
            getEYELINK().setOfflineMode();
            # Close the file and transfer it to Display PC
            getEYELINK().closeDataFile()
            if fileName:
                getEYELINK().receiveDataFile(self.edfFileName, fileName)

    def closeConnectionToEyeTracker(self, eyeMoveFile = None):
        # Clean everything up, save data and close connection to tracker
        if getEYELINK() != None:
            # File transfer and cleanup!
            getEYELINK().setOfflineMode();
            core.wait(0.5)
            # Close the file and transfer it to Display PC
            getEYELINK().closeDataFile()
            #getEYELINK().receiveDataFile(self.edfFileName, eyeMoveFile)
            getEYELINK().close();
            # Close the experiment graphics
            pylink.closeGraphics()
            return "Eyelink connection closed successfully"
        else:
            return "Eyelink not available, not closed properly"

    def getNewestSample(self, eye_tracked, mouse_pos):

        if self.dummy:
            pos = mouse_pos
            pos[0] = +self.win.size[0] / 2 + mouse_pos[0]
            pos[1] = +self.win.size[1] / 2 - mouse_pos[1]
            return pos
        sample = (-1, -1)
        nSData = getEYELINK().getNewestSample()
        #print(nSData.getType())
        if nSData:
            if eye_tracked == 0 and nSData.isRightSample():
                sample = nSData.getRightEye().getGaze()
                # INSERT OWN CODE (EX: GAZE-CONTINGENT GRAPHICS NEED TO BE UPDATED)
            elif eye_tracked == 1 and nSData.isLeftSample():
                sample = nSData.getLeftEye().getGaze()

        return sample

    def getNextData(self):
        if self.dummy:
            return 0
        return getEYELINK().getNextData()

    def getLastData(self):
        return getEYELINK().getLastData()

    def resetData(self):
        if self.dummy:
            return 0
        return getEYELINK().resetData()

    def reset(self):
        return getEYELINK().reset()
