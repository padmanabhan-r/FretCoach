# Desktop Application

The desktop application is your primary training environment—a standalone Electron app with integrated Python backend for real-time audio analysis and AI coaching.

![FretCoach Studio Home Page](assets/images/studio/1.%20Studio%20-%20Home%20Page.png)

---

## Overview

Architecture:
- **Electron + React** — User interface
- **Python + FastAPI** — Audio processing and AI
- **WebSocket** — Real-time metric streaming
- **USB audio interface** — Professional-grade input

Personal practice studio with AI coach analyzing every note.

---

> **Architecture:** See [System Architecture](architecture.md) for detailed desktop app architecture and technical diagrams.

---

## Key Features

### 1. Real-Time Audio Analysis

**How it works:**

The backend continuously processes audio in overlapping windows (0.8 seconds by default) and calculates four metrics:

- **Pitch Accuracy** — Evaluates intonation against detected notes
- **Scale Conformity** — Checks if notes are within the chosen scale
- **Timing Stability** — Measures consistency of note spacing
- **Noise Control** — Assesses signal clarity

Metrics stream to the frontend via WebSocket at ~300ms intervals for live display.

**Technical details:**
- Audio sampling: 44100 Hz (CD quality)
- Analysis window: 800ms with 50% overlap
- Frequency detection: librosa `piptrack` (YIN algorithm)
- Onset detection: Coefficient of variation on recent intervals

**See:** [Audio Analysis Agent Engine](audio-analysis-agent-engine.md) for deep dive.

### 2. Dual Practice Modes

![Mode Selection](assets/images/studio/2.%20Studio%20-%20Mode%20Selection.png)

#### Manual Mode

**Use case:** Targeted practice on specific scales

**User controls:**
- Scale selection (24 options across 12 keys)
- Scale type (natural/pentatonic)
- **Metric toggles** (enable/disable pitch, scale conformity, timing)
- Sensitivity (how quiet a note can be detected)
- Strictness (how harshly wrong notes are penalized)
- Ambient lighting (on/off)

**Metric Customization:**
- Toggle individual metrics on/off based on practice focus
- Disabled metrics are not calculated, stored, or shown in UI
- AI coach adapts feedback to only enabled metrics
- Overall score recalculated from active metrics only
- Preferences persist across sessions

**Flow:**
```
Select Scale → Adjust Settings → Start Session → Play → Get Feedback → End Session
```

**Scale Selection:**

![Scale Selection](assets/images/studio/3.%20Studio%20-%20Manual%20Mode%20-%20Scale%20Selection.png)

**Scale Type Selection:**

![Scale Type](assets/images/studio/4.%20Studio%20-%20Manual%20Mode%20-%20Scale%20Type.png)

**Practice Settings:**

![Practice Settings](assets/images/studio/5.%20Studio%20-%20Manual%20Mode%20-%20Practice%20Settings.png)

#### AI Mode

**Use case:** Adaptive learning with personalized recommendations

**How it works:**
1. System analyzes your last 5 practice sessions from the database
2. AI identifies your weakest performance area (pitch, scale, or timing)
3. Recommends a specific scale, scale type, and difficulty settings
4. Provides reasoning for the recommendation
5. User can customize metric toggles and ambient lighting before accepting
6. User accepts or requests a new recommendation

**Flow:**
```
Request Recommendation → Review AI Suggestion → Accept → Start Session → Play → End Session
```

**AI Coach Analyzing Session History:**

![Coach Analyzing](assets/images/studio/6.%20Studio%20-%20Coach%20Analysing.png)

**AI Recommendations:**

![AI Recommendations](assets/images/studio/8.%20Studio%20-%20AI%20Coach%20Rec.png)

The AI uses OpenAI GPT-4o-mini or Google Gemini to analyze patterns and generate recommendations. Every recommendation is traced in Comet Opik.

