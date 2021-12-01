import cv2
import numpy as np
import math
import constants
import jsonlines
items = []
data = {}
for trialnum in range(13):
    logMAR = 1.2 - trialnum / 10
    radius = int(((math.tan(1 / 12 * math.pi / 180) * 6096 / 10 ** (-logMAR)) / constants.PIXEL_SIZE) / 2)

    number_of_Cs = round(constants.BACKGROUND_SIZE[0] / (2*radius))
    if number_of_Cs >= 5:
        number_of_Cs = 5
    background = np.zeros((2 * radius, 2 * radius, 3), np.uint8)
    background = cv2.circle(background, [radius, radius], radius, (255, 255, 255), -1)
    background = cv2.circle(background, [radius, radius], int((3 / 5) * radius), (0, 0, 0), -1)
    landolt_C_0 = cv2.rectangle(background.copy(), (radius, int(4 / 5 * radius)), (2 * radius, int(6 / 5 * radius)), (0, 0, 0),-1)
    landolt_C_90 = cv2.rectangle(background.copy(), (int(4 / 5 * radius), radius), ( int(6 / 5 * radius), 0), (0, 0, 0),
                                -1)
    landolt_C_180 = cv2.rectangle(background.copy(), (0, int(4 / 5 * radius)), (radius, int(6 / 5 * radius)), (0, 0, 0),
                                -1)
    landolt_C_270 = cv2.rectangle(background.copy(), (int(4 / 5 * radius), radius), (int(6 / 5 * radius), 2 * radius), (0, 0, 0),
                                -1)
    logMAR = round(logMAR, 1)
    All_Cs = np.array([landolt_C_0, landolt_C_90, landolt_C_180, landolt_C_270])
    order = np.random.randint(4, size=number_of_Cs)
    Cs = All_Cs[order]
    Background = np.zeros((2 * radius, ((2 * number_of_Cs) - 1) * 2*radius, 3), np.uint8)
    i = 0
    for C in Cs:
        Background[0:2*radius, 4*i*radius:4*i*radius + 2*radius, :] = C
        i+=1

    data["img_id"] = "val-" + str(trialnum)
    data["img_fn"] = str(logMAR) + ".bmp"
    items.append(data.copy())
    #cv2.imshow("Back", Background)
    #cv2.waitKey(0)
    #print(np.array(data["img_fn"])[order])
    cv2.imwrite("data/Landolt_C_New/" + str(logMAR) + ".bmp", Background)
    '''
    cv2.imwrite("data/Landolt_C/90_" + str(logMAR) + ".bmp", landolt_C_90)
    cv2.imwrite("data/Landolt_C/180_" + str(logMAR) + ".bmp", landolt_C_180)
    cv2.imwrite("data/Landolt_C/270_" + str(logMAR) + ".bmp", landolt_C_270)
    '''

with jsonlines.open('JSONS/LandoltLibrary.jsonl', mode='w') as writer:
    for item in items:
        writer.write(item)

