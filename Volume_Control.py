import cv2
import numpy as np
import math
import time
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

device = AudioUtilities.GetSpeakers()
volume = device.EndpointVolume
volRange = volume.GetVolumeRange()
# volume.SetMasterVolumeLevel(0,None)
minVol = volRange[0]
maxVol = volRange[1]

def control_volume(vol_percent):
    vol = np.interp(vol_percent, [0,100], [minVol, maxVol])
    volume.SetMasterVolumeLevel(vol, None)
    print("Volume:", int(vol_percent), "%")
    
    # vol = np.interp(length,[50,200],[minVol,maxVol])
    # volume.SetMasterVolumeLevel(vol, None)
    # volPer = np.interp(length, [50, 200], [0, 100])
    # print("Volume:", int(volPer), "%")