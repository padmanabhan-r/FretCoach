# Frequently Asked Questions (FAQ)

---

## General Questions

### 1. Why FretCoach?

**Because bad habits form faster than good ones.**

Traditional practice methods give you feedback days or weeks later—through recordings you analyze after practice, or worse, through a teacher who sees you once a week. By then, incorrect finger positions, poor timing, and sloppy technique have already been repeated hundreds of times, encoding themselves into motor memory.

**The neuroscience problem:** It takes 10-20× more repetitions to unlearn a motor habit than to prevent one from forming. Early-stage neuroplasticity is fast and fragile—your brain rapidly adapts to whatever patterns you repeat, whether they're correct or not.

**FretCoach's solution:** Real-time intervention during the critical plasticity window. Every note you play is evaluated immediately, with visual, auditory, and environmental feedback that reinforces correct patterns and flags incorrect ones **before they solidify into habits**.

---

### 2. What makes it different?

**Preventive feedback, not corrective.**

Most practice tools operate on a record-analyze-improve cycle: you record yourself playing, listen back later, identify mistakes, and try to fix them next time. This is **corrective feedback**—you're retrofitting correct technique onto already-formed motor patterns.

FretCoach operates differently with **preventive feedback**:

- **During execution:** Feedback arrives while you're still playing, not after you've finished
- **Multi-sensory channels:** Visual metrics on screen, AI voice coaching between phrases, ambient lighting in your peripheral vision
- **Dual-brain architecture:** Fast deterministic audio analysis (<300ms) handles real-time metrics, while intelligent AI coaching provides strategic guidance
- **Context-aware coaching:** The AI coach sees your full practice history and adapts recommendations to your specific weak areas

Think of it like having a basketball coach who corrects your shooting form mid-shot, rather than reviewing game footage days later. The feedback loop is measured in milliseconds, not days.

---

### 3. Is it like Guitar Hero or GarageBand?

**No—different tools for different purposes.**

**Guitar Hero:**
- Uses plastic game controllers, not real guitars
- Teaches rhythm game mechanics, not actual guitar technique
- Focuses on entertainment and score-chasing
- No transferable skill to real instrument playing

**GarageBand:**
- A Digital Audio Workstation (DAW) for recording and music production
- Designed for composition, multi-track recording, and mixing
- Post-performance tool—you analyze recordings after playing
- Doesn't provide real-time feedback or technique coaching

**FretCoach:**
- Uses real guitars with real technique requirements
- Focuses on skill acquisition through deliberate practice
- Real-time coaching during execution, not post-analysis
- Trains motor patterns for actual guitar playing
- Not for recording songs—for building foundational technique

The difference: Guitar Hero is a game. GarageBand is a production tool. FretCoach is a **practice coach** and **skill development system**.

---

### 4. How does it work?

**Dual-brain architecture combining speed and intelligence:**

**Audio Analysis Engine (Fast Loop) — "Left Brain":**
- Runs continuously with <300ms latency
- Processes audio in real-time using digital signal processing (DSP)
- Evaluates 4 core metrics every buffer cycle:
  - **Pitch Accuracy:** Detects notes played, compares against target scale
  - **Scale Conformity:** Checks if notes belong to the selected scale
  - **Timing Stability:** Measures rhythmic consistency and note spacing
  - **Noise Control:** Quantifies unwanted string noise and artifacts
- Controls on-screen metrics display and ambient lighting system
- Pure computation—no AI, deterministic and reliable
- Runs locally on-device with zero cloud dependency

**AI Coach Agent (Slow Loop) — "Right Brain":**
- Powered by LLMs (Gemini 3 Flash Preview for Hub, GPT-4o-mini for Studio)
- Provides three types of coaching:
  1. **Live voice coaching:** Speaks feedback during practice sessions at regular intervals
  2. **Practice plan generation:** Analyzes your session history and creates personalized recommendations
  3. **Conversational coaching:** Chat-based coach in FretCoach Hub that answers questions about your progress
- Uses LangGraph for agent orchestration with tool-calling capabilities
- Accesses your practice database to provide context-aware recommendations
- Triggered on-demand, not real-time critical

**Result:** The fast loop ensures you never miss immediate feedback, while the slow loop provides the strategic intelligence a human coach would offer.

---

### 5. How is the audio signal processed so fast?

**Optimized pipeline from hardware to software:**

**Signal Flow:**
```
Guitar → Audio Interface → Computer Sound Card →
Buffer (2048 samples) → FFT Analysis →
Pitch Detection → Metric Computation →
UI Update + AI Coach + Lighting
```

**Key Parameters:**

| Parameter | Value | Technical Rationale |
|-----------|-------|---------------------|
| **Buffer Size** | 2048 samples | Sweet spot between latency and stability. Smaller buffers (512-1024) cause audio glitches; larger buffers (4096+) feel sluggish. |
| **Sample Rate** | 44100 Hz | Standard CD-quality audio. Higher rates (96kHz) don't improve pitch detection for guitar range (80-1200 Hz). |
| **Hop Length** | 512 samples | For Short-Time Fourier Transform (STFT). Balances time resolution with frequency resolution. |
| **Processing Latency** | <300ms | Total time from sound input to visual feedback. Fast enough to feel "instant" without disrupting practice flow. |
| **FFT Window** | Hann window | Reduces spectral leakage in frequency domain analysis. |

**Processing Pipeline Details:**

1. **Audio Capture (46ms per buffer):**
   - USB interface or built-in mic captures raw audio
   - 2048 samples at 44100 Hz = ~46ms per chunk
   - Continuous buffer streaming with no gaps

2. **Pitch Detection (librosa.pyin):**
   - Probabilistic YIN algorithm for guitar pitch tracking
   - Handles polyphonic input (multiple strings ringing)
   - 10-cent accuracy tolerance (standard for human pitch perception)
   - Outputs fundamental frequency (f0) and confidence score

3. **Metric Computation:**
   - **Pitch Accuracy:** Compare detected f0 against target note frequencies
   - **Scale Conformity:** Check if detected notes match scale degrees
   - **Timing Stability:** Analyze inter-onset intervals (time between note attacks)
   - **Noise:** RMS energy analysis during silence periods between notes

4. **Output Distribution:**
   - Metrics sent to UI for real-time display
   - Aggregated data fed to AI coach for strategic analysis
   - Performance score mapped to smart bulb color (if enabled)

**Why local processing matters:** No network round-trips, no cloud API latency, no dependency on internet connection. The audio never leaves your device, ensuring consistent sub-300ms performance.

---

### 6. Isn't it just another guitar app?

**No—it's a practice coach, not a utility tool.**

Let's break down the guitar app landscape:

**Category 1: Setup Tools**
- Tuners (Guitar Tuna, Fender Tune)
- Metronomes
- **Use case:** One-time setup before practice
- **FretCoach difference:** Continuous guidance throughout your entire session

**Category 2: Content Libraries**
- Tab apps (Ultimate Guitar, Songsterr)
- Chord libraries
- **Use case:** Sheet music and reference material
- **FretCoach difference:** Active coaching on technique, not passive content consumption

**Category 3: Recording/Analysis Tools**
- DAWs (GarageBand, Logic Pro)
- Recording apps (AmpliTube, BIAS FX)
- **Use case:** Post-performance analysis
- **FretCoach difference:** Real-time feedback during execution, not after

**Category 4: Learning Platforms**
- Video lesson platforms (JustinGuitar, Fender Play)
- Interactive courses
- **Use case:** Instructional content and curriculum
- **FretCoach difference:** Real-time technical feedback, complementing instructional content

**Where FretCoach fits:**

FretCoach is a **practice coach**—it sits beside you during practice and actively trains your technique through:
- Instant feedback on every note
- AI-powered strategic guidance
- Progress tracking and weak area identification
- Adaptive practice plan generation

Think of it as the difference between:
- **Other apps:** Providing tools, content, or analysis
- **FretCoach:** Being an active participant in your practice session

---

### 7. How does it control the light?

**Smart bulb integration via Tuya Cloud API with real-time performance mapping.**

**Technical Setup:**

1. **Hardware:** WiFi-enabled smart bulb (Tuya-compatible, e.g., Havells Smart Bulb)
2. **API Integration:** Python `tinytuya` library (v1.17.4) for Tuya Cloud communication
3. **Color Calculation:** Performance score aggregated from 4 metrics mapped to RGB values

**How It Works:**

```
Audio Analysis → Performance Score (0-100%) →
Color Mapping → Tuya API Call →
Smart Bulb Color Change
```

**Color Mapping Logic:**

| Score Range | Color | RGB Values | Meaning |
|-------------|-------|------------|---------|
| 70-100% | 🟢 Green | (0, 255, 0) | Excellent playing—technique on point |
| 50-70% | 🟡 Yellow-Green | (128, 255, 0) | Good, but room for improvement |
| 30-50% | 🟠 Orange | (255, 165, 0) | Average—needs focused practice |
| 0-30% | 🔴 Red | (255, 0, 0) | Below target—slow down and focus |

