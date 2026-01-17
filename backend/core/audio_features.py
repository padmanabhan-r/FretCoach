"""
Audio Feature Extraction for FretCoach
Contains AI-powered feature functions for analyzing guitar performance.
"""
import numpy as np
import librosa

# Import Opik for tracking (non-blocking)
try:
    from opik import track
    OPIK_ENABLED = True
except ImportError:
    # Fallback decorator if opik is not installed
    def track(name=None, **kwargs):
        def decorator(func):
            return func
        return decorator
    OPIK_ENABLED = False


@track(name="calculate_pitch_correctness")
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
    DEPRECATED: Use note_timing_stability instead.
    This function is kept for backwards compatibility but should not be called.
    """
    return 0.5


@track(name="calculate_timing_stability")
def calculate_note_timing_stability(onset_times_ms, window_size=8, consistency_threshold=0.15):
    """
    Calculate timing stability based on note onset times.
    Measures consistency of intervals in recent notes using coefficient of variation.

    Args:
        onset_times_ms: List of note onset times in milliseconds
        window_size: Number of notes to analyze (default 8, requires minimum 3)
        consistency_threshold: CV threshold for "in time" (default 0.15 = 15% variation)

    Returns:
        Tuple of (score, notes_analyzed)
        - score: Float between 0.0 and 1.0 (0.0 = very inconsistent, 1.0 = perfectly consistent)
        - notes_analyzed: Number of notes that could be analyzed
    """
    if len(onset_times_ms) < 2:
        # Can't calculate with less than 2 notes (need 1 interval)
        return 0.0, len(onset_times_ms)

    # Take the last window_size notes, but only if we have them
    window = min(window_size, len(onset_times_ms))
    recent_onsets = onset_times_ms[-window:]

    # Calculate intervals between consecutive notes
    intervals = list(np.diff(recent_onsets))

    if len(intervals) < 1:
        return 0.0, len(recent_onsets)

    # Calculate mean and std of intervals
    mean_interval = np.mean(intervals)
    std_interval = np.std(intervals)

    if mean_interval < 1.0:  # Less than 1ms, invalid
        return 0.0, len(recent_onsets)

    # Calculate coefficient of variation (normalized standard deviation)
    # CV = std / mean
    # CV of 0.0 = perfectly consistent intervals
    # CV of 0.15 = 15% variation (acceptable)
    # CV of 0.5+ = 50%+ variation (very inconsistent)
    cv = std_interval / mean_interval

    # Convert CV to score using exponential decay
    # CV=0 -> score=1.0 (perfect)
    # CV=0.15 -> score=0.86 (good)
    # CV=0.3 -> score=0.74 (acceptable)
    # CV=0.5+ -> score approaches 0 (bad)
    timing_score = np.exp(-2.0 * cv)

    return float(np.clip(timing_score, 0.0, 1.0)), window


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


@track(name="calculate_scale_coverage")
def calculate_scale_coverage(note_counts, target_pitch_classes):
    """
    Calculate how evenly distributed the played notes are across the scale.

    This measures the evenness of note distribution. Perfect distribution
    means each note is played equally. Playing only one note repeatedly = low score.

    Args:
        note_counts: Dict with pitch_class as key and play count as value
                     e.g., {0: 50, 2: 40, 5: 60} for uneven playing
        target_pitch_classes: Set of pitch classes in the target scale

    Returns:
        Float between 0.0 and 1.0 representing distribution evenness
        - 1.0 = perfectly even distribution across all scale notes
        - 0.2 (for pentatonic) = playing mostly one note
        - 0.0 = no notes played
    """
    if not target_pitch_classes or not note_counts:
        return 0.0

    num_scale_notes = len(target_pitch_classes)

    # Get counts for scale notes
    scale_note_counts = []
    for pitch_class in target_pitch_classes:
        scale_note_counts.append(note_counts.get(pitch_class, 0))

    # Count bad notes (notes not in the scale)
    bad_note_count = 0
    for pitch_class, count in note_counts.items():
        if pitch_class not in target_pitch_classes:
            bad_note_count += count

    total_scale_notes = sum(scale_note_counts)
    total_all_notes = total_scale_notes + bad_note_count

    if total_all_notes == 0:
        return 0.0

    # Calculate the distribution percentages (among scale notes only)
    percentages = np.array([count / total_scale_notes if total_scale_notes > 0 else 0 for count in scale_note_counts])

    # Calculate how far we are from perfect distribution using coefficient of variation
    # Perfect distribution has all notes at equal percentage
    # Uneven distribution has high variation

    mean_percentage = np.mean(percentages)
    std_percentage = np.std(percentages)

    if mean_percentage == 0:
        return 0.0

    # Coefficient of variation (normalized std dev)
    cv = std_percentage / mean_percentage

    # Convert CV to evenness score (0.0 = very uneven, 1.0 = perfectly even)
    # When CV=0, all notes equal -> score=1.0
    # When CV is high, notes are uneven -> score approaches 0.0
    evenness_score = np.exp(-2.0 * cv)

    # Apply penalty for bad notes
    # Ratio of scale notes to all notes played
    scale_note_ratio = total_scale_notes / total_all_notes

    # Final score is evenness weighted by how many notes are actually in scale
    # If 100% scale notes: full evenness score
    # If 50% scale notes: 50% of evenness score
    # If 0% scale notes: 0 score
    final_score = evenness_score * scale_note_ratio

    return float(np.clip(final_score, 0.0, 1.0))
