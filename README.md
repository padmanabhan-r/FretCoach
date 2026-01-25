# FretCoach - AI-Powered Guitar Training

> **Turn your 2026 guitar resolutions into reality.**

![FretCoach](images/FretCoach.jpeg)

**Real-time AI coaching for guitar practice**

---

## Overview

FretCoach is a real-time AI guitar practice system that reshapes motor learning before conscious correction is required. It listens to every note you play and provides **instant feedback** — closing the loop from days to milliseconds — helping you build correct technique before bad habits form.

> 🧠 **Neuroscience insight:** It's 10–20× harder to unlearn a motor habit than to prevent it. Early-stage neuroplasticity is fast and fragile — FretCoach operates inside this critical window. 

**FretCoach doesn't correct — it prevents.**

## Philosophy: Prevention Over Correction

### Why Prevention Matters

Traditional guitar feedback arrives **days or weeks late**:
- Weekly lessons with an instructor
- Reviewing your own recordings after practice
- Posting videos online for feedback


### The FretCoach Approach

**Close the feedback loop from days to milliseconds:**

1. **Fast Loop (<300ms):** Real-time audio analysis provides instant metrics
2. **Slow Loop (1-2s):** AI coach offers strategic guidance
3. **Multi-channel feedback:** Visual + ambient + vocal reinforcement
4. **Gamification:** Scores, color feedback, and progress tracking

Every note you play receives immediate evaluation. Correct patterns are reinforced. Incorrect patterns are flagged **before they become habits**.

**Result:** Neuroadaptive learning that shapes motor behavior in real-time, not retroactively.

### Key Features

- **Real-time audio analysis** — Continuous evaluation during playing
- **Multi-channel feedback** — Visual metrics, AI vocal feedback, and environmental feedback through ambient lighting
- **Intelligent practice** — AI-generated practice plans based on your history
- **Instant feedback loop** — Millisecond-level feedback that prevents mistakes before they become habits
- **Cross-device sync** — Practice anywhere, track everything in one place

---

## Platform Ecosystem

FretCoach operates across three interconnected components sharing a central database.

![FretCoach Trifecta](images/FretCoach%20Trifecta.jpeg)

- **FretCoach Studio** — Desktop app for real-time practice with AI coaching and ambient feedback
- **FretCoach Portable** — Raspberry Pi powered portable device for practising on-the-go
- **FretCoach Hub** — Web analytics, progress tracking, and AI practice planning

---
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
- **AI Voice Coach** — Spoken guidance via GPT-4o-mini and GPT-4o-mini-TTS models
- **Ambient lighting** — Smart bulb feedback (green = good, red = needs work)

## Audio Analysis Agent Features

Powered by **librosa**, **NumPy**, and **SciPy**:

### Real-Time Pitch Detection
- **Algorithm:** librosa piptrack() (autocorrelation-based)
- **Frequency:** Every 300ms
- **Processing:** Hz → MIDI note → Pitch class (0-11)
- **Purpose:** Instant note accuracy and intonation tracking

### Scale Validation Engine
- **Library:** 24 scales (12 Major + 12 Minor, Natural + Pentatonic)
- **Method:** Pitch class validation against target scale
- **Tracking:** Note histogram, scale coverage, conformity percentage
- **Purpose:** Ensure practice stays within chosen scale

### Quality Scoring System
- **Formula:** quality = 0.55 × pitch + 0.15 × scale + 0.15 × timing + 0.15 × noise
- **Smoothing:** Exponential Moving Average (EMA) with α = 0.10–0.40
- **Window:** 0.8 seconds phrase grouping
- **Purpose:** Aggregate real-time performance score

### Feedback Mechanisms
- **Visual:** WebSocket broadcast to React UI (6.67 Hz updates)
- **Ambient:** Smart bulb HSV color control (Green → Yellow → Orange → Red)
- **Database:** Session logging to PostgreSQL/Supabase
- **Purpose:** Multi-channel real-time feedback

**Processing:** All audio analysis runs **locally** with no cloud dependency.

## AI Coaching Features

Powered by **LangChain**, **OpenAI**, and **Google Gemini**:

### Live Coaching (During Session)
- **Model:** GPT-4o-mini + GPT-4o-mini-TTS
- **Frequency:** Every 30 seconds
- **Output:** 1-sentence corrective feedback + spoken audio
- **Purpose:** Real-time guidance on weakest metric

