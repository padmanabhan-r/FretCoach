# Audio Analysis Agent Engine - The Fast Loop

Real-time audio processing engine that provides <300ms feedback on every note you play. The deterministic "Fast Brain" of FretCoach's dual-brain architecture.

![FretCoach Brain Architecture](assets/images/FretCoach%20Brain.png)

---

## Overview

The **Audio Analysis Agent** is FretCoach's real-time processing engine—a deterministic, local audio analysis system that operates independently of cloud services.

**Design Philosophy:** Preventive intervention requires **speed**. The engine operates in the critical <300ms window where the brain can still adjust motor patterns.

---

## Dual-Brain Architecture

```
┌─────────────────────────────────────┐
│  AUDIO ANALYSIS AGENT (Fast Loop)  │
│  • Local processing (no cloud)     │
│  • <300ms latency                  │
│  • Deterministic algorithms        │
│  • 4 metric evaluation             │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│      AI COACH (Slow Loop)          │
│  • Cloud LLM APIs                  │
│  • 1-3 second latency              │
│  • Strategic coaching              │
└─────────────────────────────────────┘
```

**Why separation?**
- **Speed:** Can't wait for LLM API calls
- **Reliability:** Works offline
- **Cost:** Running pitch detection via GPT-4 would be expensive
- **Privacy:** Playing never leaves your device

---

## Processing Pipeline

```
Guitar → Audio Interface → Analysis → Output

1. Audio Capture (44.1kHz, mono)
   ↓
2. Windowing (800ms chunks, 50% overlap)
   ↓
3. Feature Extraction (librosa)
   ├─ Pitch detection
   ├─ Onset detection
   └─ Noise estimation
   ↓
4. Metric Calculation
   ├─ Pitch Accuracy
   ├─ Scale Conformity
   ├─ Timing Stability
   └─ Noise Control
   ↓
5. Quality Scoring (EMA smoothing)
   ↓
6. Multi-Channel Feedback
   ├─ WebSocket → UI
   ├─ Tuya API → Smart Bulb
   └─ PostgreSQL → Session logs
```

**Total latency:** 250-300ms (measured end-to-end)

---

## Core Components

### 1. Audio Capture

**Library:** `sounddevice` (PortAudio wrapper)

**Configuration:**
- Sample rate: 44.1kHz (CD quality)
- Channels: Mono (guitar is mono)
- Block size: 512 samples (~11.6ms)

**Strategy:** Non-blocking callbacks with ring buffer for continuous capture.

---

### 2. Feature Extraction

