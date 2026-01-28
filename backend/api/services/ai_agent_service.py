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
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def get_opik_config(user_id: str, trace_name: str, practice_id: str = None) -> dict:
    """Create Opik config for LangChain calls tied to user session"""
    metadata = {"user_id": user_id}
    if practice_id:
        metadata["practice_id"] = practice_id

    tracer = OpikTracer(
        tags=["ai-mode", trace_name],
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


def get_pending_practice_plan(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Check if there's an unexecuted practice plan for the user.
    Returns the pending plan if exists and is recent (< 24 hours old), None otherwise.
    """
    query = text("""
        SELECT practice_id, practice_plan, generated_at
        FROM fretcoach.ai_practice_plans
        WHERE user_id = :user_id
          AND executed_session_id IS NULL
          AND generated_at > :cutoff_time
        ORDER BY generated_at DESC
        LIMIT 1
    """)

    cutoff_time = datetime.now() - timedelta(hours=24)

    with engine.connect() as conn:
        result = conn.execute(query, {"user_id": user_id, "cutoff_time": cutoff_time})
        row = result.fetchone()

        if row:
            try:
                # Try to parse the JSON plan
                plan_data = json.loads(row[1]) if row[1] else None
                if plan_data and isinstance(plan_data, dict):
                    # Only return if it's a properly structured JSON dict
                    return {
                        "practice_id": str(row[0]),
                        "plan": plan_data,
                        "generated_at": row[2]
                    }
            except (json.JSONDecodeError, TypeError) as e:
                # If JSON is invalid (plain text format), ignore this pending plan
                # This allows the system to generate a fresh recommendation
                print(f"Warning: Skipping non-JSON pending practice plan {row[0]}, will generate new recommendation")
                pass
    return None


def get_recent_sessions(user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get recent practice sessions for analysis.
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
    analysis: Dict[str, Any]
) -> PracticeRecommendation:
    """
    Generate structured practice recommendation based on analysis.
    Single LLM call with structured output. Traced with OpikTracer.

    Args:
        user_id: The user's identifier
        analysis: Dictionary containing practice history analysis

    Returns:
        Structured practice recommendation
    """
    # Use structured output to generate recommendation - SINGLE LLM CALL
    structured_llm = model.with_structured_output(PracticeRecommendation)

    # Check if there's a pending plan to include in the context
    pending_plan_context = ""
    if analysis.get('pending_plan'):
        pending_plan = analysis['pending_plan']
        pending_plan_context = f"""

PENDING PRACTICE PLAN:
There is an unexecuted practice plan from {pending_plan['generated_at']}:
- Scale: {pending_plan['plan']['scale_name']} ({pending_plan['plan']['scale_type']})
- Focus: {pending_plan['plan']['focus_area']}
- Reasoning: {pending_plan['plan']['reasoning']}
- Strictness: {pending_plan['plan']['strictness']}
- Sensitivity: {pending_plan['plan']['sensitivity']}

DECISION REQUIRED:
Review this pending plan in context of the current practice history. You have two options:
1. If the pending plan is still relevant and it is the recent one, it must be given the priority and you can continue with it (same or similar recommendation)
2. If the user's needs have changed or a different focus would be better, generate a new recommendation
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

RECENT SESSIONS:
{json.dumps(analysis['recent_sessions'][:3], indent=2) if analysis['recent_sessions'] else 'No recent sessions'}{pending_plan_context}

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


async def get_ai_practice_session(user_id: str) -> Dict[str, Any]:
    """
    Main entry point for AI-driven practice session generation.
    Optimized flow:
    1. Check for pending (unexecuted) practice plan first
    2. If pending plan exists and is recent, return it
    3. Otherwise, analyze history and generate new recommendation

    LLM calls are traced via OpikTracer in generate_practice_recommendation().

    Args:
        user_id: The user's identifier

    Returns:
        Dictionary containing practice recommendation and metadata
    """
    # Step 1: Check for existing pending practice plan
    pending_plan = get_pending_practice_plan(user_id)
    if pending_plan:
        print(f"[AI Coach] Found pending plan from {pending_plan['generated_at']}, including in AI analysis")

    # Step 2: Analyze practice history (direct SQL - no LLM, no tracing needed)
    analysis = await analyze_practice_history(user_id)

    # Add pending plan to analysis context if it exists
    if pending_plan:
        analysis['pending_plan'] = pending_plan

    # Step 3: Generate recommendation (single LLM call - traced with OpikTracer)
    recommendation = await generate_practice_recommendation(user_id, analysis)

    # Step 4: Save practice plan
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
        "is_pending_plan": False
    }
