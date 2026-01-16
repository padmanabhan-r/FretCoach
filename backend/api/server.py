"""
FastAPI server for FretCoach
Provides REST API endpoints for the Electron app to communicate with the Python backend
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import sounddevice as sd
import asyncio
import json
import sys
import os

# Import Opik for tracking (non-blocking)
try:
    from opik import track
    from opik import opik_context
    OPIK_ENABLED = True
    print("✅ Opik tracking enabled")
except ImportError:
    # Fallback decorator if opik is not installed
    def track(func):
        return func
    OPIK_ENABLED = False
    print("⚠️  Opik not installed, tracking disabled")

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))

from audio_setup import list_audio_devices
from scales import ALL_SCALES
from audio_features import pitch_correctness, pitch_stability, timing_cleanliness, noise_control, calculate_scale_coverage
from smart_bulb import set_bulb_hsv, bulb_on, bulb_off
import numpy as np
from collections import deque
import threading
import time

app = FastAPI(title="FretCoach API")

# Enable CORS for Electron app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
session_state = {
    "is_running": False,
    "config": None,
    "current_note": "-",
    "pitch_accuracy": 0,
    "scale_conformity": 0,
    "timing_stability": 0,
    "debug_info": {
        "detected_hz": 0,
        "detected_midi": 0,
        "pitch_class": 0,
        "in_scale": False,
        "raw_pitch": 0,
        "raw_timing": 0,
    },
}

# Audio processing state
audio_state = {
    "stream": None,
    "buffer": None,
    "buffer_lock": None,
    "processing_task": None,
    "last_sent_hue": None,
    "last_send_time": 0.0,
    "ema_quality": 0.0,
    "ema_pitch": 0.0,
    "ema_timing": 0.0,
    "last_phrase_time": 0.0,
    "strictness": 0.5,
    "sensitivity": 0.5,
    "ambient_lighting": True,
    "notes_played_in_scale": set(),  # Track unique pitch classes from scale that have been played
}

AUDIO_CONSTANTS = {
    "SAMPLE_RATE": 44100,
    "BLOCK_SIZE": 128,
    "ANALYSIS_WINDOW_SEC": 0.30,
    "TUYA_UPDATE_INTERVAL": 0.30,
    "HUE_EPSILON": 5,
    "PHRASE_WINDOW": 0.8,
}

# Models
class AudioDevice(BaseModel):
    index: int
    name: str
    max_input_channels: int
    max_output_channels: int
    default_samplerate: float

class AudioConfig(BaseModel):
    input_device: int
    output_device: int
    guitar_channel: int
    channels: int
    scale_name: str
    scale_type: Optional[str] = "diatonic"  # "diatonic" or "pentatonic"
    ambient_lighting: Optional[bool] = True
    strictness: Optional[float] = 0.5
    sensitivity: Optional[float] = 0.5

class SessionMetrics(BaseModel):
    is_running: bool
    current_note: str
    pitch_accuracy: float
    scale_conformity: float
    timing_stability: float
    target_scale: str
    debug_info: Optional[Dict] = None

# Endpoints
@app.get("/")
async def root():
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
    import numpy as np
    import threading
    import queue
    
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
    from scales import MAJOR_DIATONIC, MINOR_DIATONIC
    
    return {
        "major": sorted(MAJOR_DIATONIC.keys()),
        "minor": sorted(MINOR_DIATONIC.keys())
    }

@app.post("/config")
async def save_config(config: AudioConfig):
    """Save audio and scale configuration"""
    session_state["config"] = config.model_dump()
    
    # Save to file for persistence
    import json
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

def audio_callback(indata, outdata, frames, time_info, status):
    """Real-time audio callback"""
    if status:
        print(f"Audio status: {status}")
    
    config = session_state["config"]
    if not config:
        return
    
    # Handle both mono and stereo input
    if config["channels"] == 1 or indata.ndim == 1:
        guitar = indata.flatten()
    else:
        guitar = indata[:, config["guitar_channel"]]
    
    with audio_state["buffer_lock"]:
        audio_state["buffer"].extend(guitar)

def score_to_hue(score):
    """Convert quality score (0-1) to hue (0-120, red to green)"""
    return int(np.clip(score, 0.0, 1.0) * 120)

@track(name="process_audio_session")
def process_audio():
    """Background task to process audio and update metrics"""
    config = session_state["config"]
    sample_rate = AUDIO_CONSTANTS["SAMPLE_RATE"]
    buffer_size = int(sample_rate * AUDIO_CONSTANTS["ANALYSIS_WINDOW_SEC"])
    
    # Get configuration parameters
    strictness = audio_state["strictness"]
    sensitivity = audio_state["sensitivity"]
    ambient_lighting = audio_state["ambient_lighting"]
    
    # Calculate EMA alpha based on strictness
    ema_alpha = 0.10 + (strictness * 0.30)  # Range: 0.10 to 0.40
    
    # Get target pitch classes from scale
    from scales import MAJOR_DIATONIC, MINOR_DIATONIC, MAJOR_PENTATONIC, MINOR_PENTATONIC
    
    scale_name = config["scale_name"]
    scale_type = config.get("scale_type", "diatonic")
    is_major = "Major" in scale_name
    
    if scale_type == "diatonic":
        scales_dict = MAJOR_DIATONIC if is_major else MINOR_DIATONIC
    else:
        scales_dict = MAJOR_PENTATONIC if is_major else MINOR_PENTATONIC
    
    target_pitch_classes = set(scales_dict[scale_name])
    
    print(f"\n🎸 Processing audio for {scale_name} ({scale_type})")
    print(f"Target notes: {sorted(target_pitch_classes)}")
    print(f"Strictness: {strictness:.2f} | Sensitivity: {sensitivity:.2f}")
    print(f"Ambient lighting: {'Enabled' if ambient_lighting else 'Disabled'}")
    
    audio_state["ema_quality"] = 0.0
    audio_state["ema_pitch"] = 0.0
    audio_state["ema_timing"] = 0.0
    audio_state["notes_played_in_scale"] = set()  # Reset scale coverage tracking
    audio_state["last_phrase_time"] = time.time()
    audio_state["last_sent_hue"] = None
    audio_state["last_send_time"] = 0.0
    
    # Turn on bulb at start if enabled
    if ambient_lighting:
        try:
            bulb_on()
            print("💡 Smart bulb enabled")
        except Exception as e:
            print(f"⚠️  Smart bulb not available: {e}")
    
    while session_state["is_running"]:
        time.sleep(0.15)
        
        with audio_state["buffer_lock"]:
            if len(audio_state["buffer"]) < buffer_size:
                continue
            audio = np.array(audio_state["buffer"])
        
        # Check if there's enough energy (adjusted by sensitivity)
        energy = np.mean(audio ** 2)
        energy_threshold = 1e-7 * (1 + sensitivity * 10)
        if energy < energy_threshold:
            session_state["current_note"] = "-"
            continue
        
        # Calculate pitch correctness
        p, debug_info = pitch_correctness(audio, sample_rate, target_pitch_classes)
        
        # Track notes played for scale coverage
        if debug_info.get("note_detected") and debug_info.get("in_scale") and debug_info.get("pitch_class") is not None:
            audio_state["notes_played_in_scale"].add(debug_info["pitch_class"])
        
        # Calculate all metrics
        s = pitch_stability(audio, sample_rate)
        t = timing_cleanliness(audio, sample_rate)
        n = noise_control(audio)
        
        # Calculate scale coverage (what % of scale notes have been played)
        scale_coverage = calculate_scale_coverage(
            audio_state["notes_played_in_scale"],
            target_pitch_classes
        )
        
        # Store debug info
        session_state["debug_info"] = {
            **debug_info,
            "raw_pitch": float(p),
            "raw_timing": float(t),
            "scale_coverage": float(scale_coverage),
            "notes_played_count": len(audio_state["notes_played_in_scale"]),
            "scale_total_notes": len(target_pitch_classes),
        }
        
        # Adjust weights based on strictness
        pitch_weight = 0.40 + (strictness * 0.15)
        other_weight = (1.0 - pitch_weight) / 3
        
        quality = (
            pitch_weight * p +
            other_weight * s +
            other_weight * t +
            other_weight * n
        )
        
        # Apply wrong note penalty based on strictness
        if p == 0.0:
            session_state["current_note"] = "Wrong Note"
            
            # At high strictness (>0.7), instant punishment
            if strictness > 0.7:
                audio_state["ema_quality"] = 0.0
                audio_state["last_phrase_time"] = time.time()
            else:
                # At low strictness, wrong notes still get partial credit
                penalty_factor = (1.0 - strictness)
                quality = quality * penalty_factor
                
                # Update EMA quality
                now = time.time()
                if now - audio_state["last_phrase_time"] > AUDIO_CONSTANTS["PHRASE_WINDOW"]:
                    audio_state["ema_quality"] = (
                        ema_alpha * quality + 
                        (1 - ema_alpha) * audio_state["ema_quality"]
                    )
                    audio_state["last_phrase_time"] = now
        else:
            session_state["current_note"] = "In Scale"
            
            # Update EMA quality when playing correct notes
            now = time.time()
            if now - audio_state["last_phrase_time"] > AUDIO_CONSTANTS["PHRASE_WINDOW"]:
                audio_state["ema_quality"] = (
                    ema_alpha * quality + 
                    (1 - ema_alpha) * audio_state["ema_quality"]
                )
                audio_state["last_phrase_time"] = now
        
        # Update smart bulb color if enabled
        if ambient_lighting:
            now = time.time()
            hue = score_to_hue(audio_state["ema_quality"])
            brightness = int(300 + 700 * audio_state["ema_quality"])
            
            if (
                (audio_state["last_sent_hue"] is None or 
                 abs(hue - audio_state["last_sent_hue"]) >= AUDIO_CONSTANTS["HUE_EPSILON"])
                and (now - audio_state["last_send_time"]) >= AUDIO_CONSTANTS["TUYA_UPDATE_INTERVAL"]
            ):
                try:
                    set_bulb_hsv(hue, v=brightness)
                    audio_state["last_sent_hue"] = hue
                    audio_state["last_send_time"] = now
                except Exception as e:
                    # Silently fail - don't spam console
                    pass
        
        # Update session state metrics with EMA smoothing
        # Use slower EMA (0.15) for smoother, less jumpy metrics
        metric_ema_alpha = 0.15
        audio_state["ema_pitch"] = metric_ema_alpha * p + (1 - metric_ema_alpha) * audio_state["ema_pitch"]
        audio_state["ema_timing"] = metric_ema_alpha * t + (1 - metric_ema_alpha) * audio_state["ema_timing"]
        
        session_state["pitch_accuracy"] = audio_state["ema_pitch"]
        session_state["scale_conformity"] = scale_coverage  # Use scale coverage instead of ema_quality
        session_state["timing_stability"] = audio_state["ema_timing"]

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
        
        # Initialize audio buffer
        buffer_size = int(
            AUDIO_CONSTANTS["SAMPLE_RATE"] * 
            AUDIO_CONSTANTS["ANALYSIS_WINDOW_SEC"]
        )
        audio_state["buffer"] = deque(maxlen=buffer_size)
        audio_state["buffer_lock"] = threading.Lock()
        
        # Start audio stream
        audio_state["stream"] = sd.Stream(
            device=(config["input_device"], config["output_device"]),
            channels=config["channels"],
            samplerate=AUDIO_CONSTANTS["SAMPLE_RATE"],
            blocksize=AUDIO_CONSTANTS["BLOCK_SIZE"],
            dtype="float32",
            callback=audio_callback,
        )
        audio_state["stream"].start()
        
        # Start processing in background thread
        session_state["is_running"] = True
        audio_state["processing_task"] = threading.Thread(
            target=process_audio,
            daemon=True
        )
        audio_state["processing_task"].start()
        
        print(f"\n✅ Session started: {config['scale_name']}")
        return {"success": True}
        
    except Exception as e:
        session_state["is_running"] = False
        return {"success": False, "error": str(e)}

@app.post("/session/stop")
async def stop_session():
    """Stop the guitar learning session"""
    session_state["is_running"] = False
    
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
