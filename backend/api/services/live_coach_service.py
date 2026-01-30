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
from opik.integrations.langchain import OpikTracer
from opik import track

# Load environment variables
load_dotenv(find_dotenv())

# Get deployment type for tracing tags
DEPLOYMENT_TYPE = os.getenv("DEPLOYMENT_TYPE", "fretcoach-studio")  # Default to studio
DEPLOYMENT_PREFIX = "studio" if "studio" in DEPLOYMENT_TYPE.lower() else "portable"

# Initialize LLM - using a fast model for real-time feedback
FEEDBACK_MODEL_NAME = "gpt-4o-mini"
TTS_MODEL_NAME = "gpt-4o-mini-tts"

live_coach_model = ChatOpenAI(
    model=FEEDBACK_MODEL_NAME,
    temperature=0.9,  # Higher creativity for varied feedback
    max_tokens=100  # Room for 30-word feedback with context
)

# Initialize OpenAI client for TTS
openai_client = AsyncOpenAI()

# Global audio player instance
_audio_player = None


async def get_audio_player():
    """Get or create a singleton audio player instance with optimized settings."""
    global _audio_player
    if _audio_player is None:
        # LocalAudioPlayer with default settings
        # Note: OpenAI's LocalAudioPlayer doesn't expose buffer configuration,
        # but using PCM format with streaming helps reduce latency issues
        _audio_player = LocalAudioPlayer()
    return _audio_player


def get_opik_config(session_id: str, trace_name: str, mode: str = "manual-mode") -> dict:
    """
    Create Opik config for LangChain calls tied to session_id.
    Tags include: fretcoach-core, model name, mode (ai-mode/manual-mode), and deployment type.
    Thread ID format: {session_id}-live-aicoach-feedback

    All live coaching feedback for a session goes into the same thread,
    identified by the session_id.

    Args:
        session_id: Session identifier for tracking and threading
        trace_name: Name of the trace (e.g., "live-feedback", "session-summary")
        mode: Either "ai-mode" or "manual-mode" (defaults to "manual-mode")
    """
    # Build comprehensive tags for tracing
    tags = [
        "fretcoach-core",
        FEEDBACK_MODEL_NAME,
        mode,
        DEPLOYMENT_TYPE,
        trace_name
    ]

    tracer = OpikTracer(
        tags=tags,
        metadata={"session_id": session_id}
    )

    # Use session_id for thread to group all feedback for this session
    return {
        "callbacks": [tracer],
        "configurable": {"thread_id": f"{session_id}-live-aicoach-feedback"}
    }

# System prompt for coaching
COACHING_SYSTEM_PROMPT = """You are a direct guitar coach giving quick real-time feedback.

Your feedback MUST be 1-2 sentences, maximum 30 words total.

Format: "[What's good], but [what's weak] - [specific actionable fix]"

Metric interpretations and specific fixes:
- Pitch Accuracy: How cleanly notes are fretted (low = finger pressure issues)
  → Fix: "ease finger pressure" or "focus on clean fretting"

- Scale Conformity: Playing correct scale notes across fretboard positions (low = stuck in one position or wrong notes)
  → Fix: "explore positions 5-7" or "move up the fretboard" or "try higher positions now"

- Timing Stability: Consistency of note spacing (low = rushing, dragging, uneven rhythm)
  → Fix: "use a metronome" or "practice with metronome at 60 BPM" or "slow down and count"

Examples:
- "Timing is solid at 98%, but scale conformity at 73% means you're stuck. Move up to the 5th position now."
- "Pitch is excellent and timing good, but scale conformity needs work. Explore different fretboard positions - try 7th and 9th frets."
- "Great scale coverage, but timing stability is low at 45%. Practice with a metronome to build consistency."

Be direct, conversational, and vary your wording. Maximum 30 words."""

COACHING_USER_TEMPLATE = """Metrics: Pitch {pitch_accuracy}%, Scale {scale_conformity}%, Timing {timing_stability}%
Strongest: {strongest_area_name} ({strongest_score}%)
Weakest: {weakest_area_name} ({weakest_score}%)

Give 1-2 sentences (max 30 words) - what's good, what's weak, specific actionable fix:"""


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


@track(
    name="live-coach-tts",
    tags=["fretcoach-core", TTS_MODEL_NAME, "live-coach", DEPLOYMENT_TYPE, "tts"]
)
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
            "voice": "coral",
            "speed": 1.15,
            "format": "pcm"
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
    wrong_notes: int = 0,
    mode: str = "manual-mode"
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
        mode: Either "ai-mode" or "manual-mode" (defaults to "manual-mode")

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
    opik_config = get_opik_config(session_id or "unknown", "live-feedback", mode)

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
    session_id: Optional[str] = None,
    mode: str = "manual-mode"
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
        mode: Either "ai-mode" or "manual-mode" (defaults to "manual-mode")

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
    opik_config = get_opik_config(session_id or "unknown", "session-summary", mode)

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
