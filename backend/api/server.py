"""
FastAPI server for FretCoach
Provides REST API endpoints for the Electron app to communicate with the Python backend
Endpoints only - business logic is in separate modules
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import sounddevice as sd
import asyncio
import json
import sys
import os
import queue
import threading
import numpy as np
from collections import deque

# Import Opik for tracking (non-blocking)
try:
    from opik import track
    OPIK_ENABLED = True
    print("✅ Opik tracking enabled")
except ImportError:
    # Fallback decorator if opik is not installed
    def track(name):
        def decorator(func):
            return func
        return decorator
    OPIK_ENABLED = False
    print("⚠️  Opik not installed, tracking disabled")

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))

from scales import MAJOR_DIATONIC, MINOR_DIATONIC
from session_logger import get_session_logger

# Import from local modules
from models import AudioDevice, AudioConfig, SessionMetrics
from app_state import session_state, audio_state, AUDIO_CONSTANTS
from audio_processing import audio_callback, process_audio

app = FastAPI(title="FretCoach API")

# Enable CORS for Electron app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """API root endpoint"""
    return {"message": "FretCoach API", "version": "0.1.0"}

@app.get("/audio/devices", response_model=List[AudioDevice])
async def get_audio_devices():
    """Get list of available audio devices"""
    devices = sd.query_devices()
    device_list = []
    
    for i, device in enumerate(devices):
        if isinstance(device, dict):
            device_list.append(AudioDevice(
                index=i,
                name=device['name'],
                max_input_channels=device['max_input_channels'],
                max_output_channels=device['max_output_channels'],
                default_samplerate=device['default_samplerate']
            ))
    
    return device_list


@app.post("/audio/test/{device_index}")
async def test_audio_device(device_index: int, channel: int = 0):
    """Test audio input from a specific device and channel"""
    try:
        # Get device info to determine number of channels
        device_info = sd.query_devices(device_index)
        num_channels = int(device_info['max_input_channels'])
        
        if channel >= num_channels:
            return {
                "success": False,
                "error": f"Channel {channel} not available. Device has {num_channels} channels."
            }
        
        # Record a short sample to test
        duration = 2  # seconds
        sample_rate = 44100
        
        # Use a queue to get the result from the recording thread
        result_queue = queue.Queue()
        
        def record():
            try:
                # Record all channels from the device
                recording = sd.rec(
                    int(duration * sample_rate),
                    samplerate=sample_rate,
                    channels=num_channels,
                    device=device_index,
                    blocking=True
                )
                
                # Extract the specific channel
                if num_channels > 1:
                    channel_data = recording[:, channel]
                else:
                    channel_data = recording.flatten()
                
                # Calculate RMS to check if there's signal
                rms = float(np.sqrt(np.mean(channel_data**2)))
                peak = float(np.max(np.abs(channel_data)))
                
                # More lenient threshold for guitar signals
                result_queue.put({
                    "success": True,
                    "rms_level": rms,
                    "peak_level": peak,
                    "has_signal": rms > 0.001 or peak > 0.01
                })
            except Exception as e:
                result_queue.put({
                    "success": False,
                    "error": str(e)
                })
        
        # Run recording in a thread
        thread = threading.Thread(target=record)
        thread.start()
        thread.join(timeout=duration + 1)
        
        # Get result
        if not result_queue.empty():
            return result_queue.get()
        else:
            return {
                "success": False,
                "error": "Recording timed out"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/scales")
async def get_scales():
    """Get list of available musical scales grouped by type"""
    return {
        "major": sorted(MAJOR_DIATONIC.keys()),
        "minor": sorted(MINOR_DIATONIC.keys())
    }


# ============================================================================
# CONFIGURATION ENDPOINTS
# ============================================================================

@app.post("/config")
async def save_config(config: AudioConfig):
    """Save audio and scale configuration"""
    session_state["config"] = config.model_dump()
    
    # Save to file for persistence
    config_file = os.path.join(os.path.dirname(__file__), '..', 'core', 'audio_config.json')
    try:
        with open(config_file, 'w') as f:
            json.dump(session_state["config"], f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save config to file: {e}")
    
    return {"success": True, "config": session_state["config"]}


@app.get("/config")
async def get_config():
    """Get current configuration"""
    if session_state["config"]:
        return session_state["config"]
    
    # Try to load from file
    config_file = os.path.join(os.path.dirname(__file__), '..', 'core', 'audio_config.json')
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            session_state["config"] = json.load(f)
            return session_state["config"]
    
    return None


# ============================================================================
# SESSION ENDPOINTS
# ============================================================================

@app.post("/session/start")
@track(name="start_practice_session")
async def start_session():
    """Start the guitar learning session"""
    if not session_state["config"]:
        return {"success": False, "error": "Configuration not set"}
    
    if session_state["is_running"]:
        return {"success": False, "error": "Session already running"}
    
    try:
        config = session_state["config"]
        
        # Initialize session logger
        logger = get_session_logger()
        audio_state["session_logger"] = logger
        audio_state["strictness"] = config.get("strictness", 0.5)
        audio_state["sensitivity"] = config.get("sensitivity", 0.5)
        audio_state["ambient_lighting"] = config.get("ambient_lighting", True)
        
        # Start session logging
        session_id = logger.start_session(
            scale_name=config["scale_name"],
            strictness=audio_state["strictness"],
            sensitivity=audio_state["sensitivity"],
            ambient_lighting=audio_state["ambient_lighting"],
            scale_type=config.get("scale_type", "diatonic")
        )
        audio_state["session_id"] = session_id
        audio_state["notes_detected_count"] = 0
        audio_state["notes_in_scale_count"] = 0
        audio_state["notes_out_of_scale_count"] = 0
        audio_state["note_counts"] = {}
        audio_state["note_onset_times_ms"] = []
        
        # Initialize audio buffer
        buffer_size = int(
            AUDIO_CONSTANTS["SAMPLE_RATE"] * 
            AUDIO_CONSTANTS["ANALYSIS_WINDOW_SEC"]
        )
        audio_state["buffer"] = deque(maxlen=buffer_size)
        audio_state["buffer_lock"] = threading.Lock()
        
        # Start audio stream with callback
        def stream_callback(indata, outdata, frames, time_info, status):
            audio_callback(indata, outdata, frames, time_info, status, config, audio_state)
        
        audio_state["stream"] = sd.Stream(
            device=(config["input_device"], config["output_device"]),
            channels=config["channels"],
            samplerate=AUDIO_CONSTANTS["SAMPLE_RATE"],
            blocksize=AUDIO_CONSTANTS["BLOCK_SIZE"],
            dtype="float32",
            callback=stream_callback,
        )
        audio_state["stream"].start()
        
        # Start processing in background thread
        session_state["is_running"] = True
        audio_state["processing_task"] = threading.Thread(
            target=process_audio,
            args=(session_state, audio_state, AUDIO_CONSTANTS),
            daemon=True
        )
        audio_state["processing_task"].start()
        
        print(f"\n✅ Session started: {config['scale_name']} (Session ID: {session_id})")
        return {"success": True, "session_id": session_id}
        
    except Exception as e:
        session_state["is_running"] = False
        return {"success": False, "error": str(e)}


@app.post("/session/stop")
async def stop_session():
    """Stop the guitar learning session"""
    session_state["is_running"] = False
    
    # End session logging
    if audio_state["session_logger"] and audio_state["session_id"]:
        try:
            # Get total number of notes in the scale
            total_inscale_notes = audio_state.get("total_inscale_notes", 5)
            audio_state["session_logger"].end_session(
                session_id=audio_state["session_id"],
                total_inscale_notes=total_inscale_notes
            )
        except Exception as e:
            print(f"Error ending session: {e}")
    
    # Stop audio stream
    if audio_state["stream"] is not None:
        try:
            audio_state["stream"].stop()
            audio_state["stream"].close()
            audio_state["stream"] = None
        except Exception as e:
            print(f"Error stopping stream: {e}")
    
    # Wait for processing task to finish
    if audio_state["processing_task"] is not None:
        audio_state["processing_task"].join(timeout=1.0)
        audio_state["processing_task"] = None
    
    # Reset metrics
    session_state["current_note"] = "-"
    session_state["pitch_accuracy"] = 0
    session_state["scale_conformity"] = 0
    session_state["timing_stability"] = 0
    
    print("\n🛑 Session stopped")
    return {"success": True}


# ============================================================================
# METRICS ENDPOINTS
# ============================================================================

@app.get("/session/metrics", response_model=SessionMetrics)
async def get_metrics():
    """Get current session metrics"""
    return SessionMetrics(
        is_running=session_state["is_running"],
        current_note=session_state["current_note"],
        pitch_accuracy=session_state["pitch_accuracy"],
        scale_conformity=session_state["scale_conformity"],
        timing_stability=session_state["timing_stability"],
        target_scale=session_state["config"]["scale_name"] if session_state["config"] else "Not Set",
        debug_info=session_state["debug_info"],
    )


@app.websocket("/ws/metrics")
async def websocket_metrics(websocket: WebSocket):
    """WebSocket endpoint for real-time metrics updates"""
    await websocket.accept()
    try:
        while True:
            if session_state["is_running"]:
                metrics = {
                    "current_note": session_state["current_note"],
                    "pitch_accuracy": session_state["pitch_accuracy"],
                    "scale_conformity": session_state["scale_conformity"],
                    "timing_stability": session_state["timing_stability"],
                }
                await websocket.send_json(metrics)
            await asyncio.sleep(0.1)  # Update 10 times per second
    except WebSocketDisconnect:
        pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
