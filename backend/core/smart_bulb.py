"""
Smart Bulb Controller for FretCoach
Handles Tuya smart bulb operations including on/off and color control.
"""
import tinytuya
import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

# =========================================================
# TUYA CLOUD CONFIGURATION
# =========================================================
ACCESS_ID = os.getenv("HAVELLS_ACCESS_ID")
ACCESS_SECRET = os.getenv("HAVELLS_ACCESS_SECRET")
DEVICE_ID = os.getenv("HAVELLS_DEVICE_ID")
REGION = os.getenv("HAVELLS_REGION", "in")

# Initialize Tuya Cloud connection
cloud = tinytuya.Cloud(
    apiRegion=REGION,
    apiKey=ACCESS_ID,
    apiSecret=ACCESS_SECRET
)

# =========================================================
# SMART BULB FUNCTIONS
# =========================================================

def bulb_on():
    """Turn the smart bulb on."""
    cloud.sendcommand(DEVICE_ID, {
        "commands": [{"code": "switch_led", "value": True}]
    })

def bulb_off():
    """Turn the smart bulb off."""
    cloud.sendcommand(DEVICE_ID, {
        "commands": [{"code": "switch_led", "value": False}]
    })

def set_bulb_color(h, s=1000, v=1000):
    """
    Set the bulb color using HSV values.
    
    Args:
        h: Hue (0-360)
        s: Saturation (0-1000), default 1000
        v: Value/Brightness (0-1000), default 1000
    """
    cloud.sendcommand(DEVICE_ID, {
        "commands": [{
            "code": "colour_data_v2",
            "value": {"h": int(h), "s": int(s), "v": int(v)}
        }]
    })

def set_bulb_hsv(h, s=1000, v=1000):
    """
    Alias for set_bulb_color for backward compatibility.
    
    Args:
        h: Hue (0-360)
        s: Saturation (0-1000), default 1000
        v: Value/Brightness (0-1000), default 1000
    """
    set_bulb_color(h, s, v)
