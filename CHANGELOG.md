# Changelog

## [0.3.1] - 2026-02-09

### Documentation
- Enhanced documentation clarity and consistency across all components
- Updated references to MiniMax model for clarity throughout documentation
- Improved desktop application (Studio) documentation with better explanations
- Streamlined FretCoach Portable and Hub documentation with enhanced clarity
- Added comprehensive details on AI services and observability configuration
- Enhanced Real-time Augmented Feedback (RAF) descriptions in README and milestone docs
- Updated environment setup and quickstart guides with additional AI provider information
- Improved scale conformity descriptions to include fretboard coverage details
- Added documentation refinement notes and updated navigation links in appendix
- Updated README with additional FretCoach Portable details and local development instructions

### Improvements
- Refined wording across multiple documentation files for better user experience
- Enhanced clarity in desktop app and observability documentation
- Updated footer and cleaned up documentation formatting

---

## [0.3.0] - 2026-02-08

### Major Features

#### AI Coaching Improvements
- Upgraded LLM from Gemini 2.5 Flash to Gemini 3 Flash Preview
- Optimized live feedback prompt using HRPO (Optimization Studio) → **32% improvement in coaching quality**
- System prompt tightened to "1-2 sentences, max 30 words" for faster real-time responses
- MiniMax fallback model for Gemini rate limit scenarios (~15% of requests)
- Fixed AI coach cold start / serverless timeout issue on web
- Chat session inactivity timeout and dynamic message handling
- User-specific metric toggling (pitch accuracy, scale conformity, timing stability, noise control)
- Improved AI recommendation threading and session tracking

#### Opik Observability Integration (Complete)
- Traces with structured metadata and tags across all 3 AI features
- Thread management with naming conventions per feature
- LangGraph agent graph visualization with `xray=True`
- Annotation queues for human-in-the-loop evaluation
- Datasets and prompts for reproducible experiments
- Experiments with default and custom metrics
- Optimization Studio (HRPO) for prompt improvement
- OpikAssist for token usage analysis and optimization
- Custom feedback definitions and AI providers (Perplexity Sonar Pro, OpenRouter)
- **11 online evaluation rules** (7 Hub Coach + 4 Studio AI Mode)
- Production dashboard with 7 real-time AI quality metrics
- Slack alerts for trace errors, feedback score degradation, and latency spikes
- Key production insights surfaced and acted on

#### Platform Updates

**FretCoach Hub (Web)**
- Renamed from FretCoach Dashboard to FretCoach Hub
- UserSwitcher component for multi-user demo
- Markdown table support in AI chat responses
- Fixed chat timeout on web

**FretCoach Studio (Desktop)**
- Studio branding refresh
- User-specific metric preference configuration

**FretCoach Portable (Raspberry Pi)**
- Startup script (`./start.sh`)
- Improved audio configuration
- Enhanced debug logging

#### Developer Experience
- Added `.env.example` for easier setup
- `GEMINI_MODEL` environment variable for model flexibility
- Deployment repos linked (Vercel frontend, Railway backend)

#### Documentation
- Full README overhaul with RAF (Real-time Augmented Feedback) concept
- Future Expandability section
- Comprehensive Opik usage documentation (opik-usage.md + PDF)
- Online evaluation rules documentation
- Environment setup, FAQ, and troubleshooting guides
- GitHub Pages docs site

### Platform Status
- **FretCoach Studio (Desktop)**: Complete ✅
- **FretCoach Hub (Web)**: Complete ✅
- **FretCoach Portable (Raspberry Pi)**: Complete ✅

---

## [0.2.0] - 2026-01-25

**Codename:** "Dual Brain"

> **Preventive AI coaching for guitar practice - now with full observability**

This milestone marks the completion of FretCoach's **dual-brain architecture** with comprehensive **Comet Opik integration** for full AI observability. We built three interconnected components that work together seamlessly to provide real-time guitar coaching with measurable, data-driven improvements.

### Platform Completion Status
- **FretCoach Studio (Desktop)**: 60% Complete
- **FretCoach Hub (Web)**: 90% Complete
- **FretCoach Portable (Raspberry Pi)**: 30% Complete
- **Opik Integration**: 100% Complete
- **Documentation**: 100% Complete

### Major Features

#### FretCoach Studio (Desktop Application)

**Real-Time Audio Analysis Engine**
- <300ms latency audio processing using librosa and NumPy
- 4-metric evaluation system:
  - Pitch Accuracy (intonation and note correctness)
  - Scale Conformity (note coverage and evenness)
  - Timing Stability (rhythmic consistency)
  - Noise Control (signal clarity)
- Support for USB audio interfaces (Focusrite Scarlett Solo tested) and built-in microphones

**AI-Powered Coaching**
- **AI Practice Mode**: Personalized practice recommendations based on session history
- **Live Vocal Coaching**: Real-time spoken feedback using GPT-4o-mini + TTS
- **Practice Plan Generator**: LLM analyzes weakest areas and suggests targeted exercises
- Multi-LLM support: GPT-4o-mini, Gemini 2.5 Flash, Deepseek, Minimax

**Multi-Sensory Feedback**
- Visual metrics with color-coded performance indicators
- Vocal coaching with natural speech synthesis
- Smart bulb ambient lighting (Tuya WiFi integration)
- Real-time WebSocket updates at 6.67 Hz

**Session Management**
- Automatic session logging to PostgreSQL/Supabase
- Manual Mode: User-selected scales and difficulty
- AI Mode: Adaptive recommendations based on history
- Post-session summaries with performance analysis

#### FretCoach Hub (Web Platform)

