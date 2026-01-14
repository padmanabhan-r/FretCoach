import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
import colorsys
import threading
import time
from collections import deque
from audio_setup import get_configuration
from smart_bulb import set_bulb_hsv, bulb_on, bulb_off
from audio_features import pitch_correctness, pitch_stability, timing_cleanliness, noise_control

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

        p = pitch_correctness(audio, SAMPLE_RATE, TARGET_PITCH_CLASSES)

        # 🚨 INSTANT RED ON WRONG NOTE
        if p == 0.0:
            ema_quality = 0.0
        else:
            s = pitch_stability(audio, SAMPLE_RATE)
            t = timing_cleanliness(audio, SAMPLE_RATE)
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