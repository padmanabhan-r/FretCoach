"""
Audio processing logic for FretCoach
Handles real-time audio analysis and metric calculation
This is the core application logic (not endpoint-specific)
"""

import sys
import os
import numpy as np
import sounddevice as sd
import time
from collections import deque
from typing import Optional, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))

from audio_features import (
    pitch_correctness, 
    pitch_stability, 
    calculate_note_timing_stability, 
    noise_control, 
    calculate_scale_coverage
)
from smart_bulb import set_bulb_hsv, bulb_on, bulb_off
from scales import MAJOR_DIATONIC, MINOR_DIATONIC, MAJOR_PENTATONIC, MINOR_PENTATONIC

# Import Opik for tracking (non-blocking)
try:
    from opik import track
    OPIK_ENABLED = True
except ImportError:
    # Fallback decorator if opik is not installed
    def track(name):
        def decorator(func):
            return func
        return decorator
    OPIK_ENABLED = False


def score_to_hue(score):
    """Convert quality score (0-1) to hue (0-120, red to green)"""
    return int(np.clip(score, 0.0, 1.0) * 120)


def audio_callback(indata, outdata, frames, time_info, status, config, audio_state):
    """
    Real-time audio callback
    
    Args:
        indata: Audio input buffer
        outdata: Audio output buffer
        frames: Number of frames
        time_info: Time information
        status: Stream status
        config: Session configuration
        audio_state: Audio processing state
    """
    if status:
        print(f"Audio status: {status}")
    
    if not config:
        return
    
    # Handle both mono and stereo input
    if config["channels"] == 1 or indata.ndim == 1:
        guitar = indata.flatten()
    else:
        guitar = indata[:, config["guitar_channel"]]
    
    with audio_state["buffer_lock"]:
        audio_state["buffer"].extend(guitar)


