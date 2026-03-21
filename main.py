import cv2
import numpy as np
import time
import pyautogui
import math
import threading

from Hand_Tracker import get_hand_landmarks
from Volume_Control import control_volume
from Gesture_Utils import distance,fingers_pos
from Media_Control import pause_media,resume_media
from Scroll_Control import scroll_up,scroll_down
import screen_brightness_control as sbc 
 

wCam,hCam = 640,480
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
pTime = 0
prev_gesture = None
prev_scroll_pos=None
prev_brightness_x = None
canvas = np.zeros((hCam,wCam,3), dtype=np.uint8)
prev_x = None
prev_y = None
smooth_x = 0
smooth_y = 0
alpha = 0.2
smooth_scroll_y = 0
scroll_alpha = 0.3
smooth_brightness_x = 0
brightness_alpha = 0.5
last_brightness = sbc.get_brightness()[0] 
last_screenshot_time = 0
screenshot_cooldown = 2
prev_volume_x = None
smooth_volume_x = 0
volume_alpha = 0.35
last_volume = 50 
volume_frames = 0
scroll_frames = 0
brightness_frames = 0
screenshot_active = False
# ================== MOUSE VARIABLES ==================
mouse_mode = False
mouse_toggle_frames = 0
mouse_toggle_threshold = 5

prev_mouse_x = 0
prev_mouse_y = 0
smooth_mouse_x = 0
smooth_mouse_y = 0
mouse_alpha = 0.06

stable_frames = 0

screen_w, screen_h = pyautogui.size()

click_frames = 0
right_click_frames = 0


click_cooldown = 0.3
last_click_time = 0
mouse_toggle_cooldown = 1.0
last_toggle_time = 0

#================= lag reduction variables =================
pyautogui.PAUSE = 0
last_move_time = 0
latest_frame = None
frame_lock = threading.Lock()
frame_count = 0
lmList = []
hand_type = None


def camera_thread():
    global latest_frame
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        
        with frame_lock:
            latest_frame = frame.copy()
            
threading.Thread(target=camera_thread, daemon=True).start()