**Update Frequency:** Every 3-5 seconds (configurable)

**Environmental Feedback Psychology:**

Why ambient lighting works:
- **Peripheral vision feedback:** You see color changes without breaking focus on your hands/fretboard
- **Subconscious reinforcement:** Green = reward signal, red = correction needed
- **Flow state maintenance:** Non-intrusive feedback that doesn't interrupt playing momentum
- **Multi-sensory learning:** Visual + auditory feedback strengthens neural encoding

**Completely Optional:**

If you don't have a smart bulb or don't want to set one up, just leave the `HAVELLS_*` environment variables blank in your `.env` file. FretCoach detects the missing configuration and disables lighting features automatically—all other functionality works perfectly.

**Supported Bulbs:** Any Tuya-compatible smart bulb. The code can be adapted for Philips Hue, LIFX, or other smart lighting platforms.

---

### 8. How do AI and Audio Analysis work together?

**Dual-loop architecture with clear separation of concerns:**

**Why Separate Them?**

Audio analysis must be **fast, deterministic, and reliable**—it can't afford to wait for network calls or handle probabilistic AI responses. AI coaching is **intelligent but slower**—LLM inference takes 500-3000ms, which would block real-time feedback.

**Solution:** Two independent loops that communicate asynchronously.

---

**Fast Loop (Audio Analysis Agent):**

**Responsibilities:**
- Real-time audio processing (<300ms latency)
- Continuous metric computation (pitch, scale, timing, noise)
- Visual feedback updates (on-screen metrics display)
- Ambient lighting control

**Technology Stack:**
- Python `librosa` for DSP
- NumPy/SciPy for mathematical operations
- Pure computation—no AI, no LLM calls
- Local processing with zero network dependency

**Runs:** Continuously during practice sessions

**Output:**
- Real-time performance metrics
- Aggregated session data stored in database

---

**Slow Loop (AI Coach Agent):**

**Responsibilities:**
1. **Live Voice Coaching (Studio):**
   - Monitors your playing every 20-30 seconds
   - Analyzes current metrics vs. recent performance
   - Generates contextual spoken feedback: "Great pitch accuracy! Now focus on timing consistency."
   - Uses GPT-4o-mini + GPT-4o-mini-TTS for voice synthesis

2. **Practice Plan Generation (Studio + Hub):**
   - Analyzes your session history from database
   - Identifies weakest metric areas
   - Generates personalized recommendations with specific scales, difficulty levels
   - Uses GPT-4o-mini with structured JSON output

3. **Conversational Coaching (Hub):**
   - LangGraph agent with text-to-SQL tool
   - Answers questions like "What's my weakest metric?" or "Show my progress over time"
   - Uses Gemini 3 Flash Preview for natural language understanding
   - Database-grounded responses with citation of actual session data

**Technology Stack:**
- LangChain + LangGraph for agent orchestration
- OpenAI GPT-4o-mini (Studio coaching)
- Google Gemini 3 Flash Preview (Hub conversational coach)
- Comet Opik for LLM observability and evaluation

**Runs:** On-demand, triggered by user actions or periodic intervals

**Output:**
- Voice feedback audio
- Practice plan recommendations
- Conversational coaching responses

---

**Data Flow Between Loops:**

```
[Audio Analysis Loop]
  ↓ (writes to DB)
[PostgreSQL Database]
  ↑ (reads from DB)
[AI Coach Loop]
```

- **Async communication:** No direct coupling between loops
- **Database as contract:** Session metrics written by analysis engine, read by AI coach
- **Independent failures:** If AI coach fails (network issue, API error), audio analysis continues unaffected

**Example Workflow:**

1. **During practice:** Fast loop processes every note, displays metrics in real-time
2. **Every 30 seconds:** AI coach reads recent metrics, generates voice feedback if improvement areas detected
3. **After session:** Fast loop writes final session summary to database
4. **User opens Hub:** AI coach analyzes session history, generates practice plan for next session

**Result:** Speed where it matters (real-time analysis) + intelligence where it adds value (strategic coaching).

---

### 9. Where is the pedal?

**It's in prototyping—here's the roadmap:**

**Current State (Raspberry Pi 5 Prototype):**

✅ **Hardware tested and working:**
- Raspberry Pi 5 (8GB RAM)
- Focusrite Scarlett Solo USB audio interface
- 64GB microSD card with Raspberry Pi OS
- Power supply and cooling

✅ **Software integrated:**
- Same audio analysis engine as FretCoach Studio
- Real-time metric computation working on ARM architecture
- Database sync with Supabase implemented
- Smart bulb integration functional

✅ **Proof of concept complete:**
- Can practice with portable unit completely independent of laptop
- Edge processing—no cloud dependency for Manual Mode
- Performance metrics comparable to desktop version

---

**Next Steps (Physical Pedal Design):**

📋 **Planned features:**

**Enclosure Design:**
- Compact pedal-style form factor (similar to guitar effects pedals)
- Durable aluminum or steel enclosure
- Rubber feet for stage/floor use
- Cable routing and strain relief

**User Interface:**
- 3.5" LCD touchscreen for metric display
- Tactile buttons for mode selection (Manual vs. AI Mode)
- LED indicators for power, status, connectivity

**Input/Output:**
- 1/4" guitar input jack (standard instrument cable)
- Integrated audio interface (eliminates need for Scarlett Solo)
- USB-C for power and firmware updates
- WiFi for database sync and AI features

**Controls:**
- Footswitch for on/off control (hands-free operation during practice)
- Rotary encoders for volume and sensitivity adjustment
- Scale selection via touchscreen

**Power:**
- Wall adapter for studio use
- Rechargeable battery option for portability (2-4 hour battery life target)

---

**Why Pedal Form Factor?**

- **Familiar to guitarists:** Looks and feels like existing gear (tuner pedals, effects pedals)
- **Portability:** Take to rehearsals, lessons, gigs
- **Minimal setup:** Plug in guitar → power on → practice
- **Floor-based control:** Footswitch allows hands-free operation
- **Practice-first design:** Not a recording tool or effects processor—purely focused on technique training

**Timeline:** Enclosure design and prototyping planned for next development phase. Community contributions welcome for industrial design and electronics integration.

---

### 10. What's the future? Next steps?

**Starts with guitar. Expands everywhere.**

**Core Vision:** AI-powered instant feedback for any skill-based learning—not just music, but any domain where real-time coaching improves motor skill acquisition.

---

**Short-Term Roadmap (Next 3-6 Months):**

**FretCoach Portable Completion:**
- Physical pedal enclosure design
- Integrated audio input (eliminate external USB interface)
- Footswitch control for hands-free operation
- Battery power option for true portability

**Expanded Training Modes:**
- Arpeggios (chord tone exercises)
- Chord progressions (rhythm guitar training)
- Alternate picking patterns
- Speed drills with tempo ramping

**Mobile Application:**
- iOS and Android companion apps
- Practice session review on phone/tablet
- Push notifications for practice reminders
- Mobile-friendly dashboard

**Onboarding & UX Improvements:**
- Interactive tutorial for first-time users
- Video guides for setup and calibration
- In-app tooltips and contextual help
- Simplified configuration workflow

---

**Medium-Term Goals (6-12 Months):**

**Multi-Instrument Support:**

**Piano/Keyboard:**
- Polyphonic note detection
- Hand independence metrics (left vs. right hand)
- Chord accuracy evaluation
- Rhythm and pedaling feedback

**Vocals:**
- Pitch accuracy for melody lines
- Vibrato consistency analysis
- Breath control metrics
- Range training with target note visualization

**Bass Guitar:**
- Low-frequency pitch detection optimization
- Groove and timing emphasis
- Dynamics and articulation tracking

**Drums:**
- Rhythm pattern recognition via microphone array or MIDI input
- Timing consistency across different drum voices
- Dynamics (velocity) tracking

---

**Long-Term Vision (1-2+ Years):**

**Vision-Based Feedback:**
- Computer vision for posture analysis
- Hand position and finger placement detection
- Body mechanics evaluation (guitar angle, wrist position)
- Augmented reality overlays for visual guidance

**Sport & Skill Training Expansion:**
- **Basketball:** Free throw form analysis using motion tracking
- **Dance:** Movement timing and posture feedback
- **Speech/Presentation:** Vocal clarity, pacing, filler word detection
- **Typing:** Keystroke timing and accuracy training

**Adaptive Learning System:**
- Difficulty auto-adjustment based on performance trends
- Personalized skill trees and progression paths
- Spaced repetition scheduling for technique drills
- Gamification with achievements and streaks

**Community Features:**
- Leaderboards and challenges
- Practice session sharing
- Technique tutorials from advanced users
- Collaborative practice sessions (multiplayer practice modes)

