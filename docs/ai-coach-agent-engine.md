# AI Coach Agent Engine - The Slow Loop

LLM-powered coaching system that provides strategic guidance and conversational support. The intelligent "Slow Brain" of FretCoach's dual-brain architecture.

![FretCoach Brain Architecture](assets/images/FretCoach%20Brain.png)

---

## Overview

The **AI Coach Agent** is FretCoach's strategic coaching layer—an LLM-powered system that analyzes session history, provides live feedback, and offers conversational guidance.

**Design Philosophy:** Strategic improvement requires **context**. The AI coach operates on a 1-3 second timescale, analyzing patterns and providing personalized recommendations.

---

## Dual-Brain Architecture

```
┌─────────────────────────────────────┐
│  AUDIO ANALYSIS AGENT (Fast Loop)  │
│  • Local processing (no cloud)     │
│  • <300ms latency                  │
│  • Deterministic algorithms        │
│  • 4 metric evaluation             │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│      AI COACH (Slow Loop)          │
│  • Cloud LLM APIs                  │
│  • 1-3 second latency              │
│  • Strategic coaching              │
└─────────────────────────────────────┘
```

**Why separation?**
- **Speed:** Real-time analysis can't wait for LLM calls
- **Cost:** Running every analysis via LLM would be expensive
- **Reliability:** Core functionality works offline
- **Specialization:** Each brain optimized for its role

---

## Three AI Coaching Features

### 1. Practice Recommendations (AI Mode)

**Purpose:** Analyze history and recommend optimal next session.

**Flow:**
1. User selects "AI Mode" in Studio
2. System fetches previous sessions from database
3. Calculates average metrics, identifies weakest area
4. LLM generates structured recommendation (scale, focus area, difficulty)
5. User reviews and accepts to start session

**LLM Input:**
- Recent session data (scores, scales, durations)
- Average metrics and identified weakness
- Practice patterns

**LLM Output (Pydantic structured):**
```python
{
  "scale_name": "C Major",
  "scale_type": "pentatonic",
  "focus_area": "timing",
  "reasoning": "Your timing stability is consistently low...",
  "strictness": 0.5,
  "sensitivity": 0.5
}
```

**Models:** GPT-4o-mini (Studio), Gemini 3 Flash Preview (Hub)

**Tracing:** Opik tags: `ai-mode`, `practice-recommendation`

**Location:** `backend/api/services/ai_agent_service.py`

---

### 2. Live Session Coaching

**Purpose:** Real-time corrective feedback during practice.

**Flow:**
1. Session starts
2. Every 30 seconds: Frontend sends current metrics to backend
3. Backend identifies weakest metric
4. LLM generates brief, specific coaching feedback
5. TTS converts text to speech (OpenAI gpt-4o-mini-tts)
6. Feedback spoken aloud + displayed in UI

**LLM Input:**
```
Session: A Minor Pentatonic, 2m 30s
Pitch Accuracy: 78%
Scale Conformity: 82%
Timing Stability: 23% ← Weakest
```

**LLM Output:**
> "Your timing is very inconsistent (23%). Focus on playing each note at exactly the same interval—try counting '1-2-3-4' out loud."

**System Prompt Key Points:**
- Be CORRECTIVE, not generic praise
- Reference specific metrics
- Give ONE actionable technique
- Maximum 2 sentences

**TTS Implementation:**
- Voice: "onyx"
- Streaming response format for low latency
- Singleton player prevents audio overlap
- Coaching-specific voice instructions

**Models:** GPT-4o-mini (text), GPT-4o-mini-tts (speech)

**Tracing:** Opik tags: `live-coach`, `tts`

**Location:** `backend/api/services/live_coach_service.py`

---

### 3. Conversational Chat (Hub Dashboard)

**Purpose:** Natural language guidance using practice data.

**Flow:**
1. User visits Hub → AI Coach tab
2. Types question: "What should I practice next?"
3. Backend detects intent via keyword matching
4. Calls appropriate database query function
5. LLM formats results conversationally
6. Returns response with optional charts

