# AI Coaching System

Deep dive into FretCoach's intelligent coaching capabilities powered by LLMs and Comet Opik.

---

## Overview

FretCoach uses Large Language Models (LLMs) to provide three types of AI-powered coaching:

1. **Practice Recommendations** — Analyzing history to suggest what to practice next
2. **Live Session Coaching** — Real-time feedback during active practice
3. **Conversational Chat** — Discussion-based guidance via web dashboard

All AI interactions are traced through **Comet Opik** for observability, debugging, and improvement.

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                User Practice History                     │
│              (PostgreSQL fretcoach.sessions)             │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│              AI Agent Service                            │
│  ──────────────────────────────────────────────────────  │
│                                                          │
│  1. Fetch Recent Sessions (SQL Query)                    │
│     ↓                                                    │
│  2. Analyze Performance Patterns                         │
│     ↓                                                    │
│  3. LLM Call (OpenAI/Gemini/Deepseek/Minimax)           │
│     ├─ System Prompt: Coaching expertise                │
│     ├─ User Prompt: Session data + request              │
│     └─ Structured Output: Pydantic model                │
│     ↓                                                    │
│  4. Opik Tracing (inputs, outputs, metadata)            │
│     ↓                                                    │
│  5. Save Recommendation (ai_practice_plans table)        │
│     ↓                                                    │
│  6. Return to User                                       │
└──────────────────────────────────────────────────────────┘
```

---

## Feature 1: Practice Recommendations (AI Mode)

### Purpose

Analyze user's practice history and recommend the optimal scale, difficulty, and focus area for the next session.

### User Flow

1. **User launches desktop app → Selects "AI Mode"**
2. **App calls:** `GET /ai/start-session?user_id=xxx`
3. **Backend:**
   - Fetches last 5 sessions from database
   - Checks for pending practice plans (<24h old)
   - If pending plan exists: Returns it
   - Otherwise: Generates new recommendation via LLM
4. **Frontend displays:**
   - Recommended scale (e.g., "D Minor Pentatonic")
   - Focus area (pitch, scale conformity, or timing)
   - AI reasoning for the recommendation
   - Suggested difficulty (strictness/sensitivity)
5. **User accepts or requests new recommendation**

### Technical Implementation

**File:** `backend/api/services/ai_agent_service.py`

**Function:** `generate_ai_recommendation(user_id: str)`

**Steps:**

1. **Fetch recent sessions:**
```python
query = """
    SELECT session_id, scale_chosen, pitch_accuracy, 
           scale_conformity, timing_stability, 
           total_notes_played, duration_seconds
    FROM fretcoach.sessions
    WHERE user_id = :user_id
    ORDER BY start_timestamp DESC
    LIMIT 5
"""
```

2. **Analyze patterns:**
```python
# Calculate average scores
avg_pitch = np.mean([s['pitch_accuracy'] for s in sessions])
avg_scale = np.mean([s['scale_conformity'] for s in sessions])
avg_timing = np.mean([s['timing_stability'] for s in sessions])

# Identify weakest area
weakest = min([
    ('pitch', avg_pitch),
    ('scale', avg_scale),
    ('timing', avg_timing)
], key=lambda x: x[1])
```

3. **LLM prompt construction:**
```python
system_prompt = """
You are an expert guitar coach analyzing practice session data.
Your goal: Recommend the optimal scale and focus area for improvement.

Rules:
- Focus on the weakest performance metric
- Consider practice history and patterns
- Recommend specific, actionable practice
- Provide clear reasoning
"""

user_prompt = f"""
Recent practice sessions:
{format_sessions(sessions)}

Weakest area: {weakest[0]} at {weakest[1]:.1f}%

Recommend:
1. Which scale to practice
2. Scale type (natural or pentatonic)
3. Focus area (pitch, scale, or timing)
4. Reasoning for your recommendation
5. Suggested strictness (0-1)
6. Suggested sensitivity (0-1)
"""
```

4. **Structured output (Pydantic):**
```python
class PracticeRecommendation(BaseModel):
    scale_name: str  # e.g., "D Minor"
    scale_type: str  # "natural" or "pentatonic"
    focus_area: str  # "pitch", "scale", or "timing"
    reasoning: str   # Explanation
    strictness: float  # 0.0-1.0
    sensitivity: float  # 0.0-1.0

