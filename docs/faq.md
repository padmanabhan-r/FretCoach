# Frequently Asked Questions (FAQ)

FretCoach is a **Real-time Augmented Feedback (RAF)** system.

---

## General Questions

### 1. Why FretCoach?

**Because bad habits form faster than good ones.**

Traditional feedback arrives days later—recordings you analyze after practice, or a teacher who sees you once a week. By then, incorrect patterns have been repeated hundreds of times and encoded into motor memory. It takes 10-20× more repetitions to unlearn a motor habit than to prevent one from forming.

**FretCoach's solution:** Real-time intervention during the critical plasticity window—every note evaluated immediately, with visual, auditory, and environmental feedback before mistakes solidify into habits.

---

### 2. What makes it different?

**Preventive feedback, not corrective.**

Most tools record-analyze-improve: you finish playing, then review what went wrong. FretCoach operates during execution:

- **Multi-sensory feedback:** Visual metrics, AI voice coaching between phrases, ambient lighting in peripheral vision
- **Dual-brain architecture:** Fast deterministic audio analysis (<300ms) + intelligent AI coaching
- **Context-aware:** AI coach sees your full practice history and adapts to your specific weak areas

Think of it like a coach who corrects your form mid-shot, not one reviewing footage days later.

---

### 3. Is it like Guitar Hero or GarageBand?

**No—different tools for different purposes.**

- **Guitar Hero:** Plastic game controller, entertainment-focused, no transferable technique
- **GarageBand:** DAW for recording/production, post-performance analysis, not real-time coaching
- **FretCoach:** Real guitar technique training with real-time feedback during execution

FretCoach is a **practice coach** and skill development system—not a game, not a recording tool.

---

### 4. How does it work?

**Dual-brain architecture combining speed and intelligence:**

**Audio Analysis Engine (Fast Loop — "Left Brain"):**
- <300ms latency, processes every note continuously
- Evaluates pitch accuracy, scale conformity, timing stability, and noise
- Controls on-screen metrics and ambient lighting
- Pure local computation—no AI, no cloud dependency

**AI Coach Agent (Slow Loop — "Right Brain"):**
- Live voice coaching during practice (every 20-30 seconds)
- Practice plan generation from your session history
- Conversational coaching in FretCoach Hub (chat interface)
- Powered by GPT-4o-mini (Studio) and Gemini 3 Flash Preview (Hub)

The fast loop handles immediate feedback; the slow loop provides strategic intelligence.

---

### 5. How is the audio signal processed so fast?

**Local DSP pipeline with no cloud round-trips.**

Guitar audio is captured in 2048-sample buffers (~46ms at 44.1kHz), analyzed via FFT pitch detection (librosa pyin), and metrics are computed—all on-device. Total latency stays under 300ms because nothing leaves your machine.

---

### 6. Isn't it just another guitar app?

**No—it's a practice coach, not a utility tool.**

| Category | Examples | FretCoach difference |
|----------|----------|---------------------|
| Setup tools | Tuners, metronomes | Continuous guidance throughout your session |
| Content libraries | Ultimate Guitar, Songsterr | Active coaching on technique, not passive content |
| Recording/analysis | GarageBand, Logic | Real-time feedback *during* playing, not after |
| Learning platforms | JustinGuitar, Fender Play | Technique feedback complementing instructional content |

---

### 7. How does it control the light?

**Performance score mapped to smart bulb color via Tuya Cloud API.**

Your 4-metric score is aggregated each buffer cycle and mapped to RGB:

| Score | Color | Meaning |
|-------|-------|---------|
| 70-100% | 🟢 Green | Excellent |
| 50-70% | 🟡 Yellow-Green | Good, room to improve |
| 30-50% | 🟠 Orange | Needs focus |
| 0-30% | 🔴 Red | Slow down |

Peripheral vision picks up color changes without breaking focus on your fretboard. Completely optional—leave `HAVELLS_*` env vars blank to disable.

---

### 8. How do AI and Audio Analysis work together?

**Two independent loops communicating through the database.**

Audio analysis must be fast and deterministic—it can't wait for LLM inference (500-3000ms). So they run independently:

