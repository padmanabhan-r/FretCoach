# Opik Observability in FretCoach

How we integrated Opik to monitor, debug, and improve FretCoach's AI coaching features.

---

## Integration Overview

FretCoach traces **three AI coaching features** through Opik:

1. **AI Practice Recommendations** — AI Mode practice plan generation
2. **Live Session Coaching** — Real-time feedback during practice (LLM + TTS)
3. **Web Chat Agent** — Natural language queries on the dashboard

All LLM interactions are traced with LangChain's `OpikTracer`, and custom functions use the `@track` decorator.

---

## 1. AI Practice Recommendations

**File:** `backend/api/services/ai_agent_service.py`

### What We Trace

When a user starts AI Mode, we:
- Fetch their last 5 sessions from the database
- Analyze performance patterns (weakest metric)
- Generate a personalized practice plan via LLM with structured output

### Implementation

```python
from opik.integrations.langchain import OpikTracer

def get_opik_config(user_id: str, practice_id: str) -> dict:
    """Configure Opik tracing for AI recommendations"""
    tracer = OpikTracer(
        tags=["ai-mode", "practice-plan"],
        metadata={
            "user_id": user_id,
            "practice_id": practice_id
        }
    )
    return {
        "callbacks": [tracer],
        "configurable": {"thread_id": f"user-{user_id}"}
    }

# Usage with LangChain structured output
llm_with_structure = model.with_structured_output(PracticeRecommendation)
recommendation = llm_with_structure.invoke(
    [SystemMessage(content=system_prompt),
     HumanMessage(content=user_prompt)],
    config=get_opik_config(user_id, practice_id)
)
```

### Metadata Strategy

- **`user_id`** — Links traces to specific users for pattern analysis
- **`practice_id`** — UUID for each generated plan (correlates with database)
- **Thread ID** — Groups all recommendations for a single user over time

### Tags

- `"ai-mode"` — All AI practice recommendations
- `"practice-plan"` — Specifically plan generation (vs other AI features)

---

## 2. Live Session Coaching (LLM + TTS)

**File:** `backend/api/services/live_coach_service.py`

### What We Trace

During practice sessions (every 30s):
- LLM generates coaching feedback based on current metrics
- TTS converts feedback to speech using `gpt-4o-mini-tts`
- Both operations are traced as separate spans

### Implementation

**LLM Coaching:**
```python
def get_opik_config(session_id: str, trace_name: str) -> dict:
    tracer = OpikTracer(
        tags=["live-coach", trace_name],
        metadata={"session_id": session_id}
    )
    return {
        "callbacks": [tracer],
        "configurable": {"thread_id": f"session-{session_id}"}
    }

# Every 30s during practice
opik_config = get_opik_config(session_id, "live-feedback")
response = await live_coach_model.ainvoke(
    [
        {"role": "system", "content": COACHING_SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ],
    config=opik_config
)
```

**TTS Generation:**
```python
from opik import track

@track(name="live-coach-tts", tags=["tts", "live-coach"])
async def generate_and_play_tts(
    feedback_text: str,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate and play TTS audio.
    Traced separately to monitor TTS latency and failures.
    """
    player = get_audio_player()
    player.stop()  # Prevent overlap

    async with openai_client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="onyx",
        input=feedback_text,
        instructions="Speak in a direct, encouraging tone...",
        response_format="pcm",
    ) as response:
        await player.play(response)

    return {"status": "played", "model": "gpt-4o-mini-tts"}
```

### Why Separate Traces for TTS?

We trace TTS separately (not as a nested span) because:
- **TTS failures shouldn't fail the LLM trace** — If TTS breaks, we still want the text feedback
- **Independent latency monitoring** — TTS latency (2-3s) vs LLM latency (1-2s)
- **Different failure modes** — Audio playback issues vs LLM errors

### Metadata Strategy

- **`session_id`** — Links all traces from a single practice session
- **Thread ID** — Groups all live coaching calls within one session (see conversation flow)

### Tags

- `"live-coach"` — All live coaching features
- `"live-feedback"` — LLM-generated coaching text
- `"tts"` — TTS audio generation
- `"session-summary"` — End-of-session summary (different prompt)

---

## 3. Web Chat Agent (Text-to-SQL)

**File:** `web/web-backend/routers/chat.py`

### What We Trace

Users ask natural language questions:
- "What should I practice next?"
- "Show me my progress trends"
- "Compare my latest session to my average"

We trace:
- Intent detection
- Database queries triggered
- LLM response generation
- Multi-turn conversations

### Implementation

```python
def invoke_with_fallback(messages, thread_id: str):
    """
    Try Gemini, fall back to MiniMax on rate limits.
    Both use OpikTracer for conversation tracking.
    """
    tracer = OpikTracer(
        tags=["ai-coach", "web-chat"],
        metadata={"thread_id": thread_id}
    )
    config = {"callbacks": [tracer]}

    if thread_id:
        config["configurable"] = {"thread_id": thread_id}

    try:
        return gemini_model.invoke(messages, config=config)
    except Exception as e:
        if "RESOURCE_EXHAUSTED" in str(e):
            # Fallback traced with same config
            return minimax_model.invoke(messages, config=config)
        raise
```

### Metadata Strategy

- **`thread_id`** — Chat conversation ID (groups all messages from one chat session)
- **`user_id`** — Embedded in system prompt context (visible in trace)

### Tags

- `"ai-coach"` — All AI coaching features
- `"web-chat"` — Specifically web dashboard chat (vs desktop app)
- `"practice-plan"` — When user asks for practice recommendations

---

