# FretCoach - AI-Powered Adaptive Guitar Training

![FretCoach](images/FretCoach.jpeg)

> *"An AI guitar pedal that trains your brain, not your tone."*

## Overview

FretCoach is an AI-powered learning system that transforms guitar practice through real-time audio analysis and adaptive feedback. By translating performance metrics into immediate ambient lighting cues, FretCoach enables subconscious motor skill development—allowing your brain to self-correct while playing.

## How It Works

FretCoach processes live guitar audio and evaluates four key metrics:
- **Pitch Accuracy** — Correctness of fretted notes against the target scale
- **Scale Conformity** — Coverage and adherence to the chosen scale pattern
- **Timing Stability** — Consistency of note spacing and rhythmic precision
- **Noise Control** — Detection of unwanted artifacts and clean playing

These metrics drive real-time visual feedback through connected smart bulbs, creating a feedback loop that trains muscle memory without interrupting your playing flow.

## Intelligent Coaching

Beyond real-time feedback, FretCoach acts as an autonomous practice coach:
- Aggregates performance metrics across sessions
- Identifies patterns and learning bottlenecks
- Generates personalized practice recommendations using LLM
- Provides live coaching feedback during sessions—like a coach standing courtside
- Adapts training strategies based on historical performance

All real-time audio analysis runs **locally and deterministically**. AI coaching features connect to cloud services for enhanced insights.

---

## System Architecture

FretCoach consists of three interconnected components connected to a central database:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLOUD LAYER                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    PostgreSQL (Supabase)                            │   │
│  │         Sessions • Practice Plans • Performance History             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                    ▲                  ▲                  ▲                  │
└────────────────────│──────────────────│──────────────────│──────────────────┘
                     │                  │                  │
        ┌────────────┴───────┐    ┌─────┴─────┐    ┌───────┴────────┐
        │                    │    │           │    │                │
┌───────▼────────┐   ┌───────▼────────┐   ┌───▼───────────┐   ┌─────▼─────┐
│  Desktop App   │   │  Web Dashboard │   │ Portable Pedal│   │   Smart   │
│  ────────────  │   │  ────────────  │   │ ────────────  │   │   Bulb    │
│ Electron+React │   │ React+FastAPI  │   │ Raspberry Pi  │   │  ──────   │
│ Python Backend │   │ Analytics &    │   │ Edge Audio    │   │  Ambient  │
│ Audio Analysis │   │ AI Coach Chat  │   │ Processing    │   │  Lighting │
│ Live AI Coach  │   │ Practice Plans │   │ Portable Mode │   │  Feedback │
└───────┬────────┘   └────────────────┘   └───────┬───────┘   └───────────┘
        │                                         │                  ▲
        │                                         │                  │
   ┌────▼────┐                               ┌────▼────┐             │
   │ USB     │                               │ Direct  │    ◄────────┘
   │ Audio   │                               │ Audio   │    Real-time Color
   │Interface│                               │ Input   │    Performance Cues
   └────┬────┘                               └────┬────┘
        │                                         │
      🎸 Guitar                                 🎸 Guitar
```

---

## 1. Desktop Application

**Location:** `/application/`

The primary training environment—a standalone desktop application for focused practice sessions.

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

## 2. Portable Pedal (Raspberry Pi)

**Location:** `/portable/`

A standalone physical device designed as an intelligent guitar pedal for practice anywhere.

**Status:** Prototyping phase — demonstrating edge computing capabilities.

### Concept
- Raspberry Pi 5-based controller
- Real-time audio processing at the edge (same analysis engine as desktop)
- Ambient lighting feedback via smart bulbs
- Syncs with central database for seamless experience across devices
- Battery-powered for true portability
- Supports both Manual and AI practice modes

### Current Progress
Hardware setup complete with Raspberry Pi 5 and Scarlett Solo USB interface. Audio analysis engine adaptation in progress.

---

## 3. Web Dashboard

**Location:** `/web/`

Cloud-based analytics platform for reviewing progress and planning practice sessions—accessible from any device.

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

Integrated across Desktop and Portable components for subconscious feedback during practice.

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
├── application/          # Desktop App (Electron + React)
│   ├── electron/         # Electron main process
│   ├── src/              # React components & UI
│   └── build/            # App icons
├── backend/              # Shared Python Backend
│   ├── api/              # FastAPI routes & services
│   ├── core/             # Audio analysis engine
│   └── sql/              # Database schemas
├── web/                  # Web Dashboard
│   ├── src/              # React frontend
│   ├── server/           # FastAPI backend
│   └── public/           # Static assets
├── portable/             # Raspberry Pi Pedal (in development)
└── images/               # Project assets
```

---

## Feature Matrix

| Feature | Desktop | Web | Portable |
|---------|:-------:|:---:|:--------:|
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

FretCoach transforms unstructured practice into a guided learning loop—an intelligent pedal that trains the player, not the sound. The architecture is designed to generalize to other instruments and vocal training that benefit from adaptive, embodied feedback.

---