while True:
    # cap.grab()
    with frame_lock:
        if latest_frame is None:
            continue
        frame = latest_frame.copy()
    
    
    # frame = cv2.flip(frame, 1)
    frame_count += 1
    cTime = time.time()
    fps = 1/(cTime-pTime + 1e-6)
    pTime = cTime
    cv2.putText(frame, "FPS: {0:.2f}".format(fps), (10, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    
    #  # -------- FRAME SKIP (after FPS) --------
   
    if frame_count % 2 == 0:
        new_lmList, new_hand_type = get_hand_landmarks(frame)
        lmList = new_lmList
        hand_type = new_hand_type
    
                
    if hand_type == "Right" and len(lmList) != 0:
    
                
            fingers = fingers_pos(lmList)
            
             # -------- MOUSE MODE TOGGLE --------
            if fingers == [0,1,1,1,0]:
                mouse_toggle_frames += 1
            else:
                mouse_toggle_frames = 0

            if mouse_toggle_frames > mouse_toggle_threshold:
                if time.time() - last_toggle_time > mouse_toggle_cooldown:

                    mouse_mode = not mouse_mode
                    print("Mouse Mode:", mouse_mode)

                    last_toggle_time = time.time()
                    mouse_toggle_frames = 0

                # RESET
                stable_frames = 0
                click_frames = 0
                right_click_frames = 0
                prev_mouse_x = prev_mouse_y = 0
                smooth_mouse_x = smooth_mouse_y = 0

                prev_volume_x = None
                prev_brightness_x = None
                prev_scroll_pos = None

        # -------- MOUSE CONTROL --------
            if mouse_mode:

                index_x = int(lmList[8][1])
                index_y = int(lmList[8][2])

            # stabilization
                if prev_mouse_x == 0 and prev_mouse_y == 0:
                    prev_mouse_x, prev_mouse_y = index_x, index_y

                movement = abs(index_x - prev_mouse_x) + abs( index_y - prev_mouse_y)

                if movement < 8:
                    stable_frames += 1
                else:
                    stable_frames = 0

                prev_mouse_x, prev_mouse_y = index_x, index_y

                if stable_frames > 3:
                    
                    screen_x = np.interp(index_x, (0, wCam), (screen_w,0))
                    screen_y = np.interp(index_y, (0, hCam), (0,screen_h))
                    speed = 1.5   # try 1.5 → 2.5
                    screen_x *= speed
                    screen_y *= speed
                    smooth_mouse_x = mouse_alpha * screen_x + (1 - mouse_alpha) * smooth_mouse_x
                    smooth_mouse_y = mouse_alpha * screen_y + (1 - mouse_alpha) * smooth_mouse_y
        
                    # # -------- ANTI-TELEPORT  --------

                    if time.time() - last_move_time > 0.02:
                        pyautogui.moveTo(int(smooth_mouse_x), int(smooth_mouse_y), _pause=False)
                        last_move_time = time.time()
                        
            # left click
                thumb = (lmList[4][1], lmList[4][2])
                middle = (lmList[12][1], lmList[12][2])
           

                if distance(thumb, middle) < 25:
                    click_frames += 1
                else:
                    click_frames = 0

                if click_frames > 4:
                    if time.time() - last_click_time > click_cooldown:
                        pyautogui.click()
                        print("Left Click")
                        last_click_time = time.time()
                    click_frames = 0

            # right click
                ring = (lmList[16][1], lmList[16][2])
               

                if distance(thumb, ring) < 25:
                    right_click_frames += 1
                else:
                    right_click_frames = 0

                if right_click_frames > 4:
                    if time.time() - last_click_time > click_cooldown:
                        pyautogui.rightClick()
                        print("Right Click")
                        last_click_time = time.time()
                    right_click_frames = 0

                continue 
            
            # -------- SCREENSHOT (THUMB + MIDDLE PINCH) --------

            thumb = (lmList[4][1], lmList[4][2])
            middle = (lmList[12][1], lmList[12][2])

            screenshot_dist = distance(thumb, middle)

           
            
            if screenshot_dist < 25:
                
                if not screenshot_active and time.time() - last_screenshot_time > screenshot_cooldown:
                    print("Screenshot Captured")

                    pyautogui.hotkey('win', 'prtsc')

                    last_screenshot_time = time.time()
                    screenshot_active = True
                
            # reset other gesture states (IMPORTANT)
                prev_scroll_pos = None
                prev_volume_x = None
                prev_brightness_x = None
            else:
                screenshot_active = False
    
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
                    smooth_x,smooth_y = x,y
                cv2.line(canvas, (prev_x, prev_y), (smooth_x,smooth_y),(180,25,125), 4,cv2.LINE_AA)
                prev_x = smooth_x
                prev_y = smooth_y
            else:
                prev_x = None
                prev_y = None
            
            # -------- VOLUME CONTROL (PINCH + MOVE LEFT/RIGHT) --------
            
            thumb = (lmList[4][1], lmList[4][2])
            index = (lmList[8][1], lmList[8][2])
            volume_pinch_dist = distance(thumb, index)
            
            
            if volume_pinch_dist < 30:
                volume_frames += 1
            else:
                volume_frames = 0

            if volume_frames > 3:

                cx = (lmList[4][1] + lmList[8][1]) // 2
                cx = wCam - cx

                margin = 80
                if cx < margin or cx > wCam - margin:
                    prev_volume_x = None
                   
                else:
                # smooth movement
                    smooth_volume_x = int(
                        volume_alpha * cx + (1 - volume_alpha) * smooth_volume_x
                )

                    if prev_volume_x is not None:
                    #  prev_volume_x = smooth_volume_x


                        movement =   smooth_volume_x - prev_volume_x 

                    # clamp speed
                        movement = max(-40, min(40, movement))

                        volume = last_volume + movement * 0.3
                    
                    else: 
                        volume = last_volume
            
                    volume = max(0, min(100, volume))

                    if abs(volume - last_volume) >= 1:
                        control_volume(volume)
                        last_volume = volume

                    prev_volume_x = smooth_volume_x

            else:
                prev_volume_x = None
            
    elif hand_type == "Left" and len(lmList) != 0:
   
        fingers = fingers_pos(lmList)
    
        wrist_x = lmList[0][1]
        wrist_y = lmList[0][2]
        middle_base_x = lmList[9][1]
        middle_base_y = lmList[9][2]

        dx = middle_base_x - wrist_x
        dy = middle_base_y - wrist_y
        palm_angle = math.degrees(math.atan2(dy, dx))
        palm_angle = (palm_angle + 360) % 360   # normalize


            
        # -------- PINCH DISTANCE (thumb + index) --------
        thumb = (lmList[4][1], lmList[4][2])
        index = (lmList[8][1], lmList[8][2])

        pinch_dist = distance(thumb, index)
        
        

        # print(f"DEBUG - Palm: {int(palm_angle)}°, PinchDist: {int(pinch_dist)}, Fingers: {fingers}")


        current_y = lmList[9][2]

        if current_y < 60:   # near top of camera
                # print("DEBUG: Palm detected at TOP of frame -> resetting prev_index_pos")
            prev_scroll_pos = None
            
        elif current_y > 420:
                # print("DEBUG: Palm entered from BOTTOM -> resetting prev_index_pos")
            prev_scroll_pos = None
            
        # -------- SCROLLING -------------
            
                    
        if 180 <= palm_angle <= 260 and pinch_dist > 30:
            scroll_frames += 1
        else:
            scroll_frames = 0

        if scroll_frames > 3:

           # print(">>> SCROLLING <<<")
            smooth_scroll_y = int(scroll_alpha * current_y + (1 - scroll_alpha) * smooth_scroll_y)
            current_hand_pos = smooth_scroll_y
                
            if prev_scroll_pos is not None:
                    
                     
                movement =  prev_scroll_pos - current_hand_pos
                    
                    
                    #print(f"DEBUG movement = {movement}")
                    

                if abs(movement) > 4:   # ignore tiny noise
                    scroll_strength = int(movement * abs(movement) * 0.8)

                    scroll_strength = max(-800, min(800, scroll_strength))

                    if scroll_strength > 0:
                        scroll_down(scroll_strength)

                    else:
                        scroll_up(abs(scroll_strength))

            prev_scroll_pos = current_hand_pos
            
        else:
            prev_scroll_pos = None
                 

        # -------- BRIGHTNESS CONTROL (PINCH + MOVE LEFT/RIGHT) --------
        if pinch_dist < 30:
            brightness_frames += 1
        else:
            brightness_frames = 0

        if brightness_frames > 3:
            prev_scroll_pos = None
                #print(">>> BRIGHTNESS MODE <<<")

    # midpoint of pinch
            cx = (lmList[4][1] + lmList[8][1]) // 2
            cx = wCam - cx
                
            margin = 80
            if cx < margin or cx > wCam - margin:
                prev_brightness_x = None
              
                
    # smooth movement
            else:
                smooth_brightness_x = int(
                    brightness_alpha * cx + (1 - brightness_alpha) * smooth_brightness_x
                )
                
                # ---- VELOCITY CLAMPING ----
                if prev_brightness_x is not None:

                    movement = smooth_brightness_x - prev_brightness_x

        # clamp movement speed (limits sudden jumps)
                    movement = max(-40, min(40, movement))

        # update brightness using movement
                    brightness = last_brightness + movement * 0.7

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