from User import User
import constants
import json_lines
import os
import cv2
import numpy as np

Subjects = {0: "NH",
            1: "DK",
            2: "MFP"
}
def psychopy_image(path):
    background = np.ones(constants.BACKGROUND_SIZE, np.uint8) * 128
    img = cv2.imread(path)
    aspectRatio = img.shape[1] / img.shape[0]
    dim = (int(aspectRatio * constants.IMG_HEIGHT), constants.IMG_HEIGHT)
    H = constants.IMG_HEIGHT
    W = dim[0]
    start = [constants.Psych2CV[0] - int(H / 2), constants.Psych2CV[1] - int(W / 2)]
    resized_img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    background[start[0]:start[0] + H, start[1]:start[1] + W, :] = resized_img
    return background


imgsPath = []
items = []
with open('JSONS/eye_track_exp1.jsonl', 'rb') as f:  # opening file in binary(rb) mode
    for item in json_lines.reader(f):
        imgsPath.append(os.path.join('data/EyeTrackingExp1Images', item['img_fn']))
        items.append(item)
i = 0

SM = User("DK", "Study1")
order = SM.get("TrialOrder")
eyeData = SM.get("EyeTrackData")
trials = SM.get("TrialsCompleted")
#print(eyeData)
while i < trials:
    img = psychopy_image(imgsPath[order[i]])
    #print(eyeData[i])
    j=0
    for fixations in eyeData[i]['AllFixations']:
        img = cv2.circle(img, (int(fixations[0]), int(fixations[1])), 3, (255, 0, 0), 2)
        if j > 0:
            img = cv2.line(img, (int(oldfixations[0]), int(oldfixations[1])), (int(fixations[0]), int(fixations[1])), (255, 0, 0), 2)
        oldfixations = fixations
        j+=1


    #cv2.imshow("asrg", img)
    #cv2.waitKey(0)
    cv2.imwrite("Documents/DK/img" + str(i) + ".jpeg", img)
    i += 1
