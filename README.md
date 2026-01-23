# FretCoach - AI-Powered Guitar Training

> **This year 2026 turn your guitar resolutions into a reality.**

![FretCoach](images/FretCoach.jpeg)

> *Real-time AI coaching for guitar practice*

## What It Does

**FretCoach doesn't correct — it prevents.**

FretCoach is a real-time preventive AI guitar practice system that reshapes motor learning before conscious correction is required. It listens to every note you play and provides **instant feedback** — closing the loop from days to milliseconds — helping you build correct technique before bad habits form.

> 🧠 **Neuroscience insight:** It's 10–20× harder to unlearn a motor habit than to prevent it. Early-stage neuroplasticity is fast and fragile — FretCoach operates inside this critical window.

The system tracks your progress and guides improvement across four key metrics: **pitch accuracy**, **scale conformity**, **timing stability**, and **noise control**.

### Key Features

- **Real-time audio analysis** — Continuous evaluation during skill execution, not after
- **Multi-channel feedback** — Visual metrics, AI coaching, and ambient lighting for gamified practice
- **Intelligent practice** — AI-generated practice plans based on your history
- **Instant feedback loop** — Millisecond-level guidance that prevents mistakes before they become habits
- **Cross-device sync** — Practice anywhere, track everything in one place

> 🎮 **Gamification:** Turn practice into an engaging experience with real-time scores, color-coded lighting, and AI-powered progress tracking

## Platform Ecosystem

FretCoach consists of three interconnected components, all sharing a central database for seamless cross-device practice tracking.

![FretCoach Trifecta](images/FretCoach%20Trifecta.jpeg)

- **FretCoach Studio** — Desktop application for focused practice with real-time analysis, AI coaching, and ambient feedback
- **FretCoach Portable** — Raspberry Pi device for practice anywhere
- **FretCoach Hub** — Web platform for analytics, progress tracking, and AI-generated practice recommendations

## How It Works

### Preventive Neurofeedback Systems

FretCoach belongs to a new category we call **Preventive Neurofeedback Systems** — AI systems that shape neural and motor behavior in real time before maladaptive patterns form. Unlike traditional corrective AI that analyzes performance after the fact, FretCoach intervenes **during skill execution** to guide motor learning inside the brain's plasticity window.

> **Habit Formation vs Habit Repair:** Prevention is neuroadaptive. Correction is retrofitting.

FretCoach uses a **dual-brain architecture** combining fast deterministic audio processing with intelligent AI coaching.

![FretCoach Brain Architecture](images/FretCoach%20Brain.png)

### The Two Systems

**Audio Analysis Agent (Fast Loop)**
- Deterministic real-time processing (<300ms latency)
- **Preventive intervention** during skill execution
- Continuous evaluation of pitch, scale, timing, and noise
- Immediate visual feedback and ambient lighting control
- Runs locally without cloud dependencies

**AI Coach (Slow Loop)**
- LLM-powered intelligent guidance
- Analyzes performance patterns and provides **preventive** verbal coaching
- Generates personalized practice plans
- Operates on-demand (not real-time critical)

This hybrid approach delivers the speed of local processing with the intelligence of AI coaching — intervening in the motor learning window before bad habits solidify.

### Performance Metrics

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
- **Environmental feedback** — Sensory reinforcement through smart lighting that controls your practice environment (green = good, red = needs work)

## AI Coaching

Powered by LLMs (Gemini 2.5 Flash, OpenAI GPT 4o Mini, GPT-4o-mini-TTS):
- **AI Practice Mode** — Get personalized practice plans based on your history
- **Live Vocal Feedback** — Real-time spoken coaching using GPT-4o-mini-TTS during sessions
- **Progress Tracking** — Performance trends and pattern recognition
- **Adaptive Plans** — Practice recommendations that evolve with you

Audio analysis runs **locally**. AI features use cloud APIs for coaching and sync.

### Vocal Coach (TTS)
The live AI coach uses OpenAI's `gpt-4o-mini-tts` model to convert coaching text to speech with a natural, encouraging tone. Audio playback is synchronized to prevent overlapping feedback and crackling.

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

**Access Here:** [fretcoach.online](https://fretcoach.online)

**Location:** `/web/`

![Screenshot Placeholder: FretCoach Hub Dashboard]
*[TODO: Add screenshot of web dashboard]*

Web platform for analytics and practice planning.

### Features
- **AI Practice Coach** — Natural language chat interface powered by text-to-SQL agent
- **Ask Questions** — "What should I practice next?", "Show my progress trends", "Compare my latest session"
- **Performance Analytics** — Trend charts and session comparisons
- **Practice Plan Generation** — AI-generated plans synced to devices
- **Session History** — Browse past sessions
- **Statistics** — Total practice time, notes played, scores

The chat agent uses intent detection to trigger database queries and Gemini 2.5 Flash to provide conversational responses with visualizations.

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

**Website and Dashboard:** [fretcoach.online](https://fretcoach.online)

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

**Prevention, Not Correction**

FretCoach is a **Preventive Neurofeedback System** — it doesn't wait for mistakes to happen and then fix them. Instead, it operates inside the motor learning window, providing instant guidance during skill execution to shape correct technique from the start.

**Why this matters:**
- Traditional practice relies on delayed feedback (days/weeks between lessons)
- By the time mistakes are identified, motor patterns are already encoded
- Neural research shows it's 10–20× harder to unlearn a habit than to prevent it
- FretCoach closes the feedback loop from days to **milliseconds**

**Gamification meets neuroscience:**  
Real-time scores, color-coded ambient lighting, and AI coaching transform practice into an engaging, neuroadaptive experience. Every note you play is an opportunity to reinforce correct motor patterns before incorrect ones take root.

The system is designed for guitar but built with an architecture that could extend to other instruments (KeysCoach, VocalCoach, DrumCoach) and motor skills in the future.

---

