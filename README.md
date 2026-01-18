# FretCoach - An Adaptive Guitar Learning Agent

![FretCoach](images/FretCoach.jpeg)

> *"FretCoach is like an AI guitar pedal that trains your brain, not your tone."*

## Overview

FretCoach is an edge-first AI learning agent designed to function like an intelligent guitar pedal for beginners, helping players fine-tune their playing through real-time evaluation and adaptive visual feedback. Instead of effects like distortion or delay, FretCoach provides **learning effects**.

## How It Works

FretCoach listens to live guitar input and evaluates:
- **Pitch accuracy** - How cleanly notes are being fretted
- **Scale conformity** - Whether notes match the chosen scale pattern
- **Timing stability** - Consistency of note spacing and rhythm
- **Noise control** - Detection of unwanted sound artifacts

It translates performance quality into immediate visual lighting cues. These cues act as a subconscious training signal, allowing the brain to adapt and self-correct while playing.

## Intelligent Coaching

Beyond real-time feedback, FretCoach operates as an autonomous coach. The system:
- Aggregates performance metrics over time
- Identifies dominant learning bottlenecks
- Uses a large language model to synthesize structured metrics
- Diagnoses learning issues and adapts future training strategies
- Provides live coaching feedback during practice sessions

All real-time audio analysis and feedback remain **deterministic** and run locally.

---

## The FretCoach Ecosystem

FretCoach consists of **four interconnected components**, all powered by AI and connected to a central database:

```
                    ┌─────────────────────────────┐
                    │   🌐 Web Dashboard          │
                    │   AI Practice Coach         │
                    │   Analytics & Insights      │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │  ☁️  Supabase Database      │
                    │     Performance Data        │
                    │     Practice Plans          │
                    └──────────┬──────────┬───────┘
                               │          │
                ┏━━━━━━━━━━━━━━┷━━━━┓   ┏┷━━━━━━━━━━━━━━━━┓
                ┃                   ┃   ┃                  ┃
    ┌───────────▼──────────┐        ┃   ┃        ┌─────────▼─────────┐
    │ 💻 Desktop App       │        ┃   ┃        │ 🎛️  Portable Pedal │
    │ ──────────────────   │◄──────►┃💡 ┃◄──────►│ ─────────────────  │
    │ • Electron + React   │        ┃   ┃        │ • Raspberry Pi     │
    │ • Real-time Analysis │        ┗━━━┛        │ • Edge Processing  │
    │ • AI Coach Mode      │     Ambient         │ • Standalone Mode  │
    │ • Live Feedback      │     Lighting        │ • Stage Ready      │
    └──────────▲───────────┘                     └─────────▲──────────┘
               │                                           │
      ┌────────┴─────────┐                       ┌────────┴─────────┐
      │  🎸 ➜ USB Audio  │                       │  🎸 ➜ Direct In  │
      │     Interface    │                       │                  │
      └──────────────────┘                       └──────────────────┘
```

---

## 1. Desktop Application

**Location:** `/application/`

The primary training environment running as an Electron application with React frontend.

### Features
- **Real-time audio analysis** via USB audio interface (e.g., Focusrite Scarlett)
- **Live visual feedback** with performance scoring (Excellent, Good, Average, Needs Work)
- **AI Coach Mode** - Generates personalized practice recommendations using LLM
- **Live AI Coaching** - Real-time motivational feedback during sessions
- **Ambient lighting control** - Syncs smart bulbs to performance quality
- **Manual & AI Practice Modes** - Choose your own scale or let AI recommend
- **Session logging** - All practice sessions saved to database
- **Session summary** - Detailed metrics at the end of each session

### Tech Stack
- Electron 28.0.0
- React 18.2.0
- Vite (bundler)
- Tailwind CSS
- FastAPI Python backend (audio processing)

### Getting Started
```bash
cd application
npm install
npm run dev  # Starts Vite + Electron in development mode
```

### Backend
```bash
cd backend
source .venv/bin/activate
uvicorn backend.api.server:app --reload --host 127.0.0.1 --port 8000
```

---

## 2. Portable Pedal (Raspberry Pi)

