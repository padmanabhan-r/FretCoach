# FretCoach Documentation

> *"An AI guitar pedal that trains your brain, not your tone."*

[![Live Demo](https://img.shields.io/badge/Demo-fretcoach.online-blue)](https://fretcoach.online)

---

## The Problem

When practicing alone, guitar players often don't realize they are rushing the beat, playing out of tune, or reinforcing bad technique—leading to slow progress and ingrained mistakes. Without immediate feedback, you spend thousands of hours unknowingly cementing errors into muscle memory.

## The Solution

FretCoach closes the feedback loop during learning by providing instant, in-the-moment feedback while you practice. The system listens to your live guitar signal and analyzes performance in real time across four dimensions: **pitch accuracy**, **scale conformity**, **timing stability**, and **noise control**.

Instead of showing delayed reports, FretCoach delivers immediate feedback through:
- **On-screen visualizations** — Real-time metrics with color-coded performance
- **Spoken AI coaching cues** — Corrective guidance during practice
- **Ambient smart lighting** — Subconscious peripheral feedback

This allows players to self-correct instinctively without breaking their practice flow, shifting learning from delayed correction to immediate prevention.

---

## The Learning Ecosystem

FretCoach is built as a connected system:

- **Desktop application** — Focused practice with real-time metrics, live AI coaching, and automatic session logging
- **Portable Raspberry Pi device** — Practice anywhere with the same analysis engine running at the edge
- **Web dashboard** — Aggregate session data, track progress, and generate personalized practice recommendations

Think of it as having a professional coach watching every practice session—providing real-time guidance, tracking progress, and adapting training based on your strengths and weaknesses.

---

## The Vision

While FretCoach is designed specifically for guitar players, the underlying approach—closing the feedback loop in milliseconds through real-time AI feedback—can be extended to other instruments, vocal training, and skill-based activities such as sports and physical training, where immediate feedback helps prevent incorrect practice.

**The goal: make effective practice embodied, measurable, and sustainable—like having a coach with you every time you practice.**

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
- **Live session feedback** — Real-time verbal guidance during practice
- **Practice planning** — Personalized recommendations based on performance history
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
| Desktop Frontend | Electron + React + Vite |
| Desktop Backend | Python + FastAPI |
| Web Frontend | React + TypeScript + Tailwind CSS |
| Web Backend | Python + FastAPI |
| Database | PostgreSQL (Supabase) |
| Audio Processing | NumPy + librosa + sounddevice |
| AI Orchestration | LangChain + LangGraph |
| LLM Providers | OpenAI, Google Gemini, Deepseek, Minimax |
| Observability | Comet Opik |

---

## Live Demo

**Website:** [fretcoach.online](https://fretcoach.online)

Try the web dashboard to:
- Chat with the AI practice coach
- View session history and analytics
- Generate personalized practice plans

---

## Documentation Navigation

- [Introduction →](introduction.md)
- [Quickstart Guide →](quickstart.md)
- [← Back to GitHub Repo](../)
