# FretCoach System Architecture

Technical overview of FretCoach's architecture and implementation.

---

## System Overview

FretCoach is a guitar practice feedback system with three components sharing a central PostgreSQL database:

1. **FretCoach Studio** - Electron desktop app for practice sessions with real-time audio analysis
2. **FretCoach Hub** - Web dashboard for analytics and AI chat coaching
3. **FretCoach Portable** - Raspberry Pi device (in development)

**Database:** PostgreSQL (Supabase) for session storage and cross-device sync

---

## Core Architecture

### Two-Loop System

**Fast Loop (Deterministic):**
- Real-time audio analysis (<300ms latency)
- Pitch detection, scale conformity, timing analysis
- Visual feedback and ambient lighting control
- No LLM calls - predictable, offline-capable

**Slow Loop (LLM-Powered):**
- Practice recommendations based on session history
- Live coaching feedback during sessions
- Conversational AI chat on web dashboard
- All LLM calls traced via Opik

---

## Technology Stack

### Desktop Application (Studio)

| Component | Technology |
|-----------|------------|
| Frontend | React 18, Vite, JavaScript, Tailwind CSS |
| Desktop Runtime | Electron 27 |
| Backend | Python 3.10+, FastAPI |
| Audio Processing | NumPy, librosa, sounddevice |
| AI Orchestration | LangChain, LangGraph |
| Database | psycopg2 (PostgreSQL) |
| Observability | Comet Opik SDK |

### Web Application (Hub)

**Frontend:**
- React 18, TypeScript, Vite
- shadcn/ui, Tailwind CSS
- Recharts for visualizations
- TanStack React Query
- Deployed on Vercel

**Backend:**
- Python 3.10+, FastAPI
- LangChain, LangGraph for AI chat
- Supabase Python SDK
- Deployed on Railway

### Portable Device

- Raspberry Pi 5 (8GB RAM)
- Python 3.10+, FastAPI
- Focusrite Scarlett Solo USB audio interface

---

## Database Schema

### Table: fretcoach.sessions

Stores all practice session data across all devices.

```sql
CREATE TABLE fretcoach.sessions (
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,

    start_timestamp TIMESTAMP NOT NULL,
    end_timestamp TIMESTAMP,

    -- Metrics
    pitch_accuracy DOUBLE PRECISION,
    scale_conformity DOUBLE PRECISION,
    timing_stability DOUBLE PRECISION,

    -- Session configuration
    scale_chosen VARCHAR(100) NOT NULL,
    scale_type VARCHAR(20) DEFAULT 'natural',
    sensitivity DOUBLE PRECISION NOT NULL,
    strictness DOUBLE PRECISION NOT NULL,

    -- Note counts
    total_notes_played INTEGER DEFAULT 0,
    correct_notes_played INTEGER DEFAULT 0,
    bad_notes_played INTEGER DEFAULT 0,
    total_inscale_notes INTEGER,

    -- Session metadata
    duration_seconds DOUBLE PRECISION,
    ambient_light_option BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (session_id, user_id)
);
```

**Indexes:**
- `idx_sessions_start_timestamp` on `start_timestamp DESC`
- `idx_sessions_user_id` on `user_id`

### Table: fretcoach.ai_practice_plans

Stores AI-generated practice recommendations.

