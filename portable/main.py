#!/usr/bin/env python3
"""
FretCoach Portable - Terminal-based guitar practice tool for Raspberry Pi.
Uses rich for a polished, flicker-free terminal experience.

Shares core logic with the desktop application - no code duplication.
"""

import sys
import os
import time
import threading
import signal
from collections import deque
from datetime import datetime
from typing import Optional, Dict, Any

import numpy as np
import sounddevice as sd

# Rich imports for beautiful TUI
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

# Add backend/core to path for shared imports
BACKEND_CORE = os.path.join(os.path.dirname(__file__), '..', 'backend', 'core')
sys.path.insert(0, BACKEND_CORE)

# Shared imports from backend/core (DRY - no code duplication)
from audio_metrics import (
    QualityConfig,
    QualityState,
    BulbState,
    process_audio_frame,
    score_to_hue,
    calculate_bulb_brightness,
)
from smart_bulb import set_bulb_hsv, bulb_on, bulb_off, SMART_BULB_ENABLED
from scales import (
    MAJOR_DIATONIC, MINOR_DIATONIC,
    MAJOR_PENTATONIC, MINOR_PENTATONIC,
    select_scale_interactive,
)
from session_logger import get_session_logger, SessionLogger

# Console for rich output
console = Console()

# Audio constants (same as desktop)
SAMPLE_RATE = 44100
BLOCK_SIZE = 128
ANALYSIS_WINDOW_SEC = 0.30
BUFFER_SIZE = int(SAMPLE_RATE * ANALYSIS_WINDOW_SEC)
PHRASE_WINDOW = 0.8

# Global state for graceful shutdown
running = True
# Reference to the current audio processor for signal handler cleanup
_audio_processor_ref = None


def signal_handler(_sig, _frame):
    """Handle Ctrl+C gracefully - stop audio and cleanup."""
    global running
    running = False

    # Immediately stop the audio processor if one exists
    global _audio_processor_ref
    if _audio_processor_ref is not None:
        try:
            _audio_processor_ref.stop()
        except Exception:
            pass


signal.signal(signal.SIGINT, signal_handler)


# =========================================================
# FEEDBACK MESSAGES (same logic as desktop)
# =========================================================

def get_feedback_message(quality_state: QualityState, result: Any) -> tuple[str, str]:
    """
    Generate feedback message based on current performance.
    Returns (emoji, message) tuple.
    """
    ema = quality_state.ema_quality

    if result is None:
        return "⚪", "Waiting for input..."

    if not result.note_detected:
        return "⚪", "Play a note..."

    if not result.in_scale:
        return "🔴", "Wrong note! Stay in scale"

    # In scale - give feedback based on quality
    if ema >= 0.90:
        return "🟢", "Excellent! Keep it up!"
    elif ema >= 0.70:
        return "🟢", "Good playing!"
    elif ema >= 0.50:
        return "🟡", "Getting there, stay focused"
    elif ema >= 0.30:
        return "🟡", "Work on your timing"
    else:
        return "🟠", "Slow down, focus on accuracy"


def get_feedback_color(ema: float) -> str:
    """Get color for feedback based on quality score."""
    if ema >= 0.90:
        return "green"
    elif ema >= 0.70:
        return "yellow"
    elif ema >= 0.50:
        return "orange1"
    else:
        return "red"


# =========================================================
# TUI RENDERING
# =========================================================

