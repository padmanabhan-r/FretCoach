"""
Live Coach Router for FretCoach
Provides endpoints for real-time AI coaching feedback during practice sessions.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from ..services.live_coach_service import (
    generate_coaching_feedback,
    generate_session_summary
)

router = APIRouter(prefix="/live-coach", tags=["live-coach"])


class CoachingRequest(BaseModel):
    """Request model for coaching feedback."""
    pitch_accuracy: float = Field(..., ge=0, le=100, description="Pitch accuracy percentage")
    scale_conformity: float = Field(..., ge=0, le=100, description="Scale conformity percentage")
    timing_stability: float = Field(..., ge=0, le=100, description="Timing stability percentage")
    scale_name: str = Field(..., description="Name of the current scale")
    elapsed_seconds: int = Field(..., ge=0, description="Seconds elapsed in session")
    session_id: Optional[str] = Field(None, description="Optional session ID")
    total_notes_played: int = Field(0, ge=0, description="Total notes played so far")
    correct_notes: int = Field(0, ge=0, description="Number of notes in scale")
    wrong_notes: int = Field(0, ge=0, description="Number of notes outside scale")


class SummaryRequest(BaseModel):
    """Request model for session summary."""
    pitch_accuracy: float = Field(..., ge=0, le=100, description="Final pitch accuracy")
    scale_conformity: float = Field(..., ge=0, le=100, description="Final scale conformity")
    timing_stability: float = Field(..., ge=0, le=100, description="Final timing stability")
    scale_name: str = Field(..., description="Scale that was practiced")
    total_duration_seconds: int = Field(..., ge=0, description="Total session duration")
    session_id: Optional[str] = Field(None, description="Optional session ID")


@router.post("/feedback")
async def get_coaching_feedback(request: CoachingRequest):
    """
    Get real-time coaching feedback based on current session metrics.

    Returns specific, actionable feedback to help the guitarist improve.
    """
    try:
        result = await generate_coaching_feedback(
            pitch_accuracy=request.pitch_accuracy,
            scale_conformity=request.scale_conformity,
            timing_stability=request.timing_stability,
            scale_name=request.scale_name,
            elapsed_seconds=request.elapsed_seconds,
            session_id=request.session_id,
            total_notes_played=request.total_notes_played,
            correct_notes=request.correct_notes,
            wrong_notes=request.wrong_notes
        )
        return {
            "success": True,
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate coaching feedback: {str(e)}")


@router.post("/summary")
async def get_session_summary(request: SummaryRequest):
    """
    Get a summary of the completed practice session.

    Returns an encouraging summary with suggestions for next time.
    """
    try:
        result = await generate_session_summary(
            pitch_accuracy=request.pitch_accuracy,
            scale_conformity=request.scale_conformity,
            timing_stability=request.timing_stability,
            scale_name=request.scale_name,
            total_duration_seconds=request.total_duration_seconds,
            session_id=request.session_id
        )
        return {
            "success": True,
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate session summary: {str(e)}")
