# Opik Observability in FretCoach

## Overview

FretCoach uses **Comet Opik** for LLM observability and tracing. Opik provides comprehensive monitoring of all AI interactions, enabling debugging, performance analysis, and quality tracking across the system.

## What is Opik?

Opik is an open-source LLM observability platform that helps track, debug, and improve AI applications. It integrates seamlessly with LangChain and provides detailed traces of LLM calls, including prompts, responses, latency, and cost.

**Official Documentation**: https://www.comet.com/docs/opik/

---

## Core Concepts

### 1. Traces
A **trace** represents a complete user interaction or workflow. In FretCoach, a trace typically corresponds to:
- A single practice session
- A single AI coaching feedback request
- A complete conversation with the AI practice planner

**Example**: When a user gets live coaching feedback, Opik creates a trace that includes:
- The metrics passed to the LLM
- The prompt template used
- The LLM response
- Latency and token usage

### 2. Spans
A **span** represents a single operation within a trace. Spans can be nested to show hierarchical operations.

**Example**: A practice session trace might contain spans for:
- LLM call for live coaching feedback
- TTS generation for audio playback
- Database write for session logging

### 3. Threads
A **thread** groups related traces together over time. In FretCoach, threads track:
- All interactions within a single practice session
- A multi-turn conversation with the AI coach in FretCoach Hub
- A sequence of AI recommendations across sessions

**Threading enables context tracking**: You can see how a user's interactions evolve over time and how the AI's responses adapt.

### 4. Tags
**Tags** are labels applied to traces and spans for filtering and organization.

FretCoach uses tags like:
- `"live-coach"` — Live coaching feedback during practice
- `"session-summary"` — End-of-session summary generation
- `"practice-planning"` — AI practice plan generation
- `"tts"` — Text-to-speech audio generation

---

## How FretCoach Uses Opik

### 1. Live Coaching Feedback

**File**: `backend/api/services/live_coach_service.py`

```python
from opik.integrations.langchain import OpikTracer

def get_opik_config(session_id: str, trace_name: str) -> dict:
    """Create Opik config for LangChain calls tied to session_id"""
    tracer = OpikTracer(
        tags=["live-coach", trace_name],
        metadata={"session_id": session_id}
    )
    return {
        "callbacks": [tracer],
        "configurable": {"thread_id": f"session-{session_id}"}
    }

# Usage in live coaching
opik_config = get_opik_config(session_id, "live-feedback")
response = await live_coach_model.ainvoke(
    [
        {"role": "system", "content": COACHING_SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ],
    config=opik_config
)
```

**What this does**:
- Creates a trace for each live coaching request
- Tags it with `"live-coach"` and `"live-feedback"`
- Associates it with the session ID via metadata
- Groups all feedback from the same session into a **thread** using `thread_id`

### 2. TTS Audio Generation

**File**: `backend/api/services/live_coach_service.py`

```python
from opik import track

@track(name="live-coach-tts", tags=["tts", "live-coach"])
async def generate_and_play_tts(
    feedback_text: str,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """Generate and play TTS audio for coaching feedback."""
    # TTS generation logic...
    pass
```

**What this does**:
- Creates a **span** for TTS generation
- Tags it with `"tts"` and `"live-coach"`
- Tracks latency and success/failure status
- Links to the parent trace (live coaching feedback)

### 3. AI Practice Planning

**File**: `web/web-backend/routers/chat.py`

```python
from opik.integrations.langchain import OpikTracer

opik_tracer = OpikTracer(
    tags=["fretcoach-hub", "practice-planning"],
    metadata={
        "user_id": user_id,
        "conversation_length": len(messages)
    }
)

config = {
    "callbacks": [opik_tracer],
    "configurable": {"thread_id": f"user-{user_id}"}
}

response = await chain.ainvoke({"messages": messages}, config=config)
```

**What this does**:
- Creates a trace for each chat message
- Tags it with `"fretcoach-hub"` and `"practice-planning"`
- Groups all messages from the same user into a **thread**
- Tracks conversation length and user context

---

## Trace Hierarchy Example

Here's how Opik structures a typical FretCoach practice session:

```
📊 Trace: Practice Session (session-abc123)
  │
  ├─ 🔷 Span: Live Coaching Feedback (15s elapsed)
  │   ├─ LLM Call (gpt-4o-mini) - 1.2s
  │   └─ Tags: ["live-coach", "live-feedback"]
  │
  ├─ 🔷 Span: TTS Generation (2.1s elapsed)
  │   ├─ OpenAI TTS (gpt-4o-mini-tts) - 2.0s
  │   └─ Tags: ["tts", "live-coach"]
  │
  ├─ 🔷 Span: Live Coaching Feedback (15s elapsed)
  │   ├─ LLM Call (gpt-4o-mini) - 1.3s
  │   └─ Tags: ["live-coach", "live-feedback"]
  │
  └─ 🔷 Span: Session Summary (session end)
      ├─ LLM Call (gpt-4o-mini) - 1.5s
      └─ Tags: ["live-coach", "session-summary"]

🧵 Thread: session-abc123
   Groups all traces from this practice session
```

