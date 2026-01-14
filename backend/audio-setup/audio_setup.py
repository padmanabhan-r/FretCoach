"""
Audio device configuration helper for guitar feedback applications.
Allows user to interactively select input/output devices and channels.
Saves and loads configuration from file.
"""

import sounddevice as sd
import json
import os
import numpy as np
import time
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
from scales import select_scale_interactive

CONFIG_FILE = "audio_config.json"


def list_audio_devices():
    """Display all available audio devices."""
    print("\n" + "="*60)
    print("AVAILABLE AUDIO DEVICES")
    print("="*60)
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if isinstance(device, dict):
            print(f"\n[{i}] {device['name']}")
            print(f"    Inputs: {device['max_input_channels']}, Outputs: {device['max_output_channels']}")
            print(f"    Default Sample Rate: {device['default_samplerate']} Hz")
    print("="*60 + "\n")
    return devices


def save_config(config):
    """Save configuration to JSON file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✓ Configuration saved to {CONFIG_FILE}")
    except Exception as e:
        print(f"❌ Error saving config: {e}")


def load_config():
    """Load configuration from JSON file. Returns None if not found."""
    if not os.path.exists(CONFIG_FILE):
        return None
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        # Convert pitch_classes back to set
        if 'pitch_classes' in config and isinstance(config['pitch_classes'], list):
            config['pitch_classes'] = set(config['pitch_classes'])
        return config
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return None


def test_audio(input_device, output_device, channels, guitar_channel, sample_rate=44100):
    """
    Test audio input by recording for a few seconds and showing the signal level.
    Returns True if test passed, False otherwise.
    """
    print("\n" + "="*60)
    print("AUDIO TEST")
    print("="*60)
    print("Get ready to play your guitar...")
    print("\nCountdown:")
    for i in range(3, 0, -1):
        print(f"  {i}...", flush=True)
        time.sleep(1)
    print("  🎸 Play!\n")
    
    recording = []
    
    def callback(indata, frames, time_info, status):
        if status:
            print(status)
        if channels == 1 or indata.ndim == 1:
            audio = indata.flatten()
        else:
            audio = indata[:, guitar_channel]
        recording.extend(audio)
    
    try:
        with sd.InputStream(
            device=input_device,
            channels=channels,
            samplerate=sample_rate,
            callback=callback
        ):
            time.sleep(3)
        
        if len(recording) == 0:
            print("❌ No audio received!")
            return False
        
        audio_array = np.array(recording)
        energy = np.mean(audio_array ** 2)
        max_amplitude = np.max(np.abs(audio_array))
        
        print(f"\n✓ Audio test complete!")
        print(f"  Energy level: {energy:.2e}")
        print(f"  Max amplitude: {max_amplitude:.4f}")
        
        if energy < 1e-10:
            print("\n⚠️  WARNING: Signal level is very low!")
            print("   Make sure your guitar is plugged in and turn up the input gain.")
            return False
        elif energy < 1e-6:
            print("\n⚠️  Signal level is low. Consider turning up the input gain.")
        else:
            print("\n✓ Signal level looks good!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during audio test: {e}")
        return False


def get_user_device_selection():
    """
    Prompt user to select input/output devices and input channel.
    Returns a dict with device configuration.
    """
    devices = list_audio_devices()
    
    # Get input device
    while True:
        try:
            inp = input("Enter INPUT device number (or press Enter for default): ").strip()
            if inp == "":
                input_device = None
                print("Using default input device")
                # Get default input device info
                default_input = sd.query_devices(kind='input')
                max_input_channels = default_input['max_input_channels']
                break
            else:
                input_device = int(inp)
                if isinstance(devices[input_device], dict):
                    max_input_channels = devices[input_device]['max_input_channels']
                    if max_input_channels == 0:
                        print(f"❌ Device {input_device} has no input channels. Please choose another.")
                        continue
                    print(f"✓ Selected: {devices[input_device]['name']}")
                    break
                else:
                    print("Invalid device number. Please try again.")
        except (ValueError, IndexError):
            print("Invalid input. Please enter a valid device number.")
    
    # Get output device
    while True:
        try:
            out = input("Enter OUTPUT device number (or press Enter for default): ").strip()
            if out == "":
                output_device = None
                print("Using default output device")
                break
            else:
                output_device = int(out)
                if isinstance(devices[output_device], dict):
                    max_output_channels = devices[output_device]['max_output_channels']
                    if max_output_channels == 0:
                        print(f"❌ Device {output_device} has no output channels. Please choose another.")
                        continue
                    print(f"✓ Selected: {devices[output_device]['name']}")
                    break
                else:
                    print("Invalid device number. Please try again.")
        except (ValueError, IndexError):
            print("Invalid input. Please enter a valid device number.")
    
    # Get input channel
    print(f"\nYour input device has {max_input_channels} channel(s)")
    if max_input_channels > 1:
        while True:
            try:
                ch = input(f"Enter input CHANNEL number (0-{max_input_channels-1}, press Enter for 0): ").strip()
                if ch == "":
                    guitar_channel = 0
                    print("✓ Using channel 0")
                    break
                else:
                    guitar_channel = int(ch)
                    if 0 <= guitar_channel < max_input_channels:
                        print(f"✓ Using channel {guitar_channel}")
                        break
                    else:
                        print(f"Channel must be between 0 and {max_input_channels-1}")
            except ValueError:
                print("Invalid input. Please enter a number.")
    else:
        guitar_channel = 0
        print("✓ Using channel 0 (only one channel available)")
    
    # Determine number of channels for stream
    # Use stereo if both devices support it, otherwise mono
    if input_device is not None:
        input_channels = devices[input_device]['max_input_channels']
    else:
        input_channels = sd.query_devices(kind='input')['max_input_channels']
    
    if output_device is not None:
        output_channels = devices[output_device]['max_output_channels']
    else:
        output_channels = sd.query_devices(kind='output')['max_output_channels']
    
    # Use minimum common channels, but at least 1
    stream_channels = max(1, min(input_channels, output_channels))
    
    return {
        'input_device': input_device,
        'output_device': output_device,
        'guitar_channel': guitar_channel,
        'channels': stream_channels,
    }


def setup_configuration():
    """
    Complete setup flow: device selection, scale selection, audio test, save config.
    Returns complete configuration dict.
    """
    # Step 1: Select audio devices
    audio_config = get_user_device_selection()
    
    # Step 2: Select musical scale
    scale_name, pitch_classes = select_scale_interactive()
    audio_config['scale_name'] = scale_name
    audio_config['pitch_classes'] = list(pitch_classes)  # Convert set to list for JSON
    
    # Step 3: Display configuration summary
    print("\n" + "="*60)
    print("CONFIGURATION SUMMARY")
    print("="*60)
    print(f"Input Device:    {audio_config['input_device'] if audio_config['input_device'] is not None else 'Default'}")
    print(f"Output Device:   {audio_config['output_device'] if audio_config['output_device'] is not None else 'Default'}")
    print(f"Guitar Channel:  {audio_config['guitar_channel']}")
    print(f"Stream Channels: {audio_config['channels']}")
    print(f"Musical Scale:   {scale_name}")
    print("="*60)
    
    # Step 4: Test audio
    test_passed = test_audio(
        audio_config['input_device'],
        audio_config['output_device'],
        audio_config['channels'],
        audio_config['guitar_channel']
    )
    
    if test_passed:
        # Step 5: Ask to save audio configuration (without scale)
        save = input("\nSave audio device configuration? (Y/n): ").strip().lower()
        if save != 'n':
            # Save only audio device settings, not the scale
            audio_only_config = {
                'input_device': audio_config['input_device'],
                'output_device': audio_config['output_device'],
                'guitar_channel': audio_config['guitar_channel'],
                'channels': audio_config['channels']
            }
            save_config(audio_only_config)
            print("✓ Audio device configuration saved!")
        return audio_config
    else:
        retry = input("\nAudio test failed. Try again? (Y/n): ").strip().lower()
        if retry != 'n':
            return setup_configuration()
        else:
            return None


def get_configuration():
    """
    Main entry point for configuration.
    Tries to load saved config, asks user if it's good, or runs setup.
    Returns complete configuration dict.
    """
    print("\n" + "🎸"*30)
    print("GUITAR FEEDBACK AUDIO CONFIGURATION")
    print("🎸"*30 + "\n")
    
    # Try to load existing config
    existing_config = load_config()
    
    if existing_config:
        print("Found existing audio device configuration:")
        print(f"  Input Device:   {existing_config.get('input_device', 'Default')}")
        print(f"  Output Device:  {existing_config.get('output_device', 'Default')}")
        print(f"  Guitar Channel: {existing_config.get('guitar_channel', 0)}")
        
        use_existing = input("\nUse these audio settings? (Y/n): ").strip().lower()
        
        if use_existing != 'n':
            # Test the existing configuration
            print("\nTesting existing audio configuration...")
            test_passed = test_audio(
                existing_config['input_device'],
                existing_config['output_device'],
                existing_config['channels'],
                existing_config['guitar_channel']
            )
            
            if test_passed:
                print("\n✓ Audio test passed!")
                # Now select scale (always ask for scale)
                scale_name, pitch_classes = select_scale_interactive()
                existing_config['scale_name'] = scale_name
                existing_config['pitch_classes'] = list(pitch_classes)
                return existing_config
            else:
                print("\n⚠️  Audio test failed.")
                retry = input("Configure again? (Y/n): ").strip().lower()
                if retry == 'n':
                    return None
    
    # Run full setup
    return setup_configuration()


if __name__ == "__main__":
    # Test the module
    config = get_configuration()
    if config:
        print("\n✓ Configuration ready to use:")
        print(json.dumps(config, indent=2))
    else:
        print("\n❌ Configuration setup cancelled.")
