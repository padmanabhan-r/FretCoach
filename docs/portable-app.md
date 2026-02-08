# FretCoach Portable - Raspberry Pi Practice Device

Edge-powered guitar training in a portable form factor. Practice anywhere with the same real-time analysis engine as FretCoach Studio.

![FretCoach Portable](assets/images/pedal-device.jpg)

---

## Overview

FretCoach Portable is a **Raspberry Pi 5-based practice device** that brings the full power of real-time audio analysis and AI coaching to a portable, standalone package. It runs the same core analysis engine as FretCoach Studio but in an edge-computing environment optimized for portability and independence.

**Key Philosophy:** Practice should not be confined to your desk. FretCoach Portable enables neural adaptation training anywhere—your living room, practice space, or on the road.

---

## Why Portable Matters

### Neuroplasticity and Context

Motor learning is **context-dependent**. Practicing in multiple environments:
- Strengthens neural pathways through varied stimulus
- Reduces location-specific dependencies
- Improves performance consistency across contexts
- Enables practice during limited time windows (travel, breaks)

### Traditional Limitations

Desktop-only systems restrict practice to:
- Fixed locations (home office, studio)
- Specific times (when computer is available)
- Wired infrastructure requirements

### FretCoach Portable Solution

**Practice anywhere:**
- Hotel rooms during travel
- Living room jam sessions
- Outdoor practice spaces
- Band rehearsal studios

**Zero setup friction:**
- Boot → Plug guitar → Play
- No laptop required
- Integrated audio interface
- Battery-powered option (future)

**Same quality training:**
- Identical audio analysis algorithms
- Real-time metric evaluation
- Database synchronization
- AI practice recommendations

---

## Hardware Architecture

<p align="center">
  <img src="assets/images/fretcoach-pedal.jpeg" alt="FretCoach Portable Hardware" width="500"/>
</p>

<p align="center">
  <img src="assets/images/portable/FretCoach Portable Rpi5.png" alt="FretCoach Portable Raspberry Pi 5" width="500"/>
</p>

### Core Components

