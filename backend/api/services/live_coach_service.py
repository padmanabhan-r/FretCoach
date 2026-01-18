"""
Live Coach Service for FretCoach
Provides real-time coaching feedback during practice sessions.
Uses LangChain for LLM integration and Opik for tracing.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import os
from dotenv import load_dotenv, find_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Import Opik for tracking with LangChain integration
try:
    from opik.integrations.langchain import OpikTracer
    OPIK_ENABLED = True
except ImportError:
    OpikTracer = None
    OPIK_ENABLED = False

# Load environment variables
load_dotenv(find_dotenv())

# Initialize LLM - using a fast model for real-time feedback
live_coach_model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,  # Slightly more creative for motivational feedback
    max_tokens=150  # Keep responses short
)


def get_opik_config(session_id: str, trace_name: str) -> dict:
    """Create Opik config for LangChain calls tied to session_id"""
    if not OPIK_ENABLED or not OpikTracer:
        return {}

    tracer = OpikTracer(
        tags=["live-coach", trace_name],
        metadata={"session_id": session_id}
    )
    return {
        "callbacks": [tracer],
        "configurable": {"thread_id": f"session-{session_id}"}
    }

# Coaching prompt template
COACHING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a direct, practical guitar coach analyzing real-time playing data.

Your feedback must be:
- CORRECTIVE: Address the actual problem shown in the metrics
- SPECIFIC: Reference the exact metric that needs work
- ACTIONABLE: Give one concrete technique to try RIGHT NOW
- BRIEF: 1-2 sentences maximum

DO NOT:
- Use generic motivational phrases like "Great job!" or "Keep it up!"
- Be vague about what needs improvement
- Give multiple suggestions at once

Interpretation guide:
- Pitch Accuracy: How cleanly notes are being fretted. Low = pressing too hard/soft, poor finger placement
- Scale Conformity: Whether notes are in the chosen scale. Low = playing wrong notes, not knowing the scale positions
- Timing Stability: Consistency of note spacing. Low = rushing, dragging, or uneven rhythm

For the WEAKEST metric, provide a specific corrective instruction."""),
    ("human", """Session metrics after {elapsed_time} practicing {scale_name}:

Pitch Accuracy: {pitch_accuracy}% ({pitch_assessment})
Scale Conformity: {scale_conformity}% ({scale_assessment})
Timing Stability: {timing_stability}% ({timing_assessment})

Weakest area: {weakest_area_name} at {weakest_score}%
Notes played so far: {notes_played}
Correct notes: {correct_notes} | Wrong notes: {wrong_notes}

Give ONE specific corrective instruction for the weakest metric:""")
])

# Create the chain
coaching_chain = COACHING_PROMPT | live_coach_model | StrOutputParser()


def get_performance_label(score: float) -> str:
    """Get performance label based on score."""
    if score > 70:
        return "Excellent"
    elif score >= 50:
        return "Good"
    elif score >= 20:
        return "Average"
    return "Needs Work"


def format_elapsed_time(seconds: int) -> str:
    """Format elapsed time for display."""
    if seconds < 60:
        return f"{seconds} seconds"
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    if remaining_seconds == 0:
        return f"{minutes} minute{'s' if minutes > 1 else ''}"
    return f"{minutes}m {remaining_seconds}s"


def get_metric_assessment(score: float) -> str:
    """Get a brief assessment label for a metric score."""
    if score >= 80:
        return "excellent"
    elif score >= 60:
        return "good"
    elif score >= 40:
        return "needs work"
    elif score >= 20:
        return "struggling"
    return "very low"


