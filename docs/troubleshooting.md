# Troubleshooting Guide

Comprehensive solutions to common issues across all FretCoach components.

---

## Table of Contents

- [Backend Issues](#backend-issues)
- [Audio & Hardware Issues](#audio--hardware-issues)
- [Database Issues](#database-issues)
- [AI & API Issues](#ai--api-issues)
- [Frontend & UI Issues](#frontend--ui-issues)
- [Smart Bulb Issues](#smart-bulb-issues)
- [Platform-Specific Issues](#platform-specific-issues)
- [Performance Issues](#performance-issues)

---

## Backend Issues

### Backend Won't Start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Cause:** Dependencies not installed

**Solutions:**
```bash
# Ensure you're in the project root
cd /path/to/FretCoach

# Install/reinstall dependencies
cd backend
uv sync
```

---

### Port Already in Use

**Error:** `ERROR: [Errno 48] Address already in use`

**Cause:** Port 8000 is occupied by another process

**Solutions:**

**Option 1 - Kill the process:**
```bash
# Find process using port 8000
lsof -ti:8000 | xargs kill -9  # macOS/Linux
# OR
netstat -ano | findstr :8000  # Windows (note the PID, then kill it)
```

**Option 2 - Use different port:**
```bash
uv run uvicorn backend.api.server:app --reload --host 127.0.0.1 --port 8001
```

---

### Module Import Errors

**Error:** `ModuleNotFoundError: No module named 'backend'`

**Cause:** Running uvicorn from wrong directory

**Solution:**
```bash
# MUST run from project root, not from backend/ directory
cd /path/to/FretCoach  # Project root
uv run uvicorn backend.api.server:app --reload --host 127.0.0.1 --port 8000
```

---

### Python Version Mismatch

**Error:** `SyntaxError: invalid syntax` or version-related errors

**Cause:** Python version below 3.12

**Solution:**
```bash
# Check Python version
python --version  # Should be 3.12+

# If wrong version, install Python 3.12+
# macOS (using Homebrew)
brew install python@3.12

# Ubuntu/Debian
sudo apt update
sudo apt install python3.12

# Install dependencies with uv (automatically uses correct Python version)
cd backend
uv sync
```

---

## Audio & Hardware Issues

### No Audio Devices Found

**Error:** "No audio devices found" or empty device list

**Cause:** Audio interface not connected or permissions not granted

**Solutions:**

**Step 1 - Check connection:**
- Ensure USB audio interface is plugged in
- Check device appears in system sound settings
- Try different USB port

**Step 2 - Grant permissions (macOS):**
```bash
# If running from Terminal
System Preferences → Security & Privacy → Privacy → Microphone
Enable: Terminal

# If running Electron app
Enable: Electron or FretCoach
```

**Step 3 - Test audio device:**
```bash
# List available audio devices
uv run python -c "import sounddevice as sd; print(sd.query_devices())"
```

**Step 4 - Linux specific:**
```bash
# Install PortAudio
sudo apt-get install portaudio19-dev python3-pyaudio

# Check ALSA devices
arecord -l
```

---

### High Audio Latency

**Symptom:** Delayed feedback, metrics lag behind playing

**Causes & Solutions:**

**1. Built-in microphone (high latency):**
- **Solution:** Use USB audio interface (Focusrite Scarlett Solo recommended)
- Built-in mics: ~50-100ms latency
- USB interfaces: ~10-20ms latency

**2. Buffer size too large:**
- **Solution:** Adjust buffer size in backend settings
- Smaller buffer = lower latency but higher CPU usage

**3. System audio settings:**
- **macOS:** Reduce sample rate in Audio MIDI Setup
- **Windows:** Disable audio enhancements in Sound settings

---

### Audio Crackling or Dropouts

**Symptom:** Distorted audio, missing notes, choppy playback

**Causes & Solutions:**

**1. USB power issues:**
- Use powered USB hub
- Connect directly to computer (not through hub)

**2. Sample rate mismatch:**
```bash
# Check device sample rate
# Should match backend config (typically 44100 Hz)
```

**3. CPU overload:**
- Close other applications
- Reduce AI coaching frequency
- Disable ambient lighting temporarily

---

### Input Gain Too Low/High

**Symptom:** Notes not detected or constant noise triggering

**Solutions:**

**Too low (notes not detected):**
- Increase input gain on audio interface
- Target: -12dB peak level
- Increase sensitivity in FretCoach settings

**Too high (noise triggering):**
- Decrease input gain on audio interface
- Lower sensitivity in FretCoach settings
- Check for electrical interference

---

## Database Issues

### Connection Refused

**Error:** `psycopg2.OperationalError: could not connect to server`

**Cause:** Database not running or wrong credentials

**Solutions:**

**Step 1 - Verify credentials:**
```bash
# Check .env file
cat backend/.env | grep DB_

# Should show:
# DB_HOST=your_host.supabase.co
# DB_PORT=5432
# DB_USER=postgres
# DB_PASSWORD=your_password
```

**Step 2 - Test connection:**
```bash
# Using psql
psql -h your_host.supabase.co -U postgres -d postgres

# Using Python
uv run python -c "import psycopg2; conn = psycopg2.connect(host='your_host', user='postgres', password='your_pass'); print('Connected!')"
```

**Step 3 - Check Supabase status:**
- Login to [supabase.com](https://supabase.com)
- Verify project is active and not paused
- Check database health in dashboard

---

### SSL/TLS Errors

**Error:** `SSL error: certificate verify failed`

**Cause:** Missing SSL mode in connection string

**Solution:**
```env
# Add to .env
DB_SSLMODE=require
```

---

### Schema/Table Not Found

**Error:** `relation "sessions" does not exist`

**Cause:** Database schema not initialized

**Solution:**
```bash
# Run schema creation script
cd backend
psql -h your_host -U postgres -d postgres -f sql/fretcoach_supabase_schema.sql

# OR copy/paste contents into Supabase SQL Editor
```

---

### Session Write Failures

**Error:** Database insert fails but session continues

**Cause:** Missing columns or schema mismatch

**Solutions:**

**1. Check schema version:**
```sql
-- Run in Supabase SQL Editor
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'sessions';
```

**2. Update schema:**
```bash
# Re-run schema creation (safe, uses CREATE IF NOT EXISTS)
psql -h your_host -U postgres -d postgres -f sql/fretcoach_supabase_schema.sql
```

---

## AI & API Issues

### OpenAI API Key Invalid

**Error:** `openai.error.AuthenticationError: Incorrect API key`

**Solutions:**

**1. Verify key format:**
```bash
# New format (project-based)
OPENAI_API_KEY=sk-proj-...

# Old format (deprecated)
OPENAI_API_KEY=sk-...
```

**2. Regenerate key:**
- Visit [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- Create new key
- Update `.env` file
- Restart backend

**3. Check billing:**
- Ensure billing is enabled
- Verify payment method is valid
- Check usage limits not exceeded

---

### Gemini API Quota Exceeded

**Error:** `google.generativeai.types.generation_types.BlockedPromptException`

**Cause:** Free tier limits exceeded

**Solutions:**

**Free tier limits:**
- 15 requests/minute
- 1500 requests/day

**Reduce usage:**
- Use AI Practice Mode less frequently
- Disable live coaching temporarily
- Switch to OpenAI for coaching

**Upgrade:**
- Visit [aistudio.google.com](https://aistudio.google.com)
- Upgrade to paid tier for higher limits

---

### AI Coach Not Responding

**Symptom:** No vocal feedback during session

**Diagnostic Steps:**

**1. Check backend logs:**
```bash
# Look for error messages in terminal where backend is running
# Common errors: API key invalid, quota exceeded, network timeout
```

**2. Verify API keys:**
```bash
cat backend/.env | grep API_KEY
# Should show valid OpenAI and Google API keys
```

**3. Test API directly:**
```bash
# Test OpenAI
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Test Gemini
curl "https://generativelanguage.googleapis.com/v1/models?key=$GOOGLE_API_KEY"
```

**4. Check network:**
- Firewall blocking API requests
- Corporate proxy interfering
- VPN causing connection issues

---

### Opik Tracing Not Working

**Symptom:** No traces appearing in Opik dashboard

**Solutions:**

**1. Verify credentials:**
```bash
cat backend/.env | grep OPIK
# Should show:
# OPIK_API_KEY=...
# OPIK_WORKSPACE=...
```

**2. Check Opik status:**
- Login to [comet.com](https://www.comet.com)
- Verify workspace exists
- Check API key is active

**3. Network issues:**
```bash
# Test Opik connectivity
curl https://api.opik.io/v1/health
```

**Note:** Opik is optional - AI features work without it

---

## Frontend & UI Issues

### Electron App Won't Launch

**Error:** App window doesn't appear or crashes immediately

**Solutions:**

**1. Check Node.js version:**
```bash
node --version  # Should be 18+
npm --version
```

**2. Rebuild dependencies:**
```bash
cd application
rm -rf node_modules package-lock.json
npm install
npm run dev
```

**3. Clear Electron cache:**
```bash
# macOS
rm -rf ~/Library/Application\ Support/fretcoach

# Linux
rm -rf ~/.config/fretcoach

# Windows
del %APPDATA%\fretcoach
```

---

### Web Dashboard Not Loading

**Error:** Blank page or connection refused at localhost:5173

**Diagnostic Steps:**

**1. Check backend is running:**
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy"}
```

**2. Verify frontend .env:**
```bash
cat web/web-frontend/.env
# Should show:
# VITE_API_BASE_URL=http://localhost:8000
```

**3. Check for port conflicts:**
```bash
lsof -ti:5173 | xargs kill -9  # Kill process on 5173
npm run dev  # Restart
```

**4. Browser console errors:**
- Open DevTools (F12)
- Check Console tab for errors
- Common: CORS errors, API connection failures

---

### WebSocket Connection Failures

**Symptom:** Real-time metrics not updating during session

**Causes & Solutions:**

**1. Backend not running:**
- Ensure backend is running with `uv run uvicorn`
- Check for error messages in backend terminal

**2. Port mismatch:**
```javascript
// Check frontend WebSocket URL
// Should match backend port (default 8000)
ws://localhost:8000/ws
```

**3. Firewall blocking:**
- Allow WebSocket connections through firewall
- Check antivirus not blocking

---

### Metrics Not Displaying

**Symptom:** Zeros or no data in metric cards

**Causes & Solutions:**

**1. No audio input:**
- Check audio device selected
- Verify input gain not zero
- Play some notes to trigger analysis

**2. All metrics disabled:**
- At least one metric must be enabled
- Noise control is always enabled
- Check metric toggles in settings

**3. WebSocket disconnected:**
- Check browser console for WS errors
- Restart session

---

## Smart Bulb Issues

### Bulb Not Responding

**Symptom:** Smart bulb doesn't change color during practice

**Diagnostic Steps:**

**1. Verify Tuya credentials:**
```bash
cat backend/.env | grep TUYA
# Should show:
# TUYA_CLIENT_ID=...
# TUYA_CLIENT_SECRET=...
# TUYA_DEVICE_ID=...
# TUYA_REGION=us
```

**2. Check bulb online status:**
- Open Tuya Smart app
- Verify bulb is online and responsive
- Test manual color change in app

**3. Verify device ID:**
- Tuya Smart app → Device → Settings → Device Information
- Copy exact device ID to `.env`

**4. Test API access:**
```bash
# Use Tuya API Explorer at iot.tuya.com
# Test device control commands
```

**5. Region mismatch:**
```env
# Ensure region matches your account
TUYA_REGION=us  # or eu, cn, in
```

---

### Bulb Color Incorrect

**Symptom:** Bulb changes color but not matching performance

**Cause:** Color mapping misconfigured or bulb doesn't support HSV

**Solutions:**

**1. Check bulb capabilities:**
- Some bulbs only support RGB, not HSV
- Verify bulb model supports color temperature control

**2. Calibrate colors:**
- Test each color level manually
- Check backend color mapping logic

---

## Platform-Specific Issues

### macOS

**Microphone Permission Denied:**
```
System Preferences → Security & Privacy → Privacy → Microphone
Enable: Terminal and/or Electron
```

**Rosetta 2 (Apple Silicon):**
```bash
# uv automatically handles architecture - no special configuration needed
```

**Audio MIDI Setup:**
- Open Audio MIDI Setup app
- Ensure sample rate is 44100 Hz
- Disable any aggregate devices causing conflicts

---

### Linux

**PortAudio Installation:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install portaudio19-dev python3-pyaudio libasound2-dev

# Fedora
sudo dnf install portaudio-devel

# Arch
sudo pacman -S portaudio
```

**ALSA Permissions:**
```bash
# Add user to audio group
sudo usermod -a -G audio $USER
# Logout and login again
```

**PulseAudio Issues:**
```bash
# Restart PulseAudio
pulseaudio --kill
pulseaudio --start
```

---

### Windows

**Python Installation:**
- Download from [python.org](https://www.python.org/downloads/)
- Check "Add Python to PATH" during installation
- Use Python 3.12+ installer

**Running commands with uv:**
```cmd
# No virtual environment activation needed with uv
cd backend
uv run <command>
```

**Long Path Support:**
```cmd
# Enable long paths (requires admin)
reg add HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1
```

---

## Performance Issues

### High CPU Usage

**Symptom:** System slowdown during practice sessions

**Causes & Solutions:**

**1. Too frequent AI coaching:**
- Increase coaching interval (30s → 1min or more)
- Disable live coaching temporarily

**2. Multiple audio processes:**
- Close other audio applications
- Stop Opik tracing (optional feature)

**3. Background processes:**
- Check Activity Monitor/Task Manager
- Close unnecessary applications

---

### High Memory Usage

**Symptom:** Memory consumption increasing over time

**Causes & Solutions:**

**1. Memory leak in session:**
- Restart backend periodically
- End long sessions and start fresh

**2. Large session history:**
- Archive old sessions in database
- Clear browser cache for web dashboard

---

### Slow Database Queries

**Symptom:** Delays when loading sessions or generating plans

**Solutions:**

**1. Add indexes:**
```sql
-- Run in Supabase SQL Editor
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
```

**2. Limit query results:**
- Web dashboard: Only load recent sessions
- Archive old data periodically

---

## Still Having Issues?

If your problem isn't covered here:

1. **Check backend logs** for detailed error messages
2. **Review environment variables** in `.env` files
3. **Test components individually** (database, API, audio)
4. **Create GitHub issue** at [github.com/padmanabhan-r/FretCoach/issues](https://github.com/padmanabhan-r/FretCoach/issues)

Include:
- Error message (full stack trace)
- Operating system and version
- Python and Node.js versions
- Steps to reproduce

---

**Navigation:**
- [← Quickstart Guide](quickstart.md)
- [Environment Setup →](environment-setup.md)
