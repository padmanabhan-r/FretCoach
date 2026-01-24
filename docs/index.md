# FretCoach Documentation

> *"An AI guitar pedal that trains your brain, not your tone."*

[![Live Demo](https://img.shields.io/badge/Demo-fretcoach.online-blue)](https://fretcoach.online)

---

## The Problem

Solo practice without feedback reinforces both good and bad habits equally. By the time mistakes are identified, motor patterns are already encoded. Unlearning is 10–20× harder than prevention.

## The Solution

FretCoach provides millisecond-level feedback during skill execution. Real-time analysis across four metrics: **pitch accuracy**, **scale conformity**, **timing stability**, and **noise control**.

Three feedback channels:
- **On-screen metrics** — Real-time scoring and note detection
- **AI coaching** — Verbal guidance during practice
- **Ambient lighting** — Smart bulb visual feedback

Preventive intervention inside the motor learning window.

---

## The Ecosystem

FretCoach consists of three connected components sharing a central database for seamless cross-device practice tracking.

![FretCoach Trifecta](/images/FretCoach%20Trifecta.jpeg)

- **FretCoach Studio** — Desktop app for focused practice with real-time analysis and AI coaching
- **FretCoach Portable** — Raspberry Pi device for practice anywhere
- **FretCoach Hub** — Web platform for analytics, session history, and practice planning

All three components sync through PostgreSQL (Supabase), enabling the AI coach to access your complete practice history regardless of which device you use.

---

## The Vision

AI-powered preventive neurofeedback for guitar. Built to extend to other instruments and motor skills.

**Goal:** Reshape motor learning before correction is required.

---

## Quick Navigation

### Getting Started
- **[Introduction](introduction.md)** — The problem with traditional practice and how FretCoach solves it
- **[Quickstart Guide](quickstart.md)** — Get up and running in 5 minutes

### System Components
- **[Desktop Application](desktop-app.md)** — Primary training environment with real-time analysis
- **[AI Coaching System](ai-coaching.md)** — How the intelligent coaching works

### Technical Details
- **[System Architecture](architecture.md)** — Overall design and component interaction
- **[Audio Processing Mathematics](appendix-audio-math.md)** — Deep dive into DSP and metrics

---

## Key Features

### Real-Time Audio Analysis
- Four performance metrics: pitch accuracy, scale conformity, timing stability, noise control
- Deterministic local processing with zero latency
- USB audio interface or built-in microphone support

### AI Coaching
- **Live vocal feedback** — Real-time spoken coaching using GPT-4o-mini-TTS during practice
- **Practice planning** — Personalized recommendations based on performance history
- **Natural language queries** — Text-to-SQL agent in web dashboard for asking questions about your data
- **Multiple LLM support** — Gemini 2.5 Flash, GPT-4o Mini, Minimax 2.1, Deepseek Chat 3.1
- **Observable** — Full trace logging via Comet Opik

### Multi-Sensory Feedback
- **Visual** — On-screen metrics with color-coded performance indicators
- **Verbal** — AI coach commentary during and after sessions
- **Ambient** — Smart bulb color shifts from red (struggling) to green (excellent)

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| Desktop Frontend | Electron, React |
| Desktop Backend | Python, FastAPI |
| Web Frontend | React, Vite, Tailwind CSS |
| Web Backend | Python, FastAPI |
| Database | PostgreSQL (Supabase) |
| File Storage | Buckets (Supabase) |
| Agent Orchestration | Custom orchestration for audio analysis agent engine, LangChain/LangGraph for AI coach |
| Portable Hardware | Raspberry Pi 5, Scarlett Solo USB Audio Interface |
| Observability | Comet Opik |
| Deployment | Vercel (web frontend), Render (web backend) |

---

## Live Demo

**Website:** [fretcoach.online](https://fretcoach.online)

Try the web dashboard to:
- Chat with the AI practice coach
- View session history and analytics
- Generate personalized practice plans

---

## Current Progress

| Component | Status | Notes |
|-----------|--------|-------|
| Desktop Application | ~60% | Core functionality complete. Fine-tuning and evaluation with Opik in progress. |
| Web Dashboard | ~90% | Nearly complete. Deployment pending. |
| Portable Device | ~30% | Hardware setup complete (RPi 5 + Scarlett Solo). Audio analysis agent engine adaptation in progress. |
| Database | Complete | Supabase schema fully set up and operational. |

---

## Documentation Navigation

- [Introduction →](introduction.md)
- [Quickstart Guide →](quickstart.md)
- [← Back to GitHub Repo](../)
