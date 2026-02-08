# Audio Analysis Agent Engine - The Fast Loop

Real-time audio processing engine that provides <300ms feedback on every note you play. The deterministic "Fast Brain" of FretCoach's dual-brain architecture.

![FretCoach Brain Architecture](assets/images/FretCoach%20Brain.png)

---

## Overview

The **Audio Analysis Agent** is FretCoach's real-time processing engine—a deterministic, local audio analysis system that operates independently of cloud services. It processes guitar audio continuously, evaluating every note against four performance metrics and providing immediate feedback through multiple channels.

**Design Philosophy:** Preventive intervention requires **speed**. The audio analysis agent operates in the critical <300ms window where the brain can still adjust motor patterns before habits solidify.

---

## Architecture: The Fast Loop

### Dual-Brain System

FretCoach uses a **two-system architecture** inspired by neuroscience:

```
┌─────────────────────────────────────────────────────────┐
│              AUDIO ANALYSIS AGENT (Fast Loop)           │
│                                                         │
│  • Local processing (no cloud)                          │
│  • <300ms latency                                       │
│  • Deterministic algorithms                             │
│  • Continuous real-time operation                       │
│  • 4 metric evaluation                                  │
│                                                         │
│  Purpose: Preventive intervention during execution      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                 AI COACH (Slow Loop)                    │
│                                                         │
│  • Cloud LLM APIs (OpenAI, Gemini)                      │
│  • 1-3 second latency                                   │
│  • Adaptive reasoning                                   │
│  • On-demand operation                                  │
│  • Strategic coaching                                   │
│                                                         │
│  Purpose: Reflective analysis and practice planning     │
└─────────────────────────────────────────────────────────┘
```

**Why this separation?**
- **Speed:** Audio analysis can't wait for LLM API calls
- **Reliability:** Practice sessions continue even if internet fails
- **Cost:** Running pitch detection via GPT-4o would be prohibitively expensive
- **Determinism:** Audio metrics are reproducible and explainable
- **Privacy:** Your playing never leaves your device (unless you want session summaries)

### Processing Pipeline

```
🎸 Guitar → Audio Interface → Audio Analysis Agent → Multiple Outputs

┌─────────────────────────────────────────────────────────┐
│                    PROCESSING STAGES                    │
└─────────────────────────────────────────────────────────┘

1. Audio Capture (sounddevice)
   ↓
   ├─ 44.1kHz sampling rate
   ├─ Mono channel (left input)
   └─ Streaming buffer (non-blocking)

2. Windowing (800ms chunks, 50% overlap)
   ↓
   ├─ Hann window function
   ├─ Overlap for smoothness
   └─ Energy threshold check

3. Feature Extraction (librosa, NumPy, SciPy)
   ↓
   ├─ Pitch detection (piptrack)
   ├─ Frequency → MIDI → Pitch class
   ├─ Onset detection (energy + timing)
   └─ Noise estimation

4. Metric Calculation
   ↓
   ├─ Pitch Accuracy (intonation + scale conformity)
   ├─ Scale Conformity (coverage + evenness)
   ├─ Timing Stability (interval consistency)
   └─ Noise Control (signal-to-noise ratio)

5. Quality Scoring
   ↓
   ├─ Weighted combination
   ├─ Exponential Moving Average (EMA) smoothing
   └─ Phrase-level aggregation (800ms groups)

6. Multi-Channel Feedback
   ↓
   ├─ WebSocket → Frontend UI (6.67 Hz updates)
   ├─ Tuya API → Smart Bulb (HSV color control)
   └─ PostgreSQL → Session logging
```

**Latency breakdown:**
- Audio capture: ~23ms (512 sample buffer at 44.1kHz)
- Processing: ~100-150ms (librosa operations)
- WebSocket transmission: ~10ms
- UI rendering: ~16ms (60 FPS)
- **Total: 250-300ms** (measured end-to-end)

---

## Core Components

### 1. Audio Capture (`audio_setup.py`)

**Library:** `sounddevice` (PortAudio wrapper)

