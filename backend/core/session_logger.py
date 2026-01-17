"""
Session Logging System for FretCoach
Handles database schema creation and session data logging to PostgreSQL.
"""

import os
import uuid
import psycopg2
from psycopg2 import sql
from datetime import datetime
from typing import Optional, Dict, Any
import json

# Import Opik for tracking (non-blocking)
try:
    from opik import track, opik_context
    OPIK_ENABLED = True
except ImportError:
    # Fallback decorator if opik is not installed
    def track(name=None, **kwargs):
        def decorator(func):
            return func
        return decorator
    opik_context = None
    OPIK_ENABLED = False

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env from backend directory
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    load_dotenv(env_path)
except ImportError:
    print("[WARN] python-dotenv not installed. Make sure to set environment variables.")

# Database configuration from environment
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "postgres")


class SQLLoader:
    """Load and parse SQL from files"""

    def __init__(self, sql_dir: str):
        """
        Initialize SQL loader.

        Args:
            sql_dir: Path to directory containing SQL files
        """
        self.sql_dir = sql_dir
        self.queries = {}
        self.schema = None
        self._load_files()

    def _load_files(self):
        """Load SQL files from the sql directory"""
        # Load schema
        schema_path = os.path.join(self.sql_dir, "schema.sql")
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                self.schema = f.read()

        # Load and parse queries
        queries_path = os.path.join(self.sql_dir, "queries.sql")
        if os.path.exists(queries_path):
            with open(queries_path, 'r') as f:
                content = f.read()
            self._parse_queries(content)

    def _parse_queries(self, content: str):
        """
        Parse SQL file with named queries.
        Format: -- name: query_name followed by the SQL query
        """
        current_name = None
        current_sql = []

        for line in content.split('\n'):
            stripped = line.strip()
            if stripped.startswith('-- name:'):
                # Save previous query if exists
                if current_name and current_sql:
                    self.queries[current_name] = '\n'.join(current_sql).strip()
                # Start new query
                current_name = stripped.replace('-- name:', '').strip()
                current_sql = []
            elif current_name is not None:
                # Skip comment lines (descriptions)
                if not stripped.startswith('--'):
                    current_sql.append(line)

        # Save last query
        if current_name and current_sql:
            self.queries[current_name] = '\n'.join(current_sql).strip()

    def get_query(self, name: str) -> Optional[str]:
        """Get a query by name"""
        return self.queries.get(name)

    def get_schema(self) -> Optional[str]:
        """Get the schema SQL"""
        return self.schema


