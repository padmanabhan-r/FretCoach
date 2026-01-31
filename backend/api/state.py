"""
Application state management for FretCoach API.
Uses dataclasses for cleaner, type-safe state management.
"""

from dataclasses import dataclass, field
from typing import Optional, Any, Dict
from collections import deque
import threading
import sys
import os

# Add core to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))

from audio_metrics import QualityState, BulbState

# Application constants
AUDIO_CONSTANTS = {
    "SAMPLE_RATE": 44100,
    "BLOCK_SIZE": 128,
    "ANALYSIS_WINDOW_SEC": 0.30,
    "TUYA_UPDATE_INTERVAL": 0.30,
    "HUE_EPSILON": 5,
    "PHRASE_WINDOW": 0.8,
}


@dataclass
class DebugInfo:
    """Debug information from pitch detection."""
    detected_hz: float = 0.0
    detected_midi: float = 0.0
    pitch_class: Optional[int] = None
    in_scale: bool = False
    raw_pitch: float = 0.0
    raw_timing: float = 0.0
    scale_coverage: float = 0.0
    notes_played_count: int = 0
    unique_notes_used: int = 0
    scale_total_notes: int = 0
    notes_for_timing_analysis: int = 0
    correct_notes: int = 0
    wrong_notes: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "detected_hz": self.detected_hz,
            "detected_midi": self.detected_midi,
            "pitch_class": self.pitch_class,
            "in_scale": self.in_scale,
            "raw_pitch": self.raw_pitch,
            "raw_timing": self.raw_timing,
            "scale_coverage": self.scale_coverage,
            "notes_played_count": self.notes_played_count,
            "unique_notes_used": self.unique_notes_used,
            "scale_total_notes": self.scale_total_notes,
            "notes_for_timing_analysis": self.notes_for_timing_analysis,
            "correct_notes": self.correct_notes,
            "wrong_notes": self.wrong_notes,
        }


@dataclass
class SessionState:
    """State visible to the UI/API consumers."""
    is_running: bool = False
    config: Optional[Dict[str, Any]] = None
    current_note: str = "-"
    pitch_accuracy: float = 0.0
    scale_conformity: float = 0.0
    timing_stability: float = 0.0
    debug_info: DebugInfo = field(default_factory=DebugInfo)

    def reset_metrics(self):
        """Reset metrics when session stops."""
        self.current_note = "-"
        self.pitch_accuracy = 0.0
        self.scale_conformity = 0.0
        self.timing_stability = 0.0
        self.debug_info = DebugInfo()


@dataclass
class AudioState:
    """State for audio processing during a session."""
    # Audio stream resources
    stream: Any = None
    buffer: Optional[deque] = None
    buffer_lock: Optional[threading.Lock] = None
    processing_task: Optional[threading.Thread] = None

    # Session tracking
    session_id: Optional[str] = None
    session_logger: Any = None

    # Quality tracking (uses shared module)
    quality: QualityState = field(default_factory=QualityState)
    bulb: BulbState = field(default_factory=BulbState)

    # Config values (copied from session config for easy access)
    strictness: float = 0.5
    sensitivity: float = 0.5
    ambient_lighting: bool = True
    enabled_metrics: Dict[str, bool] = field(default_factory=lambda: {
        "pitch_accuracy": True,
        "scale_conformity": True,
        "timing_stability": True
    })

    def reset(self):
        """Reset state for a new session."""
        self.quality.reset()
        self.bulb = BulbState()

    def cleanup(self):
        """Clean up resources when session ends."""
        if self.stream is not None:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None

        if self.processing_task is not None:
            self.processing_task.join(timeout=1.0)
            self.processing_task = None

        self.buffer = None
        self.buffer_lock = None
        self.session_id = None


# Global state instances
session_state = SessionState()
audio_state = AudioState()
