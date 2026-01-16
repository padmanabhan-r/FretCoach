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
AMBIENT_LIGHTING = audio_config.get('ambient_lighting', True)  # Default to True for backward compatibility
STRICTNESS = audio_config.get('strictness', 0.5)  # Default to 0.5 (balanced)
SENSITIVITY = audio_config.get('sensitivity', 0.5)  # Default to 0.5 (normal)

SAMPLE_RATE = 44100
BLOCK_SIZE = 128
ANALYSIS_WINDOW_SEC = 0.30
BUFFER_SIZE = int(SAMPLE_RATE * ANALYSIS_WINDOW_SEC)

print(f"\n🎸 Starting Guitar Coach for {SCALE_NAME}")
print(f"   Target pitch classes: {sorted(TARGET_PITCH_CLASSES)}")
print(f"   Ambient lighting: {'Enabled' if AMBIENT_LIGHTING else 'Disabled'}")
print(f"   Strictness: {STRICTNESS:.2f} | Sensitivity: {SENSITIVITY:.2f}")
print("="*60)

# =========================================================
# BUFFERS & STATE
# =========================================================
audio_buffer = deque(maxlen=BUFFER_SIZE)
buffer_lock = threading.Lock()

ema_quality = 0.0
# Adjust EMA based on strictness: lower strictness = slower decay (more forgiving)
EMA_ALPHA = 0.10 + (STRICTNESS * 0.30)  # Range: 0.10 (very forgiving) to 0.40 (very strict)

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
if AMBIENT_LIGHTING:
    print("   Green = clean phrases | Red = wrong notes")
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

        energy = np.mean(audio ** 2)
        # Adjust energy threshold based on sensitivity
        energy_threshold = 1e-7 * (1 + SENSITIVITY * 10)  # Range: 1e-7 to 1.1e-6
        if energy < energy_threshold:
            continue

        p, debug_info = pitch_correctness(audio, SAMPLE_RATE, TARGET_PITCH_CLASSES, debug=True)

        # Calculate all metrics
        s = pitch_stability(audio, SAMPLE_RATE)
        t = timing_cleanliness(audio, SAMPLE_RATE)
        n = noise_control(audio)

        # Adjust weights based on strictness
        # Higher strictness = more weight on pitch correctness
        pitch_weight = 0.40 + (STRICTNESS * 0.15)  # Range: 0.40 to 0.55
        other_weight = (1.0 - pitch_weight) / 3    # Distribute remaining weight
        
        quality = (
            pitch_weight * p +
            other_weight * s +
            other_weight * t +
            other_weight * n
        )
        
        # Apply wrong note penalty based on strictness
        if p == 0.0:
            # At high strictness (>0.7), instant punishment like before
            if STRICTNESS > 0.7:
                ema_quality = 0.0
                last_phrase_time = time.time()
            else:
                # At low strictness, wrong notes still get partial credit from other metrics
                penalty_factor = (1.0 - STRICTNESS)  # Range: 1.0 (no penalty) to 0.0 (full penalty)
                quality = quality * penalty_factor
                
                # Update EMA quality
                now = time.time()
                if now - last_phrase_time > PHRASE_WINDOW:
                    ema_quality = EMA_ALPHA * quality + (1 - EMA_ALPHA) * ema_quality
                    last_phrase_time = now
        else:
            # Correct note - update EMA normally
            now = time.time()
            if now - last_phrase_time > PHRASE_WINDOW:
                ema_quality = EMA_ALPHA * quality + (1 - EMA_ALPHA) * ema_quality
                last_phrase_time = now

        # ---------------- VISUAL ----------------
        rect.set_color(score_to_color(ema_quality))
        fig.canvas.draw()
        fig.canvas.flush_events()

        # ---------------- BULB ----------------
        if AMBIENT_LIGHTING:
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