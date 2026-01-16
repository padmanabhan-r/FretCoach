# Session Logging System

## Overview

FretCoach now includes comprehensive session logging to PostgreSQL. Every practice session is logged with detailed metrics and statistics for tracking progress over time.

## Database Schema

### `sessions` Table
Stores summary data for each practice session.

```sql
sessions
├── id (UUID) - Primary key
├── user_id (VARCHAR) - Optional user identifier
├── session_id (VARCHAR) - Unique session UUID
├── start_time (TIMESTAMP) - When session started
├── end_time (TIMESTAMP) - When session ended
├── duration_seconds (FLOAT) - Total session duration
├── scale_name (VARCHAR) - Scale practiced (e.g., "A Minor Pentatonic")
├── strictness (FLOAT) - Strictness level (0.0-1.0)
├── sensitivity (FLOAT) - Sensitivity level (0.0-1.0)
├── pitch_accuracy (FLOAT) - Final pitch accuracy score
├── scale_conformity (FLOAT) - Final scale conformity percentage
├── timing_stability (FLOAT) - Final timing stability score
├── notes_detected_count (INT) - Total notes detected
├── unique_notes_used (INT) - Unique scale notes played
├── notes_in_scale (INT) - Count of notes in scale
├── notes_out_of_scale (INT) - Count of wrong notes
├── ambient_lighting_enabled (BOOLEAN) - Whether bulb feedback was enabled
├── created_at (TIMESTAMP) - Record creation time
└── updated_at (TIMESTAMP) - Last update time
```

### `session_metrics` Table
Stores detailed per-metric data from each session for analysis.

```sql
session_metrics
├── id (UUID) - Primary key
├── session_id (UUID) - Foreign key to sessions
├── timestamp (TIMESTAMP) - When this metric was recorded
├── pitch_accuracy (FLOAT) - Pitch accuracy at this moment
├── scale_conformity (FLOAT) - Scale conformity at this moment
├── timing_stability (FLOAT) - Timing stability at this moment
├── detected_pitch_hz (FLOAT) - Detected frequency
├── detected_midi (FLOAT) - MIDI note number
├── pitch_class (INT) - Pitch class (0-11)
├── in_scale (BOOLEAN) - Whether note is in scale
├── note_detected (BOOLEAN) - Whether note was detected
└── created_at (TIMESTAMP) - Record creation time
```

## Usage

### In Backend API (`server.py`)

Session logging is automatically integrated:

```python
# Session starts automatically when you call /session/start
# No additional code needed

# Session ends automatically when you call /session/stop
# All metrics are saved to database
```

### Session Logger API

```python
from session_logger import get_session_logger

# Get logger instance
logger = get_session_logger()

# Start a session
session_id = logger.start_session(
    scale_name="A Minor Pentatonic",
    strictness=0.7,
    sensitivity=0.5,
    user_id="user123",  # Optional
    ambient_lighting=True
)

# Log individual metrics (called automatically in server)
logger.log_metric(
    session_id=session_id,
    pitch_accuracy=0.85,
    scale_conformity=0.60,
    timing_stability=0.72,
    debug_info=debug_dict  # Optional detailed info
)

# End session
logger.end_session(
    session_id=session_id,
    final_pitch_accuracy=0.87,
    final_scale_conformity=0.75,
    final_timing_stability=0.80,
    notes_detected=45,
    unique_notes_used=4,
    notes_in_scale=42,
    notes_out_of_scale=3
)

# Retrieve session stats
stats = logger.get_session_stats(session_id)
print(f"Session duration: {stats['duration_seconds']}s")
print(f"Final score: Pitch {stats['pitch_accuracy']*100:.1f}%")

# Get user's recent sessions
user_sessions = logger.get_user_sessions("user123", limit=10)
for session in user_sessions:
    print(f"{session['scale_name']}: {session['duration_seconds']}s")
```

## Environment Variables

Required PostgreSQL connection info in `.env`:

```env
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydb
```

## Auto-Initialization

The `SessionLogger` class automatically:
1. Connects to PostgreSQL
2. Creates tables if they don't exist
3. Creates indices for performance
4. Handles schema migrations gracefully

## Tracking Coverage

The logging system tracks:

### Scale Conformity
- **What it measures**: Percentage of unique scale notes you've played
- **Example**: A minor pentatonic has 5 notes. If you play all 5 unique notes (even repeated), that's 100% conformity
- **Stored as**: `scale_conformity` (0.0-1.0) in sessions table

### Pitch Accuracy
- **What it measures**: How close your played notes are to exact pitch
- **Range**: 0.0 (wrong notes) to 1.0 (perfectly in tune)
- **Stored as**: `pitch_accuracy` in sessions table

### Timing Stability
- **What it measures**: How evenly spaced your notes are
- **Range**: 0.0 (erratic) to 1.0 (perfectly consistent)
- **Stored as**: `timing_stability` in sessions table

## Data Analysis

Access raw metrics for analysis:

```python
import psycopg2

conn = psycopg2.connect(...)
cursor = conn.cursor()

# Get all sessions for a user
cursor.execute("""
    SELECT scale_name, duration_seconds, pitch_accuracy, scale_conformity, timing_stability
    FROM sessions
    WHERE user_id = %s
    ORDER BY start_time DESC
""", ("user123",))

sessions = cursor.fetchall()

# Get detailed metrics for a session
cursor.execute("""
    SELECT timestamp, pitch_accuracy, scale_conformity, timing_stability
    FROM session_metrics
    WHERE session_id = %s
    ORDER BY timestamp
""", (session_id,))

metrics = cursor.fetchall()
```

## Notes

- Database operations are non-blocking and won't affect audio processing
- Metrics are logged in real-time during the session
- Session data is immutable after `end_session()` is called
- Use `user_id` field to group sessions by learner
- Detailed metrics table allows for progress visualization and analysis
