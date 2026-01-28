"""
Session management endpoints for FretCoach API
"""

from fastapi import APIRouter
import sys
import os

# Import Opik for tracking
from opik import track

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'core'))

from session_logger import get_session_logger

from ..state import session_state, audio_state, AUDIO_CONSTANTS
from ..services.session_service import start_session_impl, stop_session_impl

router = APIRouter()


@router.post("/session/start")
async def start_session():
    """Start the guitar learning session"""
    return start_session_impl(session_state, audio_state, AUDIO_CONSTANTS)


@router.post("/session/stop")
async def stop_session():
    """Stop the guitar learning session"""
    return stop_session_impl(session_state, audio_state)
