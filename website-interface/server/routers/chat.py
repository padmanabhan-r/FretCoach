"""
AI Practice Coach Chat Router
Uses OpenAI with function calling and Opik tracing
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import json
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Import Opik for tracking
try:
    from opik import track, opik_context
    OPIK_ENABLED = True
except ImportError:
    def track(name=None, **kwargs):
        def decorator(func):
            return func
        return decorator
    opik_context = None
    OPIK_ENABLED = False

router = APIRouter()

# Initialize LLM
model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# In-memory store for pending practice plans (per thread)
# In production, you might use Redis or a database table
pending_plans: Dict[str, Dict[str, Any]] = {}


class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    user_id: str = "default_user"
    thread_id: Optional[str] = None


class SavePlanRequest(BaseModel):
    plan_id: str
    user_id: str = "default_user"


class ChartData(BaseModel):
    type: str
    data: Any
    metric: Optional[str] = None
    plan_id: Optional[str] = None  # For tracking pending plans


def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "fretcoach"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


@track(name="get_user_practice_data")
def get_user_practice_data(user_id: str) -> Dict[str, Any]:
    """Fetch user's practice data for context"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Get aggregates
    cursor.execute("""
        SELECT
            COUNT(*) as total_sessions,
            COALESCE(AVG(pitch_accuracy), 0) as avg_pitch_accuracy,
            COALESCE(AVG(scale_conformity), 0) as avg_scale_conformity,
            COALESCE(AVG(timing_stability), 0) as avg_timing_stability,
            COALESCE(SUM(duration_seconds), 0) as total_practice_time
        FROM sessions WHERE user_id = %s
    """, (user_id,))
    agg = cursor.fetchone()

    # Get recent sessions
    cursor.execute("""
        SELECT session_id, start_timestamp, pitch_accuracy, scale_conformity,
               timing_stability, scale_chosen, scale_type, duration_seconds
        FROM sessions WHERE user_id = %s
        ORDER BY start_timestamp DESC LIMIT 10
    """, (user_id,))
    recent = cursor.fetchall()

    # Get scales with performance
    cursor.execute("""
        SELECT scale_chosen, scale_type, COUNT(*) as count,
               AVG(pitch_accuracy) as avg_pitch,
               AVG(scale_conformity) as avg_scale,
               AVG(timing_stability) as avg_timing
        FROM sessions WHERE user_id = %s
        GROUP BY scale_chosen, scale_type
        ORDER BY count DESC
    """, (user_id,))
    scales = cursor.fetchall()

    cursor.close()
    conn.close()

    # Determine weakest area
    metrics = {
        "pitch": float(agg['avg_pitch_accuracy'] or 0),
        "scale": float(agg['avg_scale_conformity'] or 0),
        "timing": float(agg['avg_timing_stability'] or 0)
    }
    weakest = min(metrics, key=metrics.get) if agg['total_sessions'] > 0 else "pitch"

    return {
        "total_sessions": int(agg['total_sessions'] or 0),
        "avg_pitch_accuracy": metrics["pitch"],
        "avg_scale_conformity": metrics["scale"],
        "avg_timing_stability": metrics["timing"],
        "total_practice_time": float(agg['total_practice_time'] or 0),
        "recent_sessions": [dict(r) for r in recent],
        "practiced_scales": [dict(s) for s in scales],
        "weakest_area": weakest
    }


@track(name="get_performance_chart_data")
def get_performance_chart_data(user_id: str, metric: str = "all") -> Dict[str, Any]:
    """Generate chart data for performance trends"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        SELECT start_timestamp, pitch_accuracy, scale_conformity, timing_stability,
               scale_chosen, duration_seconds
        FROM sessions WHERE user_id = %s
        ORDER BY start_timestamp DESC LIMIT 20
    """, (user_id,))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # Reverse for chronological order
    rows = list(reversed(rows))

    chart_data = []
    for i, row in enumerate(rows):
        chart_data.append({
            "session": i + 1,
            "date": row['start_timestamp'].strftime("%m/%d") if row['start_timestamp'] else "",
            "pitch_accuracy": round((row['pitch_accuracy'] or 0) * 100),
            "scale_conformity": round((row['scale_conformity'] or 0) * 100),
            "timing_stability": round((row['timing_stability'] or 0) * 100),
            "scale": row['scale_chosen']
        })

    return {
        "type": "performance_trend",
        "data": chart_data,
        "metric": metric
    }


