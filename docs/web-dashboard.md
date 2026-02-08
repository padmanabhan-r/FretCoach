# FretCoach Hub - Web Dashboard

Post-practice analytics, performance tracking, and AI coaching through a web interface.

![FretCoach Hub Home](assets/images/hub/1.%20Hub%20-%20Home.png)

---

## Overview

**FretCoach Hub** ([fretcoach.online](https://www.fretcoach.online)) is the analytics and planning center of the FretCoach ecosystem. While Studio and Portable focus on real-time practice, the Hub provides post-session analysis, trend visualization, and conversational AI coaching.

**Core Purpose:** Transform practice data into actionable insights and improvement strategies.

---

## Key Features

### 1. Performance Analytics Dashboard

**Visual analysis of all practice sessions**

![Hub Dashboard](assets/images/hub/3.%20Hub%20-%20Dashboard.png)

**Session History:**
- Sortable table with date, duration, scale, metrics, and quality scores
- Filter by date range or scale
- Search and pagination
- Export to CSV (planned)

**Performance Charts:**
- **Metric trends over time** — Track improvement across pitch, scale, timing, noise
- **Scale distribution** — See which scales you practice most
- **Quality score distribution** — Understand your typical performance level
- **Practice volume** — Total time investment tracking

**Summary Statistics:**
- Total sessions and practice time
- Average metrics across all sessions
- Most practiced scale and best performance
- Weakest area identification

---

### 2. AI Chat Coach

**Conversational interface for practice guidance**

![Hub AI Coach](assets/images/hub/4.%20Hub%20-%20AI%20Coach.png)

The AI coach uses your practice data to provide personalized recommendations and answer questions about your progress.

**What you can ask:**
- "What should I practice next?"
- "Show me my progress trends"
- "Compare my latest session to my average"
- "Which scales have I practiced?"
- "Why is my timing inconsistent?"

**How it works:**
- Uses Google Gemini 3 Flash Preview (with MiniMax 2.1 fallback)
- Queries your session database for context
- Generates data-driven recommendations
- Creates practice plans you can save
- All conversations traced via Opik for observability

**Practice Plan Generation:**
- AI analyzes weakest metrics
- Recommends specific scales and exercises
- You can save plans and use them in Studio/Portable AI Mode
- Plans marked as completed after practice sessions

---

### 3. Session Detail View

Click any session in the history table to see:
- Full session metadata and configuration
- Detailed metric breakdown
- Note statistics and scale coverage
- Performance assessment

**Actions:**
- Delete session
- Export session data
- Compare with other sessions

---

## Technical Stack

### Frontend
- React 18 + TypeScript + Vite
- Tailwind CSS + shadcn/ui components
- Recharts for visualizations
- Deployed on Vercel

### Backend
- Python FastAPI
- LangChain for AI orchestration
- PostgreSQL (Supabase) database
- Deployed on Railway

> **Architecture:** See [System Architecture](architecture.md) for detailed technical diagrams.

---

## Setup

### Prerequisites

- Node.js 18+
- Python 3.10+
- PostgreSQL (or Supabase account)
- Google Gemini API key

### Backend Setup

```bash
cd web/web-backend
uv sync
cp ../../backend/.env .env  # Use same credentials as desktop backend

# Start backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Environment variables** (`.env`):
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/fretcoach

# LLM Providers
GOOGLE_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3-flash-preview
MINIMAX_API_KEY=your_minimax_api_key  # Optional fallback

# Observability
OPIK_API_KEY=your_opik_key  # Optional
OPIK_WORKSPACE=your_workspace

# Application
USER_ID=your_user_id
```

### Frontend Setup

```bash
cd web/web-frontend
npm install
echo "VITE_API_BASE_URL=http://localhost:8000" > .env

# Start frontend
npm run dev  # Visit http://localhost:5173
```

> **Detailed setup:** See [Quickstart Guide](quickstart.md) and [Environment Setup](environment-setup.md).

---

## Usage

### Reviewing Practice Sessions

1. Visit the dashboard to see recent sessions
2. Sort/filter the session table by date, scale, or quality
3. View charts to identify trends and patterns
4. Click any session for detailed breakdown

### Using AI Coach

1. Navigate to AI Coach tab
2. Ask questions about your practice data
3. Request practice recommendations
4. Save generated practice plans
5. Use saved plans in Studio/Portable AI Mode

### Generating Practice Plans

**Via AI Chat:**
- Ask "What should I practice next?"
- Review AI recommendation
- Click "Save Plan"

**Via Dashboard Button:**
- Click "Generate Practice Plan"
- Review recommendation
- Accept or regenerate
- Plan saved to database

### Practice Plan Workflow

```
Web Dashboard (Generate Plan) → Studio/Portable (AI Mode loads plan)
→ Practice Session → Plan marked completed → Web Dashboard (Review results)
```

---

## API Endpoints

**Sessions:**
- `GET /api/sessions?user_id={id}` — List sessions
- `GET /api/sessions/{session_id}` — Session details
- `DELETE /api/sessions/{session_id}` — Delete session

**Analytics:**
- `GET /api/analytics/summary?user_id={id}` — Summary stats
- `GET /api/analytics/trends?user_id={id}` — Chart data
- `GET /api/analytics/scales?user_id={id}` — Per-scale analysis

**AI Coach:**
- `POST /api/chat` — Send message to AI
- `GET /api/chat/history?thread_id={id}` — Conversation history

**Practice Plans:**
- `GET /api/practice-plans?user_id={id}` — List plans
- `POST /api/practice-plans` — Generate plan
- `PUT /api/practice-plans/{id}` — Update status
- `DELETE /api/practice-plans/{id}` — Delete plan

---

## Database Schema

**Sessions Table:** `fretcoach.sessions`
- session_id, user_id, timestamps, duration
- scale_chosen, scale_type, settings
- pitch_accuracy, scale_conformity, timing_stability, noise_control
- total_notes_played, correct_notes, wrong_notes
- practice_mode (manual/ai)

**Practice Plans Table:** `fretcoach.ai_practice_plans`
- practice_id, user_id, generated_at
- practice_plan (JSON with scale, exercises, reasoning)
- status (pending/in_progress/completed)
- session_id (link to completed session)

> **Complete schema:** See [System Architecture](architecture.md#database-schema).

---

## Troubleshooting

**Dashboard not loading sessions:**
- Check user_id matches database records
- Verify database connection in backend logs
- Check browser console for API errors
- Ensure CORS settings if on different domains

**AI Coach not responding:**
- Verify Google API key in backend `.env`
- Check API rate limits
- Review backend logs for errors
- Check Opik traces for failure points

**Charts not displaying:**
- Ensure at least 2 sessions exist
- Check browser console for Recharts errors
- Verify API returns valid data format
- Clear browser cache

**Slow performance:**
- Check network tab for slow API responses
- Optimize database queries (add indexes)
- Enable React Query caching
- Reduce chart data points

> **Detailed troubleshooting:** See [Troubleshooting Guide](troubleshooting.md).

---

## Deployment

### Frontend (Vercel)
- Connected to GitHub repo
- Build: `cd web/web-frontend && npm run build`
- Auto-deploy on push to `main`
- Domain: [fretcoach.online](https://www.fretcoach.online)

### Backend (Railway)
- Connected to GitHub repo
- Start: `cd web/web-backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
- Auto-deploy on push to `main`
- Health check: `GET /health`

### Database (Supabase)
- Managed PostgreSQL with automatic backups
- Connection pooling enabled
- Point-in-time recovery

---

## Best Practices

**For Users:**
- Review dashboard weekly to track progress
- Use AI coach for data-driven recommendations
- Save and use practice plans regularly
- Compare sessions to understand patterns

**For Developers:**
- Use React Query for API calls (caching)
- Keep components small and focused
- Enable Opik tracing for all LLM calls
- Index user_id and timestamp columns

---

## Future Enhancements

- Social features (leaderboards, challenges)
- Advanced analytics (skill forecasting, correlation analysis)
- Instructor mode (teacher dashboards)
- Mobile app (iOS/Android)
- Export to DAWs (Ableton, Logic Pro)

---

**Navigation:**
- [← Portable Application](portable-app.md)
- [Architecture →](architecture.md)
- [Back to Index](index.md)
