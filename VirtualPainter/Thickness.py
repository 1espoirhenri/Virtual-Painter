import cv2
import time
import numpy as np
import HandTrackingModules as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbc
def ControlBrightness(length):#config brightness void
    last_update_time = 0
    brightness_control = np.interp(length, [50, 300], [0, 100])
    briBar = np.interp(length, [50, 300], [400, 150])
    briPer = np.interp(length, [50, 300], [0, 100])

    print(int(length), brightness_control)
    current_time = time.time()
    # set light into level
    if brightness_control > 0 and brightness_control < 25 and (current_time - last_update_time) > 0.5:
        sbc.set_brightness(25, force=True)
        last_update_time = current_time
    elif brightness_control > 25 and brightness_control < 50 and (current_time - last_update_time) > 0.5:
        sbc.set_brightness(50, force=True)
        last_update_time = current_time
    elif brightness_control > 50 and brightness_control < 75 and (current_time - last_update_time) > 0.5:
        sbc.set_brightness(75, force=True)
        last_update_time = current_time
    elif brightness_control > 75 and brightness_control < 100 and (current_time - last_update_time) > 0.5:
        sbc.set_brightness(100, force=True)
        last_update_time = current_time
    return briBar,briPer
def ControlVolume(length): #config volume void
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volRange = volume.GetVolumeRange()
    minVol = volRange[0]
    maxVol = volRange[1]
    vol = np.interp(length, [50, 300], [minVol, maxVol])
    volBar = np.interp(length, [50, 300], [400, 150])
    volPer = np.interp(length, [50, 300], [0, 100])
    print(int(length), vol)
    volume.SetMasterVolumeLevel(vol, None)
    return volBar,volPer


def main():
    wCam, hCam = 640, 480
    ################################
    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)
    pTime = 0

    detector = htm.HandDetector(staticMode=False, maxHands=2, modelComplexity=1, detectionCon=0.5, minTrackCon=0.5)
    enable_bri = False
    enable_vol = False
    while True:
        success, img = cap.read()
        hands, img = detector.findHands(img, draw=True, flipType=True)
        if len(hands) == 2:
            # Information for the first hand detected
            hand1 = hands[0]  # Get the first hand detected
            lmList1 = hand1["lmList"]  # List of 21 landmarks for the first hand
            bbox1 = hand1["bbox"]  # Bounding box around the first hand (x,y,w,h coordinates)
            center1 = hand1['center']  # Center coordinates of the first hand
            handType1 = hand1["type"]  # Type of the first hand ("Left" or "Right")

            # Information for the second hand
            hand2 = hands[1]
            lmList2 = hand2["lmList"]
            bbox2 = hand2["bbox"]
            center2 = hand2['center']
            handType2 = hand2["type"]
            # anh thu ve bi nguoc, nen dao lai
            if handType1 == "Right":
                handLeft = hand1
                handRight = hand2
            else:
                handLeft = hand2
                handRight = hand1

            # Count the number of fingers up for the second hand
            fingers_left = detector.fingersUp(handLeft)
            finger_countLeft = fingers_left.count(1)
            fingers_right = detector.fingersUp(handRight)
            finger_countRight = fingers_right.count(1)
            # Calculate distance between the index fingers of both hands and draw it on the image
            length, info, img = detector.findDistance(handRight["lmList"][8][0:2], handLeft["lmList"][8][0:2], img, color=(255, 0, 0),
                                                      scale=10)


            if finger_countRight == 5 and finger_countLeft == 5: #save at that point
                enable_bri = False
                enable_vol = False
            # the condition if finger list finger[1, 1, 1, 0, 0] the index following thump, index, middle finger is up
            #and total fingers are up is 3
            if (fingers_right[0] == 1 and fingers_right[1] == 1 and finger_countRight == 2) or enable_bri == True:
                enable_bri = True
                # get landmarks


                cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
                briBar, briPer = ControlBrightness(length)
                cv2.rectangle(img, (50, int(briBar)), (85, 400), (255, 0, 0), cv2.FILLED)
                cv2.putText(img, f'brightness: {int(briPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                            1, (255, 0, 0), 3)

            elif (fingers_left[0] == 1 and fingers_left[1] == 1 and finger_countLeft == 2) or enable_vol == True:
                enable_vol = True
                volBar, volPer = ControlVolume(length)
                cv2.rectangle(img, (50, 150), (85, 400), (255,127,80), 3)
                cv2.rectangle(img, (50, int(volBar)), (85, 400), (255,127,80), cv2.FILLED)
                cv2.putText(img, f'voulme: {int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                            1, (255,127,80), 3)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX,
                    1, (255, 0, 0), 3)
        cv2.imshow("Img", img)
        cv2.waitKey(1)

if __name__ == '__main__':
    main()