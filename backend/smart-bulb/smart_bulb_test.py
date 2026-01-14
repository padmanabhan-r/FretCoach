import tinytuya
import time
import os

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# =========================================================

ACCESS_ID = os.getenv("HAVELLS_ACCESS_ID")
ACCESS_SECRET = os.getenv("HAVELLS_ACCESS_SECRET")
DEVICE_ID = os.getenv("HAVELLS_DEVICE_ID")
REGION = os.getenv("HAVELLS_REGION")   

cloud = tinytuya.Cloud(
    apiRegion=REGION,
    apiKey=ACCESS_ID,
    apiSecret=ACCESS_SECRET
)

def bulb_on():
    cloud.sendcommand(DEVICE_ID, {
        "commands": [{"code": "switch_led", "value": True}]
    })

def bulb_off():
    cloud.sendcommand(DEVICE_ID, {
        "commands": [{"code": "switch_led", "value": False}]
    })

def set_color(h, s=1000, v=1000):
    cloud.sendcommand(DEVICE_ID, {
        "commands": [{
            "code": "colour_data_v2",
            "value": {"h": h, "s": s, "v": v}
        }]
    })

# ---- TEST SEQUENCE ----
bulb_on()
time.sleep(1)

# Red
set_color(0)
time.sleep(1)

# Yellow
set_color(60)
time.sleep(1)

# Green
set_color(120)
time.sleep(1)

# Blue
set_color(240)
time.sleep(1)

# Purple
set_color(300)
time.sleep(1)