**Hardware Innovations:**
- Wearable sensors for posture and hand position tracking
- Force-sensitive fret sensors for finger pressure analysis
- Integrated metronome with haptic feedback (vibration)
- Multi-device ecosystem (watch, headphones, smart lighting)

---

**Guiding Question:**

> If feedback arrived the moment you made a mistake, how would that change the way you practice?
> And what skill would you want AI to coach you on?

FretCoach is building toward a future where instant, intelligent feedback accelerates skill acquisition across any domain that requires deliberate practice.

---

## Technical Questions

### 11. What tech stack does FretCoach use?

**Desktop Application (FretCoach Studio):**

**Runtime & Frontend:**
- **Electron 28:** Cross-platform desktop framework (Chromium + Node.js)
- **React 18:** UI component library with hooks and functional components
- **Vite:** Fast build tool and dev server with hot module replacement
- **Tailwind CSS:** Utility-first styling for responsive UI

**Backend (Embedded Python FastAPI):**
- **Python 3.12+:** Primary language for audio processing and AI orchestration
- **FastAPI 0.109+:** Async web framework for REST API endpoints
- **Uvicorn:** ASGI server for hosting FastAPI backend

**Audio Processing:**
- **librosa 0.10+:** Music and audio analysis library
- **NumPy:** Numerical computing for array operations
- **SciPy:** Scientific computing for signal processing
- **sounddevice:** Cross-platform audio I/O

**AI & LLM Integration:**
- **OpenAI API:** GPT-4o-mini for practice plan generation
- **GPT-4o-mini-TTS:** Text-to-speech for voice coaching
- **LangChain:** LLM orchestration framework
- **Pydantic:** Data validation for LLM structured outputs

**Communication:**
- **REST API:** HTTP endpoints for frontend-backend communication
- **WebSocket:** Real-time bidirectional updates for metrics streaming

---

**Web Platform (FretCoach Hub):**

**Frontend:**
- **React 18:** UI framework
- **TypeScript:** Type-safe JavaScript superset
- **Vite:** Build tool and dev server
- **Tailwind CSS:** Utility-first styling
- **shadcn/ui:** Pre-built accessible component library (built on Radix UI)
- **Radix UI:** Headless UI primitives for accessibility
- **Recharts:** Composable charting library for analytics visualization
- **TanStack React Query:** Server state management and caching
- **React Router v6:** Client-side routing

**Backend:**
- **Python FastAPI:** API server
- **LangChain + LangGraph:** AI agent orchestration
- **Google Gemini 3 Flash Preview:** Conversational AI coach with text-to-SQL capabilities
- **SQLAlchemy:** Database ORM for PostgreSQL
- **Pydantic:** Data validation and serialization

**Deployment:**
- **Vercel:** Frontend hosting with CDN and edge caching
- **Railway:** Backend hosting with auto-scaling and database integration

---

**Shared Infrastructure:**

**Database:**
- **PostgreSQL:** Relational database for session data
- **Supabase:** Managed PostgreSQL hosting with real-time subscriptions and auth

**LLM Providers:**
- **OpenAI:** GPT-4o-mini (Studio coaching, practice plans)
- **Google Gemini 3 Flash Preview:** Conversational coach (Hub)
- **GPT-4o-mini-TTS:** Voice synthesis (Studio live coaching)

**AI Orchestration:**
- **LangChain:** Framework for LLM-powered applications
- **LangGraph:** Stateful agent workflows with tool calling
- **Comet Opik:** LLM observability, tracing, evaluation, and optimization

**Smart Bulb Integration:**
- **Tuya Cloud API:** IoT platform for smart home devices
- **tinytuya 1.17.4:** Python library for Tuya device control

---

**Development Tools:**
- **Git:** Version control
- **GitHub:** Repository hosting
- **ESLint + Prettier:** Code linting and formatting
- **pytest:** Python testing framework
- **Vitest:** JavaScript/TypeScript testing framework

---

### 12. Does it work offline?

**Partially—depends on which features you use.**

**Fully Offline (Manual Mode):**

✅ **Works without internet:**
- Real-time audio analysis and metric computation
- Visual feedback on-screen (pitch, scale, timing, noise)
- Smart bulb control (if bulb is on local WiFi)
- Session logging to local database cache

**Why it works offline:**
- Audio analysis runs entirely on-device (local DSP processing)
- No cloud API calls for metric computation
- Database writes queued locally if internet unavailable
- Syncs to Supabase when connection restored

**Manual Mode workflow:**
1. Select scale manually (e.g., C Major Pentatonic)
2. Set difficulty parameters (strictness, sensitivity)
3. Practice with real-time feedback
4. Session saved locally, synced later

---

**Requires Internet (AI Mode):**

❌ **Needs internet connection:**
- AI-generated practice plan recommendations (LLM API calls)
- Live voice coaching during sessions (GPT-4o-mini + TTS)
- FretCoach Hub conversational AI coach (Gemini 3 Flash Preview)
- Database sync with Supabase

**Why it needs internet:**
- LLM inference requires cloud API calls (OpenAI, Google)
- Practice plan generation queries your full session history (cloud database)
- Voice synthesis uses OpenAI TTS API

---

**Offline Capabilities Summary:**

| Feature | Studio (Manual) | Studio (AI Mode) | Hub | Portable (Manual) |
|---------|:---------------:|:----------------:|:---:|:-----------------:|
| Real-time Audio Analysis | ✅ Offline | ✅ Offline | ❌ N/A | ✅ Offline |
| Visual Metrics | ✅ Offline | ✅ Offline | ❌ N/A | ✅ Offline |
| Smart Bulb Control | ✅ Offline* | ✅ Offline* | ❌ N/A | ✅ Offline* |
| Session Logging | ✅ Offline** | ✅ Offline** | ❌ Online | ✅ Offline** |
| AI Voice Coaching | ❌ N/A | ❌ Online | ❌ N/A | ❌ Planned |
| Practice Plans | ❌ N/A | ❌ Online | ❌ Online | ❌ Online |
| Session Analytics | ❌ N/A | ❌ N/A | ❌ Online | ❌ N/A |
| AI Chat Coach | ❌ N/A | ❌ N/A | ❌ Online | ❌ N/A |

\* Smart bulb requires local WiFi (bulb and device on same network)
\** Sessions saved locally, synced to cloud when internet available

---

**Offline Workflow Recommendations:**

**For portable practice (no internet):**
1. Use Manual Mode in Studio or Portable
2. Sessions save locally with timestamps
3. Connect to WiFi later—sessions auto-sync to Supabase
4. Review analytics in Hub once synced

**For travel/remote locations:**
- Manual Mode provides core training functionality
- AI features available when you have hotspot or WiFi
- All session data preserved locally until sync

---

### 13. What audio interface do I need?

**Short answer: Focusrite Scarlett Solo is recommended, but you have options.**

---

**Recommended Setup:**

**Focusrite Scarlett Solo (3rd Gen) - ~$100**