**Example Questions:**
- "What should I practice next?"
- "Show me my progress trends"
- "Compare my latest session to my average"
- "Which scales have I practiced?"

**Architecture: Hybrid Text-to-SQL Agent**

Unlike pure text-to-SQL (where LLM generates raw SQL), this uses **intent-based tool selection** with **predefined queries**:

```python
# Intent detection via keywords
if any(word in message for word in ["progress", "trend", "chart"]):
    chart_data = get_performance_chart_data(user_id)

elif any(word in message for word in ["practice", "recommend", "suggest"]):
    chart_data = generate_practice_recommendation(user_id)
```

**Why Hybrid?**
- ✅ Robust: No malformed SQL queries
- ✅ Secure: No SQL injection risk
- ✅ Fast: Optimized queries, not generated
- ✅ Natural: LLM provides conversational responses

**Database Tools:**
- `get_user_practice_data()` — Aggregated statistics
- `get_performance_chart_data()` — Trend charts
- `get_comparison_chart_data()` — Session comparisons
- `generate_practice_recommendation()` — Next session suggestion

**Models:** Gemini 3 Flash Preview (primary), Minimax (MiniMax-M2.1) fallback on rate limits

**Tracing:** Opik tags: `web-chat`, `ai-coach`

**Location:** `web/web-backend/routers/chat.py`

---

## LLM Providers

FretCoach supports multiple providers, all traced via Opik:

### OpenAI GPT-4o-mini
- **Use:** Studio live coaching, TTS, practice recommendations
- **Pros:** Fast, reliable, good reasoning
- **Cost:** ~$0.15 per 1M input tokens

### Google Gemini 3 Flash Preview
- **Use:** Hub AI chat (primary)
- **Model:** `gemini-3-flash-preview`
- **Pros:** Very fast, free tier available
- **Cost:** Free tier available

### Minimax (MiniMax-M2.1)
- **Use:** Hub AI chat (fallback on rate limits)
- **Model:** MiniMax-M2.1
- **Pros:** Reliable fallback, multilingual support

### Provider Selection

**Studio backend:** GPT-4o-mini (hardcoded)

**Hub backend:** Gemini 3 Flash Preview with fallback:
```bash
# .env
USE_OPENAI_MODEL=true   # Switch to GPT-4o-mini
MINIMAX_API_KEY=...     # Automatic fallback
```

**Fallback logic:**
```python
try:
    return gemini_model.invoke(messages)
except Exception as e:
    if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
        return minimax_model.invoke(messages)
```

---

## Prompt Engineering

### Design Principles

1. **Specificity** — Reference exact metrics and data
2. **Actionability** — Outputs immediately usable
3. **Brevity** — Live coaching limited to 1-2 sentences
4. **Structured** — Use Pydantic models for type safety
5. **Context** — Include relevant session history

### System Prompt Strategy

**AI Mode Recommendations:**
```
You are an expert guitar coach analyzing practice data.

Context: User has practiced {n} times
Average scores: Pitch {x}%, Scale {y}%, Timing {z}%
Weakest area: {area}

Recommend optimal scale and settings to address weakness.

Rules:
- Focus on improvement, not variety
- Timing weak → natural scales (more notes = rhythm practice)
- Pitch weak → pentatonic (fewer notes = accuracy focus)
- Scale conformity weak → same scale again
```

**Live Coaching:**
```
You are a direct, practical guitar coach.

Current: {scale} for {time}
Metrics: Pitch {p}%, Scale {s}%, Timing {t}%
Weakest: {metric} at {score}%

Provide ONE corrective instruction.

Requirements:
- Be direct and specific
- Reference the metric
- Give actionable technique NOW
- Maximum 2 sentences
- No generic praise
```

**Hub Chat:**
```
You are an AI guitar coach with access to user's practice data.

User Data:
- Total sessions: {n}
- Average metrics: {scores}
- Weakest area: {area}
- Recent sessions: {sessions}

Provide personalized coaching advice based on this data.
```

---

## Opik Observability

All LLM calls traced via Comet Opik integration.

