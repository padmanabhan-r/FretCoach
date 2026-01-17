# FretCoach AI Integration Setup Guide

## Environment Variables

Create a `.env` file in the project root with the following:

```bash
# Google API Key (required for AI mode with Gemini)
GOOGLE_API_KEY=your_google_api_key_here

# Database connection (required for AI mode)
DB_USER=paddy
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fretcoach

# Optional: Opik API Key for tracking
OPIK_API_KEY=your_opik_key_here
```

## Database Setup

1. Ensure PostgreSQL is running
2. Create the database:
```sql
CREATE DATABASE fretcoach;
```

3. Run the schema creation:
```bash
psql -d fretcoach -f backend/sql/schema.sql
```

## Dependencies

All required dependencies are in `pyproject.toml`. Install them:

```bash
pip install -e .
```google-genai` - Google Gemini integration
- `langgraph` - State graph orchestration
- `langchain-community` - SQL tools
- `psycopg2-binary` - PostgreSQL adapter
- `sqlalchemy` - Database ORM
- `python-dotenv` - Environment variable loading integration
- `langgraph` - State graph orchestration
- `langchain-community` - SQL tools
- `psycopg2-binary` - PostgreSQL adapter
- `sqlalchemy` - Database ORM

## AI Mode Features

### How it Works

1. **Analysis Phase**: The AI agent analyzes your practice history by:
   - Checking for existing unexecuted practice plans
   - Querying recent session performance metrics
   - Identifying weak areas (pitch, scale conformity, timing)
   - Analyzing scale diversity in recent practice

2. **Recommendation Phase**: Based on analysis, the AI:
   - Recommends a specific scale to practice
   - Selects scale type (diatonic or pentatonic)
   - Identifies primary focus area
   - Sets appropriate difficulty (strictness/sensitivity)
   - Provides reasoning for the recommendation

3. **Execution Phase**: When you accept:
   - Practice plan is saved to `ai_practice_plans` table
   - Session starts with recommended settings
   - Session is linked to the practice plan via `executed_session_id`

### LangGraph Architecture

The AI agent uses a state graph with these nodes:
1. `list_tables` - Discovers available database tables
2. `call_get_schema` - Retrieves table schemas
3. `get_schema` - Executes schema retrieval
4. `generate_query` - Creates SQL queries for analysis
5. `check_query` - Validates SQL syntax and logic
6. `run_query` - Executes validated queries

The graph flows through these states to safely analyze your data and generate insights.

## API Endpoints

### AI Mode Endpoints

**GET /ai/status** - Check for pending practice plans
**POST /ai/recommend** - Get new AI recommendation
**POST /ai/session/start** - Start AI-guided session
**POST /ai/plan/{practice_id}/execute** - Mark plan as executed

### Manual Mode Endpoints (existing)

**POST /session/start** - Start manual practice session
**POST /session/stop** - Stop current session
**GET /session/metrics** - Get current metrics

## Frontend Flow

1. User selects between Manual and AI mode
2. **Manual Mode**: User chooses scale → starts practice
3. **AI Mode**:
   - AI analyzes history → shows recommendation
   - User accepts → session configured automatically
   - User rejects → returns to mode selection

## Testing AI Mode

1. Start with some manual sessions to build history:
```bash
# In the app, select Manual mode
# Practice 2-3 sessions with different scales
# Vary your performance intentionally
```

2. Switch to AI mode:
```bash
# Select AI Coach mode
# AI will analyze your sessions
# Review the recommendation
# Accept to start practice
```

3. Monitor the AI's reasoning:
```bash
# Check console for AI analysis output
# Review database for saved plans:
SELECT * FROM ai_practice_plans ORDER BY generated_at DESC LIMIT 5;
```

## Troubleshooting

### "FaiGoogle get AI recommendation"
- Check OpenAI API key in `.env`
- Verify database connection
- Check console for detailed errors

### "No practice history found"
- Complete at least 2-3 manual sessions first
- AI needs data to analyze

### SQL Query Errors
- Ensure schema is up to date
- Check PostgreSQL connection
- Verify table structure matches schema.sql

## Future Enhancements

- Multi-user support with user authentication
- Historical trend visualization
- Progressive difficulty adjustment
- Scale mastery tracking
- Custom practice plan templates
