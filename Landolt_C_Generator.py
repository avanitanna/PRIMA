import cv2
import numpy as np
import math
import constants
import jsonlines

j=1
dxy = 0
for k in range(1):
    items = []
    data = {}
    for trialnum in range(13):
        logMAR = 1.2 - trialnum / 10
        radius = int(((math.tan(1 / 12 * math.pi / 180) * constants.OBSERVER_VIEWING_DISTANCE / 10 ** (-logMAR)) / constants.PIXEL_SIZE) / 2)

        number_of_Cs = int((round(constants.BACKGROUND_SIZE[0] / (2*radius)) + 1) / 2)


        if number_of_Cs >= 5:
            number_of_Cs = 5
        print(number_of_Cs)
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
        Background = np.zeros((2 * (radius + dxy), 2* (((2 * number_of_Cs) - 1) * radius + dxy), 3), np.uint8)
        i = 0
        for C in Cs:
            Background[dxy:2*radius+dxy, dxy + 4*i*radius:4*i*radius + 2*radius + dxy, :] = C
            i+=1

        data["img_id"] = "val-" + str(trialnum)
        data["img_fn"] = str(logMAR) + ".bmp"
        items.append(data.copy())
        cv2.imshow("Back", Background)
        cv2.waitKey(0)
        #print(np.array(data["img_fn"])[order])
        cv2.imwrite("data/Landolt_C_New_" + str(k) + "/" + str(logMAR) + ".bmp", Background)

        '''
        cv2.imwrite("data/Landolt_C/90_" + str(logMAR) + ".bmp", landolt_C_90)
        cv2.imwrite("data/Landolt_C/180_" + str(logMAR) + ".bmp", landolt_C_180)
        cv2.imwrite("data/Landolt_C/270_" + str(logMAR) + ".bmp", landolt_C_270)
        '''
        j+=1
    k += 1

with jsonlines.open('JSONS/LandoltLibrary.jsonl', mode='w') as writer:
    for item in items:
        writer.write(item)

