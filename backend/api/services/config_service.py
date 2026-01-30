"""
Configuration persistence service for FretCoach
"""

import os
import json
from typing import Optional


def get_config_file_path() -> str:
    """Get the path to the audio config file"""
    return os.path.join(os.path.dirname(__file__), '..', '..', 'core', 'audio_config.json')


def get_session_config_file_path() -> str:
    """Get the path to the session config file"""
    return os.path.join(os.path.dirname(__file__), '..', '..', 'core', 'session_config.json')


def save_config_to_file(config: dict) -> bool:
    """
    Save configuration to file.

    Args:
        config: Configuration dictionary to save

    Returns:
        True if saved successfully, False otherwise
    """
    config_file = get_config_file_path()
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Warning: Could not save config to file: {e}")
        return False


def load_config_from_file() -> Optional[dict]:
    """
    Load configuration from file.

    Returns:
        Configuration dictionary if found, None otherwise
    """
    config_file = get_config_file_path()
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load config from file: {e}")
    return None


def save_session_config_to_file(config: dict) -> bool:
    """
    Save session configuration to file.

    Args:
        config: Session configuration dictionary to save

    Returns:
        True if saved successfully, False otherwise
    """
    config_file = get_session_config_file_path()
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Warning: Could not save session config to file: {e}")
        return False


def load_session_config_from_file() -> dict:
    """
    Load session configuration from file.

    Returns:
        Session configuration dictionary, returns defaults if file not found
    """
    config_file = get_session_config_file_path()
    default_config = {
        "enabled_metrics": {
            "pitch_accuracy": True,
            "scale_conformity": True,
            "timing_stability": True
        }
    }

    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load session config from file: {e}")

    return default_config
