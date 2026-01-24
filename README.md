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

FretCoach operates across three interconnected components sharing a central database.

![FretCoach Trifecta](images/FretCoach%20Trifecta.jpeg)

- **FretCoach Studio** — Desktop app for real-time practice with AI coaching and ambient feedback
- **FretCoach Portable** — Raspberry Pi device for portable practice
- **FretCoach Hub** — Web analytics, progress tracking, and AI practice planning

## How It Works

### Preventive Neurofeedback Systems

FretCoach is a **Preventive Neurofeedback System** — it shapes motor behavior in real time before maladaptive patterns form. Instead of corrective feedback after mistakes solidify, FretCoach intervenes **during skill execution** inside the brain's plasticity window.

> **Prevention is neuroadaptive. Correction is retrofitting.**

Architecture: **dual-brain system** combining fast deterministic processing with intelligent AI coaching.

![FretCoach Brain Architecture](images/FretCoach%20Brain.png)

### The Two Systems

**Audio Analysis Agent (Fast Loop)**
- Real-time processing (<300ms latency)
- Preventive intervention during execution
- Continuous pitch, scale, timing, noise evaluation
- Local processing, no cloud dependency

**AI Coach (Slow Loop)**
- LLM-powered preventive coaching
- Pattern analysis and personalized practice plans
- On-demand (not real-time critical)

Hybrid architecture: local speed + AI intelligence = intervention before habits solidify.

### Performance Metrics

FretCoach's audio analysis engine evaluates your playing across four metrics:

| Metric | What It Measures |
|--------|------------------|
| **Pitch Accuracy** | Note accuracy against the target scale |
| **Scale Conformity** | Scale coverage and adherence |
| **Timing Stability** | Rhythmic consistency |
| **Noise Control** | String noise and unwanted artifacts |

Three feedback channels:
- **On-screen metrics** — Live scores and note detection
- **AI coach** — Real-time verbal guidance
- **Ambient lighting** — Smart bulb feedback (green = good, red = needs work)

## AI Coaching

Powered by LLMs (Gemini 2.5 Flash, OpenAI GPT-4o, GPT-4o-mini-TTS):
- **AI Practice Mode** — Personalized plans from practice history
- **Live Vocal Feedback** — Real-time spoken coaching (GPT-4o-mini-TTS)
- **Progress Tracking** — Performance trends and pattern recognition
- **Adaptive Plans** — Evolving recommendations

Audio analysis runs **locally**. AI features use cloud APIs.

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

Desktop application for focused practice sessions.

### Features
- Real-time audio analysis (USB interface or built-in mic)
- Live visual metrics and performance scoring
- Manual Mode (choose scale/settings) or AI Mode (recommended plans)
- Live vocal AI coaching during sessions
- Ambient lighting integration
- Automatic session logging and summaries

### Getting Started
```bash
cd application
npm install
npm run dev  # Starts frontend + backend
```

> **Environment setup:** See [docs/environment-setup.md](docs/environment-setup.md)

---

## 2. FretCoach Portable (Raspberry Pi Device)

**Location:** `/portable/`

Raspberry Pi 5-based portable practice device. Same analysis engine as Studio.

**Status:** Prototyping phase — hardware complete, software in progress

### Features
- Real-time edge processing
- Ambient lighting feedback
- Manual and AI practice modes
- Database sync

### Current Progress
Hardware operational. Software integration ongoing.

---

## 3. FretCoach Hub (Web Platform)

**Access:** [fretcoach.online](https://fretcoach.online) | **Location:** `/web/`

Web platform for analytics and practice planning.

### Features
- AI chat coach (text-to-SQL agent + Gemini 2.5 Flash)
- Performance analytics and trend charts
- AI-generated practice plans
- Session history and statistics

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

> **Environment setup:** See [docs/environment-setup.md](docs/environment-setup.md)

---

## 4. Ambient Lighting

Smart bulb integration for visual performance feedback.

### Color Coding
- 🟢 Green — Excellent (70%+)
- 🟡 Yellow-Green — Good (50-70%)
- 🟠 Yellow — Average (30-50%)
- 🔴 Red — Needs Work (<30%)

> **Configuration:** See [docs/environment-setup.md](docs/environment-setup.md#smart-bulb-setup-tuya)

---

## Database Schema

FretCoach uses PostgreSQL hosted on Supabase with two core tables:

| Table | Purpose |
|-------|---------|
| `sessions` | Practice session data: metrics, scale config, note statistics, timestamps |
| `ai_practice_plans` | AI-generated recommendations linked to sessions |

---

## Environment Setup

See complete setup guide: [docs/environment-setup.md](docs/environment-setup.md)

**Quick reference:** Configure database (Supabase), AI keys (OpenAI, Gemini), smart bulb (Tuya), and observability (Opik).

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

FretCoach operates inside the motor learning window — providing instant guidance during skill execution before mistakes encode.

**Why:**
- Traditional feedback arrives days/weeks late (lessons, recordings)
- Motor patterns solidify before mistakes are identified
- 10–20× harder to unlearn than prevent (neural research)
- FretCoach closes the loop from days to **milliseconds**

Real-time scores, ambient lighting, and AI coaching create an engaging neuroadaptive experience. Every note reinforces correct patterns before incorrect ones form.

Built for guitar. Designed to extend to other instruments and motor skills.

---