**Pitch Detection:**
- Algorithm: `librosa.piptrack()` (YIN-based)
- Frequency → MIDI note → Pitch class (C, C#, D, etc.)
- Confidence threshold to filter noise

**Onset Detection:**
- Energy-based detection
- Coefficient of variation on recent intervals
- Filters sustained notes vs. new attacks

**Noise Estimation:**
- RMS energy of audio signal
- Zero-crossing rate analysis

---

### 3. Metrics Engine

Four core metrics evaluated every ~300ms:

#### Pitch Accuracy
Measures intonation and note correctness.

**Calculation:**
- Detect pitch frequency
- Compare to ideal frequency for note
- Check if note is in chosen scale
- Penalize out-of-scale notes based on strictness

**Weight:** 40-55% (adjustable by strictness setting)

---

#### Scale Conformity
Measures scale adherence and fretboard coverage.

**Calculation:**
- Track which scale notes you've played
- Measure evenness of note distribution (entropy)
- Penalize playing same notes repeatedly
- Reward exploring full scale coverage

**Components:**
- **Pitch stability:** How consistently you stay in-scale
- **Scale coverage:** How many different notes you use

---

#### Timing Stability
Measures rhythmic consistency.

**Calculation:**
- Track time intervals between note onsets
- Calculate coefficient of variation (std/mean)
- Lower CV = more consistent timing
- Not a metronome—measures your consistency

**Range:** 0-100% (higher = more consistent)

---

#### Noise Control
Measures signal clarity.

**Calculation:**
- RMS energy level
- Zero-crossing rate (indicator of high-frequency noise)
- Penalizes string buzz, fret noise, unwanted artifacts

**Always enabled:** Mandatory baseline quality metric

---

### 4. Quality Scoring

**Weighted Combination:**
```
quality_score = (
    pitch_accuracy * pitch_weight +
    scale_conformity * scale_weight +
    timing_stability * timing_weight +
    noise_control * noise_weight
)
```

**Weights adjust based on:**
- Strictness setting (higher strictness = more pitch weight)
- Enabled metrics (disabled metrics get 0 weight)
- User preferences (stored in database)

**Smoothing:**
- Exponential Moving Average (EMA) prevents jittery UI
- Alpha value: `0.10 + (strictness * 0.30)`
- Wrong notes at high strictness instantly drop quality to 0

---

### 5. Feedback Channels

**WebSocket (UI):**
- Updates at ~6.67 Hz (every 150ms)
- JSON payload with all metrics
- Color-coded performance indicators

**Smart Bulb (Tuya):**
- HSV color mapping from quality score
- Green (70%+) → Yellow (50-70%) → Red (<50%)
- Throttled to 300ms to prevent flickering

**Database (PostgreSQL):**
- Session start/end timestamps
- Final metric scores
- Note counts and statistics
- User and device metadata

---

## Configuration

### Sensitivity (0.0 - 1.0)
Controls note detection threshold.

- **Low (0.2):** Only loud notes
- **Medium (0.5):** Balanced
- **High (0.8):** Detects quiet notes

Formula: `energy_threshold = 1e-7 * (1 + sensitivity * 10)`

### Strictness (0.0 - 1.0)
Controls wrong note penalties.

- **Low (0.2):** Forgiving, gradual changes
- **Medium (0.5):** Balanced
- **High (0.8):** Strict, wrong notes drop score to 0

**Effects:**
- EMA smoothing speed
- Pitch weight in overall score
- Wrong note penalty severity

---

## Code Structure

**Location:** `backend/core/`

**Key files:**
- `audio_setup.py` — Device enumeration, stream management
- `audio_features.py` — DSP algorithms (pitch, onset, noise)
- `audio_metrics.py` — Quality scoring and EMA smoothing
- `scales.py` — Scale definitions (24 scales × 2 types)
- `smart_bulb.py` — Tuya API integration
- `session_logger.py` — PostgreSQL session persistence

**Service layer:** `backend/api/services/audio_processor.py`
- Orchestrates the full pipeline
- Manages WebSocket connections
- Handles session lifecycle

---

## Performance Characteristics

**CPU Usage:**
- Desktop: 10-15% (single core)
- Raspberry Pi 5: 15-25% (single core)

**Memory:**
- Audio buffer: ~10 MB
- Feature cache: ~5 MB
- Total: ~200 MB Python process

**Latency:**
- Audio capture: ~23ms
- Processing: ~100-150ms
- WebSocket: ~10ms
- UI render: ~16ms
- **Total: 250-300ms**

**Update frequency:**
- Metric calculations: Every ~300ms
- WebSocket updates: ~6.67 Hz (150ms)
- Smart bulb updates: ~3.33 Hz (300ms)

---

## Technical Details

### Libraries Used

- **NumPy** — Array operations, FFT
- **librosa** — Audio feature extraction
- **SciPy** — Signal processing utilities
- **sounddevice** — Audio I/O
- **psycopg2** — PostgreSQL connection
- **tinytuya** — Smart bulb control

### Audio Processing

**Windowing:**
- 800ms windows with 50% overlap
- Hann window function for smooth edges
- Prevents spectral leakage

**Pitch Detection:**
- YIN algorithm (via librosa)
- Frequency domain analysis
- Confidence threshold: 0.5

**Onset Detection:**
- Energy-based with coefficient of variation
- Distinguishes new notes from sustained notes

---

## Offline Capability

The audio analysis engine works completely offline:

✅ **Local processing only:**
- All DSP runs on-device
- No cloud API calls in the fast loop
- Session logging queues if database unavailable

✅ **Degraded mode:**
- If PostgreSQL unreachable: Sessions not saved, but practice continues
- If smart bulb unavailable: Visual feedback continues
- If LLM APIs down: Manual mode still works (AI mode needs connectivity)

---

## Shared Codebase

**Desktop, Portable, and Web** all use the same audio analysis code:

```
backend/core/
  ├── audio_features.py    ← Shared across all platforms
  ├── audio_metrics.py     ← Shared
  ├── scales.py            ← Shared
  └── session_logger.py    ← Shared
```

**Platform differences:**
- **Desktop:** Electron GUI
- **Portable:** Terminal UI (Rich library)
- **Web:** No local audio (analytics only)

**Result:** Code changes propagate to all platforms automatically.

---

## Future Enhancements

**Planned improvements:**
- Chord recognition (multi-note detection)
- Harmonic analysis (frequency ratios)
- Adaptive difficulty (auto-adjust strictness)
- Multi-guitar support (stereo input)
- Real-time recording and playback

---

**Navigation:**
- [← Architecture](architecture.md)
- [AI Coach Agent Engine →](ai-coach-agent-engine.md)
- [Back to Index](index.md)
