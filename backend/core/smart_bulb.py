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

# Check if credentials are configured
SMART_BULB_ENABLED = bool(ACCESS_ID and ACCESS_SECRET and DEVICE_ID)

if not SMART_BULB_ENABLED:
    print("⚠️  Smart bulb credentials not configured. Light features will be disabled.")
    print("   Set HAVELLS_ACCESS_ID, HAVELLS_ACCESS_SECRET, and HAVELLS_DEVICE_ID in .env file")
    cloud = None
else:
    # Initialize Tuya Cloud connection
    cloud = tinytuya.Cloud(
        apiRegion=REGION,
        apiKey=ACCESS_ID,
        apiSecret=ACCESS_SECRET
    )
    print("✅ Smart bulb initialized successfully")

# =========================================================
# SMART BULB FUNCTIONS
# =========================================================

def bulb_on():
    """Turn the smart bulb on."""
    if not SMART_BULB_ENABLED or not cloud:
        return
    try:
        cloud.sendcommand(DEVICE_ID, {
            "commands": [{"code": "switch_led", "value": True}]
        })
    except Exception as e:
        print(f"⚠️  Failed to turn bulb on: {e}")

def bulb_off():
    """Turn the smart bulb off."""
    if not SMART_BULB_ENABLED or not cloud:
        return
    try:
        cloud.sendcommand(DEVICE_ID, {
            "commands": [{"code": "switch_led", "value": False}]
        })
    except Exception as e:
        print(f"⚠️  Failed to turn bulb off: {e}")

def set_bulb_color(h, s=1000, v=1000):
    """
    Set the bulb color using HSV values.
    
    Args:
        h: Hue (0-360)
        s: Saturation (0-1000), default 1000
        v: Value/Brightness (0-1000), default 1000
    """
    if not SMART_BULB_ENABLED or not cloud:
        return
    try:
        cloud.sendcommand(DEVICE_ID, {
            "commands": [{
                "code": "colour_data_v2",
                "value": {"h": int(h), "s": int(s), "v": int(v)}
            }]
        })
    except Exception as e:
        print(f"⚠️  Failed to set bulb color: {e}")

def set_bulb_hsv(h, s=1000, v=1000):
    """
    Alias for set_bulb_color for backward compatibility.
    
    Args:
        h: Hue (0-360)
        s: Saturation (0-1000), default 1000
        v: Value/Brightness (0-1000), default 1000
    """
    set_bulb_color(h, s, v)
