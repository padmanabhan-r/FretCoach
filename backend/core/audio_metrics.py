"""
Shared quality calculation and metrics logic for FretCoach.
Used by both the API (audio_processor.py) and CLI (fret_coach.py).
"""

import time
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, Set, Optional, Tuple, Dict

from audio_features import (
    pitch_correctness,
    pitch_stability,
    calculate_note_timing_stability,
    noise_control,
    calculate_scale_coverage,
    detect_note_onset
)


@dataclass
class QualityConfig:
    """Configuration for quality calculation."""
    strictness: float = 0.5
    sensitivity: float = 0.5
    sample_rate: int = 44100
    phrase_window: float = 0.8


@dataclass
class QualityState:
    """Mutable state for quality tracking during a session."""
    ema_quality: float = 0.0
    ema_pitch: float = 0.0
    ema_timing: float = 0.0
    last_phrase_time: float = field(default_factory=time.time)
    note_counts: Dict[int, int] = field(default_factory=dict)
    note_onset_times_ms: list = field(default_factory=list)
    last_pitch_class: Optional[int] = None

    def reset(self):
        """Reset state for a new session."""
        self.ema_quality = 0.0
        self.ema_pitch = 0.0
        self.ema_timing = 0.0
        self.last_phrase_time = time.time()
        self.note_counts.clear()
        self.note_onset_times_ms.clear()
        self.last_pitch_class = None

    @property
    def total_notes(self) -> int:
        """Total notes played."""
        return sum(self.note_counts.values())

    def notes_in_scale(self, target_pitch_classes: Set[int]) -> int:
        """Count of notes played that are in the target scale."""
        return sum(
            count for pc, count in self.note_counts.items()
            if pc in target_pitch_classes
        )

    def notes_out_of_scale(self, target_pitch_classes: Set[int]) -> int:
        """Count of notes played that are outside the target scale."""
        return sum(
            count for pc, count in self.note_counts.items()
            if pc not in target_pitch_classes
        )


@dataclass
class QualityResult:
    """Result of processing one audio frame."""
    pitch_score: float
    stability_score: float
    timing_score: float
    noise_score: float
    quality_score: float
    scale_coverage: float
    note_detected: bool
    in_scale: bool
    pitch_class: Optional[int]
    detected_hz: float
    detected_midi: float
    notes_for_timing: int


def score_to_hue(score: float) -> int:
    """Convert quality score (0-1) to hue (0-120, red to green)."""
    return int(np.clip(score, 0.0, 1.0) * 120)


def calculate_energy_threshold(sensitivity: float) -> float:
    """Calculate energy threshold based on sensitivity setting."""
    return 1e-7 * (1 + sensitivity * 10)


def calculate_ema_alpha(strictness: float) -> float:
    """Calculate EMA alpha based on strictness setting."""
    return 0.10 + (strictness * 0.30)  # Range: 0.10 to 0.40


def calculate_weighted_quality(
    pitch_score: float,
    scale_score: float,
    timing_score: float,
    noise_score: float,
    strictness: float,
    enabled_metrics: Dict[str, bool]
) -> float:
    """
    Calculate quality with dynamic weight distribution based on enabled metrics.

    Args:
        pitch_score: Pitch correctness score (0-1)
        scale_score: Pitch stability score (0-1)
        timing_score: Timing stability score (0-1)
        noise_score: Noise control score (0-1)
        strictness: Strictness parameter (0-1)
        enabled_metrics: Dictionary of enabled metric flags

    Returns:
        Weighted quality score (0-1)
    """
    # Noise is always enabled (mandatory)
    enabled_count = 1

    # Count enabled metrics
    pitch_enabled = enabled_metrics.get("pitch_accuracy", True)
    scale_enabled = enabled_metrics.get("scale_conformity", True)
    timing_enabled = enabled_metrics.get("timing_stability", True)

    if pitch_enabled:
        enabled_count += 1
    if scale_enabled:
        enabled_count += 1
    if timing_enabled:
        enabled_count += 1

    # Calculate weights
    if pitch_enabled:
        pitch_weight = 0.40 + (strictness * 0.15)  # 40-55%
        remaining = 1.0 - pitch_weight
        other_weight = remaining / (enabled_count - 1)  # Exclude pitch

        quality = pitch_weight * pitch_score
        quality += other_weight * scale_score if scale_enabled else 0
        quality += other_weight * timing_score if timing_enabled else 0
        quality += other_weight * noise_score
    else:
        # Equal split among enabled
        equal_weight = 1.0 / enabled_count
        quality = 0
        quality += equal_weight * scale_score if scale_enabled else 0
        quality += equal_weight * timing_score if timing_enabled else 0
        quality += equal_weight * noise_score

    return quality