llm_with_structure = model.with_structured_output(PracticeRecommendation)
recommendation = llm_with_structure.invoke(
    [SystemMessage(content=system_prompt),
     HumanMessage(content=user_prompt)],
    config=opik_config  # Opik tracing enabled
)
```

5. **Save to database:**
```python
query = """
    INSERT INTO fretcoach.ai_practice_plans
    (practice_id, user_id, practice_plan, generated_at)
    VALUES (:practice_id, :user_id, :plan_json, NOW())
"""
```

6. **Opik tracing:**
```python
def get_opik_config(user_id: str, trace_name: str, practice_id: str):
    tracer = OpikTracer(
        tags=["ai-mode", trace_name],
        metadata={"user_id": user_id, "practice_id": practice_id}
    )
    return {"callbacks": [tracer]}
```

### Example Recommendation

**Input data:**
```json
{
  "sessions": [
    {
      "scale": "C Major",
      "pitch_accuracy": 78,
      "scale_conformity": 82,
      "timing_stability": 45
    },
    {
      "scale": "A Minor",
      "pitch_accuracy": 75,
      "scale_conformity": 79,
      "timing_stability": 41
    }
  ]
}
```

**LLM output:**
```json
{
  "scale_name": "C Major",
  "scale_type": "natural",
  "focus_area": "timing",
  "reasoning": "Your timing stability is consistently low (averaging 43%) while pitch and scale conformity are good. Practice C Major again with focus on maintaining even note spacing. Use a metronome if available.",
  "strictness": 0.5,
  "sensitivity": 0.5
}
```

---

## Feature 2: Live Session Coaching

### Purpose

Provide real-time corrective feedback during practice based on current performance metrics.

### User Flow

1. **User starts practice session**
2. **Every 30 seconds:** Frontend sends current metrics to backend
3. **Backend:**
   - Identifies weakest metric
   - Generates specific, actionable coaching feedback via LLM
   - Returns feedback text
4. **Frontend displays feedback in "Live Coach" panel**

### Technical Implementation

**File:** `backend/api/services/live_coach_service.py`

**Function:** `generate_coaching_feedback(...)`

**Parameters:**
- `pitch_accuracy: float` (0-100)
- `scale_conformity: float` (0-100)
- `timing_stability: float` (0-100)
- `scale_name: str`
- `elapsed_seconds: int`
- `session_id: str` (for Opik tracing)

**Steps:**

1. **Identify weakest metric:**
```python
metrics = {
    "pitch": pitch_accuracy,
    "scale": scale_conformity,
    "timing": timing_stability
}
weakest = min(metrics.items(), key=lambda x: x[1])
```

2. **System prompt:**
```python
SYSTEM_PROMPT = """
You are a direct, practical guitar coach analyzing real-time playing data.

Your feedback must be:
- CORRECTIVE: Address the actual problem shown in the metrics
- SPECIFIC: Reference the exact metric that needs work
- ACTIONABLE: Give one concrete technique to try RIGHT NOW
- BRIEF: 1-2 sentences maximum

DO NOT:
- Use generic motivational phrases like "Great job!"
- Be vague about what needs improvement
- Give multiple suggestions at once

For the WEAKEST metric, provide a specific corrective instruction.
"""
```

3. **User prompt:**
```python
user_prompt = f"""
Session metrics after {elapsed_time} practicing {scale_name}:

Pitch Accuracy: {pitch_accuracy}% ({pitch_label})
Scale Conformity: {scale_conformity}% ({scale_label})
Timing Stability: {timing_stability}% ({timing_label})

Weakest area: {weakest_name} at {weakest_score}%
Notes played: {notes_played}
Correct notes: {correct_notes} | Wrong notes: {wrong_notes}

Give ONE specific corrective instruction for the weakest metric:
"""
```

4. **LLM call (GPT-4o-mini):**
```python
model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,  # Slightly creative
    max_tokens=150    # Keep brief
)