**Location:** `/portable/`

A standalone physical device designed as an intelligent guitar pedal for on-the-go practice.

### Features
- Raspberry Pi-based controller with integrated ADC
- Real-time audio processing at the edge
- Ambient lighting feedback via smart bulbs
- Database connectivity for session sync
- Battery-powered portable operation
- Stage-ready design

### Status
Framework ready for development. Hardware specifications and schematics in progress.

---

## 3. Web Dashboard

**Location:** `/web/`

Cloud-based analytics platform with AI Practice Coach.

### Features
- **AI Practice Coach** - Chat-based coach that analyzes your practice data
- **Performance visualizations** - Trend charts, comparison radar charts
- **Practice plan generation** - AI-generated recommendations saved to database
- **Session history** - Browse all past practice sessions
- **Date range filtering** - Analyze specific time periods
- **Aggregate statistics** - Total practice time, notes played, average scores

### Tech Stack
- React 18.3.1 + TypeScript
- Vite (bundler)
- Tailwind CSS + shadcn/ui components
- Recharts (data visualization)
- React Query
- Supabase integration
- LangChain with Gemini/Claude for AI Coach

### Getting Started
```bash
cd web
npm install
npm run dev  # Frontend on http://localhost:5173
```

### Web Backend
```bash
cd web/server
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 4. Ambient Lighting Control

Integrated across both Desktop and Portable components.

### Features
- **Smart bulb integration** via Tuya API
- **Real-time color feedback** based on performance:
  - 🟢 Green - Excellent (70%+)
  - 🟡 Yellow-Green - Good (50-70%)
  - 🟠 Yellow - Average (30-50%)
  - 🔴 Red - Needs Work (<30%)
- **Configurable per session** - Enable/disable via UI

### Configuration
Add your Tuya smart bulb credentials to `backend/.env`:
```env
TUYA_CLIENT_ID=your_client_id
TUYA_CLIENT_SECRET=your_secret
TUYA_DEVICE_ID=your_bulb_device_id
TUYA_REGION=us  # or eu, cn, in
```

---

## Database Schema

FretCoach uses PostgreSQL (Supabase) with the following tables:

### `sessions`
Stores all practice session data:
- Session metrics (pitch_accuracy, scale_conformity, timing_stability)
- Scale configuration (scale_chosen, scale_type)
- Note statistics (total_notes, correct_notes, wrong_notes)
- Duration and timestamps

### `ai_practice_plans`
AI-generated practice recommendations:
- JSON practice plan with exercises
- Focus area and reasoning
- Link to executed session (if practiced)

---

## Environment Setup

### Required Environment Variables
Create `backend/.env` with:
```env
# Database
DB_HOST=your_supabase_host
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

---

## Project Structure

```
FretCoach/
├── application/           # Desktop App (Electron + React)
│   ├── electron/         # Main process
│   ├── src/              # React components
│   └── build/            # App icons
├── web/                   # Web Dashboard
│   ├── src/              # React frontend
│   ├── server/           # FastAPI backend
│   └── public/           # Static assets
├── backend/               # Shared Python Backend
│   ├── api/              # FastAPI routes & services
│   ├── core/             # Audio processing & session logging
│   └── sql/              # Database schemas
├── portable/              # Raspberry Pi Pedal (framework)
├── images/                # Project assets
└── README.md
```

---

## Key Features Summary

| Feature | Desktop | Web | Portable |
|---------|---------|-----|----------|
| Real-time Analysis | Yes | - | Yes |
| AI Practice Coach | Yes | Yes | - |
| Live AI Feedback | Yes | - | Yes |
| Session Logging | Yes | View | Yes |
| Ambient Lighting | Yes | - | Yes |
| Practice Plans | Yes | Generate | Yes |
| Performance Charts | - | Yes | - |

---

## Philosophy

FretCoach transforms unstructured practice into a guided learning loop, acting as a physical, intelligent pedal that trains the player — not the sound. The architecture is designed to generalize to other instruments and vocal training that benefit from adaptive, embodied feedback.

---

## Contributing

Contributions welcome! Please open an issue or submit a PR.

## License

MIT License
