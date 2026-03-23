import cv2
import mediapipe as mp
import numpy as np
import math
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


MARGIN = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54)
base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = vision.HandLandmarkerOptions(base_options=base_options,num_hands=2)
detector = vision.HandLandmarker.create_from_options(options)
mp_hands = mp.tasks.vision.HandLandmarksConnections
mp_drawing = mp.tasks.vision.drawing_utils
mp_drawing_styles = mp.tasks.vision.drawing_styles

def draw_landmarks_on_image(rgb_image, detection_result):
  hand_landmarks_list = detection_result.hand_landmarks
  handedness_list = detection_result.handedness
  annotated_image = np.copy(rgb_image)

  # Loop through the detected hands to visualize.
  for idx in range(len(hand_landmarks_list)):
    hand_landmarks = hand_landmarks_list[idx]
    handedness = handedness_list[idx]

    # Draw the hand landmarks.
    mp_drawing.draw_landmarks(
      annotated_image,
      hand_landmarks,
      mp_hands.HAND_CONNECTIONS,
      mp_drawing_styles.get_default_hand_landmarks_style(),
      mp_drawing_styles.get_default_hand_connections_style())
    height, width, _ = annotated_image.shape
    thumb = hand_landmarks[4]
    index = hand_landmarks[8]
    thumb_point = (int(thumb.x * width), int(thumb.y * height))
    index_point = (int(index.x * width), int(index.y * height))
    cv2.line(annotated_image, thumb_point, index_point, (255, 0, 255), 3)
    cv2.circle(annotated_image, thumb_point, 10, (255, 0, 255), cv2.FILLED)
    cv2.circle(annotated_image, index_point, 10, (255, 0, 255), cv2.FILLED)

    # Get the top left corner of the detected hand's bounding box.
    x_coordinates = [landmark.x for landmark in hand_landmarks]
    y_coordinates = [landmark.y for landmark in hand_landmarks]
    text_x = int(min(x_coordinates) * width)
    text_y = int(min(y_coordinates) * height) - MARGIN

    # Draw handedness (left or right hand) on the image.
    cv2.putText(annotated_image, f"{handedness[0].category_name}",
                (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX,
                FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)

  return annotated_image

def get_hand_landmarks(annotated_image, display_volume, display_brightness, last_volume_update, last_brightness_update, bar_show_time):
    imgRGB = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=imgRGB)
    detection_result = detector.detect(mp_image)
    annotated_image = draw_landmarks_on_image(mp_image.numpy_view(), detection_result)
    current_time = time.time()
    h, w, _ = annotated_image.shape 
# ===== BRIGHTNESS BAR =====
    if current_time - last_brightness_update < bar_show_time:
      bar_x1, bar_y1 = 50, h-80
      bar_x2, bar_y2 = 300, h-60

      cv2.rectangle(annotated_image, (bar_x1, bar_y1), (bar_x2, bar_y2), (50, 50, 50), -1)

      fill_width = int((display_brightness / 100) * (bar_x2 - bar_x1))
      cv2.rectangle(annotated_image, (bar_x1, bar_y1), (bar_x1 + fill_width, bar_y2), (0, 255, 255), -1)

      cv2.putText(annotated_image, f"Brightness: {int(display_brightness)}%", 
                (bar_x1, bar_y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 
                0.7, (0, 165, 255), 2)


# ===== VOLUME BAR =====
    if current_time - last_volume_update < bar_show_time:
      bar_x1, bar_y1 = 50, h-40
      bar_x2, bar_y2 = 300, h-20

      cv2.rectangle(annotated_image, (bar_x1, bar_y1), (bar_x2, bar_y2), (50, 50, 50), -1)
      fill_width = int((display_volume / 100) * (bar_x2 - bar_x1))
      cv2.rectangle(annotated_image, (bar_x1, bar_y1), (bar_x1 + fill_width, bar_y2), (255, 255, 0), -1)

      cv2.putText(annotated_image, f"Volume: {int(display_volume)}%", 
                (bar_x1, bar_y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 
                0.7, (255, 255, 0), 2)
    cv2.imshow("Annotated",cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))
    lmList = []
    hand_type = None
    if detection_result.hand_landmarks:
        hand_type = detection_result.handedness[0][0].category_name
        h, w, _ = annotated_image.shape
        for hand_landmarks in detection_result.hand_landmarks:
            for id, lm in enumerate(hand_landmarks):
                cx = int(lm.x * w)
                cy = int(lm.y * h)
                lmList.append([id, cx, cy])
                cv2.circle(annotated_image, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
    return lmList,hand_type