response = model.invoke(
    [SystemMessage(content=SYSTEM_PROMPT),
     HumanMessage(content=user_prompt)],
    config=opik_config  # Traced with session_id
)
```

5. **Text-to-Speech (TTS) conversion:**
```python
# Generate and play TTS audio using OpenAI's gpt-4o-mini-tts
async def generate_and_play_tts(feedback_text: str, session_id: str):
    openai_client = AsyncOpenAI()
    player = LocalAudioPlayer()

    # Stop any previous audio to prevent overlap/crackling
    player.stop()

    # Stream TTS audio with coaching-specific instructions
    async with openai_client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="onyx",
        input=feedback_text,
        instructions="Speak in a direct, encouraging tone like a guitar coach giving real-time feedback to a student during practice.",
        response_format="pcm",
    ) as response:
        await player.play(response)
```

6. **Return feedback:**
```python
{
    "feedback": response.content,
    "weakest_metric": weakest_name,
    "overall_performance": "Good",  # Based on average
    "timestamp": datetime.now().isoformat(),
    "tts": {
        "status": "played",
        "model": "gpt-4o-mini-tts",
        "voice": "onyx"
    }
}
```

### Vocal Feedback (TTS)

The live coach doesn't just display text—it **speaks** the feedback using OpenAI's `gpt-4o-mini-tts` model.

**Key features:**
- **Natural voice:** Uses the "onyx" voice with coaching-specific instructions
- **Prevents overlap:** Singleton audio player stops previous feedback before playing new audio
- **Low latency:** Streaming response format minimizes delay
- **Traced in Opik:** TTS generation is tracked with the `tts` tag for monitoring

This creates a more immersive coaching experience, allowing guitarists to keep their eyes on their hands instead of reading text on screen.

### Example Feedback

**Input metrics:**
```
Pitch: 78%, Scale: 82%, Timing: 23%
Scale: A Minor Pentatonic
Time: 2m 30s
```

**LLM output:**
> "Your timing is very inconsistent (23%). Focus on playing each note at exactly the same interval—try counting '1-2-3-4' out loud while playing to establish a steady rhythm."

---

## Feature 3: Conversational Chat (Web Dashboard) - Text-to-SQL Agent

### Purpose

Allow users to ask open-ended questions about their practice data using natural language. The AI agent interprets questions, queries the database, and returns conversational answers with visualizations.

### User Flow

1. **User visits web dashboard → AI Coach tab**
2. **Types natural language question:**
   - "What should I practice next?"
   - "Show me my progress trends"
   - "Compare my latest session to my average"
   - "Which scales have I practiced?"
3. **Backend:**
   - AI agent detects intent from natural language
   - Calls appropriate database query tools
   - LLM formats results conversationally
   - Returns response with optional charts
4. **Frontend displays conversational response + visualizations**

### Technical Implementation

**File:** `web/web-backend/routers/chat.py`

This is a **hybrid text-to-SQL agent**: The LLM doesn't generate raw SQL (which can be error-prone), but instead uses **predefined database query functions** triggered by intent detection. This combines the robustness of hardcoded queries with the flexibility of natural language interaction.

**Architecture Steps:**

1. **Intent Detection** — Keyword matching on user message:
```python
last_user_msg_lower = request.messages[-1].content.lower()

# Detect "show progress" intent
if any(word in last_user_msg_lower for word in
       ["progress", "trend", "chart", "graph", "show me"]):
    chart_data = get_performance_chart_data(user_id)

# Detect "compare sessions" intent
elif any(word in last_user_msg_lower for word in
         ["compare", "versus", "vs", "latest", "average"]):
    chart_data = get_comparison_chart_data(user_id, practice_data)

# Detect "practice recommendation" intent
elif any(word in last_user_msg_lower for word in
         ["practice", "recommend", "suggest", "what should"]):
    chart_data = generate_practice_recommendation(practice_data, user_id)
```

2. **Database Query Functions** — Predefined SQL tools:

```python
def get_user_practice_data(user_id: str) -> Dict[str, Any]:
    """Fetch aggregated practice statistics"""
    query = """
        SELECT COUNT(*) as total_sessions,
               AVG(pitch_accuracy) as avg_pitch_accuracy,
               AVG(scale_conformity) as avg_scale_conformity,
               AVG(timing_stability) as avg_timing_stability,
               SUM(duration_seconds) as total_practice_time
        FROM fretcoach.sessions
        WHERE user_id = %s
    """
    # Returns structured data for LLM context

