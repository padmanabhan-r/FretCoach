"""
AI Mode endpoints for FretCoach API
Provides AI-driven practice session recommendations
LLM calls are traced via OpikTracer in ai_agent_service.py
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime

from ..services.ai_agent_service import get_ai_practice_session, engine
from sqlalchemy import text

router = APIRouter()


@router.post("/ai/recommend")
async def get_ai_recommendation(user_id: str = "default_user", request_new: bool = False) -> Dict[str, Any]:
    """
    Get AI-driven practice recommendation based on historical performance.
    LLM call is traced via OpikTracer in ai_agent_service.

    Args:
        user_id: The user identifier (default: "default_user")
        request_new: If True, generate a new recommendation even if pending plan exists

    Returns:
        Practice recommendation with scale, focus area, and reasoning
    """
    try:
        result = await get_ai_practice_session(user_id, request_new=request_new)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate AI recommendation: {str(e)}")


@router.post("/ai/session/start")
async def start_ai_session(user_id: str = "default_user", request_new: bool = False) -> Dict[str, Any]:
    """
    Start an AI-recommended practice session.
    LLM call is traced via OpikTracer in ai_agent_service.

    This endpoint:
    1. Gets AI recommendation (or returns pending plan if exists)
    2. Configures the session with recommended settings

    Args:
        user_id: The user identifier
        request_new: If True, generate a new recommendation even if pending plan exists

    Returns:
        Session configuration and start status
    """
    try:
        # Get AI recommendation (checks for pending plan first, unless request_new=True)
        recommendation_result = await get_ai_practice_session(user_id, request_new=request_new)

        recommendation = recommendation_result["recommendation"]

        return {
            "success": True,
            "ai_mode": True,
            "practice_id": recommendation_result["practice_id"],
            "config": {
                "scale_name": recommendation["scale_name"],
                "scale_type": recommendation["scale_type"],
                "strictness": recommendation["strictness"],
                "sensitivity": recommendation["sensitivity"],
            },
            "focus_area": recommendation["focus_area"],
            "reasoning": recommendation["reasoning"],
            "analysis": recommendation_result["analysis"],
            "is_pending_plan": recommendation_result.get("is_pending_plan", False)
        }
    except Exception as e:
        import traceback
        print(f"Error in AI session start: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to start AI session: {str(e)}")


@router.get("/ai/status")
async def get_ai_status(user_id: str = "default_user") -> Dict[str, Any]:
    """
    Check if there's a pending AI-generated practice plan

    Args:
        user_id: The user identifier

    Returns:
        Status of pending practice plans
    """
    try:
        import json

        query = text("""
            SELECT practice_id, practice_plan, generated_at
            FROM fretcoach.ai_practice_plans
            WHERE user_id = :user_id AND executed_session_id IS NULL
            ORDER BY generated_at DESC
            LIMIT 1
        """)

        with engine.connect() as conn:
            result = conn.execute(query, {"user_id": user_id})
            row = result.fetchone()

            if row:
                plan = json.loads(row[1])
                return {
                    "has_pending_plan": True,
                    "practice_id": str(row[0]),
                    "plan": plan,
                    "generated_at": row[2].isoformat() if row[2] else None
                }
            else:
                return {
                    "has_pending_plan": False
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check AI status: {str(e)}")


@router.post("/ai/plan/{practice_id}/execute")
async def mark_plan_executed(practice_id: str, session_id: str) -> Dict[str, Any]:
    """
    Mark a practice plan as executed by linking it to a session

    Args:
        practice_id: The practice plan UUID
        session_id: The session ID that executed this plan

    Returns:
        Success status
    """
    try:
        query = text("""
            UPDATE fretcoach.ai_practice_plans
            SET executed_session_id = :session_id
            WHERE practice_id = :practice_id
        """)

        with engine.begin() as conn:
            conn.execute(query, {
                "practice_id": practice_id,
                "session_id": session_id
            })

        return {
            "success": True,
            "message": "Practice plan marked as executed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark plan as executed: {str(e)}")
