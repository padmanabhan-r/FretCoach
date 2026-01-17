"""
Configuration persistence service for FretCoach
"""

import os
import json
from typing import Optional


def get_config_file_path() -> str:
    """Get the path to the config file"""
    return os.path.join(os.path.dirname(__file__), '..', '..', 'core', 'audio_config.json')


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
