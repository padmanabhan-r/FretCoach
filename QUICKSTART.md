# FretCoach - Quick Start Guide

## Setup

### 1. Install Python Dependencies

```bash
cd /Users/paddy/Documents/Github/FretCoach
pip install fastapi uvicorn websockets
# or if using uv:
uv pip install fastapi uvicorn websockets
```

### 2. Install Node Dependencies

```bash
cd application
npm install
```

## Running the Application

### Start the Desktop App

```bash
cd application
npm run dev
```

This will:
1. Start the Vite dev server (React UI)
2. Launch the Electron app
3. The Electron app will automatically start the FastAPI backend

## Application Flow

### 1. Audio Setup
- Select your audio input device (guitar interface)
- Choose the guitar channel
- Test the audio to ensure signal is detected

### 2. Scale Selection
- Browse and select from major or minor scales
- Search for specific scales

### 3. Practice Session
- Start the session to begin real-time feedback
- The app displays:
  - Current note being played
  - Pitch accuracy score
  - Scale conformity score
  - Timing stability score
  - Visual feedback circle that changes color based on performance

## API Endpoints

The FastAPI backend runs on `http://127.0.0.1:8000`

- `GET /audio/devices` - List available audio devices
- `POST /audio/test/{device_index}` - Test audio device
- `GET /scales` - List available scales
- `POST /config` - Save configuration
- `GET /config` - Get current configuration
- `POST /session/start` - Start practice session
- `POST /session/stop` - Stop practice session
- `GET /session/metrics` - Get current metrics
- `WS /ws/metrics` - WebSocket for real-time metrics updates

## Troubleshooting

### Backend won't start
- Make sure FastAPI dependencies are installed
- Check console output in Electron DevTools

### No audio devices shown
- Ensure your audio interface is connected
- Try restarting the application

### WebSocket connection fails
- Wait 2-3 seconds after starting for backend to fully initialize
- Check that port 8000 is not in use by another application
