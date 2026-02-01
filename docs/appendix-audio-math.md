# Appendix: How FretCoach Analyzes Your Playing

This document explains how FretCoach listens to your guitar and scores your performance in plain English.

---

## Overview

FretCoach listens to your guitar through your microphone and calculates four scores:
1. **Pitch Accuracy** - Are you playing the right notes in tune?
2. **Scale Coverage** - Are you practicing all the notes in the scale evenly?
3. **Timing Stability** - Are you playing notes with consistent timing?
4. **Noise Control** - How clean is your playing?

We use Python libraries (NumPy, librosa, sounddevice) to process the audio locally on your computer.

**Audio Settings:**
- Sample rate: 44,100 Hz (CD quality)
- We process audio in 800ms chunks
- We analyze new audio every 150ms
- This gives feedback in about 100-120ms

---

## 1. Pitch Accuracy

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

## 2. Scale Coverage

### What we're measuring

If you play C Major (C, D, E, F, G, A, B), are you playing all seven notes evenly? Or are you just playing C and G over and over?

### How we track it

We count how many times you play each note:
```python
note_counts = {0: 50, 2: 48, 4: 45, 5: 52, 7: 49, 9: 51, 11: 50}  # Pretty even!
note_counts = {0: 100, 7: 5, 9: 2}  # Only playing C mostly - bad!
```

### How we score it

We calculate the "coefficient of variation" (CV), which measures how uneven the distribution is:

```python
percentages = [count/total for count in note_counts]
mean = average of percentages
std = standard deviation of percentages
cv = std / mean
evenness_score = exp(-2 * cv)
```

- CV = 0 (perfectly even) → score = 1.0
- CV = 0.35 (somewhat uneven) → score = 0.5
- CV = 1.0 (very uneven) → score = 0.14

We also penalize you for playing wrong notes:
```python
scale_note_ratio = correct_notes / total_notes
final_score = evenness_score * scale_note_ratio
```

---

## 3. Timing Stability

### What we're measuring

Are you playing notes with consistent timing? Like a metronome, or all over the place?

### How we track it

Every time we detect a new note, we record the timestamp:
```python
onset_times = [100, 600, 1100, 1600, 2100]  # Every 500ms - consistent!
onset_times = [100, 800, 900, 1700, 3000]  # All over the place - inconsistent!
```

### How we score it

We look at the last 8 notes and calculate how consistent the intervals are:

```python
intervals = [600-100, 1100-600, 1600-1100, ...]  # Time between notes
mean_interval = average of intervals
std_interval = standard deviation of intervals
cv = std_interval / mean_interval
timing_score = exp(-2 * cv)
```

- CV = 0 (perfect metronome) → score = 1.0
- CV = 0.15 (15% variation, pretty good) → score = 0.74
- CV = 0.5 (50% variation, inconsistent) → score = 0.37

---

## 4. Noise Control

### What we're measuring

How clean is your signal? Are you getting string buzz, fret noise, or muted strings?

### How we calculate it

We compare the total signal power to the noise:

```python
total_power = average of (audio ** 2)
noise_power = average of (audio - mean) ** 2
noise_score = 1 - (noise_power / total_power)
```

- High score → clean tone
- Low score → noisy/buzzy tone

---

## Combined Quality Score

### Weighting the metrics

We combine all four scores with weights that depend on your strictness setting:

```python
pitch_weight = 0.40 + (strictness * 0.15)  # Range: 0.40 to 0.55
other_weight = (1 - pitch_weight) / 3       # Split remaining among the other 3

quality = (pitch_weight * pitch_score +
           other_weight * stability_score +
           other_weight * timing_score +
           other_weight * noise_score)
```

At medium strictness (0.5):
- Pitch: 47.5%
- Stability: 17.5%
- Timing: 17.5%
- Noise: 17.5%

### Penalty for wrong notes

If you play a wrong note (pitch_score = 0):

- **High strictness (>0.7)**: Quality instantly drops to 0
- **Lower strictness**: Quality = quality * (1 - strictness), giving you partial credit

### Smoothing (EMA)

To prevent the score from jumping around wildly, we smooth it:

```python
alpha = 0.10 + (strictness * 0.30)  # Range: 0.10 to 0.40
smoothed_quality = alpha * new_quality + (1 - alpha) * old_quality
```

- Low strictness → slow, smooth changes
- High strictness → fast, responsive changes

We only update the score every 0.8 seconds (the "phrase window") to group notes together.

---

## Smart Bulb Color

We map your quality score to a color:

```python
hue = quality * 120  # 0 to 120
```

- 0 (red) = Poor
- 60 (yellow) = Average
- 120 (green) = Excellent

Brightness also increases with quality:
```python
brightness = 300 + (quality * 700)  # 300 to 1000
```

To prevent flickering, we only update the bulb if:
- The color changed by at least 5 hue units, OR
- At least 300ms have passed

---

## Sensitivity Setting

The sensitivity controls when audio is loud enough to be considered a "note":

```python
energy = average of (audio ** 2)
threshold = 0.0000001 * (1 + sensitivity * 10)

if energy >= threshold:
    # Process this as a note
```

- Low sensitivity: Only loud notes trigger analysis
- High sensitivity: Quiet notes also trigger analysis

---

## Summary

That's it! We:
1. Detect your pitch using librosa
2. Check if it's the right note and in tune
3. Track which notes you play and how evenly
4. Measure timing consistency
5. Measure signal cleanliness
6. Combine everything into a quality score
7. Smooth the score over time
8. Map it to a color for your smart bulb

All calculations happen locally on your computer, running every 150ms for real-time feedback.

---

**Navigation:**
- [← Troubleshooting Guide](troubleshooting.md)
- [Back to Index](index.md)
