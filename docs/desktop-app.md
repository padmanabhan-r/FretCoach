# Desktop Application

The desktop application is your primary training environment — a standalone Electron app with integrated Python backend for real-time audio analysis and AI coaching.

![FretCoach Studio Home Page](assets/images/studio/1.%20Studio%20-%20Home%20Page.png)

---

## Overview

**Architecture:**
- Electron + React frontend
- Python + FastAPI backend
- WebSocket for real-time metrics
- USB audio interface recommended

Personal practice studio with AI coach analyzing every note.

> **For detailed architecture:** See [System Architecture](architecture.md)

---

## Key Features

### 1. Real-Time Audio Analysis

The backend processes audio in overlapping 800ms windows and streams four metrics via WebSocket:

- **Pitch Accuracy** — Intonation against detected notes
- **Scale Conformity** — Notes within scale + fretboard coverage
- **Timing Stability** — Consistency of note spacing
- **Noise Control** — Signal clarity

Metrics update every ~300ms with exponential smoothing for stable display.

> **Deep dive:** [Audio Analysis Agent Engine](audio-analysis-agent-engine.md)

---

### 2. Dual Practice Modes

![Mode Selection](assets/images/studio/2.%20Studio%20-%20Mode%20Selection.png)

#### Manual Mode

Choose your scale, sensitivity, strictness, and metric toggles.

**Flow:** Select Scale → Adjust Settings → Start → Play → End

![Scale Selection](assets/images/studio/3.%20Studio%20-%20Manual%20Mode%20-%20Scale%20Selection.png)

#### AI Mode

System analyzes previous sessions, identifies weakest area, and recommends a practice plan.

**Flow:** Request Recommendation → Review → Accept → Start → Play → End

![AI Recommendations](assets/images/studio/8.%20Studio%20-%20AI%20Coach%20Rec.png)

Uses GPT-4o-mini or Gemini. All recommendations traced in Opik.

> **Details:** [AI Coach Agent Engine](ai-coach-agent-engine.md)

---

### 3. Live AI Coaching

Every 30 seconds (configurable), the AI coach provides spoken + visual feedback:

- *"Your timing is drifting—lock in with the beat."*
- *"Pitch accuracy is solid—focus on reducing string noise."*

**How it works:**
- Frontend sends metrics → Backend identifies weakness
- GPT-4o-mini generates feedback → GPT-4o-mini-TTS converts to speech
- Feedback spoken aloud + displayed in Live Coach panel

---

### 4. Metric Customization

Toggle individual metrics on/off based on practice focus.

**Configurable:**
- ✅ Pitch Accuracy
- ✅ Scale Conformity
- ✅ Timing Stability
- 🔒 Noise Control (always enabled)

**When disabled:**
- Not calculated, stored, or displayed
- AI coach ignores it in feedback
- Overall score recalculated from enabled metrics only

Preferences persist across sessions.

---

### 5. Visual Feedback

![Live Session](assets/images/studio/9.%20Studio%20-%20Live%20Session.png)

**Display:**
```
┌──────────────────────────────┐
│  Pitch Accuracy      78%  🟢 │
│  Scale Conformity    45%  🟡 │
│  Timing Stability    23%  🔴 │
│  Noise Control       82%  🟢 │
└──────────────────────────────┘

Overall: 57%
Notes: 142 (138 correct, 4 wrong)
```

**Color legend:**
- 🟢 Green: 70%+ (Excellent)
- 🟡 Yellow-Green: 50-70% (Good)
- 🟠 Yellow: 30-50% (Average)
- 🔴 Red: <30% (Needs Work)

---

### 6. Ambient Lighting

Optional Tuya smart bulb integration for subconscious feedback.

**How it works:**
- Bulb color reflects overall quality score
- Green (70%+) → Yellow (50-70%) → Orange (30-50%) → Red (<30%)
- Peripheral vision processes color without breaking focus

> **Setup:** [Environment Setup](environment-setup.md#smart-bulb-setup-optional)

---

### 7. Session Logging

Every session automatically saved to PostgreSQL:
- Start/end timestamps
- Final metric scores
- Note statistics
- Scale and settings used

---

## Configuration

### Sensitivity (0.0 - 1.0)

Controls note detection threshold.

- **Low (0.2):** Only loud notes. Good for noisy environments.
- **Medium (0.5):** Balanced. Recommended.
- **High (0.8):** Detects quiet notes. Good for fingerstyle.

### Strictness (0.0 - 1.0)

Controls wrong note penalties.

- **Low (0.2):** Forgiving. Good for beginners.
- **Medium (0.5):** Balanced.
- **High (0.8):** Strict. Wrong notes instantly drop score to 0.

---

## Installation

### Prerequisites

- Node.js 18+ and npm
- Python 3.12+
- Audio interface (USB recommended)
- PostgreSQL database (Supabase)

### Quick Setup

```bash
# Install dependencies (from project root)
uv sync

# Frontend
cd application
npm install
npm run dev
```

> **Full setup:** [Quickstart Guide](quickstart.md)

---

## Development

**Terminal 1 (Backend):**
```bash
cd backend
uv run uvicorn backend.api.server:app --reload
```

**Terminal 2 (Frontend):**
```bash
cd application
npm run dev
```

### Building

```bash
cd application
npm run build
npm run package  # Creates bundled app in release/
```

---

## Troubleshooting

**Audio device not detected:**
- Grant microphone permissions (macOS: System Settings → Privacy)
- Try different USB port

**Backend not starting:**
- Check port 8000 is free: `lsof -i :8000`
- Reinstall: `cd backend && uv sync`

**AI features not working:**
- Verify API keys in `.env`
- Check API credits/quota

**Poor audio quality:**
- Use USB interface instead of built-in mic
- Adjust input gain
- Increase sensitivity setting

---

**Navigation:**
- [← Quickstart Guide](quickstart.md)
- [Portable Application →](portable-app.md)
- [Back to Index](index.md)