**Performance Analytics Dashboard**
- Interactive charts (Recharts) showing metric trends over time
- Session history table with filtering and sorting
- Summary statistics across all practice sessions
- Scale distribution and performance breakdown

**AI Chat Coach**
- Hybrid text-to-SQL agent using LangGraph
- Natural language queries: "What should I practice next?"
- Intent-based tool selection for robust query handling
- Conversational coaching with practice recommendations

**Practice Plan Management**
- Generate AI-powered practice plans from web interface
- Save plans for use in desktop/portable apps
- Track plan status (pending, in-progress, completed)
- Plan history and recommendations archive

**Deployment**
- Frontend: Vercel with global CDN
- Backend: Railway with auto-deploy
- Database: Supabase (PostgreSQL) with connection pooling
- Live at: [fretcoach.online](https://fretcoach.online)

#### FretCoach Portable (Raspberry Pi Device)

**Hardware Setup**
- Raspberry Pi 5 (8GB RAM)
- Focusrite Scarlett Solo USB audio interface
- Same audio analysis engine as desktop (ARM64 optimized)
- Performance: 280-320ms latency (comparable to desktop)

**Features**
- Full audio analysis engine ported to ARM64
- Database synchronization with cloud
- Offline capability (Manual Mode works without internet)
- Smart bulb integration for ambient feedback

### Comet Opik Integration - Full Observability

All AI interactions are fully traced through Comet Opik with comprehensive metadata and tagging.

**What We Trace:**

**1. AI Practice Recommendations** (`ai-mode` tag)
- Function: `generate_ai_recommendation()`
- Inputs: Recent session data (last 5 sessions), performance metrics
- Outputs: Structured Pydantic models (scale, focus area, reasoning, difficulty)
- Metadata: `user_id`, `practice_id`
- Thread grouping: All recommendations per user

**2. Live Session Coaching** (`live-coach` tag)
- Function: `generate_coaching_feedback()`
- Inputs: Real-time metrics (pitch, scale, timing, noise)
- Outputs: Corrective feedback text (1-2 sentences)
- Frequency: Every 30 seconds during practice
- Metadata: `session_id`, timestamp

**3. Text-to-Speech Generation** (`tts` tag)
- Function: `generate_and_play_tts()`
- Separate trace from LLM (independent failure tracking)
- Model: gpt-4o-mini-tts with voice "onyx"
- Latency monitoring: 2-3s typical
- Prevents audio overlap with singleton player

**4. Web Chat Agent** (`web-chat` tag)
- LangGraph agent with multiple tool calls
- Intent detection → Database queries → LLM response
- Full reasoning chain visible in traces
- Multi-turn conversation tracking via thread IDs

**Trace Organization:**
- **Tags**: `ai-mode`, `live-coach`, `web-chat`, `tts`, `practice-plan`
- **Metadata**: `user_id`, `session_id`, `practice_id`, `thread_id`
- **Thread Hierarchy**: Session threads, user threads, chat threads

**Insights Gained from Opik:**
- ✅ Prompt Optimization: Reduced coaching prompt → 50% faster responses
- ✅ TTS Latency Bottleneck: Fixed audio overlap with singleton player
- ✅ Fallback Model Usage: Gemini rate limits ~15% → MiniMax fallback working
- ✅ Token Usage Patterns: Optimized for cost (AI Mode 300-400 tokens, Live Coach 100-150 tokens)

### Documentation

**New Documentation (14 Files):**

**Getting Started**
- `index.md` - Main landing page and navigation
- `introduction.md` - Philosophy and system overview
- `quickstart.md` - 5-minute setup guide
- `judges-start-here.md` - Demo guide for hackathon reviewers

**System Components**
- `desktop-app.md` - Studio application deep dive
- `portable-app.md` - Raspberry Pi device documentation
- `web-dashboard.md` - Web analytics platform guide

**Technical Architecture**
- `architecture.md` - System design and components
- `audio-analysis-agent-engine.md` - Fast Loop (real-time audio processing)
- `ai-coach-agent-engine.md` - Slow Loop (LLM coaching)
- `appendix-audio-math.md` - DSP mathematics and algorithms

**Configuration & Observability**
- `environment-setup.md` - Complete configuration guide
- `opik-observability.md` - Opik integration details
- `README.md` - Documentation structure and publishing

**GitHub Pages**
- Custom orange-themed documentation site
- Assets organized in `docs/assets/` (CSS + images)

### Technical Stack

**Desktop Application:**
- Desktop Runtime: Electron 28
- Frontend: React 18, Vite, Tailwind CSS
- Backend: Python 3.12+, FastAPI 0.109+
- Audio Processing: librosa, NumPy, SciPy, sounddevice
- Communication: REST API, WebSocket

**Web Platform:**
- Frontend: React 18, TypeScript, Vite, Tailwind CSS
- UI Components: shadcn/ui, Radix UI, Recharts
- State Management: TanStack React Query, React Router v6
- Backend: Python FastAPI, LangChain, LangGraph
- Deployment: Vercel (frontend), Railway (backend)

**Shared Infrastructure:**
- Database: PostgreSQL (Supabase)
- LLM Providers: OpenAI (GPT-4o-mini, TTS), Google Gemini 2.5 Flash
- AI Orchestration: LangChain, LangGraph
- Observability: Comet Opik
- Smart Bulb: Tuya Cloud API (tinytuya 1.17.4)

### Known Issues
- Desktop app UI polish needed (60% complete)
- Raspberry Pi software integration in progress (30% complete)
- Some edge cases in audio analysis need refinement
- Performance optimization ongoing based on Opik traces