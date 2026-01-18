# Core Project Details

## Overview

FretCoach is a comprehensive AI practice system that transforms how guitarists learn. It combines real-time audio analysis, live performance metrics, intelligent coaching, and multi-sensory feedback into a unified learning experience.

FretCoach acts as an always-available coach that listens to every note, identifies what needs improvement, and provides instant feedback through multiple channels:

- **On-screen visualizations** — Live metrics, performance scoring, and note detection
- **AI coach commentary** — Real-time verbal guidance during practice sessions
- **Ambient lighting** — Smart light color feedback for subconscious motor skill training

Think of it as having a professional coach watching your practice—providing real-time guidance, tracking progress across sessions, and adapting your training based on your unique strengths and weaknesses. FretCoach closes the feedback loop that traditional practice leaves open.

## How FretCoach Accelerates Learning

Traditional learning is slow: practice alone → get feedback much later → try to remember corrections. FretCoach compresses this loop to **milliseconds**:

| Traditional Learning | With FretCoach |
|---------------------|----------------|
| Mistakes go unnoticed | Mistakes flagged instantly |
| Bad habits form | Errors corrected immediately |
| Feedback is abstract | Feedback is visual, verbal, and environmental |
| Progress feels subjective | Progress is measured and tracked |
| Practice lacks direction | AI recommends what to work on next |

**Result:** Correct muscle memory forms faster because mistakes aren’t reinforced. Multi-sensory feedback (screen + voice + lighting) engages more neural pathways, improving retention.

---

## The Learning Ecosystem

FretCoach consists of three interconnected components, all connected to a central database:

### 1. Desktop Application

The primary training environment—a standalone desktop application for focused practice sessions.

**How It Works:**

The input audio signal from the guitar (via USB audio interface or microphone) is processed using DSP (Digital Signal Processing) techniques. An audio analysis agent engine continuously evaluates performance on four key metrics:

- **Pitch Accuracy** — How correctly notes are played against the target scale
- **Scale Conformity** — Coverage of notes within the chosen scale
- **Timing Stability** — Consistency of note spacing and rhythmic precision
- **Noise Control** — Detection of unwanted artifacts and clarity of playing

These metrics are displayed live on screen with visual feedback, allowing the player to see their performance in real-time.

Together, these answer one question:
“Am I playing the right notes, at the right time, cleanly?”

**Practice Modes**

- **Manual Mode** — Player selects exercises and difficulty. Ideal for targeted drills.  
- **AI Mode** — The system analyzes past sessions and recommends what to practice next.  

**Live AI Coach Feedback**

An AI coach provides real-time verbal cues, such as:
- *“Your timing is drifting—lock in with the beat.”*
- *“Pitch accuracy is solid—focus on reducing string noise.”*

This prevents players from unknowingly reinforcing mistakes.

**Ambient Lighting — Subconscious Feedback**

A connected smart bulb reflects performance quality:
- **Green** — Strong performance  
- **Yellow** — Minor issues  
- **Red** — Needs attention  

Color changes are processed faster than conscious thought, encouraging instinctive self-correction. Over time, this creates a subconscious association between good technique and positive feedback—accelerating muscle memory formation.

**Session Logging**

Every session is logged: notes played, accuracy, duration, and trends. This data powers personalized AI recommendations and long-term progress tracking.

---

### 2. Portable Device

A dedicated, Raspberry Pi-powered pedal-like device for practice on the go.

**Concept:**

Imagine having a guitar coach you can carry anywhere. Powered by a Raspberry Pi 5, it runs the same audio analysis agent engine as the desktop application. It runs the same analysis engine as the desktop app, supports Manual and AI modes, and syncs practice history automatically.

**Use Case**

Practice anywhere—without a laptop—while retaining the same intelligent feedback and progress tracking.

---

### 3. Web Dashboard

A cloud-based platform for reviewing progress and planning practice—accessible from any device.

**Features:**

- View recent sessions and performance statistics
- Analyze trends across over time
- Chat with the AI coach to discuss what went wrong and how to improve
- Generate practice plans that sync across devices

All data from both devices continuously aggregates in the central database, making the web dashboard a comprehensive view of your learning journey.

---

## Expandability

The current implementation focuses on **scales**—the foundational building blocks of music. Future versions can expand to chord progressions, song learning, and improvisation training.

Beyond guitar, FretCoach is designed as a foundation that can generalize to other instruments and training contexts—vocals, keyboards, drums—any skill that benefits from adaptive, embodied feedback.

---

## Target Applications

- Music schools seeking technology-enhanced instruction
- Students learning guitar independently
- Guitar players wanting a personal coach always by their side

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
| Portable Device | ~30% | Hardware setup complete (RPi 5 + Scarlett Solo). audio analysis agent engine adaptation in progress. |
| Database | Complete | Supabase schema fully set up and operational. |

---

## Source Code

The GitHub repository will be made public closer to the submission deadline.