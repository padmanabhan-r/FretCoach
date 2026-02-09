# FretCoach Hub - Web Dashboard

Post-practice analytics, performance tracking, and AI coaching through a web interface.

![FretCoach Hub Home](assets/images/hub/1.%20Hub%20-%20Home.png)

---

## Overview

**FretCoach Hub** ([fretcoach.online](https://www.fretcoach.online)) is the analytics and planning center of the FretCoach ecosystem.

**Purpose:** Transform practice data into actionable insights and improvement strategies.

**Live Demo:** [fretcoach.online/dashboard](https://www.fretcoach.online/dashboard)

> **Note:** Demo shows two sample users for demonstration purposes.

---

## Key Features

### 1. Performance Analytics Dashboard

![Hub Dashboard](assets/images/hub/3.%20Hub%20-%20Dashboard.png)

**Session History:**
- Sortable table with date, duration, scale, metrics, quality scores
- Filter by date range or scale
- Click any session for detailed breakdown

**Performance Charts:**
- **Metric trends** — Track improvement over time
- **Scale distribution** — Which scales you practice most
- **Quality distribution** — Your typical performance levels
- **Practice volume** — Total time investment

**Summary Stats:**
- Total sessions and practice time
- Average metrics
- Most practiced scale
- Weakest area identification

---

### 2. AI Chat Coach

![Hub AI Coach](assets/images/hub/4.%20Hub%20-%20AI%20Coach.png)

Conversational interface for practice guidance using your session data.

**Example questions:**
- "What should I practice next?"
- "Show me my progress trends"
- "Compare my latest session to my average"
- "Which scales have I practiced?"

**How it works:**
- Google Gemini 3 Flash Preview (with Minimax MiniMax-M2.1 fallback)
- Queries session database for context
- Generates data-driven recommendations
- Creates practice plans you can save
- All conversations traced in Opik

**Practice Plans:**
- AI analyzes weakest metrics
- Recommends specific scales and exercises
- Save plans to use in Studio/Portable AI Mode
- Plans marked completed after practice

---

### 3. Session Details

Click any session to see:
- Full metadata and configuration
- Detailed metric breakdown
- Note statistics
- Performance assessment

---

## Technical Stack

**Frontend:**
- React 18 + TypeScript + Vite
- Tailwind CSS + shadcn/ui
- Recharts for visualizations
- Deployed on Vercel

**Backend:**
- Python FastAPI
- LangChain for AI orchestration
- LangGraph for agent workflows
- PostgreSQL (Supabase)
- Deployed on Railway

> **Architecture:** See [System Architecture](architecture.md)

---

## Setup

### Prerequisites

- Node.js 18+
- Python 3.12+
- PostgreSQL (Supabase)
- Google Gemini API key

### Quick Start

Start both backend and frontend together:

```bash
cd web
./start.sh
```

Or manually:

**Backend:**
```bash
cd web/web-backend
uv sync
cp ../../backend/.env .env
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
cd web/web-frontend
npm install
echo "VITE_API_BASE_URL=http://localhost:8000" > .env
npm run dev  # http://localhost:5173
```

> **Full setup:** [Quickstart Guide](quickstart.md) | [Environment Setup](environment-setup.md)

---

## Usage

### Reviewing Sessions

1. Visit dashboard to see recent sessions
2. Sort/filter by date, scale, or quality
3. View charts for trends and patterns
4. Click sessions for detailed breakdown

### Using AI Coach

1. Navigate to AI Coach tab
2. Ask questions about your practice data
3. Request practice recommendations
4. Save generated plans
5. Use plans in Studio/Portable AI Mode

### Practice Plan Workflow

```
Hub (Generate Plan) → Studio/Portable (AI Mode loads plan)
→ Practice → Plan marked completed → Hub (Review results)
```

---

## API Endpoints

**Sessions:**
- `GET /api/sessions?user_id={id}` — List all sessions
- `GET /api/sessions/{id}` — Session details
- `DELETE /api/sessions/{id}` — Delete session

**Analytics:**
- `GET /api/analytics/summary?user_id={id}` — Summary stats
- `GET /api/analytics/trends?user_id={id}` — Chart data

**AI Coach:**
- `POST /api/chat` — Send message
- `GET /api/chat/history?thread_id={id}` — Conversation history

**Practice Plans:**
- `GET /api/practice-plans?user_id={id}` — List plans
- `POST /api/practice-plans` — Generate plan
- `PUT /api/practice-plans/{id}` — Update status

> **Complete API docs:** See backend README

---

## Database

**Main tables:**
- `fretcoach.sessions` — Practice session data
- `fretcoach.ai_practice_plans` — Generated practice plans
- `fretcoach.user_configs` — User preferences

> **Schema details:** See [System Architecture](architecture.md#database-schema)

---

## Deployment

**Frontend (Vercel):**
- Auto-deploy on push to `main`
- Build: `cd web/web-frontend && npm run build`
- Domain: [fretcoach.online](https://www.fretcoach.online)

**Backend (Railway):**
- Auto-deploy on push to `main`
- Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Health check: `GET /health`

**Database (Supabase):**
- Managed PostgreSQL with automatic backups
- Connection pooling enabled

---

## Troubleshooting

**Dashboard not loading sessions:**
- Check user_id matches database records
- Verify database connection in backend logs
- Check browser console for API errors

**AI Coach not responding:**
- Verify Google API key in `.env`
- Check API rate limits and quota
- Review backend logs for errors

**Charts not displaying:**
- Ensure at least 2 sessions exist
- Check browser console for errors
- Verify API returns valid data

**Slow performance:**
- Check network tab for slow API responses
- Enable React Query caching
- Reduce chart data points

---

**Navigation:**
- [← Portable Application](portable-app.md)
- [Architecture →](architecture.md)
- [Back to Index](index.md)