def get_performance_chart_data(user_id: str, metric: str = "all"):
    """Generate chart data for performance trends"""
    query = """
        SELECT start_timestamp, pitch_accuracy,
               scale_conformity, timing_stability, scale_chosen
        FROM fretcoach.sessions
        WHERE user_id = %s
        ORDER BY start_timestamp DESC LIMIT 20
    """
    # Returns chart-ready data
```

3. **LLM Context Building** — System prompt includes user's data:

```python
def build_system_prompt(practice_data: Dict) -> str:
    return f"""You are an AI guitar practice coach for FretCoach.

## User's Practice Data
- Total sessions: {practice_data['total_sessions']}
- Average pitch accuracy: {practice_data['avg_pitch_accuracy']}%
- Average scale conformity: {practice_data['avg_scale_conformity']}%
- Average timing stability: {practice_data['avg_timing_stability']}%
- Weakest area: {practice_data['weakest_area']}

Recent Sessions:
{format_recent_sessions(practice_data)}

Provide personalized coaching advice based on this data."""
```

4. **LLM Response Generation** — Gemini 2.5 Flash with fallback:

```python
def invoke_with_fallback(messages, thread_id: str):
    """Try Gemini, fall back to MiniMax on rate limits"""

    # Create Opik tracer for conversation tracking
    tracer = OpikTracer(
        tags=["ai-coach", "web-chat"],
        metadata={"thread_id": thread_id}
    )
    config = {"callbacks": [tracer]}

    try:
        return gemini_model.invoke(messages, config=config)
    except Exception as e:
        if "RESOURCE_EXHAUSTED" in str(e):
            return minimax_model.invoke(messages, config=config)
        raise
```

5. **Response Enhancement** — Add chart data to response:

```python
response = invoke_with_fallback(messages, thread_id)
ai_content = response.content

if chart_data:
    if chart_data['type'] == 'performance_trend':
        ai_content += "\n\n*I've displayed your performance trend chart below.*"
    elif chart_data['type'] == 'practice_plan':
        ai_content += "\n\n*I've created a practice plan for you below. Click 'Save Plan' to save it.*"

return {
    "message": {"role": "assistant", "content": ai_content},
    "chartData": chart_data
}
```

### Why This Hybrid Approach?

**Advantages over pure text-to-SQL:**
- **Robust:** No risk of malformed SQL queries
- **Secure:** No SQL injection vulnerabilities
- **Fast:** Optimized queries, not LLM-generated
- **Predictable:** Known query patterns and performance
- **Natural:** LLM still provides conversational interface

**Key features:**
- Intent-based tool selection (not LLM tool calling)
- Predefined SQL queries (not generated)
- Conversational LLM responses (natural language output)
- Chart visualization support
- Opik tracing for all interactions

### Example Conversation:

**User:** "What should I practice next?"

**Backend processing (traced in Opik):**

1. **Intent detection:** Keyword "practice" matches → trigger practice recommendation
2. **Fetch user data:**
   ```sql
   SELECT AVG(pitch_accuracy), AVG(scale_conformity), AVG(timing_stability)
   FROM fretcoach.sessions WHERE user_id = 'user123'
   ```
   Results: Pitch 78%, Scale 82%, Timing 42% (weakest)
3. **Generate recommendation:** Call `generate_practice_recommendation()`
4. **Build system prompt with context:**
   ```
   Total sessions: 15
   Weakest area: timing
   Recent practice: C Major, A Minor
   ```
5. **LLM generates response** (Gemini 2.5 Flash)
6. **Return with practice plan card**

**Agent response:**
> "Based on your practice history, timing stability is your weakest area at 42%. I recommend practicing **C Major Pentatonic** with these exercises:
> - Practice slow scales focusing on hitting each note cleanly
> - Use a metronome starting at a slow tempo
> - Focus on consistent note duration before speed
>
> I've created a practice plan below. Click 'Save Plan' to save it."

**Chart data returned:**
```json
{
  "type": "practice_plan",
  "data": {
    "focus_area": "Timing Stability",
    "current_score": 42,
    "suggested_scale": "C Major",
    "suggested_scale_type": "pentatonic",
    "exercises": ["Practice with metronome...", "Focus on consistent note duration..."]
  },
  "plan_id": "uuid-123"
}
```

**Frontend displays:** Conversational response + practice plan card with "Save Plan" button

---

**User:** "Show me my progress trends"

**Backend processing:**

1. **Intent detection:** Keywords "show", "progress", "trends" → trigger chart generation
2. **Fetch session history:**
   ```sql
   SELECT start_timestamp, pitch_accuracy, scale_conformity, timing_stability
   FROM fretcoach.sessions WHERE user_id = 'user123'
   ORDER BY start_timestamp DESC LIMIT 20
   ```
3. **Format as chart data** (reversed for chronological order)
4. **LLM response** with chart context

**Agent response:**
> "Here's your performance trend over the last 20 sessions. Your pitch accuracy has been consistently improving (78% → 85%), but timing stability remains an area for focus."
>
> *I've displayed your performance trend chart below.*

**Chart data:** Line chart showing all three metrics over time

---

## Multi-LLM Support

FretCoach supports four LLM providers, all traced identically through Opik:

### OpenAI GPT-4o-mini (Default)

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)
```

