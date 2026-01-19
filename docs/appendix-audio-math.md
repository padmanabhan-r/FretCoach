# Appendix: Audio Processing Mathematics

This appendix provides the mathematical foundations for FretCoach's real-time audio analysis engine.

---

## Overview

FretCoach's audio analysis operates on digitized audio signals, applying Digital Signal Processing (DSP) techniques to extract musical features. All processing runs **deterministically and locally** with no LLM involvement for real-time performance.

**Core Technologies:**
- **NumPy** — Array processing and mathematical operations
- **librosa** — Music and audio analysis library
- **sounddevice** — Cross-platform audio I/O

---

## Signal Acquisition

### Audio Sampling

**Sample Rate:** 44100 Hz (CD quality)

**Bit Depth:** 32-bit float (sounddevice default)

**Channels:** Mono or stereo (guitar typically on one channel)

The continuous analog guitar signal is sampled at discrete time intervals:

$$
x[n] = x_a(nT_s), \quad n = 0, 1, 2, \ldots
$$

Where:
- $x[n]$ = discrete sample value
- $x_a(t)$ = continuous analog signal
- $T_s = \frac{1}{f_s} = \frac{1}{44100} \approx 22.68 \, \mu s$ = sampling period
- $f_s = 44100 \, Hz$ = sampling frequency

**Nyquist Theorem:** With $f_s = 44100$ Hz, we can accurately represent frequencies up to $\frac{f_s}{2} = 22050$ Hz, well above the highest guitar frequency (~1200 Hz for 24th fret on high E string).

### Frame-Based Processing

Audio is processed in overlapping frames (windows):

**Frame Size:** 800 ms = 35,280 samples at 44100 Hz

**Hop Size:** 150 ms = 6,615 samples (approximately 81% overlap)

This overlap ensures smooth transitions and catches transient events.

---

## Metric 1: Pitch Accuracy

### Pitch Detection (YIN Algorithm via librosa)

**Goal:** Determine the fundamental frequency $f_0$ of the guitar note.

**Method:** librosa's `piptrack` function uses the YIN algorithm, which finds the fundamental frequency by detecting periodicities in the autocorrelation function.

**Implementation:**
```python
pitches, magnitudes = librosa.piptrack(y=audio, sr=sample_rate)
```

**Output:**
- `pitches`: 2D array of frequency values (Hz) for each time frame and frequency bin
- `magnitudes`: 2D array of magnitude values indicating confidence

**Fundamental frequency extraction:**
```python
idx = magnitudes.argmax()  # Find index of maximum magnitude
f0 = pitches.flatten()[idx]  # Extract corresponding frequency
```

If $f_0 \leq 0$, no pitch is detected (silence or noise).

### MIDI Conversion

Convert frequency to MIDI note number:

$$
m = 69 + 12 \cdot \log_2\left(\frac{f_0}{440}\right)
$$

Where:
- $m$ = MIDI note number (69 = A4 = 440 Hz)
- $f_0$ = detected frequency in Hz

**Example:**
- $f_0 = 440$ Hz → $m = 69$ (A4)
- $f_0 = 329.63$ Hz → $m \approx 64$ (E4)
- $f_0 = 82.41$ Hz → $m \approx 40$ (E2, low E string)

### Pitch Class Extraction

Reduce MIDI note to pitch class (0-11):

$$
p_c = \text{round}(m) \bmod 12
$$

Where:
- $p_c \in \{0, 1, 2, \ldots, 11\}$
- 0 = C, 1 = C♯/D♭, 2 = D, ..., 11 = B

**Example:** E4 (MIDI 64) → $64 \bmod 12 = 4$ (pitch class E)

### Scale Conformity Check

Given target scale $S = \{p_1, p_2, \ldots, p_k\}$ (set of pitch classes):

$$
\text{in\_scale} = 
\begin{cases}
1 & \text{if } p_c \in S \\
0 & \text{otherwise}
\end{cases}
$$

If the note is **not in scale**, the pitch score is immediately 0 (hard fail).

### Intonation Quality (for notes in scale)

Measure how close the detected pitch is to the ideal semitone:

$$
\text{error} = |m - \text{round}(m)|
$$

Where:
- $\text{error} \in [0, 0.5]$
- 0 = perfect intonation
- 0.5 = exactly between semitones (maximum out-of-tune)

**Pitch accuracy score:**

$$
s_{\text{pitch}} = \max(0, 1 - \text{error})
$$

