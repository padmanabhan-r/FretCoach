"""
Audio device testing service for FretCoach
"""

import queue
import threading
import numpy as np
import sounddevice as sd


def test_audio_device_impl(device_index: int, channel: int = 0) -> dict:
    """
    Test audio input from a specific device and channel.

    Args:
        device_index: Index of the audio device to test
        channel: Channel number to test (0-indexed)

    Returns:
        dict with success status, rms_level, peak_level, and has_signal
    """
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
