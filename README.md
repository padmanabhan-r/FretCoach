# FretCoach - AI-Powered Physical Skill Training

![FretCoach](images/FretCoach.jpeg)

> *"Close the feedback loop. Prevent mistakes before they stick."*

## The Core Theory

Learning any physical skill—guitar, tennis, golf—suffers from the same problem: **delayed feedback**. Without a coach watching, practitioners can't see their own mistakes in real time. They rush, hold wrong form, or reinforce bad habits. By the time feedback arrives, the moment has passed. The brain has already encoded the error.

FretCoach closes this loop from seconds/minutes to **milliseconds**. Instant feedback enables **prevention instead of correction**—self-correction while the movement is fresh, before the brain commits the mistake.

## What FretCoach Provides

- **Instant feedback** — Analysis in real time across performance dimensions
- **Multi-channel delivery** — Visual, audio (AI coaching), and ambient lighting cues
- **Gamified practice** — Scoring, metrics, and progress tracking that make routine engaging
- **Cross-device sync** — Practice anywhere, track everything, see it all in one place

FretCoach is the first implementation of this theory for guitar. The architecture is designed for generalization to other instruments, sports, and physical training.

## Platform Ecosystem

- **FretCoach Studio** — Desktop application for focused practice with real-time analysis, AI coaching, and ambient feedback
- **FretCoach Portable** — Raspberry Pi device for practice anywhere
- **FretCoach Hub** — Web platform for analytics, progress tracking, and AI-generated practice recommendations

## Real-Time Audio Analysis Agent Engine

FretCoach's audio analysis agent processes live guitar input and evaluates four key performance metrics:

| Metric | What It Measures |
|--------|------------------|
| **Pitch Accuracy** | Correctness of fretted notes against the target scale |
| **Scale Conformity** | Coverage and adherence to the chosen scale |
| **Timing Stability** | Consistency of note spacing and rhythmic precision |
| **Noise Control** | Clarity of playing and detection of unwanted artifacts |

These metrics power a multi-channel feedback system:
- **On-screen visualizations** — Live metrics display, performance scoring, and note detection
- **AI coach commentary** — Real-time verbal guidance during practice, like a coach standing courtside
- **Ambient lighting** — Smart bulb color shifts from red to green based on performance quality

## Intelligent Coaching

FretCoach operates as an autonomous practice coach powered by LLM (Gemini 2.5 Flash, OpenAI GPT 4o Mini, Minimax 2.1 and Deepseek Chat 3.1):
- **AI Practice Mode** — Analyzes your history and curates personalized practice routines through conversation
- **Live Session Feedback** — Provides real-time coaching insights based on your performance metrics
- **Progress Tracking** — Aggregates data across sessions to identify patterns and bottlenecks
- **Adaptive Recommendations** — Generates practice plans that evolve with your skill level

All real-time audio analysis runs **locally and deterministically**. AI coaching features connect to cloud services for enhanced insights and cross-device synchronization.

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

The primary training environment—a standalone desktop application for focused practice sessions. Currently implements guitar training; architecture designed for extensibility.

### Features
- **Real-time Audio Analysis** — USB audio interface (e.g., Focusrite Scarlett) or built-in microphone
- **Live Visual Feedback** — On-screen metrics with performance scoring (Excellent, Good, Average, Needs Work)
- **Dual Practice Modes:**
  - *Manual Mode* — Select your own scale, sensitivity, and strictness settings
  - *AI Mode* — Let the AI coach recommend what to practice based on your history
- **Live AI Coaching** — Real-time verbal feedback during sessions, analyzing your metrics and guiding improvement
- **Ambient Lighting Control** — Syncs smart bulbs to performance quality for subconscious feedback
- **Session Logging** — All sessions automatically saved to the central database
- **Session Summary** — Detailed metrics breakdown at the end of each session

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

A standalone physical device—pedal-style—for practice anywhere. Same analysis engine as FretCoach Studio, running at the edge.

**Status:** Prototyping phase — demonstrating edge computing capabilities.

### Concept
- Raspberry Pi 5-based controller
- Real-time audio processing at the edge (same analysis agent engine as desktop)
- Ambient lighting feedback via smart bulbs
- Syncs with central database for seamless experience across devices
- Battery-powered for true portability
- Supports both Manual and AI practice modes

### Current Progress
Hardware setup complete with Raspberry Pi 5 and integrated audio I/O. Audio analysis agent engine adaptation in progress.

---

## 3. FretCoach Hub (Web Platform)

**Location:** `/web/`

Cloud-based analytics platform for reviewing progress and planning practice sessions—accessible from any device. Skill-agnostic design for tracking across multiple physical activities.

### Features
- **AI Practice Coach** — Chat interface to discuss performance and get recommendations
- **Performance Analytics** — Trend charts and session comparisons
- **Practice Plan Generation** — AI-generated plans saved to database and synced to devices
- **Session History** — Browse and filter past practice sessions
- **Aggregate Statistics** — Total practice time, notes played, average scores

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

Integrated across FretCoach Studio and FretCoach Portable for subconscious feedback—visual cues that reinforce performance quality without breaking focus.

### How It Works
- **Smart bulb integration** via Tuya API
- **Real-time color mapping** based on performance score:
  - 🟢 Green — Excellent (70%+)
  - 🟡 Yellow-Green — Good (50-70%)
  - 🟠 Yellow — Average (30-50%)
  - 🔴 Red — Needs Work (<30%)
- **Toggle per session** — Enable or disable via the UI

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

FretCoach applies a simple theory: **prevention instead of correction**. By closing the feedback loop to milliseconds, practitioners self-correct instinctively—before the brain encodes the mistake. The architecture is designed to generalize from guitar to any physical skill that benefits from instant, embodied feedback.

---