### AI Practice Mode (Pre-Session)
- **Model:** Gemini 2.5 Flash
- **Input:** Recent session history from database
- **Output:** Personalized practice plan (scale, strictness, focus area)
- **Purpose:** Targeted practice based on weaknesses

### Web AI Coach (Post-Session)
- **Model:** Gemini 2.5 Flash + LangGraph
- **Interface:** Conversational chat with text-to-SQL capabilities
- **Tools:** Database queries, trend analysis, plan generation
- **Purpose:** Performance review and long-term strategy

**Observability:** All LLM calls traced via **Comet Opik** with token counting and latency tracking

Audio analysis runs **locally**. AI features use cloud APIs.

---

## System Architecture

### High-Level Architecture

```
                    ┌─────────────────────────────────────────────┐
                    │   CENTRAL DATABASE (PostgreSQL/Supabase)    │
                    │                                             │
                    │  • Practice Sessions & Metrics              │
                    │  • AI-Generated Practice Plans              │
                    │  • Cross-Device Synchronization             │
                    └──────┬──────────────┬──────────────┬────────┘
                           │              │              │
         ┌─────────────────┴──────┐       │       ┌──────┴─────────────────┐
         │                        │       │       │                        │
         ▼                        ▼       ▼       ▼                        ▼
┌─────────────────────┐  ┌─────────────────────────────┐  ┌─────────────────────┐
│  FRETCOACH STUDIO   │  │     FRETCOACH HUB (Web)     │  │ FRETCOACH PORTABLE  │
│    (Desktop App)    │  │                             │  │   (Raspberry Pi)    │
├─────────────────────┤  ├─────────────────────────────┤  ├─────────────────────┤
│                     │  │                             │  │                     │
│ Stack:              │  │ Frontend:                   │  │ Hardware:           │
│ • Electron          │  │ • React    + TypeScript     │  │ • Raspberry Pi 5    │
│ • React             │  │ • Vite + Tailwind CSS       │  │ • Scarlett Solo USB │
│ • Python FastAPI    │  │ • shadcn/ui + Recharts      │  │                     │
│ • librosa + NumPy   │  │                             │  │ Stack:              │
│                     │  │ Backend:                    │  │ • Python FastAPI    │
│ Features:           │  │ • Python FastAPI            │  │ • librosa + NumPy   │
│ • Live Audio        │  │ • LangGraph + LangChain     │  │ • Same Engine       │
│   Analysis          │  │ • Gemini 2.5 Flash          │  │                     │
│ • Real-time         │  │                             │  │ Features:           │
│   Metrics           │  │ Features:                   │  │ • Portable Practice │
│ • AI Voice Coach    │  │ • AI Chat Coach             │  │ • Edge Processing   │
│ • Practice Plans    │  │ • Session Analytics         │  │ • Offline Capable   │
│ • Smart Lighting    │  │ • Performance Trends        │  │ • Smart Lighting    │
│                     │  │ • Practice Plan Generator   │  │ • Database Sync     │
└──────────┬──────────┘  └─────────────────────────────┘  └──────────┬──────────┘
           │                                                          │
           ▼                                                          ▼
   ┌───────────────┐                                          ┌──────────────┐
   │ Scarlett Solo │                                          │ Integrated   │
   │  USB Audio    │                                          │ Audio Input  │
   └───────┬───────┘                                          └──────┬───────┘
           │                                                         │
           ▼                                                         ▼
         🎸 Guitar                                                 🎸 Guitar


                        ┌───────────────────────────────┐
                        │   AMBIENT FEEDBACK (Optional) │
                        │                               │
                        │  💡 Smart Bulb (Tuya WiFi)    │
                        │                               │
                        │  🟢 Green  → Excellent (70%+) │
                        │  🟡 Yellow → Good (50-70%)    │
                        │  🟠 Orange → Average (30-50%) │
                        │  🔴 Red    → Needs Work (<30%)│
                        └───────────────────────────────┘
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
**Prerequisites:**
- Node.js 18+
- Python 3.12+
- Audio interface (Focusrite Scarlett Solo recommended) or built-in mic

**Installation:**
```bash
cd application
npm install
npm run dev  # Starts Electron + React frontend + Python FastAPI backend
```
> **Environment setup:** See [docs/environment-setup.md](docs/environment-setup.md)

---

## 2. FretCoach Portable (Raspberry Pi Device)

**Location:** `/portable/`

Raspberry Pi 5-based portable practice device. Same analysis engine as Studio.

**Status:** Prototyping phase - but showing the possibility here!

### Features
- Real-time edge processing
- Ambient lighting feedback
- Manual and AI practice modes
- Database sync

**Hardware:**
- Raspberry Pi 5 (8GB RAM)
- Focusrite Scarlett Solo USB
- microSD 64GB+

**Current Progress:**
- ✅ Hardware setup complete
- ✅ Audio I/O testing successful
- ✅ Software integration in progress
- ✅ Database sync mechanism
- 📋 Planned: Physical enclosure design using 3D printers, footswitch control, LCD touchscreen 

---

## 3. FretCoach Hub (Web Platform)

**Website:** [fretcoach.online](https://www.fretcoach.online)
**Anlytics and AI Coach Dashboard:** [fretcoach.online/dashboard](https://www.fretcoach.online/dashboard)

Web platform for analytics and practice planning.

### Features
- AI chat coach (text-to-SQL agent + Gemini 2.5 Flash)
- Performance analytics and trend charts
- AI-generated practice plans
- Session history and statistics

### Getting Started

**Local Development:**

**Backend:**
```bash
cd web/web-backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
cd web/web-frontend
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

