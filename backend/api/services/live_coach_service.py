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

# Load environment variables
load_dotenv(find_dotenv())

# Initialize LLM - using a fast model for real-time feedback
live_coach_model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,  # Slightly more creative for motivational feedback
    max_tokens=150  # Keep responses short
)

# Coaching prompt template
COACHING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a supportive guitar coach providing real-time feedback during a practice session.
Your feedback should be:
- SHORT (1-2 sentences max)
- MOTIVATIONAL and encouraging
- SPECIFIC about what to focus on
- ACTIONABLE with clear guidance

You're like a basketball coach on the sideline - brief, direct, and encouraging.

Focus areas based on metrics:
- Low pitch accuracy (<50%): Focus on hitting notes cleanly
- Low scale conformity (<50%): Stay within the scale, explore the fretboard
- Low timing stability (<50%): Keep steady rhythm, use a metronome mentally

Performance levels:
- Excellent (>70%): Celebrate, push for more challenge
- Good (50-70%): Encourage, minor adjustments
- Average (20-50%): Focus on fundamentals
- Bad (<20%): Simplify, slow down, breathe"""),
    ("human", """Current session stats after {elapsed_time}:
- Pitch Accuracy: {pitch_accuracy}%
- Scale Conformity: {scale_conformity}%
- Timing Stability: {timing_stability}%
- Overall Performance: {overall_performance}
- Current Scale: {scale_name}

Give brief, motivational coaching feedback for this guitarist:""")
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


@track(name="generate_live_coaching_feedback")
async def generate_coaching_feedback(
    pitch_accuracy: float,
    scale_conformity: float,
    timing_stability: float,
    scale_name: str,
    elapsed_seconds: int,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate live coaching feedback based on current session metrics.

    Args:
        pitch_accuracy: Current pitch accuracy (0-100)
        scale_conformity: Current scale conformity (0-100)
        timing_stability: Current timing stability (0-100)
        scale_name: Name of the current scale being practiced
        elapsed_seconds: Time elapsed in the session
        session_id: Optional session ID for tracking

    Returns:
        Dictionary containing feedback and metadata
    """
    # Generate thread ID for Opik tracking
    thread_id = f"live-coach-{session_id or 'unknown'}-{datetime.now().strftime('%H%M%S')}"

    if OPIK_ENABLED and opik_context:
        opik_context.update_current_trace(thread_id=thread_id)

    # Calculate overall performance
    overall_score = (pitch_accuracy + scale_conformity + timing_stability) / 3
    overall_performance = get_performance_label(overall_score)

    # Format elapsed time
    elapsed_time = format_elapsed_time(elapsed_seconds)

    # Generate feedback using the chain
    feedback = await coaching_chain.ainvoke({
        "pitch_accuracy": round(pitch_accuracy),
        "scale_conformity": round(scale_conformity),
        "timing_stability": round(timing_stability),
        "overall_performance": overall_performance,
        "scale_name": scale_name,
        "elapsed_time": elapsed_time
    })

    # Identify the weakest area for additional context
    metrics = {
        "pitch": pitch_accuracy,
        "scale": scale_conformity,
        "timing": timing_stability
    }
    weakest_area = min(metrics, key=metrics.get)

    return {
        "feedback": feedback.strip(),
        "overall_performance": overall_performance,
        "overall_score": round(overall_score),
        "weakest_area": weakest_area,
        "elapsed_time": elapsed_time,
        "timestamp": datetime.now().isoformat()
    }


@track(name="generate_session_summary")
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
    thread_id = f"session-summary-{session_id or 'unknown'}"

    if OPIK_ENABLED and opik_context:
        opik_context.update_current_trace(thread_id=thread_id)

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

    summary = await summary_chain.ainvoke({
        "duration": duration,
        "scale_name": scale_name,
        "pitch_accuracy": round(pitch_accuracy),
        "scale_conformity": round(scale_conformity),
        "timing_stability": round(timing_stability),
        "overall_performance": overall_performance
    })

    return {
        "summary": summary.strip(),
        "overall_performance": overall_performance,
        "overall_score": round(overall_score),
        "duration": duration,
        "timestamp": datetime.now().isoformat()
    }