```
[Audio Analysis Loop] → writes metrics to DB
[AI Coach Loop]       → reads metrics from DB
```

If the AI coach fails (API error, rate limit), audio analysis continues unaffected. Each loop does what it's best at: speed vs. intelligence.

This architecture—fast real-time signal augmented by intelligent context—is what we call **Real-time Augmented Feedback (RAF)**.

---

### 9. What is Real-time Augmented Feedback (RAF)?

**A design pattern that augments real-time feedback with contextual intelligence.**

We refer to this pattern as **Real-time Augmented Feedback (RAF)**, analogous to how RAG (Retrieval-Augmented Generation) augments generation with retrieval.

In FretCoach's case:
- **RAG:** Retrieved context → augments LLM response quality
- **RAF:** Real-time audio analysis → augments practice feedback with live performance context

The fast deterministic loop provides the real-time signal; the slow AI loop augments it with coaching intelligence grounded in your session history. The result: feedback that is both immediate (<300ms) and contextually intelligent.

This pattern generalizes beyond guitar—any skill-based training domain requiring fast sensor feedback augmented by intelligent analysis can adopt the RAF approach.

---

### 10. Where is the pedal?

**Raspberry Pi 5 prototype is working—physical enclosure is next.**

The software runs on Pi 5 with a Focusrite Scarlett Solo. All features work (audio analysis, smart bulb, database sync). The next step is a compact pedalboard-style enclosure with integrated audio input, footswitch, and LCD screen.

---

### 11. What's the future? Next steps?

**Immediate:**
- Physical pedal enclosure (compact form factor with footswitch and LCD)
- More training modes: arpeggios, chord progressions, alternate picking

**Planned:**
- Multi-instrument support (bass, piano, vocals, drums)
- Mobile companion app

---

## Technical Questions

### 12. What tech stack does FretCoach use?

**Desktop Application (FretCoach Studio):**
- **Frontend:** Electron 28, React 18, Vite, Tailwind CSS
- **Backend:** Python FastAPI, sounddevice, librosa, NumPy/SciPy
- **AI:** OpenAI GPT-4o-mini, LangChain, Pydantic

**Web Platform (FretCoach Hub):**
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui, Recharts, TanStack Query
- **Backend:** Python FastAPI, LangChain + LangGraph, Google Gemini 3 Flash Preview, SQLAlchemy

**Shared:**
- **Database:** PostgreSQL via Supabase
- **AI observability:** Comet Opik
- **Smart bulb:** Tuya Cloud API, tinytuya
- **Deployment:** Vercel (frontend), Railway (backend)

---

### 13. Does it work offline?

**Manual Mode works fully offline; AI features require internet.**

| Feature | Offline? |
|---------|----------|
| Real-time audio analysis + metrics | ✅ |
| Visual feedback, smart bulb | ✅ |
| Session logging (syncs to cloud later) | ✅ |
| AI voice coaching, practice plans | ❌ |
| FretCoach Hub AI chat | ❌ |

Manual Mode gives you the full real-time training experience with zero cloud dependency.

---

### 14. What audio interface do I need?

**Focusrite Scarlett Solo (~$100) is recommended.**

Low-noise preamps, high-impedance guitar input, works out-of-box on Mac/Windows/Linux. Alternatives: PreSonus AudioBox USB 96, Behringer U-Phoria UM2 (~$50 budget option).

Built-in microphone works for testing but picks up room noise and reduces pitch detection accuracy. Not recommended for regular practice.

---

### 15. Can I use it with an electric guitar? Acoustic?

**Both work. Electric is the optimal setup.**

- **Electric → audio interface:** Best signal, most accurate pitch detection
- **Acoustic-electric → audio interface:** Equally good
- **Acoustic → microphone:** Works, but environmental noise affects accuracy
- **Acoustic → built-in mic:** OK for testing only

---

### 16. Is it open source?

**Yes—MIT-style license.**