def create_practice_display(
    scale_name: str,
    session_start: datetime,
    quality_state: QualityState,
    result: Any,
    enabled_metrics: dict,
) -> Panel:
    """Create the main practice display panel."""

    # Calculate session time
    elapsed = datetime.now() - session_start
    minutes = int(elapsed.total_seconds() // 60)
    seconds = int(elapsed.total_seconds() % 60)
    session_time = f"{minutes:02d}:{seconds:02d}"

    # Calculate metrics
    pitch_pct = int(quality_state.ema_pitch * 100)
    timing_pct = int(quality_state.ema_timing * 100)

    # Scale Conformity (coverage) - how evenly you're using all notes in the scale
    scale_conformity_pct = int(result.scale_coverage * 100) if result else 0

    # Get feedback
    emoji, message = get_feedback_message(quality_state, result)
    color = get_feedback_color(quality_state.ema_quality)

    # Build the display
    lines = []

    # Header info
    lines.append(f"[bold cyan]Scale[/]        : [white]{scale_name}[/]")
    lines.append(f"[bold cyan]Session Time[/] : [white]{session_time}[/]")
    lines.append("")

    # Progress bars (show "Disabled" for disabled metrics)
    lines.append(create_progress_line(
        "Pitch Accuracy",
        pitch_pct,
        "green" if pitch_pct >= 90 else "yellow" if pitch_pct >= 70 else "red",
        enabled_metrics.get("pitch_accuracy", True)
    ))
    lines.append(create_progress_line(
        "Timing Stability",
        timing_pct,
        "green" if timing_pct >= 90 else "yellow" if timing_pct >= 70 else "red",
        enabled_metrics.get("timing_stability", True)
    ))
    lines.append(create_progress_line(
        "Scale Conformity",
        scale_conformity_pct,
        "green" if scale_conformity_pct >= 90 else "yellow" if scale_conformity_pct >= 70 else "red",
        enabled_metrics.get("scale_conformity", True)
    ))
    lines.append("")

    # Feedback
    lines.append(f"[bold]Current Feedback[/]   {emoji}  [{color}]{message}[/]")

    content = "\n".join(lines)

    return Panel(
        content,
        title="[bold white]FRETCOACH — PRACTICE MODE[/]",
        border_style="cyan",
        box=box.DOUBLE,
        padding=(1, 2),
    )


def create_progress_line(label: str, value: int, color: str, enabled: bool = True) -> str:
    """Create a single progress bar line."""
    # Pad label to 18 chars
    padded_label = f"{label:<18}"

    # Show "Disabled" for disabled metrics
    if not enabled:
        return f"{padded_label} [dim]Disabled[/]"

    # Create bar (10 chars wide)
    filled = value // 10
    empty = 10 - filled

    bar = f"[{color}]{'█' * filled}[/][dim]{'░' * empty}[/]"

    return f"{padded_label} [{bar}] {value:>3}%"


# =========================================================
# AUDIO PROCESSING
# =========================================================

class AudioProcessor:
    """Handles audio capture and processing."""

    def __init__(
        self,
        input_device: Optional[int],
        output_device: Optional[int],
        channels: int,
        guitar_channel: int,
        target_pitch_classes: set,
        strictness: float,
        sensitivity: float,
        ambient_lighting: bool,
    ):
        self.input_device = input_device
        self.output_device = output_device
        self.channels = channels
        self.guitar_channel = guitar_channel
        self.target_pitch_classes = target_pitch_classes
        self.ambient_lighting = ambient_lighting

        # Audio buffer
        self.buffer = deque(maxlen=BUFFER_SIZE)
        self.buffer_lock = threading.Lock()

        # Quality tracking (from shared module)
        self.quality_config = QualityConfig(
            strictness=strictness,
            sensitivity=sensitivity,
            sample_rate=SAMPLE_RATE,
            phrase_window=PHRASE_WINDOW,
        )
        self.quality_state = QualityState()
        self.bulb_state = BulbState()

        # Latest result
        self.latest_result = None

        # Stream
        self.stream = None

    def audio_callback(self, indata, outdata, _frames, _time_info, status):
        """Real-time audio callback - just fills the buffer."""
        if status:
            pass  # Suppress status messages during live display

        # Handle mono/stereo
        if self.channels == 1 or indata.ndim == 1:
            guitar = indata.flatten()
        else:
            guitar = indata[:, self.guitar_channel]

        with self.buffer_lock:
            self.buffer.extend(guitar)

        outdata[:] = 0

    def start(self):
        """Start the audio stream."""
        self.stream = sd.Stream(
            device=(self.input_device, self.output_device),
            channels=self.channels,
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            dtype="float32",
            callback=self.audio_callback,
        )
        self.stream.start()

        # Turn on bulb if enabled
        if self.ambient_lighting and SMART_BULB_ENABLED:
            try:
                bulb_on()
            except Exception:
                pass

    def stop(self):
        """Stop the audio stream and release the device properly."""
        if self.stream:
            try:
                # Check if stream is still active before stopping
                if hasattr(self.stream, 'active') and self.stream.active:
                    self.stream.stop()
                self.stream.close()
            except Exception as e:
                console.print(f"[dim]Stream close warning: {e}[/]")
            finally:
                self.stream = None

        # RPi-specific: SoundDevice uses PortAudio which handles device cleanup.
        # The stream.stop() and stream.close() calls above properly release the device.
        # A full PortAudio terminate would require the underlying library access.

        # Turn off bulb
        if self.ambient_lighting and SMART_BULB_ENABLED:
            try:
                bulb_off()
            except Exception:
                pass

    def process_frame(self) -> Optional[Any]:
        """Process current audio buffer and return result."""
        with self.buffer_lock:
            if len(self.buffer) < BUFFER_SIZE:
                return None
            audio = np.array(self.buffer)

        result = process_audio_frame(
            audio=audio,
            target_pitch_classes=self.target_pitch_classes,
            config=self.quality_config,
            state=self.quality_state,
        )

        self.latest_result = result

        # Update bulb if enabled
        if result and self.ambient_lighting and SMART_BULB_ENABLED:
            hue = score_to_hue(self.quality_state.ema_quality)
            if self.bulb_state.should_update(hue):
                try:
                    brightness = calculate_bulb_brightness(self.quality_state.ema_quality)
                    set_bulb_hsv(hue, v=brightness)
                    self.bulb_state.mark_sent(hue)
                except Exception:
                    pass

        return result


# =========================================================
# USER AND MODE SELECTION
# =========================================================

def select_user() -> str:
    """Let user select between default_user and test_user."""
    console.print("\n" + "═" * 50)
    console.print("[bold cyan]SELECT USER[/]")
    console.print("═" * 50)
    console.print("\n  [bold]1.[/] default_user")
    console.print("  [bold]2.[/] test_user")
    console.print("\n" + "═" * 50)

    while True:
        choice = input("\nEnter choice (1 or 2): ").strip()
        if choice == "1":
            return "default_user"
        elif choice == "2":
            return "test_user"
        else:
            console.print("[red]Invalid choice. Please enter 1 or 2.[/]")


def select_mode() -> str:
    """Let user select between Manual and AI mode."""
    console.print("\n" + "═" * 50)
    console.print("[bold cyan]SELECT PRACTICE MODE[/]")
    console.print("═" * 50)
    console.print("\n  [bold]1.[/] Manual Mode - Choose your own scale")
    console.print("  [bold]2.[/] AI Mode - Get personalized recommendations")
    console.print("\n" + "═" * 50)

    while True:
        choice = input("\nEnter choice (1 or 2): ").strip()
        if choice == "1":
            return "manual"
        elif choice == "2":
            return "ai"
        else:
            console.print("[red]Invalid choice. Please enter 1 or 2.[/]")


def get_ai_recommendation(user_id: str, request_new: bool = False) -> Optional[Dict[str, Any]]:
    """
    Get AI-powered practice recommendation.
    Uses the SAME flow as desktop app - saves to DB, proper Opik tracing.
    """
    console.print("\n[cyan]Analyzing your practice history...[/]")

    try:
        import asyncio

        # Set deployment type BEFORE importing ai_agent_service
        os.environ["DEPLOYMENT_TYPE"] = "fretcoach-portable"

        # Import AI service (lazy import to avoid loading if not needed)
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'api', 'services'))
        from ai_agent_service import get_ai_practice_session

        # Use the SAME function as desktop - handles everything:
        # - Check pending plans
        # - Analyze practice history
        # - Generate recommendation with proper Opik tracing
        # - Save to database
        result = asyncio.run(get_ai_practice_session(user_id, request_new=request_new))

        recommendation = result["recommendation"]

        return {
            "practice_id": result["practice_id"],
            "scale_name": recommendation["scale_name"],
            "scale_type": recommendation["scale_type"],
            "focus_area": recommendation["focus_area"],
            "reasoning": recommendation["reasoning"],
            "strictness": recommendation["strictness"],
            "sensitivity": recommendation["sensitivity"],
            "analysis": result["analysis"],
            "is_pending_plan": result.get("is_pending_plan", False),
        }

    except Exception as e:
        console.print(f"[red]AI recommendation failed: {e}[/]")
        console.print("[yellow]Falling back to manual mode...[/]")
        return None