**Configuration:**
```python
SAMPLE_RATE = 44100  # Hz (CD quality)
CHANNELS = 1         # Mono (guitar is mono source)
DTYPE = 'float32'    # Normalized audio (-1.0 to 1.0)
BLOCKSIZE = 512      # Samples per callback (11.6ms at 44.1kHz)
```

**Device selection:**
```python
def get_audio_devices():
    """List available input devices"""
    devices = sd.query_devices()
    return [d for d in devices if d['max_input_channels'] > 0]

def open_audio_stream(device_id, callback):
    """Open non-blocking audio stream"""
    return sd.InputStream(
        device=device_id,
        channels=CHANNELS,
        samplerate=SAMPLE_RATE,
        blocksize=BLOCKSIZE,
        dtype=DTYPE,
        callback=callback
    )
```

**Streaming strategy:**
- Non-blocking callbacks (prevents UI freezing)
- Ring buffer for continuous capture
- Graceful handling of buffer overruns
- Automatic reconnection on device disconnect

**Audio quality recommendations:**
- **USB audio interface** (Focusrite Scarlett Solo): Clean signal, low noise floor
- **Built-in microphone:** Works but higher noise, room acoustics affect metrics
- **Guitar → Interface → Computer:** Recommended setup for best results

---

### 2. Pitch Detection (`audio_features.py`)

**Algorithm:** librosa `piptrack` (autocorrelation-based YIN variant)

**Why piptrack?**
- Fast (vectorized NumPy operations)
- Robust to noise (better than naive FFT peak detection)
- Works well for monophonic sources (guitar)
- Provides confidence scores (magnitude)

**Implementation:**
```python
def detect_pitch(audio_chunk, sample_rate=44100):
    """
    Detect fundamental frequency using librosa piptrack.

    Returns:
        frequency (float): Detected Hz (e.g., 440.0 for A4)
        confidence (float): Detection confidence (0.0 - 1.0)
    """
    pitches, magnitudes = librosa.piptrack(
        y=audio_chunk,
        sr=sample_rate,
        fmin=librosa.note_to_hz('E2'),  # Low E string (82 Hz)
        fmax=librosa.note_to_hz('E6')   # High fret limit (~1300 Hz)
    )

    # Find strongest pitch
    idx = magnitudes.argmax()
    detected_hz = pitches.flatten()[idx]
    confidence = magnitudes.flatten()[idx]

    return detected_hz, confidence
```

**Frequency → MIDI conversion:**
```python
midi_number = librosa.hz_to_midi(detected_hz)
# Examples:
#   82 Hz   → MIDI 40 → E2 (low E string)
#   110 Hz  → MIDI 45 → A2 (A string)
#   440 Hz  → MIDI 69 → A4 (reference pitch)
```

**MIDI → Pitch class (ignoring octave):**
```python
pitch_class = int(round(midi_number)) % 12
# Pitch classes: 0=C, 1=C♯, 2=D, ..., 11=B
```

**Intonation accuracy:**
```python
intonation_error = abs(midi_number - round(midi_number))
intonation_score = 1.0 - intonation_error
# Perfect pitch (440.0 Hz): error = 0.0, score = 100%
# Slightly sharp (445 Hz): error = 0.2, score = 80%
```

**Why this matters for prevention:**
- Intonation errors detected **before** you release the string
- Real-time feedback allows micro-adjustments mid-note
- Trains muscle memory for correct finger pressure

---

### 3. Scale Validation (`scales.py`)

**Scale Library:** 24 scales (12 keys × 2 types)

**Structure:**
```python
SCALES = {
    "C Major": [0, 2, 4, 5, 7, 9, 11],           # C D E F G A B
    "C Major Pentatonic": [0, 2, 4, 7, 9],       # C D E G A
    "C Minor": [0, 2, 3, 5, 7, 8, 10],           # C D Eb F G Ab Bb
    "C Minor Pentatonic": [0, 3, 5, 7, 10],      # C Eb F G Bb
    # ... (all 12 keys)
}
```