```sql
CREATE TABLE fretcoach.ai_practice_plans (
    practice_id UUID NOT NULL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,

    practice_plan TEXT NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    executed_session_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:**
- `idx_practice_plans_execution` on `executed_session_id`
- `idx_practice_plans_user_time` on `(user_id, generated_at DESC)`

### Table: fretcoach.user_configs

Stores user preferences for enabled metrics.

```sql
CREATE TABLE fretcoach.user_configs (
    user_id VARCHAR(255) NOT NULL PRIMARY KEY,
    enabled_metrics JSONB NOT NULL DEFAULT
        '{"pitch_accuracy": true, "scale_conformity": true, "timing_stability": true}',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Desktop Application Architecture

```
┌──────────────────────────────────────────┐
│         Electron Main Process            │
│  • Window management                     │
│  • Python subprocess spawning            │
└────────────┬─────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────┐    ┌──────────────────────┐
│ React   │    │   Python Backend     │
│ Frontend│◄───┤   FastAPI Server     │
│         │    │                      │
│         │    │  Routers:            │
│         │    │  • /session          │
│         │    │  • /config           │
│         │    │  • /ai/*             │
│         │    │  • /live-coach       │
│         │    │                      │
│         │    │  Core:               │
│         │    │  • audio_processor   │
│         │    │  • ai_agent_service  │
│         │    │  • live_coach_service│
└─────────┘    └──────────┬───────────┘
                          │
                          ▼
               ┌──────────────────────┐
               │  USB Audio Interface │
               └──────────────────────┘
```

**Communication:**
- REST API for session control and configuration
- WebSocket (`ws://127.0.0.1:8000/ws/metrics`) for real-time metrics at ~6.67 Hz
- IPC between Electron main and renderer processes

---

## Web Application Architecture

```
┌─────────────────────────────────┐
│    React Frontend (Vercel)      │
│  • Dashboard with charts        │
│  • Session history              │
│  • AI Coach Chat                │
└────────────┬────────────────────┘
             │ HTTPS
             ▼
┌─────────────────────────────────┐
│  FastAPI Backend (Railway)      │
│  • /sessions endpoints          │
│  • /chat (LangGraph agent)      │
│  • Supabase client              │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│   PostgreSQL (Supabase)         │
│  • fretcoach.sessions           │
│  • fretcoach.ai_practice_plans  │
│  • fretcoach.user_configs       │
└─────────────────────────────────┘
```

**Demo:** The live deployment at [fretcoach.online](https://fretcoach.online) shows two sample users for demonstration purposes.

---

## Portable Application Architecture

```
┌────────────────────────────────────────┐
│        Raspberry Pi 5                  │
│  ────────────────────────────────────  │
│                                        │
│  Python Backend (FastAPI):             │
│  • Same audio analysis engine          │
│  • Local session storage (SQLite)      │
│  • Periodic sync to Supabase           │
│  • Smart bulb control via Tuya API     │
│                                        │
│  Optional UI:                          │
│  • Web interface on local WiFi         │
│  • Physical buttons/LEDs               │
└──────────┬─────────────────────────────┘
           │
           ├──────► USB Audio (Scarlett Solo)
           │              │
           │              └──► Guitar Input
           │
           └──────► WiFi ──► Supabase (sync)
```

**Use Cases:**
- Backstage warmup without laptop
- Travel practice (fits in guitar case)
- Offline practice (syncs later)

---

## AI System

### LLM Providers

Supports multiple providers via LangChain:
- OpenAI (GPT-4o-mini)
- Google Gemini (2.0-flash-exp, 2.5-flash)
- Deepseek
- Minimax

### AI Workflows

**1. Practice Recommendations (AI Mode)**
- Fetch recent sessions from PostgreSQL
- Analyze performance patterns
- LLM generates structured recommendation (Pydantic)
- Save to `ai_practice_plans` table
- Traced in Opik with tags: `fretcoach-core`, `ai-mode`, `practice-recommendation`

**2. Live Coaching**
- Every 30 seconds during session
- Send current metrics to LLM
- Generate brief coaching feedback
- Display in UI
- Traced in Opik with tags: `fretcoach-core`, `ai-mode`, `live-feedback`

**3. AI Chat (Hub Dashboard)**
- LangGraph agent with database tools
- Tools: `execute_sql_query`, `get_database_schema`
- Conversational interface for practice guidance
- Traced in Opik with tags: `fretcoach-hub`, `ai-coach-chat`, `from-hub-dashboard`

---

## Observability with Opik

All LLM calls are traced via Opik integration.

**Trace Organization:**
- **Tags:** Categorize traces by type (e.g., `ai-coach-chat`, `ai-mode`, `live-feedback`)
- **Thread IDs:** Group related calls (e.g., `hub-{user_id}`, `{session_id}-live-aicoach-feedback`)
- **Metadata:** User IDs, session IDs, practice IDs

See [opik-usage.md](../opik/opik-usage.md) for detailed implementation.

---

## API Endpoints

### Desktop Backend

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/devices` | GET | List audio devices |
| `/config` | GET/POST | Get/set configuration |
| `/session/start` | POST | Start practice session |
| `/session/end` | POST | End session and save |
| `/ai/start-session` | GET | Get AI recommendation |
| `/live-coach/feedback` | POST | Request live coaching |
| `/ws/metrics` | WebSocket | Real-time metrics stream |

### Web Backend

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/sessions` | GET | List user sessions |
| `/sessions/{id}` | GET | Get session details |
| `/chat` | POST | AI coach chat messages |
| `/health` | GET | Health check |

---

## Deployment

### Desktop Application
- Built with electron-builder
- Artifacts: `.dmg` (macOS), `.exe` (Windows), `.AppImage` (Linux)

### Web Frontend
- Deployed on Vercel
- URL: [fretcoach.online](https://fretcoach.online)
- Auto-deploy from Git

### Web Backend
- Deployed on Railway
- Auto-deploy from Git
- CORS configured for fretcoach.online

---

## Security

**API Keys:**
- Stored in `.env` files (gitignored)
- Production: Environment variables in deployment platforms

**Database:**
- SSL/TLS encryption
- Row-level security (RLS) enabled on all tables
- Service role policies for backend access

**CORS:**
- Desktop: `allow_origins=["*"]` (local only)
- Web: `allow_origins=["https://fretcoach.online"]`

---

## Future Expandability

**Starts With Guitar, Expands Everywhere**

One coaching core. Many instruments.
AI-powered instant feedback for any skill-based training—music, sports, and beyond.

<p align="center">
  <img src="assets/images/future-expandability.jpg" alt="Future Expandability - Core Audio Analysis Agent" width="800"/>
</p>

The FretCoach architecture is designed for extensibility beyond guitar:

**Core Analysis Engine:**
- Modular audio processing pipeline adaptable to different instruments
- Configurable metric evaluation system
- Real-time feedback loop (<300ms) applicable across domains

**Potential Expansions:**
- **Piano:** Chord recognition, key velocity analysis, timing precision
- **Vocals:** Pitch accuracy, vibrato control, breath support metrics
- **Drums:** Rhythm consistency, dynamics control, polyrhythm coordination
- **Beyond Music:** Any skill requiring real-time audio or motion feedback—sports coaching, speech training, physical therapy

The dual-brain architecture (fast deterministic loop + slow AI loop) remains constant. Only the analysis parameters and domain-specific models need adaptation.

---

**Navigation:**
- [← AI Coach Agent Engine](ai-coach-agent-engine.md)
- [Environment Setup →](environment-setup.md)
- [Back to Index](index.md)
