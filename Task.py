from psychopy import visual, core, event  # import some libraries from PsychoPy
import numpy as np
import taskUtils
import constants


class Task:
    def __init__(self, subject, data):
        self.subject = subject
        self.data = data
        self.clock = core.Clock()
        self.trial = self.subject.get_trial_number()
        self.trialOrder = self.subject.get_trial_order()
        self.condition = self.subject.get_condition()
        self.window = visual.Window(constants.MONITOR_RESOLUTION, monitor="testMonitor", units="pix")

    def task_message(self, message):
        self.subject.append_data_field((message, self.clock.getTime()), "TaskMessages")

    def load_stimulus(self):
        taskUtils.guide_text(self.window, self.trial, self.condition)
        stimulus = visual.ImageStim(self.window, image=self.data['ImagePaths'][self.trialOrder[self.trial]], pos=[0, 100])
        aspectRatio = stimulus.size[0] / stimulus.size[1]
        stimulus.size = np.array([aspectRatio * constants.IMG_HEIGHT, constants.IMG_HEIGHT])
        stimulus.draw()
        self.window.flip()
        core.wait(constants.STIMULI_DURATION)

    def save_subject_data(self):
        self.subject.update_data_field(self.trial, 'TrialsCompleted')

    def run_trials(self):
        n = self.trial
        for ID in self.trialOrder[n:]:
            self.task_message("Fixation loaded.")
            taskUtils.guide_text(self.window, self.trial, self.condition)
            quitExperiment = taskUtils.draw_fixation(self.window, [0, -300])
            if quitExperiment:
                self.task_message("Observer force quit the experiment on trial %d" % self.trial)
                self.window.close()
                core.quit()
                event.clearEvents()
                break
            self.task_message("Stimulus loaded.")
            self.load_stimulus()
            self.trial += 1
            self.save_subject_data()
            self.window.flip()