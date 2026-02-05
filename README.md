# FretCoach : AI-Powered Adaptive Guitar Training

> **Turn your 2026 guitar resolutions into reality.**

![FretCoach](images/FretCoach.jpeg)

**A real-time practice coach that guides you while you play**

> **Already know about FretCoach?** Jump to the [Quickstart Guide](docs/quickstart.md) to get started. **New here?** Read on to understand what makes this different.

---

## Overview

**FretCoach is a real-time AI guitar practice system** that listens as you play and delivers **instant feedback**, fixing mistakes **in the moment**—not days later.

This helps you learn correct technique **before bad habits form**.

**Most tools correct mistakes. FretCoach prevents them from happening in the first place.**

---

## The FretCoach Approach

![FretCoach Approach](images/FretCoach%20Approach.png)

**Close the feedback loop from days to milliseconds:**

- **Local Audio Analysis Agent Engine (<300ms):** A real-time audio analysis engine (fast loop) that listens to every note and computes live performance metrics
- **AI Practice Coach:** Provides strategic guidance and practice insights based on your playing patterns (slow loop)
- **Multi-sensory feedback:** Visual on-screen cues, voice reinforcement, and ambient environmental feedback (*Yes! Your environment becomes a feedback channel*)
- **Gamification:** Scores, color signals, and progress tracking to reinforce consistency and motivation

Every note you play is evaluated immediately. Correct patterns are reinforced. Incorrect ones are flagged **before they turn into habits**.

**Result:** Neuroadaptive learning that shapes motor behavior in real time—not retroactively.

> 🧠 **Neuroscience insight:** It’s 10–20× harder to unlearn a motor habit than to prevent one. Early-stage neuroplasticity is fast and fragile—and FretCoach operates inside this critical window.

---

## Platform Ecosystem

FretCoach is built as a three-part system, with all components connected through a shared central database.

![FretCoach Trifecta](images/FretCoach%20Trifecta.jpeg)

- **FretCoach Studio** — Desktop application for real-time practice, live AI coaching, and ambient lighting feedback
- **FretCoach Portable** — Raspberry Pi–powered portable unit for practicing on-the-go
- **FretCoach Hub** — Web-based dashboard for analytics, progress tracking, session review, and AI-driven practice planning

> **Like having a coach next to you, wherever you go!!**

---

## For Commit To Change Hackathon Judges 🏆