@track(name="get_comparison_chart_data")
def get_comparison_chart_data(user_id: str, practice_data: Dict) -> Dict[str, Any]:
    """Generate comparison chart data (latest vs average)"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        SELECT pitch_accuracy, scale_conformity, timing_stability
        FROM sessions WHERE user_id = %s
        ORDER BY start_timestamp DESC LIMIT 1
    """, (user_id,))

    latest = cursor.fetchone()
    cursor.close()
    conn.close()

    if not latest:
        return None

    return {
        "type": "comparison",
        "data": {
            "latest": {
                "pitch": round((latest['pitch_accuracy'] or 0) * 100),
                "scale": round((latest['scale_conformity'] or 0) * 100),
                "timing": round((latest['timing_stability'] or 0) * 100)
            },
            "average": {
                "pitch": round(practice_data['avg_pitch_accuracy'] * 100),
                "scale": round(practice_data['avg_scale_conformity'] * 100),
                "timing": round(practice_data['avg_timing_stability'] * 100)
            }
        }
    }


@track(name="generate_practice_recommendation")
def generate_practice_recommendation(practice_data: Dict, user_id: str, thread_id: str) -> Dict[str, Any]:
    """Generate a practice recommendation based on user data"""
    weakest = practice_data['weakest_area']
    focus_names = {
        "pitch": "Pitch Accuracy",
        "scale": "Scale Conformity",
        "timing": "Timing Stability"
    }

    exercises = {
        "pitch": [
            "Practice slow scales focusing on hitting each note cleanly",
            "Use a tuner while practicing to get immediate feedback",
            "Work on sustaining notes and listening to their quality"
        ],
        "scale": [
            "Practice the scale patterns slowly before increasing speed",
            "Focus on one scale at a time until it becomes muscle memory",
            "Try playing the scale in different positions on the neck"
        ],
        "timing": [
            "Practice with a metronome starting at a slow tempo",
            "Focus on consistent note duration before speed",
            "Try rhythm exercises with varying note values"
        ]
    }

    # Suggest a scale that needs work
    scales = practice_data.get('practiced_scales', [])
    suggested_scale = "C Major"
    suggested_scale_type = "diatonic"
    if scales:
        for s in scales:
            if s.get('avg_pitch', 1) < 0.8:
                suggested_scale = s['scale_chosen']
                suggested_scale_type = s.get('scale_type', 'diatonic')
                break

    score_key = f"avg_{weakest}_{'accuracy' if weakest == 'pitch' else 'conformity' if weakest == 'scale' else 'stability'}"

    # Generate a plan_id for this recommendation
    plan_id = str(uuid.uuid4())

    plan_data = {
        "focus_area": focus_names.get(weakest, weakest),
        "current_score": round(practice_data.get(score_key, practice_data['avg_pitch_accuracy']) * 100),
        "suggested_scale": suggested_scale,
        "suggested_scale_type": suggested_scale_type,
        "exercises": exercises.get(weakest, exercises['pitch']),
        "session_target": "20-30 minutes"
    }

    # Store the pending plan
    pending_plans[thread_id] = {
        "plan_id": plan_id,
        "user_id": user_id,
        "plan_data": plan_data,
        "plan_text": format_plan_text(plan_data)
    }

    return {
        "type": "practice_plan",
        "data": plan_data,
        "plan_id": plan_id
    }


def format_plan_text(plan_data: Dict) -> str:
    """Format the practice plan as text for database storage"""
    exercises_text = "\n".join([f"- {ex}" for ex in plan_data['exercises']])
    return f"""Practice Plan
Focus Area: {plan_data['focus_area']}
Current Score: {plan_data['current_score']}%
Suggested Scale: {plan_data['suggested_scale']} ({plan_data.get('suggested_scale_type', 'diatonic')})
Session Target: {plan_data['session_target']}

Exercises:
{exercises_text}"""


@track(name="save_practice_plan")
def save_practice_plan_to_db(plan_id: str, user_id: str, plan_text: str) -> bool:
    """Save a confirmed practice plan to the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO ai_practice_plans (practice_id, user_id, practice_plan)
            VALUES (%s, %s, %s)
        """, (plan_id, user_id, plan_text))

        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save practice plan: {e}")
        return False


def check_for_confirmation(message: str) -> bool:
    """Check if user message is confirming a practice plan"""
    confirm_phrases = [
        "yes", "save", "confirm", "ok", "okay", "sure", "sounds good",
        "looks good", "perfect", "great", "let's do it", "go ahead",
        "i like it", "save it", "save the plan", "confirmed", "accept"
    ]
    message_lower = message.lower().strip()
    return any(phrase in message_lower for phrase in confirm_phrases)


