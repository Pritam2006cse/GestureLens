import numpy as np
import screen_brightness_control as sbc

def control_brightness(length):
    # Map finger distance to brightness (0-100%)
    brightness = np.interp(length, [50, 200], [0, 100])
    
    # Set system brightness
    sbc.set_brightness(int(brightness))
    
    # Print for debugging
    print("Brightness:", int(brightness), "%")