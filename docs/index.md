# FretCoach Documentation

> **Turn your 2026 guitar resolutions into reality.**

[![Live Demo](https://img.shields.io/badge/Demo-fretcoach.online-blue)](https://fretcoach.online)

![FretCoach](assets/images/FretCoach.jpeg)

**Real-time AI coaching for guitar practice**

---

## Overview

FretCoach is a real-time AI guitar practice system that reshapes motor learning before conscious correction is required. It listens to every note you play and provides **instant feedback** — closing the loop from days to milliseconds — helping you build correct technique before bad habits form.

> 🧠 **Neuroscience insight:** It's 10–20× harder to unlearn a motor habit than to prevent it. Early-stage neuroplasticity is fast and fragile — FretCoach operates inside this critical window.

**FretCoach doesn't correct — it prevents.**

## Philosophy: Prevention Over Correction

Traditional guitar feedback arrives **days or weeks late**:
- Weekly lessons with an instructor
- Reviewing your own recordings after practice
- Posting videos online for feedback

**FretCoach closes the feedback loop from days to milliseconds:**

1. **Fast Loop (<300ms):** Real-time audio analysis provides instant metrics
2. **Slow Loop (1-2s):** AI coach offers strategic guidance
3. **Multi-channel feedback:** Visual + ambient + vocal reinforcement
4. **Gamification:** Scores, color feedback, and progress tracking

Every note you play receives immediate evaluation. Correct patterns are reinforced. Incorrect patterns are flagged **before they become habits**.

**Result:** Neuroadaptive learning that shapes motor behavior in real-time, not retroactively.

---

## Platform Ecosystem

FretCoach operates across three interconnected components sharing a central database.

![FretCoach Trifecta](assets/images/FretCoach%20Trifecta.jpeg)

- **FretCoach Studio** — Desktop app for real-time practice with AI coaching and ambient feedback

  ![Studio Session](assets/images/studio/9.%20Studio%20-%20Live%20Session.png)

- **FretCoach Portable** — Raspberry Pi powered portable device for practising on-the-go

- **FretCoach Hub** — Web analytics, progress tracking, and AI practice planning

  ![Hub Dashboard](assets/images/hub/3.%20Hub%20-%20Dashboard.png)

---

## How It Works

### Preventive Neurofeedback Systems

FretCoach is a **Preventive Neurofeedback System** — it shapes motor behavior in real time before maladaptive patterns form. Instead of corrective feedback after mistakes solidify, FretCoach intervenes **during skill execution** inside the brain's plasticity window.

> **Prevention is neuroadaptive. Correction is retrofitting.**

Architecture: **dual-brain system** combining fast deterministic processing with intelligent AI coaching.

![FretCoach Brain Architecture](assets/images/FretCoach%20Brain.png)

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
- **[Audio Processing Mathematics](appendix-audio-math.md)** — Deep dive into DSP and metrics

---

## Key Features

- **Real-time audio analysis** — Continuous evaluation during playing
- **Multi-channel feedback** — Visual metrics, AI vocal feedback, and environmental feedback through ambient lighting
- **Intelligent practice** — AI-generated practice plans based on your history
- **Instant feedback loop** — Millisecond-level feedback that prevents mistakes before they become habits
- **Cross-device sync** — Practice anywhere, track everything in one place

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

## Live Demo

**Website:** [fretcoach.online](https://fretcoach.online)

Try the web dashboard to:
- Chat with the AI practice coach
- View session history and analytics
- Generate personalized practice plans

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

## Documentation Navigation

- [Introduction →](introduction.md)
- [Quickstart Guide →](quickstart.md)
- [← Back to GitHub Repo](../)
