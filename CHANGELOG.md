# Changelog

All notable changes to FretCoach will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

## [0.2.0] - 2026-01-XX

### Added
- Initial three-platform ecosystem (Studio, Hub, Portable)
- Real-time audio analysis engine with 4 metrics
- AI-powered practice recommendations
- Smart bulb ambient lighting integration
- Database integration (Supabase PostgreSQL)
- LangGraph agent for AI coach

---

## [0.1.0] - 2025-XX-XX

### Added
- Initial project setup
- Core audio analysis algorithms
- Basic desktop application prototype
