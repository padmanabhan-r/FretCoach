"""
Metrics endpoints for FretCoach API.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio

from ..models import SessionMetrics
from ..state import session_state

router = APIRouter()


@router.get("/session/metrics", response_model=SessionMetrics)
async def get_metrics():
    """Get current session metrics."""
    return SessionMetrics(
        is_running=session_state.is_running,
        current_note=session_state.current_note,
        pitch_accuracy=session_state.pitch_accuracy,
        scale_conformity=session_state.scale_conformity,
        timing_stability=session_state.timing_stability,
        target_scale=session_state.config["scale_name"] if session_state.config else "Not Set",
        debug_info=session_state.debug_info.to_dict(),
    )


@router.websocket("/ws/metrics")
async def websocket_metrics(websocket: WebSocket):
    """WebSocket endpoint for real-time metrics updates."""
    await websocket.accept()
    try:
        while True:
            if session_state.is_running:
                metrics = {
                    "current_note": session_state.current_note,
                    "pitch_accuracy": session_state.pitch_accuracy,
                    "scale_conformity": session_state.scale_conformity,
                    "timing_stability": session_state.timing_stability,
                }
                await websocket.send_json(metrics)
            await asyncio.sleep(0.1)  # Update 10 times per second
    except WebSocketDisconnect:
        pass
