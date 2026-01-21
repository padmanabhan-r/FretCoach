# System Architecture

Complete technical overview of FretCoach's multi-component architecture.

---

## High-Level Architecture

FretCoach consists of three main components sharing a central PostgreSQL database:

```
┌────────────────────────────────────────────────────────────────────┐
│                     PostgreSQL Database (Supabase)                 │
│                                                                    │
│  ┌─────────────────────┐         ┌──────────────────────────┐   │
│  │  fretcoach.sessions │         │ fretcoach.ai_practice_   │   │
│  │  ─────────────────  │         │        plans             │   │
│  │  • session_id (PK)  │         │  ──────────────────────  │   │
│  │  • user_id          │◄────────┤  • practice_id (PK)      │   │
│  │  • scale_chosen     │         │  • user_id               │   │
│  │  • metrics          │         │  • practice_plan (JSON)  │   │
│  │  • timestamps       │         │  • executed_session_id   │   │
│  └─────────────────────┘         └──────────────────────────┘   │
└───────────────────────┬───────────────────┬───────────────────────┘
                        │                   │
        ┌───────────────┼───────────────────┼───────────────┐
        │               │                   │               │
        ▼               ▼                   ▼               ▼
┌────────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐
│ Desktop App    │  │ Web Frontend │  │ Web Backend  │  │  Portable   │
│ ─────────────  │  │ ───────────  │  │ ───────────  │  │   Device    │
│ • Electron     │  │ • React      │  │ • FastAPI    │  │ ───────────│
│ • React UI     │  │ • TypeScript │  │ • Python     │  │ • RPi 5     │
│ • Python API   │  │ • Vite       │  │ • LangChain  │  │ • Python    │
│ • Audio DSP    │  │ • Tailwind   │  │ • Supabase   │  │ • Audio I/O │
│ • USB Audio    │  │              │  │   Client     │  │             │
└────────────────┘  └──────────────┘  └──────────────┘  └─────────────┘
        │                                     │                 │
        └───────────────────┬─────────────────┘                 │
                            │                                   │
                            ▼                                   ▼
                   ┌─────────────────┐               ┌─────────────────┐
                   │  LLM Providers  │               │  Smart Bulb     │
                   │  ─────────────  │               │  ─────────────  │
                   │  • OpenAI       │               │  • Tuya API     │
                   │  • Gemini       │               │  • WiFi Control │
                   │  • Deepseek     │               └─────────────────┘
                   │  • Minimax      │
                   └─────────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │   Comet Opik    │
                   │  ─────────────  │
                   │  • Trace Logs   │
                   │  • Observability│
                   └─────────────────┘
```

---

## Component 1: Desktop Application

### Purpose
Primary training environment for focused practice with real-time audio analysis and live AI coaching.

### Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, Vite, JavaScript |
| UI Framework | Tailwind CSS, Custom components |
| Desktop Runtime | Electron 27 |
| Backend | Python 3.10+, FastAPI 0.104+ |
| Audio Processing | NumPy, librosa, sounddevice |
| AI Orchestration | LangChain, OpenAI/Gemini SDKs |
| Database Client | psycopg2 (PostgreSQL) |
| Observability | Comet Opik SDK |

### Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    Electron Main Process                     │
│  ──────────────────────────────────────────────────────────  │
│  • Window management                                         │
│  • Python subprocess spawning                                │
│  • IPC bridge                                                │
└────────────────────────────┬─────────────────────────────────┘
                             │
          ┌──────────────────┴──────────────────┐
          │                                     │
          ▼                                     ▼
┌─────────────────────┐              ┌──────────────────────────┐
│  Renderer Process   │              │   Python Backend         │
│  ─────────────────  │              │  ──────────────────────  │
│                     │              │                          │
│  React Components:  │              │  FastAPI Server:         │
│  ├─ Header          │              │  └─ Routers:             │
│  ├─ StatusPanel     │              │     ├─ /devices          │
│  ├─ MetricsDisplay  │◄─────REST────┤     ├─ /config           │
│  ├─ VisualFeedback  │              │     ├─ /session          │
│  ├─ ControlPanel    │              │     ├─ /ai/...           │
│  ├─ AIRecommend     │              │     └─ /live-coach       │
│  ├─ LiveCoachFeed   │◄───WebSocket─┤                          │
│  └─ DebugPanel      │              │  Services:               │
│                     │              │  ├─ audio_processor      │
└─────────────────────┘              │  ├─ ai_agent_service     │
                                     │  ├─ live_coach_service   │
                                     │  └─ session_service      │
                                     │                          │
                                     │  Core:                   │
                                     │  ├─ audio_features       │
                                     │  ├─ audio_metrics        │
                                     │  ├─ scales               │
                                     │  └─ smart_bulb           │
                                     └──────────┬───────────────┘
                                                │
                                                ▼
                                     ┌──────────────────────────┐
                                     │   Audio Input Device     │
                                     │  USB Interface / Mic     │
                                     └──────────────────────────┘