**Example:**
- Detected: 440.2 Hz (MIDI 69.008) → error = 0.008 → score = 0.992 (99.2%)
- Detected: 453 Hz (MIDI 69.5) → error = 0.5 → score = 0.5 (50%)

---

## Metric 2: Scale Coverage

### Purpose

Measures how evenly the player distributes practice across all notes in the target scale.

**Problem:** A player might repeatedly play the same 2-3 notes instead of practicing the full scale.

**Solution:** Reward even distribution using statistical dispersion.

### Note Counting

Throughout the session, maintain a dictionary:

$$
N = \{p_c : \text{count}\}
$$

Where $\text{count}$ = number of times pitch class $p_c$ was played.

**Example:**
```
N = {0: 50, 2: 48, 4: 45, 5: 52, 7: 49, 9: 51, 11: 50}  # C Major
```

### Distribution Analysis

For a target scale with $k$ notes, extract counts for scale notes:

$$
C_S = [\text{count}(p_1), \text{count}(p_2), \ldots, \text{count}(p_k)]
$$

**Total scale notes:**

$$
n_S = \sum_{i=1}^{k} \text{count}(p_i)
$$

**Total out-of-scale notes:**

$$
n_{\text{bad}} = \sum_{p_c \notin S} \text{count}(p_c)
$$

**Scale note ratio:**

$$
r_S = \frac{n_S}{n_S + n_{\text{bad}}}
$$

This penalizes playing notes outside the target scale.

### Evenness Score (Coefficient of Variation)

Calculate the percentage each scale note represents:

$$
P = \left[\frac{\text{count}(p_i)}{n_S}\right]_{i=1}^{k}
$$

**Mean percentage:**

$$
\mu_P = \frac{1}{k} \sum_{i=1}^{k} P_i = \frac{1}{k}
$$

(For perfect distribution, each note would be $\frac{1}{k}$)

**Standard deviation:**

$$
\sigma_P = \sqrt{\frac{1}{k} \sum_{i=1}^{k} (P_i - \mu_P)^2}
$$

**Coefficient of variation:**

$$
CV = \frac{\sigma_P}{\mu_P}
$$

Where:
- $CV = 0$ → perfectly even distribution
- $CV > 0$ → uneven distribution

**Evenness score:**

$$
s_{\text{even}} = e^{-2 \cdot CV}
$$

This exponential decay converts CV to a 0-1 score:
- $CV = 0$ → $s_{\text{even}} = 1.0$ (perfect)
- $CV = 0.35$ → $s_{\text{even}} \approx 0.5$ (moderate unevenness)
- $CV = 1.0$ → $s_{\text{even}} \approx 0.135$ (very uneven)

### Final Scale Coverage Score

$$
s_{\text{coverage}} = s_{\text{even}} \cdot r_S
$$

This combines evenness with the penalty for out-of-scale notes.

---

## Metric 3: Timing Stability

### Onset Detection

**Goal:** Detect when new notes begin (attacks).

**Method:** Simple energy threshold approach.

When a new note is detected (pitch class changes and energy exceeds threshold), record:

$$
t_{\text{onset}} = \text{current\_time\_ms}
$$

Maintain a list of onset times:

$$
T = [t_1, t_2, t_3, \ldots, t_n]
$$

### Interval Calculation

Calculate time intervals between consecutive notes:

$$
\Delta T = [t_2 - t_1, t_3 - t_2, \ldots, t_n - t_{n-1}]
$$

### Timing Consistency Analysis

**Goal:** Measure how consistent the intervals are.

**Method:** Use recent intervals (window of last 8 notes by default).

**Mean interval:**

$$
\mu_{\Delta T} = \frac{1}{w} \sum_{i=1}^{w} \Delta T_i
$$

Where $w$ = window size (typically 8).

**Standard deviation:**

$$
\sigma_{\Delta T} = \sqrt{\frac{1}{w} \sum_{i=1}^{w} (\Delta T_i - \mu_{\Delta T})^2}
$$

**Coefficient of variation:**

$$
CV_{\text{timing}} = \frac{\sigma_{\Delta T}}{\mu_{\Delta T}}
$$

Interpretation:
- $CV_{\text{timing}} = 0$ → perfectly consistent intervals (metronomic)
- $CV_{\text{timing}} = 0.15$ → 15% variation (acceptable)
- $CV_{\text{timing}} = 0.5$ → 50% variation (inconsistent)

### Timing Stability Score

