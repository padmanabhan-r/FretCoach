# Core Project Details

## Overview

FretCoach is a comprehensive AI practice system that transforms how guitarists learn. It combines real-time audio analysis, live performance metrics, intelligent coaching, and multi-sensory feedback into a unified learning experience.

The system listens to every note you play, evaluates your technique across four dimensions (pitch accuracy, scale conformity, timing stability, and noise control), and delivers instant feedback through:

- **On-screen visualizations** — Live metrics, performance scoring, and note detection
- **AI coach commentary** — Real-time verbal guidance during practice sessions
- **Ambient lighting** — Smart bulb color feedback for subconscious motor skill training

Think of it as having a professional coach watching your practice—providing real-time guidance, tracking progress across sessions, and adapting your training based on your unique strengths and weaknesses. FretCoach closes the feedback loop that traditional practice leaves open.

---

## The Learning Ecosystem

FretCoach consists of three interconnected components, all connected to a central database:

### 1. Desktop Application

The primary training environment—a standalone desktop application for focused practice sessions at home.

**How It Works:**

The input audio signal from the guitar (via USB audio interface or microphone) is processed using DSP techniques. An audio analysis agent engine continuously evaluates performance on four key metrics:

- **Pitch Accuracy** — How correctly notes are played against the target scale
- **Scale Conformity** — Coverage of notes within the chosen scale
- **Timing Stability** — Consistency of note spacing and rhythmic precision
- **Noise Control** — Detection of unwanted artifacts and clarity of playing

These metrics are displayed live on screen with visual feedback, allowing the player to see their performance in real-time.

**Practice Modes:**

- **Manual Mode** — The player selects their own scale, along with sensitivity (how clearly notes must be played to register) and strictness (how much error is tolerated) parameters.
- **AI Mode** — Acts as a personal coach, analyzing practice history and discussing with the player to curate personalized practice routines.

**Live AI Coach Feedback:**

During sessions, the AI coach provides real-time verbal feedback based on the performance metrics—similar to a basketball coach standing courtside, constantly guiding the player on what to focus on to improve.

**Ambient Lighting:**

A connected smart bulb is continuously controlled by the audio analysis agent engine. The bulb color reflects performance quality (green for good, red for needs improvement), providing subconscious feedback that drives the brain to "keep the lights green" and reinforces motor skill development.

**Session Logging:**

All session data—metrics, scale configuration, notes played, duration—is logged to the central database, enabling the AI to adapt future sessions based on historical performance.

---

### 2. Portable Pedal Device

A dedicated, Raspberry Pi-powered device for practice on the go.

**Concept:**

Imagine having a guitar coach you can carry anywhere. Powered by a Raspberry Pi 5, it runs the same audio analysis engine as the desktop application. It features both Manual and AI modes, connects to the central database to fetch practice routines and player history, and controls the same ambient lighting system.

When you can't practice in front of a computer, the portable pedal is your companion.

---

### 3. Web Dashboard

A cloud-based platform for reviewing progress and planning practice—accessible from any device.

**Features:**

- View recent sessions and performance statistics
- Analyze trends across multiple practice sessions
- Chat with the AI coach to discuss what went wrong and how to improve
- Generate practice plans that sync to both the desktop app and portable device

All data from both devices continuously aggregates in the central database, making the web dashboard a comprehensive view of your learning journey.

---

## Expandability

FretCoach is designed as a foundation that can generalize to other instruments and training contexts—vocals, keyboards, drums—any skill that benefits from adaptive, embodied feedback.

---

## Target Applications

- Music schools seeking technology-enhanced instruction
- Students learning guitar independently
- Beginner to intermediate players wanting a personal coach always by their side

---

## Technical Implementation

### Tech Stack

| Component | Technology |
|-----------|------------|
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

### Database Schema

Two core tables in the `fretcoach` schema:

- **`sessions`** — Stores all practice session data including metrics, scale configuration, note statistics, and timestamps
- **`ai_practice_plans`** — AI-generated practice recommendations linked to executed sessions

---

## Current Progress

| Component | Status | Notes |
|-----------|--------|-------|
| Desktop Application | ~60% | Core functionality complete. Fine-tuning and evaluation with Opik in progress. |
| Web Dashboard | ~90% | Nearly complete. Deployment pending. |
| Portable Pedal | ~30% | Hardware setup complete (RPi 5 + Scarlett Solo). Audio analysis engine adaptation in progress. |
| Database | Complete | Supabase schema fully set up and operational. |

---

## Source Code

The GitHub repository will be made public closer to the submission deadline.