def mark_practice_plan_executed(practice_id: str, session_id: str) -> bool:
    """
    Mark a practice plan as executed by linking it to a session.
    Same as desktop API endpoint.
    """
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'api', 'services'))
        from sqlalchemy import create_engine, text

        # Get DB credentials
        from dotenv import load_dotenv, find_dotenv
        load_dotenv(find_dotenv())

        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_name = os.getenv("DB_NAME")

        db_uri = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        engine = create_engine(db_uri, pool_pre_ping=True)

        query = text("""
            UPDATE fretcoach.ai_practice_plans
            SET executed_session_id = :session_id
            WHERE practice_id = :practice_id
        """)

        with engine.begin() as conn:
            conn.execute(query, {
                "practice_id": practice_id,
                "session_id": session_id
            })

        return True
    except Exception as e:
        console.print(f"[yellow]Failed to mark plan as executed: {e}[/]")
        return False


def configure_metrics(user_id: str) -> dict:
    """
    Interactive metric configuration.
    Loads current config, allows user to toggle metrics, and saves to database.
    """
    # Import config service
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'api', 'services'))
    try:
        from config_service import load_user_session_config, save_user_session_config

        # Load current config
        config = load_user_session_config(user_id)
        enabled_metrics = config.get("enabled_metrics", {
            "pitch_accuracy": True,
            "scale_conformity": True,
            "timing_stability": True
        })

        console.print("\n" + "═" * 50)
        console.print(f"[bold cyan]CONFIGURE METRICS - {user_id}[/]")
        console.print("═" * 50)

        # Toggle each metric
        for metric_name, metric_label in [
            ("pitch_accuracy", "Pitch Accuracy"),
            ("scale_conformity", "Scale Conformity"),
            ("timing_stability", "Timing Stability")
        ]:
            current = "Enabled" if enabled_metrics.get(metric_name, True) else "Disabled"
            console.print(f"\n[bold]{metric_label}[/] (currently {current})")

            toggle = input(f"Enable {metric_label}? (Y/n): ").strip().lower()
            enabled_metrics[metric_name] = (toggle != 'n')

        # Save to database
        save_user_session_config(user_id, {"enabled_metrics": enabled_metrics})
        console.print("\n[green]Metric configuration saved![/]")

        return enabled_metrics

    except Exception as e:
        console.print(f"[yellow]Could not load/save metric config: {e}[/]")
        console.print("[yellow]Using default configuration (all metrics enabled)[/]")
        return {
            "pitch_accuracy": True,
            "scale_conformity": True,
            "timing_stability": True
        }


