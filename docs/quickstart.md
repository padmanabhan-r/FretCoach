# Quickstart Guide

Get FretCoach up and running in 5 minutes.

---

## Prerequisites

Before starting, ensure you have:

- **Python 3.10+** installed
- **Node.js 18+** and npm installed
- A **guitar and audio input** (USB interface like Focusrite Scarlett, or built-in microphone)
- **PostgreSQL database** (Supabase recommended for cloud sync)
- **API keys:**
  - OpenAI API key (for AI coaching)
  - Google Gemini API key (optional, alternative to OpenAI)
  - Tuya smart bulb credentials (optional, for ambient lighting)

---

## Desktop Application Setup

The desktop app is your primary practice interface. Get it running locally:

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/FretCoach.git
cd FretCoach
```

### 2. Set Up Backend Environment

```bash
cd backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create `backend/.env` with database, AI keys, and optional services.

> **Complete setup guide:** [environment-setup.md](environment-setup.md)

**Quick template:**
```bash
DB_HOST=your_supabase_host.supabase.co
DB_USER=postgres
DB_PASSWORD=your_password
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
TUYA_CLIENT_ID=...  # Optional
```

### 4. Set Up Database

Run the schema creation script:

```bash
# From the backend directory
psql -h your_host -U postgres -d postgres -f sql/fretcoach_supabase_schema.sql
```

Or if using Supabase, copy the contents of `sql/fretcoach_supabase_schema.sql` and run it in the Supabase SQL editor.

### 5. Start Backend Server

```bash
# From backend directory, with venv activated
uvicorn backend.api.server:app --reload --host 127.0.0.1 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

Keep this terminal open.

### 6. Start Desktop Frontend

Open a new terminal:

```bash
cd application
npm install
npm run dev
```

The Electron app will launch automatically. You should see the FretCoach launch animation.

---

## First Practice Session

### 1. Audio Device Setup

When the app launches, you'll be prompted to select your audio input:
- **USB Audio Interface:** Select your device (e.g., "Scarlett Solo USB")
- **Built-in Microphone:** Select "Built-in Microphone" (works but lower quality)

**Tip:** USB audio interfaces provide much better quality and lower latency.

### 2. Choose Practice Mode

**Manual Mode:**
- You select the scale, sensitivity, and strictness
- Good for targeted practice on specific scales
- Full control over difficulty

**AI Mode:**
- The AI analyzes your history and recommends what to practice
- Adaptive difficulty based on your performance
- Best for guided improvement

For your first session, try **Manual Mode** to get familiar with the interface.

### 3. Select a Scale

Choose from the scale library:
- **C Major Diatonic** — Good starting point (C-D-E-F-G-A-B)
- **A Minor Pentatonic** — Popular for rock/blues (A-C-D-E-G)
- Any of 24 scales across all keys

### 4. Adjust Settings

**Sensitivity** (0.0 - 1.0):
- Low (0.2): Only loud, clear notes trigger analysis
- Medium (0.5): Balanced
- High (0.8): Even quiet notes are analyzed

**Strictness** (0.0 - 1.0):
- Low (0.2): Forgiving of mistakes, gradual score changes
- Medium (0.5): Balanced
- High (0.8): Harsh penalties for wrong notes, instant score drops

**Ambient Lighting:**
- Toggle on to sync with a smart bulb
- Requires Tuya credentials in `.env`

### 5. Start Playing

Click **Start Session** and begin playing the scale. You'll immediately see:
- Real-time metrics updating (pitch, scale conformity, timing, noise)
- Current note detection
- Performance quality score (0-100)
- Live AI coach feedback (appears after a few seconds)

### 6. End Session

Click **Stop Session** when finished. You'll see:
- Session summary with final metrics
- Total notes played (correct vs. wrong)
- Practice duration
- Performance assessment (Excellent, Good, Average, or Needs Work)

The session is automatically saved to the database.

---

## Web Dashboard Setup (Optional)

The web dashboard lets you review sessions, chat with the AI coach, and generate practice plans.

### 1. Set Up Backend

```bash
cd web/server

# Install dependencies
pip install -r requirements.txt

# Create .env (same credentials as desktop backend)
cp ../../backend/.env .env
```

### 2. Start Backend

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Set Up Frontend

Open a new terminal:

```bash
cd web
npm install