def process_audio_frame(
    audio: np.ndarray,
    target_pitch_classes: Set[int],
    config: QualityConfig,
    state: QualityState,
    enabled_metrics: Optional[Dict[str, bool]] = None
) -> Optional[QualityResult]:
    """
    Process a single audio frame and update quality metrics.

    Args:
        audio: Audio buffer as numpy array
        target_pitch_classes: Set of valid pitch classes for the scale
        config: Quality configuration
        state: Mutable quality state (will be updated)

    Returns:
        QualityResult if audio has sufficient energy, None otherwise
    """
    # Check if there's enough energy
    energy = np.mean(audio ** 2)
    if energy < calculate_energy_threshold(config.sensitivity):
        return None

    # Calculate pitch correctness
    p, debug_info = pitch_correctness(audio, config.sample_rate, target_pitch_classes)

    # Track notes played
    note_detected = debug_info.get("note_detected", False)
    in_scale = debug_info.get("in_scale", False)
    pitch_class = debug_info.get("pitch_class")

    # Track note onsets for timing analysis
    # ONLY track when pitch class CHANGES (different note played)
    # Also track silence to handle same-note-after-pause (C → silence → C)
    current_time_ms = time.time() * 1000.0

    last_pitch = state.last_pitch_class

    if note_detected and pitch_class is not None:
        state.note_counts[pitch_class] = state.note_counts.get(pitch_class, 0) + 1

        # Track as onset if:
        # 1. Different pitch than last time (C → D)
        # 2. First note after silence (silence → C)
        is_new_note = (pitch_class != last_pitch)

        if is_new_note:
            time_since_last = 0
            if len(state.note_onset_times_ms) > 0:
                time_since_last = current_time_ms - state.note_onset_times_ms[-1]

            state.note_onset_times_ms.append(current_time_ms)
            state.last_pitch_class = pitch_class

            # Debug: Log onset detection
            import random
            if random.random() < 0.15:  # 15% of the time
                print(f"[ONSET DEBUG] Onset #{len(state.note_onset_times_ms)}: {last_pitch}→{pitch_class}, gap={time_since_last:.0f}ms")
    else:
        # No note detected = silence
        # Reset last_pitch so next note (even if same pitch class) triggers onset
        if state.last_pitch_class is not None:
            state.last_pitch_class = None  # Mark silence

    # Calculate other metrics
    s = pitch_stability(audio, config.sample_rate)
    timing_score, notes_for_timing = calculate_note_timing_stability(
        state.note_onset_times_ms,
        window_size=15,  # Analyze last 15 notes for better timing consistency assessment
        consistency_threshold=0.15
    )
    n = noise_control(audio)
    scale_coverage = calculate_scale_coverage(state.note_counts, target_pitch_classes)

    # Calculate weighted quality score
    strictness = config.strictness
    if enabled_metrics is None:
        enabled_metrics = {
            "pitch_accuracy": True,
            "scale_conformity": True,
            "timing_stability": True
        }

    quality = calculate_weighted_quality(
        pitch_score=p,
        scale_score=s,
        timing_score=timing_score,
        noise_score=n,
        strictness=strictness,
        enabled_metrics=enabled_metrics
    )

    # Apply wrong note penalty based on strictness
    ema_alpha = calculate_ema_alpha(strictness)
    now = time.time()

    if p == 0.0:
        # Wrong note
        if strictness > 0.7:
            # High strictness: instant punishment
            state.ema_quality = 0.0
            state.last_phrase_time = now
        else:
            # Lower strictness: partial credit
            quality = quality * (1.0 - strictness)
            if now - state.last_phrase_time > config.phrase_window:
                state.ema_quality = ema_alpha * quality + (1 - ema_alpha) * state.ema_quality
                state.last_phrase_time = now
    else:
        # Correct note
        if now - state.last_phrase_time > config.phrase_window:
            state.ema_quality = ema_alpha * quality + (1 - ema_alpha) * state.ema_quality
            state.last_phrase_time = now

    # Update EMA for individual metrics
    # Higher alpha = faster response to changes
    metric_alpha = 0.25  # Increased from 0.15 for faster response
    state.ema_pitch = metric_alpha * p + (1 - metric_alpha) * state.ema_pitch
    state.ema_timing = metric_alpha * timing_score + (1 - metric_alpha) * state.ema_timing

    return QualityResult(
        pitch_score=p,
        stability_score=s,
        timing_score=timing_score,
        noise_score=n,
        quality_score=quality,
        scale_coverage=scale_coverage,
        note_detected=note_detected,
        in_scale=in_scale,
        pitch_class=pitch_class,
        detected_hz=debug_info.get("detected_hz", 0.0),
        detected_midi=debug_info.get("detected_midi", 0.0),
        notes_for_timing=notes_for_timing,
    )


@dataclass
class BulbState:
    """State for smart bulb throttling."""
    last_sent_hue: Optional[int] = None
    last_send_time: float = 0.0
    update_interval: float = 0.30
    hue_epsilon: int = 5

    def should_update(self, new_hue: int) -> bool:
        """Check if bulb should be updated based on throttling rules."""
        now = time.time()
        hue_changed = (
            self.last_sent_hue is None or
            abs(new_hue - self.last_sent_hue) >= self.hue_epsilon
        )
        time_elapsed = (now - self.last_send_time) >= self.update_interval
        return hue_changed and time_elapsed

    def mark_sent(self, hue: int):
        """Mark that a bulb update was sent."""
        self.last_sent_hue = hue
        self.last_send_time = time.time()


def calculate_bulb_brightness(ema_quality: float) -> int:
    """Calculate bulb brightness from quality score."""
    return int(300 + 700 * ema_quality)
