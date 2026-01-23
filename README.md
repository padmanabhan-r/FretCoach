# FretCoach - AI-Powered Guitar Training

![FretCoach](images/FretCoach.jpeg)

> *Real-time AI coaching for guitar practice*

## What It Does

FretCoach analyzes your guitar playing in real-time and provides instant feedback to help you practice effectively. It acts as an always-available practice coach that listens to every note you play, tracks your progress, and guides improvement across four key metrics: **pitch accuracy**, **scale conformity**, **timing stability**, and **noise control**.

### Key Features

- **Real-time audio analysis** — Continuous evaluation of your playing
- **Multi-channel feedback** — Visual metrics, AI coaching, and ambient lighting
- **Intelligent practice** — AI-generated practice plans based on your history
- **Cross-device sync** — Practice anywhere, track everything in one place

## Platform Ecosystem

- **FretCoach Studio** — Desktop application for focused practice with real-time analysis, AI coaching, and ambient feedback
- **FretCoach Portable** — Raspberry Pi device for practice anywhere
- **FretCoach Hub** — Web platform for analytics, progress tracking, and AI-generated practice recommendations

## How It Works

![Screenshot Placeholder: Real-time analysis in action]
*[TODO: Add screenshot showing live metrics and note detection]*

FretCoach's audio analysis engine evaluates your playing across four metrics:

| Metric | What It Measures |
|--------|------------------|
| **Pitch Accuracy** | Note accuracy against the target scale |
| **Scale Conformity** | Scale coverage and adherence |
| **Timing Stability** | Rhythmic consistency |
| **Noise Control** | String noise and unwanted artifacts |

You get feedback through three channels:
- **On-screen metrics** — Live performance scores and note detection
- **AI coach** — Real-time verbal guidance during practice
- **Smart lighting** — Color-coded ambient feedback (green = good, red = needs work)

## AI Coaching

Powered by LLMs (Gemini 2.5 Flash, OpenAI GPT 4o Mini, Minimax 2.1, Deepseek Chat 3.1):
- **AI Practice Mode** — Get personalized practice plans based on your history
- **Live Feedback** — Real-time coaching during practice sessions
- **Progress Tracking** — Performance trends and pattern recognition
- **Adaptive Plans** — Practice recommendations that evolve with you

Audio analysis runs **locally**. AI features use cloud APIs for coaching and sync.

---

## System Architecture

FretCoach consists of three interconnected components connected to a central database:

```
                        ┌───────────────────────────────────┐
                        │      PostgreSQL (Supabase)        │
                        │  Sessions • Plans • Performance   │
                        └───────────────┬───────────────────┘
                                        │
                 ┌──────────────────────┼──────────────────────┐
                 │                      │                      │
                 ▼                      ▼                      ▼
┌────────────────────────┐  ┌─────────────────────┐  ┌────────────────────────┐
│   FretCoach Studio     │  │   FretCoach Hub     │  │  FretCoach Portable    │
│  ────────────────────  │  │  ─────────────────  │  │  ────────────────────  │
│  Electron + React      │  │  React + FastAPI    │  │  Raspberry Pi 5        │
│  Python FastAPI        │  │                     │  │  Python FastAPI        │
│                        │  │  • AI Coach Chat    │  │  Integrated Audio I/O  │
│  • Audio Analysis      │  │  • Session History  │  │                        │
│  • Live AI Coaching    │  │  • Analytics        │  │  • Audio Analysis      │
│  • On-screen Metrics   │  │  • Practice Plans   │  │  • AI Assisted Mode    │
│  • Ambient Lighting    │  │                     │  │  • Ambient Lighting    │
└───────────┬────────────┘  └─────────────────────┘  └───────────┬────────────┘
            │                                                    │
            ▼                                                    │
   ┌─────────────────┐                                           │
   │   USB Audio     │                                           │
   │   Interface     │                                           │
   └────────┬────────┘                                           │
            │                                                    │
           🎸                                                   🎸
        Guitar                                               Guitar


                    ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐
                      💡 Smart Bulb (Tuya API)
                    │   Controlled by Desktop &     │
                        Portable for ambient feedback
                    └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘
```

---

## 1. FretCoach Studio (Desktop Application)

**Location:** `/application/`

![Screenshot Placeholder: FretCoach Studio Interface]
*[TODO: Add screenshot of desktop app showing live session]*

Desktop application for focused practice sessions.

### Features
- **Real-time Audio Analysis** — Works with USB audio interface or built-in mic
- **Live Visual Feedback** — On-screen metrics with performance scoring
- **Dual Practice Modes:**
  - *Manual Mode* — Choose scale, sensitivity, and strictness
  - *AI Mode* — Get AI-recommended practice plans
