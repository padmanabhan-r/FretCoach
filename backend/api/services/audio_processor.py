"""
Audio processing logic for FretCoach API.
Handles real-time audio analysis using shared quality module.
"""

import sys
import os
import numpy as np
import time
from collections import deque

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'core'))

from audio_metrics import (
    QualityConfig,
    process_audio_frame,
    score_to_hue,
    calculate_bulb_brightness,
)
from smart_bulb import set_bulb_hsv, bulb_on, bulb_off
from scales import MAJOR_DIATONIC, MINOR_DIATONIC, MAJOR_PENTATONIC, MINOR_PENTATONIC

from ..state import SessionState, AudioState, DebugInfo

# Import Opik for tracking (non-blocking)
try:
    from opik import track
    OPIK_ENABLED = True
except ImportError:
    def track(name):
        def decorator(func):
            return func
        return decorator
    OPIK_ENABLED = False


def audio_callback(indata, outdata, frames, time_info, status, config, audio_state: AudioState):
    """
    Real-time audio callback - just fills the buffer.
    Keep this minimal for real-time safety.
    """
    # Input overflow is normal when buffer fills faster than processing
    # Only log actual errors (status is a CallbackFlags object from sounddevice)
    if status and not status.input_overflow:
        print(f"Audio status: {status}")

    if not config:
        return

    # Handle both mono and stereo input
    if config["channels"] == 1 or indata.ndim == 1:
        guitar = indata.flatten()
    else:
        guitar = indata[:, config["guitar_channel"]]

    with audio_state.buffer_lock:
        audio_state.buffer.extend(guitar)


def get_target_pitch_classes(scale_name: str, scale_type: str) -> set:
    """Get the pitch classes for a given scale."""
    is_major = "Major" in scale_name

    if scale_type == "natural":
        scales_dict = MAJOR_DIATONIC if is_major else MINOR_DIATONIC
    else:
        scales_dict = MAJOR_PENTATONIC if is_major else MINOR_PENTATONIC

    return set(scales_dict[scale_name])

def process_audio(session_state: SessionState, audio_state: AudioState, audio_constants: dict):
    """
    Background task to process audio and update metrics.
    Uses shared quality module for calculations.
    """
    config = session_state.config
    sample_rate = audio_constants["SAMPLE_RATE"]
    buffer_size = int(sample_rate * audio_constants["ANALYSIS_WINDOW_SEC"])

    # Get target scale
    scale_name = config["scale_name"]
    scale_type = config.get("scale_type", "natural")
    target_pitch_classes = get_target_pitch_classes(scale_name, scale_type)

    # Create quality config
    quality_config = QualityConfig(
        strictness=audio_state.strictness,
        sensitivity=audio_state.sensitivity,
        sample_rate=sample_rate,
        phrase_window=audio_constants["PHRASE_WINDOW"],
    )

    # Reset quality state for new session
    audio_state.reset()

    print(f"\n[AUDIO] Processing audio for {scale_name} ({scale_type})")
    print(f"Target notes: {sorted(target_pitch_classes)}")
    print(f"Strictness: {quality_config.strictness:.2f} | Sensitivity: {quality_config.sensitivity:.2f}")
    print(f"Ambient lighting: {'Enabled' if audio_state.ambient_lighting else 'Disabled'}")

    # Turn on bulb at start if enabled
    if audio_state.ambient_lighting:
        try:
            bulb_on()
            print("[BULB] Smart bulb enabled")
        except Exception as e:
            print(f"[WARN] Smart bulb not available: {e}")

    while session_state.is_running:
        time.sleep(0.15)

        # Get audio from buffer
        with audio_state.buffer_lock:
            if len(audio_state.buffer) < buffer_size:
                continue
            audio = np.array(audio_state.buffer)

        # Process the audio frame
        result = process_audio_frame(
            audio=audio,
            target_pitch_classes=target_pitch_classes,
            config=quality_config,
            state=audio_state.quality,
        )

        if result is None:
            session_state.current_note = "-"
            continue

        # Update debug info first to calculate cumulative accuracy
        num_unique_notes = len([c for c in audio_state.quality.note_counts.values() if c > 0])
        correct_notes = audio_state.quality.notes_in_scale(target_pitch_classes)
        wrong_notes = audio_state.quality.notes_out_of_scale(target_pitch_classes)

        # Calculate cumulative pitch accuracy (percentage of correct notes)
        total_notes = correct_notes + wrong_notes
        if total_notes > 0:
            pitch_accuracy_pct = correct_notes / total_notes
        else:
            pitch_accuracy_pct = 0.0

        # Update session state with results
        session_state.current_note = "In Scale" if result.in_scale else "Wrong Note"
        session_state.pitch_accuracy = pitch_accuracy_pct  # Cumulative: correct / total
        session_state.scale_conformity = result.scale_coverage  # Cumulative: coverage distribution
        session_state.timing_stability = audio_state.quality.ema_timing  # Cumulative: EMA of timing
        session_state.debug_info = DebugInfo(
            detected_hz=result.detected_hz,
            detected_midi=result.detected_midi,
            pitch_class=result.pitch_class,
            in_scale=result.in_scale,
            raw_pitch=result.pitch_score,
            raw_timing=result.timing_score,
            scale_coverage=result.scale_coverage,
            notes_played_count=audio_state.quality.total_notes,
            unique_notes_used=num_unique_notes,
            scale_total_notes=len(target_pitch_classes),
            notes_for_timing_analysis=result.notes_for_timing,
            correct_notes=correct_notes,
            wrong_notes=wrong_notes,
        )

        # Log metric to database
        if audio_state.session_logger and audio_state.session_id:
            try:
                audio_state.session_logger.log_metric(
                    session_id=audio_state.session_id,
                    pitch_accuracy=session_state.pitch_accuracy,
                    scale_conformity=result.scale_coverage,
                    timing_stability=session_state.timing_stability,
                    debug_info={
                        "note_detected": result.note_detected,
                        "in_scale": result.in_scale,
                        "pitch_class": result.pitch_class,
                    }
                )
            except Exception:
                pass  # Silently fail to avoid blocking audio processing

        # Update smart bulb if enabled
        if audio_state.ambient_lighting:
            hue = score_to_hue(audio_state.quality.ema_quality)
            if audio_state.bulb.should_update(hue):
                try:
                    brightness = calculate_bulb_brightness(audio_state.quality.ema_quality)
                    set_bulb_hsv(hue, v=brightness)
                    audio_state.bulb.mark_sent(hue)
                except Exception:
                    pass  # Silently fail
