# Colors for psychopy experiment
COLOR_RED = [229, 72, 35]
COLOR_GRAY = [57, 48, 42]
COLOR_WHITE = [255, 255, 255]
COLOR_BACKGROUND = [128, 128, 128]
COLOR_DISABLED = [80, 80, 80]

RATING_GREEN = [50, 255, 50]
RATING_RED = [255, 50, 50]

# code for eyelink
EYE_TRACKED = {"Right": 0,
               "Left": 1}

STARTSACC = 5
ENDSACC = 6

# for rating scale
CONFIDENCE = {8: ['HIGHEST', 'HIGH', 'MEDIUM', 'LOW', 'LOW', 'MEDIUM', 'HIGH', 'HIGHEST'],
              4: ['HIGH', 'LOW', 'LOW', 'HIGH']}

# Image props
IMG_HEIGHT = 700

# Cross props
CROSS_SIZE = 45 # pixels

# General
stimuli_dimensions = (1024, 800) # in pixels for a single slice of the 3D volume (columns, rows) or (x,y) instead of (rows, columns)
MONITOR_RESOLUTION = (1280, 1024)
fixation_duration = 2 # in seconds
num_trials_per_condition = 100
EVENT_PROCEED_KEY = 'space'
RECALIBRATE_KEY = 'c'
STIMULI_DURATION = 2.0

# User data action

GET = "get"
UPDATE = "update"
APPEND = "append"