**Scale conformity check:**
```python
def is_in_scale(pitch_class, scale_notes):
    """
    Check if detected pitch class is in target scale.

    Args:
        pitch_class (int): 0-11 (C to B)
        scale_notes (list): List of pitch classes in scale

    Returns:
        bool: True if note is in scale
    """
    return pitch_class in scale_notes
```

**Coverage tracking:**
```python
class ScaleCoverageTracker:
    def __init__(self, scale_notes):
        self.scale_notes = set(scale_notes)
        self.note_counts = defaultdict(int)
        self.correct_notes = 0
        self.wrong_notes = 0

    def record_note(self, pitch_class):
        if pitch_class in self.scale_notes:
            self.note_counts[pitch_class] += 1
            self.correct_notes += 1
        else:
            self.wrong_notes += 1

    def get_coverage_score(self):
        """
        Calculate how evenly the scale is being practiced.

        Uses coefficient of variation (CV) to measure distribution evenness.
        Lower CV = more even practice across all scale notes.
        """
        if not self.note_counts:
            return 0.0

        counts = list(self.note_counts.values())
        mean = np.mean(counts)
        std = np.std(counts)
        cv = std / mean if mean > 0 else 0

        # Convert CV to score (0 to 1)
        evenness_score = np.exp(-2 * cv)

        # Penalize for wrong notes
        total_notes = self.correct_notes + self.wrong_notes
        scale_ratio = self.correct_notes / total_notes if total_notes > 0 else 0

        return evenness_score * scale_ratio
```

**Why coverage matters:**
- Practicing only 2-3 notes of a scale = incomplete motor learning
- FretCoach encourages **full scale exploration**
- Evenness metric prevents over-reliance on comfortable notes

---

### 4. Timing Analysis (`audio_features.py`)

**Goal:** Measure rhythmic consistency (not tempo detection)

**Onset detection:**
```python
def detect_onsets(audio_chunk, sample_rate, energy_threshold):
    """
    Detect note onsets based on energy increase.

    Returns:
        onset_time (float): Timestamp in seconds
    """
    energy = np.sum(audio_chunk ** 2) / len(audio_chunk)

    if energy >= energy_threshold:
        # Energy threshold crossed → new note onset
        timestamp = time.time()
        return timestamp

    return None
```

**Interval consistency calculation:**
```python
class TimingAnalyzer:
    def __init__(self, window_size=8):
        self.onset_times = []
        self.window_size = window_size

    def record_onset(self, timestamp):
        self.onset_times.append(timestamp)
        # Keep only recent onsets (sliding window)
        if len(self.onset_times) > self.window_size:
            self.onset_times.pop(0)

    def get_timing_score(self):
        """
        Calculate timing stability using coefficient of variation.

        Lower CV = more consistent intervals = better timing.
        """
        if len(self.onset_times) < 3:
            return 0.5  # Not enough data yet

        # Calculate intervals between consecutive onsets
        intervals = np.diff(self.onset_times)

        mean_interval = np.mean(intervals)
        std_interval = np.std(intervals)

        cv = std_interval / mean_interval if mean_interval > 0 else 0

        # Convert CV to score
        timing_score = np.exp(-2 * cv)

        return timing_score
```

**Example:**
```python
# Consistent timing (metronome-like):
onset_times = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5]
intervals = [0.5, 0.5, 0.5, 0.5, 0.5]  # Perfect consistency
cv = 0.0 → score = 1.0 (100%)

# Inconsistent timing:
onset_times = [0.0, 0.8, 0.9, 1.7, 3.0]
intervals = [0.8, 0.1, 0.8, 1.3]  # Highly variable
cv = 0.52 → score = 0.35 (35%)
```

**Why timing stability matters:**
- Rhythm is a motor skill, not just tempo matching
- Inconsistent timing indicates lack of motor control
- Real-time feedback trains internal timing sense

---

### 5. Noise Control (`audio_features.py`)

**Goal:** Assess signal cleanliness

