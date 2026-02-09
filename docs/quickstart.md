# Quickstart Guide

Get FretCoach up and running in 5 minutes.

---

## Prerequisites

Before starting, ensure you have:

- **Python 3.12+** installed
- **Node.js 18+** and npm installed
- A **guitar and audio input** (USB interface recommended, or built-in microphone)
- **PostgreSQL database** (Supabase recommended for cloud sync)
- **API keys:**
  - [OpenAI API key](https://platform.openai.com/api-keys) (for AI coaching and TTS)
  - [Google Gemini API key](https://aistudio.google.com/app/apikey) (for practice plans and web AI coach)
  - [Opik API key](https://www.comet.com/site/products/opik/) (optional, for LLM observability)
  - Tuya smart bulb credentials (optional, for ambient lighting)

---

## Desktop Application Setup

The desktop app is your primary practice interface.

### 1. Clone the Repository

```bash
git clone https://github.com/padmanabhan-r/FretCoach.git
cd FretCoach
```

### 2. Set Up Backend Environment

```bash
uv sync  # Install dependencies with uv (run from project root)
```

> **Note:** If you don't have `uv` installed, get it from [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/)

### 3. Configure Environment Variables

Create a `backend/.env` file with your database credentials and API keys.

> **Complete setup guide:** See [environment-setup.md](environment-setup.md) for detailed configuration instructions.

**Minimal template:**
```bash
# Database (Supabase)
DB_HOST=your_supabase_host.supabase.co
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=postgres
DB_PORT=5432

# AI Services
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
GEMINI_MODEL=gemini-3-flash-preview
```

### 4. Set Up Database

Run the schema creation script:

```bash
psql -h your_host -U postgres -d postgres -f sql/fretcoach_supabase_schema.sql
```

Or copy the contents of `sql/fretcoach_supabase_schema.sql` and run it in the Supabase SQL editor.

### 5. Start Desktop Application

```bash
cd application
npm install
npm run dev
```

The Electron app will launch both the backend and frontend automatically.

> **Detailed guide:** See [desktop-app.md](desktop-app.md) for comprehensive documentation.

---

## First Practice Session

### 1. Configure Audio Device

When the app launches, select your audio input device (USB interface recommended for best quality).

### 2. Choose Practice Mode

- **Manual Mode:** You select the scale, sensitivity, and strictness
- **AI Mode:** AI analyzes your history and recommends what to practice

### 3. Start Playing

Click **Start Session** and begin playing. You'll see real-time metrics updating.

### 4. End Session

Click **Stop Session** when finished. The session is automatically saved to the database.

> **Detailed guide:** See [desktop-app.md](desktop-app.md) for complete feature documentation.

---

## Portable Application Setup

The portable version runs on Raspberry Pi or any computer (terminal-based interface).

### Prerequisites

Ensure the backend dependencies are installed (from Desktop Application Setup, step 2).

### Start the Application

```bash
cd portable
./start.sh  # Launches the terminal-based application
```

Follow the on-screen instructions to configure audio, select practice mode, and start your session.

> **Detailed guide:** See [portable-app.md](portable-app.md) for hardware setup and comprehensive documentation.

---

## Web Dashboard Setup

The web dashboard lets you review sessions, chat with the AI coach, and generate practice plans.

### 1. Ensure Backend Dependencies

Ensure backend dependencies are installed (from step 2 above - `uv sync` at project root).

### 2. Configure Environment

```bash
cd web/web-backend
cp ../../backend/.env .env  # Use same credentials as desktop backend
```

### 3. Set Up Frontend

```bash
cd ../web-frontend
npm install
echo "VITE_API_BASE_URL=http://localhost:8000" > .env
```

### 4. Start Web Dashboard

From the `web` directory, use the start script to launch both backend and frontend:

```bash
cd ..  # Now in web/ directory
./start.sh
```

Visit http://localhost:8080 in your browser.

> **Detailed guide:** See [web-dashboard.md](web-dashboard.md) for comprehensive documentation.

---

## Quick Tips

### Audio Quality

- Use USB audio interface (Focusrite Scarlett, PreSonus) for best results
- Direct guitar connection (not through amp)
- Input gain at -12dB peak
- Minimize background noise

### Getting Started

- **Beginners:** Start with Manual Mode, low strictness (0.2-0.4), familiar scales (C Major, A Minor)
- **Intermediate:** Switch to AI Mode for adaptive challenges, increase strictness (0.5-0.7)
- **Advanced:** Use high strictness (0.7+), enable ambient lighting for subconscious training

### Understanding Metrics

- **Pitch Accuracy:** How cleanly you're fretting notes
- **Scale Conformity:** Whether you're playing notes within the chosen scale and covering as much of the fretboard as possible
- **Timing Stability:** Consistency of note spacing
- **Noise Control:** Clarity of playing (string buzz, fret noise)

---

## Troubleshooting

- **Backend won't start:** Ensure dependencies are installed with `uv sync` from the project root
- **No audio detected:** Check device connection and microphone permissions in system settings
- **Database connection failed:** Verify Supabase credentials in `.env` file
- **AI coach not responding:** Check API keys are valid and account has sufficient credits
- **Smart bulb not working:** Verify Tuya credentials in `.env` (optional feature)

> **For detailed troubleshooting:** See [Troubleshooting Guide](troubleshooting.md) for comprehensive solutions.

---

## Next Steps

Once you're up and running:

1. **Practice regularly** with the desktop app or portable device
2. **Review your progress** on the web dashboard
3. **Chat with AI coach** for personalized recommendations
4. **Generate practice plans** based on your performance data

**Learn more:**
- [Desktop Application Guide](desktop-app.md) - Comprehensive Studio documentation
- [Portable Application Guide](portable-app.md) - Raspberry Pi setup and usage
- [Web Dashboard Guide](web-dashboard.md) - Analytics and AI coaching
- [Environment Setup](environment-setup.md) - Detailed configuration instructions
- [Architecture Overview](architecture.md) - System design and technical details

---

**Navigation:**
- [← Introduction](introduction.md)
- [Desktop Application →](desktop-app.md)
