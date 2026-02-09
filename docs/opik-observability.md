# Opik Observability in FretCoach

How we integrated Comet Opik to monitor, debug, and optimize FretCoach's AI coaching features in production.

---

## Overview

FretCoach uses **Comet Opik** for comprehensive LLM observability across three AI coaching features:

1. **AI Practice Recommendations** — Personalized practice plans generated via LangChain structured output
2. **Live Session Coaching** — Real-time feedback during practice (LLM text generation + TTS audio)
3. **Web Chat Agent** — Natural language queries with LangGraph-based text-to-SQL agent

All LLM interactions are traced using LangChain's `OpikTracer`, custom functions use the `@track` decorator, and LangGraph workflows are visualized with agent graphs.

---

## Integration Architecture

### 1. AI Practice Recommendations

**Location:** `backend/api/services/ai_agent_service.py`

When users start AI Mode, the system:
- Fetches their last 5 practice sessions from PostgreSQL
- Analyzes performance patterns to identify the weakest metric
- Generates a structured practice plan via GPT-4o-mini with LangChain structured output

**Tracing approach:**
- Uses `OpikTracer` as LangChain callback
- Tags: `ai-mode`, `practice-plan`
- Metadata: `user_id`, `practice_id` (links traces to database records)
- Thread ID: `user-{user_id}` (groups recommendations over time)

---

### 2. Live Session Coaching

**Location:** `backend/api/services/live_coach_service.py`

During practice sessions, the system provides coaching feedback every 30 seconds:
- **LLM generates text feedback** based on current performance metrics
- **TTS converts text to speech** using `gpt-4o-mini-tts`
- Both operations are **traced separately** for independent failure tracking

**Why separate TTS traces?**
- TTS failures shouldn't break LLM text generation
- Independent latency monitoring (TTS is the bottleneck: 2-3s vs LLM: 1-2s)
- Different failure modes (audio playback vs LLM errors)

**Tracing approach:**
- LLM calls use `OpikTracer` with LangChain
- TTS uses `@track` decorator for custom function tracing
- Tags: `live-coach`, `live-feedback`, `tts`
- Metadata: `session_id` (links all traces from one practice session)
- Thread ID: `session-{session_id}` (shows coaching conversation flow)

---

### 3. Web Chat Agent (LangGraph)

**Location:** `web/web-backend/routers/chat_langgraph.py`

The web dashboard features an AI coach chatbot that answers natural language questions about practice data:
- "What should I practice next?"
- "Show me my progress trends"
- "How did my timing improve this week?"

**Agent architecture:**
- Built with **LangGraph** for multi-step reasoning
- Tools: `execute_sql_query`, `get_database_schema`, `generate_practice_plan`
- Fallback: Gemini 2.5 Flash → Minimax Claude (on rate limits)

**Tracing approach:**
- LangGraph workflow traced via `OpikTracer`
- Agent graph visualization enabled with `workflow.get_graph(xray=True)`
- Tags: `ai-coach`, `web-chat`, `practice-plan`
- Metadata: `thread_id` (conversation ID), `user_id`
- Shows full agent reasoning path: agent → tool calls → decision nodes → response

---

## Tagging Strategy

Our hierarchical tag structure enables efficient filtering and analysis:

| Tag | Purpose | Applied To |
|-----|---------|------------|
| `ai-mode` | AI practice recommendations | Practice plan generation |
| `live-coach` | Live session coaching | Real-time feedback during practice |
| `web-chat` | Web dashboard chat | Chatbot interactions |
| `tts` | TTS audio generation | Speech synthesis operations |
| `practice-plan` | Practice plan generation | Cross-feature (AI Mode + Web Chat) |
| `live-feedback` | Live coaching text | LLM responses during sessions |

**Example filters:**
- `tag:live-coach AND tag:tts` → All TTS calls during live coaching
- `tag:web-chat AND tag:practice-plan` → Practice plans requested via chat

---

## Thread Management

Threads group related traces chronologically, enabling conversation flow analysis:

