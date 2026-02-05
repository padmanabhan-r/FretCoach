# Appendix: How FretCoach Analyzes Your Playing

This document explains how FretCoach listens to your guitar and scores your performance in plain English.

---

## Overview

FretCoach listens to your guitar through your microphone and calculates four scores:
1. **Pitch Accuracy** - Are you playing the right notes in tune?
2. **Scale Conformity** - Are you practicing all the notes in the scale evenly?
3. **Timing Stability** - Are you playing notes with consistent timing?
4. **Noise Control** - How clean is your playing?

We use Python libraries (NumPy, librosa, sounddevice) to process the audio locally on your computer.

**Audio Settings:**
- Sample rate: 44,100 Hz (CD quality)
- We process audio in chunks
- Real-time feedback in <300ms

---

## 1. Pitch Accuracy

**What it measures:** Are you playing the correct notes in tune?

### Step 1: Detect the pitch

We use librosa's `piptrack` function to find the pitch (frequency) of your guitar:

```python
pitches, magnitudes = librosa.piptrack(y=audio, sr=44100)
idx = magnitudes.argmax()
detected_hz = pitches.flatten()[idx]
```

This gives us a frequency like 440 Hz (the note A).

### Step 2: Convert to a note name

We convert the frequency to a MIDI number using librosa:
```python
midi = librosa.hz_to_midi(detected_hz)
```

Examples:
- 440 Hz = MIDI 69 = A4
- 330 Hz = MIDI 64 = E4
- 82 Hz = MIDI 40 = E2 (low E string)

### Step 3: Get the pitch class (just the note, ignoring octave)

We take the MIDI number modulo 12 to get the pitch class:
```python
pitch_class = int(round(midi)) % 12
```

Pitch classes: 0=C, 1=C♯, 2=D, 3=D♯, 4=E, 5=F, 6=F♯, 7=G, 8=G♯, 9=A, 10=A♯, 11=B

### Step 4: Check if it's in the scale

```python
if pitch_class not in target_scale:
    return 0.0  # Wrong note!
```

If you play a note outside the scale, you get a score of 0 immediately.

### Step 5: Check intonation (how in-tune you are)

If the note is correct, we check how close you are to perfect pitch:

```python
intonation_error = abs(midi - round(midi))
score = 1 - intonation_error
```

- Perfect pitch (exactly 440 Hz for A): error = 0, score = 1.0 (100%)
- Slightly sharp (445 Hz): error = 0.2, score = 0.8 (80%)
- Halfway between notes (very out of tune): error = 0.5, score = 0.5 (50%)

---

## 2. Scale Conformity

**What it measures:** Are you practicing all the notes in the scale evenly? This has two components:

### Component A: Pitch Stability (How steady you hold notes)

We measure how consistently you hold a note without wavering:

```python
pitches, mags = librosa.piptrack(y=audio, sr=sample_rate)
stable = pitches[mags > np.max(mags) * 0.7]
stability_score = np.exp(-np.std(stable))
```

- Steady note → low standard deviation → high score (near 1.0)
- Wobbly note → high standard deviation → lower score

### Component B: Scale Coverage (How evenly you practice the scale)

We track how many times you play each note:
```python
note_counts = {0: 50, 2: 48, 4: 45, 5: 52, 7: 49, 9: 51, 11: 50}  # Pretty even!
note_counts = {0: 100, 7: 5, 9: 2}  # Only playing C mostly - bad!
```

We calculate the "coefficient of variation" (CV), which measures how uneven the distribution is:

```python
percentages = [count/total for count in note_counts]
mean = average of percentages
std = standard deviation of percentages
cv = std / mean
evenness_score = exp(-2.0 * cv)
```

- CV = 0 (perfectly even) → score = 1.0
- CV = 0.35 (somewhat uneven) → score = 0.5
- CV = 1.0 (very uneven) → score = 0.14

We also penalize you for playing wrong notes:
```python
scale_note_ratio = correct_notes / total_notes
final_score = evenness_score * scale_note_ratio
```

**Final Scale Conformity** combines pitch stability (how steady) with scale coverage (how evenly you practice).

---

## 3. Timing Stability

**What it measures:** Are you playing notes with consistent timing?

### How we track note onsets

Every time you play a **different note** (or the same note after silence), we record the timestamp:
```python
onset_times = [100, 600, 1100, 1600, 2100]  # Every 500ms - consistent!
onset_times = [100, 800, 900, 1700, 3000]  # All over the place - inconsistent!
```

**Important:** We only count note changes, not every frame. So C→D is one onset, C→C (held) is not.

### How we score it

We look at the last 15 notes and calculate how consistent the intervals are:

