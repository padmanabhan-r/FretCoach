# FretCoach Documentation

> *"An AI guitar pedal that trains your brain, not your tone."*

[![Live Demo](https://img.shields.io/badge/Demo-fretcoach.online-blue)](https://fretcoach.online)
[![Hackathon](https://img.shields.io/badge/Hackathon-Comet_Opik-green)](https://comet.com/opik/padmanabhan-r-7119/projects/019bcefc-a27c-718d-8c5f-36472d5decb2)

---

## What is FretCoach?

FretCoach is a comprehensive AI practice system that transforms how guitarists learn by closing the feedback loop that traditional practice leaves open. It combines real-time audio analysis, live performance coaching, and multi-sensory feedback to turn unstructured practice into a guided learning experience.

**The core problem:** When practicing alone, you reinforce mistakes without realizing it. You don't know if you're rushing, buzzing strings, or playing out of tune.

**FretCoach's solution:** Every note you play is analyzed across four dimensions (pitch accuracy, scale conformity, timing stability, noise control) with instant feedback through on-screen visualizations, AI coaching commentary, and ambient lighting cues.

---

## Quick Navigation

### Getting Started
- **[Introduction](introduction.md)** - Why FretCoach exists and how it accelerates learning
- **[Quickstart Guide](quickstart.md)** - Get up and running in 5 minutes
- **[For Hackathon Judges](judges-start-here.md)** - Essential guide for Comet Opik reviewers

### System Components
- **[Desktop Application](desktop-app.md)** - Primary training environment with real-time analysis
- **[Web Dashboard](web-dashboard.md)** - Cloud analytics and AI coach chat interface
- **[Portable Device](portable-device.md)** - Raspberry Pi edge computing prototype

### Architecture & Technical Details
- **[System Architecture](architecture.md)** - Overall design and component interaction
- **[Audio Processing Engine](audio-engine.md)** - Real-time DSP and metric calculation
- **[AI Coaching System](ai-coaching.md)** - LLM-powered adaptive coaching
- **[Database Schema](database.md)** - PostgreSQL structure and data flow

### Reference
- **[API Reference](api-reference.md)** - FastAPI endpoints and usage
- **[Configuration Guide](configuration.md)** - Environment setup and customization
- **[Appendix: Audio Processing Mathematics](appendix-audio-math.md)** - Deep dive into DSP formulas

---

## The Learning Ecosystem

FretCoach consists of three interconnected components, all connected to a central PostgreSQL database:

```
                    ┌───────────────────────────────────┐
                    │      PostgreSQL (Supabase)        │
                    │  Sessions • Plans • Performance   │
                    └───────────────┬───────────────────┘
                                    │
             ┌──────────────────────┼──────────────────────┐
             │                      │                      │
             ▼                      ▼                      ▼
┌────────────────────┐  ┌─────────────────────┐  ┌────────────────────┐
│   Desktop App      │  │  Web Dashboard      │  │  Portable Device   │
│  Real-time Audio   │  │  Analytics & AI     │  │  Edge Computing    │
│  Live Coaching     │  │  Progress Tracking  │  │  Practice Anywhere │
└────────────────────┘  └─────────────────────┘  └────────────────────┘
```

---

## Key Features

### Real-Time Audio Analysis
- **Four Performance Metrics:** Pitch accuracy, scale conformity, timing stability, noise control
- **Deterministic Processing:** All audio analysis runs locally with zero latency
- **DSP Foundation:** librosa-based frequency analysis and onset detection

### AI Coaching
- **Live Session Feedback:** Real-time verbal guidance during practice
- **Practice Planning:** Personalized recommendations based on performance history
- **Multiple LLM Support:** Gemini 2.5 Flash, GPT-4o Mini, Deepseek Chat 3.1, Minimax 2.1
- **Observable:** Full trace logging via Comet Opik

### Multi-Sensory Feedback
- **Visual:** On-screen metrics with color-coded performance indicators
- **Verbal:** AI coach commentary during and after sessions
- **Ambient:** Smart bulb color shifts from red (struggling) to green (excellent)

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| Desktop Frontend | Electron + React + Vite |
| Desktop Backend | Python + FastAPI |
| Web Frontend | React + TypeScript + Tailwind CSS |
| Web Backend | Python + FastAPI |
| Database | PostgreSQL (Supabase) |
| Audio Processing | NumPy + librosa + sounddevice |
| AI Orchestration | LangChain + LangGraph |
| LLM Providers | OpenAI, Google Gemini, Deepseek, Minimax |
| Observability | Comet Opik |
| Smart Home | Tuya API |
| Deployment | Vercel (web), Electron Builder (desktop) |

---

## For Hackathon Judges

**If you're reviewing this project for the Comet Opik hackathon, start here:**

→ **[Judges Start Here](judges-start-here.md)**

This guide provides:
- Quick demo walkthrough
- Opik integration highlights
- Key evaluation points
- Direct links to trace data

**Live Demo:** [fretcoach.online](https://fretcoach.online)  
**Opik Project:** [View Traces](https://comet.com/opik/padmanabhan-r-7119/projects/019bcefc-a27c-718d-8c5f-36472d5decb2)

---

## Project Philosophy

FretCoach transforms unstructured practice into a guided learning loop. It's designed as an intelligent pedal that **trains the player, not the sound**.

Traditional learning is slow: practice alone → get feedback much later → try to remember corrections.

**FretCoach compresses this loop to milliseconds:**

| Traditional Learning | With FretCoach |
|---------------------|----------------|
| Mistakes go unnoticed | Mistakes flagged instantly |
| Bad habits form | Errors corrected immediately |
| Feedback is abstract | Feedback is visual, verbal, and environmental |
| Progress feels subjective | Progress is measured and tracked |
| Practice lacks direction | AI recommends what to work on next |

**Result:** Correct muscle memory forms faster because mistakes aren't reinforced. Multi-sensory feedback engages more neural pathways, improving retention.

---

## Current Status

| Component | Status | Progress |
|-----------|--------|----------|
| Desktop Application | Production | ~90% |
| Web Dashboard | Production | ~95% |
| Portable Device | Prototype | ~30% |
| Database | Complete | 100% |
| Documentation | In Progress | ~80% |

---

## License & Contact

FretCoach is currently private during hackathon submission. The repository will be made public after evaluation.

**Website:** [fretcoach.online](https://fretcoach.online)  
**Opik Traces:** [View Project](https://comet.com/opik/padmanabhan-r-7119/projects/019bcefc-a27c-718d-8c5f-36472d5decb2)

---

## Documentation Navigation

- [← Back to GitHub Repo](../)
- [Introduction →](introduction.md)