def get_target_pitch_classes(scale_name: str, scale_type: str) -> set:
    """Get pitch classes for a given scale (same as desktop)."""
    # Remove type suffix if present
    clean_name = scale_name.replace(" (Natural)", "").replace(" (Pentatonic)", "")
    is_major = "Major" in clean_name

    if scale_type == "natural":
        scales_dict = MAJOR_DIATONIC if is_major else MINOR_DIATONIC
    else:
        scales_dict = MAJOR_PENTATONIC if is_major else MINOR_PENTATONIC

    return set(scales_dict[clean_name])


# =========================================================
# AUDIO CONFIGURATION (device only, no scale selection)
# =========================================================

def get_audio_config() -> Optional[Dict[str, Any]]:
    """
    Get audio device configuration only (no scale selection).
    Reuses helper functions from audio_setup but controls the flow.
    """
    from audio_setup import (
        list_audio_devices,
        load_config,
        save_config,
        test_audio,
    )

    console.print("\n" + "=" * 60)
    console.print("[bold cyan]AUDIO CONFIGURATION[/]")
    console.print("=" * 60 + "\n")

    # Try to load existing config
    existing_config = load_config()

    if existing_config:
        console.print("[green]Found existing audio device configuration:[/]")
        console.print(f"  Input Device:   {existing_config.get('input_device', 'Default')}")
        console.print(f"  Output Device:  {existing_config.get('output_device', 'Default')}")
        console.print(f"  Guitar Channel: {existing_config.get('guitar_channel', 0)}")

        use_existing = input("\nUse these audio settings? (Y/n): ").strip().lower()

        if use_existing != 'n':
            # Test the existing configuration
            console.print("\n[cyan]Testing existing audio configuration...[/]")
            test_passed = test_audio(
                existing_config['input_device'],
                existing_config['output_device'],
                existing_config['channels'],
                existing_config['guitar_channel']
            )

            if test_passed:
                console.print("\n[green]Audio test passed![/]")
                # Get additional settings
                return get_practice_settings(existing_config)
            else:
                console.print("\n[yellow]Audio test failed.[/]")
                retry = input("Configure new audio settings? (Y/n): ").strip().lower()
                if retry == 'n':
                    return None

    # Run device selection
    audio_config = select_audio_devices(list_audio_devices)

    if audio_config is None:
        return None

    # Test audio
    test_passed = test_audio(
        audio_config['input_device'],
        audio_config['output_device'],
        audio_config['channels'],
        audio_config['guitar_channel']
    )

    if not test_passed:
        retry = input("\nAudio test failed. Try again? (Y/n): ").strip().lower()
        if retry != 'n':
            return get_audio_config()
        return None

    # Ask to save
    save = input("\nSave audio device configuration? (Y/n): ").strip().lower()
    if save != 'n':
        save_config({
            'input_device': audio_config['input_device'],
            'output_device': audio_config['output_device'],
            'guitar_channel': audio_config['guitar_channel'],
            'channels': audio_config['channels']
        })
        console.print("[green]Audio device configuration saved![/]")

    # Get additional settings
    return get_practice_settings(audio_config)