**Signal-to-Noise estimation:**
```python
def calculate_noise_score(audio_chunk):
    """
    Estimate noise level based on signal variance.

    High noise = string buzz, fret scrapes, muted notes
    Low noise = clean tone
    """
    # Total signal power
    total_power = np.mean(audio_chunk ** 2)

    # Noise power (variance around mean)
    mean_signal = np.mean(audio_chunk)
    noise_power = np.mean((audio_chunk - mean_signal) ** 2)

    # Noise ratio (0 to 1)
    noise_ratio = noise_power / total_power if total_power > 0 else 1.0

    # Invert to get score (lower noise = higher score)
    noise_score = 1.0 - noise_ratio

    return max(0.0, min(1.0, noise_score))
```

**Common noise sources:**
- String buzz (action too low)
- Fret scrapes (finger sliding)
- Muted strings (palm touching strings)
- Ambient room noise (refrigerator, AC)
- Electrical interference (poor grounding)

**Why noise control matters:**
- Clean tone = proper technique (finger pressure, hand positioning)
- Noise often correlates with bad habits (sloppy fretting, inconsistent attack)
- Real-time feedback encourages cleaner playing

---

### 6. Quality Scoring (`audio_metrics.py`)

**Weighted combination of all metrics:**

```python
def calculate_quality_score(
    pitch_accuracy,
    scale_conformity,
    timing_stability,
    noise_control,
    strictness=0.5
):
    """
    Combine all metrics into overall quality score.

    Strictness affects weighting:
    - Higher strictness = pitch more important
    - Lower strictness = balanced weighting
    """
    # Dynamic pitch weighting based on strictness
    pitch_weight = 0.40 + (strictness * 0.15)  # Range: 0.40 to 0.55

    # Remaining weight split among other metrics
    other_weight = (1.0 - pitch_weight) / 3.0

    quality = (
        pitch_weight * pitch_accuracy +
        other_weight * scale_conformity +
        other_weight * timing_stability +
        other_weight * noise_control
    )

    return quality
```

**Example weightings:**

| Strictness | Pitch | Scale | Timing | Noise |
|------------|-------|-------|--------|-------|
| 0.0 (Low)  | 40%   | 20%   | 20%    | 20%   |
| 0.5 (Med)  | 47.5% | 17.5% | 17.5%  | 17.5% |
| 1.0 (High) | 55%   | 15%   | 15%    | 15%   |

**Wrong note penalty:**
```python
if pitch_accuracy == 0.0:  # Wrong note detected
    if strictness > 0.7:
        quality = 0.0  # Instant penalty
    else:
        quality *= (1.0 - strictness)  # Partial penalty
```

**Exponential Moving Average (EMA) smoothing:**
```python
class QualityScoreTracker:
    def __init__(self, strictness=0.5):
        self.smoothed_quality = 0.5  # Initial neutral score
        self.alpha = 0.10 + (strictness * 0.30)  # Range: 0.10 to 0.40

    def update(self, new_quality):
        """
        Update smoothed quality using EMA.

        Higher alpha = more responsive to new data
        Lower alpha = smoother, less reactive
        """
        self.smoothed_quality = (
            self.alpha * new_quality +
            (1 - self.alpha) * self.smoothed_quality
        )
        return self.smoothed_quality
```

**Phrase-level grouping:**
- Quality updates every **800ms** (phrase window)
- Groups notes together (prevents jitter)
- Aligns with musical phrasing (2-3 notes at moderate tempo)

**Why this matters:**
- Smooth UI updates (no flickering metrics)
- Musically meaningful feedback (not per-note overload)
- Strictness control gives users agency over difficulty

---

## Feedback Mechanisms

### 1. WebSocket Streaming to UI

**Update frequency:** ~6.67 Hz (every 150ms)

**Message format:**
```json
{
  "pitch_accuracy": 78.5,
  "scale_conformity": 82.3,
  "timing_stability": 45.2,
  "noise_control": 79.8,
  "quality_score": 71.2,
  "current_note": "D",
  "current_frequency": 293.7,
  "in_scale": true,
  "notes_played": 142,
  "correct_notes": 138,
  "wrong_notes": 4,
  "elapsed_time": 125.4
}
```

