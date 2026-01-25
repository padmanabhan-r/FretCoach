# FretCoach Hub - Web Analytics & AI Coach Dashboard

Post-practice analytics, performance tracking, and conversational AI coaching through an intuitive web interface.

![FretCoach Web Dashboard](assets/images/web-dashboard.jpg)

---

## Overview

**FretCoach Hub** ([fretcoach.online](https://www.fretcoach.online)) is the analytics and planning center of the FretCoach ecosystem. While FretCoach Studio and Portable focus on **real-time practice**, the Hub provides **post-session analysis, trend visualization, and conversational AI coaching**.

**Core Purpose:** Transform practice data into actionable insights and long-term improvement strategies.

---

## Philosophy: Data-Driven Practice Planning

### Traditional Practice Feedback Loop

```
Practice → Manual self-assessment → Vague next steps → Repeat
```

**Problems:**
- Subjective evaluation ("I think I'm getting better")
- No quantitative progress tracking
- Difficulty identifying specific weaknesses
- No historical trend analysis
- Generic practice advice

### FretCoach Hub Approach

```
Practice (Studio/Portable) → Automatic logging → Data analysis →
AI-powered insights → Personalized plan → Targeted practice → Progress tracking
```

**Advantages:**
- Objective metric tracking (pitch, scale, timing, noise)
- Historical trend visualization
- AI identifies patterns humans miss
- Personalized practice plans based on actual data
- Conversational interface for exploration

**Result:** Evidence-based practice planning that adapts to your actual performance, not your perception.

---

## Key Features

### 1. Performance Analytics Dashboard

**Visual trend analysis of all practice sessions**

![Web Dashboard Analytics](assets/images/web-dashboard.jpg)

#### Session History Table

**Displays:**
- Date and time of each session
- Duration (minutes:seconds)
- Scale practiced (e.g., "C Major", "A Minor Pentatonic")
- Final metric scores (pitch, scale, timing, noise)
- Overall quality percentage
- Notes played (total, correct, wrong)

**Features:**
- Sort by any column (date, duration, quality)
- Filter by date range
- Filter by scale
- Search sessions
- Pagination for long histories
- Export to CSV (planned)

**Use cases:**
- Review recent practice patterns
- Identify most/least practiced scales
- Track session duration trends
- Compare performance across different days/times

#### Performance Trend Charts

**Interactive visualizations powered by Recharts:**

**1. Metric Trends Over Time (Line Chart)**
- X-axis: Session date/time
- Y-axis: Percentage (0-100%)
- Four lines: Pitch, Scale, Timing, Noise
- Tooltips showing exact values
- Zoom and pan support

**Insights:**
- Which metric is improving fastest?
- Are improvements consistent or erratic?
- Did a break from practice cause decline?
- Which metric plateaued?

**2. Scale Distribution (Bar Chart)**
- X-axis: Scale names
- Y-axis: Number of sessions
- Color-coded by average quality
- Shows practice variety

**Insights:**
- Are you over-practicing familiar scales?
- Which scales need more attention?
- Correlation between scale and performance?

**3. Quality Score Distribution (Histogram)**
- X-axis: Quality score bins (0-30%, 30-50%, 50-70%, 70%+)
- Y-axis: Session count
- Color-coded by quality category

**Insights:**
- What's your typical performance level?
- Are you improving (distribution shifting right)?
- Consistency vs. variability

**4. Practice Volume Over Time (Area Chart)**
- X-axis: Week/Month
- Y-axis: Total practice time (minutes)
- Stacked area showing session counts

**Insights:**
- Am I practicing consistently?
- Seasonal patterns (more practice in winter?)
- Total time investment tracking

#### Summary Statistics

**Aggregate metrics across all sessions:**

```
┌─────────────────────────────────────────┐
│         Practice Statistics             │
├─────────────────────────────────────────┤
│ Total Sessions: 127                     │
│ Total Practice Time: 42h 15m            │
│ Average Session: 19m 58s                │
│                                         │
│ Average Metrics:                        │
│   Pitch Accuracy:    76.3%              │
│   Scale Conformity:  81.2%              │
│   Timing Stability:  58.7%              │
│   Noise Control:     79.5%              │
│                                         │
│ Most Practiced Scale: C Major (23x)     │
│ Best Performance: A Minor Pent (84.2%)  │
│ Weakest Area: Timing Stability          │
│                                         │
│ Total Notes Played: 31,472              │
│ Note Accuracy: 94.3%                    │
└─────────────────────────────────────────┘
```

**Use cases:**
- Quick performance overview
- Identify overall weakest metric
- Track total time investment
- Celebrate milestones (100th session!)

---

### 2. AI Chat Coach

**Conversational interface for practice guidance and data exploration**

![AI Coach Chat Interface](assets/images/web-dashboard.jpg)

#### Architecture: Hybrid Text-to-SQL Agent

**Not pure text-to-SQL generation** (error-prone, insecure)

**Instead: Intent-based tool selection**

```
User Question → Intent Detection → Predefined Query Function →
Database Results → LLM Formats Response → User
```

**Example flow:**

```
User: "What should I practice next?"
  ↓
Intent: "practice_recommendation"
  ↓
Query: get_user_practice_data(user_id) → avg metrics, recent sessions
  ↓
Function: generate_practice_recommendation(data)
  ↓
LLM (Gemini 2.5 Flash): Analyzes data, generates recommendation
  ↓
Response: "Your timing stability is your weakest area at 58%.
          I recommend practicing C Major Pentatonic with these exercises..."
  ↓
Chart Data: Practice plan card with "Save Plan" button
```

**Why this approach?**
- **Robust:** No risk of malformed SQL
- **Secure:** No SQL injection vulnerabilities
- **Fast:** Optimized queries, not LLM-generated
- **Natural:** Conversational interface maintained
- **Predictable:** Known query patterns

#### Supported Query Types

**1. Practice Recommendations**

**Trigger keywords:** "practice", "recommend", "suggest", "what should"

**Backend actions:**
- Fetch recent sessions and metrics
- Calculate weakest area
- Generate personalized practice plan
- Return recommendation with reasoning

**Example interaction:**
```
User: "What should I practice next?"

AI: "Based on your practice history, timing stability is your weakest
area at 58.7%. I recommend practicing C Major Pentatonic with these exercises:

• Practice slow scales focusing on hitting each note cleanly
• Use a metronome starting at a slow tempo (60 BPM)
• Focus on consistent note duration before increasing speed
• Practice in 5-minute focused intervals

I've created a practice plan below. Click 'Save Plan' to save it."
```

**Practice Plan Card displayed:**
- Focus area: Timing Stability
- Current score: 58.7%
- Suggested scale: C Major Pentatonic
- Exercises list
- "Save Plan" button → Creates entry in `ai_practice_plans` table

**2. Performance Trends**

**Trigger keywords:** "progress", "trend", "chart", "graph", "show me"

**Backend actions:**
- Query last 20 sessions
- Format as chart data
- LLM provides contextual commentary

**Example interaction:**
```
User: "Show me my progress trends"

AI: "Here's your performance trend over the last 20 sessions. Your pitch
accuracy has been consistently improving (76% → 85%), and scale conformity
remains strong. However, timing stability needs focused attention as it's
been fluctuating between 45-65%.

Recommendation: Dedicate 2-3 sessions specifically to timing exercises with
a metronome before practicing scales."

[Line chart appears showing all metrics over time]
```

**3. Session Comparisons**

**Trigger keywords:** "compare", "versus", "vs", "latest", "average"

**Backend actions:**
- Get latest session data
- Calculate historical averages
- Generate comparison chart

**Example interaction:**
```
User: "Compare my latest session to my average"

AI: "Your latest session (D Minor, 15m):
• Pitch: 82% (avg: 76%) → +6% above average ✓
• Scale: 79% (avg: 81%) → -2% below average
• Timing: 71% (avg: 59%) → +12% above average ✓
• Noise: 77% (avg: 80%) → -3% below average

Excellent timing improvement! This was your best timing session in the last
month. Keep practicing D Minor to solidify these gains."

[Bar chart comparing latest vs. average]
```

**4. Scale-Specific Analysis**

**Trigger keywords:** "scale", "which scales", "practiced"

**Backend actions:**
- Group sessions by scale
- Calculate per-scale averages
- Identify patterns

**Example interaction:**
```
User: "Which scales have I practiced?"

AI: "You've practiced 8 different scales across 127 sessions:

Top 3 by frequency:
1. C Major - 23 sessions (avg quality: 78%)
2. A Minor - 19 sessions (avg quality: 81%)
3. G Major Pentatonic - 15 sessions (avg quality: 74%)

Best performing: A Minor Pentatonic (84% avg)
Needs practice: E Minor (68% avg, only 6 sessions)

Recommendation: Your pentatonic scales perform better than natural scales
(81% vs 74%). This suggests timing might be easier with fewer notes. Try
practicing natural scales with slower tempos."
```

**5. Open-Ended Coaching**

**Trigger keywords:** General questions, technique advice

**Backend actions:**
- LLM uses practice data as context
- Provides coaching based on metrics
- May suggest specific tools/techniques

**Example interaction:**
```
User: "Why is my timing so inconsistent?"

AI: "Looking at your session data, I notice:

1. **Session length correlation:** Your timing scores are better in
   shorter sessions (15-20m) vs longer ones (30m+). This suggests
   fatigue impacts timing consistency.

2. **Scale complexity:** Natural scales show 15% lower timing scores
   than pentatonic scales, indicating more notes = harder timing control.

3. **Trend:** Your timing has improved from 45% (3 weeks ago) to 59%
   (current average), but with high variance (σ = 12%).

**Recommendations:**
• Practice in focused 15-minute blocks
• Start with pentatonic scales to build timing habits
• Use a metronome or backing track for rhythmic anchoring
• Track timing-specific exercises separately

Would you like me to create a timing-focused practice plan?"
```

#### LLM Configuration

**Primary model:** Google Gemini 2.5 Flash
- Fast inference (<2s typical)
- Free tier available
- Strong reasoning capabilities
- Context window: 1M tokens

**Fallback model:** MiniMax 2.1
- Used on Gemini rate limits
- Compatible API interface
- Automatic failover

**Prompt engineering:**

```python
system_prompt = f"""You are an AI guitar practice coach for FretCoach.

## User's Practice Data
- Total sessions: {total_sessions}
- Average pitch accuracy: {avg_pitch}%
- Average scale conformity: {avg_scale}%
- Average timing stability: {avg_timing}%
- Weakest area: {weakest_area}

Recent Sessions:
{format_recent_sessions(sessions)}

Provide personalized, data-driven coaching advice. Reference specific
metrics and patterns in your responses. Be encouraging but honest about
areas needing improvement."""
```

**Opik tracing:**
- All conversations logged
- Token usage tracked
- Latency monitoring
- Tag: `web-chat`

---

### 3. AI Practice Plan Generator

**Structured practice plan creation based on session history**

#### Access Points

**1. Via AI Chat:**
- User asks: "What should I practice next?"
- AI generates recommendation with reasoning
- Practice plan card displayed
- Click "Save Plan" → Stored in database

**2. Via Dashboard Button:**
- Click "Generate Practice Plan"
- Modal shows AI-generated recommendation
- Accept or regenerate
- Save to database

#### Plan Structure

```json
{
  "practice_id": "uuid-123",
  "user_id": "paddy",
  "generated_at": "2026-01-25T14:30:00Z",
  "scale_name": "C Major",
  "scale_type": "natural",
  "focus_area": "timing",
  "reasoning": "Your timing stability is 58% (weakest metric).
                Natural scales provide more notes for rhythm practice.",
  "suggested_strictness": 0.6,
  "suggested_sensitivity": 0.5,
  "exercises": [
    "Practice with metronome at 60 BPM",
    "Focus on even note spacing",
    "Use quarter notes before eighth notes",
    "Practice in 5-minute focused intervals"
  ],
  "status": "pending"  // "pending", "in_progress", "completed"
}
```

#### Plan Management

**Features:**
- View all practice plans (pending, in-progress, completed)
- Mark plans as "in-progress" when starting session
- Mark plans as "completed" after session
- Delete unused plans
- Regenerate plans

**Integration with Studio/Portable:**
- Desktop app fetches pending plans
- "AI Mode" uses latest plan
- Session completion marks plan as "completed"
- Feedback loop: plan → practice → results → next plan

---

### 4. Session Detail View

**Deep dive into individual practice sessions**

**Access:** Click any session in history table

**Displays:**
- Full session metadata (start, end, duration)
- Scale configuration
- Final metric scores with labels
- Note statistics (total, correct, wrong, unique)
- Scale coverage percentage
- Quality score trend during session (if available)
- AI coaching feedback received during session (if available)

**Actions:**
- Delete session
- Export session data (JSON/CSV)
- Compare with other sessions
- Add session notes (planned)

**Use cases:**
- Review specific practice session
- Understand what worked/didn't work
- Identify outlier sessions (unusually good/bad)
- Prepare for lessons (show instructor data)

---

## Technical Implementation

### Frontend Stack

**Framework:** React 18 + TypeScript
**Build Tool:** Vite 4
**Styling:** Tailwind CSS 3
**UI Components:** shadcn/ui + Radix UI
**Charts:** Recharts 2
**State Management:** TanStack React Query + Zustand
**Routing:** React Router v6
**HTTP Client:** Axios

**Key libraries:**
- `@tanstack/react-query` — Server state management, caching
- `recharts` — Declarative charts (line, bar, area, pie)
- `lucide-react` — Icon library
- `date-fns` — Date formatting and manipulation
- `tailwindcss` — Utility-first CSS
- `shadcn/ui` — Pre-built accessible components

**Deployment:** Vercel
- Automatic deployments from `main` branch
- Edge network CDN
- Environment variable management
- Domain: [fretcoach.online](https://www.fretcoach.online)

### Backend Stack

**Framework:** Python FastAPI
**AI Orchestration:** LangChain + LangGraph
**LLM Providers:** Google Gemini 2.5 Flash, MiniMax 2.1
**Database:** PostgreSQL (Supabase)
**Observability:** Comet Opik
**HTTP Server:** Uvicorn (ASGI)

**Key libraries:**
- `fastapi` — Async web framework
- `langchain` — LLM orchestration
- `langchain-google-genai` — Gemini integration
- `psycopg2` — PostgreSQL driver
- `opik` — LLM tracing and monitoring
- `pydantic` — Data validation and structured outputs

**Deployment:** Render / Railway
- Automatic deployments
- PostgreSQL connection pooling
- Environment variable management
- Health checks and auto-restart

### API Endpoints

**Session Management:**
```
GET  /api/sessions?user_id={id}           # List all sessions
GET  /api/sessions/{session_id}           # Get session details
POST /api/sessions                        # Create session (from Studio/Portable)
DELETE /api/sessions/{session_id}         # Delete session
```

**Analytics:**
```
GET  /api/analytics/summary?user_id={id}  # Summary statistics
GET  /api/analytics/trends?user_id={id}   # Trend data for charts
GET  /api/analytics/scales?user_id={id}   # Per-scale analysis
```

**AI Coach:**
```
POST /api/chat                            # Send message to AI coach
GET  /api/chat/history?thread_id={id}     # Get conversation history
POST /api/chat/clear                      # Clear conversation
```

**Practice Plans:**
```
GET  /api/practice-plans?user_id={id}     # List all plans
POST /api/practice-plans                  # Generate new plan
PUT  /api/practice-plans/{id}             # Update plan status
DELETE /api/practice-plans/{id}           # Delete plan
```

**Health:**
```
GET  /health                              # Service health check
GET  /api/config                          # Frontend configuration
```

### Database Schema

**Sessions Table:** `fretcoach.sessions`

```sql
CREATE TABLE fretcoach.sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    start_timestamp TIMESTAMP NOT NULL,
    end_timestamp TIMESTAMP,
    duration_seconds INTEGER,
    scale_chosen VARCHAR(100),
    scale_type VARCHAR(50),  -- "natural" or "pentatonic"
    sensitivity FLOAT,
    strictness FLOAT,
    pitch_accuracy FLOAT,
    scale_conformity FLOAT,
    timing_stability FLOAT,
    noise_control FLOAT,
    quality_score FLOAT,
    total_notes_played INTEGER,
    correct_notes INTEGER,
    wrong_notes INTEGER,
    unique_notes_used INTEGER,
    ambient_enabled BOOLEAN DEFAULT FALSE,
    practice_mode VARCHAR(50),  -- "manual" or "ai"
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sessions_user_id ON fretcoach.sessions(user_id);
CREATE INDEX idx_sessions_start_time ON fretcoach.sessions(start_timestamp DESC);
```

**Practice Plans Table:** `fretcoach.ai_practice_plans`

```sql
CREATE TABLE fretcoach.ai_practice_plans (
    practice_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    generated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    practice_plan JSONB NOT NULL,  -- Full plan structure
    status VARCHAR(50) DEFAULT 'pending',  -- "pending", "in_progress", "completed"
    session_id UUID REFERENCES fretcoach.sessions(session_id),  -- Link to completed session
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_practice_plans_user_id ON fretcoach.ai_practice_plans(user_id);
CREATE INDEX idx_practice_plans_status ON fretcoach.ai_practice_plans(status);
```

**See:** [Architecture Documentation](architecture.md) for complete schema.

---

## User Interface Components

### Dashboard Layout

```
┌─────────────────────────────────────────────────────────┐
│  Header: FretCoach Hub | User Menu | Settings           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────┬──────────────────────────────────────┐  │
│  │ Sidebar   │  Main Content Area                   │  │
│  │           │                                      │  │
│  │ • Home    │  📊 Performance Summary              │  │
│  │ • Sessions│                                      │  │
│  │ • AI Coach│  [Total Sessions] [Practice Time]   │  │
│  │ • Plans   │  [Avg Metrics]    [Best Scale]      │  │
│  │ • Profile │                                      │  │
│  │           │  📈 Metric Trends Chart              │  │
│  │           │  ═══════════════════════════════════ │  │
│  │           │                                      │  │
│  │           │  📋 Recent Sessions Table            │  │
│  │           │  ┌────┬──────┬───────┬────────────┐ │  │
│  │           │  │Date│Scale │Quality│Metrics     │ │  │
│  │           │  ├────┼──────┼───────┼────────────┤ │  │
│  │           │  │... │ ...  │  ...  │ ...        │ │  │
│  │           │  └────┴──────┴───────┴────────────┘ │  │
│  └───────────┴──────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### AI Coach Interface

```
┌─────────────────────────────────────────────────────────┐
│  🤖 AI Practice Coach                                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Conversation History                           │   │
│  │                                                 │   │
│  │  👤 User: What should I practice next?         │   │
│  │                                                 │   │
│  │  🤖 AI: Based on your practice history,        │   │
│  │      timing stability is your weakest area...  │   │
│  │                                                 │   │
│  │      ┌─────────────────────────────────────┐   │   │
│  │      │  📋 Practice Plan                   │   │   │
│  │      │  Focus: Timing Stability            │   │   │
│  │      │  Scale: C Major Pentatonic          │   │   │
│  │      │  Exercises: [...]                   │   │   │
│  │      │  [Save Plan]                        │   │   │
│  │      └─────────────────────────────────────┘   │   │
│  │                                                 │   │
│  │  👤 User: Show me my progress trends           │   │
│  │                                                 │   │
│  │  🤖 AI: Here's your performance over time...   │   │
│  │                                                 │   │
│  │      [Line Chart: Metrics Over Time]           │   │
│  │                                                 │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Your question here...                    [Send] │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Development Setup

### Prerequisites

- Node.js 18+
- Python 3.10+
- PostgreSQL (or Supabase account)
- OpenAI or Google API key

### Frontend Setup

```bash
cd web/web-frontend
npm install
npm run dev  # http://localhost:5173
```

**Environment variables** (`.env`):
```bash
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

### Backend Setup

```bash
cd web/web-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure .env
cp .env.example .env
# Edit .env with your credentials

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Environment variables** (`.env`):
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/fretcoach

# LLM Providers
GOOGLE_API_KEY=your_gemini_api_key
MINIMAX_API_KEY=your_minimax_api_key

# Observability
OPIK_API_KEY=your_opik_key
OPIK_WORKSPACE=your_workspace

# Application
USER_ID=paddy  # Default user ID for testing
```

**See:** [Environment Setup Guide](environment-setup.md) for detailed configuration.

---

## Best Practices

### For Users

**Regular review:**
- Check dashboard weekly to track progress
- Identify metric trends (improving/declining)
- Adjust practice focus based on data

**Use AI coach actively:**
- Ask specific questions about your data
- Request practice recommendations
- Compare sessions to understand patterns

**Save practice plans:**
- Generate plans from web dashboard
- Use in Studio/Portable AI Mode
- Mark as completed after sessions

**Export data:**
- Backup session history periodically
- Share data with instructors
- Analyze in external tools (Excel, Python)

### For Developers

**Frontend:**
- Use React Query for all API calls (caching, optimistic updates)
- Keep components small and focused
- Use TypeScript for type safety
- Follow shadcn/ui patterns for consistency

**Backend:**
- Keep database queries in separate service modules
- Use Pydantic models for all API responses
- Enable Opik tracing for all LLM calls
- Handle rate limits gracefully (fallback models)

**Database:**
- Index user_id and timestamp columns
- Use prepared statements (prevent SQL injection)
- Implement pagination for large result sets
- Regular backups (Supabase handles this)

---

## Future Enhancements

**Planned features:**

- **Social features:**
  - Leaderboards (optional opt-in)
  - Share session achievements
  - Challenge friends

- **Advanced analytics:**
  - Skill forecasting (predict when you'll reach goals)
  - Practice schedule optimization
  - Correlation analysis (best time of day, session length, etc.)

- **Integration:**
  - Export to DAWs (Ableton, Logic Pro)
  - Import backing tracks for practice
  - Spotify integration (practice to favorite songs)

- **Instructor mode:**
  - Teacher can view student dashboards
  - Assign practice plans to students
  - Track student progress over time

- **Mobile app:**
  - iOS/Android companion app
  - Push notifications for practice reminders
  - Quick session logging

---

## Troubleshooting

### Dashboard Not Loading Sessions

**Symptom:** Empty session table, no data

**Solutions:**
1. Check user_id in URL matches database records
2. Verify database connection (check backend logs)
3. Check browser console for API errors
4. Ensure backend is running and accessible
5. Check CORS settings if frontend/backend on different domains

### AI Coach Not Responding

**Symptom:** Spinner indefinitely, no response

**Solutions:**
1. Verify API keys in backend `.env` (Gemini/MiniMax)
2. Check API rate limits (switch to different provider)
3. Review backend logs for LLM errors
4. Check Opik traces for failure points
5. Ensure database connection (needed for context)

### Charts Not Displaying

**Symptom:** Empty chart area, no visualization

**Solutions:**
1. Check browser console for Recharts errors
2. Verify API returns valid chart data format
3. Ensure at least 2 sessions exist (needed for trends)
4. Check window size (responsive layout issues)
5. Clear browser cache

### Slow Performance

**Symptom:** Dashboard lags, slow page loads

**Solutions:**
1. Check network tab (slow API responses?)
2. Optimize database queries (add indexes)
3. Enable React Query caching
4. Reduce chart data points (pagination)
5. Check backend server resources (CPU/memory)

---

## Observability and Monitoring

### Comet Opik Integration

**All AI interactions traced:**
- Chat conversations
- Practice plan generation
- LLM model used
- Input/output tokens
- Latency (response time)
- Success/failure status

**Dashboard:** [Opik Project](https://comet.com/opik)

**Useful filters:**
- `tag:web-chat` — All web dashboard AI interactions
- `metadata.user_id:paddy` — Specific user traces
- `tag:practice-plan` — Practice plan generations

**Metrics monitored:**
- Average response latency
- Token usage (cost tracking)
- Error rates by provider
- Popular query types

**See:** [Opik Observability Guide](opik-observability.md) for details.

---

## Deployment

### Frontend (Vercel)

**Repository:** Connected to GitHub repo
**Build command:** `cd web/web-frontend && npm run build`
**Output directory:** `web/web-frontend/dist`
**Environment variables:** Set in Vercel dashboard

**Automatic deployments:**
- Push to `main` → Production deployment
- Pull requests → Preview deployments
- Domain: [fretcoach.online](https://www.fretcoach.online)

### Backend (Render / Railway)

**Repository:** Connected to GitHub repo
**Start command:** `cd web/web-backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
**Environment variables:** Set in Render/Railway dashboard

**Automatic deployments:**
- Push to `main` → Production deployment
- Health check: `GET /health`
- Auto-restart on failure

**Database:** Supabase (managed PostgreSQL)
- Connection pooling enabled
- Automatic backups
- Point-in-time recovery

---

## Conclusion

**FretCoach Hub transforms practice data into actionable improvement strategies.** By combining quantitative analytics with conversational AI coaching, the web dashboard closes the loop from practice → data → insights → improvement.

**Key innovations:**
- **Objective progress tracking:** No more guessing if you're improving
- **AI-powered insights:** Patterns humans miss, recommendations based on real data
- **Conversational interface:** Natural language data exploration
- **Cross-device continuity:** Practice on Studio/Portable, analyze on web
- **Evidence-based planning:** Practice plans driven by actual performance metrics

**Philosophy:** Guitar mastery requires not just practice, but **smart practice**. FretCoach Hub ensures every session contributes to measurable, data-driven improvement.

---

**Navigation:**
- [← Portable Application](portable-app.md)
- [AI Coach Agent Engine →](ai-coach-agent-engine.md)
- [Architecture Overview](architecture.md)
- [Back to Index](index.md)