✅ **Why it's ideal:**
- Clean preamps with low noise floor (<-128 dBu EIN)
- USB-C connectivity (bus-powered, no external power needed)
- Direct instrument input (high-impedance 1/4" jack for guitar)
- 24-bit/192kHz capability (FretCoach uses 44.1kHz, but headroom is great)
- Widely available, well-supported drivers (Mac/Windows/Linux)
- Compact and portable

**Alternatives in same quality tier:**
- **PreSonus AudioBox USB 96:** Similar features, slightly cheaper
- **Behringer U-Phoria UM2:** Budget option (~$50), acceptable but noisier preamps
- **Audient EVO 4:** Excellent quality, auto-gain feature helpful for beginners

---

**Other Input Options:**

**Built-in Computer Microphone:**
- ✅ **Pros:** Free, no setup required, works immediately
- ❌ **Cons:** Picks up room noise, less accurate pitch detection, distance affects signal quality
- **Recommended for:** Testing FretCoach before committing to hardware purchase
- **Not recommended for:** Serious practice sessions (too much environmental interference)

**USB Audio Interfaces (Consumer-Grade):**
- Entry-level interfaces ($30-60 range like Behringer UCA202)
- ✅ **Pros:** Better than built-in mic, cheap
- ❌ **Cons:** Noisy preamps, USB 2.0 bottlenecks, driver issues
- **Verdict:** Workable but you'll notice the quality difference

**Direct Guitar-to-USB Cables:**
- Cables like iRig or Rocksmith cable
- ✅ **Pros:** Cheap ($20-40), convenient
- ❌ **Cons:** Poor signal quality, high noise floor, latency issues
- **Verdict:** Not recommended—audio interfaces are much better value

**High-End Audio Interfaces ($200-500+):**
- Universal Audio Volt, Apogee Duet, RME Babyface
- ✅ **Pros:** Exceptional audio quality, ultra-low latency, professional-grade preamps
- **Verdict:** Overkill for FretCoach's needs, but if you already own one, perfect

---

**Setup Guide (Scarlett Solo):**

1. **Connect hardware:**
   - Plug Scarlett Solo into computer USB port
   - Connect guitar to "INST" input on front panel (high-Z input)
   - Turn "GAIN" knob to 12 o'clock position (adjust later)

2. **Configure FretCoach:**
   - Set input device to "Scarlett Solo" in settings
   - Adjust gain so signal peaks around -12 to -6 dB (green LED, avoid red clipping)
   - Enable "Direct Monitor" switch if you want to hear yourself through headphones

3. **Test signal:**
   - Play a few notes
   - Check if pitch detection accurately identifies notes
   - Adjust gain if detection is spotty (usually means signal too low)

---

**Do I Really Need an Interface?**

**For casual testing:** Built-in mic is fine.

**For serious practice:** Audio interface is strongly recommended. Here's why:

- **Signal-to-noise ratio:** Interfaces have dedicated preamps with low noise—critical for accurate pitch detection
- **Direct instrument input:** High-impedance input designed for guitars (built-in mics aren't)
- **Latency:** USB interfaces have optimized drivers for low-latency audio streaming
- **Consistency:** Room acoustics don't affect the signal (unlike microphones)

**Bottom line:** Scarlett Solo (~$100) is the best value for quality, reliability, and compatibility with FretCoach.

---

### 14. Can I use it with an electric guitar? Acoustic?

**Yes, both work—with different optimal setups.**

---

**Electric Guitar (Recommended Primary Use Case):**

**Best Setup:**
- **Electric guitar → Audio interface (Scarlett Solo) → FretCoach**

✅ **Why it's ideal:**
- **Clean signal:** Direct instrument input, no environmental noise
- **Accurate pitch detection:** Sustained notes, clear fundamental frequency
- **No room acoustics:** Signal path is entirely electrical
- **Volume control:** Adjust gain without affecting playing dynamics

**Guitar Types Tested:**
- Solid-body electric (Stratocaster, Les Paul style)
- Semi-hollow electric
- 7-string and extended-range guitars (works, requires scale database expansion)

**Pickup Considerations:**
- **Single-coil pickups:** Work great, slight 60Hz hum filterable
- **Humbucker pickups:** Excellent signal, very clean
- **Active pickups:** Perfect signal-to-noise ratio

---

**Acoustic Guitar:**

**Setup Options:**

**Option 1: Microphone (Built-in or External)**
- Acoustic guitar → Mic (air gap) → Audio interface/built-in mic → FretCoach
- ✅ **Pros:** Natural sound, no guitar modification needed
- ❌ **Cons:** Picks up room noise, position-sensitive, environmental interference
- **Best for:** Quiet practice spaces, testing FretCoach before committing

**Option 2: Acoustic-Electric with Pickup/Preamp**
- Acoustic-electric guitar → 1/4" cable → Audio interface → FretCoach
- ✅ **Pros:** Clean signal like electric guitar, no room noise
- ✅ **Best of both worlds:** Acoustic tone with electric guitar signal clarity
- **Recommended:** If you have an acoustic-electric, this is the optimal setup

**Option 3: External Soundhole Pickup**
- Add magnetic soundhole pickup to acoustic → Audio interface → FretCoach
- **Products:** Seymour Duncan SA-3XL, DiMarzio DP168
- ✅ **Pros:** Converts standard acoustic into electric-like signal
- **Cost:** ~$40-80 for pickup

---

**Comparison:**

| Setup | Pitch Accuracy | Noise Immunity | Setup Complexity |
|-------|:--------------:|:--------------:|:----------------:|
| Electric → Interface | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ Easy |
| Acoustic-Electric → Interface | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ Easy |
| Acoustic → External Mic | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ Moderate |
| Acoustic → Built-in Mic | ⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ Easy |

---

**Key Takeaway:**

- **Electric guitar:** Best experience, highly recommended
- **Acoustic-electric:** Equally good as electric
- **Pure acoustic with mic:** Works, but environmental factors matter
- **All guitar types supported:** 6-string, 12-string, bass, extended range (with scale adjustments)

---

### 15. Is it open source?

**Yes—fully open source under MIT-style license.**

---

**Main Repository:**
- **GitHub:** [github.com/padmanabhan-r/FretCoach](https://github.com/padmanabhan-r/FretCoach)
- **Contains:** FretCoach Studio (desktop app), FretCoach Portable (Raspberry Pi), reference implementations of Hub components
- **License:** Open source (check LICENSE file in repo)

**Production Web Repositories (Separate for Deployment):**
- **Backend:** [github.com/padmanabhan-r/FretCoach-Web-Backend](https://github.com/padmanabhan-r/FretCoach-Web-Backend)
- **Frontend:** [github.com/padmanabhan-r/FretCoach-Web-Frontend](https://github.com/padmanabhan-r/FretCoach-Web-Frontend)
- **Why separate?** Automated deployments to Railway (backend) and Vercel (frontend) via GitHub Actions

---

**What "Open Source" Means for FretCoach:**

✅ **You can:**
- Clone the repository and run FretCoach locally
- Modify the code for personal use
- Fork the project and create derivative works
- Contribute bug fixes and features via pull requests
- Study the audio analysis algorithms and AI orchestration code
- Deploy your own instance of FretCoach Hub

❌ **You cannot:**
- Use the FretCoach name/branding for commercial products without permission
- Claim the original work as your own

---

**Contributing:**

**We welcome contributions in these areas:**

**Code Contributions:**
- Bug fixes
- Performance optimizations
- Cross-platform compatibility improvements (especially Linux/Windows testing)
- New features (with prior discussion via GitHub Issues)

**Non-Code Contributions:**
- Documentation improvements
- Tutorial videos
- Testing on different hardware setups
- Translation/localization
- UI/UX design suggestions

**How to Contribute:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make changes with clear commit messages
4. Test thoroughly (include test cases if applicable)
5. Submit pull request with description of changes

**Contribution Guidelines:**
- Follow existing code style (Python: PEP 8, JavaScript: Prettier/ESLint)
- Write clear commit messages
- Document new features in README or docs
- Test on your platform before submitting PR

---

**Community & Support:**

- **GitHub Issues:** Bug reports and feature requests
- **GitHub Discussions:** Questions, ideas, showcases
- **Pull Requests:** Code contributions

**Philosophy:** FretCoach is built in the open to enable collaboration, transparency, and community-driven improvements. Open source accelerates innovation—especially for domain-specific tools like music education.

---

### 16. Does it support other instruments besides guitar?

**Not yet—but the architecture is designed for multi-instrument expansion.**

---

**Current Status:**

✅ **Fully Supported:**
- 6-string guitar (electric and acoustic)
- Standard tuning (E-A-D-G-B-E)
- Alternate tunings (Drop D, DADGAD, Open G, etc.)
- Extended-range guitars (7-string, 8-string with manual scale config)

⚠️ **Partial Support:**
- Bass guitar (works, but metrics calibrated for guitar frequency range)
- 12-string guitar (works, octave doubling can confuse pitch detection slightly)

❌ **Not Yet Supported:**
- Piano/keyboard
- Vocals
- Drums
- Woodwinds/brass
- Other string instruments (violin, cello, etc.)

---

**Why Multi-Instrument Support is Feasible:**

**The audio analysis engine is fundamentally instrument-agnostic:**

1. **Pitch Detection:** FFT-based analysis works for any tonal instrument
2. **Timing Analysis:** Inter-onset interval detection works for rhythm instruments
3. **Metric Framework:** The 4-metric system (pitch, scale, timing, noise) generalizes

**What needs adaptation:**

| Instrument | Required Changes |
|------------|------------------|
| **Bass Guitar** | Frequency range adjustment (E1 = 41 Hz vs guitar E2 = 82 Hz), timing emphasis over pitch |
| **Piano** | Polyphonic note detection (multiple simultaneous notes), wider frequency range (A0-C8) |
| **Vocals** | Vibrato tolerance, breath detection, lyric phoneme timing |
| **Drums** | Percussion onset detection (no pitch), rhythm pattern recognition, dynamics tracking |

---

**Roadmap for Multi-Instrument Support:**

**Phase 1: Bass Guitar (Next Release)**
- Low-frequency pitch detection optimization
- Groove-focused timing metrics
- Bassline-specific scale patterns (e.g., walking bass, pentatonic bass lines)

**Phase 2: Piano/Keyboard (6-12 Months)**
- Polyphonic pitch detection (chord recognition)
- Hand independence metrics (left vs. right hand evaluation)
- Chord progression accuracy
- Pedaling feedback (sustain, dampening)

**Phase 3: Vocals (12-18 Months)**
- Singing pitch accuracy vs. target melody
- Vibrato consistency analysis
- Breath control metrics (duration, phrasing)
- Range training with visual guides

**Phase 4: Drums (Future)**
- Microphone array or MIDI input support
- Rhythm pattern recognition (kick, snare, hi-hat independence)
- Timing consistency across different drum voices
- Dynamics (velocity) tracking

---

**How You Can Help:**

If you're interested in multi-instrument support:
- **Musicians:** Share practice challenges specific to your instrument
- **Developers:** Contribute pitch detection algorithms optimized for different frequency ranges
- **Researchers:** Share papers on instrument-specific audio analysis techniques

Open a GitHub Issue with tag `[Feature] Multi-Instrument` to discuss specific instrument support needs.

---

### 17. How accurate is the pitch detection?

**Very accurate for clean signals—comparable to professional tuners.**

---

**Technical Specifications:**

| Metric | Value | Context |
|--------|-------|---------|
| **Accuracy** | ±10 cents | Human pitch perception threshold is ~5-10 cents; FretCoach operates at perceptual limit |
| **Frequency Range** | 80 Hz - 1200 Hz | Covers guitar range from low E (82 Hz) to high E (1318 Hz) with margin |
| **Latency** | <300ms | Time from sound input to detection result |
| **Confidence Threshold** | >0.5 | Probabilistic detection—only reports pitches above 50% confidence |
| **Polyphonic Handling** | Limited | Best for single-note playing; chords can confuse detection |

---

**Algorithm: Probabilistic YIN (librosa.pyin)**

**Why this algorithm?**

- **YIN family:** Industry standard for monophonic pitch tracking (used in Audacity, Sonic Visualizer)
- **Probabilistic enhancement:** Handles noisy signals better than naive autocorrelation
- **Guitar-optimized:** Works well with harmonic-rich signals (guitar has strong overtones)

**How it works:**
1. **Autocorrelation:** Finds repeating patterns in the audio signal (fundamental frequency)
2. **Frequency estimation:** Converts lag time to frequency (f = sample_rate / lag)
3. **Confidence scoring:** Assigns probability to detected pitch (filters spurious detections)
4. **Temporal smoothing:** Tracks pitch over time to reduce jitter

---

**Factors Affecting Accuracy:**

**✅ Clean Signal = High Accuracy:**
- Electric guitar through audio interface
- Minimal string buzz or fret noise
- Single-note playing (no chords)
- Moderate sustain (not too short/staccato)

**⚠️ Challenging Scenarios:**
- **Polyphonic input (chords):** Detection confused by multiple fundamentals
- **Very low notes:** Sub-100 Hz can be ambiguous (bass guitar challenging)
- **Fast tremolo picking:** Note onsets too close together for reliable tracking
- **Noisy environment:** Background noise degrades signal-to-noise ratio

---

**Comparison to Other Tools:**

| Tool | Accuracy | Latency | Use Case |
|------|----------|---------|----------|
| **FretCoach** | ±10 cents | <300ms | Real-time practice feedback |
| **Boss TU-3 Tuner** | ±1 cent | <50ms | One-time tuning (not continuous) |
| **Auto-Tune (Studio)** | ±1 cent | N/A | Post-processing (not real-time) |
| **Guitar Hero** | Rhythm only | N/A | Note detection, not pitch accuracy |

**Key difference:** FretCoach prioritizes **real-time continuous tracking** over one-time precision. Tuners detect single static pitches; FretCoach tracks dynamic playing.

---

**Improving Detection Accuracy:**

**Hardware:**
1. Use audio interface (Scarlett Solo) instead of built-in mic
2. Eliminate string buzz (proper setup, fresh strings)
3. Adjust gain for optimal signal level (-12 to -6 dB)

**Playing Technique:**
1. Play cleanly (mute unused strings)
2. Let notes sustain (don't cut off too quickly)
3. Avoid heavy distortion/effects (clean tone best)

**Software Settings:**
1. Increase confidence threshold if getting false positives
2. Adjust frequency range if using extended-range guitars
3. Use noise gate to filter background noise

---

**Bottom Line:**

For clean electric guitar signals through an audio interface, FretCoach's pitch detection is **on par with professional software tuners**. The ±10 cent tolerance is at the threshold of human pitch perception—if you're within this range, your intonation is excellent.

---

### 18. Can I customize the metrics or feedback?

**Yes, partially—with more customization options coming in future updates.**

---

**Current Customization Options:**

**1. User Preference Weights (Database Config):**

The `user_configs` table in the database stores your metric priorities:

| Field | Range | Default | What It Controls |
|-------|-------|---------|------------------|
| `pitch_accuracy_weight` | 0.0 - 1.0 | 0.4 | Importance of pitch in overall score |
| `scale_conformity_weight` | 0.0 - 1.0 | 0.3 | Importance of playing correct scale notes |
| `timing_stability_weight` | 0.0 - 1.0 | 0.3 | Importance of rhythmic consistency |

**How it works:**
- Total performance score is weighted average: `Score = (pitch * 0.4) + (scale * 0.3) + (timing * 0.3)`
- You can adjust weights to emphasize specific areas (e.g., increase timing weight for rhythm-focused practice)
- Changes affect ambient lighting color and AI coach recommendations

**How to modify:**
- Currently: Direct database edit via SQL
- Planned: UI settings panel in Studio for easy weight adjustment

---

**2. AI Coach Behavior (Adaptive):**

The AI coach automatically adapts based on your playing history:

**Automatic Adjustments:**
- Identifies your weakest metric from session data
- Generates practice plans targeting weak areas
- Adjusts coaching tone based on progress trends (encouraging vs. corrective)

**Customization:**
- Future: Coaching style preferences (strict vs. encouraging, technical vs. motivational)
- Future: Focus mode (ignore certain metrics for specialized practice)

---

**3. Ambient Lighting Thresholds (Code-Level):**

Current thresholds are hardcoded but modifiable:

```python
# Current mapping (in lighting control module):
if score >= 70:
    color = GREEN
elif score >= 50:
    color = YELLOW
elif score >= 30:
    color = ORANGE
else:
    color = RED
```

**How to customize:**
1. Edit `lighting_control.py` (or equivalent in your codebase)
2. Adjust threshold values (e.g., stricter: 80/60/40 instead of 70/50/30)
3. Change colors (e.g., blue instead of green for excellent)

**Planned:** UI-based threshold adjustment in settings

---

**4. Scale Library (Expandable):**

FretCoach currently supports common scales:
- Major, Minor, Pentatonic, Blues, Dorian, etc.

**How to add custom scales:**
1. Edit `scale_definitions.json` (or database table)
2. Define scale intervals (e.g., Major = [0, 2, 4, 5, 7, 9, 11] semitones from root)
3. Add scale to UI dropdown

**Planned:** In-app scale editor for custom scale creation

---

**5. Audio Processing Parameters (Advanced):**

For advanced users, you can tweak DSP parameters:

| Parameter | File/Location | What It Affects |
|-----------|---------------|-----------------|
| Buffer Size | `audio_config.py` | Latency vs. stability tradeoff |
| Confidence Threshold | `pitch_detection.py` | Sensitivity of pitch detection |
| FFT Window Size | `audio_processing.py` | Frequency resolution |
| Noise Gate Threshold | `noise_filter.py` | Background noise filtering |

**Warning:** Changing these requires understanding of audio processing—incorrect values can break functionality.

---

**Planned Customization Features (Future Releases):**

**UI Settings Panel:**
- Metric weight sliders (visual weight adjustment)
- Lighting threshold configuration
- Coaching style preferences (technical/motivational/strict/encouraging)
- Display preferences (metric colors, font sizes, layout)

**Practice Mode Customization:**
- Focus mode (disable specific metrics for specialized practice)
- Metronome integration with configurable subdivisions
- Custom difficulty presets (beginner/intermediate/advanced profiles)

**Advanced:**
- Plugin system for custom metric algorithms
- API for third-party integrations
- Export settings/config files for sharing

---

**How to Request Features:**

Open a GitHub Issue with tag `[Feature] Customization` describing:
- What you want to customize
- Your use case (why this customization matters)
- Proposed UI/workflow for the feature

Community-driven feature requests help prioritize development.

---

### 19. Does it work on Windows? Mac? Linux?

**Cross-platform support with varying levels of testing.**

---

**macOS (Primary Development Platform):**

✅ **Fully Supported and Tested:**

- **Versions:** macOS 11 Big Sur and later
- **Architecture:** Intel (x86_64) and Apple Silicon (ARM64/M1/M2/M3)
- **Status:** Primary development and testing platform—most stable

**Installation:**
- All dependencies available via Homebrew or pip
- Audio drivers work out-of-box (Core Audio)
- Electron app builds natively for both architectures

**Tested Hardware:**
- MacBook Pro (M1, M2)
- MacBook Air (M1)
- Mac Mini (Intel)

---

**Windows (Tested, Supported):**

✅ **Supported with Known Issues:**

- **Versions:** Windows 10 (1909+) and Windows 11
- **Architecture:** x64 (64-bit Intel/AMD)
- **Status:** Tested and working, but fewer test cycles than macOS

**Known Issues:**
- **Audio driver setup:** Requires ASIO4ALL or manufacturer-specific ASIO drivers for low-latency audio
- **Path handling:** Some file path issues in earlier versions (fixed in recent commits)
- **Python environment:** Recommend using `venv` or Conda for clean Python setup

**Installation Notes:**
1. Install Python 3.12+ from python.org (not Windows Store version)
2. Install Node.js LTS from nodejs.org
3. Install audio interface drivers (e.g., Focusrite Scarlett Solo drivers for Windows)
4. Follow [Environment Setup](environment-setup.md) for detailed steps

**Tested Hardware:**
- Desktop PCs with dedicated audio interfaces
- Laptops with built-in audio (works, but not recommended)

---

**Linux (Should Work, Limited Testing):**

⚠️ **Experimental Support:**

- **Distributions:** Ubuntu 20.04+, Debian 11+, Fedora 35+ (others likely work)
- **Architecture:** x86_64
- **Status:** Not extensively tested—community feedback needed

**Expected to Work:**
- Audio processing (librosa, NumPy, sounddevice all have Linux builds)
- Electron desktop app (cross-platform framework)
- Database connectivity (PostgreSQL client libraries available)

**Potential Issues:**
- **Audio backend:** May need ALSA/PulseAudio/JACK configuration
- **Smart bulb control:** Tuya library should work, but untested
- **Package dependencies:** Some Python packages may need compilation from source

**Linux Installation Tips:**
1. Install system dependencies: `sudo apt install python3-dev portaudio19-dev`
2. Use virtual environment: `python3 -m venv venv`
3. Install audio libraries: `pip install librosa sounddevice numpy scipy`
4. Test audio input with `arecord -l` to verify device detection

**Community Help Needed:**
- If you get FretCoach running on Linux, please share your setup steps via GitHub Issue
- Contributions for Linux-specific documentation welcome

---

**Raspberry Pi OS (FretCoach Portable):**

✅ **Fully Supported (ARM Architecture):**

- **Platform:** Raspberry Pi 5 with Raspberry Pi OS (Debian-based)
- **Architecture:** ARM64
- **Status:** Tested and working—FretCoach Portable runs on this platform

**Installation:**
- Follow [Portable App documentation](portable-app.md)
- Uses same codebase as Desktop app (cross-platform Python)

---

**Platform Feature Matrix:**

| Platform | Desktop App | Web Hub | Portable | Smart Bulb | Testing Status |
|----------|:-----------:|:-------:|:--------:|:----------:|:--------------:|
| **macOS** | ✅ | ✅ | N/A | ✅ | ⭐⭐⭐⭐⭐ Extensive |
| **Windows** | ✅ | ✅ | N/A | ✅ | ⭐⭐⭐⭐ Good |
| **Linux** | ⚠️ | ✅ | N/A | ⚠️ | ⭐⭐ Limited |
| **Raspberry Pi OS** | N/A | ✅ | ✅ | ✅ | ⭐⭐⭐⭐ Good |

✅ = Supported | ⚠️ = Should work, needs testing | N/A = Not applicable

---

**Web Hub (Browser-Based):**

✅ **Works on All Platforms:**

FretCoach Hub is browser-based, so it works on any OS with a modern browser:
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

**Accessible via:** [fretcoach.online](https://www.fretcoach.online)

---

**Help Us Test:**

If you're using Windows or Linux:
- Report any issues via GitHub
- Share successful setup configurations
- Contribute platform-specific documentation improvements

---

### 20. How much does it cost?

**Free and open source—zero subscription fees, no paywalls.**

---

**Software Costs:**

| Component | Cost |
|-----------|:----:|
| FretCoach Studio (Desktop App) | **FREE** |
| FretCoach Hub (Web Dashboard) | **FREE** |
| FretCoach Portable (Software) | **FREE** |
| Source Code Access | **FREE** |

**License:** Open source (MIT-style)—free to use, modify, and distribute.

---

**Hardware Costs (Optional):**

**Minimal Setup (Desktop Only):**

| Item | Cost | Notes |
|------|------|-------|
| **Audio Interface** | ~$100 | Focusrite Scarlett Solo (recommended) |
| **Guitar Cable** | ~$15 | 1/4" instrument cable |
| **Computer** | $0 | Use existing Mac/PC |
| **TOTAL** | **~$115** | One-time purchase |

**Optional Add-Ons:**

| Item | Cost | Purpose |
|------|------|---------|
| **Smart Bulb (Tuya)** | ~$10-20 | Ambient lighting feedback |
| **Better Audio Interface** | $150-300 | Universal Audio Volt, Apogee Duet (optional upgrade) |

---

**Portable Setup (Raspberry Pi):**

| Item | Cost | Notes |
|------|------|-------|
| **Raspberry Pi 5 (8GB)** | ~$80 | Core compute unit |
| **Focusrite Scarlett Solo** | ~$100 | USB audio interface |
| **microSD Card (64GB)** | ~$15 | Storage for OS and data |
| **Power Supply (USB-C)** | ~$10 | Official Raspberry Pi power supply |
| **Case + Cooling** | ~$15 | Optional but recommended |
| **Guitar Cable** | ~$15 | 1/4" instrument cable |
| **TOTAL** | **~$235** | One-time purchase |

**Future Pedal Version:** TBD (enclosure, LCD, footswitch will add cost)

---

**Cloud/API Costs (Covered by You via API Keys):**

**AI Features (Optional):**

If you use AI-powered features (practice plan generation, voice coaching), you'll need API keys:

| Service | Feature | Cost | Free Tier |
|---------|---------|------|-----------|
| **OpenAI API** | GPT-4o-mini (practice plans, voice coaching) | ~$0.15 per 1M input tokens, $0.60 per 1M output tokens | $5 free credit for new accounts |
| **Google Gemini API** | Gemini 3 Flash Preview (Hub AI coach) | Free tier: 1500 requests/day | Generous free tier |
| **Supabase** | Database hosting | Free tier: 500MB storage, unlimited API requests | Free forever plan available |

**Estimated Monthly Costs (AI Features):**
- **Light usage** (10-20 practice sessions/month with AI): <$1/month
- **Moderate usage** (daily practice with AI coach): ~$2-5/month
- **Heavy usage** (multiple users, extensive AI coaching): ~$10-20/month

**Free Tier is Usually Enough:** Most users stay within free tiers for Gemini and OpenAI (especially with GPT-4o-mini's low pricing).

---

**Manual Mode (Zero Ongoing Costs):**

You can use FretCoach entirely offline in **Manual Mode**:
- No AI features (no API calls)
- No cloud database (local session storage)
- Real-time audio analysis still works perfectly
- Smart bulb control (local WiFi only)

**Cost:** $0/month after initial hardware purchase.

---

**Comparison to Alternatives:**

| Product | Type | Cost |
|---------|------|------|
| **Fender Play** | Video lessons subscription | $10-20/month ongoing |
| **Yousician** | Gamified practice app | $10-30/month ongoing |
| **JustinGuitar** | Free lessons + optional courses | Free (donations encouraged) |
| **Private Guitar Teacher** | In-person coaching | $30-60/hour |
| **FretCoach** | Real-time AI practice coach | **$0/month (FREE)** + optional $115 hardware |

---

**Total Cost of Ownership (1 Year):**

**Scenario 1: Desktop Only (Minimal Setup)**
- Hardware: $115 (one-time)
- Software: $0
- API costs: <$60/year (assuming AI usage)
- **Total:** ~$175/year

**Scenario 2: Manual Mode (Zero Ongoing Costs)**
- Hardware: $115 (one-time)
- Software: $0
- API costs: $0 (no AI features)
- **Total:** $115 one-time, then **$0/year**

**Scenario 3: Private Lessons (Comparison)**
- Weekly 1-hour lessons: $30/hour × 52 weeks = **$1,560/year**

---

**Bottom Line:**

FretCoach is **free software** with optional hardware costs (~$115 for audio interface). No subscriptions, no paywalls, no hidden fees. AI features cost pennies per session if you use them, or you can use Manual Mode for free forever.

---

### 21. Can I use it with my existing practice routine?

**Absolutely—FretCoach is designed to complement, not replace, traditional practice.**

---

**How FretCoach Fits Into a Balanced Practice Routine:**

**Typical Practice Session Structure:**

**1. Warm-Up & Technique (20-30 min) — Use FretCoach**
- Scale drills with real-time feedback
- Focus on weak areas identified by AI coach
- Practice recommendations from previous session
- **Why FretCoach here:** Builds motor patterns with instant feedback

**2. Creative Playing (20-30 min) — No FretCoach**
- Play songs you enjoy
- Improvise over backing tracks
- Work on musical expression and phrasing
- **Why no FretCoach:** Creativity thrives without metric evaluation

**3. Learning New Material (15-20 min) — Optional FretCoach**
- Learn new scales or chord progressions
- Slow practice with metronome
- Use FretCoach for initial accuracy check
- **Why optional:** Once you've got the pattern, turn it off and play musically

**4. Performance Practice (10-15 min) — No FretCoach**
- Play through songs start to finish
- Simulate performance conditions
- Focus on flow and musicality
- **Why no FretCoach:** Performing requires getting comfortable with imperfection

---

**FretCoach as a Technique Trainer, Not a Judge:**

**What FretCoach is FOR:**
- Building foundational technique (scales, arpeggios, timing drills)
- Identifying weak areas you might not notice
- Providing consistent feedback when practicing alone
- Reinforcing correct motor patterns through repetition

**What FretCoach is NOT FOR:**
- Evaluating your creative playing or improvisation
- Judging your musical expression or feel
- Replacing the joy of playing songs
- Criticizing your artistic choices

---

**Integration Examples:**

**Example 1: Beginner (6 months experience)**

**Monday/Wednesday/Friday:**
- 15 min: FretCoach scale drills (C Major, G Major)
- 15 min: Learn a new song (tabs, no FretCoach)
- 10 min: Play along with favorite songs

**Tuesday/Thursday:**
- 20 min: FretCoach timing exercises
- 10 min: Free improvisation
- 10 min: Chord practice

**FretCoach usage:** ~45 min/week out of 180 min total practice (25% of time)

---

**Example 2: Intermediate (2-3 years experience)**

**Daily Practice (60 min):**
- 20 min: FretCoach advanced scales (modes, arpeggios)
- 15 min: Technique exercises (alternate picking, legato)
- 15 min: Learn new song sections
- 10 min: Improvisation over backing tracks

**FretCoach usage:** 20 min/day (33% of practice time)

---

**Example 3: Advanced (5+ years, preparing for performance)**

**Pre-Gig Routine:**
- 10 min: FretCoach warm-up (check hand sync)
- 20 min: Run through setlist (no metrics)
- 5 min: FretCoach diagnosis if something feels off

**Regular Practice:**
- Use FretCoach for specific technique weaknesses
- Focus on musical development without metrics
- Bring back FretCoach when preparing new technical material

**FretCoach usage:** As needed (~10-15% of practice time)

---

**Complementary Tools:**

FretCoach works alongside:
- **Tab apps (Ultimate Guitar):** Learn songs, then practice technique with FretCoach
- **Backing tracks (YouTube):** Improvise freely, use FretCoach for scale mastery
- **Metronome apps:** FretCoach has timing metrics, but external metronome for rhythm focus
- **Video lessons (JustinGuitar, Fender Play):** Learn concepts, refine execution with FretCoach

---

**When to Use FretCoach:**

✅ **Use it when:**
- Drilling scales or technical exercises
- Working on timing and rhythm consistency
- Diagnosing why something doesn't sound right
- Building muscle memory for new patterns
- Practicing in isolation (no teacher/bandmates for feedback)

❌ **Don't use it when:**
- Playing for fun or stress relief
- Improvising creatively
- Performing songs
- Jamming with others
- Exploring new musical ideas

---

**The Bigger Picture:**

**Practice is not just about perfection—it's about:**
- Developing technique (FretCoach helps)
- Building musicality (FretCoach stays out of the way)
- Finding joy in playing (FretCoach doesn't judge artistic choices)

FretCoach is a **tool for deliberate practice**, not a replacement for musical expression. Use it when you need objective feedback, put it aside when you need creative freedom.

---

### 22. How do I get started?

**Fastest path from zero to practicing with FretCoach:**

---

**Option 1: Explore FretCoach Hub (Fastest—5 Minutes)**

**No installation required—just visit the web app:**

1. **Go to:** [fretcoach.online](https://www.fretcoach.online)
2. **Explore the demo:**
   - Click "Dashboard" to see practice analytics
   - Try the AI Chat Coach (ask: "What's my weakest metric?")
   - View session history and trend charts
3. **Understand the concept:**
   - See how metrics are tracked
   - Learn what the AI coach recommends
   - Decide if you want to install locally

**Result:** 5-minute understanding of what FretCoach offers, zero setup.

---

**Option 2: Install FretCoach Studio (Full Experience—30 Minutes)**

**Prerequisites:**
- Computer (Mac/Windows/Linux)
- Audio interface (recommended: Focusrite Scarlett Solo) OR built-in microphone (testing only)
- Guitar and cable

**Installation Steps:**

**1. Clone the Repository:**
```bash
git clone https://github.com/padmanabhan-r/FretCoach.git
cd FretCoach
```

**2. Set Up Environment:**

Follow detailed instructions in [Environment Setup Guide](environment-setup.md):
- Install Node.js 18+
- Install Python 3.12+
- Create `.env` file with API keys (if using AI features)
- Install dependencies

**Quick version (macOS/Linux):**
```bash
cd application
npm install
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**3. Configure Audio Input:**
- Connect audio interface (or use built-in mic for testing)
- Check device settings in Studio app

**4. Start FretCoach Studio:**
```bash
npm run dev
```

This starts:
- Electron app (desktop UI)
- React frontend (practice interface)
- Python FastAPI backend (audio analysis engine)

**5. First Practice Session:**
- Select "Manual Mode"
- Choose a scale (e.g., C Major)
- Play along with real-time feedback

**Result:** Fully functional local installation in ~30 minutes.

---

**Option 3: Try Manual Mode Only (Minimal Setup—15 Minutes)**

**If you want to skip AI features and database setup:**

1. Clone repository (same as Option 2, Step 1)
2. Install dependencies (same as Option 2, Step 2)
3. **Skip `.env` file creation** (no API keys needed)
4. Start app in Manual Mode only
5. Practice with offline audio analysis

**Result:** Core functionality without cloud dependencies, 15-minute setup.

---

**Quickstart Checklist:**

**Hardware:**
- [ ] Guitar (electric or acoustic)
- [ ] Audio interface (Scarlett Solo recommended) or built-in mic
- [ ] Computer with available USB port
- [ ] Guitar cable (1/4" instrument cable)

**Software:**
- [ ] Node.js 18+ installed
- [ ] Python 3.12+ installed
- [ ] Git installed (for cloning repository)
- [ ] Code editor (optional: VS Code, Cursor)

**Optional (for AI features):**
- [ ] OpenAI API key (for GPT-4o-mini)
- [ ] Google Gemini API key (for conversational AI coach)
- [ ] Supabase account (for cloud database)

---

**Common First-Time Issues:**

**Issue 1: Audio Input Not Detected**
- **Solution:** Check that audio interface drivers are installed (especially Windows)
- **macOS:** Core Audio works out-of-box
- **Windows:** Install ASIO4ALL or manufacturer-specific drivers

**Issue 2: Pitch Detection Not Working**
- **Solution:** Adjust gain on audio interface (signal should peak at -12 to -6 dB)
- Play louder or increase gain knob

**Issue 3: Python Package Errors**
- **Solution:** Use virtual environment (`python3 -m venv venv`)
- Install `librosa` separately if it fails: `pip install librosa==0.10.0`

**Issue 4: npm Install Fails**
- **Solution:** Clear npm cache: `npm cache clean --force`
- Use Node.js LTS version (avoid bleeding-edge versions)

---

**Help & Support:**

**Documentation:**
- [Quickstart Guide](quickstart.md) — Step-by-step installation
- [Environment Setup](environment-setup.md) — Detailed configuration
- [Troubleshooting](troubleshooting.md) — Common issues and solutions

**Community:**
- [GitHub Issues](https://github.com/padmanabhan-r/FretCoach/issues) — Bug reports and questions
- [GitHub Discussions](https://github.com/padmanabhan-r/FretCoach/discussions) — General questions and ideas

---

**Next Steps After Installation:**

1. **Complete first practice session** (Manual Mode)
2. **Review your metrics** in FretCoach Hub
3. **Try AI Mode** (if API keys configured)
4. **Explore ambient lighting** (if smart bulb available)
5. **Read [full documentation](https://padmanabhan-r.github.io/FretCoach/)** for advanced features

**Welcome to FretCoach—happy practicing! 🎸**

---

### 23. I found a bug. How do I report it?

**GitHub Issues is the official channel for bug reports.**

---

**Where to Report:**

**GitHub Repository:**
[github.com/padmanabhan-r/FretCoach/issues](https://github.com/padmanabhan-r/FretCoach/issues)

**Before Creating a New Issue:**
1. **Search existing issues** to avoid duplicates
2. **Check closed issues** (bug might already be fixed in latest version)
3. **Update to latest version** (bug might be resolved)

---

**What to Include in Your Bug Report:**

**Minimum Required Information:**

**1. Environment Details:**
```
- OS: macOS 14.2 / Windows 11 / Ubuntu 22.04
- FretCoach Version: v1.0.0 (or commit hash if running from source)
- Node.js Version: v18.17.0
- Python Version: 3.12.1
- Audio Interface: Focusrite Scarlett Solo (or built-in mic)
```

**2. Steps to Reproduce:**
```
1. Open FretCoach Studio
2. Select Manual Mode
3. Choose C Major scale
4. Start practice session
5. Bug occurs: [describe what happens]
```

**3. Expected Behavior:**
- What you thought should happen

**4. Actual Behavior:**
- What actually happened

**5. Screenshots/Logs (if applicable):**
- Screenshots of error messages
- Console logs (open Developer Tools: Cmd+Shift+I / Ctrl+Shift+I)
- Backend logs (check terminal where `npm run dev` is running)

---

**Example Bug Report (Good):**

**Title:** Pitch detection fails on low E string (electric guitar)

**Description:**
When playing the low E string (82 Hz) on my electric guitar through a Scarlett Solo, the pitch detection doesn't register any notes. Higher strings work fine.

**Environment:**
- macOS 14.2 (M1 MacBook Pro)
- FretCoach v1.0.0
- Node.js v18.17.0
- Python 3.12.1
- Audio Interface: Focusrite Scarlett Solo 3rd Gen

**Steps to Reproduce:**
1. Connect electric guitar to Scarlett Solo
2. Open FretCoach Studio
3. Select Manual Mode → E Minor scale
4. Play low E string (open, 82 Hz)
5. Observe: No pitch detected in UI

**Expected:** Low E detected and displayed

**Actual:** UI shows "No note detected"

**Additional Info:**
- High E string (329 Hz) works perfectly
- Gain level is correct (-10 dB in DAW when testing)
- Same issue in both Manual and AI modes

**Screenshots:** [Attached]

---

**Example Bug Report (Bad—Don't Do This):**

**Title:** It doesn't work

**Description:**
FretCoach isn't working. Please fix.

**What's Wrong:**
- No environment details
- No steps to reproduce
- Vague description
- No context on what "doesn't work" means

---

**Issue Labels (will be added by maintainers):**

| Label | Meaning |
|-------|---------|
| `bug` | Confirmed software defect |
| `enhancement` | Feature request |
| `question` | Help or clarification needed |
| `documentation` | Docs improvement needed |
| `good first issue` | Beginner-friendly contribution opportunity |
| `wontfix` | Issue acknowledged but won't be addressed |
| `duplicate` | Already reported elsewhere |

---

**Response Time:**

- **Acknowledgment:** Usually within 1-3 days
- **Investigation:** Depends on complexity and maintainer availability
- **Fix:** Critical bugs prioritized, enhancements scheduled for future releases

**Open source = community-driven timeline.** Maintainers work on this in their free time, so patience is appreciated.

---

**Security Vulnerabilities:**

**If you find a security issue (e.g., API key exposure, injection vulnerability):**

❌ **Don't:** Open a public GitHub Issue

✅ **Do:** Email privately to maintainer (check README for contact info) or use GitHub's private vulnerability reporting feature

**Why?** Public disclosure of security issues before they're fixed puts users at risk.

---

**Feature Requests (Not Bugs):**

If you want to suggest a new feature:
- Open a GitHub Issue with `[Feature Request]` in the title
- Use label `enhancement`
- Describe the use case (why you need this)
- Propose how it might work (optional)

---

**Contributing a Fix:**

If you're comfortable fixing the bug yourself:
1. Fork the repository
2. Create a branch: `git checkout -b fix/bug-description`
3. Fix the bug and test thoroughly
4. Submit a pull request referencing the issue number

**Maintainers appreciate code contributions!** Fixes with tests and documentation are more likely to be merged quickly.

---

### 24. Can I contribute to the project?

**Yes! Contributions are welcome in many forms—code, docs, testing, and more.**

---

**Why Contribute?**

- **Learn:** Dive into audio processing, AI orchestration, and full-stack development
- **Impact:** Help musicians around the world practice more effectively
- **Community:** Join a community building the future of skill-based learning
- **Portfolio:** Open source contributions look great on resumes and GitHub profiles

---

**Ways to Contribute:**

**1. Code Contributions:**

**Backend (Python):**
- Audio processing optimizations (DSP algorithms)
- New metric implementations (e.g., dynamics, vibrato)
- Database schema improvements
- API endpoint enhancements

**Frontend (React/TypeScript):**
- UI/UX improvements
- New visualizations for metrics
- Settings panels for customization
- Accessibility enhancements

**AI/LLM Integration:**
- LangGraph workflow optimizations
- New AI coach capabilities
- Prompt engineering improvements
- LLM evaluation metrics

**Cross-Platform:**
- Linux testing and compatibility fixes
- Windows-specific bug fixes
- Raspberry Pi optimizations

---

**2. Documentation:**

**Needed:**
- Beginner-friendly tutorials
- Video walkthroughs (installation, first session)
- Troubleshooting guides for common issues
- Translations (non-English documentation)
- Architecture deep-dives for developers

**How to Help:**
- Improve existing docs with clearer explanations
- Add screenshots and diagrams
- Write blog posts about your FretCoach experience
- Create YouTube tutorials

---

**3. Testing & Bug Reports:**

**Valuable Contributions:**
- Test on different platforms (Windows, Linux)
- Test with different audio interfaces
- Test with different guitar types (7-string, bass, acoustic)
- Report bugs with detailed reproduction steps
- Verify fixes in unreleased branches

---

**4. Design & UX:**

**Opportunities:**
- UI mockups for new features
- Iconography and visual design
- User flow improvements
- Accessibility audits (screen readers, keyboard navigation)
- Branding and marketing materials

---

**5. Community Support:**

**Help Others:**
- Answer questions in GitHub Discussions
- Share your setup and configuration tips
- Create "How I Use FretCoach" blog posts
- Share on social media (Twitter, Reddit, YouTube)

---

**Contribution Workflow:**

**Step 1: Find (or Create) an Issue**
- Browse [GitHub Issues](https://github.com/padmanabhan-r/FretCoach/issues)
- Look for `good first issue` label for beginner-friendly tasks
- Comment on the issue to express interest

**Step 2: Fork & Clone**
```bash
# Fork on GitHub (click "Fork" button)
git clone https://github.com/YOUR_USERNAME/FretCoach.git
cd FretCoach
git remote add upstream https://github.com/padmanabhan-r/FretCoach.git
```

**Step 3: Create a Branch**
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

**Step 4: Make Changes**
- Write code following existing style conventions
- Add tests if applicable
- Update documentation if needed
- Commit with clear messages:
  ```bash
  git commit -m "Fix: Pitch detection for low E string"
  git commit -m "Feature: Add vibrato metric"
  git commit -m "Docs: Update environment setup for Windows"
  ```

**Step 5: Push & Create Pull Request**
```bash
git push origin feature/your-feature-name
```
- Go to GitHub and click "Create Pull Request"
- Fill out PR template with description of changes
- Reference related issues: "Fixes #42" or "Relates to #35"

**Step 6: Code Review**
- Maintainers will review your PR
- Address feedback and update code if needed
- Once approved, PR will be merged

---

**Coding Guidelines:**

**Python:**
- Follow PEP 8 style guide
- Use type hints: `def process_audio(buffer: np.ndarray) -> float:`
- Write docstrings for public functions
- Test with pytest: `pytest tests/`

**JavaScript/TypeScript:**
- Use ESLint and Prettier (configs provided)
- Functional components with hooks (no class components)
- TypeScript types for all function signatures
- Test with Vitest (if applicable)

**Git Commits:**
- Conventional commits: `fix:`, `feat:`, `docs:`, `chore:`
- Clear, concise messages
- One logical change per commit

---

**Recognition:**

**Contributors will be:**
- Listed in README.md contributors section
- Credited in release notes
- Thanked in commit messages and PR descriptions

**Top contributors may be invited to:**
- Join maintainer team (if interested)
- Co-author future releases
- Influence roadmap priorities

---

**Questions Before Contributing?**

**Ask in GitHub Discussions:**
- "I want to add [feature]—is this something you'd accept?"
- "I'm new to open source—where should I start?"
- "How can I help with [specific area]?"

**Maintainers are happy to guide newcomers!**

---

**First Contribution Ideas:**

**Easy (Good for Beginners):**
- Fix typos in documentation
- Add screenshots to README
- Improve error messages in UI
- Write a "Getting Started" video tutorial

**Medium:**
- Add new scale definitions (harmonic minor, melodic minor)
- Implement settings panel for metric weights
- Test on Linux and document setup steps

**Advanced:**
- Optimize pitch detection algorithm
- Implement new metric (e.g., vibrato, dynamics)
- Add multi-instrument support (bass guitar)

---

**Thank you for considering contributing to FretCoach!**

Every contribution—no matter how small—helps make guitar practice more effective for musicians worldwide. 🎸

---

**Still have questions?** Open an issue on [GitHub](https://github.com/padmanabhan-r/FretCoach/issues) or explore the [full documentation](https://padmanabhan-r.github.io/FretCoach/).
