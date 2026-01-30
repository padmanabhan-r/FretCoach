"""
Session lifecycle management service for FretCoach.
"""

import sys
import os
import threading
from collections import deque

import sounddevice as sd

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'core'))

from session_logger import get_session_logger
from .audio_processor import audio_callback, process_audio, get_target_pitch_classes
from ..state import SessionState, AudioState


def start_session_impl(session_state: SessionState, audio_state: AudioState, audio_constants: dict) -> dict:
    """
    Initialize and start a practice session.

    Args:
        session_state: Session state dataclass
        audio_state: Audio processing state dataclass
        audio_constants: Audio processing constants

    Returns:
        dict with success status and session_id or error
    """
    if not session_state.config:
        return {"success": False, "error": "Configuration not set"}

    if session_state.is_running:
        return {"success": False, "error": "Session already running"}

    try:
        config = session_state.config

        # Load session config for metric toggles
        from ..services.config_service import load_session_config_from_file
        session_config = load_session_config_from_file()
        enabled_metrics = session_config.get("enabled_metrics", {
            "pitch_accuracy": True,
            "scale_conformity": True,
            "timing_stability": True
        })

        # Initialize session logger
        logger = get_session_logger()
        audio_state.session_logger = logger
        audio_state.strictness = config.get("strictness", 0.5)
        audio_state.sensitivity = config.get("sensitivity", 0.5)
        audio_state.ambient_lighting = config.get("ambient_lighting", True)
        audio_state.enabled_metrics = enabled_metrics

        # Start session logging
        session_id = logger.start_session(
            scale_name=config["scale_name"],
            strictness=audio_state.strictness,
            sensitivity=audio_state.sensitivity,
            ambient_lighting=audio_state.ambient_lighting,
            scale_type=config.get("scale_type", "natural"),
            enabled_metrics=enabled_metrics
        )
        audio_state.session_id = session_id

        # Initialize audio buffer
        buffer_size = int(
            audio_constants["SAMPLE_RATE"] *
            audio_constants["ANALYSIS_WINDOW_SEC"]
        )
        audio_state.buffer = deque(maxlen=buffer_size)
        audio_state.buffer_lock = threading.Lock()

        # Start audio stream with callback
        def stream_callback(indata, outdata, frames, time_info, status):
            audio_callback(indata, outdata, frames, time_info, status, config, audio_state)

        audio_state.stream = sd.Stream(
            device=(config["input_device"], config["output_device"]),
            channels=config["channels"],
            samplerate=audio_constants["SAMPLE_RATE"],
            blocksize=audio_constants["BLOCK_SIZE"],
            dtype="float32",
            callback=stream_callback,
        )
        audio_state.stream.start()

        # Start processing in background thread
        session_state.is_running = True
        audio_state.processing_task = threading.Thread(
            target=process_audio,
            args=(session_state, audio_state, audio_constants),
            daemon=True
        )
        audio_state.processing_task.start()

        print(f"\n[OK] Session started: {config['scale_name']} (Session ID: {session_id})")
        return {"success": True, "session_id": session_id}

    except Exception as e:
        session_state.is_running = False
        return {"success": False, "error": str(e)}


def stop_session_impl(session_state: SessionState, audio_state: AudioState) -> dict:
    """
    Stop the current practice session and cleanup resources.

    Args:
        session_state: Session state dataclass
        audio_state: Audio processing state dataclass

    Returns:
        dict with success status
    """
    session_state.is_running = False

    # End session logging
    if audio_state.session_logger and audio_state.session_id:
        try:
            # Get total number of notes in the scale from config
            config = session_state.config
            if config:
                scale_name = config["scale_name"]
                scale_type = config.get("scale_type", "natural")
                target_pitch_classes = get_target_pitch_classes(scale_name, scale_type)
                total_inscale_notes = len(target_pitch_classes)
            else:
                total_inscale_notes = 5

            audio_state.session_logger.end_session(
                session_id=audio_state.session_id,
                total_inscale_notes=total_inscale_notes
            )
        except Exception as e:
            print(f"Error ending session: {e}")

    # Cleanup audio resources
    audio_state.cleanup()

    # Reset session metrics
    session_state.reset_metrics()

    print("\n[STOP] Session stopped")
    return {"success": True}
