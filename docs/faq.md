# Frequently Asked Questions (FAQ)

---

## General Questions

### 1. Why FretCoach?

**Because bad habits form faster than good ones.**

Traditional practice methods give you feedback days or weeks later—after mistakes have already solidified into motor memory. FretCoach intervenes in real time, **before habits form**, making learning 10-20× more efficient.

---

### 2. What makes it different?

**Preventive feedback, not corrective.**

Most tools analyze recordings after you're done. FretCoach listens **as you play** and gives instant feedback through visual metrics, voice coaching, and ambient lighting. It's like having a coach sitting next to you—except the coach never gets tired.

---

### 3. Is it like Guitar Hero or GarageBand?

**No.**

- **Guitar Hero:** A rhythm game with plastic guitars. FretCoach uses real guitars and teaches actual technique.
- **GarageBand:** A recording/composition tool. FretCoach is a practice coach—it doesn't record tracks, it trains your playing.

FretCoach focuses on **skill acquisition through real-time feedback**, not entertainment or music production.

---

### 4. How does it work?

**Two-brain architecture:**

1. **Audio Analysis Engine (Fast Loop)** — Processes your playing in real time (<300ms), evaluates pitch, scale conformity, timing, and noise. Runs locally on-device.
2. **AI Coach (Slow Loop)** — Powered by LLMs (Gemini 2.5 Flash, GPT-4o-mini), provides strategic coaching, practice recommendations, and session insights.

**Result:** Instant feedback during practice + intelligent guidance for long-term improvement.

---

### 5. How is the audio signal processed so fast?

**Optimized for real-time performance:**

| Parameter | Value | Why |
|-----------|-------|-----|
| **Buffer Size** | 2048 samples | Balance between latency and processing stability |
| **Sample Rate** | 44100 Hz | Standard audio quality, efficient processing |
| **Latency** | <300ms | Fast enough for real-time feedback without disrupting flow |
| **Processing** | Local on-device | No cloud dependency, zero network delays |

**How it works:**
1. Audio captured via USB interface or built-in mic
2. Buffered in 2048-sample chunks (~46ms per chunk)
3. Processed using Fast Fourier Transform (FFT) for pitch detection
4. Metrics computed using librosa, NumPy, and custom algorithms
5. Results displayed + sent to AI coach + ambient lighting

**No cloud processing = consistent low latency.**

---

### 6. Isn't it just another guitar app?

**No.**

Most guitar apps are either:
- **Tuners** — One-time setup tools
- **Tab libraries** — Static sheet music
- **Recording tools** — Post-practice analysis

FretCoach is a **live practice coach** that actively trains you during execution. It's the difference between watching a workout video and having a personal trainer correct your form in real time.

---

### 7. How does it control the light?

**Smart bulb integration via Tuya Cloud API.**

- FretCoach calculates your average performance score every few seconds
- Sends color commands to a WiFi-enabled smart bulb (Tuya-compatible)
- **Color mapping:**
  - 🟢 Green → Excellent (70%+)
  - 🟡 Yellow → Good (50-70%)
  - 🟠 Orange → Average (30-50%)
  - 🔴 Red → Needs work (<30%)

**Optional feature** — FretCoach works perfectly without the bulb. Just leave the `HAVELLS_*` env variables blank.

---

### 8. How do AI and Audio Analysis work together?

**Dual-loop architecture:**

**Fast Loop (Audio Analysis Agent):**
- Runs continuously (<300ms latency)
- Computes 4 core metrics: pitch accuracy, scale conformity, timing stability, noise control
- Deterministic, fast, local processing
- No AI—pure signal processing

**Slow Loop (AI Coach Agent):**
- Triggered on-demand (not real-time critical)
- Uses LLMs to analyze patterns, identify weak areas, generate practice plans
- Provides voice feedback during live sessions
- Post-session strategic insights

**Why separate?** Audio processing must be **fast and reliable**. AI is **intelligent but slower**. Separating them ensures real-time feedback never blocks on LLM calls.

---

### 9. Where is the pedal?

**It's in prototyping!**

FretCoach Portable runs on a Raspberry Pi 5 right now. The vision is a physical pedal-style enclosure with:
- LCD touchscreen
- Footswitch for on/off control
- Integrated audio input
- Battery power option

**Current status:** Hardware tested, software integrated, enclosure design planned.

---

### 10. What's the future? Next steps?

**Starts with guitar. Expands everywhere.**

**Short-term:**
- Physical pedal enclosure for FretCoach Portable
- More scales and training modes (arpeggios, chord progressions)
- Mobile app (iOS/Android)

**Long-term:**
- Multi-instrument support (piano, vocals, drums, bass)
- Vision-based feedback (computer vision for posture/technique)
- Sport/skill training (basketball free throws, dance, speech coaching)

**Core vision:** AI-powered instant feedback for any skill-based learning—not just music.

---

## Technical Questions

### 11. What tech stack does FretCoach use?

