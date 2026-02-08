# FretCoach Hub - Web Analytics Platform

Web platform for FretCoach practice tracking, AI coaching, and session analytics.

**Live Demo:** [fretcoach.online](https://fretcoach.online)

![FretCoach Trifecta](/images/FretCoach%20Trifecta.jpeg)

## Overview

FretCoach Hub is the cloud analytics companion to FretCoach Studio and Portable. Review practice history, chat with the AI coach, generate personalized practice plans, and track progress across all devices.

> **Demo Note:** The live deployment at [fretcoach.online](https://fretcoach.online) shows two sample users for demonstration purposes.

![FretCoach Hub Home](../docs/assets/images/hub/1.%20Hub%20-%20Home.png)

## Key Features

- **AI Practice Coach** — Conversational chat interface powered by text-to-SQL agent and Gemini 3 Flash Preview
- **Session History** — Browse and analyze all past practice sessions
- **Performance Analytics** — Trend charts, session comparisons, and aggregate statistics
- **Practice Plan Generation** — AI-generated recommendations synced to Studio and Portable

### Features Overview

![Hub Features](../docs/assets/images/hub/2.%20Hub%20-%20Features.png)

### Performance Dashboard

![Hub Dashboard](../docs/assets/images/hub/3.%20Hub%20-%20Dashboard.png)

### AI Practice Coach

![Hub AI Coach](../docs/assets/images/hub/4.%20Hub%20-%20AI%20Coach.png)

## Tech Stack

**Frontend:**
- React 18 with TypeScript
- Vite for build tooling
- Tailwind CSS + shadcn/ui components
- Recharts for data visualization
- TanStack React Query for state management

**Backend:**
- FastAPI (Python)
- LangChain/LangGraph for AI orchestration
- Supabase PostgreSQL client
- Comet Opik for observability

## Quick Start

### Backend

```bash
cd web-backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Environment variables** (create `web-backend/.env`):
```env
DB_HOST=your_supabase_host.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_password
GOOGLE_API_KEY=your_gemini_api_key
```

### Frontend

```bash
cd web-frontend
npm install
npm run dev  # http://localhost:5173
```

**Environment variables** (create `web-frontend/.env`):
```env
VITE_API_BASE_URL=http://localhost:8000
```

> **Complete setup guide:** [docs/environment-setup.md](../docs/environment-setup.md)

## Deployment

**Frontend:** Deployed on Vercel
**Backend:** Deployed on Railway
**Website:** [fretcoach.online](https://fretcoach.online)

## Documentation

For detailed usage and architecture:
- [System Architecture](../docs/architecture.md#component-2-web-dashboard)
- [AI Coaching System](../docs/ai-coach-agent-engine.md)
- [Quickstart Guide](../docs/quickstart.md)
