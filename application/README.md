# FretCoach Studio - Desktop Application

Desktop training environment for real-time guitar practice with AI coaching and ambient feedback.

![FretCoach Trifecta](/images/FretCoach%20Trifecta.jpeg)

## Overview

FretCoach Studio is the primary practice interface for FretCoach. It provides real-time audio analysis, live AI coaching with vocal feedback, on-screen metrics, and smart bulb integration — all synced to a central database for cross-device tracking.

![Studio Home Page](../docs/assets/images/studio/1.%20Studio%20-%20Home%20Page.png)

## Key Features

- **Real-time Audio Analysis** — Continuous evaluation of pitch, scale conformity, timing, and noise
- **Live AI Coaching** — Spoken feedback during practice using GPT-4o-mini-TTS
- **Dual Practice Modes:**
  - *Manual Mode* — Choose your own scale, sensitivity, and strictness
  - *AI Mode* — Get AI-recommended practice plans based on history
- **Ambient Lighting** — Smart bulb visual feedback (green = good, red = needs work)
- **Session Logging** — Automatic save to Supabase PostgreSQL
- **Performance Metrics** — Real-time scoring across four metrics

![FretCoach Brain Architecture](/images/FretCoach%20Brain.png)

### Practice Modes

**Mode Selection:**

![Mode Selection](../docs/assets/images/studio/2.%20Studio%20-%20Mode%20Selection.png)

**Manual Mode - Scale Selection:**

![Scale Selection](../docs/assets/images/studio/3.%20Studio%20-%20Manual%20Mode%20-%20Scale%20Selection.png)

**Manual Mode - Scale Type:**

![Scale Type](../docs/assets/images/studio/4.%20Studio%20-%20Manual%20Mode%20-%20Scale%20Type.png)

**Manual Mode - Practice Settings:**

![Practice Settings](../docs/assets/images/studio/5.%20Studio%20-%20Manual%20Mode%20-%20Practice%20Settings.png)

**AI Mode - Coach Analyzing:**

![Coach Analyzing](../docs/assets/images/studio/6.%20Studio%20-%20Coach%20Analysing.png)

**AI Mode - Recommendations:**

![AI Recommendations](../docs/assets/images/studio/8.%20Studio%20-%20AI%20Coach%20Rec.png)

**Live Practice Session:**

![Live Session](../docs/assets/images/studio/9.%20Studio%20-%20Live%20Session.png)

## Tech Stack

- **Frontend:** Electron, React, Vite, Tailwind CSS
- **Backend:** Python, FastAPI
- **Audio Processing:** NumPy, librosa, sounddevice
- **AI:** LangChain, OpenAI, Google Gemini
- **Database:** PostgreSQL (Supabase)

## Installation

```bash
npm install
```

## Development

```bash
# Start the development server
npm run dev
```

This will start both the Vite dev server and Electron in development mode.

## Building

```bash
# Build for production
npm run build

# Package for your platform
npm run package

# Or platform-specific
npm run package:mac
npm run package:win
npm run package:linux
```

## Project Structure

```
application/
├── src/              # React frontend components
├── electron/         # Electron main & preload scripts
├── dist/             # Build output
├── release/          # Packaged applications
└── build/            # App icons and assets
```

Backend located at: `../backend/`

## Environment Setup

Create `backend/.env`:
```env
# Database (Supabase)
DB_HOST=your_supabase_host.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_password

# AI Services
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_gemini_key

# Smart Bulb (Optional)
TUYA_CLIENT_ID=...
TUYA_CLIENT_SECRET=...
TUYA_DEVICE_ID=...
TUYA_REGION=us

# Observability (Optional)
OPIK_API_KEY=your_opik_key
```

> **Complete setup guide:** [docs/environment-setup.md](../docs/environment-setup.md)

## Troubleshooting

### No audio input detected

```bash
# Check audio devices
python -c "import sounddevice; print(sounddevice.query_devices())"
```

Ensure your USB audio interface or built-in mic is connected and recognized.

### Backend connection failed

Verify the FastAPI backend is running:
```bash
curl http://127.0.0.1:8000/health
```

If not running, start it manually from `backend/` directory.

### Smart bulb not responding

- Verify Tuya credentials in `backend/.env`
- Check bulb is online in Tuya Smart app
- Ambient lighting is optional — practice works without it

## Documentation

For detailed usage and architecture:
- [Desktop App Guide](../docs/desktop-app.md)
- [System Architecture](../docs/architecture.md#component-1-desktop-application)
- [AI Coaching System](../docs/ai-coaching.md)
- [Audio Processing Mathematics](../docs/appendix-audio-math.md)
