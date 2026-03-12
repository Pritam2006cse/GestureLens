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

Scroll web pages or documents using the index finger movement.

 Gesture           Action           
 ----------------  ---------------- 
 Index finger up   Enable scrolling 
 Move finger up    Scroll up        
 Move finger down  Scroll down      

### 4. Air Drawing

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