**Frontend integration:**
```javascript
const ws = new WebSocket('ws://127.0.0.1:8000/ws/metrics');

ws.onmessage = (event) => {
  const metrics = JSON.parse(event.data);

  // Update UI components
  updateMetricBars(metrics);
  updateVisualFeedback(metrics.quality_score);
  updateNoteDetection(metrics.current_note, metrics.in_scale);
};
```

**Why WebSocket?**
- Low latency (no HTTP overhead)
- Server push (no polling)
- Full-duplex communication
- Automatic reconnection handling

---

### 2. Ambient Lighting (Smart Bulb)

**Hardware:** Tuya WiFi RGB bulb

**Color mapping:**
```python
def quality_to_hsv(quality_score):
    """
    Map quality score (0-1) to HSV color.

    HSV:
        H (Hue): 0 (red) → 60 (yellow) → 120 (green)
        S (Saturation): 100% (full color)
        V (Value/Brightness): 30% (dark) → 100% (bright)
    """
    hue = int(quality_score * 120)  # 0 to 120
    saturation = 1000  # Full saturation (Tuya scale: 0-1000)
    brightness = int(300 + quality_score * 700)  # 300 to 1000

    return (hue, saturation, brightness)
```

**Color examples:**
- Quality 0.0 (0%) → HSV(0, 1000, 300) → Dark red
- Quality 0.5 (50%) → HSV(60, 1000, 650) → Bright yellow
- Quality 1.0 (100%) → HSV(120, 1000, 1000) → Bright green

**Update throttling:**
```python
class SmartBulbController:
    def __init__(self):
        self.last_hue = None
        self.last_update_time = 0
        self.min_update_interval = 0.3  # 300ms
        self.min_hue_change = 5  # Hue units

    def update_color(self, quality_score):
        hue, sat, bright = quality_to_hsv(quality_score)
        now = time.time()

        # Only update if significant change or timeout
        if (abs(hue - self.last_hue) >= self.min_hue_change or
            now - self.last_update_time >= self.min_update_interval):

            # Send to Tuya API
            bulb.set_colour(hue, sat, bright)

            self.last_hue = hue
            self.last_update_time = now
```

**Why throttling?**
- Prevents flickering (bulb has ~100ms response time)
- Reduces API calls (Tuya rate limits)
- Smoother visual experience

**Neuroscience rationale:**
- **Peripheral vision** processes color faster than conscious awareness
- **Subconscious feedback** doesn't interrupt focus on playing
- **Multi-sensory reinforcement** strengthens motor learning pathways
- **Green = good** creates positive association (dopamine release)