**See:** [AI Coach Agent Engine](ai-coach-agent-engine.md) for details.

### 3. Live AI Coach Feedback

During active practice sessions, the AI coach provides real-time feedback both visually and vocally:

**Example feedback:**
- *"Your timing is drifting—lock in with the beat."*
- *"Pitch accuracy is solid—focus on reducing string noise."*
- *"You're playing outside the scale. Review the note positions."*

**How it works:**
- Every 30 seconds (configurable), frontend sends current metrics to backend
- Backend identifies the weakest metric
- LLM (GPT-4o-mini) generates specific, actionable coaching instruction
- Text-to-speech (GPT-4o-mini-TTS) converts feedback to spoken audio
- Feedback is both **spoken aloud** and **displayed** in the "Live Coach" panel
- All interactions traced in Opik

**Feedback intervals:**
- Configurable: 30 seconds, 1 minute, 2 minutes, or 5 minutes
- Adapts commentary to only enabled metrics

**System prompt** (excerpt):
```
You are a direct, practical guitar coach analyzing real-time playing data.

Your feedback must be:
- CORRECTIVE: Address the actual problem shown in the metrics
- SPECIFIC: Reference the exact metric that needs work
- ACTIONABLE: Give one concrete technique to try RIGHT NOW
- BRIEF: 1-2 sentences maximum
```

### 4. Metric Customization (Toggling)

**Use case:** Focus practice on specific areas by disabling irrelevant metrics

**Available in both modes:**
- Manual Mode: Configure during scale settings step
- AI Mode: Customize before accepting AI recommendation

**Configurable metrics:**
- ✅ **Pitch Accuracy** — Optional (can be toggled)
- ✅ **Scale Conformity** — Optional (can be toggled)
- ✅ **Timing Stability** — Optional (can be toggled)
- 🔒 **Noise Control** — Always enabled (mandatory baseline)

**What happens when a metric is disabled:**
- **Not calculated** — No CPU cycles spent on disabled metric
- **Not stored** — Database stores `NULL` instead of values
- **Not displayed** — UI hides disabled metrics completely
- **Not in AI feedback** — Coach only mentions enabled metrics
- **Weight redistribution** — Overall score recalculated from enabled metrics only

**Weight Distribution Algorithm:**
```python
# When pitch is enabled:
pitch_weight = 0.40 + (strictness * 0.15)  # 40-55% based on strictness
remaining_weight = 1.0 - pitch_weight
other_weight = remaining_weight / (num_enabled - 1)  # Split among others

# When pitch is disabled:
equal_weight = 1.0 / num_enabled  # Equal split among enabled
```

**Example scenarios:**
1. **Focus on rhythm only:**
   - Enable: Timing Stability only
   - Disable: Pitch Accuracy, Scale Conformity
   - Result: 50% timing, 50% noise (equal split)

2. **Ignore timing for slow practice:**
   - Enable: Pitch Accuracy, Scale Conformity
   - Disable: Timing Stability
   - Result: 40-55% pitch, remainder split between scale and noise

3. **All metrics (default):**
   - Enable: All metrics
   - Result: 40-55% pitch, remainder split among scale, timing, and noise

**Persistence:**
- Preferences saved to `backend/core/session_config.json`
- Global setting across all future sessions
- Can be changed anytime during scale/AI recommendation setup

### 5. Visual Feedback System

Real-time metrics displayed with color-coded performance indicators:

![Live Session](assets/images/studio/9.%20Studio%20-%20Live%20Session.png)

**Metric Display:**
```
┌──────────────────────────────┐
│  Pitch Accuracy      78%  🟢 │  ← Excellent (70%+)
│  Scale Conformity    45%  🟡 │  ← Average (30-50%)
│  Timing Stability    23%  🔴 │  ← Needs Work (<30%)
│  Noise Control       82%  🟢 │  ← Excellent (70%+)
└──────────────────────────────┘

Overall Quality: 57% (Good)
Current Note: In Scale
Notes Played: 142 (138 correct, 4 wrong)
```

