#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

import time
import zmq
import cv2
import pulse2percept as p2p
from pulse2percept.models import ScoreboardModel
import numpy as np

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

#capture = cv2.VideoCapture(0)

#while True:
    #  Wait for next request from client
start = time.time()
#_, frame = capture.read()


## Create PRIMA p2p image
model = ScoreboardModel(xrange=(-2, 2), yrange=(-2, 2), xystep=0.02, rho=20)
model.build()
implant = p2p.implants.PRIMA40()
implant.stim = p2p.stimuli.ImageStimulus('single_landolt_C.png')
percept = model.predict_percept(implant)
percept.save('percept_single_landolt_C.png')
frame = cv2.imread('percept_single_landolt_C.png')
data = {
    'image': cv2.imencode('.png', frame)[1].ravel().tolist()
}
message = socket.recv()
print("Received request: %s" % message)
socket.send_json(data)

end = time.time()
print('FPS:', 1 / (end - start))

cv2.imshow('p2p-prima', frame)
cv2.waitKey(delay=1)
#message = socket.recv()
#print("Received request: %s" % message)

#  Do some 'work'.
#  Try reducing sleep time to 0.01 to see how blazingly fast it communicates
#  In the real world usage, you just need to replace time.sleep() with
#  whatever work you want python to do, maybe a machine learning task?
#time.sleep(1)

#  Send reply back to client
#  In the real world usage, after you finish your work, send your output here
#socket.send(b"World")