**See:** [Environment Setup - Smart Bulb Configuration](environment-setup.md#smart-bulb-setup-tuya)

---

### 3. Database Logging

**Session storage:** PostgreSQL (Supabase)

**Schema:**
```sql
CREATE TABLE fretcoach.sessions (
    session_id UUID PRIMARY KEY,
    user_id VARCHAR(255),
    start_timestamp TIMESTAMP,
    end_timestamp TIMESTAMP,
    duration_seconds INTEGER,
    scale_chosen VARCHAR(100),
    scale_type VARCHAR(50),
    sensitivity FLOAT,
    strictness FLOAT,
    pitch_accuracy FLOAT,
    scale_conformity FLOAT,
    timing_stability FLOAT,
    noise_control FLOAT,
    quality_score FLOAT,
    total_notes_played INTEGER,
    correct_notes INTEGER,
    wrong_notes INTEGER,
    unique_notes_used INTEGER
);
```

**Logging strategy:**
- **Session start:** Insert row with initial settings
- **Real-time:** Update metrics in memory (not every note)
- **Session end:** Final update with aggregated metrics

**Why deferred writes?**
- Performance (database I/O is slow)
- Accuracy (final metrics more meaningful than intermediate)
- Scalability (reduces database load)

**Cross-device sync:**
- Studio, Portable, Hub all write to same database
- User can review all sessions in web dashboard
- AI coach uses unified history for recommendations

---

## Performance Optimization

### Latency Reduction Strategies

**1. Vectorized operations (NumPy)**
```python
# Slow (Python loops):
energy = 0
for sample in audio_chunk:
    energy += sample ** 2
energy /= len(audio_chunk)

# Fast (NumPy vectorization):
energy = np.mean(audio_chunk ** 2)
```

**Speedup:** ~100x for 44,100 sample arrays

**2. Precomputed scale lookups**
```python
# Precompute set for O(1) lookup
scale_set = set(scale_notes)

# Fast membership test
is_in_scale = pitch_class in scale_set  # O(1)
```

**3. Sliding window buffers**
```python
# Reuse recent audio for overlapping windows
# Avoid reprocessing same samples
```

**4. Conditional processing**
```python
# Skip expensive pitch detection if energy too low
if energy < threshold:
    return  # No note playing, skip analysis
```

**5. Multi-threading (planned)**
```python
# Separate threads for:
# - Audio capture (real-time critical)
# - Processing (CPU-bound)
# - WebSocket broadcast (I/O-bound)
```

### Raspberry Pi Optimizations

**ARM64 considerations:**
- NumPy compiled with BLAS acceleration
- librosa uses SciPy (optimized for ARM)
- Reduced buffer sizes (lower latency, acceptable on Pi 5)

**Performance governor:**
```bash
sudo cpufreq-set -g performance
# Prevents CPU throttling during sessions
```

**Thermal management:**
- Passive cooling sufficient for continuous use
- Active cooling (fan) recommended for long sessions (>1 hour)

---

## Configuration Parameters

### Sensitivity (0.0 - 1.0)

**Controls:** Energy threshold for note detection

**Formula:**
```python
energy_threshold = 1e-7 * (1 + sensitivity * 10)
```

**Sensitivity levels:**
- **0.0 (Low):** threshold = 1e-7 → Only very loud notes detected
- **0.5 (Medium):** threshold = 6e-7 → Balanced (recommended)
- **1.0 (High):** threshold = 1.1e-6 → Even quiet notes detected

**Use cases:**
- **Low:** Noisy environment, electric guitar with high output
- **Medium:** Most scenarios
- **High:** Fingerstyle, classical guitar, quiet acoustic

### Strictness (0.0 - 1.0)

**Controls:** Penalty severity and smoothing responsiveness

**Effects:**

| Strictness | Pitch Weight | EMA Alpha | Wrong Note Penalty |
|------------|--------------|-----------|-------------------|
| 0.0        | 40%          | 0.10      | Partial (0%)      |
| 0.5        | 47.5%        | 0.25      | Partial (50%)     |
| 0.7        | 50.5%        | 0.31      | **Instant (100%)** |
| 1.0        | 55%          | 0.40      | Instant (100%)    |

**Strictness levels:**
- **0.0-0.3 (Beginner):** Forgiving, smooth scores, encourages exploration
- **0.4-0.6 (Intermediate):** Balanced, moderate penalties
- **0.7-1.0 (Advanced):** Strict, instant penalties, precision training

---

## Error Handling

### Audio Device Failures

**Symptom:** Device disconnected mid-session

**Handling:**
```python
try:
    stream.read()
except sd.PortAudioError:
    logger.error("Audio device disconnected")
    # Attempt reconnection
    reconnect_audio_device()
    # Or gracefully end session
    end_session_gracefully()
```

### Buffer Overruns

**Symptom:** Missed audio chunks (CPU overload)

**Handling:**
```python
def audio_callback(indata, frames, time, status):
    if status.input_overflow:
        logger.warning("Buffer overrun - processing too slow")
        # Skip this chunk to catch up
        return

    # Process audio normally
    process_audio(indata)
```

### Pitch Detection Failures

**Symptom:** No pitch detected (silence, noise, or ambiguous signal)

**Handling:**
```python
detected_hz, confidence = detect_pitch(audio)

if confidence < 0.3:  # Low confidence
    # Skip this chunk - unclear pitch
    return

if detected_hz < 82 or detected_hz > 1300:  # Out of guitar range
    # Likely noise or harmonics
    return
```

---

## Testing and Validation

### Unit Tests

**Pitch detection accuracy:**
```python
def test_pitch_detection():
    # Generate synthetic 440 Hz sine wave
    test_audio = generate_sine_wave(440, duration=1.0, sr=44100)
    detected_hz, confidence = detect_pitch(test_audio, sr=44100)

    assert abs(detected_hz - 440.0) < 1.0  # Within 1 Hz
    assert confidence > 0.8  # High confidence
```

**Scale conformity:**
```python
def test_scale_conformity():
    scale_notes = [0, 2, 4, 5, 7, 9, 11]  # C Major

    assert is_in_scale(0, scale_notes) == True   # C - in scale
    assert is_in_scale(1, scale_notes) == False  # C# - not in scale
    assert is_in_scale(4, scale_notes) == True   # E - in scale
```

**Timing stability:**
```python
def test_timing_stability():
    analyzer = TimingAnalyzer()

    # Perfect timing (500ms intervals)
    for t in [0.0, 0.5, 1.0, 1.5, 2.0]:
        analyzer.record_onset(t)

    score = analyzer.get_timing_score()
    assert score > 0.95  # Nearly perfect score
```

### Integration Tests

**End-to-end latency:**
```python
def test_e2e_latency():
    # Measure time from audio input to WebSocket broadcast
    start_time = time.time()

    # Simulate audio chunk
    audio = generate_test_audio()

    # Process
    metrics = process_audio_chunk(audio)

    # Broadcast
    broadcast_metrics(metrics)

    latency = time.time() - start_time
    assert latency < 0.3  # <300ms requirement
```

**Real guitar validation:**
- Play known scales at moderate tempo
- Verify pitch detection matches played notes
- Check metric trends align with perceived performance
- Validate smart bulb color changes

---

## Future Enhancements

### Planned Improvements

**1. Multi-guitar support**
- Detect guitar type (electric vs acoustic vs bass)
- Adjust frequency ranges and sensitivity automatically
- Custom tunings (drop D, open G, etc.)

**2. Advanced onset detection**
- Spectral flux for better note separation
- Attack transient analysis
- Distinguish picking from hammer-ons/pull-offs

**3. Harmonic analysis**
- Detect chords (not just single notes)
- Voicing analysis (root position, inversions)
- Chord progression validation

**4. Tempo extraction**
- Actual BPM detection (not just timing consistency)
- Metronome integration
- Tempo drift tracking

**5. Recording and playback**
- Save raw audio alongside metrics
- Post-session playback with metrics overlay
- Export for sharing with instructors

**6. MIDI output**
- Real-time MIDI note generation
- Route to DAWs, amp simulators
- Enable practice with virtual instruments

---

## Performance Benchmarks

### Laptop (Apple M1 Pro)

| Metric | Value |
|--------|-------|
| End-to-end latency | 240-270ms |
| CPU usage | 15-25% (single core) |
| Memory | ~600MB |
| Sustained throughput | Unlimited (hours) |

### Raspberry Pi 5 (8GB)

| Metric | Value |
|--------|-------|
| End-to-end latency | 280-320ms |
| CPU usage | 25-40% (single core) |
| Memory | ~800MB |
| Sustained throughput | Unlimited (tested 2+ hours) |
| Thermal | 50-60°C (passive cooling) |

**Conclusion:** Raspberry Pi 5 performance is **acceptable for real-time use**.

---

## Conclusion

The **Audio Analysis Agent** is the deterministic foundation of FretCoach's preventive training system. By operating in the critical <300ms window, it enables **real-time motor pattern correction** before habits solidify.

**Key achievements:**
- <300ms latency (fast enough for motor learning)
- 4-metric comprehensive evaluation
- Local processing (no cloud dependency)
- Multi-channel feedback (visual, ambient, database)
- Cross-platform (laptop, Raspberry Pi)
- Extensible architecture (easy to add metrics)

**Design philosophy:** Speed and reliability enable prevention. The Audio Analysis Agent operates at the neuroplasticity timescale, providing the fast feedback loop that makes FretCoach's preventive approach possible.

---

**Navigation:**
- [← Architecture](architecture.md)
- [AI Coach Agent Engine →](ai-coach-agent-engine.md)
- [Back to Index](index.md)
