# GestureLens – Gesture Controlled System

GestureLens is a computer vision based gesture-controlled interface built using Python.
It allows users to control system functions like **volume, media playback, scrolling, and drawing** using hand gestures captured through a webcam.

The project uses MediaPipe for hand tracking and OpenCV for real-time video processing.

## Features Implemented

### 1. Volume Control (Right Hand)

Adjust system volume using the distance between the thumb and index finger.

Gesture:

1. Pinch fingers closer → decrease volume
2.  Spread fingers apart → increase volume

### 2. Media Control (Right Hand)

Control media playback with simple gestures.

 Gesture      Action       
 -----------  ------------ 
 Closed Fist  Pause Media  
 Open Palm    Resume Media 

Works with browsers and media players.

### 3. Scrolling (Left Hand)

Scrolling is controlled using the **left hand**.

## Activating Scroll Mode

Scrolling is activated **as soon as you show your hand to the camera** in the  **180°–260°** region .

⚠️ **Important:**
The movement should come from **rotating the forearm**, not just twisting the wrist or palm.
Rotating only the wrist will not produce stable scrolling.

Scrolling will only activate when the **thumb and index finger are not pinched together**.

---

# Scrolling Up

To scroll **upwards**, rotate your forearm **from top to bottom** in a **loose half-cycle motion**.

To reach this position:

1.Extend your left forearm slightly in front of you, while keeping your elbow bent at approximately a 90° angleand make sure you keep showing your palm clearly and steadily to the camera while rotating. The rotation of the forearm should naturally form a gentle arc, rather than a rigid straight movement or a rigid half cycle movement. 

3. Now **rotate your entire forearm toward the right side** (**clockwise** from your perspective).

4. Continue rotating the forearm.

The movement should resemble a **gentle upward arc** of the forearm.

Although moving the hand **straight downward** may still work, it is **not recommended** because scrolling becomes less smooth.

---

# Scrolling Down

To scroll **downwards**, rotate your forearm **from bottom to top** in a **loose half-cycle motion**.

To reach this position:

1. Keep your left forearm slightly toward your chest, with the elbow bent outward so that the angle between the elbow and forearm is relatively small, and make sure you keep showing your palm clearly and steadily to the camera while rotating. The rotation of the forearm should naturally form a gentle arc, rather than a rigid straight movement or a rigid half cycle movement.
   
2. Now **rotate your entire forearm toward the left side** (**anticlockwise** from your perspective).

3. Continue rotating the forearm.

The motion should resemble a **gentle upward arc**.

Straight upward movement may still work but is **not recommended for stable scrolling**.

---

# Precautions for Better Scrolling

### Keep the wrist stable

While performing the motion, try to keep the **wrist stable**.
Unstable wrist movement may introduce small fluctuations in the detected hand position and cause **unwanted scrolling**.

---

### Starting upward scrolling

1. Place your hand near the **bottom of the camera frame**.

2. Wait briefly for the system to stabilize the position.

3. Then rotate your forearm **from bottom to top** to start scrolling.

---

### Starting downward scrolling

1. Place your hand near the **top of the camera frame**.

2. Wait briefly for stabilization.

3. Then rotate your forearm **from top to bottom**.

### Avoid very fast movements

Moving the hand too quickly may prevent the program from accurately detecting the motion.


### 4.Brightness Control Gesture
Brightness is controlled using the left hand.

Activating Brightness Control:- 
Join (pinch) the tip of the index finger with the tip of the thumb.
Keep this pinch position clearly visible to the camera while performing the movement.
Increasing Brightness
While maintaining the pinch gesture, move your hand from left to right across the camera frame.
Decreasing Brightness
While maintaining the pinch gesture, move your hand from right to left across the camera frame.

Tips for Better Control:-
Keep the pinch stable and clearly visible to the camera.
Move your hand smoothly rather than very quickly.
Avoid moving your hand too close to the extreme edges of the camera frame, as brightness tracking may reset
     

### 5. Air Drawing

You can draw shapes in the air using your index finger.

Gesture:

 Gesture                Action         
 ---------------------  -------------- 
 Index + Middle finger  Start drawing  
 Move finger            Draw on screen 

The drawing canvas is overlaid on the webcam feed.

## Technologies Used

1. Python
2. OpenCV
3. MediaPipe
4. NumPy
5. PyAutoGUI
6. Pycaw (for system volume control)

## Project Structure

GestureControlSystem
│
├── main.py
├── Hand_Tracker.py
├── Gesture_Utils.py
├── Volume_Control.py
├── Media_Control.py
├── Scroll_Control.py
├── requirements.txt
└── README.md

### 3. Run the project
python main.py

## Controls Summary

 Hand   Gesture                 Function       
 -----  ----------------------  -------------- 
 Right  Thumb + Index distance  Volume control 
 Right  Fist                    Pause media    
 Right  Open palm               Resume media   
 Left   Index finger movement   Scroll         
 Right  Index + Middle finger   Air drawing    

## Author

Pritam Sarkar
Computer Science Engineering Student (2nd year)

GitHub:
https://github.com/Pritam2006cse
