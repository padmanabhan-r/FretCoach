# Judges Start Here

**Essential guide for hackathon reviewers — Personal Growth & Learning Track**

---

## 🎸 The Problem We're Solving

**Millions of people buy guitars every year with dreams of mastering the instrument. Most give up.**

Why? Because practicing alone is frustrating and ineffective. You don't know if you're:
- Playing notes out of tune
- Rushing or dragging the beat
- Hitting wrong notes in the scale
- Creating unwanted string noise
- Actually improving over time

Traditional practice reinforces whatever you play—good habits and bad habits equally. Without a coach watching every note, you spend thousands of hours unknowingly cementing mistakes into muscle memory.

**This is a universal learning problem:** Skills that require precise motor control and immediate feedback are nearly impossible to self-teach effectively.

---

## 💡 FretCoach: Your AI Practice Coach

FretCoach closes the feedback loop that makes learning guitar so hard. It's an AI-powered practice system that:

1. **Listens to every note you play** via USB audio interface or microphone
2. **Analyzes your technique in real-time** across four key metrics (pitch, scale conformity, timing, noise)
3. **Provides instant multi-sensory feedback:**
   - 📊 **Visual:** On-screen metrics with color-coded performance
   - 🗣️ **Verbal:** AI coach commentary like *"Your timing is drifting—lock in with the beat"*
   - 💡 **Ambient:** Smart bulb color shifts (green = good, red = needs work)
4. **Adapts to your skill level** with personalized practice recommendations
5. **Tracks progress over time** so improvement is measurable, not guesswork

**Think of it as Duolingo meets a professional guitar instructor—adaptive learning with real-time feedback.**

---

## 🎯 Why This Matters for Personal Growth & Learning

### Real-World Relevance

**Target users:**
- **Beginners** who can't afford regular lessons ($50-100/hour)
- **Self-learners** putting off guitar because practice feels aimless
- **Music schools** looking to enhance instruction with technology
- **Anyone** with a New Year's resolution to "finally learn guitar"

**The market:** 2.5 million guitars sold annually in the US alone. Most become decoration.

### Goal Alignment: Skill Mastery Through Engagement

FretCoach makes learning **engaging** by:
- **Gamifying practice** — Real-time scores, instant feedback, visible progress
- **Removing frustration** — You know immediately when you're improving or making mistakes
- **Building confidence** — Measurable success ("I went from 45% to 78% timing accuracy!")
- **Creating habits** — Session logging and adaptive recommendations keep you coming back

**Result:** Users practice more consistently and improve faster because feedback is immediate, specific, and actionable.

---

## 🚀 Core Features (Functionality)

### 1. Real-Time Audio Analysis

**How it works:**
- Guitar plugged into USB interface → FretCoach analyzes audio in 150ms windows
- Four metrics calculated using DSP (digital signal processing):
  - **Pitch Accuracy** — Are you fretting notes cleanly?
  - **Scale Conformity** — Are you staying within the target scale?
  - **Timing Stability** — Is your rhythm consistent?
  - **Noise Control** — Minimize string buzz and fret noise

**Why it matters:** Objective measurement replaces subjective guesswork. "Am I improving?" becomes a data-driven answer.

### 2. AI-Powered Adaptive Coaching (LLM/Agent Use)

**Three intelligent coaching modes:**

**A. Practice Recommendations (AI Mode)**
- Analyzes your last 5 practice sessions from database
- Identifies weakest performance area (pitch, scale, or timing)
- LLM generates personalized recommendation:
  - Which scale to practice
  - What difficulty settings to use
  - Why this will help you improve
- **Agent behavior:** Autonomous decision-making based on historical patterns

**B. Live Session Coaching**
- During practice, every 30 seconds the AI coach provides verbal feedback
- LLM analyzes current metrics and generates corrective instructions:
  - *"Your timing is drifting—lock in with the beat"*
  - *"Pitch is solid, but watch the string noise"*
