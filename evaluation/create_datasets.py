"""
Create Evaluation Datasets from Production Data

This script creates Opik datasets from real FretCoach sessions for
systematic evaluation of AI coaching and recommendations.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment
load_dotenv()

import opik
from opik import Opik


def get_db_connection():
    """Get database connection"""
    import psycopg2
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


def calculate_skill_level(metrics: Dict[str, float]) -> str:
    """Calculate skill level based on metrics"""
    avg = (metrics.get('pitch', 0) + metrics.get('scale', 0) + metrics.get('timing', 0)) / 3
    if avg >= 0.8:
        return "advanced"
    elif avg >= 0.5:
        return "intermediate"
    return "beginner"


def create_coaching_evaluation_dataset(opik_client: Opik) -> Dict[str, Any]:
    """Create dataset of coaching feedback for evaluation"""

    dataset = opik_client.get_or_create_dataset("coaching_feedback_evaluation")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get recent sessions (no need for historical feedback - we'll generate it during evaluation)
    query = """
        SELECT
            s.session_id, s.user_id, s.scale_chosen, s.scale_type,
            s.pitch_accuracy, s.scale_conformity, s.timing_stability,
            s.duration_seconds, s.start_timestamp
        FROM fretcoach.sessions s
        WHERE s.pitch_accuracy IS NOT NULL
          AND s.scale_conformity IS NOT NULL
          AND s.timing_stability IS NOT NULL
        ORDER BY s.start_timestamp DESC
        LIMIT 85
    """

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    items = []
    for row in rows:
        session_id, user_id, scale_chosen, scale_type, pitch, scale_conf, timing, duration, start_ts = row

        # Identify weakest area
        metrics = {
            "pitch": pitch,
            "scale": scale_conf,
            "timing": timing
        }
        weakest_area = min(metrics, key=metrics.get)

        # Calculate skill level
        skill_level = calculate_skill_level(metrics)

        # Create dataset item
        item = {
            "input": {
                "scale_name": scale_chosen,
                "scale_type": scale_type,
                "pitch_accuracy": pitch,
                "scale_conformity": scale_conf,
                "timing_stability": timing,
                "weakest_area": weakest_area,
                "session_duration": duration,
                "skill_level": skill_level,
                "metrics": metrics
            },
            "expected_output": {
                "focus_area": weakest_area,
                "tone": "encouraging",
                "actionable": True
            },
            "metadata": {
                "session_id": str(session_id),
                "user_id": user_id,
                "start_timestamp": start_ts.isoformat() if start_ts else None
            }
        }

        # No historical feedback needed - we'll generate during evaluation
        items.append(item)

    # Insert in batches
    batch_size = 50
    for i in range(0, len(items), batch_size):
        dataset.insert(items[i:i + batch_size])

    print(f"Created coaching dataset with {len(items)} items")

    return {
        "name": "coaching_feedback_evaluation",
        "count": len(items)
    }


def create_recommendation_evaluation_dataset(opik_client: Opik) -> Dict[str, Any]:
    """Create dataset of recommendation → outcome pairs"""

    dataset = opik_client.get_or_create_dataset("recommendation_accuracy_evaluation")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get practice plans with subsequent sessions
    query = """
        SELECT
            p.practice_id, p.user_id, p.practice_plan, p.generated_at,
            p.executed_session_id,
            s.pitch_accuracy, s.scale_conformity, s.timing_stability, s.start_timestamp
        FROM fretcoach.ai_practice_plans p
        LEFT JOIN fretcoach.sessions s ON p.executed_session_id = s.session_id
        WHERE p.executed_session_id IS NOT NULL
          AND s.pitch_accuracy IS NOT NULL
        ORDER BY p.generated_at DESC
        LIMIT 100
    """

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    items = []

    # Get user history for each execution
    conn = get_db_connection()
    cursor = conn.cursor()

    for row in rows:
        practice_id, user_id, plan_json, generated_at, exec_session_id, pitch, scale_conf, timing, exec_start = row

        # Get user's historical performance before this session
        hist_query = """
            SELECT
                AVG(pitch_accuracy) as avg_pitch,
                AVG(scale_conformity) as avg_scale,
                AVG(timing_stability) as avg_timing,
                COUNT(*) as session_count
            FROM fretcoach.sessions
            WHERE user_id = %s
              AND start_timestamp < %s
        """
        cursor.execute(hist_query, [user_id, exec_start])
        hist_row = cursor.fetchone()

        avg_pitch = hist_row[0] or 0.5
        avg_scale = hist_row[1] or 0.5
        avg_timing = hist_row[2] or 0.5

        # Parse practice plan
        try:
            plan = json.loads(plan_json) if plan_json else {}
            focus_area = plan.get('focus_area', 'pitch')
            scale_name = plan.get('scale_name', 'Unknown')
        except:
            plan = {}
            focus_area = 'pitch'
            scale_name = 'Unknown'

        # Calculate hours since generation
        hours_since = (exec_start - generated_at).total_seconds() / 3600 if generated_at and exec_start else 0

        item = {
            "input": {
                "user_history": {
                    "avg_pitch_accuracy": round(avg_pitch, 3),
                    "avg_scale_conformity": round(avg_scale, 3),
                    "avg_timing_stability": round(avg_timing, 3),
                    "total_sessions": hist_row[3] or 0
                },
                "recommended_scale": scale_name,
                "recommended_focus": focus_area,
                "recommended_strictness": plan.get('strictness', 0.5),
                "hours_since_generation": round(hours_since, 1)
            },
            "output": {
                "execution_metrics": {
                    "pitch_accuracy": round(pitch, 3),
                    "scale_conformity": round(scale_conf, 3),
                    "timing_stability": round(timing, 3)
                }
            },
            "expected_output": {
                "completion": True,
                "improvement": True
            },
            "metadata": {
                "practice_id": str(practice_id),
                "session_id": str(exec_session_id),
                "user_id": user_id
            }
        }

        items.append(item)

    conn.close()

    # Insert in batches
    batch_size = 50
    for i in range(0, len(items), batch_size):
        dataset.insert(items[i:i + batch_size])

    print(f"Created recommendation dataset with {len(items)} items")

    return {
        "name": "recommendation_accuracy_evaluation",
        "count": len(items)
    }


def create_learning_progress_dataset(opik_client: Opik) -> Dict[str, Any]:
    """Create dataset for tracking learning progress over time"""

    dataset = opik_client.get_or_create_dataset("learning_progress_tracking")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get user session history (at least 10 sessions per user)
    query = """
        SELECT user_id, COUNT(*) as cnt
        FROM fretcoach.sessions
        WHERE pitch_accuracy IS NOT NULL
        GROUP BY user_id
        HAVING COUNT(*) >= 10
        LIMIT 20
    """

    cursor.execute(query)
    users = [row[0] for row in cursor.fetchall()]

    items = []
    for user_id in users:
        sessions_query = """
            SELECT
                session_id, start_timestamp,
                pitch_accuracy, scale_conformity, timing_stability,
                scale_chosen, duration_seconds
            FROM fretcoach.sessions
            WHERE user_id = %s
              AND pitch_accuracy IS NOT NULL
            ORDER BY start_timestamp ASC
            LIMIT 50
        """
        cursor.execute(sessions_query, [user_id])
        user_sessions = cursor.fetchall()

        if len(user_sessions) >= 10:
            sessions_data = []
            for s in user_sessions:
                sessions_data.append({
                    "session_id": str(s[0]),
                    "start_timestamp": s[1].isoformat() if s[1] else None,
                    "pitch_accuracy": s[2],
                    "scale_conformity": s[3],
                    "timing_stability": s[4],
                    "scale_chosen": s[5],
                    "duration_seconds": s[6]
                })

            # Calculate skill level from first 3 sessions
            first_three = sessions_data[:3]
            avg_first = sum((s['pitch_accuracy'] + s['scale_conformity'] + s['timing_stability']) / 3 for s in first_three) / 3

            items.append({
                "input": {
                    "user_id": user_id,
                    "sessions": sessions_data,
                    "starting_skill_level": calculate_skill_level({
                        'pitch': avg_first, 'scale': avg_first, 'timing': avg_first
                    })
                },
                "metadata": {
                    "user_id": user_id,
                    "total_sessions": len(sessions_data)
                }
            })

    conn.close()

    # Insert in batches
    batch_size = 10
    for i in range(0, len(items), batch_size):
        dataset.insert(items[i:i + batch_size])

    print(f"Created learning progress dataset with {len(items)} users")

    return {
        "name": "learning_progress_tracking",
        "count": len(items)
    }


def main():
    """Main entry point for dataset creation"""
    print("=" * 60)
    print("FretCoach Opik Dataset Creation")
    print("=" * 60)

    # Initialize Opik client
    opik_client = Opik()

    try:
        # Create coaching feedback dataset
        print("\n[1/3] Creating coaching feedback dataset...")
        coaching_result = create_coaching_evaluation_dataset(opik_client)
        print(f"   -> Created: {coaching_result['name']} with {coaching_result['count']} items")

        # Create recommendation accuracy dataset
        print("\n[2/3] Creating recommendation accuracy dataset...")
        rec_result = create_recommendation_evaluation_dataset(opik_client)
        print(f"   -> Created: {rec_result['name']} with {rec_result['count']} items")

        # Create learning progress dataset
        print("\n[3/3] Creating learning progress dataset...")
        prog_result = create_learning_progress_dataset(opik_client)
        print(f"   -> Created: {prog_result['name']} with {prog_result['count']} users")

        print("\n" + "=" * 60)
        print("Dataset creation complete!")
        print("=" * 60)
        print("\nDatasets available in Opik:")
        print(f"  1. {coaching_result['name']}")
        print(f"  2. {rec_result['name']}")
        print(f"  3. {prog_result['name']}")

    except Exception as e:
        print(f"\nError creating datasets: {e}")
        raise


if __name__ == "__main__":
    main()