class SessionLogger:
    """Handles session logging to PostgreSQL"""

    @staticmethod
    def _convert_numpy_types(value):
        """Convert numpy types to Python native types for database insertion"""
        if value is None:
            return None
        # Handle numpy scalar types
        if hasattr(value, 'item'):  # numpy types have .item() method
            return value.item()
        return value

    def __init__(self):
        """Initialize database connection and load SQL"""
        self.conn = None
        # Load SQL from files
        sql_dir = os.path.join(os.path.dirname(__file__), "..", "sql")
        self.sql_loader = SQLLoader(sql_dir)
        self.connect()
        self.ensure_tables_exist()
        # In-memory accumulator for session metrics
        self.session_data = {}  # session_id -> accumulated metrics

    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME
            )
            print(f"[OK] Connected to PostgreSQL at {DB_HOST}:{DB_PORT}/{DB_NAME}")
        except Exception as e:
            print(f"[ERR] Failed to connect to PostgreSQL: {e}")
            raise

    def ensure_tables_exist(self):
        """Create tables if they don't exist"""
        try:
            cursor = self.conn.cursor()

            # Check if the sessions table exists and has the new schema
            check_schema_sql = self.sql_loader.get_query("check_new_schema")
            if check_schema_sql:
                cursor.execute(check_schema_sql)
            else:
                cursor.execute("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'sessions' AND column_name = 'total_inscale_notes';
                """)
            has_new_schema = cursor.fetchone() is not None

            # Only drop and recreate if the old schema exists
            if not has_new_schema:
                print("[WARN] Migrating to new session table schema...")
                cursor.execute("DROP TABLE IF EXISTS session_metrics CASCADE;")
                cursor.execute("DROP TABLE IF EXISTS sessions CASCADE;")

            # Check if scale_type column exists, add it if missing
            check_scale_type_sql = self.sql_loader.get_query("check_scale_type_column")
            if check_scale_type_sql:
                cursor.execute(check_scale_type_sql)
            else:
                cursor.execute("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'sessions' AND column_name = 'scale_type';
                """)
            has_scale_type = cursor.fetchone() is not None

            if not has_scale_type and has_new_schema:
                print("[WARN] Adding scale_type column to sessions table...")
                add_scale_type_sql = self.sql_loader.get_query("add_scale_type_column")
                if add_scale_type_sql:
                    cursor.execute(add_scale_type_sql)
                else:
                    cursor.execute("""
                        ALTER TABLE sessions
                        ADD COLUMN scale_type VARCHAR(20) DEFAULT 'natural';
                    """)
                self.conn.commit()

            # Create tables using schema file or inline SQL
            if self.sql_loader.schema:
                cursor.execute(self.sql_loader.schema)
            else:
                # Fallback to inline SQL
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        session_id VARCHAR(255) NOT NULL,
                        user_id VARCHAR(255) NOT NULL,
                        start_timestamp TIMESTAMP NOT NULL,
                        end_timestamp TIMESTAMP,
                        pitch_accuracy FLOAT,
                        scale_conformity FLOAT,
                        timing_stability FLOAT,
                        scale_chosen VARCHAR(100) NOT NULL,
                        scale_type VARCHAR(20) DEFAULT 'natural',
                        sensitivity FLOAT NOT NULL,
                        strictness FLOAT NOT NULL,
                        total_notes_played INT DEFAULT 0,
                        correct_notes_played INT DEFAULT 0,
                        bad_notes_played INT DEFAULT 0,
                        total_inscale_notes INT,
                        duration_seconds FLOAT,
                        ambient_light_option BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (session_id, user_id)
                    );
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_sessions_user_id
                    ON sessions(user_id);
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_sessions_start_timestamp
                    ON sessions(start_timestamp DESC);
                """)

            self.conn.commit()
            print("[OK] Database tables verified/created")
        except Exception as e:
            print(f"[ERR] Error creating tables: {e}")
            self.conn.rollback()
            raise

    def start_session(
        self,
        scale_name: str,
        strictness: float,
        sensitivity: float,
        user_id: Optional[str] = None,
        ambient_lighting: bool = True,
        scale_type: str = "natural"
    ) -> str:
        """
        Create a new session record in memory (not in database yet).

        Args:
            scale_name: Name of the scale being practiced
            strictness: Strictness level (0.0-1.0)
            sensitivity: Sensitivity level (0.0-1.0)
            user_id: Optional user identifier
            ambient_lighting: Whether ambient lighting is enabled
            scale_type: Type of scale - 'natural' or 'pentatonic'

        Returns:
            session_id: Unique session ID for tracking
        """
        session_id = str(uuid.uuid4())
        now = datetime.now()

        # Initialize session data in memory
        self.session_data[session_id] = {
            "session_id": session_id,
            "user_id": user_id or "default_user",
            "start_timestamp": now,
            "scale_chosen": scale_name,
            "scale_type": scale_type,
            "strictness": strictness,
            "sensitivity": sensitivity,
            "ambient_light_option": ambient_lighting,
            # Accumulated metrics (will be averaged at end)
            "pitch_accuracy_sum": 0.0,
            "scale_conformity_sum": 0.0,
            "timing_stability_sum": 0.0,
            "metric_count": 0,
            # Note counters
            "total_notes_played": 0,
            "correct_notes_played": 0,
            "bad_notes_played": 0,
            "total_inscale_notes": 0,  # This is the total number of notes in the scale (e.g., 5 for pentatonic)
        }

        print(f"[OK] Session started in memory: {session_id}")
        return session_id

    def log_metric(
        self,
        session_id: str,
        pitch_accuracy: float,
        scale_conformity: float,
        timing_stability: float,
        debug_info: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Accumulate performance metrics in memory (NOT written to database yet).
        Database write happens only at end_session().

        Args:
            session_id: Session UUID
            pitch_accuracy: Pitch accuracy score (0.0-1.0)
            scale_conformity: Scale conformity percentage (0.0-1.0)
            timing_stability: Timing stability score (0.0-1.0)
            debug_info: Optional debug information from pitch detection
        """
        if session_id not in self.session_data:
            print(f"[WARN] Session {session_id} not found in memory")
            return

        # Convert numpy types to Python native types
        pitch_accuracy = self._convert_numpy_types(pitch_accuracy)
        scale_conformity = self._convert_numpy_types(scale_conformity)
        timing_stability = self._convert_numpy_types(timing_stability)

        # Accumulate metrics
        session = self.session_data[session_id]
        session["pitch_accuracy_sum"] += pitch_accuracy
        session["scale_conformity_sum"] += scale_conformity
        session["timing_stability_sum"] += timing_stability
        session["metric_count"] += 1

        # Track notes if debug info provided
        if debug_info and debug_info.get("note_detected"):
            session["total_notes_played"] += 1
            if debug_info.get("in_scale"):
                session["correct_notes_played"] += 1
            else:
                session["bad_notes_played"] += 1

    @track(name="end_session_db_write")
    def end_session(
        self,
        session_id: str,
        total_inscale_notes: int = 5  # Total number of notes in the scale (e.g., 5 for pentatonic, 7 for natural)
    ) -> None:
        """
        End a session, calculate final averages, and save to database.
        This is the ONLY time data is written to the database.

        Args:
            session_id: Session UUID
            total_inscale_notes: Total number of notes in the scale (not how many were played, but how many exist in the scale)
        """
        # Set thread_id for Opik tracking
        if OPIK_ENABLED and opik_context:
            opik_context.update_current_trace(thread_id=f"session-{session_id}")

        if session_id not in self.session_data:
            print(f"[ERR] Session {session_id} not found in memory")
            return

        try:
            session = self.session_data[session_id]
            now = datetime.now()

            # Calculate averages
            metric_count = session["metric_count"]
            if metric_count > 0:
                avg_pitch_accuracy = session["pitch_accuracy_sum"] / metric_count
                avg_scale_conformity = session["scale_conformity_sum"] / metric_count
                avg_timing_stability = session["timing_stability_sum"] / metric_count
            else:
                avg_pitch_accuracy = 0.0
                avg_scale_conformity = 0.0
                avg_timing_stability = 0.0

            # Calculate duration
            start_time = session["start_timestamp"]
            duration = (now - start_time).total_seconds()

            # Convert numpy types
            avg_pitch_accuracy = self._convert_numpy_types(avg_pitch_accuracy)
            avg_scale_conformity = self._convert_numpy_types(avg_scale_conformity)
            avg_timing_stability = self._convert_numpy_types(avg_timing_stability)

            # Set total_inscale_notes
            session["total_inscale_notes"] = total_inscale_notes

            # Insert single row into database
            cursor = self.conn.cursor()
            insert_sql = self.sql_loader.get_query("insert_session")
            if insert_sql:
                cursor.execute(insert_sql, (
                    session["session_id"],
                    session["user_id"],
                    session["start_timestamp"],
                    now,
                    avg_pitch_accuracy,
                    avg_scale_conformity,
                    avg_timing_stability,
                    session["scale_chosen"],
                    session["scale_type"],
                    session["sensitivity"],
                    session["strictness"],
                    session["total_notes_played"],
                    session["correct_notes_played"],
                    session["bad_notes_played"],
                    session["total_inscale_notes"],
                    duration,
                    session["ambient_light_option"]
                ))
            else:
                cursor.execute("""
                    INSERT INTO sessions
                    (session_id, user_id, start_timestamp, end_timestamp,
                     pitch_accuracy, scale_conformity, timing_stability,
                     scale_chosen, scale_type, sensitivity, strictness,
                     total_notes_played, correct_notes_played, bad_notes_played,
                     total_inscale_notes, duration_seconds, ambient_light_option)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    session["session_id"],
                    session["user_id"],
                    session["start_timestamp"],
                    now,
                    avg_pitch_accuracy,
                    avg_scale_conformity,
                    avg_timing_stability,
                    session["scale_chosen"],
                    session["scale_type"],
                    session["sensitivity"],
                    session["strictness"],
                    session["total_notes_played"],
                    session["correct_notes_played"],
                    session["bad_notes_played"],
                    session["total_inscale_notes"],
                    duration,
                    session["ambient_light_option"]
                ))

            self.conn.commit()

            # Clean up memory
            del self.session_data[session_id]

            print(f"[OK] Session ended and saved to database: {session_id}")
            print(f"  Duration: {duration:.1f}s | Pitch: {avg_pitch_accuracy*100:.1f}% | Scale: {avg_scale_conformity*100:.1f}% | Timing: {avg_timing_stability*100:.1f}%")
            print(f"  Notes: {session['total_notes_played']} total, {session['correct_notes_played']} correct, {session['bad_notes_played']} bad")
        except Exception as e:
            print(f"[ERR] Error ending session: {e}")
            self.conn.rollback()
            # Clean up memory even on error
            if session_id in self.session_data:
                del self.session_data[session_id]

    def get_session_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session statistics from database.

        Args:
            session_id: Session UUID

        Returns:
            Dictionary with session stats or None if not found
        """
        try:
            cursor = self.conn.cursor()
            get_stats_sql = self.sql_loader.get_query("get_session_stats")
            if get_stats_sql:
                cursor.execute(get_stats_sql, (session_id,))
            else:
                cursor.execute("""
                    SELECT
                        session_id, user_id, start_timestamp, end_timestamp,
                        pitch_accuracy, scale_conformity, timing_stability,
                        scale_chosen, scale_type, sensitivity, strictness,
                        total_notes_played, correct_notes_played, bad_notes_played,
                        total_inscale_notes, duration_seconds, ambient_light_option
                    FROM sessions
                    WHERE session_id = %s
                """, (session_id,))

            result = cursor.fetchone()
            if result:
                return {
                    "session_id": result[0],
                    "user_id": result[1],
                    "start_timestamp": result[2],
                    "end_timestamp": result[3],
                    "pitch_accuracy": result[4],
                    "scale_conformity": result[5],
                    "timing_stability": result[6],
                    "scale_chosen": result[7],
                    "scale_type": result[8],
                    "sensitivity": result[9],
                    "strictness": result[10],
                    "total_notes_played": result[11],
                    "correct_notes_played": result[12],
                    "bad_notes_played": result[13],
                    "total_inscale_notes": result[14],
                    "duration_seconds": result[15],
                    "ambient_light_option": result[16],
                }
            return None
        except Exception as e:
            print(f"[ERR] Error retrieving session stats: {e}")
            return None

    def get_user_sessions(self, user_id: str, limit: int = 10) -> list:
        """
        Retrieve recent sessions for a user.

        Args:
            user_id: User identifier
            limit: Maximum number of sessions to retrieve

        Returns:
            List of session records
        """
        try:
            cursor = self.conn.cursor()
            get_sessions_sql = self.sql_loader.get_query("get_user_sessions")
            if get_sessions_sql:
                cursor.execute(get_sessions_sql, (user_id, limit))
            else:
                cursor.execute("""
                    SELECT
                        session_id, start_timestamp, end_timestamp, duration_seconds,
                        scale_chosen, scale_type, pitch_accuracy, scale_conformity, timing_stability,
                        total_notes_played, correct_notes_played, bad_notes_played
                    FROM sessions
                    WHERE user_id = %s
                    ORDER BY start_timestamp DESC
                    LIMIT %s
                """, (user_id, limit))

            results = cursor.fetchall()
            sessions = []
            for row in results:
                sessions.append({
                    "session_id": row[0],
                    "start_timestamp": row[1],
                    "end_timestamp": row[2],
                    "duration_seconds": row[3],
                    "scale_chosen": row[4],
                    "scale_type": row[5],
                    "pitch_accuracy": row[6],
                    "scale_conformity": row[7],
                    "timing_stability": row[8],
                    "total_notes_played": row[9],
                    "correct_notes_played": row[10],
                    "bad_notes_played": row[11],
                })
            return sessions
        except Exception as e:
            print(f"[ERR] Error retrieving user sessions: {e}")
            return []

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("[OK] Database connection closed")


# Global session logger instance
_logger_instance = None


def get_session_logger() -> SessionLogger:
    """Get or create the global session logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = SessionLogger()
    return _logger_instance


def initialize_session_logger():
    """Initialize the session logger"""
    return get_session_logger()
