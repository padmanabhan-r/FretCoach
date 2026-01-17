# FretCoach AI Mode - Quick Reference

## 🚀 Quick Start

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env with your OPENAI_API_KEY and FRETCOACH_DB_PATH

# 2. Initialize database
createdb fretcoach
psql -d fretcoach -f backend/sql/schema.sql

# 3. Verify setup
python setup_ai_mode.py

# 4. Start backend
cd backend
python -m api.server

# 5. Start frontend
cd application
npm run dev
```

## 📁 Key Files Created/Modified

### Backend
```
backend/api/services/ai_agent_service.py     [NEW] LangGraph agent
backend/api/routers/ai_mode.py               [NEW] AI endpoints
backend/api/server.py                        [MOD] Added AI router
backend/api/models.py                        [MOD] Added AI models
```

### Frontend
```
application/src/components/ModeToggle.jsx         [NEW] Mode selection
application/src/components/AIRecommendation.jsx   [NEW] AI UI
application/src/App.jsx                           [MOD] AI integration
application/src/api.js                            [MOD] AI endpoints
```

### Documentation
```
docs/AI_INTEGRATION.md                 Technical details
docs/AI_MODE_QUICKSTART.md            User guide
docs/AI_IMPLEMENTATION_SUMMARY.md     Complete summary
.env.example                          Config template
setup_ai_mode.py                      Setup script
```

## 🎯 API Endpoints

```python
# Get AI recommendation
POST /ai/recommend?user_id=default_user

# Start AI session (includes config)
POST /ai/session/start?user_id=default_user

# Check pending plans
GET /ai/status?user_id=default_user

# Link session to plan
POST /ai/plan/{practice_id}/execute?session_id={session_id}

# Existing endpoints
POST /session/start    # Start practice
POST /session/stop     # Stop practice
GET /session/metrics   # Get metrics
```

## 🗄️ Database Schema

```sql
-- AI Practice Plans
CREATE TABLE ai_practice_plans (
    practice_id uuid PRIMARY KEY,
    user_id varchar(255) NOT NULL,
    practice_plan text NOT NULL,  -- JSON
    executed_session_id varchar(255),
    generated_at timestamp DEFAULT CURRENT_TIMESTAMP
);

-- Sessions (existing)
CREATE TABLE sessions (
    session_id varchar(255) NOT NULL,
    user_id varchar(255) NOT NULL,
    scale_chosen varchar(100) NOT NULL,
    pitch_accuracy float,
    scale_conformity float,
    timing_stability float,
    -- ... other fields
);
```

## 🔄 React Component Flow

```jsx
App.jsx (Main)
├── ModeToggle (mode = 'manual' | 'ai')
│   ├── Manual → ScaleSelection
│   └── AI → AIRecommendation
│
├── AIRecommendation
│   ├── Loading state (fetching)
│   ├── Display recommendation
│   ├── Accept → applyConfig() → ready
│   └── Reject → back to ModeToggle
│
└── Session (when ready)
    ├── AI mode banner (if AI)
    ├── ControlPanel (start/stop)
    └── Metrics display
```

## 🧪 Testing

```bash
# Check setup
python setup_ai_mode.py

# Test AI endpoint directly
curl -X POST http://localhost:8000/ai/recommend?user_id=test

# Check database
psql -d fretcoach
SELECT * FROM ai_practice_plans;
SELECT * FROM sessions ORDER BY start_timestamp DESC LIMIT 5;
```

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| "No GOOGLE_API_KEY" | Set in .env file |
| "Database connection failed" | Check PostgreSQL running & DB credentials |
| "No practice history" | Complete 2-3 manual sessions first |
| "Import errors" | Run `pip install -e .` |

## 📊 Sample Practice Plan JSON

```json
{
  "scale_name": "D",
  "scale_type": "pentatonic",
  "focus_area": "pitch",
  "reasoning": "Your pitch accuracy (72%) is below scale conformity (88%). Practice D pentatonic to improve pitch detection with simpler scale structure.",
  "strictness": 0.4,
  "sensitivity": 0.6,
  "generated_at": "2026-01-16T10:30:00"
}
```

## 🎨 UI States

1. **Audio Setup** → Configure devices
2. **Mode Selection** → Manual or AI
3. **Manual Path** → Choose scale → Ready
4. **AI Path** → Loading → Recommendation → Accept → Ready  
5. **Ready** → Start session → Practice → Stop

## ⚙️ Environment Variables

```bash
# Required
GOOGLE_API_KEY=your_key...
DB_USER=paddy
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fretcoach

# Optional
OPIK_API_KEY=...  # For LLM tracing
```

## 📈 Success Metrics

- ✅ Mode toggle functional
- ✅ AI generates valid recommendations
- ✅ Sessions link to practice plans
- ✅ UI shows AI mode clearly
- ✅ No errors in console
- ✅ Database updates correctly

## 🔗 Architecture Diagram

```
┌─────────────┐
│   Electron  │
│  (Frontend) │
└──────┬──────┘
       │ HTTP/WS
       ▼
┌─────────────┐
│   FastAPI   │
│  (Backend)  │
└──┬────┬─────┘
   │    │
   │    └──────► PostgreSQL
   │             (sessions, ai_practice_plans)
   │
   ▼
┌─────────────┐
│  LangGraph  │
│    Agent    │
└──────┬──────┘
       │
       ▼
   Google Gemini
```

## 📞 Support

- Docs: `docs/AI_*.md`
- Setup: `python setup_ai_mode.py`
- Schema: `backend/sql/schema.sql`
- Notebook: `backend/opik-eval/opik_langgraph_agent_test.ipynb`
