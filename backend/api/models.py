"""
Pydantic models for FretCoach API
Defines request/response schemas for all endpoints
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any


class AudioDevice(BaseModel):
    """Audio device information"""
    index: int
    name: str
    max_input_channels: int
    max_output_channels: int
    default_samplerate: float


class AudioConfig(BaseModel):
    """Audio and scale configuration"""
    input_device: int
    output_device: int
    guitar_channel: int
    channels: int
    scale_name: str
    scale_type: Optional[str] = "natural"  # "natural" or "pentatonic"
    ambient_lighting: Optional[bool] = True
    strictness: Optional[float] = 0.5
    sensitivity: Optional[float] = 0.5
    user_id: Optional[str] = "default_user"  # User identifier for session tracking


class SessionConfig(BaseModel):
    """Session configuration for metric toggles"""
    enabled_metrics: Dict[str, bool] = {
        "pitch_accuracy": True,
        "scale_conformity": True,
        "timing_stability": True
    }


class SessionMetrics(BaseModel):
    """Current session metrics"""
    is_running: bool
    current_note: str
    pitch_accuracy: float
    scale_conformity: float
    timing_stability: float
    target_scale: str
    debug_info: Optional[Dict] = None


class AIPracticeRecommendation(BaseModel):
    """AI-generated practice recommendation"""
    practice_id: str
    scale_name: str
    scale_type: str
    focus_area: str
    reasoning: str
    strictness: float
    sensitivity: float
    analysis: Optional[str] = None


class AIPracticePlan(BaseModel):
    """AI practice plan from database"""
    practice_id: str
    user_id: str
    practice_plan: str
    generated_at: str
    executed_session_id: Optional[str] = None
