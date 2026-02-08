# FretCoach Documentation

> **Turn your 2026 guitar resolutions into reality.**

[![Website](https://img.shields.io/badge/Website-fretcoach.online-blue)](https://fretcoach.online)

![FretCoach](assets/images/FretCoach.jpeg)

**A real-time practice coach that guides you while you play**

---

## Overview

**FretCoach** is a real-time AI guitar practice system that listens as you play and delivers instant feedback—fixing mistakes in the moment, not days later.

**Most tools correct mistakes. FretCoach prevents them.**

---

## Quick Navigation

### Getting Started
- **[Introduction](introduction.md)** — The problem with traditional practice and how FretCoach solves it
- **[Quickstart Guide](quickstart.md)** — Get up and running in 5 minutes
- **[FAQ](faq.md)** — Frequently asked questions about FretCoach

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
- **[Troubleshooting Guide](troubleshooting.md)** — Common issues and solutions

### Observability and Evaluation
- **[Opik Observability](opik-observability.md)** — LLM tracing and evaluation with Comet Opik

---

## Platform Details

See **[Introduction](introduction.md#the-ecosystem)** for details on:
- **FretCoach Studio** — Desktop application
- **FretCoach Portable** — Raspberry Pi device
- **FretCoach Hub** — Web platform

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
| LLM Providers | OpenAI (GPT-4o-mini, TTS), Google Gemini 3 Flash Preview |
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

- [← Back to GitHub Repo](https://github.com/padmanabhan-r/FretCoach)
- [Next: Introduction →](introduction.md)

---

**FretCoach** — *Building with love for the music and the guitar* 🎸


