"""
Configuration persistence service for FretCoach
"""

import os
import json
from typing import Optional
from sqlalchemy import create_engine, text
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

# Get PostgreSQL credentials
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

# Create database engine
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)


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


def load_user_session_config(user_id: str) -> dict:
    """
    Load session configuration for a specific user from database.
    Falls back to file-based config if no user-specific config exists.

    Args:
        user_id: The user's identifier

    Returns:
        Session configuration dictionary with enabled_metrics
    """
    default_config = {
        "enabled_metrics": {
            "pitch_accuracy": True,
            "scale_conformity": True,
            "timing_stability": True
        }
    }

    try:
        query = text("""
            SELECT enabled_metrics
            FROM fretcoach.user_configs
            WHERE user_id = :user_id
        """)

        with engine.connect() as conn:
            result = conn.execute(query, {"user_id": user_id})
            row = result.fetchone()

            if row and row[0]:
                return {"enabled_metrics": row[0]}
    except Exception as e:
        print(f"Warning: Could not load user config from database: {e}")

    # Fall back to file-based config for backward compatibility
    return load_session_config_from_file()


def save_user_session_config(user_id: str, config: dict) -> bool:
    """
    Save session configuration for a specific user to database.

    Args:
        user_id: The user's identifier
        config: Session configuration dictionary with enabled_metrics

    Returns:
        True if saved successfully, False otherwise
    """
    try:
        enabled_metrics = config.get("enabled_metrics", {
            "pitch_accuracy": True,
            "scale_conformity": True,
            "timing_stability": True
        })

        query = text("""
            INSERT INTO fretcoach.user_configs (user_id, enabled_metrics, updated_at)
            VALUES (:user_id, :enabled_metrics, CURRENT_TIMESTAMP)
            ON CONFLICT (user_id)
            DO UPDATE SET
                enabled_metrics = EXCLUDED.enabled_metrics,
                updated_at = CURRENT_TIMESTAMP
        """)

        with engine.begin() as conn:
            conn.execute(query, {
                "user_id": user_id,
                "enabled_metrics": json.dumps(enabled_metrics)
            })
        return True
    except Exception as e:
        print(f"Warning: Could not save user config to database: {e}")
        return False
