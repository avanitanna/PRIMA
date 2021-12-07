## rho = 35, PRIMA 40 - same as desktop experiment
import cv2
import pulse2percept as p2p
from pulse2percept.models import ScoreboardModel
import numpy as np

## Create PRIMA p2p image
model = ScoreboardModel(xrange=(-1.8, 1.8), yrange=(-1.8, 1.8), xystep=0.02, rho=35)
model.build()
implant = p2p.implants.PRIMA40()

implant.stim = p2p.stimuli.ImageStimulus('C:/Users/Apurv/Documents/Unity_Projects/Eye tracking test/Assets/1.2/1.2_4.png')
#implant.stim = p2p.stimuli.ImageStimulus('single_landolt_C.png')
percept = model.predict_percept(implant)
percept.save('C:/Users/Apurv/Documents/Unity_Projects/Eye tracking test/Assets/percept1.2/1.2_4.png')

""" frame = cv2.imread('percept_single_landolt_C.png')
data = {
    'image': cv2.imencode('.png', frame)[1].ravel().tolist()
}



cv2.imshow('p2p-prima', frame) """

