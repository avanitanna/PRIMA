import numpy as np
import matplotlib.pyplot as plt
import pulse2percept as p2p
from pulse2percept.stimuli import ImageStimulus
import cv2


#implant = p2p.implants.AlphaAMS()
implant = p2p.implants.PRIMA40()
#model = p2p.models.ScoreboardModel(xrange=(-10, 10), yrange=(-10, 10), rho=10, xystep=0.02)
model = p2p.models.ScoreboardModel(xrange=(-2.5, 2), yrange=(-2, 2), xystep=0.02, rho=10)
model.build()
img = plt.imread("data/EyeTrackingExp1Images/Image2.jpeg", 0)

#img = 1-img
print(np.max(img))
cv2.imshow("wef", img)
cv2.waitKey(0)
print(img.shape)
resizedImg = cv2.resize(img, (11,11), interpolation = cv2.INTER_AREA)
print(np.max(img))
print(np.max(resizedImg))
cv2.imshow("wefd", resizedImg)
cv2.waitKey(0)
cv2.imwrite("temp1.png", resizedImg*255)
print(ImageStimulus(resizedImg))
implant.stim = ImageStimulus(img)

percept = model.predict_percept(implant).data
cv2.imshow("sf", percept)
cv2.waitKey(0)
print(percept.shape)