**Desktop (FretCoach Studio):**
- Electron, React, Python FastAPI
- librosa, NumPy, SciPy for audio processing
- OpenAI GPT-4o-mini (TTS + coaching)

**Web (FretCoach Hub):**
- React, TypeScript, Tailwind CSS, shadcn/ui
- Python FastAPI backend
- LangChain + LangGraph for AI orchestration
- Gemini 2.5 Flash (conversational AI coach)

**Database:** PostgreSQL (Supabase)

**Observability:** Comet Opik

---

### 12. Does it work offline?

**Partially.**

- **Manual Mode:** Fully offline (audio analysis runs locally)
- **AI Mode:** Requires internet for LLM calls (practice plan generation, voice coaching)

FretCoach Portable and Studio can function in Manual Mode with zero internet dependency.

---

### 13. What audio interface do I need?

**Recommended:** Focusrite Scarlett Solo (USB audio interface)

**But you can use:**
- Built-in Mac/PC microphone (works, but less accurate)
- Any USB audio interface with mic/line input
- Direct guitar-to-USB cables

**Why Scarlett Solo?** Clean signal, low noise, widely available, affordable.

---

### 14. Can I use it with an electric guitar? Acoustic?

**Both.**

- **Electric:** Plug directly into the audio interface (recommended for cleanest signal)
- **Acoustic:** Use a microphone (built-in or external)

Electric guitars generally give cleaner signals for analysis, but acoustic works fine.

---

### 15. Is it open source?

**Yes.**

- Main repo: [github.com/padmanabhan-r/FretCoach](https://github.com/padmanabhan-r/FretCoach)
- Web backend: [github.com/padmanabhan-r/FretCoach-Web-Backend](https://github.com/padmanabhan-r/FretCoach-Web-Backend)
- Web frontend: [github.com/padmanabhan-r/FretCoach-Web-Frontend](https://github.com/padmanabhan-r/FretCoach-Web-Frontend)

Contributions, bug reports, and feature requests welcome.

---

### 16. Does it support other instruments besides guitar?

**Not yet, but it's designed to.**

The audio analysis engine is instrument-agnostic. With tuning adjustments, it could evaluate:
- Bass guitar
- Piano/keyboard
- Vocals
- Drums (with different metrics)

**Roadmap item:** Multi-instrument support coming in future releases.

---

### 17. How accurate is the pitch detection?

**Very accurate for clean signals.**

FretCoach uses FFT-based pitch detection with:
- ±10 cent tolerance (standard for human perception)
- Real-time tracking with <300ms latency
- Noise filtering to reduce false positives

**Best results:** Use an audio interface (Scarlett Solo) for cleanest input signal.

---

### 18. Can I customize the metrics or feedback?

**Yes, partially.**

- **User configs table:** Stores your preferred metric weights (pitch, scale, timing)
- **AI coaching:** Adapts based on your playing history
- **Lighting thresholds:** Can be adjusted in code

**Planned:** More granular customization in future UI updates.

---

### 19. Does it work on Windows? Mac? Linux?

**Desktop App (Studio):**
- ✅ macOS (primary development platform)
- ✅ Windows (tested, works)
- ⚠️ Linux (should work, not extensively tested)

**Web App (Hub):**
- ✅ All platforms (runs in browser)

**Portable:**
- ✅ Raspberry Pi OS (Debian-based Linux)

---

### 20. How much does it cost?

**Free.**

FretCoach is open source. You only need:
- A computer (for Studio)
- Optional: Audio interface (~$100 for Scarlett Solo)
- Optional: Raspberry Pi 5 setup (~$150 for Portable)
- Optional: Smart bulb (~$10-20 for ambient lighting)

**No subscriptions. No paywalls.**

---

### 21. Can I use it with my existing practice routine?

**Absolutely.**

FretCoach complements traditional practice:
- Use it for focused technique work (scales, timing drills)
- Then switch to your regular playing (songs, improvisation)

It's not a replacement for creative playing—it's a **technique trainer** for building foundational skills.

---

### 22. How do I get started?

**Quickest path:**

1. Visit [fretcoach.online](https://www.fretcoach.online) to explore the web dashboard
2. Check the [Quickstart Guide](quickstart.md)
3. Clone the repo and run FretCoach Studio locally

**Need help?** See [Environment Setup](environment-setup.md) for detailed installation instructions.

---

### 23. I found a bug. How do I report it?

**GitHub Issues:**
[github.com/padmanabhan-r/FretCoach/issues](https://github.com/padmanabhan-r/FretCoach/issues)

Please include:
- OS and version
- Steps to reproduce
- Expected vs actual behavior
- Screenshots/logs if possible

---

### 24. Can I contribute to the project?

**Yes! Contributions welcome:**

- Code improvements
- Bug fixes
- Documentation updates
- Feature suggestions
- Testing on different platforms

See [Contributing](../README.md#contributing) for guidelines.

---

**Still have questions?** Open an issue on GitHub or explore the [full documentation](https://padmanabhan-r.github.io/FretCoach/).