| Component | Specification | Purpose |
|-----------|--------------|---------|
| **Compute** | Raspberry Pi 5 (8GB RAM) | Audio processing, AI orchestration |
| **Audio Interface** | Focusrite Scarlett Solo USB | Professional-grade guitar input |
| **Storage** | microSD 64GB+ (Class 10, A2) | OS, software, local session cache |
| **Display** | HDMI touchscreen (7" planned) | Metric visualization, control interface |
| **Connectivity** | WiFi 6, Gigabit Ethernet | Database sync, AI API calls |
| **Ambient Feedback** | Tuya smart bulb (WiFi) | Environmental performance feedback |

### Optional Enhancements (Planned)

- **Battery Pack:** 20,000mAh USB-C PD for 4-6 hours practice
- **Footswitch:** Start/stop sessions hands-free
- **3D-Printed Enclosure:** Pedalboard-style rugged case
- **LCD Touchscreen:** Integrated 7" display for standalone operation

---

## Software Architecture

### Same Core, Different Package

FretCoach Portable runs **identical audio analysis code** as FretCoach Studio:

```
┌───────────────────────────────────────────────────┐
│           Raspberry Pi 5 (Debian Linux)           │
│  ───────────────────────────────────────────────  │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │      Python FastAPI Backend                 │ │
│  │  ─────────────────────────────────────────  │ │
│  │  • audio_processor.py (same as Studio)      │ │
│  │  • audio_features.py (librosa)              │ │
│  │  • audio_metrics.py (scoring)               │ │
│  │  • session_service.py (database)            │ │
│  │  • ai_agent_service.py (LLM orchestration)  │ │
│  │  • smart_bulb.py (ambient feedback)         │ │
│  └─────────────────────────────────────────────┘ │
│                     ▲                             │
│                     │                             │
│  ┌──────────────────┴──────────────────────────┐ │
│  │      Lightweight Web UI (React)             │ │
│  │  ──────────────────────────────────────────│ │
│  │  • Minimal UI optimized for small screens   │ │
│  │  • WebSocket metric updates                 │ │
│  │  • Touch-friendly controls                  │ │
│  │  • Session start/stop                       │ │
│  └─────────────────────────────────────────────┘ │
│                                                   │
└────────────┬──────────────────────────┬───────────┘
             │                          │
             ▼                          ▼
    ┌─────────────────┐       ┌─────────────────┐
    │ Scarlett Solo   │       │  PostgreSQL DB  │
    │  USB Audio I/O  │       │   (Supabase)    │
    └────────┬────────┘       └─────────────────┘
             │
             ▼
           🎸 Guitar
```

### Code Reuse Strategy

**Shared modules** (`/backend/`):
- `audio_processor.py` — Real-time analysis orchestrator
- `audio_features.py` — Pitch, scale, timing, noise metrics
- `audio_metrics.py` — Quality scoring and EMA smoothing
- `scales.py` — Scale library (24 scales)
- `session_service.py` — Database operations
- `ai_agent_service.py` — Practice plan generation
- `smart_bulb.py` — Tuya API integration

**Platform-specific** (`/portable/`):
- `portable_server.py` — Lightweight FastAPI server
- `portable_ui/` — React UI optimized for small screens
- `system_setup.sh` — Raspberry Pi OS configuration
- `autostart.service` — Systemd service for boot-on-start

**Result:** Bug fixes and feature improvements propagate automatically across all platforms.

---

## Features

### Real-Time Audio Analysis

**Same as Studio:**
- 4 metric evaluation (pitch, scale, timing, noise)
- <300ms latency
- Local processing (no cloud dependency for analysis)
- Continuous note detection
- WebSocket metric streaming

**Optimizations for Pi:**
- Reduced buffer sizes for lower latency
- Single-threaded processing (sufficient for real-time)
- Automatic CPU governor scaling (performance mode during sessions)

### Practice Modes

#### Manual Mode
- Select scale, type, sensitivity, strictness
- Immediate session start
- Offline-capable (no internet required)

#### AI Mode
- Fetch practice plan from database (requires WiFi)
- AI-recommended scale and settings
- Reasoning display
- Fallback to manual if offline

### Ambient Lighting

**Same smart bulb integration as Studio:**
- Green → Yellow → Orange → Red performance feedback
- Subconscious reinforcement
- WiFi-based control (Tuya API)

### Database Synchronization

**Cross-device practice history:**
- Sessions logged to PostgreSQL (Supabase)
- Same `fretcoach.sessions` table as Studio and Hub
- Practice anywhere, review everywhere
- AI recommendations based on unified history

### Offline Capability

**Critical for portability:**
- Manual mode works with **zero internet**
- Local audio processing (librosa runs on-device)
- Sessions cached locally if database unreachable
- Automatic sync when WiFi restored

---

## Performance Characteristics

### Raspberry Pi 5 Benchmarks

**Audio Processing:**
- Latency: ~280ms (comparable to Studio on laptop)
- CPU usage: 25-40% (single core)
- Memory: ~800MB (Python + librosa + NumPy)

**Boot Time:**
- Cold boot to ready: ~45 seconds
- Service start to audio ready: ~8 seconds

**Power Consumption:**
- Idle: ~3.5W
- Active session: ~6W
- With USB audio interface: ~8W

**Thermal:**
- Passive cooling sufficient for continuous operation
- CPU temp: 50-60°C during sessions
- No throttling observed

---

## Development Status

**Current Phase:** Prototyping and integration

### Completed ✅

- ✅ Hardware assembly and testing
- ✅ Raspberry Pi OS configuration
- ✅ Audio interface I/O validation
- ✅ Backend software ported to ARM64
- ✅ librosa performance testing on Pi
- ✅ Database connection and sync
- ✅ Smart bulb integration tested

### In Progress 🚧

- 🚧 Lightweight React UI development
- 🚧 Touch-optimized controls
- 🚧 System service configuration (autostart)
- 🚧 Offline session caching mechanism

### Planned 📋

- 📋 3D-printed enclosure design (pedalboard-style)
- 📋 Integrated 7" touchscreen LCD
- 📋 Footswitch integration (GPIO)
- 📋 Battery power option (USB-C PD)
- 📋 LED status indicators (session active, AI mode, etc.)
- 📋 Field testing and durability validation

---

## Setup Instructions

### Hardware Assembly

**Required components:**
1. Raspberry Pi 5 (8GB recommended)
2. Raspberry Pi 5 official power supply (27W USB-C)
3. microSD card 64GB+ (SanDisk Extreme recommended)
4. Focusrite Scarlett Solo (USB bus-powered)
5. HDMI display (temporary for initial setup)
6. USB keyboard/mouse (temporary)

**Assembly:**
1. Flash Raspberry Pi OS (64-bit) to microSD
2. Insert microSD into Pi
3. Connect HDMI display and peripherals
4. Connect Scarlett Solo via USB
5. Power on with USB-C supply

### Software Installation

**1. System setup:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y \
    python3.11 \
    python3-pip \
    portaudio19-dev \
    libsndfile1 \
    libatlas-base-dev \
    git

# Install Node.js for UI
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

**2. Clone repository:**
```bash
cd ~
git clone https://github.com/yourusername/FretCoach.git
cd FretCoach
```

**3. Install uv and backend dependencies:**
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

cd backend
uv sync

# Create .env file
cp .env.example .env
# Edit .env with your credentials
nano .env
```

**4. Portable UI setup:**
```bash
cd ../portable/portable_ui
npm install
npm run build
```

**5. Test audio interface:**
```bash
# List audio devices
python3 -c "import sounddevice as sd; print(sd.query_devices())"

# Should show Scarlett Solo in list
```

**6. Test backend:**
```bash
cd ~/FretCoach/backend
uv run uvicorn backend.api.server:app --host 0.0.0.0 --port 8000

# Open browser: http://<pi-ip>:8000/docs
```

### Autostart Configuration (Optional)

**Create systemd service:**
```bash
sudo nano /etc/systemd/system/fretcoach-portable.service
```

**Service file:**
```ini
[Unit]
Description=FretCoach Portable Backend
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/FretCoach/backend
ExecStart=/home/pi/.cargo/bin/uv run uvicorn backend.api.server:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable fretcoach-portable.service
sudo systemctl start fretcoach-portable.service
sudo systemctl status fretcoach-portable.service
```

**Auto-launch browser UI:**
```bash
# Add to ~/.config/autostart/fretcoach-ui.desktop
[Desktop Entry]
Type=Application
Name=FretCoach UI
Exec=chromium-browser --kiosk --app=http://localhost:8000
```

---

## Usage Guide

### Starting a Practice Session

**Manual Mode:**
1. Power on device (if not always on)
2. Wait for boot (~45 seconds)
3. UI loads automatically (kiosk mode)
4. Select **Manual Mode**
5. Choose scale, type, sensitivity, strictness
6. Enable ambient lighting (optional)
7. Tap **Start Session**
8. Play guitar
9. Monitor real-time metrics
10. Tap **End Session** when done
11. Review summary

**AI Mode (WiFi required):**
1. Boot device
2. Ensure WiFi connected
3. Select **AI Mode**
4. Wait for practice plan (~2-3 seconds)
5. Review recommendation
6. Tap **Accept** or **Generate New**
7. Session starts with AI settings
8. Play and receive live feedback
9. End session and sync to database

### Connecting to WiFi

**Via UI (if available):**
- Settings → WiFi → Select network → Enter password

**Via command line:**
```bash
sudo raspi-config
# System Options → Wireless LAN → Enter SSID and password
```

### Viewing Sessions on Web Dashboard

**All sessions sync to central database:**
1. Visit [fretcoach.online/dashboard](https://fretcoach.online/dashboard)
2. Log in with your user ID
3. View portable sessions alongside Studio sessions
4. Analyze trends and progress
5. Get AI coaching insights

---

## Troubleshooting

### Audio Interface Not Detected

**Symptom:** No audio input from Scarlett Solo

**Solutions:**
1. Check USB connection (try different USB 3.0 port)
2. Verify interface shows in `lsusb` output
3. Check ALSA devices: `arecord -l`
4. Restart ALSA: `sudo alsactl init`
5. Check power delivery (Pi 5 needs 27W supply)

### High Latency

**Symptom:** >500ms delay in metric updates

**Solutions:**
1. Reduce buffer size in `audio_setup.py`
2. Set CPU governor to performance: `sudo cpufreq-set -g performance`
3. Close background processes
4. Check CPU temp (thermal throttling if >80°C)

### Database Sync Failure

**Symptom:** Sessions not appearing in web dashboard

**Solutions:**
1. Check WiFi connection: `ping google.com`
2. Verify `.env` database credentials
3. Check Supabase connection: `psql <connection_string>`
4. Review backend logs: `journalctl -u fretcoach-portable.service`
5. Sessions cache locally and retry sync automatically

### Smart Bulb Not Responding

**Symptom:** Ambient lighting not changing colors

**Solutions:**
1. Verify bulb is powered on and connected to WiFi
2. Check Tuya credentials in `.env`
3. Test bulb via Tuya Smart app
4. Ensure Pi and bulb on same network (or bulb has internet access)
5. Check backend logs for Tuya API errors

---

## Hardware Expansion Ideas

The Pi 5's GPIO and USB ports enable further customization:

- **Pedalboard integration:** 3D-print a pedalboard-format enclosure with footswitch (GPIO) for hands-free session control
- **Battery power:** A 20,000mAh+ USB-C PD pack (~45W) gives 4–6 hours of runtime
- **Touchscreen:** The official Raspberry Pi 7" display (DSI connector) eliminates the need for an external monitor

---

## Performance Comparison

| Feature | Studio (Laptop) | Portable (Pi 5) |
|---------|----------------|-----------------|
| **Audio Latency** | 250-300ms | 280-320ms |
| **CPU Usage** | 15-25% | 25-40% |
| **Memory Usage** | ~600MB | ~800MB |
| **Boot Time** | N/A (host OS) | 45 seconds |
| **Power Draw** | 15-30W | 8-10W |
| **Portability** | Requires laptop | Standalone device |
| **Cost** | $0 (software only) | ~$150 (hardware) |
| **AI Features** | Full support | Full support |
| **Offline Capability** | Full (Manual Mode) | Full (Manual Mode) |

**Verdict:** Nearly identical performance with superior portability.

---

## Future Enhancements

### Planned Features

- **Multi-guitar support:** Switch between guitar profiles (electric, acoustic, bass)
- **Bluetooth audio:** Wireless headphone output
- **MIDI integration:** Connect to DAWs and amp simulators
- **Looper mode:** Practice over recorded backing tracks
- **Session recording:** Save audio for post-practice review

### Research Ideas

- **Haptic feedback:** Vibration motors for tactile error indication
- **E-ink display:** Low-power metric display option
- **Solar charging:** Outdoor practice capability
- **Mesh networking:** Multi-device jam sessions with synchronized feedback

---

## Bill of Materials (BOM)

| Component | Model | Price (USD) | Link |
|-----------|-------|-------------|------|
| Single Board Computer | Raspberry Pi 5 (8GB) | $80 | [raspberrypi.com](https://www.raspberrypi.com/products/raspberry-pi-5/) |
| Power Supply | Official Pi 5 27W USB-C | $12 | [raspberrypi.com](https://www.raspberrypi.com/products/27w-power-supply/) |
| Storage | SanDisk Extreme 64GB microSD | $12 | Amazon |
| Audio Interface | Focusrite Scarlett Solo (Gen 3) | $120 | Sweetwater |
| Display (optional) | Raspberry Pi 7" Touchscreen | $70 | [raspberrypi.com](https://www.raspberrypi.com/products/raspberry-pi-touch-display/) |
| Smart Bulb (optional) | Tuya RGB Smart Bulb | $15 | Amazon |
| Case (optional) | 3D-Printed Custom Enclosure | $20 | (DIY or print service) |
| Footswitch (planned) | Generic momentary footswitch | $10 | Amazon |
| **Total (minimal)** | | **$224** | |
| **Total (full featured)** | | **$339** | |

---

## Conclusion

FretCoach Portable demonstrates that **edge computing enables neuroplasticity training anywhere**. By packaging the full FretCoach audio analysis engine into a Raspberry Pi form factor, we eliminate the primary barrier to consistent practice: location dependency.

**Key achievements:**
- Same analysis quality as desktop
- <300ms real-time performance on ARM64
- Full database sync and AI integration
- True portability (standalone device)
- Offline-capable manual mode

**Philosophy:** Guitar mastery requires **consistent, high-quality practice**. FretCoach Portable ensures that real-time AI coaching travels with you—hotel rooms, rehearsal spaces, living rooms, anywhere your guitar goes.

---

**Navigation:**
- [← Desktop Application](desktop-app.md)
- [Web Dashboard →](web-dashboard.md)
- [Back to Index](index.md)
