from psychopy import visual, core, event  # import some libraries from PsychoPy
import constants


def draw_fixation(window, position=None):
    if position is None:
        position = [0, 0]

    x = position[0]
    y = position[1]
    size = constants.CROSS_SIZE
    # fixation = visual.GratingStim(win=window, size=0.5, pos=location, sf=0, rgb=-1)
    fixVerts = ((x, y - size / 2), (x, y + size / 2), (x, y), (x - size / 2, y), (x + size / 2, y))
    fixation = visual.ShapeStim(window, vertices=fixVerts, lineWidth=2, closeShape=False,
                                lineColor="white")
    guideText = visual.TextStim(window, colorSpace='rgb255', color=constants.COLOR_WHITE,
                                text="Fixate at the cross and press spacebar to continue.")
    # draw the stimuli and update the window

    fixation.draw()
    guideText.draw()


def guide_text(window, trial, conditionID):
    trialNumber = visual.TextStim(window, pos=(0 - window.size[1] / 2 * .7, window.size[1] / 2 * .9),
                                  colorSpace='rgb255', color=constants.COLOR_WHITE, bold=True, )
    condition = visual.TextStim(window, pos=(0 + window.size[1] / 2 * .7, window.size[1] / 2 * .9),
                                colorSpace='rgb255', color=constants.COLOR_WHITE, bold=True, )

    trialNumber.text = "Trial Number: {0}".format(trial + 1)
    trialNumber.draw()
    condition.text = "Condition: {0}".format(conditionID)
    condition.draw()


def draw_gaze(window, position=None):
    gaze = visual.Circle(window, radius=3, units="pix", pos=position, lineWidth=2,
                         lineColorSpace="rgb255", lineColor=constants.COLOR_WHITE)
    gaze.draw()


def wait_for_user_input():
    while True:
        keys = event.getKeys()
        if constants.EVENT_PROCEED_KEY in keys:
            return constants.EVENT_PROCEED_KEY
        elif constants.QUIT_EXPERIMENT_KEY in keys:
            return constants.QUIT_EXPERIMENT_KEY
        elif constants.RECALIBRATE_KEY in keys:
            return constants.RECALIBRATE_KEY