**Pros:** Fast, reliable, good reasoning  
**Cost:** ~$0.15 per 1M input tokens  
**Use case:** All coaching features

### Google Gemini 2.5 Flash

```python
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
```

**Pros:** Very fast, multimodal capable  
**Cost:** Free tier available  
**Use case:** High-throughput coaching

### Deepseek Chat 3.1

```python
model = ChatOpenAI(
    base_url="https://api.deepseek.com",
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY")
)
```

**Pros:** Very cheap, good reasoning  
**Cost:** ~$0.27 per 1M input tokens  
**Use case:** Cost-sensitive deployments

### Minimax 2.1

```python
model = ChatOpenAI(
    base_url="https://api.minimax.chat/v1",
    model="minimax-2.1-open",
    api_key=os.getenv("MINIMAX_API_KEY")
)
```

**Pros:** Good multilingual support  
**Cost:** Competitive  
**Use case:** International users

### Provider Selection

Configure via environment variable:

```bash
# .env
LLM_PROVIDER=openai  # or gemini, deepseek, minimax
```

All providers work seamlessly with Opik tracing—no code changes needed.

---

## Opik Integration Details

### Tracer Configuration

```python
from opik.integrations.langchain import OpikTracer

def get_opik_config(user_id: str, trace_name: str, **metadata):
    """Create Opik config for LangChain calls."""
    if not OPIK_ENABLED:
        return {}
    
    tracer = OpikTracer(
        tags=["fretcoach", trace_name],
        metadata={"user_id": user_id, **metadata}
    )
    
    return {
        "callbacks": [tracer],
        "configurable": {"thread_id": f"user-{user_id}"}
    }
```

### Usage in Code

```python
# AI Mode recommendation
opik_config = get_opik_config(
    user_id="paddy",
    trace_name="ai-recommendation",
    practice_id=practice_id
)

recommendation = llm.invoke(prompt, config=opik_config)
```

### Trace Metadata

Every trace includes:

**Tags:**
- `ai-mode` — Practice recommendations
- `live-coach` — Real-time session feedback
- `web-chat` — Dashboard conversations

**Metadata:**
- `user_id` — User identifier
- `session_id` — Session ID (for live coaching)
- `practice_id` — Practice plan ID (for recommendations)

**Custom fields:**
- `input` — Full prompt sent to LLM
- `output` — LLM response (structured or text)
- `model` — Which LLM was used
- `duration_ms` — Latency

### Viewing Traces