@track(name="process_audio_session")
def process_audio(session_state, audio_state, audio_constants):
    """
    Background task to process audio and update metrics
    Core audio processing logic
    
    Args:
        session_state: Session state dictionary
        audio_state: Audio processing state dictionary
        audio_constants: Audio processing constants
    """
    config = session_state["config"]
    sample_rate = audio_constants["SAMPLE_RATE"]
    buffer_size = int(sample_rate * audio_constants["ANALYSIS_WINDOW_SEC"])
    
    # Get configuration parameters
    strictness = audio_state["strictness"]
    sensitivity = audio_state["sensitivity"]
    ambient_lighting = audio_state["ambient_lighting"]
    
    # Calculate EMA alpha based on strictness
    ema_alpha = 0.10 + (strictness * 0.30)  # Range: 0.10 to 0.40
    
    # Get target pitch classes from scale
    scale_name = config["scale_name"]
    scale_type = config.get("scale_type", "diatonic")
    is_major = "Major" in scale_name
    
    if scale_type == "diatonic":
        scales_dict = MAJOR_DIATONIC if is_major else MINOR_DIATONIC
    else:
        scales_dict = MAJOR_PENTATONIC if is_major else MINOR_PENTATONIC
    
    target_pitch_classes = set(scales_dict[scale_name])
    
    # Store the total number of notes in the scale for logging
    audio_state["total_inscale_notes"] = len(target_pitch_classes)
    
    print(f"\n🎸 Processing audio for {scale_name} ({scale_type})")
    print(f"Target notes: {sorted(target_pitch_classes)}")
    print(f"Strictness: {strictness:.2f} | Sensitivity: {sensitivity:.2f}")
    print(f"Ambient lighting: {'Enabled' if ambient_lighting else 'Disabled'}")
    
    audio_state["ema_quality"] = 0.0
    audio_state["ema_pitch"] = 0.0
    audio_state["ema_timing"] = 0.0
    audio_state["notes_played_in_scale"] = set()  # Reset scale coverage tracking
    audio_state["last_phrase_time"] = time.time()
    audio_state["last_sent_hue"] = None
    audio_state["last_send_time"] = 0.0
    
    # Turn on bulb at start if enabled
    if ambient_lighting:
        try:
            bulb_on()
            print("💡 Smart bulb enabled")
        except Exception as e:
            print(f"⚠️  Smart bulb not available: {e}")
    
    while session_state["is_running"]:
        time.sleep(0.15)
        
        with audio_state["buffer_lock"]:
            if len(audio_state["buffer"]) < buffer_size:
                continue
            audio = np.array(audio_state["buffer"])
        
        # Check if there's enough energy (adjusted by sensitivity)
        energy = np.mean(audio ** 2)
        energy_threshold = 1e-7 * (1 + sensitivity * 10)
        if energy < energy_threshold:
            session_state["current_note"] = "-"
            continue
        
        # Calculate pitch correctness
        p, debug_info = pitch_correctness(audio, sample_rate, target_pitch_classes)
        
        # Track notes played for scale coverage and count statistics
        if debug_info.get("note_detected"):
            audio_state["notes_detected_count"] += 1
            # Track onset time in milliseconds for timing stability calculation
            current_time_ms = time.time() * 1000.0
            audio_state["note_onset_times_ms"].append(current_time_ms)
            
            if debug_info.get("in_scale"):
                audio_state["notes_in_scale_count"] += 1
                if debug_info.get("pitch_class") is not None:
                    pitch_class = debug_info["pitch_class"]
                    audio_state["note_counts"][pitch_class] = audio_state["note_counts"].get(pitch_class, 0) + 1
            else:
                audio_state["notes_out_of_scale_count"] += 1
                # Also track bad notes in note_counts so they affect distribution
                if debug_info.get("pitch_class") is not None:
                    pitch_class = debug_info["pitch_class"]
                    audio_state["note_counts"][pitch_class] = audio_state["note_counts"].get(pitch_class, 0) + 1
        
        # Calculate all metrics
        s = pitch_stability(audio, sample_rate)
        
        # Calculate timing stability based on note onset times
        timing_score, notes_for_timing = calculate_note_timing_stability(
            audio_state["note_onset_times_ms"],
            window_size=8,
            consistency_threshold=0.15
        )
        
        n = noise_control(audio)
        
        # Calculate scale coverage (how evenly distributed the notes are)
        scale_coverage = calculate_scale_coverage(
            audio_state["note_counts"],
            target_pitch_classes
        )
        
        # Store debug info
        num_unique_notes = len([n for n in audio_state["note_counts"].values() if n > 0])
        session_state["debug_info"] = {
            **debug_info,
            "raw_pitch": float(p),
            "raw_timing": float(timing_score),
            "scale_coverage": float(scale_coverage),
            "notes_played_count": audio_state["notes_detected_count"],
            "unique_notes_used": num_unique_notes,
            "scale_total_notes": len(target_pitch_classes),
            "notes_for_timing_analysis": notes_for_timing,
        }
        
        # Log metric to database
        if audio_state["session_logger"] and audio_state["session_id"]:
            try:
                audio_state["session_logger"].log_metric(
                    session_id=audio_state["session_id"],
                    pitch_accuracy=session_state["pitch_accuracy"],
                    scale_conformity=scale_coverage,
                    timing_stability=session_state["timing_stability"],
                    debug_info=debug_info
                )
            except Exception as e:
                pass  # Silently fail to avoid blocking audio processing
        
        # Adjust weights based on strictness
        pitch_weight = 0.40 + (strictness * 0.15)
        other_weight = (1.0 - pitch_weight) / 3
        
        quality = (
            pitch_weight * p +
            other_weight * s +
            other_weight * timing_score +
            other_weight * n
        )
        
        # Apply wrong note penalty based on strictness
        if p == 0.0:
            session_state["current_note"] = "Wrong Note"
            
            # At high strictness (>0.7), instant punishment
            if strictness > 0.7:
                audio_state["ema_quality"] = 0.0
                audio_state["last_phrase_time"] = time.time()
            else:
                # At low strictness, wrong notes still get partial credit
                penalty_factor = (1.0 - strictness)
                quality = quality * penalty_factor
                
                # Update EMA quality
                now = time.time()
                if now - audio_state["last_phrase_time"] > audio_constants["PHRASE_WINDOW"]:
                    audio_state["ema_quality"] = (
                        ema_alpha * quality + 
                        (1 - ema_alpha) * audio_state["ema_quality"]
                    )
                    audio_state["last_phrase_time"] = now
        else:
            session_state["current_note"] = "In Scale"
            
            # Update EMA quality when playing correct notes
            now = time.time()
            if now - audio_state["last_phrase_time"] > audio_constants["PHRASE_WINDOW"]:
                audio_state["ema_quality"] = (
                    ema_alpha * quality + 
                    (1 - ema_alpha) * audio_state["ema_quality"]
                )
                audio_state["last_phrase_time"] = now
        
        # Update smart bulb color if enabled
        if ambient_lighting:
            now = time.time()
            hue = score_to_hue(audio_state["ema_quality"])
            brightness = int(300 + 700 * audio_state["ema_quality"])
            
            if (
                (audio_state["last_sent_hue"] is None or 
                 abs(hue - audio_state["last_sent_hue"]) >= audio_constants["HUE_EPSILON"])
                and (now - audio_state["last_send_time"]) >= audio_constants["TUYA_UPDATE_INTERVAL"]
            ):
                try:
                    set_bulb_hsv(hue, v=brightness)
                    audio_state["last_sent_hue"] = hue
                    audio_state["last_send_time"] = now
                except Exception as e:
                    # Silently fail - don't spam console
                    pass
        
        # Update session state metrics with EMA smoothing
        metric_ema_alpha = 0.15
        audio_state["ema_pitch"] = metric_ema_alpha * p + (1 - metric_ema_alpha) * audio_state["ema_pitch"]
        audio_state["ema_timing"] = metric_ema_alpha * timing_score + (1 - metric_ema_alpha) * audio_state["ema_timing"]
        
        session_state["pitch_accuracy"] = audio_state["ema_pitch"]
        session_state["scale_conformity"] = scale_coverage
        session_state["timing_stability"] = audio_state["ema_timing"]
