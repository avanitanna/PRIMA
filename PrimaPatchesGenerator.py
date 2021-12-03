import cv2
import numpy as np
import math
import constants
import json_lines
import jsonlines
import os
import pulse2percept as p2p
from pulse2percept.stimuli import ImageStimulus
import glob

imgsPath = []
items = []
implant = p2p.implants.PRIMA40()
ptypes = {1: 40,
          2: 55,
          3: 75,
          4: 100}

rho = {1: 35,
          2: 50,
          3: 70,
          4: 85}

prosthesis = {1: p2p.implants.PRIMA40(),
              2: p2p.implants.PRIMA55(),
              3: p2p.implants.PRIMA75(),
              4: p2p.implants.PRIMA()}






for k in range(1, 5):
    with open(os.path.join('JSONS', "LandoltLibrary.jsonl"), 'rb') as f:  # opening file in binary(rb) mode
        for item in json_lines.reader(f):
            # paths = []
            imgsPath.append(os.path.join('data', 'Landolt_C_New_' + str(k), item['img_fn']))
            it = item.copy()
            it["Prima" + str(ptypes[k])] = {}
            it["Prima" + str(ptypes[k])]["Patches"] = {}
            it["Prima" + str(ptypes[k])]["Patches"]["img_fn"] = []
            items.append(it)

print(len(items))
i = 0
j = 0
k = 1
model = p2p.models.ScoreboardModel(xrange=(-1.8, 1.8), yrange=(-1.8, 1.8), xystep=0.02, rho=rho[k])
model.build()
dxy = constants.PRIMAXX_PATCH_SIZE
for path in imgsPath:
    logMAR = 1.2 - j / 10
    logMAR = round(logMAR, 1)
    img = cv2.imread(path)
    H, W, C = img.shape
    XSH = dxy - ((dxy * 2 + H) % dxy)

    XSH1 = int(XSH / 2)
    XSH2 = XSH - XSH1

    XSW = dxy - ((dxy * 2 + W) % dxy)

    XSW1 = int(XSW / 2)
    XSW2 = XSW - XSW1

    background = np.zeros((2 * dxy + H + XSH, 2 * dxy + W + XSW, C), np.uint8)
    background[dxy + XSH1:dxy + H + XSH1, dxy + XSW1:dxy + W + XSW1, :] = img

    Hh, Ww, Cc = background.shape
    Hh = int((constants.BACKGROUND_SIZE[0] - Hh) / 2)
    Ww = int((constants.BACKGROUND_SIZE[1] - Ww) / 2)
    m = 0
    l = 0
    if i == 0:
        heightStrides = 10
        widthStrides = 30
        strideHlength = int((background.shape[0] - dxy) / heightStrides)
        strideWlength = int((background.shape[1] - dxy) / widthStrides)
    else:
        heightStrides = int((background.shape[0] - dxy) / strideHlength)
        widthStrides = int((background.shape[1] - dxy) / strideWlength)
    print(strideHlength)
    print(strideWlength)
    print(i)
    for m in range(heightStrides):
        for l in range(widthStrides):
            patch = background[m * strideHlength: m * strideHlength + dxy, l * strideWlength:l * strideHlength + dxy, :]
            if patch.any():
                prosthesis[k].stim = ImageStimulus(patch)
                percept = model.predict_percept(prosthesis[k]).data
                percept = np.repeat(percept, 3, axis=2)

                resized = cv2.resize(percept, (dxy, dxy), interpolation=cv2.INTER_AREA) * 255
                centreCoord = [Hh + int(m * strideHlength + (dxy - 1) / 2), Ww + int(l * strideWlength + (dxy - 1) / 2)]
                if m == 0 and l == 0:
                    pat = "data/PrimaPatches/Landolt_C_New_" + str(k) + "/" + str(logMAR) + "/*"
                    print(pat)
                    files = glob.glob(pat)
                    for f in files:
                        os.remove(f)

                ppath = "Landolt_C_New_" + str(k) + "/" + str(logMAR) + "/" + str(centreCoord[0]) + "_" + str(
                    centreCoord[1]) + ".bmp"
                cv2.imwrite("data/PrimaPatches/" + ppath, resized)
                print(ppath)


                items[i]["Prima" + str(ptypes[k])]["Patches"]["img_fn"].append(ppath)

    j += 1
    i += 1
    if j == 13:
        k += 1

        if k == 4:
            dxy = constants.PRIMA_PATCH_SIZE
            model = p2p.models.ScoreboardModel(xrange=(-3.6, 3.6), yrange=(-3.6, 3.6), xystep=0.02, rho=rho[k])
            model.build()
        else:
            model = p2p.models.ScoreboardModel(xrange=(-1.8, 1.8), yrange=(-1.8, 1.8), xystep=0.02, rho=rho[k])
            model.build()
        j = 0

k = 1
j = 0
with jsonlines.open('JSONS/LandoltLibrary_withPrimaPatches.jsonl', mode='w') as writer:
    for item in items:
        writer.write(item)