$$
s_{\text{timing}} = e^{-2 \cdot CV_{\text{timing}}}
$$

**Example:**
- $CV = 0$ → score = 1.0 (perfect consistency)
- $CV = 0.15$ → score ≈ 0.74 (good)
- $CV = 0.3$ → score ≈ 0.55 (average)
- $CV = 0.5$ → score ≈ 0.37 (needs work)

**Edge cases:**
- Less than 2 notes → score = 0 (cannot calculate)
- Mean interval < 1 ms → score = 0 (invalid)

---

## Metric 4: Noise Control

### Signal-to-Noise Estimation

**Goal:** Measure clarity of playing (minimize unwanted artifacts).

**Method:** Compare signal power to noise power.

**Total signal power:**

$$
P_{\text{total}} = \frac{1}{N} \sum_{n=1}^{N} x[n]^2
$$

**Noise estimate** (variance around mean):

$$
P_{\text{noise}} = \frac{1}{N} \sum_{n=1}^{N} (x[n] - \bar{x})^2
$$

Where $\bar{x} = \frac{1}{N} \sum_{n=1}^{N} x[n]$ is the mean.

**Noise control score:**

$$
s_{\text{noise}} = \max\left(0, 1 - \frac{P_{\text{noise}}}{P_{\text{total}} + \epsilon}\right)
$$

Where $\epsilon = 10^{-9}$ prevents division by zero.

**Interpretation:**
- High score → clean signal (low noise relative to signal)
- Low score → noisy signal (string buzz, fret noise, etc.)

---

## Overall Quality Score

### Weighted Combination

The four metrics are combined with strictness-dependent weighting:

**Pitch weight:**

$$
w_{\text{pitch}} = 0.40 + 0.15 \cdot s_{\text{strictness}}
$$

Where $s_{\text{strictness}} \in [0, 1]$ is the user-configured strictness.

**Other weights:**

$$
w_{\text{other}} = \frac{1 - w_{\text{pitch}}}{3}
$$

(Equally distributed among timing, stability, and noise)

**Raw quality:**

$$
q_{\text{raw}} = w_{\text{pitch}} \cdot s_{\text{pitch}} + w_{\text{other}} \cdot (s_{\text{stability}} + s_{\text{timing}} + s_{\text{noise}})
$$

Where:
- $s_{\text{pitch}}$ = pitch accuracy score
- $s_{\text{stability}}$ = pitch stability score (not emphasized in current version)
- $s_{\text{timing}}$ = timing stability score
- $s_{\text{noise}}$ = noise control score

**Example** (strictness = 0.5):
- $w_{\text{pitch}} = 0.40 + 0.15 \times 0.5 = 0.475$
- $w_{\text{other}} = \frac{0.525}{3} = 0.175$

If all scores are 0.8:
$$
q_{\text{raw}} = 0.475 \times 0.8 + 3 \times 0.175 \times 0.8 = 0.38 + 0.42 = 0.80
$$

### Wrong Note Penalty

If pitch score is 0 (wrong note or out of scale):

**High strictness** ($s_{\text{strictness}} > 0.7$):
$$
q = 0 \quad \text{(instant punishment)}
$$

**Lower strictness:**
$$
q = q_{\text{raw}} \times (1 - s_{\text{strictness}})
$$

This allows partial credit even for wrong notes when learning.

### Exponential Moving Average (EMA)

To prevent jittery UI and create smooth score transitions:

**EMA parameter:**

$$
\alpha = 0.10 + 0.30 \cdot s_{\text{strictness}}
$$

Range: $\alpha \in [0.10, 0.40]$

**Update rule:**

$$
q_{\text{EMA}}[t] = \alpha \cdot q[t] + (1 - \alpha) \cdot q_{\text{EMA}}[t-1]
$$

Where:
- $q[t]$ = current raw quality score
- $q_{\text{EMA}}[t-1]$ = previous smoothed score

**Effect:**
- Low $\alpha$ → slow changes, heavy smoothing
- High $\alpha$ → fast changes, responsive

With strictness:
- Low strictness → slow, forgiving score changes
- High strictness → fast, responsive score changes

### Phrase Window Throttling

To prevent over-updating, the EMA only updates if sufficient time has passed:

$$
\Delta t = t_{\text{current}} - t_{\text{last\_update}}
$$

Update only if:

$$
\Delta t > t_{\text{phrase}} = 0.8 \, \text{seconds}
$$