def select_audio_devices(list_audio_devices_fn) -> Optional[Dict[str, Any]]:
    """Interactive audio device selection."""
    import sounddevice as sd

    devices = list_audio_devices_fn()

    # Get input device
    while True:
        try:
            inp = input("Enter INPUT device number (or press Enter for default): ").strip()
            if inp == "":
                input_device = None
                console.print("[green]Using default input device[/]")
                default_input = sd.query_devices(kind='input')
                max_input_channels = default_input['max_input_channels']
                break
            else:
                input_device = int(inp)
                if isinstance(devices[input_device], dict):
                    max_input_channels = devices[input_device]['max_input_channels']
                    if max_input_channels == 0:
                        console.print(f"[red]Device {input_device} has no input channels. Please choose another.[/]")
                        continue
                    console.print(f"[green]Selected: {devices[input_device]['name']}[/]")
                    break
                else:
                    console.print("[red]Invalid device number. Please try again.[/]")
        except (ValueError, IndexError):
            console.print("[red]Invalid input. Please enter a valid device number.[/]")

    # Get output device
    while True:
        try:
            out = input("Enter OUTPUT device number (or press Enter for default): ").strip()
            if out == "":
                output_device = None
                console.print("[green]Using default output device[/]")
                break
            else:
                output_device = int(out)
                if isinstance(devices[output_device], dict):
                    max_output_channels = devices[output_device]['max_output_channels']
                    if max_output_channels == 0:
                        console.print(f"[red]Device {output_device} has no output channels. Please choose another.[/]")
                        continue
                    console.print(f"[green]Selected: {devices[output_device]['name']}[/]")
                    break
                else:
                    console.print("[red]Invalid device number. Please try again.[/]")
        except (ValueError, IndexError):
            console.print("[red]Invalid input. Please enter a valid device number.[/]")

    # Get input channel
    console.print(f"\n[cyan]Your input device has {max_input_channels} channel(s)[/]")
    if max_input_channels > 1:
        while True:
            try:
                ch = input(f"Enter input CHANNEL number (0-{max_input_channels-1}, press Enter for 0): ").strip()
                if ch == "":
                    guitar_channel = 0
                    console.print("[green]Using channel 0[/]")
                    break
                else:
                    guitar_channel = int(ch)
                    if 0 <= guitar_channel < max_input_channels:
                        console.print(f"[green]Using channel {guitar_channel}[/]")
                        break
                    else:
                        console.print(f"[red]Channel must be between 0 and {max_input_channels-1}[/]")
            except ValueError:
                console.print("[red]Invalid input. Please enter a number.[/]")
    else:
        guitar_channel = 0
        console.print("[green]Using channel 0 (only one channel available)[/]")

    # Determine number of channels
    if input_device is not None:
        input_channels = devices[input_device]['max_input_channels']
    else:
        input_channels = sd.query_devices(kind='input')['max_input_channels']

    if output_device is not None:
        output_channels = devices[output_device]['max_output_channels']
    else:
        output_channels = sd.query_devices(kind='output')['max_output_channels']

    stream_channels = max(1, min(input_channels, output_channels))

    return {
        'input_device': input_device,
        'output_device': output_device,
        'guitar_channel': guitar_channel,
        'channels': stream_channels,
    }


def get_practice_settings(audio_config: Dict[str, Any]) -> Dict[str, Any]:
    """Get ambient lighting setting only. Strictness/sensitivity come later based on mode."""

    # Ambient lighting
    console.print("\n" + "=" * 60)
    console.print("[bold cyan]AMBIENT LIGHTING[/]")
    console.print("=" * 60)
    if SMART_BULB_ENABLED:
        enable_bulb = input("\nEnable smart bulb ambient lighting? (Y/n): ").strip().lower()
        audio_config['ambient_lighting'] = (enable_bulb != 'n')
    else:
        console.print("[yellow]Smart bulb not configured. Ambient lighting disabled.[/]")
        audio_config['ambient_lighting'] = False
    console.print(f"[green]Ambient lighting: {'Enabled' if audio_config['ambient_lighting'] else 'Disabled'}[/]")

    return audio_config


