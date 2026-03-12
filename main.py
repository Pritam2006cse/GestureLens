import cv2
import numpy as np
import time

from Media_Control import resume_media
from Scroll_Control import scroll_down
from Hand_Tracker import get_hand_landmarks
from Volume_Control import control_volume
from Gesture_Utils import distance,fingers_pos
from Media_Control import pause_media, resume_media
from Scroll_Control import scroll_up,scroll_down

wCam,hCam = 640,480
cap = cv2.VideoCapture(0)
cap.set(3,wCam)
cap.set(4,hCam)
pTime = 0
#last_gesture_time = 0
#cooldown = 2
prev_gesture = None
prev_index_pos = None
canvas = np.zeros((hCam,wCam,3), dtype=np.uint8)
prev_x = None
prev_y = None
smooth_x = 0
smooth_y = 0
alpha = 0.2

while True:
    ret,frame = cap.read()
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(frame, "FPS: {0:.2f}".format(fps), (10, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    lmList,hand_type = get_hand_landmarks(frame)
    if hand_type == "Right":
        if len(lmList) != 0:
            thumb = (lmList[4][1], lmList[4][2])
            index = (lmList[8][1], lmList[8][2])
            length = distance(thumb, index)
            control_volume(length)
            fingers = fingers_pos(lmList)
            # current_time = time.time()
            # if current_time-last_gesture_time > cooldown:
            if fingers == [0, 0, 0, 0, 0] and prev_gesture != "fist":
                print("Pause Triggered")
                pause_media()
                prev_gesture = "fist"
            elif fingers == [1, 1, 1, 1, 1] and prev_gesture != "open":
                print("Resume Triggered")
                resume_media()
                prev_gesture = "open"
            elif fingers == [0,1,1,0,0]:
                print("Canvas Working")
                x = lmList[8][1]
                y = lmList[8][2]
                smooth_x = int(alpha*x+(1-alpha)*smooth_x)
                smooth_y = int(alpha*y+(1-alpha)*smooth_y)
                if prev_x is None:
                    prev_x, prev_y = x, y
                cv2.line(canvas, (prev_x, prev_y), (smooth_x,smooth_y),(180,25,125), 4,cv2.LINE_AA)
                prev_x = smooth_x
                prev_y = smooth_y
            else:
                prev_x = None
                prev_y = None
    elif hand_type == "Left":
        fingers = fingers_pos(lmList)
        if fingers == [0, 1, 0, 0, 0]:
            current_index_pos = lmList[8][2]
            if prev_index_pos is not None:
                if current_index_pos > prev_index_pos + 8:
                    print("Scrolling Down")
                    scroll_down()
                elif current_index_pos < prev_index_pos - 8:
                    print("Scrolling Up")
                    scroll_up()
            prev_index_pos = current_index_pos
    gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
    frame_bg = cv2.bitwise_and(frame, frame, mask=mask)
    frame = cv2.flip(cv2.bitwise_or(frame_bg, canvas),1)
    #frame = cv2.flip(cv2.add(frame, canvas),1)
    cv2.imshow("AirDraw", frame)
    cv2.waitKey(1)
cap.release()
cv2.destroyAllWindows()