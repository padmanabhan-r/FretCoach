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

# Optional: Opik tracing for AI mode (same pattern as desktop)
try:
    from opik.integrations.langchain import OpikTracer
    OPIK_ENABLED = True
except ImportError:
    OpikTracer = None
    OPIK_ENABLED = False

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
    if ema >= 0.85:
        return "🟢", "Excellent! Keep it up!"
    elif ema >= 0.70:
        return "🟢", "Good playing!"
    elif ema >= 0.55:
        return "🟡", "Getting there, stay focused"
    elif ema >= 0.40:
        return "🟡", "Work on your timing"
    else:
        return "🟠", "Slow down, focus on accuracy"


def get_feedback_color(ema: float) -> str:
    """Get color for feedback based on quality score."""
    if ema >= 0.70:
        return "green"
    elif ema >= 0.50:
        return "yellow"
    elif ema >= 0.30:
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
    target_pitch_classes: set,
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

    # Progress bars
    lines.append(create_progress_line("Pitch Accuracy", pitch_pct, "green" if pitch_pct >= 70 else "yellow" if pitch_pct >= 50 else "red"))
    lines.append(create_progress_line("Timing Stability", timing_pct, "green" if timing_pct >= 70 else "yellow" if timing_pct >= 50 else "red"))
    lines.append(create_progress_line("Scale Conformity", scale_conformity_pct, "green" if scale_conformity_pct >= 70 else "yellow" if scale_conformity_pct >= 50 else "red"))
    lines.append("")

    # Feedback
    lines.append(f"[bold]Current Feedback[/]   {emoji}  [{color}]{message}[/]")

    # Stats line
    total = quality_state.total_notes
    if total > 0:
        correct = quality_state.notes_in_scale(target_pitch_classes)
        wrong = quality_state.notes_out_of_scale(target_pitch_classes)
        lines.append("")
        lines.append(f"[dim]Notes: {total} total | {correct} in scale | {wrong} wrong[/]")

    content = "\n".join(lines)

    return Panel(
        content,
        title="[bold white]FRETCOACH — PRACTICE MODE[/]",
        border_style="cyan",
        box=box.DOUBLE,
        padding=(1, 2),
    )


def create_progress_line(label: str, value: int, color: str) -> str:
    """Create a single progress bar line."""
    # Create bar (10 chars wide)
    filled = value // 10
    empty = 10 - filled

    bar = f"[{color}]{'█' * filled}[/][dim]{'░' * empty}[/]"

    # Pad label to 18 chars
    padded_label = f"{label:<18}"

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
# MODE SELECTION
# =========================================================

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