This groups notes into "phrases" and evaluates them as units.

---

## Smart Bulb Color Mapping

### Hue Calculation

Convert quality score (0-1) to HSV hue (0-120):

$$
h = \lfloor 120 \cdot q_{\text{EMA}} \rfloor
$$

Where:
- $h = 0$ → Red (poor performance)
- $h = 60$ → Yellow (average)
- $h = 120$ → Green (excellent)

### Brightness Calculation

$$
v = 300 + 700 \cdot q_{\text{EMA}}
$$

Range: $v \in [300, 1000]$ (Tuya scale)

**Effect:** Brightness increases with quality, providing additional visual cue.

### Throttling

To prevent flickering, bulb updates are throttled:

**Hue epsilon:** $\Delta h_{\text{min}} = 5$

**Time interval:** $\Delta t_{\text{min}} = 300$ ms

Update only if:

$$
|h_{\text{new}} - h_{\text{last}}| \geq 5 \quad \text{OR} \quad \Delta t \geq 300 \, \text{ms}
$$

---

## Energy Threshold (Sensitivity)

### Purpose

Determine when audio has sufficient energy to be considered a "note" vs. silence/noise.

### Calculation

**Energy:**

$$
E = \frac{1}{N} \sum_{n=1}^{N} x[n]^2
$$

**Threshold:**

$$
E_{\text{threshold}} = 10^{-7} \times (1 + 10 \cdot s_{\text{sensitivity}})
$$

Where $s_{\text{sensitivity}} \in [0, 1]$.

**Range:**
- Sensitivity = 0 → $E_{\text{threshold}} = 10^{-7}$
- Sensitivity = 0.5 → $E_{\text{threshold}} = 6 \times 10^{-7}$
- Sensitivity = 1.0 → $E_{\text{threshold}} = 11 \times 10^{-7}$

**Decision:**

$$
\text{process} = 
\begin{cases}
\text{True} & \text{if } E \geq E_{\text{threshold}} \\
\text{False} & \text{otherwise}
\end{cases}
$$

---

## Performance Optimization

### Real-Time Constraints

**Target latency:** <150 ms for feedback

**Achieved latency:** ~100-120 ms

**Processing pipeline:**
1. Audio callback fills buffer: ~22 ms (1024 samples at 44100 Hz)
2. Frame assembly: <1 ms
3. librosa pitch detection: ~50-80 ms
4. Metric calculation: ~5-10 ms
5. WebSocket transmission: ~5 ms
6. UI render: ~10-20 ms

**Total:** 100-140 ms

### Computational Complexity

**Pitch detection:** $O(N \log N)$ via FFT in librosa

**Metric calculations:** $O(N)$ for array operations

**Frame rate:** ~6.67 Hz (150 ms intervals)

**CPU usage:** 5-15% on modern processors

---

## Mathematical Notation Summary

| Symbol | Meaning |
|--------|---------|
| $x[n]$ | Discrete audio sample |
| $f_s$ | Sampling frequency (44100 Hz) |
| $f_0$ | Fundamental frequency (Hz) |
| $m$ | MIDI note number |
| $p_c$ | Pitch class (0-11) |
| $S$ | Target scale (set of pitch classes) |
| $q$ | Quality score |
| $s_{\text{pitch}}$ | Pitch accuracy score |
| $s_{\text{timing}}$ | Timing stability score |
| $s_{\text{noise}}$ | Noise control score |
| $s_{\text{coverage}}$ | Scale coverage score |
| $CV$ | Coefficient of variation |
| $\alpha$ | EMA smoothing parameter |
| $E$ | Energy (power) |
| $h$ | Hue (0-120 for red to green) |

---

## References

**Libraries:**
- [librosa documentation](https://librosa.org/doc/latest/index.html)
- [NumPy documentation](https://numpy.org/doc/)
- [sounddevice documentation](https://python-sounddevice.readthedocs.io/)

**Algorithms:**
- YIN pitch detection: de Cheveigné, A., & Kawahara, H. (2002). "YIN, a fundamental frequency estimator for speech and music." *The Journal of the Acoustical Society of America*, 111(4), 1917-1930.

**Audio Theory:**
- Smith, J. O. (2011). *Spectral Audio Signal Processing*. W3K Publishing.
- Müller, M. (2015). *Fundamentals of Music Processing*. Springer.

---

**Navigation:**
- [← Desktop Application](desktop-app.md)
- [Back to Index](index.md)