```

### Data Flow: Session Execution

1. **User starts session** → Frontend calls `POST /session/start`
2. **Backend initializes:**
   - Spawns audio processing thread
   - Configures audio input stream
   - Creates session record in database
   - Initializes WebSocket connection
3. **Real-time audio loop:**
   - Audio callback fills buffer (continuous)
   - Processing thread analyzes frames every 150ms
   - Metrics calculated and sent via WebSocket
   - Frontend updates UI in real-time
4. **Live AI coaching** (optional):
   - Frontend requests feedback every 30s
   - Backend sends metrics to LLM
   - LLM generates coaching text
   - Traced in Opik
5. **User ends session** → Frontend calls `POST /session/end`
6. **Backend finalizes:**
   - Stops audio stream
   - Calculates final metrics
   - Saves session to database
   - Returns summary to frontend

### Communication Protocols

**REST API:**
- Configuration: GET/POST `/config`
- Session control: POST `/session/start`, `/session/end`
- AI recommendations: GET `/ai/start-session`
- Live coaching: POST `/live-coach/feedback`

**WebSocket:**
- Endpoint: `ws://127.0.0.1:8000/ws/metrics`
- Frequency: ~6.67 Hz (every 150ms)
- Payload: JSON with current metrics and state

**IPC (Electron):**
- Main → Renderer: Python stdout/stderr logs
- Renderer → Main: Window control events

---

## Component 2: Web Dashboard

### Purpose
Cloud-based analytics platform for session review, trend analysis, and AI chat coaching.

### Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, TypeScript, Vite |
| UI Framework | shadcn/ui, Tailwind CSS |
| Charts | Recharts |
| State Management | TanStack React Query |
| Routing | React Router v6 |
| Backend | Python 3.10+, FastAPI |
| Database Client | Supabase Python SDK |
| AI Orchestration | LangChain, LangGraph |
| Deployment | Vercel (frontend), Render (backend) |

### Architecture Diagram

```
┌───────────────────────────────────────────────────────────┐
│                    Web Browser (Client)                   │
│  ───────────────────────────────────────────────────────  │
│                                                           │
│  React Application (TypeScript):                          │
│  ├─ Pages:                                                │
│  │  ├─ Index (Landing)                                    │
│  │  ├─ Dashboard (Metrics)                                │
│  │  └─ Sessions (History)                                 │
│  ├─ Components:                                           │
│  │  ├─ NavLink, SessionCard                               │
│  │  ├─ Charts (LineChart, BarChart)                       │
│  │  └─ AI Coach Chat Interface                            │
│  └─ Hooks:                                                │
│     └─ useSessions, useToast                              │
└─────────────────────────┬─────────────────────────────────┘
                          │ HTTPS
                          ▼
┌───────────────────────────────────────────────────────────┐
│              FastAPI Backend (Python)                     │
│  ───────────────────────────────────────────────────────  │
│                                                           │
│  Routers:                                                 │
│  ├─ /sessions — CRUD operations                           │
│  ├─ /chat — AI coach conversation                         │
│  └─ /health — Status check                                │
│                                                           │
│  Services:                                                │
│  ├─ Session aggregation queries                           │
│  ├─ LangGraph agent for chat                              │
│  └─ Supabase client for DB access                         │
└─────────────────────────┬─────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────┐
│                 PostgreSQL (Supabase)                     │
│  ───────────────────────────────────────────────────────  │
│  • fretcoach.sessions table                               │
│  • fretcoach.ai_practice_plans table                      │
└───────────────────────────────────────────────────────────┘
```

### Features

**Dashboard View:**
- Recent sessions list with key metrics
- Performance trend charts (line graphs over time)
- Aggregate statistics (total practice time, avg scores)
- Session comparison (latest vs. average)

**AI Coach Chat:**
- Conversational interface for practice guidance
- LangGraph-powered agent with tools:
  - `get_recent_sessions` — Fetch user history
  - `analyze_performance` — Compute trends
  - `generate_recommendation` — Create practice plans
- Every message traced in Opik

**Session History:**
- Filterable list of all past sessions
- Detailed view for individual sessions
- Export capabilities (future)

### Deployment