**Want to understand FretCoach super fast?** Check out the [quick deck](#) and [explainer video](#) for a rapid overview. But I would also suggest you read on—at least this README.md fully—to get a proper idea of this product.

**For judges of the "Best Use of Opik" category:** Please see [opik/opik-usage.md](opik/opik-usage.md) or [opik/opik-usage.pdf](opik/opik-usage.pdf) for detailed documentation on all the Opik features I've explored and implemented.

**Personal note:** Wow, what a tool! Why have I not been using Opik for my LLM projects before? I'm genuinely impressed—from advanced tracing capabilities, agent graphs for LangGraph visualization, custom eval metrics, and dashboards, to AI Assist. Right after this hackathon, I'm certain I'll be integrating Opik into my work projects. This isn't just hackathon enthusiasm—I've found a tool that solves real problems I face daily with LLM observability and optimization.

---

## How It Works

### Preventive Neurofeedback Music Learning System

FretCoach is a **Preventive Neurofeedback System** — it shapes motor behavior in real time before maladaptive patterns form. Instead of corrective feedback after mistakes solidify, FretCoach intervenes **during skill execution**, inside the brain's plasticity window.

> **Prevention is neuroadaptive. Correction is retrofitting.**

We call this a **dual-brain architecture**, combining fast deterministic processing with intelligent AI coaching.

![FretCoach Brain Architecture](images/FretCoach%20Brain.png)

---

### The Two Systems

**Audio Analysis Agent (Fast Loop) - Left Brain**
- Real-time processing (<300ms latency)
- On-device local processing, no cloud dependency
- Continuous pitch, scale, timing, noise evaluation using *Digital Signal Processing*
- Controls on screen performance metrics and ambient lighting system

**LLM Powered AI Coach (Slow Loop) - Right Brain**
- LLM-powered preventive coaching: Provides consistent vocal and textual feedback at regular intervals during live playing for instant improvement
- Post-session pattern analysis and personalized practice plan curation based on identified weak areas
- On-demand (not real-time critical)
- Powered by LLM models: Gemini 2.5 Flash, OpenAI GPT-4o-mini, GPT-4o-mini-TTS

> **Hybrid architecture: local speed + AI intelligence = intervention before habits solidify.**

---

### Performance Metrics

FretCoach currently targets scales in music (think of them as the vegetables of the music world—you gotta eat them!).

The audio analysis engine evaluates your playing across four core metrics:

| Metric | What It Measures |
|--------|------------------|
| **Pitch Accuracy** | Note accuracy and intonation against the target scale |
| **Scale Conformity** | Scale coverage and adherence |
| **Timing Stability** | Rhythmic and timing consistency |
| **Noise Control** | String noise and unwanted artifacts |

Three feedback channels:
- **On-screen metrics** — Live scores and note detection
- **AI Voice Coach** — Textual and spoken guidance via GPT-4o-mini and GPT-4o-mini-TTS models
- **Ambient lighting** — Smart bulb feedback (green = good, red = needs work)

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

<p align="center">
  <img src="docs/assets/images/studio/2. Studio - Mode Selection.png" alt="FretCoach Studio Mode Selection" width="400"/>
  <img src="docs/assets/images/studio/9. Studio - Live Session.png" alt="FretCoach Studio Live Session" width="400"/>
</p>

### Features
- Real-time audio analysis (USB interface or built-in mic)
- Live visual metrics and performance scoring
- Manual (choose scale/settings) and AI practice modes (recommended plans)
- Live vocal AI coaching during sessions. (*Imagine a courtside basketball coach*)
- Ambient lighting feedback
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

> **Like a portable guitar pedal**
> In prototyping — evolving into a physical unit with enclosure, LCD display, and footswitch for On/Off control.


**Location:** `/portable/`

<p align="center">
  <img src="images/FretCoach Portable.png" alt="FretCoach Portable Home" width="600"/>
</p>

Raspberry Pi 5-based portable practice device. Same analysis engine as Studio, but on-the-go.

**Status:** Prototyping phase — showcasing what's possible!

### Features
- Same core engine as the FretCoach Studio
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
- 📋 **Planned:** Physical enclosure design, footswitch control, LCD touchscreen interface 

---

## 3. FretCoach Hub (Web Platform)

**Website:** [fretcoach.online](https://www.fretcoach.online)
**Analytics and AI Coach Dashboard:** [fretcoach.online/dashboard](https://www.fretcoach.online/dashboard)

> **Production Repositories:**
> - Backend: [github.com/padmanabhan-r/FretCoach-Web-Backend](https://github.com/padmanabhan-r/FretCoach-Web-Backend)
> - Frontend: [github.com/padmanabhan-r/FretCoach-Web-Frontend](https://github.com/padmanabhan-r/FretCoach-Web-Frontend)

Web platform for analytics and practice planning.

<p align="center">
  <img src="docs/assets/images/hub/1. Hub - Home.png" alt="FretCoach Hub Home" width="400"/>
  <img src="docs/assets/images/hub/3. Hub - Dashboard.png" alt="FretCoach Hub Dashboard" width="400"/>
  <img src="docs/assets/images/hub/4. Hub - AI Coach.png" alt="FretCoach Hub AI Coach" width="400"/>
</p>

### Features
- AI chat coach (text-to-SQL agent + Gemini 2.5 Flash)
- Performance analytics and trend charts
- AI-generated practice plans
- Session history and statistics

> **Demo Note:** The live deployment at [fretcoach.online](https://www.fretcoach.online) shows two sample users for demonstration purposes.

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
- 🟢 Green — Good playing (70%+)
- 🟡 Yellow-Green — Could be better (50-70%)
- 🟠 Yellow — Average (30-50%)
- 🔴 Red — Below average (<30%)

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

## Documentation

📚 **For comprehensive documentation, visit: [FretCoach Docs](https://padmanabhan-r.github.io/FretCoach/)**

### Quick Links

- [Architecture Overview](https://padmanabhan-r.github.io/FretCoach/architecture.html) — Comprehensive technical documentation
- [Environment Setup](https://padmanabhan-r.github.io/FretCoach/environment-setup.html) — Configuration guide for all platforms
- [Desktop Application](https://padmanabhan-r.github.io/FretCoach/desktop-app.html) — Studio setup and usage
- [Audio Analysis Agent Engine](https://padmanabhan-r.github.io/FretCoach/audio-analysis-agent-engine.html) — Real-time audio processing (Fast Loop)
- [AI Coach Agent Engine](https://padmanabhan-r.github.io/FretCoach/ai-coach-agent-engine.html) — LLM-powered coaching (Slow Loop)
- [Portable Application](https://padmanabhan-r.github.io/FretCoach/portable-app.html) — Raspberry Pi device documentation
- [Web Dashboard](https://padmanabhan-r.github.io/FretCoach/web-dashboard.html) — Analytics and AI coach platform
- [Opik Integration](opik/README.md) — Observability and monitoring

---

## Repository Structure

> **Note:** This is a monorepo containing the core FretCoach systems (Studio, Portable and Hub applications). The **web platform components** (FretCoach Hub) are maintained in separate repositories for easy automated deployments to Railway and Vercel:
>
> - **Web Backend:** [github.com/padmanabhan-r/FretCoach-Web-Backend](https://github.com/padmanabhan-r/FretCoach-Web-Backend)
> - **Web Frontend:** [github.com/padmanabhan-r/FretCoach-Web-Frontend](https://github.com/padmanabhan-r/FretCoach-Web-Frontend)
>
> The `web/` directory in this repository contains reference implementations and development versions.

---

> **⚠️ Important for Testing:** The smart bulb integration (ambient lighting) is completely optional. FretCoach works perfectly without it—just leave the `HAVELLS_*` environment variables blank in your `.env` file. The system will automatically disable lighting features and continue normally. All core functionality (audio analysis, AI coaching, metrics) works independently.

---

## Contributing

FretCoach is under active development. Contributions, ideas, suggestions, bug reports, and feature requests are welcome.

Extra hands are always welcome to help build the product and scale it across multiple instruments.

---

**FretCoach** — *Built with love for the music and the guitar* 🎸