def get_ai_recommendation(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get AI-powered practice recommendation.
    Uses same logic as desktop app with Opik tracing.
    """
    console.print("\n[cyan]Analyzing your practice history...[/]")

    try:
        # Import AI service (lazy import to avoid loading if not needed)
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'api', 'services'))
        from ai_agent_service import (
            analyze_practice_history_sync,
            get_pending_practice_plan,
            PracticeRecommendation,
        )
        from langchain_openai import ChatOpenAI
        import json

        # Check for pending plan first
        pending_plan = get_pending_practice_plan(user_id)
        if pending_plan:
            console.print(f"[yellow]Found pending practice plan from {pending_plan['generated_at']}[/]")

        # Analyze practice history
        analysis = analyze_practice_history_sync(user_id)

        if pending_plan:
            analysis['pending_plan'] = pending_plan

        # Generate recommendation (single LLM call with Opik tracing)
        model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        structured_llm = model.with_structured_output(PracticeRecommendation)

        # Build prompt (same as desktop)
        pending_plan_context = ""
        if analysis.get('pending_plan'):
            pp = analysis['pending_plan']
            pending_plan_context = f"""

PENDING PRACTICE PLAN:
There is an unexecuted practice plan from {pp['generated_at']}:
- Scale: {pp['plan']['scale_name']} ({pp['plan']['scale_type']})
- Focus: {pp['plan']['focus_area']}
- Reasoning: {pp['plan']['reasoning']}

DECISION REQUIRED:
Review this pending plan. If still relevant, continue with it. Otherwise, generate a new recommendation.
"""

        prompt = f"""You are an AI guitar coach. Based on the practice history below, recommend a practice session.

PRACTICE HISTORY:
- Total sessions: {analysis['total_sessions']}
- Average pitch accuracy: {analysis['aggregates']['avg_pitch_accuracy']:.1%}
- Average scale conformity: {analysis['aggregates']['avg_scale_conformity']:.1%}
- Average timing stability: {analysis['aggregates']['avg_timing_stability']:.1%}
- Weakest area: {analysis['weakest_area']}

RECENTLY PRACTICED SCALES:
{json.dumps(analysis['practiced_scales'][:5], indent=2) if analysis['practiced_scales'] else 'No scales practiced yet'}

RECENT SESSIONS:
{json.dumps(analysis['recent_sessions'][:3], indent=2) if analysis['recent_sessions'] else 'No recent sessions'}{pending_plan_context}

Generate a practice recommendation that:
1. Focuses on the weakest metric area ({analysis['weakest_area']})
2. Suggests a scale (preferably one not recently practiced, or one needing improvement)
3. Sets appropriate strictness/sensitivity based on skill level
"""

        # Get Opik config for tracing (same pattern as desktop)
        opik_config = {}
        if OPIK_ENABLED and OpikTracer:
            tracer = OpikTracer(
                tags=["ai-mode", "portable-recommendation"],
                metadata={"user_id": user_id, "device": "raspberry_pi"}
            )
            opik_config = {
                "callbacks": [tracer],
                "configurable": {"thread_id": f"portable-{user_id}"}
            }

        recommendation = structured_llm.invoke(
            [{"role": "user", "content": prompt}],
            config=opik_config
        )

        return {
            "scale_name": recommendation.scale_name,
            "scale_type": recommendation.scale_type,
            "focus_area": recommendation.focus_area,
            "reasoning": recommendation.reasoning,
            "strictness": recommendation.strictness,
            "sensitivity": recommendation.sensitivity,
            "analysis": analysis,
        }

    except Exception as e:
        console.print(f"[red]AI recommendation failed: {e}[/]")
        console.print("[yellow]Falling back to manual mode...[/]")
        return None


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
):
    """Run the main practice session with live display."""
    global running
    running = True

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
        )
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
                processor.quality_state, None, target_pitch_classes
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
                        session_logger.log_metric(
                            session_id=session_id,
                            pitch_accuracy=processor.quality_state.ema_pitch,
                            scale_conformity=result.scale_coverage,
                            timing_stability=processor.quality_state.ema_timing,
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
                        processor.quality_state, result, target_pitch_classes
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
            target_pitch_classes,
        )


def show_session_summary(
    session_start: datetime,
    quality_state: QualityState,
    target_pitch_classes: set,
):
    """Display session summary after practice ends."""
    elapsed = datetime.now() - session_start
    minutes = int(elapsed.total_seconds() // 60)
    seconds = int(elapsed.total_seconds() % 60)

    total = quality_state.total_notes
    correct = quality_state.notes_in_scale(target_pitch_classes)
    wrong = quality_state.notes_out_of_scale(target_pitch_classes)

    console.print("\n")
    console.print(Panel(
        f"""[bold]Session Complete![/]

[cyan]Duration:[/] {minutes:02d}:{seconds:02d}

[cyan]Final Scores:[/]
  Pitch Accuracy:    {quality_state.ema_pitch * 100:.1f}%
  Timing Stability:  {quality_state.ema_timing * 100:.1f}%
  Overall Quality:   {quality_state.ema_quality * 100:.1f}%

[cyan]Notes Played:[/]
  Total:   {total}
  Correct: {correct}
  Wrong:   {wrong}
  Accuracy: {(correct / total * 100) if total > 0 else 0:.1f}%
""",
        title="[bold white]SESSION SUMMARY[/]",
        border_style="green",
        box=box.DOUBLE,
    ))


# =========================================================
# MAIN ENTRY POINT
# =========================================================

def main():
    """Main entry point for FretCoach Portable."""
    console.print(Panel(
        "[bold]FretCoach Portable[/]\n\n"
        "Terminal-based guitar practice tool\n"
        "Designed for Raspberry Pi",
        title="🎸",
        border_style="cyan",
        box=box.DOUBLE,
    ))

    # Step 1: Audio configuration
    audio_config = get_audio_config()
    if audio_config is None:
        console.print("[red]Audio configuration failed. Exiting.[/]")
        return

    # Step 2: Mode selection
    mode = select_mode()

    # Step 3: Get practice parameters based on mode
    if mode == "ai":
        user_id = input("\nEnter your user ID (or press Enter for 'default_user'): ").strip()
        if not user_id:
            user_id = "default_user"

        recommendation = get_ai_recommendation(user_id)

        if recommendation:
            console.print("\n" + "═" * 50)
            console.print("[bold cyan]AI RECOMMENDATION[/]")
            console.print("═" * 50)
            console.print(f"\n[bold]Scale:[/] {recommendation['scale_name']} ({recommendation['scale_type']})")
            console.print(f"[bold]Focus:[/] {recommendation['focus_area']}")
            console.print(f"[bold]Reasoning:[/] {recommendation['reasoning']}")
            console.print(f"[bold]Strictness:[/] {recommendation['strictness']:.2f}")
            console.print(f"[bold]Sensitivity:[/] {recommendation['sensitivity']:.2f}")
            console.print("\n" + "═" * 50)

            accept = input("\nAccept this recommendation? (Y/n): ").strip().lower()
            if accept != 'n':
                scale_name = recommendation['scale_name']
                scale_type = recommendation['scale_type']
                strictness = recommendation['strictness']
                sensitivity = recommendation['sensitivity']
                target_pitch_classes = get_target_pitch_classes(scale_name, scale_type)
            else:
                mode = "manual"
        else:
            mode = "manual"
            user_id = "default_user"
    else:
        user_id = "default_user"

    if mode == "manual":
        # Manual scale selection (reuse from core)
        scale_name, target_pitch_classes = select_scale_interactive()

        # Determine scale type from name
        scale_type = "pentatonic" if "Pentatonic" in scale_name else "natural"

        # Get strictness/sensitivity for manual mode
        strictness, sensitivity = get_manual_mode_settings()

    # Get ambient lighting preference
    ambient_lighting = audio_config.get('ambient_lighting', True)

    # Step 4: Run practice session
    run_practice_session(
        scale_name=scale_name,
        scale_type=scale_type,
        target_pitch_classes=target_pitch_classes,
        audio_config=audio_config,
        strictness=strictness,
        sensitivity=sensitivity,
        ambient_lighting=ambient_lighting,
        user_id=user_id,
    )

    console.print("\n[dim]Thanks for practicing with FretCoach![/]\n")


if __name__ == "__main__":
    main()