---

## Why We Use Opik

### 1. Debugging AI Behavior
- **See exact prompts and responses**: When users report issues with AI coaching, we can inspect the exact prompts and model responses
- **Track context**: Thread grouping shows how AI responses evolve within a session

### 2. Performance Monitoring
- **Latency tracking**: Identify slow LLM calls or TTS generation
- **Token usage**: Monitor API costs per session, per user, per feature
- **Error tracking**: Catch failed LLM calls or timeouts

### 3. Quality Assurance
- **Response quality**: Review AI coaching feedback for relevance and accuracy
- **Prompt engineering**: A/B test different prompt templates by comparing trace outputs
- **Model comparison**: Compare gpt-4o-mini vs other models for cost/quality trade-offs

### 4. User Analytics
- **Feature usage**: Track how often users enable live coaching vs practice planning
- **Session patterns**: Understand typical practice session lengths and AI interaction frequency
- **Retention**: Identify which AI features correlate with user retention

---

## Configuration

### Environment Setup

Add to `backend/.env` or `web/web-backend/.env`:

```env
OPIK_API_KEY=your_opik_api_key
OPIK_WORKSPACE=your_workspace_name  # Optional
```

### Enabling/Disabling Opik

Opik is **gracefully optional** in FretCoach. If the API key is not set or Opik is unavailable:
- The system continues to function normally
- Tracing is silently disabled
- No errors are raised

**File**: `backend/api/services/live_coach_service.py`

```python
try:
    from opik.integrations.langchain import OpikTracer
    from opik import track
    OPIK_ENABLED = True
except ImportError:
    OpikTracer = None
    track = lambda **kwargs: lambda f: f  # No-op decorator
    OPIK_ENABLED = False
```

---

## Best Practices

### 1. Always Use Meaningful Tags
Tags enable filtering and analysis in the Opik dashboard.

**Good**:
```python
tags=["live-coach", "session-summary"]
```

**Bad**:
```python
tags=["misc", "test"]
```

### 2. Include Metadata for Context
Metadata helps correlate traces with user sessions and application state.

**Good**:
```python
metadata={
    "session_id": session_id,
    "scale_name": scale_name,
    "user_id": user_id
}
```

**Bad**:
```python
metadata={}
```

### 3. Use Threads for Multi-Turn Interactions
Thread IDs group related traces together.

**Good**:
```python
config = {
    "configurable": {"thread_id": f"session-{session_id}"}
}
```

**Bad**:
```python
config = {}  # Each trace is isolated
```

### 4. Name Traces Descriptively
Trace names appear in the Opik dashboard. Make them searchable and clear.

**Good**:
```python
@track(name="live-coach-tts", tags=["tts"])
```

**Bad**:
```python
@track(name="func1", tags=[])
```

---

## Opik Dashboard

Access the Opik dashboard at: https://www.comet.com/opik

### Key Features

1. **Traces View**: Browse all LLM calls, filter by tags, search by session ID
2. **Threads View**: See conversation flows and multi-turn interactions
3. **Analytics**: Token usage, latency distributions, error rates
4. **Prompt Library**: Save and version prompt templates for experimentation

---

## Future Enhancements

### 1. Evaluation Datasets
Opik supports creating evaluation datasets to test prompt changes:
- Capture real user interactions as test cases
- Run A/B tests on prompt variations
- Measure response quality with automated metrics

### 2. Custom Metrics
Track FretCoach-specific metrics like:
- Coaching relevance score (manual annotation)
- TTS audio quality ratings
- Practice plan adherence rates

### 3. Multi-Model Comparison
Compare different LLM providers (OpenAI, Gemini, DeepSeek) for:
- Response quality
- Latency
- Cost per session

---

## Summary

| Concept | FretCoach Usage | Example |
|---------|----------------|---------|
| **Traces** | Complete interactions (session, feedback request) | Single live coaching feedback call |
| **Spans** | Individual operations (LLM call, TTS generation) | TTS audio generation within a feedback request |
| **Threads** | Grouped interactions (session, conversation) | All feedback from one practice session |
| **Tags** | Feature labels for filtering | `["live-coach", "tts", "practice-planning"]` |

**Key Principle**: Opik provides observability into FretCoach's AI brain—enabling debugging, performance optimization, and continuous improvement of the coaching experience.

---

**Navigation:**
- [← Back to Index](index.md)
- [Architecture Overview →](architecture.md)
