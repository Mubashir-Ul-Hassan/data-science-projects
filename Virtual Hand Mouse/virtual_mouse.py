import cv2
import time
import HandTrackingModule as htm  # Ensure this module is available and correctly named
import pyautogui
import numpy as np

##########################
wCam, hCam = 640, 480
frameR = 100  # Frame Reduction
smoothening = 7

cap = cv2.VideoCapture(0)  # Change to 0 or other values to test different cameras
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0
prevLocX, prevLocY = 0, 0
currLocX, currLocY = 0, 0

detector = htm.HandDetector(maxHands=1)  # Ensure the class name is correctly used
screenWidth, screenHeight = pyautogui.size()

while True:
    # 1 find hand landmark
    success, img = cap.read()
    if not success:
        print("Failed to capture image")
        break

    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)
    
    # 2 Get the tip of the index and middle finger
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        
        # 3 Check which fingers are up
        fingers = detector.fingersUp()
        print(fingers)

        # 4 Only index finger: Moving Mode
        if fingers[1] == 1 and fingers[2] == 0:
            # Convert Coordinates
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, screenWidth))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, screenHeight))

            # Smoothen Values
            currLocX = prevLocX + (x3 - prevLocX) / smoothening
            currLocY = prevLocY + (y3 - prevLocY) / smoothening

            # Move Mouse
            pyautogui.moveTo(screenWidth - currLocX, currLocY)
            prevLocX, prevLocY = currLocX, currLocY

        
        # 5 Both index and middle fingers are up: Clicking Mode
        if fingers[1] == 1 and fingers[2] == 1:
            # Find distance between fingers
            length, img, lineInfo = detector.findDistance(8, 12, img)
            print(length)

            # Click mouse if distance short
            if length < 40:
                pyautogui.click()
    
    # 11 Frame rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    # Display 
    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Exit the loop when 'q' is pressed
        break

cap.release()
cv2.destroyAllWindows()