**Opik Dashboard:** [FretCoach Project](https://comet.com/opik/padmanabhan-r-7119/projects/019bcefc-a27c-718d-8c5f-36472d5decb2)

**Filter examples:**
- All AI recommendations: `tag:ai-mode`
- Live coaching only: `tag:live-coach`
- Specific user: `metadata.user_id:paddy`
- Specific session: `metadata.session_id:abc-123`

---

## Prompt Engineering

### Design Principles

1. **Specificity:** Prompts reference exact metrics and data
2. **Actionability:** Outputs must be immediately usable
3. **Brevity:** Live coaching limited to 1-2 sentences
4. **Structured:** Use Pydantic models for type safety
5. **Context:** Include relevant session history

### System Prompt Template (AI Mode)

```
You are an expert guitar coach analyzing practice session data to provide personalized recommendations.

Context:
- User has practiced {num_sessions} times recently
- Average scores: Pitch {avg_pitch}%, Scale {avg_scale}%, Timing {avg_timing}%
- Weakest area: {weakest_area}

Your task:
Recommend the optimal scale and practice settings to address the weakest area.

Output requirements:
1. scale_name: Specific scale in musical notation (e.g., "D Minor")
2. scale_type: "natural" or "pentatonic"
3. focus_area: "pitch", "scale", or "timing"
4. reasoning: 1-2 sentences explaining your recommendation
5. strictness: 0.0-1.0 (difficulty level)
6. sensitivity: 0.0-1.0 (detection threshold)

Rules:
- Focus on improvement, not variety
- If timing is weak, recommend natural scales (more notes = better rhythm practice)
- If pitch is weak, recommend pentatonic (fewer notes = focus on accuracy)
- If scale conformity is weak, recommend the same scale again
```

### Live Coaching Prompt Template

```
You are a direct, practical guitar coach analyzing real-time playing data.

Current session: {scale_name} for {elapsed_time}

Metrics:
- Pitch Accuracy: {pitch}% ({pitch_label})
- Scale Conformity: {scale}% ({scale_label})
- Timing Stability: {timing}% ({timing_label})

Weakest: {weakest_name} at {weakest_score}%

Provide ONE specific corrective instruction for {weakest_name}.

Requirements:
- Be direct and specific
- Reference the actual metric
- Give actionable technique to try NOW
- Maximum 2 sentences
- No generic praise

Examples:
- "Your timing is drifting—lock in with the beat by counting out loud."
- "Reduce string noise by lifting fingers straight up, not dragging across strings."
- "You're hitting notes outside the scale—review the fretboard positions before continuing."
```

---

## Performance Optimization

### Latency Targets

- **AI recommendations:** <2 seconds (acceptable)
- **Live coaching:** <1 second (critical for real-time feel)
- **Chat responses:** <3 seconds (acceptable for conversational)

### Optimization Strategies

1. **Model selection:**
   - GPT-4o-mini and Gemini Flash optimized for speed
   - Avoid GPT-4 (too slow for live coaching)

2. **Token limits:**
   - Live coaching: max_tokens=150 (brief responses)
   - Recommendations: max_tokens=500 (structured output)

3. **Caching:**
   - Pending practice plans cached for 24 hours
   - Recent sessions cached per user

4. **Parallel processing:**
   - Live coaching doesn't block audio processing
   - Chat requests handled asynchronously

---

## Error Handling

### LLM Failures

```python
try:
    recommendation = llm.invoke(prompt, config=opik_config)
except Exception as e:
    logger.error(f"LLM call failed: {e}")
    # Fallback to sensible default
    recommendation = {
        "scale_name": "C Major",
        "scale_type": "natural",
        "focus_area": "timing",
        "reasoning": "Unable to generate custom recommendation. Starting with C Major as a safe default.",
        "strictness": 0.5,
        "sensitivity": 0.5
    }
```

### Rate Limiting

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def call_llm_with_retry(prompt, config):
    return llm.invoke(prompt, config=config)
```

### Opik Failures

Opik tracing is **non-blocking**—if tracing fails, the application continues:

```python
try:
    from opik.integrations.langchain import OpikTracer
    OPIK_ENABLED = True
except ImportError:
    OPIK_ENABLED = False
    logger.warning("Opik not available—tracing disabled")
```

---

**Navigation:**
- [← Architecture](architecture.md)
- [Appendix: Audio Math →](appendix-audio-math.md)
- [Back to Index](index.md)