## Technology Stack

### Desktop Application
| Layer | Technology |
|-------|------------|
| Desktop Runtime | Electron 28 |
| Frontend | React 18, Vite, Tailwind CSS |
| Backend | Python 3.12+, FastAPI 0.109+ |
| Audio Processing | librosa, NumPy, SciPy, sounddevice |
| Communication | REST API, WebSocket |

### Web Platform
| Layer | Technology |
|-------|------------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| UI Components | shadcn/ui, Radix UI, Recharts |
| State Management | TanStack React Query, React Router v6 |
| Backend | Python FastAPI, LangChain, LangGraph |
| Deployment | Vercel (frontend), Render/Railway (backend) |

### Shared Infrastructure
| Component | Technology |
|-----------|------------|
| Database | PostgreSQL (Supabase) |
| LLM Providers | OpenAI (GPT-4o-mini, TTS), Google Gemini 2.5 Flash |
| AI Orchestration | LangChain, LangGraph |
| Observability | Comet Opik |
| Smart Bulb | Tuya Cloud API (tinytuya 1.17.4) |

---

## Database Schema

FretCoach uses PostgreSQL hosted on Supabase with two core tables:

| Table | Purpose |
|-------|---------|
| `sessions` | Practice session data: metrics, scale config, note statistics, timestamps |
| `ai_practice_plans` | AI-generated recommendations linked to sessions |

---
## Feature Matrix

| Feature | Studio | Hub | Portable |
|---------|:------:|:---:|:--------:|
| Real-time Audio Analysis | ✅ | — | ✅ |
| 4 Metric Evaluation | ✅ | — | ✅ |
| Live Visual Feedback | ✅ | — | 🚧 |
| Smart Bulb Integration | ✅ | — | ✅ |
| AI Voice Coaching | ✅ | — | 📋 |
| AI Practice Plans | ✅ | ✅ | 📋 |
| Session Logging | ✅ | View | ✅ |
| Performance Analytics | — | ✅ | — |
| AI Chat Coach | — | ✅ | — |
| Trend Visualization | — | ✅ | — |
| Cross-Device Sync | ✅ | ✅ | ✅ |
| Offline Capable | ✅ | — | ✅ |

**Legend:** ✅ Complete | 🚧 In Progress | 📋 Planned

---

## Documentation

- [Architecture Overview](docs/architecture.md) — Comprehensive technical documentation
- [Environment Setup](docs/environment-setup.md) — Configuration guide
- [Desktop Application](docs/desktop-app.md) — Studio setup and usage
- [Audio Engine](docs/audio-engine.md) — Signal processing details
- [Opik Integration](opik/README.md) — Use of Opik

---

## Contributing

FretCoach is under active development. Contributions, bug reports, and feature requests are welcome.

**Built with:** Electron, React, Python, FastAPI, LangChain, OpenAI, Google Gemini, PostgreSQL, Supabase

---

**FretCoach** — *Preventive AI for guitar mastery*
