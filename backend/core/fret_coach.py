import sounddevice as sd
import numpy as np
import librosa
import matplotlib.pyplot as plt
import colorsys
import threading
import time
import os
from collections import deque
import tinytuya
from dotenv import load_dotenv, find_dotenv
from audio_setup import get_configuration

# =========================================================
# ENV / TUYA CONFIG
# =========================================================
load_dotenv(find_dotenv())

ACCESS_ID = os.getenv("HAVELLS_ACCESS_ID")
ACCESS_SECRET = os.getenv("HAVELLS_ACCESS_SECRET")
DEVICE_ID = os.getenv("HAVELLS_DEVICE_ID")
REGION = "in"

cloud = tinytuya.Cloud(
    apiRegion=REGION,
    apiKey=ACCESS_ID,
    apiSecret=ACCESS_SECRET
)

def set_bulb_hsv(h, s=1000, v=1000):
    cloud.sendcommand(DEVICE_ID, {
        "commands": [{
            "code": "colour_data_v2",
            "value": {"h": int(h), "s": int(s), "v": int(v)}
        }]
    })

# =========================================================
# AUDIO & SCALE CONFIG - Interactive Setup
# =========================================================
audio_config = get_configuration()

if audio_config is None:
    print("\n❌ Configuration setup failed or cancelled. Exiting.")
    exit(1)

INPUT_DEVICE = audio_config['input_device']
OUTPUT_DEVICE = audio_config['output_device']
GUITAR_CHANNEL = audio_config['guitar_channel']
CHANNELS = audio_config['channels']
SCALE_NAME = audio_config['scale_name']
TARGET_PITCH_CLASSES = set(audio_config['pitch_classes'])

SAMPLE_RATE = 44100
BLOCK_SIZE = 128
ANALYSIS_WINDOW_SEC = 0.30
BUFFER_SIZE = int(SAMPLE_RATE * ANALYSIS_WINDOW_SEC)

print(f"\n🎸 Starting Guitar Coach for {SCALE_NAME}")
print("="*60)

# =========================================================
# BUFFERS & STATE
# =========================================================
audio_buffer = deque(maxlen=BUFFER_SIZE)
buffer_lock = threading.Lock()

ema_quality = 0.0
EMA_ALPHA = 0.25

# Tuya throttling
last_sent_hue = None
last_send_time = 0.0
TUYA_UPDATE_INTERVAL = 0.30
HUE_EPSILON = 5

# Phrase timing
PHRASE_WINDOW = 0.8
last_phrase_time = time.time()

# =========================================================
# VISUAL SETUP
# =========================================================
plt.ion()
fig, ax = plt.subplots(figsize=(8, 2))
rect = plt.Rectangle((0, 0), 1, 1)
ax.add_patch(rect)
ax.axis("off")

def score_to_color(score):
    hue = (score * 120) / 360
    return colorsys.hsv_to_rgb(hue, 1.0, 1.0)

def score_to_hue(score):
    return int(np.clip(score, 0.0, 1.0) * 120)

# =========================================================
# FEATURE FUNCTIONS (AI)
# =========================================================
def pitch_correctness(audio):
    pitches, mags = librosa.piptrack(y=audio, sr=SAMPLE_RATE)
    idx = mags.argmax()
    pitch = pitches.flatten()[idx]

    if pitch <= 0:
        return 0.0

    midi = librosa.hz_to_midi(pitch)
    pitch_class = int(round(midi)) % 12

    if pitch_class not in TARGET_PITCH_CLASSES:
        return 0.0  # HARD FAIL

    intonation_error = abs(midi - round(midi))
    return np.clip(1 - intonation_error, 0, 1)

def pitch_stability(audio):
    pitches, mags = librosa.piptrack(y=audio, sr=SAMPLE_RATE)
    stable = pitches[mags > np.max(mags) * 0.7]
    if len(stable) < 5:
        return 0.5
    return np.exp(-np.std(stable))

def timing_cleanliness(audio):
    onsets = librosa.onset.onset_detect(y=audio, sr=SAMPLE_RATE)
    if len(onsets) < 2:
        return 0.6
    intervals = np.diff(onsets)
    return np.exp(-np.var(intervals))

def noise_control(audio):
    total = np.mean(audio ** 2)
    noise = np.mean((audio - np.mean(audio)) ** 2)
    return np.clip(1 - noise / (total + 1e-9), 0, 1)

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
print(f"\n🎸 AI Guitar Coach running — {SCALE_NAME}")
print("   Green = clean phrases | Red = wrong notes")
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

        energy = np.mean(audio ** 2)
        if energy < 1e-7:
            continue

        p = pitch_correctness(audio)

        # 🚨 INSTANT RED ON WRONG NOTE
        if p == 0.0:
            ema_quality = 0.0
        else:
            s = pitch_stability(audio)
            t = timing_cleanliness(audio)
            n = noise_control(audio)

            quality = (
                0.45 * p +
                0.20 * s +
                0.20 * t +
                0.15 * n
            )

            now = time.time()
            if now - last_phrase_time > PHRASE_WINDOW:
                ema_quality = EMA_ALPHA * quality + (1 - EMA_ALPHA) * ema_quality
                last_phrase_time = now

        # ---------------- VISUAL ----------------
        rect.set_color(score_to_color(ema_quality))
        fig.canvas.draw()
        fig.canvas.flush_events()

        # ---------------- BULB ----------------
        now = time.time()
        hue = score_to_hue(ema_quality)
        brightness = int(300 + 700 * ema_quality)

        if (
            (last_sent_hue is None or abs(hue - last_sent_hue) >= HUE_EPSILON)
            and (now - last_send_time) >= TUYA_UPDATE_INTERVAL
        ):
            try:
                set_bulb_hsv(hue, v=brightness)
                last_sent_hue = hue
                last_send_time = now
            except Exception as e:
                print("Tuya error:", e)

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    stream.stop()
    stream.close()