**Frontend (Vercel):**
- Automatic deployment from Git
- Global CDN distribution
- Environment variables configured in Vercel dashboard
- URL: [fretcoach.online](https://fretcoach.online)

**Backend (Render):**
- Docker container or native Python runtime
- Auto-deploy from Git
- Environment variables in Render settings
- CORS configured for fretcoach.online

---

## Component 3: Portable Device (Raspberry Pi)

### Purpose
Edge computing practice device—a guitar pedal-like unit running the same analysis engine locally.

### Technology Stack

| Layer | Technology |
|-------|------------|
| Hardware | Raspberry Pi 5 (8GB RAM) |
| OS | Raspberry Pi OS (64-bit) |
| Audio Interface | Focusrite Scarlett Solo USB |
| Backend | Python 3.10+, FastAPI |
| Audio Processing | NumPy, librosa, sounddevice |
| Database Sync | Periodic sync to Supabase |
| UI | Optional: small display or web interface |

### Status

**Current:** Prototyping phase (~30% complete)

**Completed:**
- Hardware setup (RPi 5 + Scarlett Solo)
- OS installation and configuration
- Python environment setup
- Audio I/O testing

**In Progress:**
- Adapting audio analysis agent engine for ARM architecture
- Optimizing for real-time performance on RPi
- Implementing local session caching
- Sync mechanism with cloud database

**Planned:**
- Physical enclosure design (3D printed pedal case)
- Battery power management
- LED status indicators
- Button controls for start/stop

### Architecture Concept

```
┌────────────────────────────────────────────┐
│        Raspberry Pi 5                      │
│  ────────────────────────────────────────  │
│                                            │
│  Python Backend (FastAPI):                 │
│  ├─ Audio analysis agent engine (same as desktop)│
│  ├─ Local session storage (SQLite)         │
│  ├─ Periodic sync to Supabase              │
│  └─ Smart bulb control                     │
│                                            │
│  Optional Web UI:                          │
│  └─ Accessible via local WiFi              │
└──────────────┬─────────────────────────────┘
               │
               ├──────────► USB Audio Interface (Scarlett Solo)
               │                    │
               │                    └──────► Guitar Input
               │
               └──────────► WiFi ──────► Supabase (when online)
```

### Use Cases

1. **Backstage warmup** — Practice before a performance without a laptop
2. **Travel practice** — Portable device fits in guitar case
3. **Offline practice** — Works without internet (syncs later)
4. **Bedroom practice** — Minimal setup, pedal-like form factor

---

## Data Architecture

### Database Schema

**Table: `fretcoach.sessions`**

```sql
CREATE TABLE fretcoach.sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    start_timestamp TIMESTAMP NOT NULL,
    end_timestamp TIMESTAMP,
    scale_chosen VARCHAR(100) NOT NULL,
    scale_type VARCHAR(50) NOT NULL,
    pitch_accuracy FLOAT,
    scale_conformity FLOAT,
    timing_stability FLOAT,
    noise_control FLOAT,
    total_notes_played INTEGER,
    correct_notes_played INTEGER,
    bad_notes_played INTEGER,
    unique_notes_used INTEGER,
    duration_seconds INTEGER,
    strictness FLOAT,
    sensitivity FLOAT,
    ambient_lighting_used BOOLEAN DEFAULT FALSE,
    device_type VARCHAR(50) DEFAULT 'desktop',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sessions_user_id ON fretcoach.sessions(user_id);
CREATE INDEX idx_sessions_timestamp ON fretcoach.sessions(start_timestamp DESC);
```

**Table: `fretcoach.ai_practice_plans`**

```sql
CREATE TABLE fretcoach.ai_practice_plans (
    practice_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    practice_plan JSONB NOT NULL,
    generated_at TIMESTAMP DEFAULT NOW(),
    executed_session_id UUID REFERENCES fretcoach.sessions(session_id),
    executed_at TIMESTAMP
);

CREATE INDEX idx_practice_plans_user_id ON fretcoach.ai_practice_plans(user_id);
CREATE INDEX idx_practice_plans_generated_at ON fretcoach.ai_practice_plans(generated_at DESC);
```

### Data Flow: Cross-Component

**Scenario:** User practices on desktop, reviews on web, then practices on portable device

1. **Desktop practice:**
   - Session data saved to `sessions` table
   - AI recommendation (if used) saved to `ai_practice_plans` table

2. **Web dashboard review:**
   - Frontend fetches sessions via `/sessions` endpoint
   - Backend queries Supabase for user's sessions
   - AI chat can reference this session data

3. **Portable device practice:**
   - Device syncs latest sessions from Supabase
   - User practices (data stored locally if offline)
   - When online, syncs new session back to Supabase
   - Desktop and web now see portable sessions

**Synchronization strategy:**
- Pull: Fetch sessions updated after last sync timestamp
- Push: Upload local sessions not yet in cloud
- Conflict resolution: Last-write-wins (sessions are immutable after creation)

---

## AI System Architecture

### LLM Provider Abstraction

FretCoach supports multiple LLM providers through LangChain's unified interface:

```python
# OpenAI
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Google Gemini
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")

# Deepseek
model = ChatOpenAI(
    base_url="https://api.deepseek.com",
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY")
)

# Minimax
model = ChatOpenAI(
    base_url="https://api.minimax.chat/v1",
    model="minimax-2.1-open",
    api_key=os.getenv("MINIMAX_API_KEY")
)
```

All providers traced identically through Opik.

### AI Workflows

**1. Practice Recommendation (AI Mode)**

```
User Request
    ↓
Fetch Recent Sessions (PostgreSQL)
    ↓
Analyze Performance Patterns
    ↓
LLM Call: Generate Recommendation
    ├─ Input: Session metrics
    ├─ Output: Structured (Pydantic)
    └─ Traced: Opik
    ↓
Save to ai_practice_plans (PostgreSQL)
    ↓
Return to User
```

**2. Live Coaching (During Session)**

```
Session Running (metrics updating)
    ↓
Every 30s: Send Current Metrics
    ↓
Identify Weakest Metric
    ↓
LLM Call: Generate Coaching Feedback
    ├─ Input: Real-time metrics
    ├─ Output: Brief corrective text
    └─ Traced: Opik
    ↓
Display in UI
```

**3. AI Chat (Web Dashboard)**

```
User Message
    ↓
LangGraph Agent
    ├─ Tool: get_recent_sessions
    ├─ Tool: analyze_trends
    └─ Tool: generate_practice_plan
    ↓
LLM Reasoning + Tool Calls
    ↓ (Each step traced)
Opik
    ↓
Agent Response
    ↓
Display to User
```

---

## Observability with Comet Opik

### Integration Points

Every AI interaction is traced:

**Desktop App:**
- AI practice recommendations
- Live coaching feedback
- Session analysis

**Web Dashboard:**
- AI coach chat messages
- Practice plan generation
- Performance analysis

### Trace Structure

**Metadata:**
- `user_id` — User identifier
- `session_id` — Session identifier (for live coaching)
- `practice_id` — Practice plan identifier (for AI mode)

**Tags:**
- `ai-mode` — Practice recommendations
- `live-coach` — Real-time session feedback
- `web-chat` — Dashboard chat interactions

**Example trace:**
```json
{
  "trace_id": "abc-def-123",
  "name": "generate_ai_recommendation",
  "tags": ["ai-mode", "recommendation"],
  "metadata": {
    "user_id": "user-paddy",
    "practice_id": "practice-xyz"
  },
  "input": {
    "recent_sessions": [...],
    "user_profile": {...}
  },
  "output": {
    "scale_name": "D Minor",
    "scale_type": "pentatonic",
    "focus_area": "timing",
    "reasoning": "Your timing stability has been consistently low...",
    "strictness": 0.6,
    "sensitivity": 0.5
  },
  "duration_ms": 1234
}
```

---

## Security Considerations

### API Key Management

- All API keys stored in `.env` files (never in code)
- `.env` files gitignored
- Production: Environment variables in deployment platform

### Database Access

- PostgreSQL with SSL/TLS encryption
- Row-level security policies in Supabase
- User data scoped by `user_id`

### CORS Configuration

Desktop app:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Local Electron app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Web backend:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://fretcoach.online"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

---

## Scalability Considerations

### Current Limits

- **Desktop:** Single user, local processing
- **Web:** Multi-user, shared backend
- **Database:** Supabase free tier (500MB, 2GB bandwidth/month)

### Scaling Strategy (Future)

**Database:**
- Migrate to paid Supabase tier or self-hosted PostgreSQL
- Implement connection pooling (pgBouncer)
- Add read replicas for analytics queries

**Web Backend:**
- Containerize with Docker
- Deploy to Kubernetes for auto-scaling
- Add Redis for caching sessions
- Implement rate limiting

**Audio Processing:**
- Desktop/portable remain single-user (local)
- No scaling needed (runs on client)

---

## Deployment Pipeline

### Desktop Application

**Build process:**
1. Frontend: `npm run build` → Vite bundle
2. Backend: Package Python dependencies with app
3. Electron: `electron-builder` creates installers

**Artifacts:**
- macOS: `.dmg`, `.app`
- Windows: `.exe`, `.msi`
- Linux: `.AppImage`, `.deb`

### Web Application

**Frontend (Vercel):**
```yaml
# vercel.json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm install",
  "framework": "vite"
}
```

**Backend (Render):**
```yaml
# render.yaml
services:
  - type: web
    name: fretcoach-api
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: OPENAI_API_KEY
        sync: false
```

---

**Navigation:**
- [← Judges Start Here](judges-start-here.md)
- [Desktop Application →](desktop-app.md)
- [Audio Processing Engine →](audio-engine.md)
