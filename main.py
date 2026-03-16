import cv2
import numpy as np
import time
import pyautogui

from Hand_Tracker import get_hand_landmarks
from Volume_Control import control_volume
from Gesture_Utils import distance,fingers_pos
from Media_Control import pause_media,resume_media
from Scroll_Control import scroll_up,scroll_down
import screen_brightness_control as sbc 
 

wCam,hCam = 640,480
cap = cv2.VideoCapture(0)
cap.set(3,wCam)
cap.set(4,hCam)
pTime = 0
#last_gesture_time = 0
#cooldown = 2
prev_gesture = None
prev_index_pos = None
prev_brightness_x = None
canvas = np.zeros((hCam,wCam,3), dtype=np.uint8)
prev_x = None
prev_y = None
smooth_x = 0
smooth_y = 0
alpha = 0.2
smooth_scroll_y = 0
scroll_alpha = 0.3
# scroll_active = True
smooth_brightness_x = 0
brightness_alpha = 0.35
last_brightness = -1
last_screenshot_time = 0
screenshot_cooldown = 2


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
        if len(lmList) != 0:
            
            # hand_was_visible = True
           
            fingers = fingers_pos(lmList)
            
            # -------- SCREENSHOT GESTURE (INDEX + MIDDLE FINGER) --------

            if fingers == [0,1,1,0,0] and time.time() - last_screenshot_time > screenshot_cooldown:
    
                print("Screenshot Captured")

                # Trigger normal Windows screenshot
                pyautogui.hotkey('win', 'prtsc')

                last_screenshot_time = time.time()
    
        
            wrist_x = lmList[0][1]
            wrist_y = lmList[0][2]
            middle_base_x = lmList[9][1]
            middle_base_y = lmList[9][2]

            import math
            dx = middle_base_x - wrist_x
            dy = middle_base_y - wrist_y
            palm_angle = math.degrees(math.atan2(dy, dx))
            palm_angle = (palm_angle + 360) % 360   # normalize


            
        # -------- PINCH DISTANCE (thumb + index) --------
            thumb = (lmList[4][1], lmList[4][2])
            index = (lmList[8][1], lmList[8][2])

            pinch_dist = distance(thumb, index)

            print(f"DEBUG - Palm: {int(palm_angle)}°, PinchDist: {int(pinch_dist)}, Fingers: {fingers}")


            current_y = lmList[9][2]

            if current_y < 60:   # near top of camera
                # print("DEBUG: Palm detected at TOP of frame -> resetting prev_index_pos")
                prev_index_pos = None
            
            elif current_y > 420:
                # print("DEBUG: Palm entered from BOTTOM -> resetting prev_index_pos")
                prev_index_pos = None
            
        # -------- SCROLLING -------------
            
                    
            if 180 <= palm_angle <= 260 and pinch_dist > 30:
                
            
                # print(">>> SCROLLING <<<")
                smooth_scroll_y = int(scroll_alpha * current_y + (1 - scroll_alpha) * smooth_scroll_y)
                current_hand_pos = smooth_scroll_y

                if prev_index_pos is not None:
                    
                     
                    movement =  prev_index_pos - current_hand_pos
                    
                    
                    #print(f"DEBUG movement = {movement}")
                    

                    if abs(movement) > 4:   # ignore tiny noise
                        scroll_strength = int(movement * abs(movement) * 0.8)

                        scroll_strength = max(-800, min(800, scroll_strength))

                        if scroll_strength > 0:
                            scroll_down(scroll_strength)

                        else:
                            scroll_up(abs(scroll_strength))

                prev_index_pos = current_hand_pos     

        # -------- BRIGHTNESS CONTROL (PINCH + MOVE LEFT/RIGHT) --------
            if pinch_dist < 30:
                prev_index_pos = None
                #print(">>> BRIGHTNESS MODE <<<")

    # midpoint of pinch
                cx = (lmList[4][1] + lmList[8][1]) // 2
                cx = wCam - cx
                
                margin = 80
                if cx < margin or cx > wCam - margin:
                    prev_brightness_x = None
                    continue
                
    # smooth movement
                smooth_brightness_x = int(
                    brightness_alpha * cx + (1 - brightness_alpha) * smooth_brightness_x
    )
                
                # ---- VELOCITY CLAMPING ----
                if prev_brightness_x is not None:

                    movement = smooth_brightness_x - prev_brightness_x

        # clamp movement speed (limits sudden jumps)
                    movement = max(-40, min(40, movement))

        # update brightness using movement
                    brightness = last_brightness + movement * 0.3

                else:
                    brightness = last_brightness

                brightness = max(0, min(100, brightness))

    # update brightness only if change is noticeable
                if abs(brightness - last_brightness) >= 1:
                    sbc.set_brightness(brightness)
                    last_brightness = brightness

                prev_brightness_x = smooth_brightness_x

            else:
                prev_brightness_x = None
       
    gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
    frame_bg = cv2.bitwise_and(frame, frame, mask=mask)
    frame = cv2.flip(cv2.bitwise_or(frame_bg, canvas),1)
    #frame = cv2.flip(cv2.add(frame, canvas),1)
    cv2.imshow("AirDraw", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()