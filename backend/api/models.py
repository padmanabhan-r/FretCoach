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
    scale_type: Optional[str] = "diatonic"  # "diatonic" or "pentatonic"
    ambient_lighting: Optional[bool] = True
    strictness: Optional[float] = 0.5
    sensitivity: Optional[float] = 0.5


class SessionMetrics(BaseModel):
    """Current session metrics"""
    is_running: bool
    current_note: str
    pitch_accuracy: float
    scale_conformity: float
    timing_stability: float
    target_scale: str
    debug_info: Optional[Dict] = None