async def generate_coaching_feedback(
    pitch_accuracy: float,
    scale_conformity: float,
    timing_stability: float,
    scale_name: str,
    elapsed_seconds: int,
    session_id: Optional[str] = None,
    total_notes_played: int = 0,
    correct_notes: int = 0,
    wrong_notes: int = 0
) -> Dict[str, Any]:
    """
    Generate live coaching feedback based on current session metrics.
    Traced with OpikTracer tied to session_id.

    Args:
        pitch_accuracy: Current pitch accuracy (0-100)
        scale_conformity: Current scale conformity (0-100)
        timing_stability: Current timing stability (0-100)
        scale_name: Name of the current scale being practiced
        elapsed_seconds: Time elapsed in the session
        session_id: Optional session ID for tracking
        total_notes_played: Total number of notes played so far
        correct_notes: Number of notes in scale
        wrong_notes: Number of notes outside scale

    Returns:
        Dictionary containing feedback and metadata
    """
    # Calculate overall performance
    overall_score = (pitch_accuracy + scale_conformity + timing_stability) / 3
    overall_performance = get_performance_label(overall_score)

    # Format elapsed time
    elapsed_time = format_elapsed_time(elapsed_seconds)

    # Identify the weakest area with detailed info
    metrics = {
        "Pitch Accuracy": pitch_accuracy,
        "Scale Conformity": scale_conformity,
        "Timing Stability": timing_stability
    }
    weakest_area_name = min(metrics, key=metrics.get)
    weakest_score = metrics[weakest_area_name]

    # Get assessments for each metric
    pitch_assessment = get_metric_assessment(pitch_accuracy)
    scale_assessment = get_metric_assessment(scale_conformity)
    timing_assessment = get_metric_assessment(timing_stability)

    # Get Opik config tied to session_id for tracing
    opik_config = get_opik_config(session_id or "unknown", "live-feedback")

    # Generate feedback using the chain (traced with OpikTracer)
    feedback = await coaching_chain.ainvoke(
        {
            "pitch_accuracy": round(pitch_accuracy),
            "scale_conformity": round(scale_conformity),
            "timing_stability": round(timing_stability),
            "pitch_assessment": pitch_assessment,
            "scale_assessment": scale_assessment,
            "timing_assessment": timing_assessment,
            "scale_name": scale_name,
            "elapsed_time": elapsed_time,
            "weakest_area_name": weakest_area_name,
            "weakest_score": round(weakest_score),
            "notes_played": total_notes_played,
            "correct_notes": correct_notes,
            "wrong_notes": wrong_notes
        },
        config=opik_config
    )

    # Map to simple key for frontend
    weakest_key_map = {
        "Pitch Accuracy": "pitch",
        "Scale Conformity": "scale",
        "Timing Stability": "timing"
    }

    return {
        "feedback": feedback.strip(),
        "overall_performance": overall_performance,
        "overall_score": round(overall_score),
        "weakest_area": weakest_key_map[weakest_area_name],
        "elapsed_time": elapsed_time,
        "timestamp": datetime.now().isoformat()
    }


async def generate_session_summary(
    pitch_accuracy: float,
    scale_conformity: float,
    timing_stability: float,
    scale_name: str,
    total_duration_seconds: int,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a summary at the end of a practice session.
    Traced with OpikTracer tied to session_id.

    Args:
        pitch_accuracy: Final pitch accuracy (0-100)
        scale_conformity: Final scale conformity (0-100)
        timing_stability: Final timing stability (0-100)
        scale_name: Name of the scale practiced
        total_duration_seconds: Total session duration
        session_id: Optional session ID for tracking

    Returns:
        Dictionary containing session summary
    """
    overall_score = (pitch_accuracy + scale_conformity + timing_stability) / 3
    overall_performance = get_performance_label(overall_score)
    duration = format_elapsed_time(total_duration_seconds)

    summary_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a supportive guitar coach giving a brief end-of-session summary.
Keep it to 2-3 short sentences. Be encouraging and highlight one thing to work on next time."""),
        ("human", """Session complete!
Duration: {duration}
Scale: {scale_name}
Final Stats:
- Pitch Accuracy: {pitch_accuracy}%
- Scale Conformity: {scale_conformity}%
- Timing Stability: {timing_stability}%
- Overall: {overall_performance}

Give a brief, encouraging session summary:""")
    ])

    summary_chain = summary_prompt | live_coach_model | StrOutputParser()

    # Get Opik config tied to session_id for tracing
    opik_config = get_opik_config(session_id or "unknown", "session-summary")

    summary = await summary_chain.ainvoke(
        {
            "duration": duration,
            "scale_name": scale_name,
            "pitch_accuracy": round(pitch_accuracy),
            "scale_conformity": round(scale_conformity),
            "timing_stability": round(timing_stability),
            "overall_performance": overall_performance
        },
        config=opik_config
    )

    return {
        "summary": summary.strip(),
        "overall_performance": overall_performance,
        "overall_score": round(overall_score),
        "duration": duration,
        "timestamp": datetime.now().isoformat()
    }
