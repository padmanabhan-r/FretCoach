# FretCoach Documentation

> **Turn your 2026 guitar resolutions into reality.**

[![Website](https://img.shields.io/badge/Website-fretcoach.online-blue)](https://fretcoach.online)

![FretCoach](assets/images/FretCoach.jpeg)

**A real-time practice coach that guides you while you play**

---

## Overview

**FretCoach is a real-time AI guitar practice system** that listens as you play and delivers **instant feedback**, fixing mistakes **in the moment**—not days later.

This helps you learn correct technique **before bad habits form**.

**Most tools correct mistakes. FretCoach prevents them from happening in the first place.**

> 🧠 **Neuroscience insight:** It's 10–20× harder to unlearn a motor habit than to prevent one. Early-stage neuroplasticity is fast and fragile—and FretCoach operates inside this critical window.

---

## Philosophy: Prevention Over Correction

Traditional guitar feedback arrives **days or weeks late**:
- Weekly lessons with an instructor
- Reviewing your own recordings after practice
- Posting videos online for feedback

**FretCoach closes the feedback loop from days to milliseconds:**

![FretCoach Approach](assets/images/FretCoach%20Approach.png)

- **Local Audio Analysis Agent Engine (<300ms):** A real-time audio analysis engine (fast loop) that listens to every note and computes live performance metrics
- **AI Practice Coach:** Provides strategic guidance and practice insights based on your playing patterns (slow loop)
- **Multi-sensory feedback:** Visual on-screen cues, voice reinforcement, and ambient environmental feedback (*Yes! Your environment becomes a feedback channel*)
- **Gamification:** Scores, color signals, and progress tracking to reinforce consistency and motivation

Every note you play is evaluated immediately. Correct patterns are reinforced. Incorrect ones are flagged **before they turn into habits**.

**Result:** Neuroadaptive learning that shapes motor behavior in real time—not retroactively.

---

## Platform Ecosystem

FretCoach is built as a three-part system, with all components connected through a shared central database.

![FretCoach Trifecta](assets/images/FretCoach%20Trifecta.jpeg)

- **FretCoach Studio** — Desktop application for real-time practice, live AI coaching, and ambient lighting feedback
- **FretCoach Portable** — Raspberry Pi–powered portable unit for practicing on-the-go
- **FretCoach Hub** — Web-based dashboard for analytics, progress tracking, session review, and AI-driven practice planning

> **Like having a coach next to you, wherever you go!!**

---

## How It Works

### Preventive Neurofeedback Music Learning System

FretCoach is a **Preventive Neurofeedback System** — it shapes motor behavior in real time before maladaptive patterns form. Instead of corrective feedback after mistakes solidify, FretCoach intervenes **during skill execution**, inside the brain's plasticity window.

> **Prevention is neuroadaptive. Correction is retrofitting.**

We call this a **dual-brain architecture**, combining fast deterministic processing with intelligent AI coaching.

![FretCoach Brain Architecture](assets/images/FretCoach%20Brain.png)

---

### The Two Systems

**Audio Analysis Agent (Fast Loop) - Left Brain**
- Real-time processing (<300ms latency)
- On-device local processing, no cloud dependency
- Continuous pitch, scale, timing, noise evaluation using *Digital Signal Processing*
- Controls on-screen performance metrics and ambient lighting system

**LLM Powered AI Coach (Slow Loop) - Right Brain**
- LLM-powered preventive coaching: Provides consistent vocal and textual feedback at regular intervals during live playing for instant improvement
- Post-session pattern analysis and personalized practice plan curation based on identified weak areas
- On-demand (not real-time critical)
- Powered by LLM models: Gemini 2.5 Flash, OpenAI GPT-4o-mini, GPT-4o-mini-TTS

> **Hybrid architecture: local speed + AI intelligence = intervention before habits solidify.**

---

## Performance Metrics

FretCoach currently targets scales in music (think of them as the vegetables of the music world—you gotta eat them!).

The audio analysis engine evaluates your playing across four core metrics:

| Metric | What It Measures |
|--------|------------------|
| **Pitch Accuracy** | Note accuracy and intonation against the target scale |
| **Scale Conformity** | Scale coverage across the fretboard *(advanced metric)* |
| **Timing Stability** | Rhythmic and timing consistency |
| **Noise Control** | String noise and unwanted artifacts |

*Users can enable/disable individual metrics based on their practice focus, with preferences persisting across sessions.*

### Three Feedback Channels

- **On-screen metrics** — Live scores and note detection
- **AI Voice Coach** — Textual and spoken guidance via GPT-4o-mini and GPT-4o-mini-TTS models
- **Ambient lighting** — Smart bulb feedback (green = good, red = needs work)

---

## Audio Analysis Agent Features

Powered by Digital Signal Processing using packages - **librosa**, **NumPy**, and **SciPy**:

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
- **Dynamic Weight Distribution:**
  - When **pitch enabled**: 40-55% weight (strictness-based), remainder split among enabled metrics
  - When **pitch disabled**: equal split among enabled metrics (scale, timing, noise)
  - Noise control always included as mandatory baseline
- **Smoothing:** Exponential Moving Average (EMA) with α = 0.10–0.40
- **Window:** 0.8 seconds phrase grouping
- **Purpose:** Aggregate real-time performance score from enabled metrics

*For the nerds who want to deep dive into the math and DSP, see [Audio Processing Mathematics](appendix-audio-math.md).*

### Feedback Mechanisms
- **Visual:** WebSocket broadcast to React UI (6.67 Hz updates)
- **Ambient:** Smart bulb HSV color control (Green → Yellow → Orange → Red)
- **Database:** Session logging to PostgreSQL/Supabase
- **Purpose:** Multi-channel real-time feedback

**Processing:** All audio analysis runs **locally** with no cloud dependency.

---

## AI Coaching Features

Powered by **LangChain**, **LangGraph**, **OpenAI**, and **Google Gemini**:

### Live Coaching (During Session)
- **Model:** GPT-4o-mini + GPT-4o-mini-TTS
- **Frequency:** At fixed intervals (30 seconds, 1 min, 2 min, 5 min)
- **Output:** Short corrective feedback + spoken audio
- **Purpose:** Real-time guidance. 

### AI Practice Mode (Pre-Session)
- **Model:** Gemini 2.5 Flash
- **Input:** Recent session history from database
- **Output:** Personalized practice plan (scale, strictness, focus area)
- **Purpose:** Targeted practice based on weaknesses

### Web AI Coach (Post-Session)
- **Model:** Gemini 2.5 Flash + LangGraph
- **Interface:** Conversational agent with text-to-SQL capabilities
- **Tools:** Database queries, trend analysis, plan generation
- **Purpose:** Performance review and long-term strategy

>**Observability:** All LLM calls traced via **Comet Opik**.

Audio analysis runs **locally**. AI features use cloud APIs.

---

## Quick Navigation

### Getting Started
- **[Introduction](introduction.md)** — The problem with traditional practice and how FretCoach solves it
- **[Quickstart Guide](quickstart.md)** — Get up and running in 5 minutes

### System Components
- **[Desktop Application](desktop-app.md)** — Primary training environment with real-time analysis
- **[Portable Application](portable-app.md)** — Raspberry Pi device for practice anywhere
- **[Web Dashboard](web-dashboard.md)** — Analytics and AI coach web platform
- **[Audio Analysis Agent Engine](audio-analysis-agent-engine.md)** — Real-time audio processing (Fast Loop)
- **[AI Coach Agent Engine](ai-coach-agent-engine.md)** — Intelligent coaching system (Slow Loop)

### Technical Details
- **[System Architecture](architecture.md)** — Overall design and component interaction
- **[Environment Setup](environment-setup.md)** — Configuration guide for all platforms
- **[Audio Processing Mathematics](appendix-audio-math.md)** — Deep dive into DSP and metrics

---

## Platform Details

### 1. FretCoach Studio (Desktop Application)

Desktop application for focused practice sessions.

![Studio Mode Selection](assets/images/studio/2.%20Studio%20-%20Mode%20Selection.png)
![Studio Live Session](assets/images/studio/9.%20Studio%20-%20Live%20Session.png)

**Features:**
- Real-time audio analysis (USB interface or built-in mic)
- Live visual metrics and performance scoring
- Manual Mode (choose scale/settings) or AI Mode (recommended plans)
- Live vocal AI coaching during sessions
- Ambient lighting integration
- Automatic session logging and summaries

**Getting Started:**
- Prerequisites: Node.js 18+, Python 3.12+, Audio interface (Focusrite Scarlett Solo recommended) or built-in mic
- See [Desktop Application](desktop-app.md) for detailed setup

---

### 2. FretCoach Portable (Raspberry Pi Device)

![Portable Terminal](assets/images/portable/Fretcoach%20Portable.png)

Raspberry Pi 5-based portable practice device. Same analysis engine as Studio, but on-the-go.

**Status:** Prototyping phase — showcasing what's possible!

**Features:**
- Same core engine as FretCoach Studio
- Real-time edge device processing
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
- ✅ Database sync mechanism implemented
- 📋 **Planned:** Physical enclosure design (3D printed), footswitch control, LCD touchscreen interface

See [Portable Application](portable-app.md) for details.

---

### 3. FretCoach Hub (Web Platform)

**Website:** [fretcoach.online](https://fretcoach.online)
**Analytics and AI Coach Dashboard:** [fretcoach.online/dashboard](https://fretcoach.online/dashboard)

Web platform for analytics and practice planning.

![Hub Home](assets/images/hub/1.%20Hub%20-%20Home.png)
![Hub Dashboard](assets/images/hub/3.%20Hub%20-%20Dashboard.png)
![Hub AI Coach](assets/images/hub/4.%20Hub%20-%20AI%20Coach.png)

**Features:**
- AI chat coach (text-to-SQL agent + Gemini 2.5 Flash)
- Performance analytics and trend charts
- AI-generated practice plans
- Session history and statistics

See [Web Dashboard](web-dashboard.md) for details.

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
| Deployment | Vercel (frontend), Railway (backend) |

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

FretCoach uses PostgreSQL hosted on Supabase with three core tables:

| Table | Purpose |
|-------|---------|
| `sessions` | Practice session data: metrics, scale config, note statistics, timestamps |
| `ai_practice_plans` | AI-generated recommendations linked to sessions |
| `user_configs` | User-specific metric preferences (pitch_accuracy, scale_conformity, timing_stability) |

---

## Feature Matrix

| Feature | Studio | Hub | Portable |
|---------|:------:|:---:|:--------:|
| Real-time Audio Analysis | ✅ | — | ✅ |
| 4 Metric Evaluation | ✅ | — | ✅ |
| Live Visual Feedback | ✅ | — | ✅|
| Smart Bulb Integration | ✅ | — | ✅ |
| AI Voice Coaching | ✅ | — | 📋 |
| AI Practice Plans | ✅ | ✅ | ✅ |
| Session Logging | ✅ | View | ✅ |
| Performance Analytics | 📋 | ✅ | — |
| AI Chat Coach | 📋 | ✅ | — |
| Trend Visualization | 📋 | ✅ | — |
| Cloud Sync | ✅ | ✅ | ✅ |
| Offline Capable | ✅ (Manual Mode)| — | ✅ (Manual Mode)|

**Legend:** ✅ Complete | 🚧 In Progress | 📋 Planned

---

## Ambient Lighting

Smart bulb integration for visual performance feedback.

### Color Coding
- 🟢 Green — Good playing (70%+)
- 🟡 Yellow-Green — Could be better (50-70%)
- 🟠 Yellow — Average (30-50%)
- 🔴 Red — Below average (<30%)

> **Configuration:** See [Environment Setup](environment-setup.md#smart-bulb-setup-tuya)

---

## Documentation Navigation

- [Introduction →](introduction.md)
- [Quickstart Guide →](quickstart.md)
- [System Architecture →](architecture.md)
- [← Back to GitHub Repo](https://github.com/padmanabhan-r/FretCoach)

---

**FretCoach** — *Preventive AI for guitar mastery*

*Building with love for music and guitar, by a guitarist* 🎸
