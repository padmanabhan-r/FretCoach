# FretCoach Portable - Raspberry Pi Practice Device

Edge-powered guitar training in a portable form factor. Practice anywhere with the same real-time analysis engine as FretCoach Studio.

![FretCoach Portable](../images/FretCoach%20Portable.png)

---

## Overview

FretCoach Portable is a **Raspberry Pi 5-based practice device** that runs the same core analysis engine as FretCoach Studio in a portable, standalone package.

**Key benefit:** Practice anywhere—hotel rooms, living room, band studios—without a laptop.

---

## Hardware

<p align="center">
  <img src="../images/FretCoach Portable Rpi5.png" alt="FretCoach Portable Raspberry Pi 5" width="500"/>
</p>

**Core components:**
- **Raspberry Pi 5** (8GB RAM) — Audio processing + AI orchestration
- **Focusrite Scarlett Solo** — Professional guitar input
- **microSD 64GB+** — OS, software, local cache
- **WiFi/Ethernet** — Database sync, AI API calls
- **Tuya smart bulb** (optional) — Ambient feedback

**Planned:**
- Battery pack (4-6 hours)
- Footswitch for hands-free control
- 3D-printed pedalboard enclosure
- 7" touchscreen display

---

## Software

Runs the **same audio analysis code** as FretCoach Studio:

```
┌─────────────────────────────┐
│    Raspberry Pi 5 (Linux)   │
│                             │
│  Python FastAPI Backend     │
│  • Same audio_processor.py  │
│  • Same metrics engine      │
│  • Same AI integration      │
│                             │
│  Terminal UI (Rich/Textual) │
│  • Live metric display      │
│  • Session controls         │
│  • Mode selection           │
└─────────────────────────────┘
```

**Shared codebase:**
- `backend/core/audio_features.py` — DSP algorithms
- `backend/core/audio_metrics.py` — Quality scoring
- `backend/core/scales.py` — Scale library
- `backend/api/services/` — AI services

**Portable-specific:**
- `portable/main.py` — Terminal UI
- `portable/start.sh` — Launch script

---

## Features

### 1. Real-Time Audio Analysis

Same four-metric system as Studio:
- **Pitch Accuracy** — Intonation
- **Scale Conformity** — Scale adherence + fretboard coverage
- **Timing Stability** — Note spacing consistency
- **Noise Control** — Signal clarity

Updates every ~300ms with exponential smoothing.

### 2. Terminal UI

Clean, responsive interface using Rich library:

```
╔════════════════════════════════════════════════════╗
║              FretCoach Portable v1.0               ║
╠════════════════════════════════════════════════════╣
║                                                    ║
║ Session Status: Running                            ║
║ Time: 00:03:42                                     ║
║                                                    ║
║ Pitch Accuracy     [████████░░] 82% 🟢             ║
║ Scale Conformity   [██████░░░░] 65% 🟡             ║
║ Timing Stability   [█████░░░░░] 58% 🟡             ║
║ Noise Control      [████████░░] 79% 🟢             ║
║                                                    ║
║ Overall Quality    71% 🟢 Good playing!            ║
║                                                    ║
║ Notes: 142 | Correct: 138 | Wrong: 4              ║
╚════════════════════════════════════════════════════╝

Commands: [s]top | [p]ause | [q]uit
```

### 3. Practice Modes

**Manual Mode:** Choose scale and settings manually

**AI Mode:** Get personalized recommendations based on session history

Same AI models as Studio (GPT-4o-mini, Gemini).

### 4. Database Sync

All sessions sync to shared PostgreSQL database:
- Start/end timestamps
- Final metric scores
- Note statistics
- Scale and settings

View sessions on FretCoach Hub web dashboard.

### 5. Ambient Lighting

Smart bulb control for environmental feedback:
- 🟢 Green (70%+) — Good
- 🟡 Yellow (50-70%) — Average
- 🔴 Red (<50%) — Needs work

---

## Setup

### Hardware Assembly

1. **Raspberry Pi 5** with Debian Linux
2. **Focusrite Scarlett Solo** connected via USB
3. **Smart bulb** on same WiFi (optional)
4. **HDMI display** for terminal UI

### Software Installation

```bash
# Clone repo
git clone https://github.com/padmanabhan-r/FretCoach.git
cd FretCoach

# Install dependencies (from project root)
uv sync

# Configure environment
cp backend/.env.example backend/.env
# Edit .env with database and API credentials
```

> **Environment setup:** [Environment Setup Guide](environment-setup.md)

### Running

```bash
cd portable
./start.sh
```

Follow on-screen prompts to:
1. Select audio device
2. Choose practice mode (Manual/AI)
3. Configure settings
4. Start session

---

## Configuration

Same settings as Desktop app:

**Sensitivity (0.0 - 1.0):**
- Low (0.2) — Only loud notes
- Medium (0.5) — Balanced
- High (0.8) — Detects quiet notes

**Strictness (0.0 - 1.0):**
- Low (0.2) — Forgiving
- Medium (0.5) — Balanced
- High (0.8) — Strict penalties

**Metric Toggles:**
- Enable/disable individual metrics
- Preferences persist across sessions

---

## Performance

**Audio latency:** <50ms (input → processing → display)

**Metrics update:** ~300ms intervals

**CPU usage:** 15-25% on Pi 5 (single core)

**Memory:** ~200MB Python backend + ~50MB terminal UI

**Power:** 5W typical (15W with smart bulb)

---

## Current Status

**✅ Working:**
- Real-time audio analysis
- Terminal UI with live metrics
- Manual and AI practice modes
- Database sync
- Smart bulb control

**🚧 In Progress:**
- Touchscreen display integration
- Footswitch support
- Battery power optimization

**📋 Planned:**
- Custom enclosure design
- Web-based config interface
- Multi-guitar support

---

## Troubleshooting

**Audio device not detected:**
- Check USB connection: `lsusb`
- Grant permissions: `sudo usermod -a -G audio $USER`

**Database connection failed:**
- Verify WiFi connection
- Check `.env` credentials
- Test connectivity: `ping db.your-supabase-host.co`

**Smart bulb not responding:**
- Ensure bulb and Pi on same network
- Verify Tuya credentials in `.env`

**Poor performance:**
- Close unnecessary processes
- Use wired Ethernet instead of WiFi for database
- Lower metric update frequency

---

## vs Desktop App

| Feature | Desktop | Portable |
|---------|:-------:|:--------:|
| Audio Analysis | ✅ | ✅ |
| Visual Metrics | GUI | Terminal |
| AI Coaching | ✅ | ✅ |
| Live Voice Feedback | ✅ | 📋 Planned |
| Ambient Lighting | ✅ | ✅ |
| Database Sync | ✅ | ✅ |
| Portability | ❌ | ✅ |
| Screen Required | Desktop | Any HDMI |

---

**Navigation:**
- [← Desktop Application](desktop-app.md)
- [Web Dashboard →](web-dashboard.md)
- [Back to Index](index.md)
