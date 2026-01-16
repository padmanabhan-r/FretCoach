"""
Audio Feature Extraction for FretCoach
Contains AI-powered feature functions for analyzing guitar performance.
"""
import numpy as np
import librosa


def pitch_correctness(audio, sample_rate, target_pitch_classes, debug=False):
    """
    Evaluate pitch correctness against target scale.
    
    Args:
        audio: Audio buffer (numpy array)
        sample_rate: Audio sample rate
        target_pitch_classes: Set of valid pitch classes for the scale
        debug: If True, print debug information
    
    Returns:
        Tuple of (score, debug_dict) where:
        - score: float between 0.0 and 1.0 (0.0 for wrong notes, 0.0-1.0 for intonation quality)
        - debug_dict: dict with detected_hz, detected_midi, pitch_class, in_scale, note_detected
    """
    pitches, mags = librosa.piptrack(y=audio, sr=sample_rate)
    idx = mags.argmax()
    pitch = pitches.flatten()[idx]

    debug_dict = {
        "detected_hz": float(pitch),
        "detected_midi": 0,
        "pitch_class": None,  # None if no pitch detected
        "in_scale": False,
        "note_detected": False,
    }

    if pitch <= 0:
        return 0.0, debug_dict

    midi = librosa.hz_to_midi(pitch)
    pitch_class = int(round(midi)) % 12
    in_scale = pitch_class in target_pitch_classes

    debug_dict["detected_midi"] = float(midi)
    debug_dict["pitch_class"] = int(pitch_class)
    debug_dict["in_scale"] = in_scale
    debug_dict["note_detected"] = True

    if debug:
        print(f"DEBUG: Detected {pitch:.2f} Hz | MIDI {midi:.2f} | Pitch class {pitch_class} | In scale: {in_scale}")

    if not in_scale:
        return 0.0, debug_dict  # HARD FAIL - wrong note for the scale

    intonation_error = abs(midi - round(midi))
    score = np.clip(1 - intonation_error, 0, 1)
    return score, debug_dict


def pitch_stability(audio, sample_rate):
    """
    Evaluate pitch stability (how steady the note is held).
    
    Args:
        audio: Audio buffer (numpy array)
        sample_rate: Audio sample rate
    
    Returns:
        Score between 0.0 and 1.0
    """
    pitches, mags = librosa.piptrack(y=audio, sr=sample_rate)
    stable = pitches[mags > np.max(mags) * 0.7]
    if len(stable) < 5:
        return 0.5
    return np.exp(-np.std(stable))


def timing_cleanliness(audio, sample_rate, onset_history=None):
    """
    Evaluate timing consistency based on how evenly spaced notes are.
    Uses coefficient of variation for robust, scale-invariant consistency measurement.
    
    Args:
        audio: Audio buffer (numpy array)
        sample_rate: Audio sample rate
        onset_history: Optional list to track onset times across calls for better consistency
    
    Returns:
        Score between 0.0 and 1.0 (1.0 = perfectly even spacing, 0.0 = erratic)
    """
    # Detect note onsets with higher sensitivity for better detection
    onset_frames = librosa.onset.onset_detect(
        y=audio, 
        sr=sample_rate,
        backtrack=True,  # More accurate onset timing
        units='time'  # Get time in seconds directly
    )
    
    # Need at least 3 notes to measure consistency reliably
    if len(onset_frames) < 3:
        return 0.5  # Neutral score when not enough data
    
    # Calculate intervals between consecutive notes
    intervals = np.diff(onset_frames)
    
    # Filter out very short intervals (likely false detections)
    # Minimum 50ms between notes (faster than humanly possible for distinct notes)
    intervals = intervals[intervals > 0.05]
    
    if len(intervals) < 2:
        return 0.5
    
    # Use coefficient of variation (CV) for scale-invariant consistency
    # CV = std / mean - works for both fast and slow playing
    mean_interval = np.mean(intervals)
    std_interval = np.std(intervals)
    
    if mean_interval < 1e-6:  # Avoid division by zero
        return 0.5
    
    cv = std_interval / mean_interval
    
    # Convert CV to score (0.0 = erratic, 1.0 = perfectly consistent)
    # CV of 0.0 = perfect consistency = score 1.0
    # CV of 0.5+ = very inconsistent = score approaches 0.0
    # Use exponential decay for smooth scoring
    score = np.exp(-3.0 * cv)  # -3.0 scaling factor for good sensitivity
    
    return float(np.clip(score, 0.0, 1.0))


def noise_control(audio):
    """
    Evaluate noise control (signal-to-noise ratio).
    
    Args:
        audio: Audio buffer (numpy array)
    
    Returns:
        Score between 0.0 and 1.0
    """
    total = np.mean(audio ** 2)
    noise = np.mean((audio - np.mean(audio)) ** 2)
    return np.clip(1 - noise / (total + 1e-9), 0, 1)


def calculate_scale_coverage(notes_played, target_pitch_classes):
    """
    Calculate what percentage of the target scale notes have been played.
    
    Args:
        notes_played: Set of pitch classes that have been played
        target_pitch_classes: Set of pitch classes in the target scale
    
    Returns:
        Float between 0.0 and 1.0 representing coverage percentage
    """
    if not target_pitch_classes:
        return 0.0
    
    # Only count notes that are actually in the target scale
    valid_notes_played = notes_played.intersection(target_pitch_classes)
    coverage = len(valid_notes_played) / len(target_pitch_classes)
    return coverage
