# FretCoach Portable - Raspberry Pi Practice Device

Portable guitar practice device running FretCoach's real-time analysis engine on Raspberry Pi 5.

![FretCoach Trifecta](/images/FretCoach%20Trifecta.jpeg)

## Overview

FretCoach Portable is an edge computing practice device — a guitar pedal-like unit running the same audio analysis engine as FretCoach Studio. Practice anywhere with real-time feedback, ambient lighting, and automatic sync to the central database.

**Status:** Prototyping phase (~30% complete)
- **Hardware:** Complete (RPi 5 + Scarlett Solo)
- **Software:** Adaptation in progress

## Current Capabilities

| Feature | Status |
|---------|--------|
| Audio Analysis | ✓ Same engine as Studio |
| Manual Mode | ✓ 24 scales supported |
| AI Mode | ✓ AI-recommended plans |
| Ambient Lighting | ✓ Smart bulb integration |
| Session Logging | ✓ Syncs to Supabase |
| Terminal Display | ✓ Real-time metrics |
| Live AI Voice Feedback | ✗ Desktop only |
| Web UI | ✗ Desktop only |

## Hardware Requirements

- Raspberry Pi 5 (8GB RAM recommended)
- USB Audio Interface (e.g., Focusrite Scarlett Solo)
- MicroSD card (32GB+)
- Smart bulb (optional, Tuya-compatible)
- Guitar with 1/4" cable

## What to Copy to Pi5

You only need these folders/files - **not the entire codebase**:

```
FretCoach/
├── portable/           # This folder (main application)
│   ├── main.py
│   ├── requirements.txt
│   └── __init__.py
│
├── backend/
│   ├── core/           # Shared audio processing modules
│   │   ├── __init__.py
│   │   ├── audio_features.py
│   │   ├── audio_metrics.py
│   │   ├── audio_setup.py
│   │   ├── scales.py
│   │   ├── session_logger.py
│   │   └── smart_bulb.py
│   │
│   ├── sql/            # Database schema (for session logging)
│   │   └── schema.sql
│   │
│   └── api/services/   # Only if using AI Mode
│       └── ai_agent_service.py
│
└── .env                # Your environment variables
```

### Quick Copy Command

From your development machine:

```bash
# Create the directory structure on Pi5
ssh pi@raspberrypi.local "mkdir -p ~/FretCoach/{portable,backend/{core,sql,api/services}}"

# Copy required files
scp -r portable/* pi@raspberrypi.local:~/FretCoach/portable/
scp backend/core/*.py pi@raspberrypi.local:~/FretCoach/backend/core/
scp backend/sql/schema.sql pi@raspberrypi.local:~/FretCoach/backend/sql/
scp .env pi@raspberrypi.local:~/FretCoach/

# Optional: For AI Mode
scp backend/api/services/ai_agent_service.py pi@raspberrypi.local:~/FretCoach/backend/api/services/
```

## Installation on Pi5

```bash
# SSH into your Pi
ssh pi@raspberrypi.local

# Navigate to FretCoach
cd ~/FretCoach/portable

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# For audio support on Raspberry Pi
sudo apt-get install libportaudio2 libportaudiocpp0 portaudio19-dev
```

## Environment Variables (.env)

Create a `.env` file in the project root with:

```env
# Database (for session logging)
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=5432
DB_NAME=your_db_name

# Smart Bulb (optional)
HAVELLS_ACCESS_ID=your_tuya_access_id
HAVELLS_ACCESS_SECRET=your_tuya_access_secret
HAVELLS_DEVICE_ID=your_bulb_device_id
HAVELLS_REGION=in

# AI Mode (optional)
OPENAI_API_KEY=your_openai_key
```

## Running

```bash
cd ~/FretCoach/portable
source venv/bin/activate
python main.py
```

## Use Cases

- **Portable practice** — Practice anywhere without a laptop
- **Backstage warmup** — Pre-performance preparation
- **Travel sessions** — Fits in guitar case
- **Offline practice** — Works without internet (syncs later)
- **Minimal setup** — Pedal-like form factor

## Terminal Display

```
╔══════════════════════════════════════════════════════════╗
║              FRETCOACH — PRACTICE MODE                   ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║ Scale        : A Minor (Pentatonic)                      ║
║ Session Time : 06:42                                     ║
║                                                          ║
║ Pitch Accuracy     [███████░░░] 72%                      ║
║ Timing Stability   [██████░░░░] 65%                      ║
║ Out-of-Scale Rate  [██░░░░░░░░] 18%                      ║
║                                                          ║
║ Current Feedback   🟢  Good playing!                     ║
║                                                          ║
║ Notes: 142 total | 116 correct | 26 wrong                ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

## Modes

### Manual Mode
- Select your own scale from 24 options (12 major + 12 minor)
- Choose between Natural (7 notes) or Pentatonic (5 notes)
- Set your own strictness and sensitivity

### AI Mode
- Analyzes your practice history from the database
- Recommends a scale based on your weakest areas
- Suggests optimal strictness/sensitivity for your level
- Uses Opik tracing for LLM call monitoring

## Troubleshooting

### No audio input detected
```bash
# List audio devices
python -c "import sounddevice; print(sounddevice.query_devices())"

# Make sure your audio interface is recognized
arecord -l
```

### Permission denied for audio
```bash
# Add user to audio group
sudo usermod -a -G audio $USER
# Log out and back in
```

### Database connection failed
- Check your `.env` file has correct credentials
- Ensure the database is accessible from your Pi's network
- Session logging will be skipped if unavailable (practice still works)

### Smart bulb not responding
- Verify Tuya credentials in `.env`
- Check the bulb is on the same network
- Ambient lighting is optional - practice works without it

## Future Roadmap

**Planned enhancements:**
- Physical enclosure design (3D printed pedal case)
- Battery power management for true portability
- LED status indicators
- Physical button controls for start/stop
- Local LCD display (optional)

**Current focus:** Software optimization for real-time performance on ARM architecture

## Documentation

For detailed architecture and usage:
- [System Architecture](../docs/architecture.md#component-3-portable-device-raspberry-pi)
- [Environment Setup](../docs/environment-setup.md)
- [Quickstart Guide](../docs/quickstart.md)
