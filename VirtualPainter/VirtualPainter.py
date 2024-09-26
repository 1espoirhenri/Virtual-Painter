import cv2
import numpy as np
import time
import os
import HandTrackingModules as htm


#def control_thickness(length):


def main():
    folderPath = "Header"
    myList = os.listdir(folderPath)
    print(myList)
    overlayList = []
    for imPath in myList:
        image = cv2.imread(f'{folderPath}/{imPath}')
        overlayList.append(image)
        print(len(overlayList))
        header = overlayList[0]
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    detector = htm.HandDetector(staticMode=False, maxHands=2, modelComplexity=1, detectionCon=0.5, minTrackCon=0.5)

    #######################
    brush_Thickness = 10
    eraser_Thickness = 100
    drawColor = (255, 0, 255)
    ########################


    xp, yp = 0, 0
    imgCanvas = np.zeros((720, 1280, 3), np.uint8)
    drawColor = (255, 0, 255)

    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img, draw=True, flipType=True)

        if len(hands) == 1:
            # Information for the first hand detected
            hand1 = hands[0]  # Get the first hand detected
            lmList1 = hand1["lmList"]  # List of 21 landmarks for the first hand
            bbox1 = hand1["bbox"]  # Bounding box around the first hand (x,y,w,h coordinates)
            center1 = hand1['center']  # Center coordinates of the first hand
            handType1 = hand1["type"]  # Type of the first hand ("Left" or "Right")

            # Count the number of fingers up for the second hand
            fingers = detector.fingersUp(hand1)
            finger_count = fingers.count(1)
            # Calculate distance between the index fingers of both hands and draw it on the image
            # length, info, img = detector.findDistance(handRight["lmList"][8][0:2], handLeft["lmList"][8][0:2], img,
            #                                           color=(255, 0, 0),
            #                                           scale=10)

            lmList = lmList1
            # tip of index and middle fingers
            x1, y1 = lmList[8][0:2]
            x2, y2 = lmList[12][0:2]

            # 4. If Selection Mode – Two finger are up
            if fingers[1] and fingers[2]:
                # xp, yp = 0, 0
                print("Selection Mode")
                # # Checking for the click
                if y1 < 125:
                    if 250 < x1 < 450:
                        header = overlayList[0]
                        drawColor = (255, 0, 255)
                    elif 550 < x1 < 750:
                        header = overlayList[1]
                        drawColor = (255, 0, 0)
                    elif 800 < x1 < 950:
                        header = overlayList[2]
                        drawColor = (0, 255, 0)
                    elif 1050 < x1 < 1200:
                        header = overlayList[3]
                        drawColor = (0, 0, 0)
                cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv2.FILLED)

            # 5. If Drawing Mode – Index finger is up
            if fingers[1] and fingers[2] == False:

                cv2.circle(img, (x1, y1), 15, drawColor, cv2.FILLED)
                print("Drawing Mode")
                if xp == 0 and yp == 0:
                    xp, yp = x1, y1
                    if brush_Thickness > 100:
                        brush_Thickness = 90
                    cv2.line(img, (xp, yp), (x1, y1), drawColor, brush_Thickness)

                if drawColor == (0, 0, 0):
                    if eraser_Thickness > 100:
                        eraser_Thickness = 90
                    cv2.line(img, (xp, yp), (x1, y1), drawColor, eraser_Thickness)
                    cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, eraser_Thickness)

                else:
                    if brush_Thickness > 90:
                        brush_Thickness = 90
                    cv2.line(img, (xp, yp), (x1, y1), drawColor, brush_Thickness)
                    cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brush_Thickness)

            xp, yp = x1, y1

            # # Clear Canvas when all fingers are up
            # img = cv2.addWeighted(img,0.5,imgCanvas,0.5,0)
        elif len(hands) == 2:
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
            if handType1 == "Left":
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
            if finger_countLeft == 1 and finger_countRight == 1:
                # Calculate distance between the index fingers of both hands and draw it on the image
                length, info, img = detector.findDistance(handRight["lmList"][8][0:2], handLeft["lmList"][8][0:2], img,
                                                          color=(255, 0, 0),
                                                          scale=10)
                brush_thick = np.interp(length, [50, 300], [0, 90])
                brush_Thickness = int(brush_thick)
        if brush_Thickness > 100:
            brush_Thickness = 90
        cv2.circle(img, (60, 600), brush_Thickness, drawColor, cv2.FILLED)
        imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
        _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
        imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
        imgInv = cv2.resize(imgInv, (img.shape[1], img.shape[0]))
        imgCanvas = cv2.resize(imgCanvas, (img.shape[1], img.shape[0]))

        # if imgInv.dtype != img.dtype:
        #     imgInv = imgInv.astype(img.dtype)
        #
        # if imgCanvas.dtype != img.dtype:
        #     imgCanvas = imgCanvas.astype(img.dtype)
        img = cv2.bitwise_and(img, imgInv)
        img = cv2.bitwise_or(img, imgCanvas)
        # Setting the header image
        img[0:125, 0:1280] = header
        print(xp, yp)
        cv2.imshow('Image', img)
        cv2.waitKey(1)


if __name__ == '__main__':
    main()