- **Live AI Coaching** — Real-time verbal guidance during sessions
- **Ambient Lighting** — Smart bulb integration for visual feedback
- **Session Logging** — Automatic save to database
- **Session Summary** — Detailed breakdown after each session

### Getting Started
```bash
cd application
npm install
npm run dev  # Starts both frontend and backend
```

### Backend Only
```bash
cd backend
source .venv/bin/activate
uvicorn backend.api.server:app --reload --host 127.0.0.1 --port 8000
```

---

## 2. FretCoach Portable (Raspberry Pi Device)

**Location:** `/portable/`

![Photo Placeholder: FretCoach Portable Device]
*[TODO: Add photo of Raspberry Pi setup]*

Raspberry Pi 5-based practice device for portability. Same analysis engine as Studio.

**Status:** Prototyping phase

### Features
- Real-time audio processing at the edge
- Ambient lighting feedback
- Manual and AI practice modes
- Syncs with central database
- Battery-powered (planned)

### Current Progress
Hardware setup complete. Software adaptation in progress.

---

## 3. FretCoach Hub (Web Platform)

**Location:** `/web/`

![Screenshot Placeholder: FretCoach Hub Dashboard]
*[TODO: Add screenshot of web dashboard]*

Web platform for analytics and practice planning.

### Features
- **AI Practice Coach** — Chat interface for recommendations
- **Performance Analytics** — Trend charts and session comparisons
- **Practice Plan Generation** — AI-generated plans synced to devices
- **Session History** — Browse past sessions
- **Statistics** — Total practice time, notes played, scores

### Getting Started

**Backend:**
```bash
cd web/server
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
cd web
npm install
npm run dev  # http://localhost:5173
```

**Live Demo:** [fretcoach.online](https://fretcoach.online)

---

## 4. Ambient Lighting

Smart bulb integration for visual feedback during practice.

### How It Works
- Tuya API integration
- Color-coded performance feedback:
  - 🟢 Green — Excellent (70%+)
  - 🟡 Yellow-Green — Good (50-70%)
  - 🟠 Yellow — Average (30-50%)
  - 🔴 Red — Needs Work (<30%)
- Toggle on/off per session

### Configuration
Add Tuya smart bulb credentials to `backend/.env`:
```env
TUYA_CLIENT_ID=your_client_id
TUYA_CLIENT_SECRET=your_secret
TUYA_DEVICE_ID=your_bulb_device_id
TUYA_REGION=us  # or eu, cn, in
```

---

## Database Schema

FretCoach uses PostgreSQL hosted on Supabase with two core tables:

| Table | Purpose |
|-------|---------|
| `sessions` | Practice session data: metrics, scale config, note statistics, timestamps |
| `ai_practice_plans` | AI-generated recommendations linked to sessions |

---

## Environment Setup

Create `backend/.env`:
```env
# Database (Supabase)
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
├── application/          # FretCoach Studio (Electron + React)
│   ├── electron/         # Electron main process
│   ├── src/              # React components & UI
│   └── build/            # App icons
├── backend/              # Shared Python Backend
│   ├── api/              # FastAPI routes & services
│   ├── core/             # audio analysis agent engine
│   └── sql/              # Database schemas
├── web/                  # FretCoach Hub (Web Platform)
│   ├── src/              # React frontend
│   ├── server/           # FastAPI backend
│   └── public/           # Static assets
├── portable/             # FretCoach Portable (Raspberry Pi Device)
└── images/               # Project assets
```

---

## Feature Matrix

| Feature | Studio | Hub | Portable |
|---------|:------:|:---:|:--------:|
| Real-time Audio Analysis | ✓ | — | ✓ |
| AI Practice Coach | ✓ | ✓ | ✓ |
| Live AI Feedback | ✓ | — | ✓ |
| Session Logging | ✓ | View | ✓ |
| Ambient Lighting | ✓ | — | ✓ |
| Practice Plans | ✓ | Generate | ✓ |
| Performance Charts | — | ✓ | — |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Desktop Frontend | Electron, React |
| Desktop Backend | Python, FastAPI |
| Web Frontend | React, Vite, Tailwind |
| Web Backend | FastAPI |
| Database | PostgreSQL (Supabase) |
| AI/LLM | LangChain, OpenAI, Google Gemini |
| Observability | Comet Opik |
| Smart Bulb | Tuya API |

---

## Philosophy

FretCoach provides instant feedback during practice—helping you correct mistakes in real-time before they become habits. The system is designed for guitar but built with an architecture that could extend to other instruments and motor skills in the future.

---

