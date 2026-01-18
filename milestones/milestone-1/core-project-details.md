# Core Project Details

## Overview

FretCoach is a comprehensive AI practice system that transforms how guitarists learn. It combines real-time audio analysis, live performance metrics, intelligent coaching, and multi-sensory feedback into a unified learning experience.

### The Problem: Practicing Alone Without Feedback

When learning guitar, beginners face a fundamental challenge: **they don't know what they're doing wrong**. Without a teacher present, mistakes go unnoticed and bad habits form. Traditional practice is like shooting basketballs in the dark—you hear the ball hit something, but you can't see if it went in.

FretCoach solves this by acting as an always-available coach that listens to every note, identifies exactly what needs improvement, and provides instant feedback through multiple channels:

- **On-screen visualizations** — Live metrics showing exactly where mistakes occur
- **AI coach commentary** — Real-time verbal guidance explaining what to fix and how
- **Ambient lighting** — Room lighting that shifts color based on performance, creating an intuitive feedback loop

### What FretCoach Measures (The Four Pillars)

The system evaluates playing across four dimensions that together capture the fundamentals of good guitar technique:

| Metric | What It Means (Non-Technical) | Why It Matters |
|--------|------------------------------|----------------|
| **Pitch Accuracy** | Are you pressing the right spots on the guitar neck to produce the correct notes? | Like typing—hitting the wrong keys produces gibberish. Wrong notes sound "off" to listeners. |
| **Scale Conformity** | Are you staying within the musical "ruleset" for the song? (Scales are like approved note palettes that sound good together) | Playing notes outside the scale is like using clashing colors in a painting—technically possible, but sounds wrong. |
| **Timing Stability** | Are you playing notes at a steady, consistent rhythm? | Music has a pulse like a heartbeat. Uneven timing makes music sound amateur and hard to follow. |
| **Noise Control** | Is your playing clean, without accidental string buzzes, muted notes, or unwanted sounds? | Like speaking clearly vs. mumbling—clean technique makes each note ring out intentionally. |

Together, these four metrics answer the question: **"Am I playing the right notes, at the right time, cleanly?"**

### How FretCoach Accelerates Learning

Traditional guitar learning follows a slow cycle: practice alone → take a lesson days/weeks later → teacher points out mistakes → try to remember corrections during next solo practice. FretCoach compresses this cycle to **milliseconds**:

| Traditional Learning | With FretCoach |
|---------------------|----------------|
| Mistakes go unnoticed for days | Mistakes flagged instantly |
| Bad habits form through repetition | Immediate correction prevents habit formation |
| Feedback is verbal and abstract | Feedback is visual, auditory, and environmental |
| Progress is subjective ("I think I'm getting better") | Progress is quantified with metrics and trends |
| Practice is undirected ("What should I work on?") | AI recommends exactly what to practice based on weaknesses |

**The result:** Players develop correct muscle memory faster because they never unknowingly reinforce mistakes. The multi-sensory feedback (screen + voice + lighting) engages more neural pathways than traditional practice, leading to deeper skill retention.

---

## The Learning Ecosystem

FretCoach consists of three interconnected components, all connected to a central database:

### 1. Desktop Application

The primary training environment—a standalone desktop application for focused practice sessions at home.

**How It Works:**

The guitar connects to the computer via a USB audio interface (a small device that converts guitar signals to digital audio). The software analyzes every note in real-time—within milliseconds of being played—and continuously updates the four performance metrics on screen.

The player sees a live dashboard showing:
- Which notes they're playing
- Whether those notes are correct for their chosen exercise
- A rolling score that updates with each note
- Visual indicators when timing drifts or technique falters

**Practice Modes:**

- **Manual Mode** — The player chooses what to practice (e.g., "C Major scale") and sets difficulty parameters. Good for focused drills on specific skills.
- **AI Mode** — The system analyzes past sessions, identifies weak areas, and suggests what to practice next. Like having a personal trainer who remembers every workout.

**Live AI Coach Feedback:**

During practice, an AI coach speaks in real-time through the computer speakers—similar to a basketball coach standing courtside. Examples:
- *"Your timing is drifting—try to lock in with the beat"*
- *"Great pitch accuracy! Now focus on cleaning up that string noise"*
- *"You've been avoiding the high notes—let's work on that area"*

This verbal feedback helps players correct mistakes immediately rather than reinforcing bad habits.

**Ambient Lighting — The Science of Subconscious Feedback:**

A connected smart bulb continuously changes color based on performance:
- **Green** = Playing well (correct notes, good timing, clean technique)
- **Yellow** = Minor issues (slightly off timing, occasional wrong notes)
- **Red** = Needs attention (multiple errors, poor technique)

**Why this works:** The brain processes environmental color changes faster than conscious thought. Players naturally and subconsciously adjust their playing to "keep the room green" without actively thinking about it. This leverages the same psychological principle used in:
- Video game health bars (players instinctively avoid red)
- Traffic lights (immediate behavioral response)
- Biofeedback therapy (using physiological signals to train relaxation)

Over time, this creates a **Pavlovian association** between good technique and positive environmental feedback, accelerating muscle memory formation. The player's hands learn the correct movements before the conscious mind fully understands why.

**Session Logging:**

Every practice session is recorded to a central database: which notes were played, accuracy scores, duration, improvement trends. This data powers the AI coach's personalized recommendations and lets players track their progress over weeks and months.

---

### 2. Portable Pedal Device

A dedicated, self-contained practice device shaped like a guitar pedal—the same form factor guitarists already use for effects.

**Concept:**

Imagine having a guitar coach you can carry anywhere. The pedal contains:
- A Raspberry Pi 5 (a credit-card-sized computer)
- Integrated audio input/output (guitar plugs directly into the pedal)
- WiFi connectivity to sync with the cloud database
- Battery power for true portability

It runs the same audio analysis engine as the desktop application, supports both Manual and AI practice modes, and controls the ambient lighting system. Your practice history syncs automatically—start a session at home on the desktop, continue on the pedal at a friend's house, review progress on the web dashboard from your phone.

**Use Case:** Practice anywhere without needing a laptop—at a park, backstage, in a hotel room. The pedal provides the same intelligent feedback through ambient lighting and syncs all data when connected to WiFi.

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
| Portable Hardware | Raspberry Pi 5, Integrated Audio I/O |
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
| Portable Pedal | ~30% | Hardware setup complete (RPi 5 + integrated audio). Audio analysis engine adaptation in progress. |
| Database | Complete | Supabase schema fully set up and operational. |

---

## Source Code

The GitHub repository will be made public closer to the submission deadline.
