# Project Description

**It's time to turn your 2026 guitar resolutions into reality.**

FretCoach is a real-time, AI-powered music practice system for guitar that provides feedback while you are still playing, not after the session is over.

Traditional practice relies on delayed feedback — from teachers, recordings, or self-review — by which time mistakes have already turned into muscle memory. FretCoach closes this gap by delivering immediate, multi-sensory feedback that helps players correct technique before bad habits form.

The system is built around a dual-loop feedback architecture that combines digital audio signal processing with AI-powered reasoning. A fast, deterministic loop runs locally to analyze the live audio signal with low latency and deliver instant feedback through live visual indicators, subtle ambient lighting, and vocal cues — without interrupting practice flow.

A slower reflective loop aggregates session metrics over time to analyze trends, generate targeted practice recommendations, and provide conversational coaching grounded strictly in measured performance data.

FretCoach is implemented as a connected ecosystem consisting of a desktop practice application, a portable edge device, and a web dashboard for analytics and AI-driven practice planning.

While designed for guitar, the core idea of an AI-powered real-time feedback system is instrument-agnostic and can extend to vocals, piano, sports training, and other skill-learning domains where timing, accuracy, and repetition matter.

> Most tools tell you what you did wrong later.
> FretCoach helps you stop doing it again.

---

# Submission Details

## How We Approached It

The primary design constraint was how fast feedback reaches the player — to truly close the feedback loop. Real-time feedback is only effective if it arrives before the brain has moved on. We set a target of sub-300 ms from audio input to response, which immediately ruled out cloud round-trip architectures for the fast loop.

Everything in the live feedback path — live playing analysis and visual or ambient indicators — runs locally on-device using deterministic signal processing against a live audio stream.

The AI cloud layer was deliberately kept out of the hot path. Rather than pushing LLM inference into the real-time loop, we separated concerns: the local engine handles detection and scoring, while AI operates only on aggregated signals. Live AI feedback, including spoken coaching via TTS models, is driven by aggregated performance metrics computed locally by the audio engine. These metrics are sent to the AI layer at user-configurable intervals, where an LLM (gpt-4o-mini) generates coaching guidance that is then converted to speech via a TTS model (gpt-4o-mini-TTS).
All timing decisions are made locally and by the user; the cloud is used only for interpretation and speech generation. This keeps the real-time loop independent of network latency.

---

## Architecture Decisions

The three-component structure (Studio, Portable, Hub) was designed around how learners actually practice.

- **FretCoach Studio (Desktop)** — prioritizes low-latency local processing and a rich, real-time UI
- **FretCoach Portable** — a standalone, guitar-pedal-style prototype that runs independently without a desktop
- **FretCoach Hub (Web)** — focuses on historical context, analytics, and conversational reasoning

The system is built as a connected ecosystem with a shared database, enabling a common data and metrics layer while keeping real-time analysis and cloud-based reasoning paths fully decoupled.

The autonomous, agentic chatbot in FretCoach Hub was a deliberate design choice alongside a fixed dashboard. Practice data is personal and non-uniform — different players care about different aspects of their progress. A conversational interface allows users to explore their data naturally (e.g. *"How did my timing trend last week?"*) without requiring us to predefine every possible query.

---

## What We Built During the Hackathon (Tech Preview)

- A complete real-time audio analysis pipeline for pitch accuracy, tempo tracking, scale coverage, and consistency scoring
- Live feedback integrations including visual indicators, ambient lighting (Tuya smart bulb), and spoken AI coaching via OpenAI TTS
- A LangGraph-based AI coach with tool-calling for database queries and practice plan generation
- A Raspberry Pi–based portable prototype (to later become a guitar pedal) running the same local analysis engine
- A web dashboard with session analytics, progress tracking, and the AI chat interface
- Full Comet Opik instrumentation across all AI calls, including tracing, metadata tagging, and session-level evaluation

---

## Bigger Picture

The feedback-loop problem isn't unique to guitar — it is simply a concrete starting point. The same architecture applies anywhere immediate feedback matters: other instruments, vocals, sports, physical therapy, and skill training.

FretCoach is a concrete implementation of a broader principle: **AI should augment real-time feedback systems**. We refer to this pattern as **Real-time Augmented Feedback (RAF)**, analogous to how RAG augments generation with retrieval.

Imagine an AI coach saying, *"Brace your core before you hit that deadlift,"* powered by real-time sensing on a Raspberry Pi with camera modules. Such systems could prevent errors — or even injuries — rather than merely analyzing them after the fact.

---

## On the Opik Integration

Every AI interaction was instrumented — not just logging completions, but feature-level tagging, full tool-call chains in the LangGraph agent, and user/session metadata attached to each trace. We also created evaluations, dashboards, and alerting workflows, treating this as a production system from day one.

Constraints such as limited usage on free-tier models surfaced fallback behavior early. This instrumentation gave us visibility into when fallback models were triggered, how SQL generation behaved across different query types, and where latency clustered. Full Opik usage documentation is included in the attached PDF.


# One-liner

A real-time AI music practice system for guitar that listens, reacts, and coaches while you play.

---

# Link to Code

> https://github.com/padmanabhan-r/FretCoach

# Link to Demo Video

> https://www.youtube.com/watch?v=ko7pAXDDkJQ

# Link to Presentation

> https://docs.google.com/presentation/d/1Mm2ERUg9ZhWOH_aVsTBwBKI8s9U_AHglDOdXagMTqBY/edit?usp=sharing


# Live Demo Link

> https://www.fretcoach.online/
