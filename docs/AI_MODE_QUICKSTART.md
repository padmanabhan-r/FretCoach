# FretCoach AI Integration - Quick Start

## 🚀 AI Mode Overview

FretCoach now includes an **AI Coach mode** that analyzes your practice history and provides personalized recommendations using LangGraph orchestration and OpenAI.

### Two Practice Modes:

1. **Manual Mode** (Original)
   - You select the scale and settings
   - Full control over practice parameters
   
2. **AI Coach Mode** (New!)
   - AI analyzes your recent sessions
   - Recommends optimal scale and difficulty
   - Focuses on your weakest areas
   - Provides reasoning for recommendations

## 📋 Prerequisites

- PostgreSQL database running
- Google API key (for Gemini)
- Python 3.12+ with dependencies installed

## ⚡ Quick Setup

### 1. Environment Setup

Create a `.env` file in project root:

```bash
cp .env.example .env
# Edit .env and add your keys:
# GOOGLE_API_KEY=your_google_api_key
# DB_USER=paddy
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=fretcoach
```

### 2. Database Setup

```bash
# Create database
createdb fretcoach

# Run schema
psql -d fretcoach -f backend/sql/schema.sql
```

### 3. Verify Setup

```bash
python setup_ai_mode.py
```

This will check:
- ✅ Environment variables
- ✅ Database connection  
- ✅ Required packages
- ✅ AI agent initialization

## 🎯 Using AI Mode

### First Time

1. **Build Practice History** (Required)
   - Complete 2-3 manual practice sessions first
   - AI needs data to analyze
   - Vary scales and performance

2. **Try AI Mode**
   - Select "AI Coach" on mode selection screen
   - AI analyzes your history
   - Review recommendation
   - Accept to start AI-guided practice

### AI Recommendation Includes:

- **Scale**: Which scale to practice (e.g., "C diatonic")
- **Focus Area**: pitch, scale conformity, or timing
- **Difficulty**: Automatic strictness/sensitivity adjustment
- **Reasoning**: Why this practice session will help

### Example Recommendation:

```
🤖 AI Coach Recommendation

Scale: D pentatonic
Focus: Pitch Accuracy
Reasoning: Recent sessions show pitch accuracy at 75%, 
below your scale conformity (89%). Practicing D pentatonic 
will help improve pitch detection without scale complexity.

Strictness: 40%
Sensitivity: 60%
```

## 🏗️ Architecture

### LangGraph Agent Flow:

```
User Request → SQL Analysis → AI Reasoning → Structured Output → Session Start
```

**Nodes:**
1. `list_tables` - Discover database tables
2. `get_schema` - Retrieve table schemas
3. `generate_query` - Create analysis SQL
4. `check_query` - Validate SQL syntax
5. `run_query` - Execute queries
6. AI reasoning - Generate recommendation

**Database Tables:**
- `sessions` - Practice history with metrics
- `ai_practice_plans` - AI recommendations and execution tracking

### API Endpoints:

```
POST /ai/recommend - Get AI recommendation
POST /ai/session/start - Start AI session
GET /ai/status - Check pending plans
POST /ai/plan/{id}/execute - Link session to plan
```

## 🔧 Configuration

### Environment Variables:

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

### AI Behavior:

The AI considers:
- Recent session metrics (last 5 sessions)
- Weakest metric (pitch/scale/timing)
- Scale diversity in practice history
- Existing unexecuted practice plans
- Progressive difficulty adjustment

## 📊 Monitoring

### Check AI Plans:

```sql
SELECT * FROM ai_practice_plans 
ORDER BY generated_at DESC 
LIMIT 10;
```

### Session Performance:

```sql
SELECT 
  scale_chosen,
  AVG(pitch_accuracy) as avg_pitch,
  AVG(scale_conformity) as avg_scale,
  AVG(timing_stability) as avg_timing
FROM sessions
GROUP BY scale_chosen
ORDER BY AVG(pitch_accuracy + scale_conformity + timing_stability) DESC;
```

## 🐛 Troubleshooting

### "Failed to get AI recommendation"
- ✅ Check `GOOGLE_API_KEY` in .env
- ✅ Verify database connection credentials (DB_USER, DB_PASSWORD, etc.)
- ✅ Ensure 2+ manual sessions exist
- ✅ Check backend logs for details

### "No practice history found"
- ✅ Complete at least 2 manual sessions
- ✅ Check sessions table: `SELECT COUNT(*) FROM sessions;`

### SQL Errors in AI Agent
- ✅ Verify schema is up to date
- ✅ Check PostgreSQL connection
- ✅ Review agent logs in console

### AI Recommendations Not Making Sense
- ✅ Need more diverse practice data
- ✅ Try 5+ sessions with different scales
- ✅ Vary your performance intentionally

## 🔮 Future Enhancements

- [ ] Multi-user support with authentication
- [ ] Historical trend visualization dashboard
- [ ] Adaptive difficulty curves
- [ ] Scale mastery progression tracking
- [ ] Custom practice plan templates
- [ ] Voice-guided practice sessions
- [ ] Integration with music theory concepts

## 📖 Documentation

- [AI Integration Details](docs/AI_INTEGRATION.md)
- [Session Logging](docs/SESSION_LOGGING.md)
- [Database Schema](backend/sql/schema.sql)
- [LangGraph Notebook](backend/opik-eval/opik_langgraph_agent_test.ipynb)

## 🤝 Contributing

The AI integration is modular:
- `backend/api/services/ai_agent_service.py` - LangGraph agent
- `backend/api/routers/ai_mode.py` - API endpoints
- `application/src/components/ModeToggle.jsx` - Mode selection UI
- `application/src/components/AIRecommendation.jsx` - Recommendation display

Contributions welcome for:
- Additional LLM providers (Anthropic, Google)
- More sophisticated analysis algorithms
- Enhanced UI/UX for AI recommendations
- Performance optimizations
