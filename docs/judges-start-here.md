# Demo Guide & Quick Evaluation

**For reviewers, judges, and first-time visitors**

---

## The Problem We're Solving

When practicing guitar alone, you don't realize you're rushing the beat, playing out of tune, or reinforcing bad technique. This leads to slow progress and ingrained mistakes. Without a coach providing immediate feedback, you spend thousands of hours unknowingly cementing errors into muscle memory.

---

## FretCoach: Your AI Practice Coach

FretCoach closes the feedback loop by providing instant, in-the-moment feedback while you practice:

1. **Listens to every note** via USB audio interface or microphone
2. **Analyzes technique in real-time** across four key metrics (pitch, scale conformity, timing, noise)
3. **Provides instant multi-sensory feedback:**
   - 📊 **Visual:** On-screen metrics with color-coded performance
   - 🗣️ **Verbal:** AI coach commentary like *"Your timing is drifting—lock in with the beat"*
   - 💡 **Ambient:** Smart bulb color shifts (green = good, red = needs work)
4. **Adapts to your skill level** with personalized practice recommendations
5. **Tracks progress over time** so improvement is measurable

**Think of it as having a professional guitar instructor watching every note you play.**

---

## Quick Demo (5 Minutes)

### Option 1: Web Dashboard (No Setup Required)

