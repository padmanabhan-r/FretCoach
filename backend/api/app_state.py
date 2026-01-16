"""
Application state management for FretCoach API
Manages global session state, audio state, and constants
"""

from collections import deque
import threading

# Application constants
AUDIO_CONSTANTS = {
    "SAMPLE_RATE": 44100,
    "BLOCK_SIZE": 128,
    "ANALYSIS_WINDOW_SEC": 0.30,
    "TUYA_UPDATE_INTERVAL": 0.30,
    "HUE_EPSILON": 5,
    "PHRASE_WINDOW": 0.8,
}


def get_session_state():
    """Get the global session state dictionary"""
    return {
        "is_running": False,
        "config": None,
        "current_note": "-",
        "pitch_accuracy": 0,
        "scale_conformity": 0,
        "timing_stability": 0,
        "debug_info": {
            "detected_hz": 0,
            "detected_midi": 0,
            "pitch_class": 0,
            "in_scale": False,
            "raw_pitch": 0,
            "raw_timing": 0,
        },
    }


def get_audio_state():
    """Get the global audio processing state dictionary"""
    return {
        "stream": None,
        "buffer": None,
        "buffer_lock": None,
        "processing_task": None,
        "last_sent_hue": None,
        "last_send_time": 0.0,
        "ema_quality": 0.0,
        "ema_pitch": 0.0,
        "ema_timing": 0.0,
        "last_phrase_time": 0.0,
        "strictness": 0.5,
        "sensitivity": 0.5,
        "ambient_lighting": True,
        "note_counts": {},  # Track count of each pitch class played
        "session_id": None,  # Current session ID for logging
        "session_logger": None,  # Session logger instance
        "notes_detected_count": 0,  # Total notes detected
        "notes_in_scale_count": 0,  # Notes in scale
        "notes_out_of_scale_count": 0,  # Notes out of scale
        "note_onset_times_ms": [],  # Track onset times in milliseconds
        "total_inscale_notes": 5,  # Total number of notes in the target scale
    }


# Initialize global state (will be instantiated once when module is imported)
session_state = get_session_state()
audio_state = get_audio_state()
