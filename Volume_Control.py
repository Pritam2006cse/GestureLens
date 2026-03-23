import cv2
import numpy as np
import math
import time
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

device = AudioUtilities.GetSpeakers()
volume = device.EndpointVolume


def control_volume(vol_percent):
    vol_scalar = max(0.0, min(1.0, vol_percent / 100))
    volume.SetMasterVolumeLevelScalar(vol_scalar, None)
    print("Volume:", int(vol_percent), "%")
    