# Create .env for frontend
echo "VITE_API_URL=http://localhost:8000" > .env
```

### 4. Start Frontend

```bash
npm run dev
```

Visit http://localhost:5173 in your browser.

### 5. Explore the Dashboard

**Dashboard Tab:**
- Recent sessions list
- Performance metrics
- Session comparison charts

**AI Coach Tab:**
- Chat interface for discussing your progress
- Ask questions like:
  - "What should I practice next?"
  - "Why is my timing score low?"
  - "Show me my progress over the last week"
- Get personalized practice plan recommendations

---

## Quick Tips

### Audio Quality

- USB audio interface (Focusrite Scarlett, PreSonus)
- Direct guitar connection (not through amp)
- Input gain at -12dB peak
- Minimize background noise

### Understanding Metrics

**Pitch Accuracy (0-100%):**
- How cleanly you're fretting notes
- Low score = poor intonation, pressing too hard/soft

**Scale Conformity (0-100%):**
- Whether you're playing notes within the chosen scale
- Low score = playing wrong notes, hitting chromatic notes

**Timing Stability (0-100%):**
- Consistency of note spacing
- Low score = rushing, dragging, uneven rhythm

**Noise Control (0-100%):**
- Clarity of playing
- Low score = string buzz, fret noise, unwanted harmonics

### AI Feedback

Three modes:
- **Real-time:** Analyzes metrics during execution
- **Corrective:** Specific techniques to apply immediately
- **Post-session:** Performance summary

Focus one metric at a time. Timing weakness? Prioritize timing before other metrics.

### Adjusting Difficulty

Start with:
- **Sensitivity:** 0.5 (medium)
- **Strictness:** 0.3 (forgiving)

As you improve:
- Increase sensitivity to detect quieter playing
- Increase strictness to enforce higher standards

---

## Troubleshooting

### Backend Won't Start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`  
**Fix:** Activate virtual environment and reinstall dependencies:
```bash
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
```

### No Audio Input Detected

**Error:** "No audio devices found"  
**Fix:** 
- Ensure audio interface is connected
- Check system sound settings
- On macOS: Grant microphone permissions to Terminal/Electron

### Database Connection Failed

**Error:** `Connection refused` or `could not connect to server`  
**Fix:** 
- Verify database credentials in `.env`
- Check database is running and accessible
- Test connection: `psql -h your_host -U postgres -d postgres`

### AI Coach Not Responding

**Error:** No AI feedback appearing  
**Fix:** 
- Verify OpenAI or Gemini API key in `.env`
- Check API key has sufficient credits
- Review backend logs for API errors

### Smart Bulb Not Working

**Error:** Bulb doesn't change color  
**Fix:** 
- Verify Tuya credentials in `.env`
- Check bulb is online and reachable
- Test Tuya API connection separately
- Ambient lighting is optional—FretCoach works without it

---

## Next Steps

Now that you have FretCoach running:

→ **[Desktop Application Guide](desktop-app.md)** — Deep dive into all features
→ **[AI Coach Agent Engine](ai-coach-agent-engine.md)** — Learn how AI recommendations work
→ **[Audio Analysis Agent Engine](audio-analysis-agent-engine.md)** — Learn how real-time audio analysis works
→ **[Environment Setup](environment-setup.md)** — Complete configuration guide

---

## Common Workflows

### Daily Practice Routine

1. Launch desktop app
2. Select **AI Mode** for adaptive recommendations
3. Practice the recommended scale for 10-15 minutes
4. Review session summary
5. Check web dashboard for progress trends

### Targeted Skill Building

1. Launch desktop app
2. Select **Manual Mode**
3. Choose a specific scale you want to master
4. Set **high strictness** (0.7+) for rigorous training
5. Practice until you consistently hit 70%+ quality score
6. Move to the next scale

### Pre-Performance Warmup

1. Use **Portable Device** if backstage (or desktop if at home)
2. Select **Manual Mode**
3. Choose a familiar scale as warmup
4. Set **medium sensitivity** and **low strictness** for confidence building
5. Play for 5-10 minutes to get fingers warmed up

---

**Navigation:**
- [← Introduction](introduction.md)
- [Desktop Application →](desktop-app.md)