**Color legend:**
- 🟢 Green: 70%+ (Excellent)
- 🟡 Yellow-Green: 50-70% (Good)
- 🟠 Yellow: 30-50% (Average)
- 🔴 Red: <30% (Needs Work)

**Performance smoothing:**
- Exponential moving average (EMA) prevents jittery UI
- Alpha value adjusts based on strictness setting
- Wrong notes cause instant score drops in high strictness mode

### 6. Ambient Lighting Control

Optional integration with Tuya smart bulbs for subconscious feedback:

**How it works:**
- Smart bulb color reflects overall quality score in real-time
- Green (quality 70%+) → Yellow (50-70%) → Orange (30-50%) → Red (<30%)
- Color updates throttled to every 300ms to prevent flickering
- Brightness increases with quality (300-1000 scale)

**Why lighting matters:**
- Peripheral vision processes color changes faster than conscious thought
- Creates subconscious association: good technique = green light = positive feedback
- Doesn't interrupt focus—no need to look at screen constantly
- Engages additional neural pathways for faster motor learning

**Configuration:**
- Requires Tuya developer credentials in `.env`
- Toggle on/off per session in UI
- Automatically turns on at session start, off at session end

**See:** [Environment Setup](environment-setup.md#smart-bulb-setup-tuya) for Tuya configuration.

### 7. Session Logging and Summary

Every practice session is automatically saved to the PostgreSQL database:

**Captured data:**
- Start/end timestamps and total duration
- Scale chosen and settings used (sensitivity, strictness)
- Final metric scores (pitch, scale conformity, timing, noise)
- Note statistics (total played, correct, wrong)
- Unique notes used (coverage metric)
- User ID for cross-device sync

At the end of each session, a summary screen displays the performance metrics and provides actionable feedback.

**Database table:** `fretcoach.sessions`

**See:** [Database Schema](index.md#database-schema) for table structure.

---

## User Interface Components

### Header
- App branding and logo
- Current mode indicator (Manual/AI)
- Settings button

### Status Panel
- Session state (Not Started, Running, Paused, Completed)
- Elapsed time display
- Start/Pause/Resume/Stop controls

### Visual Feedback
- Large central display showing overall quality score
- Color-coded circle visualization
- Current note detection

### Metrics Display
- Four individual metric bars with percentages
- Performance labels (Excellent/Good/Average/Needs Work)
- Real-time updates during session

### Control Panel
- Scale selection dropdown
- Sensitivity slider (0.0 - 1.0)
- Strictness slider (0.0 - 1.0)
- Ambient lighting toggle
- Mode switcher (Manual/AI)

### AI Recommendation Panel (AI Mode)
- Recommended scale display
- AI reasoning explanation
- Accept/Reject buttons
- "Generate New" button

### Live Coach Feedback
- Real-time AI feedback messages (spoken and displayed)
- Audio playback of TTS-generated coaching
- Timestamp for each message
- Scrollable history of feedback during session

### Console Output (Optional)
- Backend logs for debugging
- Audio device status
- Error messages

### Debug Panel (Optional)
- Raw audio data (Hz, MIDI, pitch class)
- Note counts and coverage
- Detailed metric breakdowns

---

## Technical Implementation

### Frontend (React + Vite)

**Entry point:** `application/src/main.jsx`

**Key components:**
- `App.jsx` — Main application logic and state
- `StatusPanel.jsx` — Session controls
- `MetricsDisplay.jsx` — Real-time metric visualization
- `AIRecommendation.jsx` — AI mode interface
- `LiveCoachFeedback.jsx` — AI coaching display
- `VisualFeedback.jsx` — Central quality visualization

**API communication:** `application/src/api.js`
```javascript
export const api = {
  // Configuration
  getConfig: () => fetch('/config').then(r => r.json()),
  saveConfig: (config) => fetch('/config', {method: 'POST', ...}),
  
  // Session control
  startSession: (config) => fetch('/session/start', {method: 'POST', ...}),
  endSession: () => fetch('/session/end', {method: 'POST', ...}),
  
  // AI features
  startAISession: () => fetch('/ai/start-session', ...),
  getLiveCoachFeedback: (metrics) => fetch('/live-coach/feedback', ...),
}
```

**WebSocket handling:**
```javascript
const ws = new WebSocket('ws://127.0.0.1:8000/ws/metrics');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  setState({
    pitchAccuracy: data.pitch_accuracy,
    scaleConformity: data.scale_conformity,
    timingStability: data.timing_stability,
    currentNote: data.current_note,
    // ...
  });
};
```

### Backend (Python + FastAPI)

**Entry point:** `backend/api/server.py`

**Router modules:**
- `devices.py` — Audio device enumeration
- `config.py` — Configuration management
- `session.py` — Session start/end/state
- `metrics.py` — WebSocket metric streaming
- `scales.py` — Scale library endpoints
- `ai_mode.py` — AI recommendation generation
- `live_coach.py` — Real-time coaching feedback

**Service modules:**
- `audio_processor.py` — Audio analysis orchestration
- `ai_agent_service.py` — Practice plan generation
- `live_coach_service.py` — Coaching feedback generation
- `device_service.py` — Audio device management
- `session_service.py` — Database session operations

**Core audio modules:**
- `audio_features.py` — DSP metric calculations
- `audio_metrics.py` — Quality score computation
- `audio_setup.py` — Audio device initialization
- `scales.py` — Scale definitions
- `smart_bulb.py` — Tuya API integration

**See:** [Audio Analysis Agent Engine](audio-analysis-agent-engine.md) for implementation details.

### Electron Integration

**Main process:** `application/electron/main.js`

Responsibilities:
- Create application window
- Spawn Python backend subprocess
- Manage IPC between frontend and backend
- Handle app lifecycle (quit, close)

**Preload script:** `application/electron/preload.js`

Exposes safe APIs to renderer:
```javascript
contextBridge.exposeInMainWorld('electronAPI', {
  onPythonOutput: (callback) => ipcRenderer.on('python-output', callback),
  onPythonError: (callback) => ipcRenderer.on('python-error', callback),
});
```

---

## Configuration Options

### Sensitivity (0.0 - 1.0)

Controls the energy threshold for note detection.

- **Low (0.2):** Only loud, clear notes trigger analysis. Good for noisy environments.
- **Medium (0.5):** Balanced. Recommended default.
- **High (0.8):** Even quiet notes are analyzed. Good for fingerstyle or clean environments.

**Formula:** `energy_threshold = 1e-7 * (1 + sensitivity * 10)`

### Strictness (0.0 - 1.0)

Controls how harshly wrong notes are penalized and how quality scores are updated.

- **Low (0.2):** Forgiving. Gradual quality changes. Good for beginners.
- **Medium (0.5):** Balanced. Wrong notes reduce score significantly but don't zero it.
- **High (0.8):** Strict. Wrong notes instantly drop quality to 0. Good for advanced players enforcing precision.

**Effects:**
- **EMA alpha:** `0.10 + (strictness * 0.30)` — Controls smoothing speed
- **Wrong note penalty:** At strictness 0.7+, wrong notes immediately set quality to 0
- **Pitch weight:** `0.40 + (strictness * 0.15)` — Increases pitch importance

### Ambient Lighting

Toggle smart bulb control on/off for each session.

**Requirements:**
- Tuya smart bulb (tested with RGB bulbs)
- Tuya developer account and API credentials
- Device ID and region code

**See:** [Environment Setup](environment-setup.md) for complete setup instructions.

---

## Installation and Setup

### Prerequisites

- **Node.js 18+** and npm
- **Python 3.10+**
- **Audio input device** (USB interface recommended)
- **PostgreSQL database** (Supabase or self-hosted)

### Quick Setup

```bash
# Backend
cd backend
uv sync

# Create .env (see environment-setup.md)
cp .env.example .env

# Start backend
uv run uvicorn backend.api.server:app --reload --host 127.0.0.1 --port 8000

# Frontend (new terminal)
cd application
npm install
npm run dev
```

**See:** [Quickstart Guide](quickstart.md) for detailed setup.

---

## Development

### Running in Development Mode

**Terminal 1 (Backend):**
```bash
cd backend
uv run uvicorn backend.api.server:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd application
npm run dev
```

Electron will launch automatically with hot reload enabled.

### Building for Production

```bash
cd application

# Build frontend
npm run build

# Package for your platform
npm run package        # Current platform
npm run package:mac    # macOS
npm run package:win    # Windows
npm run package:linux  # Linux
```

Output: `application/release/`

**Note:** The Python backend is bundled with the Electron app during packaging.

---

## Troubleshooting

### Audio Device Not Detected

**Symptom:** "No audio devices found" error

**Solutions:**
1. Check device is connected and recognized by OS
2. On macOS: Grant microphone permissions to Terminal/Electron
3. Restart audio service: `sudo killall coreaudiod` (macOS)
4. Try different USB port

### Backend Not Starting

**Symptom:** Frontend shows "Connecting to backend..."

**Solutions:**
1. Check backend logs in console output panel
2. Check port 8000 is not in use: `lsof -i :8000`
3. Reinstall dependencies: `cd backend && uv sync`

### WebSocket Connection Failed

**Symptom:** Metrics not updating in real-time

**Solutions:**
1. Check backend is running on correct host/port
2. Verify no firewall blocking WebSocket connections
3. Check browser/Electron console for WebSocket errors
4. Restart both backend and frontend

### AI Features Not Working

**Symptom:** No AI recommendations or live feedback

**Solutions:**
1. Verify API keys in `.env` (OpenAI or Gemini)
2. Check API key has sufficient credits
3. Review backend logs for API errors
4. Test API connection separately

### Poor Audio Quality

**Symptom:** Erratic note detection, low metric scores

**Solutions:**
1. Use USB audio interface instead of built-in mic
2. Adjust input gain on audio interface
3. Minimize background noise
4. Increase sensitivity setting
5. Ensure guitar is properly tuned

---

## Best Practices

### For Beginners

1. **Start with Manual Mode** to understand the metrics
2. **Use low strictness** (0.2-0.4) for forgiveness
3. **Choose familiar scales** (C Major, A Minor)
4. **Practice slowly** — timing matters more than speed
5. **Review session summaries** to identify patterns

### For Intermediate Players

1. **Switch to AI Mode** for adaptive challenges
2. **Increase strictness** (0.5-0.7) to enforce precision
3. **Practice multiple scales** to improve coverage
4. **Listen to live vocal coaching** during sessions for real-time corrections
5. **Track progress** in the web dashboard

### For Advanced Players

1. **Use high strictness** (0.7+) for rigorous training
2. **Enable ambient lighting** for subconscious training
3. **Analyze debug metrics** to optimize technique
4. **Set personal goals** (e.g., 80%+ on all metrics)
5. **Practice sight-reading** with random AI recommendations

---

## Future Enhancements

Planned features for future releases:

- **Custom scale creation** — Define your own scales beyond the library
- **Tempo/metronome integration** — Practice with a click track
- **Recording and playback** — Review your sessions aurally
- **Multi-guitar support** — Practice with multiple instruments
- **Social features** — Leaderboards and challenges
- **Advanced analytics** — Trend predictions and skill forecasting

---

**Navigation:**
- [← Quickstart Guide](quickstart.md)
- [Portable Application →](portable-app.md)
- [Back to Index](index.md)