```python
intervals = [600-100, 1100-600, 1600-1100, ...]  # Time between notes
median_interval = median of intervals

# Count intervals within 50% of median (very forgiving)
lower_bound = median_interval * 0.5  # 50% slower OK
upper_bound = median_interval * 1.5  # 50% faster OK

intervals_in_range = count of intervals in range
consistency_ratio = intervals_in_range / total_intervals
timing_score = consistency_ratio
```

**Examples:**
- 100% intervals in range → score = 1.0 (perfect consistency)
- 80% intervals in range → score = 0.8 (very good)
- 60% intervals in range → score = 0.6 (acceptable)
- 40% intervals in range → score = 0.4 (needs work)

**Note:** You need at least 3 notes (2 intervals) before timing can be calculated. With fewer notes, you get 0.0.

---

## 4. Noise Control

**What it measures:** How clean is your signal? Are you getting string buzz, fret noise, or muted strings?

### How we calculate it

We compare the total signal power to the noise:

```python
total_power = average of (audio ** 2)
noise_power = average of ((audio - mean(audio)) ** 2)
noise_score = 1 - (noise_power / (total_power + epsilon))
```

- High score → clean tone
- Low score → noisy/buzzy tone

---

## Combined Quality Score

### Weighting the metrics

Metrics can be toggled on/off by the user. Weights are distributed only among enabled metrics.

**When Pitch Accuracy is enabled (default):**
```python
pitch_weight = 0.40 + (strictness * 0.15)  # Range: 40% to 55%
remaining = 1.0 - pitch_weight
other_weight = remaining / (num_enabled - 1)  # Split among other enabled metrics

quality = (pitch_weight * pitch_score +
           other_weight * scale_score +     # if enabled
           other_weight * timing_score +    # if enabled
           other_weight * noise_score)      # always enabled
```

**At medium strictness (0.5) with all metrics enabled:**
- Pitch Accuracy: 47.5%
- Scale Conformity: 17.5%
- Timing Stability: 17.5%
- Noise Control: 17.5%

**If Pitch Accuracy is disabled:**
Weights split equally among remaining enabled metrics.

### Penalty for wrong notes

If you play a wrong note (pitch_score = 0):

- **High strictness (>0.7)**: Quality instantly drops to 0
- **Lower strictness**: Quality = quality * (1 - strictness), giving you partial credit

### Smoothing (EMA)

To prevent the score from jumping around wildly, we smooth it using Exponential Moving Average:

```python
alpha = 0.10 + (strictness * 0.30)  # Range: 0.10 to 0.40
smoothed_quality = alpha * new_quality + (1 - alpha) * old_quality
```

- Low strictness (0.2) → alpha = 0.16 → slow, smooth changes
- High strictness (0.8) → alpha = 0.34 → fast, responsive changes

We only update the score every 0.8 seconds (the "phrase window") to group notes together.

Individual metrics (pitch, timing) are smoothed with alpha = 0.25 for faster response.

---

## Smart Bulb Color

We map your quality score to a hue value:

```python
def score_to_hue(score):
    if score < 0.5:  # 0-50%: Red to Yellow (0-60)
        return score * 120
    elif score < 0.7:  # 50-70%: Yellow to Yellow-Green (60-85)
        return 60 + (score - 0.5) * 125
    elif score < 0.9:  # 70-90%: Yellow-Green to Light Green (85-110)
        return 85 + (score - 0.7) * 125
    else:  # 90-100%: Light Green to Green (110-120)
        return 110 + (score - 0.9) * 100
```

- 0-50% (poor) → Red to Yellow
- 50-70% (average) → Yellow to Yellow-Green
- 70-90% (good) → Yellow-Green to Light Green
- 90-100% (excellent) → Light Green to Green

Brightness also increases with quality:
```python
brightness = 300 + (quality * 700)  # Range: 300 to 1000
```

To prevent flickering, we only update the bulb if:
- The color changed by at least 5 hue units, AND
- At least 300ms have passed

---

## Sensitivity Setting

The sensitivity controls when audio is loud enough to be considered a "note":

```python
energy = average of (audio ** 2)
threshold = 1e-7 * (1 + sensitivity * 10)

if energy >= threshold:
    # Process this as a note
```

- Low sensitivity (0.0): threshold = 1e-7 → only loud notes trigger analysis
- High sensitivity (1.0): threshold = 1.1e-6 → quiet notes also trigger analysis

---

## Summary

That's it! We:
1. Detect your pitch using librosa
2. Check if it's the right note and in tune (Pitch Accuracy)
3. Measure how steady you hold notes and how evenly you practice the scale (Scale Conformity)
4. Track note onsets and measure timing consistency (Timing Stability)
5. Measure signal cleanliness (Noise Control)
6. Combine everything into a weighted quality score
7. Smooth the score over time with EMA
8. Map it to a color for your smart bulb

All calculations happen locally on your computer in real-time (<300ms).

---

**Navigation:**
- [← Troubleshooting Guide](troubleshooting.md)
- [Back to Index](index.md)