**Configuration:**
```python
from opik.integrations.langchain import OpikTracer

tracer = OpikTracer(
    tags=["fretcoach", "ai-mode"],
    metadata={"user_id": user_id, "session_id": session_id}
)

config = {"callbacks": [tracer]}
response = llm.invoke(messages, config=config)
```

**Trace Tags:**
- `ai-mode` — Practice recommendations
- `live-coach` — Real-time feedback
- `web-chat` — Hub conversations
- `tts` — Text-to-speech generation

**Trace Metadata:**
- `user_id` — User identifier
- `session_id` — Session ID
- `practice_id` — Practice plan ID
- `thread_id` — Conversation thread

**Dashboard:** [FretCoach Opik Project](https://comet.com/opik/padmanabhan-r-7119/projects/019bcefc-a27c-718d-8c5f-36472d5decb2)

**Filter Examples:**
- `tag:ai-mode` — All recommendations
- `tag:live-coach` — Real-time coaching only
- `metadata.user_id:paddy` — Specific user

> **Details:** [Opik Observability](opik-observability.md)

---

## Performance

**Latency Targets:**
- AI recommendations: <2s (acceptable)
- Live coaching: <1s (critical for real-time feel)
- Chat responses: <3s (acceptable for conversational)

**Optimization Strategies:**
- Model selection: GPT-4o-mini and Gemini Flash optimized for speed
- Token limits: Live coaching max_tokens=150, recommendations max_tokens=500
- Caching: Pending plans cached 24 hours, recent sessions cached per user
- Async processing: Coaching doesn't block audio processing

---

## Error Handling

**LLM Failures:**
```python
try:
    recommendation = llm.invoke(prompt, config=opik_config)
except Exception as e:
    logger.error(f"LLM call failed: {e}")
    # Fallback to sensible default
    recommendation = {
        "scale_name": "C Major",
        "reasoning": "Unable to generate custom recommendation. Starting with C Major.",
        "strictness": 0.5
    }
```

**Rate Limiting:**
- Automatic fallback to Minimax (MiniMax-M2.1) on Gemini rate limits
- Retry with exponential backoff
- User-friendly error messages

**Opik Failures:**
- Tracing is **non-blocking**
- App continues if tracing fails
- Graceful degradation

---

## Code Structure

**Location:** Multiple services

**Studio Backend:**
- `backend/api/services/ai_agent_service.py` — Practice recommendations
- `backend/api/services/live_coach_service.py` — Real-time coaching

**Hub Backend:**
- `web/web-backend/routers/chat.py` — Conversational chat
- `web/web-backend/langgraph_workflow.py` — Agent workflow

**Shared:**
- Opik configuration utilities
- Database query functions
- Prompt templates

---

## Technical Details

### Practice Recommendation Flow

1. Fetch sessions: `SELECT * FROM fretcoach.sessions WHERE user_id = ? ORDER BY start_timestamp DESC LIMIT 5`
2. Calculate averages and identify weakest metric
3. Build system prompt with context
4. LLM generates structured recommendation (Pydantic)
5. Save to `ai_practice_plans` table
6. Return to user with Opik tracing

### Live Coaching Flow

1. Frontend sends metrics every 30 seconds
2. Identify weakest metric
3. Build coaching prompt with session context
4. LLM generates brief feedback (max 150 tokens)
5. TTS converts to speech with coaching voice instructions
6. Play audio + display text
7. Opik traces both text generation and TTS

### Hub Chat Flow

1. User message received
2. Intent detection via keywords
3. Execute appropriate database query
4. Build system prompt with user data
5. LLM generates conversational response
6. Add chart data if applicable
7. Return response + optional chart

---

## Offline Capability

AI features require cloud connectivity:

❌ **Cloud dependent:**
- All AI coaching features need LLM API access
- TTS requires OpenAI API

✅ **Degraded mode:**
- Studio can run in Manual Mode (no AI)
- Audio analysis continues offline
- Sessions saved to local queue, sync later

---

**Navigation:**
- [← Audio Analysis Agent Engine](audio-analysis-agent-engine.md)
- [Environment Setup →](environment-setup.md)
- [Back to Index](index.md)
