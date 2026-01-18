# Core Project Details

## Overview

FretCoach is a comprehensive AI practice system that transforms how guitarists learn. It combines real-time audio analysis, live performance metrics, intelligent coaching, and multi-sensory feedback into a unified learning experience.

### The Problem: Practicing Alone Without Feedback

When learning guitar, beginners face a core problem: **they don’t know what they’re doing wrong**. Without a teacher present, mistakes go unnoticed and bad habits form. Practicing alone is like shooting basketballs in the dark—you hear the ball hit something, but you don’t know if it went in.

FretCoach acts as an always-available coach that listens to every note, identifies what needs improvement, and provides instant feedback through multiple channels:

- **On-screen visualizations** — Live metrics showing where mistakes occur  
- **AI coach commentary** — Real-time verbal guidance on what to fix  
- **Ambient lighting** — Room lighting that shifts color based on performance  

---

### What FretCoach Measures (The Four Pillars)

FretCoach evaluates playing across four dimensions that together define solid guitar technique:

| Metric | What It Means | Why It Matters |
|------|---------------|----------------|
| **Pitch Accuracy** | Are you producing the correct notes? | Wrong notes sound immediately “off” to listeners. |
| **Scale Conformity** | Are you staying within the musical rules of the exercise? | Notes outside the scale clash, even if played confidently. |
| **Timing Stability** | Are you playing at a steady rhythm? | Music needs a consistent pulse to feel professional. |
| **Noise Control** | Is your playing clean and intentional? | Clean technique makes each note clear and expressive. |

Together, these answer one question:  
**“Am I playing the right notes, at the right time, cleanly?”**

---

### How FretCoach Accelerates Learning

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

FretCoach consists of three interconnected components backed by a central database.

---

### 1. Desktop Application

The primary training environment for focused practice sessions.

**How It Works**

The guitar connects via a USB audio interface. Every note is analyzed in real time and mapped to live performance metrics displayed on screen.

The dashboard shows:
- Notes being played  
- Whether notes match the exercise  
- A rolling performance score  
- Visual indicators for timing or technique issues  

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

### 2. Portable Pedal Device

A self-contained practice device in a familiar guitar pedal form factor.

**Concept**

The pedal includes:
- Raspberry Pi 5  
- Integrated audio I/O  
- WiFi for cloud sync  
- Battery power for portability  

It runs the same analysis engine as the desktop app, supports Manual and AI modes, and syncs practice history automatically.

**Use Case**

Practice anywhere—without a laptop—while retaining the same intelligent feedback and progress tracking.

---

### 3. Web Dashboard

A cloud-based interface for reviewing progress and planning practice.

**Features**

- View session history and performance stats  
- Analyze trends over time  
- Chat with the AI coach about weaknesses  
- Generate practice plans that sync across devices  

The dashboard serves as a complete view of the player’s learning journey.

---

## Expandability

FretCoach is designed to extend beyond guitar—vocals, keyboards, drums, or any skill that benefits from adaptive, embodied feedback.

---

## Target Applications

- Music schools and instructors  
- Self-learning students  
- Beginner to intermediate guitarists  

---

## Technical Implementation

### Tech Stack

| Component | Technology |
|---------|------------|
| Desktop Frontend | Electron, React |
| Desktop Backend | Python, FastAPI |
| Web Frontend | React, Vite, Tailwind CSS |
| Web Backend | Python, FastAPI |
| Database | PostgreSQL (Supabase) |
| File Storage | Supabase Buckets |
| Agent Orchestration | Custom audio analysis engine, LangChain/LangGraph |
| Portable Hardware | Raspberry Pi 5 |
| Observability | Comet Opik |
| Deployment | Vercel (frontend), Render (backend) |

### Database Schema

- **`sessions`** — Practice session metrics, configuration, and timestamps  
- **`ai_practice_plans`** — AI-generated recommendations linked to sessions  

---

## Current Progress

| Component | Status | Notes |
|---------|--------|-------|
| Desktop Application | ~60% | Core functionality complete; evaluation in progress |
| Web Dashboard | ~90% | Nearly complete |
| Portable Pedal | ~30% | Hardware ready; audio engine adaptation underway |
| Database | Complete | Supabase schema operational |

---

## Source Code

The GitHub repository will be made public closer to the submission deadline.