**Thread naming conventions:**
- `user-{user_id}` → AI practice recommendations across multiple sessions
- `session-{session_id}` → Live coaching within a single practice session
- `hub-aicoach-chat-{timestamp}` → Web dashboard chat conversations

**Example session thread:**
```
🧵 Thread: session-abc123
│
├─ Trace: Live Coaching (00:30) → "Your timing is drifting—lock in with the beat"
├─ Trace: TTS Generation (00:32) → Audio playback (2.1s)
├─ Trace: Live Coaching (01:00) → "Pitch accuracy is solid—focus on reducing string noise"
└─ Trace: Session Summary (end) → "Great session! Your pitch improved..."
```

---

## Key Insights from Production

### 1. Prompt Optimization
- **Initial:** 150+ token prompts → 200+ token responses (2-3s latency)
- **Opik revealed:** Verbose outputs slowing live feedback
- **Action:** Reduced to "1 sentence maximum" constraint
- **Result:** 50% faster responses (1-1.5s), more focused feedback

### 2. TTS Latency Bottleneck
- **Opik traces showed:** TTS taking 3-4s on some calls
- **Root cause:** Audio overlap causing queuing delays
- **Action:** Implemented singleton player with `stop()` before new audio
- **Result:** Consistent 2s TTS latency, eliminated crackling

### 3. Fallback Model Monitoring
- **Gemini rate limits:** ~15% of web chat requests
- **Opik visibility:** Seamless fallback to Minimax Claude
- **Insight:** Users don't notice the switch (quality maintained)
- **Action:** Kept hybrid approach, added rate limit monitoring

### 4. Token Usage Patterns
- **AI Mode:** 300-400 tokens per recommendation (includes context)
- **Live Coach:** 100-150 tokens per feedback (brief, focused)
- **Web Chat:** 200-500 tokens (conversational, varies by question)

**Cost optimization:** Live coaching uses `gpt-4o-mini` (cheap, fast), not larger models

---

## Production Features Implemented

Beyond basic tracing, FretCoach leverages advanced Opik features:

- **Agent Graph Visualization** — LangGraph execution flow with tool calls and decision nodes
- **Annotation Queues** — Manual quality review of LLM responses
- **Datasets & Prompts** — Versioned prompt templates for experiments
- **Experiments** — A/B testing prompt variations with custom metrics
- **Optimization Studio** — Systematic prompt refinement with side-by-side comparison
- **Online Evaluation** — Automated quality scoring with custom LLM judges
- **Production Dashboard** — Real-time monitoring with token usage, latency, and error rates
- **Alerts** — Notifications for rate limits, failures, and quality degradation

> **For detailed Opik usage with screenshots and implementation details, see:** [opik/opik-usage.md](../opik/opik-usage.md)

---

## Graceful Degradation

Opik is **optional** in FretCoach. If API keys are missing or Opik is unavailable:
- System continues functioning identically
- No crashes, no errors
- Tracing is silently disabled

Implementation uses try-except import pattern with no-op fallbacks for decorators and callbacks.

---

## Configuration

**Environment variables:**

```env
# backend/.env or web/web-backend/.env
OPIK_API_KEY=your_opik_api_key
OPIK_WORKSPACE=your_workspace_name
OPIK_PROJECT_NAME=FretCoach
OPIK_URL_OVERRIDE=https://www.comet.com/opik/api
```

**No API key?** Tracing is disabled, no impact on functionality.

---

## Live Workspace

**Workspace:** [FretCoach Opik Workspace](https://www.comet.com/opik/padmanabhan-r-7119/home)

**Projects:**
- `FretCoach` — Desktop app (AI Mode, Live Coaching)
- `FretCoach-Hub` — Web dashboard (Chat Agent)

**Production Dashboard:** [View Dashboard](https://www.comet.com/opik/padmanabhan-r-7119/dashboards/019c0358-6adc-71f9-a73b-b18f0b20679d)

---

**Navigation:**
- [← Environment Setup](environment-setup.md)
- [AI Coach Agent Engine →](ai-coach-agent-engine.md)
- [Audio Analysis Agent Engine →](audio-analysis-agent-engine.md)
- [Back to Index](index.md)
