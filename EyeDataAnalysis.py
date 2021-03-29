from User import User
import constants
import json_lines
import os
import cv2
import numpy as np

#Subjects = {0: "NH",
#            1: "DK",
#            2: "MFP"
#            }

Subjects = {0: "PC"}

Condition = {0: "Study1",
             1: "Study2",
             2: "Study3",
             3: "Study4"}

Type = {0: 'Main',
        1: 'Practice'}

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
with open(os.path.join('JSONS', 'eye_tracking_experiment.jsonl'), 'rb') as f:  # opening file in binary(rb) mode
    for item in json_lines.reader(f):
        imgsPath.append(os.path.join('data', 'EyeTrackingExp1Images', item['img_fn']))
        items.append(item)

with open(os.path.join('JSONS', 'freeViewingXtras.jsonl'), 'rb') as f:  # opening file in binary(rb) mode
    for item in json_lines.reader(f):
        imgsPath.append(os.path.join('data\EyeTrackingExp1Images', item['img_fn']))
        items.append(item)
i = 0

# print(eyeData)
while i < len(items):
    print(imgsPath[i])
    img = psychopy_image(imgsPath[i])
    attentionMap = np.zeros(img.shape[:2])
    attentionMapSum = np.zeros(img.shape[:2])
    norm = np.zeros(img.shape[:2])
    for j in Subjects:
        subject = User(Subjects[j], Condition[0], Type[0])
        order = subject.get("TrialOrder")
        eyeData = subject.get("EyeTrackData")
        trials = subject.get("TrialsCompleted")
        idx = order.index(i)

        # print(eyeData[i])
        j = 0
        for fixations in eyeData[idx]['AllFixations']:
            #attentionMap[int(fixations[1]), int(fixations[0])] += 1
            attentionMapSum += cv2.circle(attentionMap, (int(fixations[0]), int(fixations[1])),
                                      constants.ATTENTION_SPOT_RADIUS, 1, -1)
            #cv2.imshow("wrfw", attentionMapSum)
            #cv2.waitKey(0)
            # img1 = cv2.circle(img, (int(fixations[0]), int(fixations[1])), 3, (255, 0, 0), 2)
            # if j > 0:
            #    img1 = cv2.line(img1, (int(oldfixations[0]), int(oldfixations[1])), (int(fixations[0]), int(fixations[1])),
            #               (255, 0, 0), 2)
            # oldfixations = fixations
            # j += 1

    #print(np.max(attentionMapSum))
    attentionMap1 = cv2.GaussianBlur(attentionMapSum, (51, 51), sigmaX=5)
    attentionMap1 = np.array(attentionMap1 / np.max(attentionMap1) * 255, np.uint8)
    ColorMap = cv2.applyColorMap(attentionMap1, cv2.COLORMAP_JET)
    alpha = 0.65
    blend = np.array(alpha * ColorMap + (1 - alpha) * img, np.uint8)

    #cv2.imshow("wrfw", blend)
    #cv2.waitKey(0)
    cv2.imwrite("results/Attention_Maps/" + str(i) + ".jpeg", blend)
    print(i)
    i += 1