- **Main repo:** [github.com/padmanabhan-r/FretCoach](https://github.com/padmanabhan-r/FretCoach)
- **Web backend:** [github.com/padmanabhan-r/FretCoach-Web-Backend](https://github.com/padmanabhan-r/FretCoach-Web-Backend)
- **Web frontend:** [github.com/padmanabhan-r/FretCoach-Web-Frontend](https://github.com/padmanabhan-r/FretCoach-Web-Frontend)

You can clone, modify, fork, and deploy your own instance. Don't use the FretCoach name/branding commercially without permission.

---

### 17. Does it support other instruments besides guitar?

**Guitar only right now—multi-instrument support is planned.**

Fully supported: 6-string electric and acoustic, standard and alternate tunings, extended range (7-8 string with config). The audio engine is instrument-agnostic (FFT pitch detection works for any tonal instrument), so bass, piano, vocals, and drums are on the roadmap.

---

### 18. How accurate is the pitch detection?

**±10 cents—at the threshold of human pitch perception.**

Uses probabilistic YIN (librosa.pyin), the industry standard for monophonic pitch tracking. Works best with clean single-note playing through an audio interface. Accuracy degrades with chords, heavy distortion, or noisy environments.

---

### 19. Can I customize the metrics or feedback?

**Yes, partially.**

- **Metric weights:** Stored in `user_configs` table—adjust pitch/scale/timing importance
- **Ambient lighting thresholds:** Configurable in code (score → color mapping)
- **Scale library:** Add custom scales via database or config file
- **AI coach behavior:** Automatically adapts to your weak areas

---

### 20. Does it work on Windows? Mac? Linux?

| Platform | Support | Notes |
|----------|---------|-------|
| macOS | ✅ Fully tested | Primary dev platform |
| Windows | ✅ Supported | Needs ASIO drivers for audio |
| Linux | ⚠️ Should work | Limited testing |
| Raspberry Pi OS | ✅ Tested | FretCoach Portable |

FretCoach Hub works on any platform via browser (Chrome/Firefox/Safari).

---

### 21. How much does it cost?

**Free and open source. Hardware is optional.**

| Item | Cost |
|------|------|
| Software | $0 |
| Audio interface (Scarlett Solo) | ~$100 |
| Raspberry Pi 5 portable setup | ~$180 additional |
| Smart bulb | ~$10-20 |

AI features use your own API keys. Estimated cost: <$1/month for light usage; free tiers (Gemini, Supabase) cover most users.

---

### 22. Can I use it with my existing practice routine?

**Yes—use it for technique drills, not creative playing.**

- **Warm-up/drills:** Use FretCoach—builds motor patterns with instant feedback
- **Learning songs/improvisation:** Skip it—creativity thrives without metric evaluation
- **Performance runs:** Skip it—focus on flow and musicality

FretCoach is a technique trainer, not a judge of musical expression.

---

### 23. How do I get started?

1. Visit [fretcoach.online](https://www.fretcoach.online) to explore the Hub (no install needed)
2. Clone the repo and follow the [Environment Setup Guide](environment-setup.md) for local install
3. Connect guitar → select scale → start practicing in Manual Mode

See the [Quickstart Guide](quickstart.md) for step-by-step instructions.

---

### 24. I found a bug. How do I report it?

Open a **GitHub Issue** at [github.com/padmanabhan-r/FretCoach/issues](https://github.com/padmanabhan-r/FretCoach/issues).

Include: OS + versions, steps to reproduce, expected vs. actual behavior, and any relevant logs or screenshots. For security vulnerabilities, use GitHub's private vulnerability reporting instead of a public issue.

---

### 25. Can I contribute to the project?

**Yes—code, docs, testing, and design contributions are all welcome.**

1. Find or create a [GitHub Issue](https://github.com/padmanabhan-r/FretCoach/issues)
2. Fork the repo and create a branch (`git checkout -b feature/your-feature`)
3. Make changes following existing style (PEP 8 for Python, Prettier/ESLint for JS)
4. Submit a pull request referencing the issue

Good first issues are tagged `good first issue`. Ask questions in GitHub Discussions.

---

**Still have questions?** Open an issue on [GitHub](https://github.com/padmanabhan-r/FretCoach/issues) or explore the [full documentation](https://padmanabhan-r.github.io/FretCoach/).
