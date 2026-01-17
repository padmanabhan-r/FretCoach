"""
FretCoach CLI - Standalone guitar practice tool.
For use on Raspberry Pi or local development with matplotlib visualization.
"""

import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
import colorsys
import threading
import time
from collections import deque

from audio_setup import get_configuration
from smart_bulb import set_bulb_hsv, bulb_on, bulb_off
from audio_metrics import (
    QualityConfig,
    QualityState,
    BulbState,
    process_audio_frame,
    score_to_hue,
    calculate_bulb_brightness,
)

# =========================================================
# AUDIO & SCALE CONFIG - Interactive Setup
# =========================================================
audio_config = get_configuration()

if audio_config is None:
    print("\n[ERR] Configuration setup failed or cancelled. Exiting.")
    exit(1)

INPUT_DEVICE = audio_config['input_device']
OUTPUT_DEVICE = audio_config['output_device']
GUITAR_CHANNEL = audio_config['guitar_channel']
CHANNELS = audio_config['channels']
SCALE_NAME = audio_config['scale_name']
TARGET_PITCH_CLASSES = set(audio_config['pitch_classes'])
AMBIENT_LIGHTING = audio_config.get('ambient_lighting', True)
STRICTNESS = audio_config.get('strictness', 0.5)
SENSITIVITY = audio_config.get('sensitivity', 0.5)

SAMPLE_RATE = 44100
BLOCK_SIZE = 128
ANALYSIS_WINDOW_SEC = 0.30
BUFFER_SIZE = int(SAMPLE_RATE * ANALYSIS_WINDOW_SEC)

print(f"\n[GUITAR] Starting Guitar Coach for {SCALE_NAME}")
print(f"   Target pitch classes: {sorted(TARGET_PITCH_CLASSES)}")
print(f"   Scale has {len(TARGET_PITCH_CLASSES)} notes - play them all for 100% conformity!")
print(f"   Ambient lighting: {'Enabled' if AMBIENT_LIGHTING else 'Disabled'}")
print(f"   Strictness: {STRICTNESS:.2f} | Sensitivity: {SENSITIVITY:.2f}")
print("=" * 60)

# =========================================================
# BUFFERS & STATE (using shared quality module)
# =========================================================
audio_buffer = deque(maxlen=BUFFER_SIZE)
buffer_lock = threading.Lock()

# Quality config and state from shared module
quality_config = QualityConfig(
    strictness=STRICTNESS,
    sensitivity=SENSITIVITY,
    sample_rate=SAMPLE_RATE,
    phrase_window=0.8,
)
quality_state = QualityState()
bulb_state = BulbState()

# =========================================================
# VISUAL SETUP
# =========================================================
plt.ion()
fig, ax = plt.subplots(figsize=(8, 2))
rect = plt.Rectangle((0, 0), 1, 1)
ax.add_patch(rect)
ax.axis("off")


def score_to_color(score):
    """Convert score to RGB color (red to green)."""
    hue = (score * 120) / 360
    return colorsys.hsv_to_rgb(hue, 1.0, 1.0)


# =========================================================
# AUDIO CALLBACK (REAL-TIME SAFE)
# =========================================================
def audio_callback(indata, outdata, frames, time_info, status):
    if status:
        print(f"Audio status: {status}")
    # Handle both mono and stereo input
    if CHANNELS == 1 or indata.ndim == 1:
        guitar = indata.flatten()
    else:
        guitar = indata[:, GUITAR_CHANNEL]
    with buffer_lock:
        audio_buffer.extend(guitar)
    outdata[:] = 0


# =========================================================
# STREAM
# =========================================================
stream = sd.Stream(
    device=(INPUT_DEVICE, OUTPUT_DEVICE),
    channels=CHANNELS,
    samplerate=SAMPLE_RATE,
    blocksize=BLOCK_SIZE,
    dtype="float32",
    callback=audio_callback,
)

stream.start()
print(f"\n[GUITAR] AI Guitar Coach running - {SCALE_NAME}")
if AMBIENT_LIGHTING:
    print("   Green = clean phrases | Red = wrong notes")
    try:
        bulb_on()
    except Exception as e:
        print(f"[WARN] Smart bulb not available: {e}")
else:
    print("   Visual feedback only (ambient lighting disabled)")
print("   Press Ctrl+C to stop\n")

# =========================================================
# MAIN LOOP
# =========================================================
try:
    while True:
        time.sleep(0.15)

        with buffer_lock:
            if len(audio_buffer) < BUFFER_SIZE:
                continue
            audio = np.array(audio_buffer)

        # Process the audio frame using shared quality module
        result = process_audio_frame(
            audio=audio,
            target_pitch_classes=TARGET_PITCH_CLASSES,
            config=quality_config,
            state=quality_state,
        )

        if result is None:
            continue

        # ---------------- VISUAL ----------------
        rect.set_color(score_to_color(quality_state.ema_quality))
        fig.canvas.draw()
        fig.canvas.flush_events()

        # ---------------- BULB ----------------
        if AMBIENT_LIGHTING:
            hue = score_to_hue(quality_state.ema_quality)
            if bulb_state.should_update(hue):
                try:
                    brightness = calculate_bulb_brightness(quality_state.ema_quality)
                    set_bulb_hsv(hue, v=brightness)
                    bulb_state.mark_sent(hue)
                except Exception as e:
                    print(f"Tuya error: {e}")

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    stream.stop()
    stream.close()
