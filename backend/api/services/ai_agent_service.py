"""
AI Agent Service for FretCoach
Optimized service that uses direct SQL queries and a single LLM call for recommendations.
No redundant schema lookups or multi-step LLM loops.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
import os
import uuid
from dotenv import load_dotenv, find_dotenv

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text

# Import Opik for tracking with LangChain integration
from opik.integrations.langchain import OpikTracer

# Load environment variables
load_dotenv(find_dotenv())

# Get deployment type for tracing tags
DEPLOYMENT_TYPE = os.getenv("DEPLOYMENT_TYPE", "fretcoach-studio")  # Default to studio

# Get PostgreSQL credentials from environment
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Create SQLAlchemy engine (reusable connection pool)
db_uri = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(db_uri, pool_pre_ping=True)

# Initialize LLM - single instance
MODEL_NAME = "gpt-4o-mini"
model = ChatOpenAI(model=MODEL_NAME, temperature=0)


def get_opik_config(user_id: str, trace_name: str, practice_id: str = None) -> dict:
    """
    Create Opik config for LangChain calls tied to user session.
    Tags include: fretcoach-core, model name, ai-mode, and deployment type.
    """
    metadata = {"user_id": user_id}
    if practice_id:
        metadata["practice_id"] = practice_id

    # Build comprehensive tags for tracing
    tags = [
        "fretcoach-core",
        MODEL_NAME,
        "ai-mode",
        DEPLOYMENT_TYPE,
        trace_name
    ]

    tracer = OpikTracer(
        tags=tags,
        metadata=metadata
    )
    return {
        "callbacks": [tracer],
        "configurable": {"thread_id": f"ai-mode-{user_id}"}
    }


class PracticeRecommendation(BaseModel):
    """Structured output for practice recommendations"""
    scale_name: str = Field(description="The recommended scale to practice (e.g., 'C Major', 'D Minor', 'E Major')")
    scale_type: str = Field(description="Type of scale: 'natural' or 'pentatonic'")
    focus_area: str = Field(description="The area to focus on: 'pitch', 'scale', or 'timing'")
    reasoning: str = Field(description="Brief explanation for why this practice session is recommended")
    strictness: float = Field(description="Recommended strictness level (0.0-1.0)", ge=0.0, le=1.0)
    sensitivity: float = Field(description="Recommended sensitivity level (0.0-1.0)", ge=0.0, le=1.0)


def get_recent_practice_plans(user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get recent practice plans (both executed and unexecuted) for the user.
    Used to track what has been suggested recently to avoid repetition.

    Args:
        user_id: The user's identifier
        limit: Maximum number of plans to retrieve

    Returns:
        List of recent practice plans with their details
    """
    query = text("""
        SELECT practice_id, practice_plan, generated_at, executed_session_id
        FROM fretcoach.ai_practice_plans
        WHERE user_id = :user_id
        ORDER BY generated_at DESC
        LIMIT :limit
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"user_id": user_id, "limit": limit})
        rows = result.fetchall()

        plans = []
        for row in rows:
            try:
                plan_data = json.loads(row[1]) if row[1] else None
                if plan_data and isinstance(plan_data, dict):
                    plans.append({
                        "practice_id": str(row[0]),
                        "plan": plan_data,
                        "generated_at": row[2],
                        "executed": row[3] is not None
                    })
            except (json.JSONDecodeError, TypeError):
                continue
        return plans


def get_pending_practice_plan(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Check if there's an unexecuted practice plan for the user.
    Gets the 3 most recent plans and returns the most recent unexecuted one.
    """
    query = text("""
        SELECT practice_id, practice_plan, generated_at, executed_session_id
        FROM fretcoach.ai_practice_plans
        WHERE user_id = :user_id
        ORDER BY generated_at DESC
        LIMIT 3
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"user_id": user_id})
        rows = result.fetchall()

        # Filter for unexecuted plans and pick the most recent one
        for row in rows:
            if row[3] is None:  # executed_session_id is NULL
                try:
                    # Try to parse the JSON plan
                    plan_data = json.loads(row[1]) if row[1] else None
                    if plan_data and isinstance(plan_data, dict):
                        # Return the most recent unexecuted plan
                        return {
                            "practice_id": str(row[0]),
                            "plan": plan_data,
                            "generated_at": row[2]
                        }
                except (json.JSONDecodeError, TypeError) as e:
                    # If JSON is invalid (plain text format), skip this plan
                    print(f"Warning: Skipping non-JSON pending practice plan {row[0]}")
                    continue
    return None


def get_recent_sessions(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get recent practice sessions for analysis (up to 10 if available).
    Direct SQL query - no LLM needed.
    """
    query = text("""
        SELECT
            session_id, start_timestamp, scale_chosen, scale_type,
            pitch_accuracy, scale_conformity, timing_stability,
            total_notes_played, correct_notes_played, bad_notes_played,
            duration_seconds, strictness, sensitivity
        FROM fretcoach.sessions
        WHERE user_id = :user_id
        ORDER BY start_timestamp DESC
        LIMIT :limit
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"user_id": user_id, "limit": limit})
        rows = result.fetchall()

        sessions = []
        for row in rows:
            sessions.append({
                "session_id": row[0],
                "start_timestamp": row[1].isoformat() if row[1] else None,
                "scale_chosen": row[2],
                "scale_type": row[3],
                "pitch_accuracy": row[4],
                "scale_conformity": row[5],
                "timing_stability": row[6],
                "total_notes_played": row[7],
                "correct_notes_played": row[8],
                "bad_notes_played": row[9],
                "duration_seconds": row[10],
                "strictness": row[11],
                "sensitivity": row[12]
            })
        return sessions


def get_session_aggregates(user_id: str) -> Dict[str, Any]:
    """
    Get aggregate statistics across all user sessions.
    Direct SQL query - no LLM needed.
    """
    query = text("""
        SELECT
            COUNT(*) as total_sessions,
            AVG(pitch_accuracy) as avg_pitch_accuracy,
            AVG(scale_conformity) as avg_scale_conformity,
            AVG(timing_stability) as avg_timing_stability,
            SUM(total_notes_played) as total_notes,
            SUM(correct_notes_played) as total_correct,
            SUM(bad_notes_played) as total_bad
        FROM fretcoach.sessions
        WHERE user_id = :user_id
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"user_id": user_id})
        row = result.fetchone()

        if row and row[0] > 0:
            return {
                "total_sessions": row[0],
                "avg_pitch_accuracy": float(row[1]) if row[1] else 0.0,
                "avg_scale_conformity": float(row[2]) if row[2] else 0.0,
                "avg_timing_stability": float(row[3]) if row[3] else 0.0,
                "total_notes": row[4] or 0,
                "total_correct": row[5] or 0,
                "total_bad": row[6] or 0
            }
        return {
            "total_sessions": 0,
            "avg_pitch_accuracy": 0.0,
            "avg_scale_conformity": 0.0,
            "avg_timing_stability": 0.0,
            "total_notes": 0,
            "total_correct": 0,
            "total_bad": 0
        }


def get_practiced_scales(user_id: str) -> List[Dict[str, Any]]:
    """
    Get scales the user has practiced and their performance on each.
    Direct SQL query - no LLM needed.
    """
    query = text("""
        SELECT
            scale_chosen, scale_type,
            COUNT(*) as times_practiced,
            AVG(pitch_accuracy) as avg_pitch,
            AVG(scale_conformity) as avg_scale,
            AVG(timing_stability) as avg_timing,
            MAX(start_timestamp) as last_practiced
        FROM fretcoach.sessions
        WHERE user_id = :user_id
        GROUP BY scale_chosen, scale_type
        ORDER BY last_practiced DESC
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"user_id": user_id})
        rows = result.fetchall()

        scales = []
        for row in rows:
            scales.append({
                "scale_name": row[0],
                "scale_type": row[1],
                "times_practiced": row[2],
                "avg_pitch": float(row[3]) if row[3] else 0.0,
                "avg_scale": float(row[4]) if row[4] else 0.0,
                "avg_timing": float(row[5]) if row[5] else 0.0,
                "last_practiced": row[6].isoformat() if row[6] else None
            })
        return scales


def analyze_practice_history_sync(user_id: str) -> Dict[str, Any]:
    """
    Analyze user's practice history using direct SQL queries.
    No LLM calls - just data gathering. No tracing needed.

    Args:
        user_id: The user's identifier

    Returns:
        Dictionary containing analysis results
    """
    # Gather all data with direct SQL queries
    recent_sessions = get_recent_sessions(user_id)
    aggregates = get_session_aggregates(user_id)
    practiced_scales = get_practiced_scales(user_id)

    # Identify weakest area
    metrics = {
        "pitch": aggregates["avg_pitch_accuracy"],
        "scale": aggregates["avg_scale_conformity"],
        "timing": aggregates["avg_timing_stability"]
    }
    weakest_area = min(metrics, key=metrics.get) if aggregates["total_sessions"] > 0 else "pitch"

    # Build analysis summary
    analysis = {
        "user_id": user_id,
        "total_sessions": aggregates["total_sessions"],
        "recent_sessions": recent_sessions,
        "aggregates": aggregates,
        "practiced_scales": practiced_scales,
        "weakest_area": weakest_area,
        "metrics_summary": metrics
    }

    return analysis


async def analyze_practice_history(user_id: str) -> Dict[str, Any]:
    """Async wrapper for analyze_practice_history_sync"""
    return analyze_practice_history_sync(user_id)


async def generate_practice_recommendation(
    user_id: str,
    analysis: Dict[str, Any],
    recent_plans: Optional[List[Dict[str, Any]]] = None,
    pending_plan: Optional[Dict[str, Any]] = None
) -> PracticeRecommendation:
    """
    Generate structured practice recommendation based on analysis.
    Single LLM call with structured output. Traced with OpikTracer.

    Args:
        user_id: The user's identifier
        analysis: Dictionary containing practice history analysis
        recent_plans: Optional list of recent practice plans to avoid repeating
        pending_plan: Optional pending plan that LLM can choose to keep or replace

    Returns:
        Structured practice recommendation
    """
    # Use structured output to generate recommendation - SINGLE LLM CALL
    structured_llm = model.with_structured_output(PracticeRecommendation)

    # Build context about pending plan
    pending_plan_context = ""
    if pending_plan:
        plan_details = pending_plan["plan"]
        pending_plan_context = f"""

PENDING PRACTICE PLAN (PREVIOUSLY SUGGESTED):
There is an unexecuted practice plan from {pending_plan['generated_at']}:
- Scale: {plan_details['scale_name']} ({plan_details['scale_type']})
- Focus: {plan_details['focus_area']}
- Reasoning: {plan_details['reasoning']}
- Strictness: {plan_details['strictness']}
- Sensitivity: {plan_details['sensitivity']}

IMPORTANT: Review the recent practice sessions above. You have two options:
1. If the pending plan is STILL the best choice given recent performance, recommend the SAME scale/type/focus (keep it)
2. If recent sessions show the user needs something DIFFERENT, generate a NEW recommendation

Base your decision on whether recent sessions indicate the pending plan is still optimal or if priorities have changed.
"""

    # Build context about recent suggestions to avoid repetition (only if no pending plan)
    recent_suggestions_context = ""
    if not pending_plan and recent_plans:
        recent_suggestions = []
        for plan in recent_plans[:3]:  # Use last 3 suggestions
            recent_suggestions.append({
                "scale": f"{plan['plan']['scale_name']} ({plan['plan']['scale_type']})",
                "focus": plan['plan']['focus_area']
            })
        if recent_suggestions:
            recent_suggestions_context = f"""

RECENT SUGGESTIONS (DO NOT REPEAT):
The following suggestions were recently made. You MUST suggest something different:
{json.dumps(recent_suggestions, indent=2)}

IMPORTANT: Choose a different scale or different scale type than what was recently suggested.
"""

    # Build a concise prompt with the analysis data
    prompt = f"""You are an AI guitar coach. Based on the practice history below, recommend a practice session.

PRACTICE HISTORY:
- Total sessions: {analysis['total_sessions']}
- Average pitch accuracy: {analysis['aggregates']['avg_pitch_accuracy']:.1%}
- Average scale conformity: {analysis['aggregates']['avg_scale_conformity']:.1%}
- Average timing stability: {analysis['aggregates']['avg_timing_stability']:.1%}
- Weakest area: {analysis['weakest_area']}

RECENTLY PRACTICED SCALES:
{json.dumps(analysis['practiced_scales'][:5], indent=2) if analysis['practiced_scales'] else 'No scales practiced yet'}

RECENT SESSIONS (last 10):
{json.dumps(analysis['recent_sessions'], indent=2) if analysis['recent_sessions'] else 'No recent sessions'}{pending_plan_context}{recent_suggestions_context}

Generate a practice recommendation that:
1. Focuses on the weakest metric area ({analysis['weakest_area']})
2. Suggests a scale (preferably one not recently practiced, or one needing improvement)
3. Sets appropriate strictness/sensitivity based on skill level
4. For beginners (< 5 sessions or low scores), use lower strictness (0.3-0.5)
5. For intermediate users, use moderate strictness (0.5-0.7)
6. For advanced users (high scores), use higher strictness (0.7-0.9)
"""

    # Get Opik config for tracing the LLM call
    opik_config = get_opik_config(user_id, "practice-recommendation")

    recommendation = structured_llm.invoke(
        [{"role": "user", "content": prompt}],
        config=opik_config
    )
    return recommendation


def save_practice_plan_sync(user_id: str, recommendation: PracticeRecommendation) -> str:
    """
    Save the practice plan to the database.

    Args:
        user_id: The user's identifier
        recommendation: The practice recommendation to save

    Returns:
        The practice_id (UUID) of the saved plan
    """
    practice_id = str(uuid.uuid4())

    practice_plan_json = json.dumps({
        "scale_name": recommendation.scale_name,
        "scale_type": recommendation.scale_type,
        "focus_area": recommendation.focus_area,
        "reasoning": recommendation.reasoning,
        "strictness": recommendation.strictness,
        "sensitivity": recommendation.sensitivity,
        "generated_at": datetime.now().isoformat()
    })

    insert_query = text("""
        INSERT INTO fretcoach.ai_practice_plans (practice_id, user_id, practice_plan)
        VALUES (:practice_id, :user_id, :practice_plan)
    """)

    with engine.begin() as conn:
        conn.execute(
            insert_query,
            {
                "practice_id": practice_id,
                "user_id": user_id,
                "practice_plan": practice_plan_json
            }
        )

    return practice_id


async def save_practice_plan(user_id: str, recommendation: PracticeRecommendation) -> str:
    """Async wrapper for save_practice_plan_sync"""
    return save_practice_plan_sync(user_id, recommendation)


def delete_pending_plans(user_id: str) -> int:
    """
    Delete all unexecuted practice plans for a user.
    Used when user requests a new suggestion to clear old rejected plans.

    Args:
        user_id: The user's identifier

    Returns:
        Number of plans deleted
    """
    delete_query = text("""
        DELETE FROM fretcoach.ai_practice_plans
        WHERE user_id = :user_id
          AND executed_session_id IS NULL
    """)

    with engine.begin() as conn:
        result = conn.execute(delete_query, {"user_id": user_id})
        return result.rowcount


async def get_ai_practice_session(user_id: str, request_new: bool = False) -> Dict[str, Any]:
    """
    Main entry point for AI-driven practice session generation.
    Flow:
    1. Always analyze recent practice sessions (last 10)
    2. Check for pending (unexecuted) practice plan
    3. Give both to LLM: sessions + pending plan (if exists)
    4. LLM decides: keep pending plan OR generate new based on sessions
    5. If request_new=True, force deletion of pending plans and generate new

    LLM calls are traced via OpikTracer in generate_practice_recommendation().

    Args:
        user_id: The user's identifier
        request_new: If True, force new recommendation (deletes pending plans)

    Returns:
        Dictionary containing practice recommendation and metadata
    """
    # Step 1: Always analyze practice history (direct SQL - no LLM, no tracing needed)
    analysis = await analyze_practice_history(user_id)

    # Step 2: Check for existing pending practice plan
    pending_plan = get_pending_practice_plan(user_id)

    # Step 3: Get recent practice plans BEFORE deleting to avoid repeating suggestions
    recent_plans = get_recent_practice_plans(user_id, limit=5)

    # Step 4: If requesting new, delete all pending plans now
    if request_new and pending_plan:
        deleted_count = delete_pending_plans(user_id)
        if deleted_count > 0:
            print(f"[AI Coach] User requested new suggestion, deleted {deleted_count} pending plan(s)")
        pending_plan = None  # Clear it so LLM generates fresh

    # Step 5: Generate recommendation (single LLM call - traced with OpikTracer)
    # LLM sees: recent sessions, pending plan (if exists), and recent suggestions
    recommendation = await generate_practice_recommendation(
        user_id,
        analysis,
        recent_plans,
        pending_plan
    )

    # Step 6: Check if LLM decided to keep the pending plan
    # If LLM returns the same scale/type/focus as pending, reuse pending plan ID
    kept_pending = False
    practice_id = None

    if pending_plan:
        pending_details = pending_plan["plan"]
        if (recommendation.scale_name == pending_details["scale_name"] and
            recommendation.scale_type == pending_details["scale_type"] and
            recommendation.focus_area == pending_details["focus_area"]):
            # LLM chose to keep the pending plan
            practice_id = pending_plan["practice_id"]
            kept_pending = True
            print(f"[AI Coach] LLM kept existing pending plan: {practice_id}")

    # Step 7: Save as new practice plan if not keeping pending
    if not kept_pending:
        # Delete old pending plans if we're generating a new one
        if pending_plan:
            delete_pending_plans(user_id)
            print(f"[AI Coach] LLM generated different suggestion, deleted old pending plan")

        practice_id = await save_practice_plan(user_id, recommendation)
        print(f"[AI Coach] Generated new practice plan: {practice_id}")

    return {
        "practice_id": practice_id,
        "recommendation": {
            "scale_name": recommendation.scale_name,
            "scale_type": recommendation.scale_type,
            "focus_area": recommendation.focus_area,
            "reasoning": recommendation.reasoning,
            "strictness": recommendation.strictness,
            "sensitivity": recommendation.sensitivity,
        },
        "analysis": {
            "total_sessions": analysis["total_sessions"],
            "weakest_area": analysis["weakest_area"],
            "metrics": analysis["metrics_summary"]
        },
        "is_pending_plan": kept_pending
    }