def get_manual_mode_settings() -> tuple[float, float]:
    """Get strictness and sensitivity settings for manual mode."""

    # Strictness
    console.print("\n" + "=" * 60)
    console.print("[bold cyan]STRICTNESS (0.0 - 1.0)[/]")
    console.print("=" * 60)
    console.print("  0.0 = Very forgiving (practice mode)")
    console.print("  0.5 = Balanced (default)")
    console.print("  1.0 = Very strict (performance mode)")
    strictness = 0.5
    while True:
        strictness_input = input("\nEnter strictness [0.5]: ").strip()
        if not strictness_input:
            break
        try:
            val = float(strictness_input)
            if 0.0 <= val <= 1.0:
                strictness = val
                break
            else:
                console.print("[red]Please enter a value between 0.0 and 1.0[/]")
        except ValueError:
            console.print("[red]Invalid input. Please enter a number.[/]")
    console.print(f"[green]Strictness: {strictness:.2f}[/]")

    # Sensitivity
    console.print("\n" + "=" * 60)
    console.print("[bold cyan]SENSITIVITY (0.0 - 1.0)[/]")
    console.print("=" * 60)
    console.print("  0.0 = Picks up soft playing")
    console.print("  0.5 = Normal volume (default)")
    console.print("  1.0 = Only loud playing")
    sensitivity = 0.5
    while True:
        sensitivity_input = input("\nEnter sensitivity [0.5]: ").strip()
        if not sensitivity_input:
            break
        try:
            val = float(sensitivity_input)
            if 0.0 <= val <= 1.0:
                sensitivity = val
                break
            else:
                console.print("[red]Please enter a value between 0.0 and 1.0[/]")
        except ValueError:
            console.print("[red]Invalid input. Please enter a number.[/]")
    console.print(f"[green]Sensitivity: {sensitivity:.2f}[/]")

    return strictness, sensitivity


# =========================================================
# MAIN PRACTICE SESSION
# =========================================================

def run_practice_session(
    scale_name: str,
    scale_type: str,
    target_pitch_classes: set,
    audio_config: Dict[str, Any],
    strictness: float,
    sensitivity: float,
    ambient_lighting: bool,
    user_id: str = "default_user",
    enabled_metrics: Optional[dict] = None,
    practice_id: Optional[str] = None,
):
    """Run the main practice session with live display."""
    global running
    running = True

    # Default enabled metrics
    if enabled_metrics is None:
        enabled_metrics = {
            "pitch_accuracy": True,
            "scale_conformity": True,
            "timing_stability": True
        }

    # Initialize session logger
    session_logger: Optional[SessionLogger] = None
    session_id: Optional[str] = None

    try:
        session_logger = get_session_logger()
        session_id = session_logger.start_session(
            scale_name=scale_name,
            strictness=strictness,
            sensitivity=sensitivity,
            user_id=user_id,
            ambient_lighting=ambient_lighting,
            scale_type=scale_type,
            enabled_metrics=enabled_metrics,
        )

        # If this is an AI mode session, mark the practice plan as executed
        if practice_id and session_id:
            if mark_practice_plan_executed(practice_id, session_id):
                console.print(f"[dim]Linked session to AI practice plan[/]")
    except Exception as e:
        console.print(f"[yellow]Session logging unavailable: {e}[/]")

    # Create audio processor
    global _audio_processor_ref
    processor = AudioProcessor(
        input_device=audio_config['input_device'],
        output_device=audio_config['output_device'],
        channels=audio_config['channels'],
        guitar_channel=audio_config['guitar_channel'],
        target_pitch_classes=target_pitch_classes,
        strictness=strictness,
        sensitivity=sensitivity,
        ambient_lighting=ambient_lighting,
    )
    _audio_processor_ref = processor

    session_start = datetime.now()

    console.print(f"\n[bold green]Starting practice session: {scale_name}[/]")
    console.print(f"[dim]Press Ctrl+C to stop[/]\n")
    time.sleep(1)

    # Start audio
    processor.start()

    try:
        # Live display loop
        with Live(
            create_practice_display(
                scale_name, session_start,
                processor.quality_state, None, enabled_metrics
            ),
            console=console,
            refresh_per_second=8,
            transient=False,
        ) as live:
            while running:
                time.sleep(0.12)

                # Process audio frame
                result = processor.process_frame()

                # Log metric to session if available
                if session_logger and session_id and result:
                    try:
                        # Pass None for disabled metrics
                        pitch_acc = processor.quality_state.ema_pitch if enabled_metrics.get("pitch_accuracy", True) else None
                        scale_conf = result.scale_coverage if enabled_metrics.get("scale_conformity", True) else None
                        timing_stab = processor.quality_state.ema_timing if enabled_metrics.get("timing_stability", True) else None

                        session_logger.log_metric(
                            session_id=session_id,
                            pitch_accuracy=pitch_acc,
                            scale_conformity=scale_conf,
                            timing_stability=timing_stab,
                            debug_info={
                                "note_detected": result.note_detected,
                                "in_scale": result.in_scale,
                                "pitch_class": result.pitch_class,
                            }
                        )
                    except Exception:
                        pass

                # Update display
                live.update(
                    create_practice_display(
                        scale_name, session_start,
                        processor.quality_state, result, enabled_metrics
                    )
                )

    finally:
        # Stop audio
        processor.stop()
        _audio_processor_ref = None

        # End session and save to database
        if session_logger and session_id:
            try:
                total_scale_notes = len(target_pitch_classes)
                session_logger.end_session(session_id, total_inscale_notes=total_scale_notes)
            except Exception as e:
                console.print(f"[yellow]Failed to save session: {e}[/]")

        # Show session summary
        show_session_summary(
            session_start,
            processor.quality_state,
            enabled_metrics,
        )


