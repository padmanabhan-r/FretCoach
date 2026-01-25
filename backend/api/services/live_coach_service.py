"""
Live Coach Service for FretCoach
Provides real-time coaching feedback during practice sessions.
Uses LangChain for LLM integration and Opik for tracing.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import os
import asyncio
from dotenv import load_dotenv, find_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Import OpenAI for TTS
from openai import AsyncOpenAI
from openai.helpers import LocalAudioPlayer

# Import Opik for tracking with LangChain integration
try:
    from opik.integrations.langchain import OpikTracer
    from opik import track
    OPIK_ENABLED = True
except ImportError:
    OpikTracer = None
    track = lambda **kwargs: lambda f: f  # No-op decorator if Opik not available
    OPIK_ENABLED = False

# Load environment variables
load_dotenv(find_dotenv())

# Initialize LLM - using a fast model for real-time feedback
live_coach_model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,  # Slightly more creative for motivational feedback
    max_tokens=200  # Room for 2-3 sentences with context
)

# Initialize OpenAI client for TTS
openai_client = AsyncOpenAI()

# Global audio player instance
_audio_player = None


async def get_audio_player():
    """Get or create a singleton audio player instance."""
    global _audio_player
    if _audio_player is None:
        _audio_player = LocalAudioPlayer()
    return _audio_player


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

# System prompt for coaching
COACHING_SYSTEM_PROMPT = """You are an energetic, direct guitar coach giving real-time feedback during practice.

Your feedback MUST have 3 parts in 2-3 sentences total:
1. ACKNOWLEDGE strength: Quickly name what's going well (1 metric that's highest)
2. IDENTIFY problem: Point out what's struggling (the weakest metric)
3. FIX IT NOW: Give ONE specific action to improve the weak area immediately

Interpretation guide:
- Pitch Accuracy: How cleanly notes are being fretted. Low = pressing too hard/soft, poor finger placement
- Scale Conformity: Whether notes are in the chosen scale and whether they are covering the full range of the scale. Low = playing wrong notes or playing in just one position, not knowing the scale positions
- Timing Stability: Consistency of note spacing. Low = rushing, dragging, or uneven rhythm

Be conversational and direct - you're talking to a student during practice, not writing a report.
Use "you" and "your". Be specific about numbers when helpful."""

COACHING_USER_TEMPLATE = """Session metrics after {elapsed_time} practicing {scale_name}:

Pitch Accuracy: {pitch_accuracy}% ({pitch_assessment})
Scale Conformity: {scale_conformity}% ({scale_assessment})
Timing Stability: {timing_stability}% ({timing_assessment})

Strongest area: {strongest_area_name} at {strongest_score}%
Weakest area: {weakest_area_name} at {weakest_score}%
Notes played: {notes_played} ({correct_notes} correct, {wrong_notes} wrong)

Give feedback that acknowledges the strength, identifies the weakness, and tells them exactly what to fix right now:"""


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


@track(name="live-coach-tts", tags=["tts", "live-coach"])
async def generate_and_play_tts(
    feedback_text: str,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate and play TTS audio for coaching feedback in real-time.
    Traced with Opik for monitoring.

    Args:
        feedback_text: The coaching feedback text to convert to speech
        session_id: Optional session ID for tracking

    Returns:
        Dictionary containing TTS metadata and status
    """
    try:
        # Get the singleton audio player
        player = await get_audio_player()

        # Generate and stream TTS audio
        async with openai_client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="coral",  # Coral is more energetic and natural than onyx
            input=feedback_text,
            instructions="You're an energetic guitar coach giving quick, direct feedback during practice. Speak naturally and conversationally, like you're in the room with the student. Keep the energy up and pace brisk.",
            response_format="pcm",
            speed=1.15,  # 15% faster for more dynamic delivery
        ) as response:
            # Play audio in real-time using the singleton player
            await player.play(response)

        return {
            "status": "played",
            "text_length": len(feedback_text),
            "model": "gpt-4o-mini-tts",
            "voice": "echo",
            "speed": 1.15
        }

    except Exception as e:
        # Log error but don't fail the entire feedback generation
        return {
            "status": "failed",
            "error": str(e)
        }


async def stop_audio_playback() -> Dict[str, Any]:
    """Stop any currently playing audio."""
    try:
        player = await get_audio_player()
        await player.stop()
        return {"status": "stopped"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}


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

    # Identify the strongest and weakest areas
    metrics = {
        "Pitch Accuracy": pitch_accuracy,
        "Scale Conformity": scale_conformity,
        "Timing Stability": timing_stability
    }
    weakest_area_name = min(metrics, key=metrics.get)
    weakest_score = metrics[weakest_area_name]
    strongest_area_name = max(metrics, key=metrics.get)
    strongest_score = metrics[strongest_area_name]

    # Get assessments for each metric
    pitch_assessment = get_metric_assessment(pitch_accuracy)
    scale_assessment = get_metric_assessment(scale_conformity)
    timing_assessment = get_metric_assessment(timing_stability)

    # Get Opik config tied to session_id for tracing
    opik_config = get_opik_config(session_id or "unknown", "live-feedback")

    # Format the user message with all metrics
    user_message = COACHING_USER_TEMPLATE.format(
        pitch_accuracy=round(pitch_accuracy),
        scale_conformity=round(scale_conformity),
        timing_stability=round(timing_stability),
        pitch_assessment=pitch_assessment,
        scale_assessment=scale_assessment,
        timing_assessment=timing_assessment,
        scale_name=scale_name,
        elapsed_time=elapsed_time,
        strongest_area_name=strongest_area_name,
        strongest_score=round(strongest_score),
        weakest_area_name=weakest_area_name,
        weakest_score=round(weakest_score),
        notes_played=total_notes_played,
        correct_notes=correct_notes,
        wrong_notes=wrong_notes
    )

    # Generate feedback with explicit messages (better Opik tracing visibility)
    response = await live_coach_model.ainvoke(
        [
            {"role": "system", "content": COACHING_SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        config=opik_config
    )
    feedback = response.content

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
