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
        - score: float between 0.0 and 1.0 (0.0 for wrong notes)
        - debug_dict: dict with detected_hz, detected_midi, pitch_class, in_scale
    """
    pitches, mags = librosa.piptrack(y=audio, sr=sample_rate)
    idx = mags.argmax()
    pitch = pitches.flatten()[idx]

    debug_dict = {
        "detected_hz": float(pitch),
        "detected_midi": 0,
        "pitch_class": 0,
        "in_scale": False,
    }

    if pitch <= 0:
        return 0.0, debug_dict

    midi = librosa.hz_to_midi(pitch)
    pitch_class = int(round(midi)) % 12
    in_scale = pitch_class in target_pitch_classes

    debug_dict["detected_midi"] = float(midi)
    debug_dict["pitch_class"] = int(pitch_class)
    debug_dict["in_scale"] = in_scale

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


def timing_cleanliness(audio, sample_rate):
    """
    Evaluate timing cleanliness based on onset consistency.
    
    Args:
        audio: Audio buffer (numpy array)
        sample_rate: Audio sample rate
    
    Returns:
        Score between 0.0 and 1.0
    """
    onsets = librosa.onset.onset_detect(y=audio, sr=sample_rate)
    if len(onsets) < 2:
        return 0.6
    intervals = np.diff(onsets)
    return np.exp(-np.var(intervals))


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