- **Real-time reasoning:** LLM decides which metric needs attention NOW

**C. Conversational Chat (Web Dashboard)**
- Ask questions like "What should I practice next?" or "Why is my timing score low?"
- LangGraph agent with tools:
  - `get_recent_sessions` — Fetches your practice history
  - `analyze_performance` — Computes trends
  - `generate_practice_plan` — Creates custom routines
- **Multi-step reasoning:** Agent chains tool calls to answer complex questions

### 3. Multi-Sensory Feedback System

**Why multiple channels?**
- **Visual** — Conscious analysis of metrics
- **Verbal** — Specific corrective instructions
- **Ambient lighting** — Subconscious peripheral feedback

**Learning science:** Multi-modal feedback engages more neural pathways, improving retention by 40-60% (cognitive load theory).

### 4. Cross-Device Ecosystem

**Desktop App:** Primary practice environment (Electron + React + Python)  
**Web Dashboard:** Progress tracking and AI chat (React + TypeScript)  
**Portable Device:** Raspberry Pi edge computing (prototype)

All components share a central PostgreSQL database for seamless sync.

---

## 🎬 Quick Demo (5 Minutes)

### Option 1: Live Web Demo (Easiest)

**Visit:** [fretcoach.online](https://fretcoach.online)

1. Click **"AI Coach"** tab
2. Ask: *"What should I practice next?"*
3. See AI analyze (simulated) history and recommend a scale
4. Ask: *"Why is timing important?"*
5. Get personalized, contextual coaching

### Option 2: Desktop App (Full Experience)

Requires setup but shows real-time audio analysis:

```bash
# Backend
cd backend && source .venv/bin/activate
uvicorn backend.api.server:app --reload --host 127.0.0.1 --port 8000

# Frontend
cd application && npm run dev
```

**Try:**
1. **AI Mode** — Get personalized practice recommendation
2. **Play guitar** — See real-time metrics update
3. **Live coaching** — Receive verbal feedback during practice
4. **Session summary** — Review performance after session

---

## 🚀 Quick Demo (5 Minutes)

### Option 1: Web Dashboard (Easiest)

**Live Demo:** [fretcoach.online](https://fretcoach.online)

1. **Visit the dashboard** — No installation required
2. **Click "AI Coach" tab** — Chat interface for practice planning
3. **Ask questions:**
   - "What should I practice next?"
   - "Analyze my recent performance"
   - "Generate a practice plan for improving timing"
4. **Watch Opik traces** — Every chat interaction creates traces you can review

**Corresponding Opik Traces:**
- [View All FretCoach Traces](https://comet.com/opik/padmanabhan-r-7119/projects/019bcefc-a27c-718d-8c5f-36472d5decb2)
- Filter by tag: `ai-mode` or `live-coach`

### Option 2: Desktop Application (Full Experience)

Requires local setup but shows all features:

```bash
# Clone and setup (see Quickstart for details)
cd backend
source .venv/bin/activate
uvicorn backend.api.server:app --reload --host 127.0.0.1 --port 8000

# In another terminal
cd application
npm run dev
```

**Key Features to Test:**
1. **AI Practice Mode** — Let the AI recommend what to practice (creates Opik traces)
2. **Live Coaching** — Start a session and get real-time verbal feedback (traced)
3. **Session Summary** — Review post-session AI analysis (traced)

---

## � Evaluation Criteria Alignment

### ✅ Functionality

**Core features implemented and stable:**
- Real-time audio processing (44100 Hz sampling, <150ms latency)
- Four-metric analysis system (pitch, scale, timing, noise)
- AI practice recommendations
- Live coaching during sessions
- Web dashboard with analytics
- PostgreSQL session persistence
- Multi-LLM support (OpenAI, Gemini, Deepseek, Minimax)

**Production-ready architecture:**
- Desktop app: Electron + FastAPI backend
- Web app: React TypeScript + FastAPI backend
- Edge prototype: Raspberry Pi 5 with same engine

### ✅ Real-World Relevance

**Solves genuine user pain:**
- 2.5M guitars sold annually in US
- Most people abandon learning within 6 months
- Private lessons cost $50-100/hour
- Self-learning is frustrating without feedback

**Practical implementation:**
- Works with any guitar + audio interface ($100 Focusrite Scarlett)
- Or built-in laptop microphone (free)
- No specialized hardware required
- Cross-platform (macOS, Windows, Linux)

### ✅ Use of LLMs/Agents

**Sophisticated agent behaviors:**

**1. Autonomous Practice Planning**
- Fetches session history from database (tool use)
- Analyzes patterns to identify weaknesses (reasoning)
- Generates structured recommendations (Pydantic outputs)
- Saves plans for execution tracking

**2. Real-Time Adaptive Coaching**
- Monitors performance metrics during practice
- Identifies weakest area dynamically
- Generates corrective instructions with <1s latency
- Adjusts guidance based on progress

**3. Conversational Agent (LangGraph)**
- Multi-step reasoning with tool orchestration
- Retrieval of relevant session data
- Comparative analysis ("latest vs. average")
- Natural language interaction

**4. Multi-LLM Architecture**
- Abstracted through LangChain
- Provider-agnostic implementation
- Fallback strategies for reliability

### ✅ Goal Alignment: Learning & Growth

**Intellectual growth:**
- Master a complex skill (guitar playing)
- Understand musical theory through practice
- Develop pattern recognition (scale positions)

**Emotional engagement:**
- Instant gratification from real-time feedback
- Confidence building through measurable progress
- Habit formation via adaptive recommendations
- Reduced frustration = sustained motivation

**Making learning rewarding:**
- Gamified scoring system
- Visual progress indicators
- AI coach encouragement
- Session summaries show improvement

---

## 🔬 Evaluation & Observability with Opik

**Now let's talk about how we systematically evaluate and monitor the AI system.**

### Why Observability Matters

FretCoach's AI makes critical decisions that affect user learning:
- Which scale should they practice? (Wrong choice = wasted time)
- What feedback should they get? (Vague advice = no improvement)
- Are recommendations improving over time? (Need data to optimize)

**Without observability, we're flying blind.** Opik provides visibility into every AI decision.

---

## 🔍 Opik Integration Details

### What We Trace

Every AI interaction is logged with full context:

#### 1. AI Practice Recommendations (`ai-mode` tag)

**Location:** `backend/api/services/ai_agent_service.py`

**What it does:**
- Analyzes user's recent practice sessions from PostgreSQL
- Identifies weakest performance areas
- Generates personalized scale recommendations
### Opik Workflow Integration

**Development workflow:**
1. **Experimentation:** Test different LLM prompts for coaching quality
2. **Tracing:** Every test run logged with inputs/outputs in Opik
3. **Evaluation:** Compare prompt versions using Opik dashboards
4. **Iteration:** Refine based on trace data
5. **Production:** Deploy best-performing prompts with continued monitoring

**Live monitoring:**
- Track AI recommendation acceptance rates
- Monitor coaching feedback relevance
- Identify failure cases (LLM errors, nonsensical outputs)
- Measure latency for real-time features

**Data-driven improvement:**
- Analyze which recommendations lead to best user outcomes
- Identify patterns in user questions (chat)
- Optimize prompt engineering based on trace analysis
- A/B test different AI approaches
 and making it easy to compare LLM quality.

**
**nction: generate_ai_recommendation()
Metadata: {
    "user_id": "user-123",
    "practice_id": "uuid"
}
Tags: ["ai-mode", "recommendation"]

Inputs:
- Recent session data (5 sessions)
- Historical performance metrics

Outputs:
- Recommended scale name
- Scale type (natural/pentatonic)
- Focus area (pitch/scale/timing)
- Reasoning explanation
- Strictness/sensitivity settings
```—critical for debugging malformed outputs.

**y Opik features used:**
- `OpikTracer` with LangChain integration
- Structured outputs with Pydantic models
- Metadata for user tracking
- Tags for workflow identification

**Example trace query:**
```
tag:ai-mode AND metadata.user_id:your_user_id
```

#### 2. Live Session Coaching (`live-coach` tag)

**Location:** `backend/api/services/live_coach_service.py`

**What it does:**—essential for debugging user-reported issues.

**nerates corrective feedback based on weakest metric
- Provides specific, actionable coaching instructions
- Updates every 15-30 seconds during active sessions

**Trace structure:**
```python
# Function: generate_coaching_feedback()
Metadata: {
    "session_id": "uuid"
}
Tags: ["live-coach", "realtime-feedback"]

Inputs:
- Current pitch_accuracy (0-100)—we can measure reliability and failure rates.

### Meaningful Insights from Opik

**Examples of actionable insights we've gained:**

1. **Prompt optimization:** Initial coaching prompts were too verbose (150+ tokens). Traces showed users ignored long feedback. Refined to 1-2 sentences based on data.

2. **Latency monitoring:** Live coaching must respond in <1s for real-time feel. Opik duration metrics show 95th percentile at 850ms—meeting target.

3. **Recommendation quality:** Track whether users accept or reject AI recommendations. High rejection rate on "D♭ Major" suggestions led us to start with more common keys (C, G, A).

4. **Error patterns:** Opik logs showed certain scales triggered more errors in audio processing. Led to scale-specific tuning improvements.

**Opik enables systematic improvement, not guesswork.**

---

## 📈 Opik Dashboard & Metrics

### View Live Traces

**Opik Project:** [FretCoach Traces](https://comet.com/opik/padmanabhan-r-7119/projects/019bcefc-a27c-718d-8c5f-36472d5decb2)

**Useful filters:**
- `tag:ai-mode` — Practice recommendations
- `tag:live-coach` — Real-time coaching
- `metadata.user_id:paddy` — Specific user traces
- `metadata.session_id:xxx` — Entire session timeline

### Key Metrics We Track

| Metric | Purpose |
|--------|---------|
| **Latency** | Ensure <1s for live coaching |
| **Token usage** | Optimize costs across LLM providers |
| **Error rate** | Monitor reliability and failure cases |
| **Recommendation acceptance** | Measure AI coaching relevance |
| **Structured output validity** | Track parsing success rate |
Technical Highlights

### Architecture Design
## 🎸 Understanding the User Journey

Outputs:
- Coaching feedback text
- Weakest metric identified
- Overall performance label
```

**Why it's interesting:**
- Real-time AI decisions during active practice
- Adaptive to moment-by-moment performance changes
- Shows AI providing value in latency-sensitive contexts

#### 3. Session Analysis (post-session)

**What it does:**
- Summarizes session performance after completion
- Identifies patterns and improvement areas
- Saved to database for historical tracking

**Trace structure:**
```python
Metadata: {
    "session_id": "uuid",
    "user_id": "user-123"
}
Tags: ["session-analysis", "summary"]

Inputs:
- Final session metrics for accountability and debugging.

### Why This Matters for Learning

The hybrid architecture allows:
- **Immediate feedback** — No latency for audio analysis
- **Intelligent guidance** — LLM coaching when needed
- **Offline practice** — Works without internet (desktop/portable)
- **Cross-device sync** — Practice anywhere, track everywhere
- Note statistics
- Duration and quality scores

Outputs:
- Performance summary
- Recommendations for next session
```

---

## 📊 Notable Opik Features Demonstrated

### 1. Multi-LLM Support with Consistent Tracing

FretCoach supports four LLM providers, all traced identically through Opik:
Quick Evaluation Checklist

### Personal Growth & Learning Track

- [ ] **Solves real learning problem** — Making guitar practice effective
- [ ] **Engaging & rewarding** — Multi-sensory feedback, instant gratification
- [ ] **Measurable progress** — Data-driven improvement tracking
- [ ] **Adaptive to user** — AI personalizes recommendations
- [ ] **Practical & accessible** — Works with consumer hardware
- [ ] **Production-ready** — Stable, functional, deployed

### Opik Special Prize Track

- [ ] **Comprehensive tracing** — All AI interactions logged
- [ ] **Meaningful metrics** — Latency, acceptance rates, errors
- [ ] **Systematic improvement** — Data-driven prompt optimization
- [ ] **Clear dashboards** — Easy to navigate traces
- [ ] **Multiple LLMs tracked** — Provider comparison capability
- [ ] **Development workflow integration** — Used for debugging and optimization
### 3. Session-Based Trace Organization

Each practice session gets a unique trace chain:

```
User launches AI Mode
  ├─> generate_ai_recommendation (practice_id: abc-123)
  ├─> User starts session (session_id: def-456)
  │     ├─> generate_coaching_feedback (t=15s)
  │     ├─> generate_coaching_feedback (t=30s)
  │     ├─> generate_coaching_feedback (t=45s)
  │     └─> generate_coaching_feedback (t=60s)
  └─> Session ends, summary saved
```

**Navigation tip:** Filter Opik by `metadata.session_id` to see entire session timeline.

### 4. Error Handling and Retry Traces

FretCoach gracefully handles LLM failures:

```python
try:
    recommendation = generate_ai_recommendation(user_id)
except Exception as e:
    # Error is traced in Opik
    logger.error(f"AI recommendation failed: {e}")
    # Fallback to sensible default
```

Check Opik for failed traces to see error handling in action.

---

## 🎸 Understanding the Application Flow

### User Journey: AI Practice Mode

**Step 1: User opens app → "Start AI Mode"**
- Frontend calls: `GET /ai/start-session?user_id=xxx`
- Backend traces: Fetches recent sessions from PostgreSQL
- LLM Call: Analyzes performance and recommends scale
- Opik trace: `ai-mode` tag, full recommendation reasoning

**Step 2: User accepts recommendation → "Start Practice"**
- Frontend calls: `POST /session/start` with recommended scale
- Backend starts: Real-time audio analysis (no LLM, deterministic)
- Metrics stream: WebSocket updates every 150ms

**Step 3: During practice (every 30 seconds)**
- Frontend calls: `POST /live-coach/feedback` with current metrics
- LLM Call: Generates coaching feedback based on weakest area
- Opik trace: `live-coach` tag, shows input metrics and output feedback
- Frontend displays: AI coach verbal feedback on screen

**Step 4: User ends session → "Stop Practice"**
- Frontend calls: `POST /session/end`
- Backend: Saves session to database, calculates final metrics
- Optional LLM Call: Generate session summary (if requested)
- Database: Updates `ai_practice_plans` table with execution link

**Step 5: User reviews in Web Dashboard**
- Visit fretcoach.online/dashboard
- View: Session history, metrics charts
- Chat: Ask AI coach questions about performance
- Each chat message: New Opik trace with `ai-mode` tag

---

## 🏗️ Architecture Highlights for Evaluation

### Why This Architecture is Noteworthy

**1. Separation of Deterministic and AI Workloads**
- Audio analysis runs **locally, deterministically** (no LLM)
- AI coaching runs **on-demand** when feedback is needed
- Result: Low-latency experience with observable AI enhancements

**2. Edge + Cloud Hybrid**
- Desktop app: Edge computing for real-time audio
- Web dashboard: Cloud-based analytics and planning
- Portable device: Edge computing on Raspberry Pi 5
- All sync through central PostgreSQL database

**3. Observable AI Decision Chain**
```
Historical Data (PostgreSQL)
  ↓
AI Recommendation (Opik traced)
  ↓
User Practice Session (deterministic audio analysis)
  ↓
Live AI Coaching (Opik traced, real-time)
  ↓
Session Saved to DB
  ↓
AI Analysis (Opik traced, post-session)
  ↓
Updated User Profile
```

Every AI decision is traced, showing complete decision provenance.

---

## 🔗 Important Links

### Live Demos
- **Web Dashboard:** [fretcoach.online](https://fretcoach.online)
- **GitHub Repository:** (Will be public after judging)

### Opik Resources
- **Main Project:** [FretCoach Opik Project](https://comet.com/opik/padmanabhan-r-7119/projects/019bcefc-a27c-718d-8c5f-36472d5decb2)
- **Filter by AI Mode:** Add filter `tag:ai-mode`
- **Filter by Live Coach:** Add filter `tag:live-coach`
- **Filter by User:** Add filter `metadata.user_id:your_id`

### Documentation
- **Full Docs:** Start at [index.md](index.md)
- **Quickstart:** [quickstart.md](quickstart.md)
- **Architecture:** [architecture.md](architecture.md)
- **AI Coaching Details:** [ai-coaching.md](ai-coaching.md)

---

## 💡 Evaluation Criteria Checklist

Use this to quickly assess FretCoach:

- [ ] **Opik Integration**
  - [ ] Traces visible in Opik UI
  - [ ] Proper metadata (user_id, session_id, practice_id)
  - [ ] Clear tag organization (ai-mode, live-coach)
  - [ ] Structured outputs logged correctly
  - [ ] Error cases traced

- [ ] **Real-World Value**
  - [ ] Solves genuine user problem
  - [ ] Production-ready (not just a demo)
  - [ ] Multiple deployment targets (desktop, web, edge)
  - [ ] Observable AI throughout

- [ ] **Technical Quality**
  - [ ] Clean code architecture
  - [ ] Proper separation of concerns
  - [ ] Database integration
  - [ ] Real-time audio processing
  - [ ] Multi-LLM support

- [ ] **Innovation**
  - [ ] Multi-sensory feedback (visual + verbal + ambient)
  - [ ] Real-time AI coaching during practice
  - [ ] Edge computing prototype (Raspberry Pi)
  - [ ] Adaptive recommendations based on history

- [ ] **Documentation**
  - [ ] Clear, comprehensive docs
  - [ ] Easy to understand system
  - [ ] Good code comments
  - [ ] Helpful for judges

---

## 🤔 Questions You Might Have

### Q: Can I test this without setting up locally?

**A:** Yes! Visit [fretcoach.online](https://fretcoach.online) and use the AI Coach chat. Each interaction creates traces you can review in Opik.

### Q: How do I find my traces in Opik?

**A:** Go to the [project link](https://comet.com/opik/padmanabhan-r-7119/projects/019bcefc-a27c-718d-8c5f-36472d5decb2) and filter by:
- **Tag:** `ai-mode` or `live-coach`
- **Metadata:** `user_id` (if you have one)
- **Time:** Recent traces

### Q: What makes this different from other music apps?

**A:** FretCoach is a **coach**, not a learning app. It doesn't teach you what to play—it analyzes *how* you play and provides adaptive feedback. Every AI decision is traced through Opik for full observability.

### Q: Is the Raspberry Pi device required?

**A:** No, it's a bonus prototype showing edge deployment. Core functionality works on desktop and web.

### Q: Why does audio processing not use LLMs?

**A:** Real-time audio analysis needs <10ms latency. LLMs would introduce 500ms+ delays. FretCoach uses deterministic DSP for audio and LLMs only for coaching/planning where latency is acceptable.

### Q: Can I see the actual Opik integration code?

**A:** Yes! Key files:
- `backend/api/services/ai_agent_service.py` (AI recommendations)
- `backend/api/services/live_coach_service.py` (live coaching)
- Both use `OpikTracer` with LangChain

---

## 📧 Contact

If you have questions during evaluation, the codebase and documentation should provide answers. If not, please leave feedback—we want to make this crystal clear!

---

**Navigation:**
- [← Back to Index](index.md)
- [Full Documentation →](index.md)
- [Architecture Details →](architecture.md)
- [AI Coaching System →](ai-coaching.md)