def show_session_summary(
    session_start: datetime,
    quality_state: QualityState,
    enabled_metrics: dict,
):
    """Display session summary after practice ends."""
    elapsed = datetime.now() - session_start
    minutes = int(elapsed.total_seconds() // 60)
    seconds = int(elapsed.total_seconds() % 60)

    # Build metric lines
    pitch_line = f"  Pitch Accuracy:    {quality_state.ema_pitch * 100:.1f}%" if enabled_metrics.get("pitch_accuracy", True) else "  Pitch Accuracy:    Disabled"
    timing_line = f"  Timing Stability:  {quality_state.ema_timing * 100:.1f}%" if enabled_metrics.get("timing_stability", True) else "  Timing Stability:  Disabled"

    # Overall quality excludes disabled metrics (simplified - just show if any metric enabled)
    overall_line = f"  Overall Quality:   {quality_state.ema_quality * 100:.1f}%"

    console.print("\n")
    console.print(Panel(
        f"""[bold]Session Complete![/]

[cyan]Duration:[/] {minutes:02d}:{seconds:02d}

[cyan]Final Scores:[/]
{pitch_line}
{timing_line}
{overall_line}
""",
        title="[bold white]SESSION SUMMARY[/]",
        border_style="green",
        box=box.DOUBLE,
    ))


# =========================================================
# WELCOME SCREEN
# =========================================================

def show_welcome_screen():
    """Display a beautiful ASCII art welcome screen."""
    # ASCII art guitar logo (braille art)
    logo = """
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⢶⠲⠐
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡤⠊⠊⢀⠐⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⣀⠄⠚⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣼⣿⠟⠁⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣶⢻⠟⠁⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣤⣀⠀⠀⠀⢀⣴⣿⡽⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢠⣼⣿⡟⠀⠀⣠⣼⣿⡾⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢀⣿⣿⣿⣷⣀⣾⣿⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢀⣤⣾⣿⡿⠃⣼⣿⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⢀⣴⣾⣿⣿⠟⠋⠋⠀⠙⠝⠻⡂⠀⢀⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢰⣿⣿⣿⣿⡇⠀⡀⠙⢆⡀⠀⠀⠉⠉⣡⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢿⣿⣿⣿⣿⣿⣦⡀⢀⠀⠠⢀⡤⠚⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠘⢻⣿⣿⣿⣿⣿⣿⡌⠀⠀⡜⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠩⢿⣿⣿⣿⣻⣿⠀⣼⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠙⠿⢿⣾⡿⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
"""

    # Create a table for the welcome screen layout
    table = Table.grid(padding=(0, 2))
    table.add_column(justify="center", width=48)
    table.add_column(justify="left", width=42)

    # Left side: Logo and title
    left_content = Text()
    left_content.append(logo, style="orange1")
    left_content.append("\n        FretCoach", style="bold orange1")
    left_content.append(" Portable\n", style="bold white")

    # Right side: Tips and info
    right_content = Text()
    right_content.append("Getting Started\n", style="bold white")
    right_content.append("Select a user profile and practice mode.\n", style="dim")
    right_content.append("AI mode analyzes your history for suggestions.\n\n", style="dim")
    right_content.append("─" * 40 + "\n", style="dim")
    right_content.append("\nFeatures\n", style="bold white")
    right_content.append("  Real-time pitch detection\n", style="dim")
    right_content.append("  Scale conformity tracking\n", style="dim")
    right_content.append("  Smart bulb ambient lighting\n", style="dim")
    right_content.append("  Session history & metrics\n", style="dim")

    table.add_row(left_content, right_content)

    # Print the welcome panel
    console.print()
    console.print(Panel(
        table,
        title="[bold white]FretCoach[/] [dim]v1.0.0[/]",
        subtitle="[dim]Press Ctrl+C anytime to exit[/]",
        border_style="orange1",
        box=box.DOUBLE,
        padding=(1, 2),
    ))
    console.print()


# =========================================================
# MAIN ENTRY POINT
# =========================================================

def main():
    """Main entry point for FretCoach Portable."""
    # Show welcome screen
    show_welcome_screen()

    # Step 1: User selection
    user_id = select_user()
    console.print(f"\n[green]Selected user: {user_id}[/]")

    # Step 2: Metric configuration (optional)
    configure = input("\nConfigure metric settings? (y/N): ").strip().lower()
    if configure == 'y':
        enabled_metrics = configure_metrics(user_id)
    else:
        # Load existing config from database
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'api', 'services'))
            from config_service import load_user_session_config

            config = load_user_session_config(user_id)
            enabled_metrics = config.get("enabled_metrics", {
                "pitch_accuracy": True,
                "scale_conformity": True,
                "timing_stability": True
            })
            console.print("[green]Loaded metric configuration from database[/]")
        except Exception as e:
            console.print(f"[yellow]Could not load metric config: {e}[/]")
            console.print("[yellow]Using default configuration (all metrics enabled)[/]")
            enabled_metrics = {
                "pitch_accuracy": True,
                "scale_conformity": True,
                "timing_stability": True
            }

    # Step 3: Audio configuration
    audio_config = get_audio_config()
    if audio_config is None:
        console.print("[red]Audio configuration failed. Exiting.[/]")
        return

    # Step 4: Mode selection
    mode = select_mode()

    # Step 5: Get practice parameters based on mode
    practice_id = None  # Track AI practice plan ID

    if mode == "ai":
        recommendation = get_ai_recommendation(user_id)

        while recommendation:
            console.print("\n" + "═" * 50)
            console.print("[bold cyan]AI RECOMMENDATION[/]")
            console.print("═" * 50)
            if recommendation.get('is_pending_plan'):
                console.print("[yellow](Continuing pending practice plan)[/]")
            console.print(f"\n[bold]Scale:[/] {recommendation['scale_name']} ({recommendation['scale_type']})")
            console.print(f"[bold]Focus:[/] {recommendation['focus_area']}")
            console.print(f"[bold]Reasoning:[/] {recommendation['reasoning']}")
            console.print(f"[bold]Strictness:[/] {recommendation['strictness']:.2f}")
            console.print(f"[bold]Sensitivity:[/] {recommendation['sensitivity']:.2f}")
            console.print("\n" + "═" * 50)

            console.print("\n  [bold]1.[/] Accept this recommendation")
            console.print("  [bold]2.[/] Try another suggestion")
            console.print("  [bold]3.[/] Switch to Manual mode")

            choice = input("\nEnter choice (1/2/3): ").strip()

            if choice == "1":
                # Accept recommendation
                scale_name = recommendation['scale_name']
                scale_type = recommendation['scale_type']
                strictness = recommendation['strictness']
                sensitivity = recommendation['sensitivity']
                practice_id = recommendation['practice_id']
                target_pitch_classes = get_target_pitch_classes(scale_name, scale_type)
                break
            elif choice == "2":
                # Try another - force new recommendation
                console.print("\n[cyan]Generating new recommendation...[/]")
                recommendation = get_ai_recommendation(user_id, request_new=True)
                # Loop continues with new recommendation
            else:
                # Switch to manual
                mode = "manual"
                break

        if recommendation is None:
            mode = "manual"

    if mode == "manual":
        # Manual scale selection (reuse from core)
        scale_name, target_pitch_classes = select_scale_interactive()

        # Determine scale type from name
        scale_type = "pentatonic" if "Pentatonic" in scale_name else "natural"

        # Get strictness/sensitivity for manual mode
        strictness, sensitivity = get_manual_mode_settings()

    # Get ambient lighting preference
    ambient_lighting = audio_config.get('ambient_lighting', True)

    # Step 6: Run practice session
    run_practice_session(
        scale_name=scale_name,
        scale_type=scale_type,
        target_pitch_classes=target_pitch_classes,
        audio_config=audio_config,
        strictness=strictness,
        sensitivity=sensitivity,
        ambient_lighting=ambient_lighting,
        user_id=user_id,
        enabled_metrics=enabled_metrics,
        practice_id=practice_id,  # Link to AI practice plan if in AI mode
    )

    console.print("\n[dim]Thanks for practicing with FretCoach![/]\n")


if __name__ == "__main__":
    main()