def build_system_prompt(practice_data: Dict, has_pending_plan: bool = False) -> str:
    """Build the system prompt with user's practice context"""
    recent_sessions_text = ""
    for s in practice_data.get('recent_sessions', [])[:5]:
        date = s['start_timestamp'].strftime("%m/%d") if s.get('start_timestamp') else "N/A"
        recent_sessions_text += f"- {date}: {s.get('scale_chosen', 'Unknown')} (Pitch: {round((s.get('pitch_accuracy') or 0) * 100)}%, Scale: {round((s.get('scale_conformity') or 0) * 100)}%, Timing: {round((s.get('timing_stability') or 0) * 100)}%)\n"

    if not recent_sessions_text:
        recent_sessions_text = "No sessions recorded yet"

    scales_text = ", ".join([s['scale_chosen'] for s in practice_data.get('practiced_scales', [])[:5]]) or "None yet"

    pending_plan_instruction = ""
    if has_pending_plan:
        pending_plan_instruction = """
7. IMPORTANT: There is a pending practice plan. If the user confirms (says yes, ok, save it, sounds good, etc.), acknowledge that the plan has been saved and encourage them to start practicing.
"""

    return f"""You are an AI guitar practice coach for FretCoach. You help users improve their guitar playing by analyzing their practice session data and providing personalized advice.

## User's Practice Data
- **Total sessions**: {practice_data['total_sessions']}
- **Average pitch accuracy**: {round(practice_data['avg_pitch_accuracy'] * 100)}%
- **Average scale conformity**: {round(practice_data['avg_scale_conformity'] * 100)}%
- **Average timing stability**: {round(practice_data['avg_timing_stability'] * 100)}%
- **Weakest area**: {practice_data['weakest_area']}
- **Scales practiced**: {scales_text}

## Recent Sessions
{recent_sessions_text}

## Instructions
1. Be encouraging and supportive while providing honest feedback
2. When the user asks about progress or trends, tell them you'll show a chart
3. When the user asks for practice recommendations, provide specific advice and ASK if they'd like to save this plan
4. Keep responses concise but helpful
5. Use markdown formatting for better readability
6. If asked to compare performance, analyze their latest session vs average{pending_plan_instruction}

## Response Format
- Use **bold** for emphasis
- Use bullet points for lists
- Use headers (##) for sections when appropriate
- Keep paragraphs short and readable"""


@track(name="ai_coach_chat")
@router.post("/chat")
async def chat(request: ChatRequest) -> Dict[str, Any]:
    """
    AI Practice Coach chat endpoint

    Processes user messages and returns AI responses with optional chart data
    """
    # Set thread_id for Opik conversation tracking
    thread_id = request.thread_id or f"chat-{request.user_id}"
    if OPIK_ENABLED and opik_context:
        try:
            opik_context.update_current_trace(thread_id=thread_id)
        except:
            pass

    try:
        # Get user's practice data
        practice_data = get_user_practice_data(request.user_id)

        # Get the last user message for intent detection
        last_user_msg = request.messages[-1].content if request.messages else ""
        last_user_msg_lower = last_user_msg.lower()

        # Check if there's a pending plan and user is confirming
        plan_saved = False
        if thread_id in pending_plans and check_for_confirmation(last_user_msg):
            pending = pending_plans[thread_id]
            if save_practice_plan_to_db(pending['plan_id'], pending['user_id'], pending['plan_text']):
                plan_saved = True
                del pending_plans[thread_id]  # Clear the pending plan

        # Check if there's a pending plan for this thread
        has_pending_plan = thread_id in pending_plans

        # Build messages for LLM
        system_prompt = build_system_prompt(practice_data, has_pending_plan)
        messages = [SystemMessage(content=system_prompt)]

        for msg in request.messages:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            else:
                messages.append(AIMessage(content=msg.content))

        # Detect intent and prepare chart data
        chart_data = None

        if any(word in last_user_msg_lower for word in ["progress", "trend", "chart", "graph", "show me", "visualize", "how am i doing"]):
            chart_data = get_performance_chart_data(request.user_id)

        elif any(word in last_user_msg_lower for word in ["compare", "versus", "vs", "latest", "average", "comparison"]):
            chart_data = get_comparison_chart_data(request.user_id, practice_data)

        elif any(word in last_user_msg_lower for word in ["practice", "recommend", "suggest", "what should", "plan", "advice", "help me"]) and not plan_saved:
            chart_data = generate_practice_recommendation(practice_data, request.user_id, thread_id)

        # Generate AI response
        response = model.invoke(messages)
        ai_content = response.content

        # Add chart context to response if chart is being shown
        if chart_data:
            if chart_data['type'] == 'performance_trend':
                ai_content += "\n\n*I've displayed your performance trend chart below.*"
            elif chart_data['type'] == 'comparison':
                ai_content += "\n\n*I've shown a comparison of your latest session vs your average below.*"
            elif chart_data['type'] == 'practice_plan':
                ai_content += "\n\n*I've created a practice plan for you below. Would you like me to save this plan?*"

        # If plan was saved, add confirmation
        if plan_saved:
            ai_content += "\n\n✅ *Your practice plan has been saved! You can access it anytime from your practice history.*"

        return {
            "success": True,
            "message": {
                "role": "assistant",
                "content": ai_content
            },
            "chartData": chart_data,
            "planSaved": plan_saved,
            "hasPendingPlan": thread_id in pending_plans,
            "sessionContext": {
                "total_sessions": practice_data['total_sessions'],
                "weakest_area": practice_data['weakest_area']
            }
        }

    except Exception as e:
        print(f"[ERROR] Chat failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")
