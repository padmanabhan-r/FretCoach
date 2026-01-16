"""
Audio device endpoints for FretCoach API
"""

from fastapi import APIRouter
from typing import List
import sounddevice as sd

from ..models import AudioDevice
from ..services.device_service import test_audio_device_impl

router = APIRouter()


@router.get("/audio/devices", response_model=List[AudioDevice])
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


@router.post("/audio/test/{device_index}")
async def test_audio_device(device_index: int, channel: int = 0):
    """Test audio input from a specific device and channel"""
    return test_audio_device_impl(device_index, channel)