## Thread Hierarchy Example

Here's how Opik groups a typical practice session:

```
🧵 Thread: session-abc123
│
├─ 📊 Trace: Live Coaching Feedback (timestamp: 00:30)
│   ├─ LLM Call: gpt-4o-mini (1.2s, 120 tokens)
│   ├─ Tags: ["live-coach", "live-feedback"]
│   └─ Output: "Your timing is drifting—lock in with the beat."
│
├─ 📊 Trace: TTS Generation (timestamp: 00:32)
│   ├─ OpenAI TTS: gpt-4o-mini-tts (2.1s)
│   ├─ Tags: ["tts", "live-coach"]
│   └─ Status: played
│
├─ 📊 Trace: Live Coaching Feedback (timestamp: 01:00)
│   ├─ LLM Call: gpt-4o-mini (1.3s, 135 tokens)
│   └─ Output: "Pitch accuracy is solid—focus on reducing string noise."
│
└─ 📊 Trace: Session Summary (timestamp: session end)
    ├─ LLM Call: gpt-4o-mini (1.5s, 180 tokens)
    ├─ Tags: ["live-coach", "session-summary"]
    └─ Output: "Great session! Your pitch improved..."
```

**Thread ID** (`session-abc123`) groups all traces chronologically, showing the coaching conversation flow.

---

## Insights We've Gained

### 1. Prompt Optimization

**Initial prompt:** 150+ tokens, verbose instructions
**Opik trace:** LLM responses were too long (200+ tokens), taking 2-3s
**Action:** Reduced prompt to "1 sentence maximum"
**Result:** 50% faster responses (1-1.5s), more focused feedback

### 2. TTS Latency Bottleneck

**Opik revealed:** TTS taking 3-4s on some calls
**Investigation:** Audio overlap causing queuing delays
**Action:** Implemented singleton player with `stop()` before new audio
**Result:** Consistent 2s TTS latency, no crackling

### 3. Fallback Model Usage

**Gemini rate limits:** ~15% of web chat requests
**Opik traces:** Fallback to MiniMax working seamlessly
**Insight:** Users don't notice the switch (quality maintained)
**Action:** Kept hybrid approach, added rate limit monitoring

### 4. Token Usage Patterns

**AI Mode:** 300-400 tokens per recommendation (includes context)
**Live Coach:** 100-150 tokens per feedback call (brief, focused)
**Web Chat:** 200-500 tokens (conversational, varies by question)

**Cost optimization:** Live coaching uses `gpt-4o-mini` (cheap, fast), not Opus

---

## Tagging Strategy

Our tagging hierarchy enables efficient filtering:

| Tag | Purpose | Example Filters |
|-----|---------|----------------|
| `"ai-mode"` | AI practice recommendations | Filter all practice plan generations |
| `"live-coach"` | Live session coaching | Filter all real-time coaching traces |
| `"web-chat"` | Web dashboard chat | Filter web vs desktop interactions |
| `"tts"` | TTS audio generation | Monitor TTS latency and failures |
| `"session-summary"` | End-of-session summaries | Different prompt template than live feedback |
| `"practice-plan"` | Practice plan generation | Cross-feature (AI Mode + Web Chat) |

**Multi-tag filtering example:**
`tags:["live-coach"] AND tags:["tts"]` → All TTS calls during live coaching

---

## Graceful Degradation

Opik is **optional** in FretCoach. If unavailable:

```python
# backend/api/services/live_coach_service.py
try:
    from opik.integrations.langchain import OpikTracer
    from opik import track
    OPIK_ENABLED = True
except ImportError:
    OpikTracer = None
    track = lambda **kwargs: lambda f: f  # No-op decorator
    OPIK_ENABLED = False

def get_opik_config(session_id: str, trace_name: str) -> dict:
    if not OPIK_ENABLED or not OpikTracer:
        return {}  # No tracing, system continues normally

    tracer = OpikTracer(...)
    return {"callbacks": [tracer]}
```

**Result:** System functions identically with or without Opik—no crashes, no errors.

---

## Configuration

**Environment variables:**

```env
# backend/.env or web/web-backend/.env
OPIK_API_KEY=your_opik_api_key
OPIK_WORKSPACE=your_workspace  # Optional
```

**No API key?** Tracing is silently disabled, no impact on functionality.

---

## Key Decisions

### Why OpikTracer + @track?

- **`OpikTracer`** (LangChain integration): Automatic prompt/response logging, works with structured outputs
- **`@track`** (function decorator): Trace custom operations like TTS, database queries

### Why Separate TTS Traces?

- Independent failure tracking (TTS can fail without breaking LLM response)
- Separate latency monitoring (TTS is the bottleneck, not LLM)

### Why Thread IDs?

- **Session threads** (`session-{id}`): See live coaching evolution over 20-minute practice
- **User threads** (`user-{id}`): Track AI recommendations across multiple days
- **Chat threads** (`chat-{id}`): Multi-turn conversations in web dashboard

---

## Live Traces

**Opik Project:** [FretCoach Traces](https://comet.com/opik/padmanabhan-r-7119/projects/019bcefc-a27c-718d-8c5f-36472d5decb2)

**Useful filters:**
- `tag:ai-mode` — AI practice plan generation
- `tag:live-coach` — Real-time coaching during sessions
- `tag:tts` — TTS audio generation
- `tag:web-chat` — Web dashboard conversations

---

**Navigation:**
- [← Back to Index](index.md)
- [AI Coach Agent Engine →](ai-coach-agent-engine.md)
- [Audio Analysis Agent Engine →](audio-analysis-agent-engine.md)
