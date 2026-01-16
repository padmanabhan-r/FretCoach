"""
Configuration endpoints for FretCoach API.
"""

from fastapi import APIRouter

from ..models import AudioConfig
from ..state import session_state
from ..services.config_service import save_config_to_file, load_config_from_file

router = APIRouter()


@router.post("/config")
async def save_config(config: AudioConfig):
    """Save audio and scale configuration."""
    session_state.config = config.model_dump()

    # Save to file for persistence
    save_config_to_file(session_state.config)

    return {"success": True, "config": session_state.config}


@router.get("/config")
async def get_config():
    """Get current configuration."""
    if session_state.config:
        return session_state.config

    # Try to load from file
    loaded_config = load_config_from_file()
    if loaded_config:
        session_state.config = loaded_config
        return session_state.config

    return None