**Live Demo:** [fretcoach.online](https://fretcoach.online)

1. **Visit the dashboard** — No installation required
2. **Click "AI Coach" tab** — Chat interface for practice planning
3. **Ask questions:**
   - "What should I practice next?"
   - "Analyze my recent performance"
   - "Generate a practice plan for improving timing"
4. **View session history** — See past practice sessions and metrics

### Option 2: Desktop Application (Full Experience)

Requires local setup but shows all features:

```bash
# Backend
cd backend && source .venv/bin/activate
uvicorn backend.api.server:app --reload --host 127.0.0.1 --port 8000

# Frontend
cd application && npm run dev
```

**Key Features to Test:**
1. **AI Practice Mode** — Let the AI recommend what to practice
2. **Live Coaching** — Start a session and get real-time verbal feedback
3. **Session Summary** — Review post-session performance analysis

See [Quickstart Guide](quickstart.md) for detailed setup instructions.

---

## System Architecture Highlights

### Hybrid Design: Deterministic + AI

**Local Deterministic Processing:**
- Real-time audio analysis runs locally with <300ms latency
- Four performance metrics calculated using DSP (no LLM)
- Works offline for desktop and portable devices

**AI Enhancements (On-Demand):**
- Practice recommendations based on historical performance
- Live coaching feedback during sessions
- Conversational guidance via web dashboard

**Result:** Low-latency real-time experience with intelligent coaching when needed.

### Multi-Component Ecosystem

```
┌────────────────────────────────────┐
│   PostgreSQL (Supabase)            │
│   Sessions • Plans • Performance   │
└────────────┬───────────────────────┘
             │
     ┌───────┼───────┐
     │       │       │
     ▼       ▼       ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│ Desktop │ │   Web   │ │Portable │
│   App   │ │Dashboard│ │ Device  │
└─────────┘ └─────────┘ └─────────┘
```

All components share a central database for seamless cross-device sync.

---

## AI Coaching System

### Three Intelligent Coaching Modes

**1. Practice Recommendations (AI Mode)**
- Analyzes your last 5 practice sessions from database
- Identifies weakest performance area (pitch, scale, or timing)
- LLM generates personalized recommendation:
  - Which scale to practice
  - What difficulty settings to use
  - Why this will help you improve
- **Traced in Comet Opik** with structured outputs

**2. Live Session Coaching**
- During practice, every 30 seconds the AI provides verbal feedback
- LLM analyzes current metrics and generates corrective instructions
- **Real-time reasoning:** Decides which metric needs attention NOW
- **Traced in Comet Opik** for observability

**3. Conversational Chat (Web Dashboard)**
- Ask questions like "What should I practice next?" or "Why is my timing score low?"
- LangGraph agent with tools:
  - `get_recent_sessions` — Fetches practice history
  - `analyze_performance` — Computes trends
  - `generate_practice_plan` — Creates custom routines
- **Multi-step reasoning** traced end-to-end in Opik

### Multi-LLM Support

FretCoach supports four LLM providers, all traced identically through Opik:
- **OpenAI GPT-4o Mini** — Fast, reliable, good reasoning
- **Google Gemini 2.5 Flash** — Very fast, multimodal capable
- **Deepseek Chat 3.1** — Cost-effective, good reasoning
- **Minimax 2.1** — Multilingual support

All providers work seamlessly with LangChain and Opik tracing.

---

## Observability with Comet Opik

### What We Trace

Every AI interaction is logged with full context:

**AI Practice Recommendations** (`ai-mode` tag)
- Function: `generate_ai_recommendation()`
- Inputs: Recent session data, performance metrics
- Outputs: Scale name, focus area, reasoning, difficulty settings
- Metadata: `user_id`, `practice_id`

**Live Session Coaching** (`live-coach` tag)
- Function: `generate_coaching_feedback()`
- Inputs: Real-time pitch, scale conformity, timing, noise metrics
- Outputs: Corrective feedback text, weakest metric identified
- Metadata: `session_id`, timestamp

**Conversational Chat** (`web-chat` tag)
- LangGraph agent traces with tool calls
- Full reasoning chain visible
- Metadata: `user_id`, conversation context

### View Live Traces

**Opik Project:** [FretCoach Traces](https://comet.com/opik/padmanabhan-r-7119/projects/019bcefc-a27c-718d-8c5f-36472d5decb2)

**Useful filters:**
- `tag:ai-mode` — Practice recommendations
- `tag:live-coach` — Real-time coaching
- `tag:web-chat` — Dashboard conversations

### Meaningful Insights from Opik

**Examples of actionable improvements:**

1. **Prompt optimization:** Initial coaching prompts were too verbose (150+ tokens). Traces showed users needed brief feedback. Refined to 1-2 sentences based on data.

2. **Latency monitoring:** Live coaching must respond in <1s for real-time feel. Opik duration metrics show 95th percentile at 850ms—meeting target.

3. **Recommendation quality:** Track whether users accept or reject AI recommendations. Adjust based on patterns.

4. **Error patterns:** Opik logs reveal failure cases and edge conditions that need handling.

**Opik enables systematic improvement, not guesswork.**

---

## Current Progress

| Component | Status | Notes |
|-----------|--------|-------|
| Desktop Application | ~60% | Core functionality complete. Fine-tuning and evaluation with Opik in progress. |
| Web Dashboard | ~90% | Nearly complete. Deployment pending. |
| Portable Device | ~30% | Hardware setup complete (RPi 5 + Scarlett Solo). Audio analysis agent engine adaptation in progress. |
| Database | Complete | Supabase schema fully set up and operational. |

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

## Evaluation Checklist

Use this to quickly assess FretCoach:

### Core Functionality
- [ ] Real-time audio processing (<300ms latency)
- [ ] Four-metric analysis system working correctly
- [ ] AI practice recommendations functional
- [ ] Live coaching during sessions operational
- [ ] Web dashboard with analytics accessible
- [ ] Database persistence working
- [ ] Multi-LLM support demonstrated

### Opik Integration
- [ ] Traces visible in Opik UI
- [ ] Proper metadata (user_id, session_id, practice_id)
- [ ] Clear tag organization (ai-mode, live-coach, web-chat)
- [ ] Structured outputs logged correctly
- [ ] Error cases traced

### Real-World Value
- [ ] Solves genuine user problem
- [ ] Production-ready (not just a demo)
- [ ] Multiple deployment targets (desktop, web, edge)
- [ ] Cross-platform support

### Innovation
- [ ] Multi-sensory feedback (visual + verbal + ambient)
- [ ] Real-time AI coaching during practice
- [ ] Edge computing prototype (Raspberry Pi)
- [ ] Adaptive recommendations based on history

---

## Important Links

### Live Demos
- **Web Dashboard:** [fretcoach.online](https://fretcoach.online)
- **GitHub Repository:** [FretCoach](https://github.com/padmanabhan-r/FretCoach)

### Opik Resources
- **Main Project:** [FretCoach Opik Project](https://comet.com/opik/padmanabhan-r-7119/projects/019bcefc-a27c-718d-8c5f-36472d5decb2)
- **Filter by AI Mode:** Add filter `tag:ai-mode`
- **Filter by Live Coach:** Add filter `tag:live-coach`

### Documentation
- **Full Docs:** Start at [index.md](index.md)
- **Quickstart:** [quickstart.md](quickstart.md)
- **Architecture:** [architecture.md](architecture.md)
- **AI Coaching Details:** [ai-coaching.md](ai-coaching.md)

---

## Frequently Asked Questions

### Q: Can I test this without setting up locally?

**A:** Yes! Visit [fretcoach.online](https://fretcoach.online) and use the AI Coach chat. Each interaction creates traces you can review in Opik.

### Q: What makes this different from other music apps?

**A:** FretCoach is a **coach**, not a learning app. It doesn't teach you what to play—it analyzes *how* you play and provides adaptive feedback. Every AI decision is traced through Opik for full observability.

### Q: Is the Raspberry Pi device required?

**A:** No, it's a prototype showing edge deployment. Core functionality works on desktop and web.

### Q: Why doesn't audio processing use LLMs?

**A:** Real-time audio analysis needs <10ms latency. LLMs would introduce 500ms+ delays. FretCoach uses deterministic DSP for audio and LLMs only for coaching/planning where latency is acceptable.

### Q: Where can I see the Opik integration code?

**A:** Key files:
- `backend/api/services/ai_agent_service.py` (AI recommendations)
- `backend/api/services/live_coach_service.py` (live coaching)
- Both use `OpikTracer` with LangChain

---

**Navigation:**
- [← Back to Index](index.md)
- [Full Documentation →](index.md)
- [Architecture Details →](architecture.md)
- [AI Coaching System →](ai-coaching.md)
