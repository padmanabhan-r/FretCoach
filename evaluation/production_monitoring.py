"""
Phase 4: Production Monitoring for FretCoach

This module provides comprehensive production monitoring capabilities including:
- Online evaluation rules configuration
- Dashboard setup and management
- Alert configuration
- Feedback score recording

Usage:
    python evaluation/production_monitoring.py
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment
load_dotenv()

from opik import Opik


# ============================================================================
# FEEDBACK SCORE RECORDING
# ============================================================================

def record_coaching_helpfulness_score(
    trace_id: str,
    score: float,
    reason: str,
    metadata: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Record coaching helpfulness feedback score for a trace.

    This should be called after generating coaching feedback to score
    its helpfulness using the custom metric.

    Args:
        trace_id: The ID of the trace to score
        score: Helpfulness score (0.0-1.0)
        reason: Explanation of the score
        metadata: Additional metadata

    Returns:
        The created feedback score
    """
    try:
        opik_client = Opik()

        # Create feedback score (result stored but not needed directly)
        _feedback_score = opik_client.api_client.create_feedback_score(
            name="coaching_helpfulness",
            value=score,
            trace_id=trace_id,
            reason=reason,
            metadata=metadata or {}
        )

        return {
            "success": True,
            "trace_id": trace_id,
            "score_name": "coaching_helpfulness",
            "score_value": score
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "trace_id": trace_id
        }


def record_recommendation_accuracy_score(
    trace_id: str,
    score: float,
    improvement_pct: float,
    metadata: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Record recommendation accuracy feedback score.

    This should be called after a practice plan is executed to measure
    if the recommendation led to improvement.

    Args:
        trace_id: The ID of the trace
        score: Accuracy/improvement score (0.0-1.0)
        improvement_pct: Percentage improvement
        metadata: Additional metadata

    Returns:
        The created feedback score
    """
    try:
        opik_client = Opik()

        # Create feedback score (result stored but not needed directly)
        _feedback_score = opik_client.api_client.create_feedback_score(
            name="recommendation_accuracy",
            value=score,
            trace_id=trace_id,
            reason=f"Improvement: {improvement_pct:.1%}",
            metadata=metadata or {}
        )

        return {
            "success": True,
            "trace_id": trace_id,
            "score_name": "recommendation_accuracy",
            "score_value": score
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "trace_id": trace_id
        }


# ============================================================================
# AUTO-SCORING INTEGRATION
# ============================================================================

class ProductionAutoScorer:
    """
    Auto-scores production traces with configurable rules.

    This class integrates with the live coach service to automatically
    score every coaching interaction.
    """

    def __init__(self, model: str = "gpt-4o-mini", sampling_rate: float = 0.1):
        """
        Initialize the auto-scorer.

        Args:
            model: LLM model to use for scoring
            sampling_rate: Fraction of traces to score (0.0-1.0)
        """
        self.model = model
        self.sampling_rate = sampling_rate
        self.opik_client = Opik()

    def should_score(self) -> bool:
        """Determine if this trace should be scored based on sampling rate"""
        import random
        return random.random() < self.sampling_rate

    def score_coaching_feedback(
        self,
        input_data: Dict[str, Any],
        output: str,
        trace_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Score coaching feedback and record feedback score.

        Args:
            input_data: The input context (metrics, weakest_area, etc.)
            output: The generated coaching feedback
            trace_id: The trace ID

        Returns:
            Score result or None if not scoring this trace
        """
        if not self.should_score():
            return None

        try:
            from evaluation import CoachingHelpfulness

            metric = CoachingHelpfulness(model=self.model)
            result = metric.score(input=input_data, output=output)

            # Record feedback score
            record_coaching_helpfulness_score(
                trace_id=trace_id,
                score=result.value,
                reason=result.reason,
                metadata=result.metadata
            )

            return {
                "score": result.value,
                "reason": result.reason,
                "metadata": result.metadata
            }
        except Exception as e:
            print(f"Auto-scoring error: {e}")
            return None


# ============================================================================
# DASHBOARD CONFIGURATIONS
# ============================================================================

DASHBOARD_CONFIGS = {
    "learning_progress": {
        "name": "FretCoach Learning Progress",
        "description": "Track user improvement over time with key learning metrics",
        "widgets": [
            {
                "name": "Overall Performance Trend",
                "type": "line_chart",
                "config": {
                    "x_axis": "date",
                    "y_axis": "avg_score",
                    "group_by": "week",
                    "metrics": ["overall_performance", "pitch_accuracy", "scale_conformity", "timing_stability"],
                    "description": "Average user performance across all metrics over time"
                }
            },
            {
                "name": "Sessions Tracked",
                "type": "stats",
                "config": {
                    "metric": "session_count",
                    "description": "Total number of practice sessions tracked"
                }
            },
            {
                "name": "Skill Level Distribution",
                "type": "bar_chart",
                "config": {
                    "group_by": "skill_level",
                    "metric": "user_count",
                    "description": "Distribution of users by skill level"
                }
            },
            {
                "name": "Weekly Improvement Rate",
                "type": "line_chart",
                "config": {
                    "x_axis": "week",
                    "y_axis": "improvement_pct",
                    "description": "Week-over-week improvement percentage"
                }
            },
            {
                "name": "Practice Plan Completion",
                "type": "gauge",
                "config": {
                    "metric": "completion_rate",
                    "thresholds": {"warning": 0.6, "critical": 0.4},
                    "description": "Percentage of practice plans that are executed"
                }
            }
        ]
    },
    "ai_quality": {
        "name": "FretCoach AI Quality",
        "description": "Monitor AI coaching and recommendation quality metrics",
        "widgets": [
            {
                "name": "Coaching Helpfulness Over Time",
                "type": "line_chart",
                "config": {
                    "x_axis": "date",
                    "y_axis": "avg_score",
                    "data_source": "feedback_scores",
                    "filter": {"name": "coaching_helpfulness"},
                    "description": "Daily average coaching helpfulness score"
                }
            },
            {
                "name": "Recommendation Accuracy",
                "type": "line_chart",
                "config": {
                    "x_axis": "date",
                    "y_axis": "avg_score",
                    "data_source": "feedback_scores",
                    "filter": {"name": "recommendation_accuracy"},
                    "description": "Daily average recommendation accuracy score"
                }
            },
            {
                "name": "Average Helpfulness Score",
                "type": "stats",
                "config": {
                    "data_source": "feedback_scores",
                    "filter": {"name": "coaching_helpfulness"},
                    "description": "Overall average coaching helpfulness score"
                }
            },
            {
                "name": "Response Quality Distribution",
                "type": "histogram",
                "config": {
                    "data_source": "feedback_scores",
                    "filter": {"name": "coaching_helpfulness"},
                    "bins": 10,
                    "range": [0, 1],
                    "description": "Distribution of coaching helpfulness scores"
                }
            },
            {
                "name": "Score Trend by Skill Level",
                "type": "bar_chart",
                "config": {
                    "x_axis": "skill_level",
                    "y_axis": "avg_score",
                    "group_by": "date",
                    "description": "Helpfulness score trend by user skill level"
                }
            }
        ]
    },
    "system_health": {
        "name": "FretCoach System Health",
        "description": "Monitor system performance, costs, and errors",
        "widgets": [
            {
                "name": "Daily Trace Volume",
                "type": "line_chart",
                "config": {
                    "x_axis": "date",
                    "y_axis": "count",
                    "data_source": "traces",
                    "description": "Number of traces per day"
                }
            },
            {
                "name": "Error Rate",
                "type": "line_chart",
                "config": {
                    "x_axis": "date",
                    "y_axis": "rate",
                    "data_source": "traces",
                    "metric": "error_count / total_count * 100",
                    "description": "Percentage of traces with errors"
                }
            },
            {
                "name": "Daily Cost",
                "type": "line_chart",
                "config": {
                    "x_axis": "date",
                    "y_axis": "total_cost",
                    "data_source": "traces",
                    "filter": {"metadata.total_cost": {"$gt": 0}},
                    "description": "Daily API cost in USD"
                }
            },
            {
                "name": "Cost Per Session",
                "type": "stats",
                "config": {
                    "data_source": "traces",
                    "metric": "AVG(metadata.total_cost)",
                    "description": "Average cost per session (USD)"
                }
            },
            {
                "name": "Token Usage",
                "type": "line_chart",
                "config": {
                    "x_axis": "date",
                    "y_axis": "total_tokens",
                    "data_source": "traces",
                    "description": "Daily token usage"
                }
            },
            {
                "name": "LLM Latency",
                "type": "line_chart",
                "config": {
                    "x_axis": "date",
                    "y_axis": "avg_latency_ms",
                    "data_source": "spans",
                    "filter": {"name": {"$regex": ".*coaching.*"}},
                    "description": "Average LLM response latency (ms)"
                }
            }
        ]
    }
}


# ============================================================================
# ONLINE EVALUATION RULES
# ============================================================================

ONLINE_EVALUATION_RULES = [
    {
        "name": "Auto-score Coaching Helpfulness",
        "description": "Automatically scores coaching feedback quality using LLM-as-judge",
        "enabled": True,
        "sampling_rate": 0.1,  # Score 10% of traces
        "model": "gpt-4o-mini",
        "evaluation_type": "feedback_score",
        "score_name": "coaching_helpfulness",
        "prompt_template": """You are evaluating coaching feedback for a guitar learning app.

Context:
- Student skill level: {{skill_level}}
- Metrics: Pitch {{metrics.pitch:.0f}}%, Scale {{metrics.scale:.0f}}%, Timing {{metrics.timing:.0f}}%
- Weakest area: {{weakest_area}}
- Coaching feedback: "{{feedback}}"

Evaluate:
1. Does it correctly identify the weakest area?
2. Is the advice actionable and specific?
3. Is the tone encouraging and supportive?
4. Is it appropriate for the skill level?

Respond with JSON:
{{"score": <0.0-1.0>, "reason": "<brief explanation>"}}""",
        "variable_mapping": {
            "skill_level": "trace.metadata.skill_level",
            "metrics": "trace.metadata.session_metrics",
            "weakest_area": "trace.metadata.weakest_area",
            "feedback": "trace.output"
        }
    },
    {
        "name": "Safety & Moderation Check",
        "description": "Checks coaching feedback for safety issues",
        "enabled": True,
        "sampling_rate": 0.05,  # Sample 5% for cost efficiency
        "model": "gpt-4o-mini",
        "evaluation_type": "feedback_score",
        "score_name": "safety_score",
        "prompt_template": """Check if the following text is safe and appropriate for guitar learning:

"{{feedback}}"

Respond with JSON:
{{"safe": <true/false>, "risk_level": <0.0-1.0>, "reason": "<brief>"}}""",
        "variable_mapping": {
            "feedback": "trace.output"
        }
    },
    {
        "name": "Response Relevance Check",
        "description": "Evaluates if response addresses the user's weakest area",
        "enabled": True,
        "sampling_rate": 0.05,
        "model": "gpt-4o-mini",
        "evaluation_type": "feedback_score",
        "score_name": "relevance_score",
        "prompt_template": """Check if the coaching feedback addresses the weakest area.

Weakest area: {{weakest_area}}
Feedback: "{{feedback}}"

Is the feedback relevant to the weakest area? Does it provide specific, actionable advice?

Respond with JSON:
{{"relevant": <true/false>, "score": <0.0-1.0>, "reason": "<brief explanation>"}}""",
        "variable_mapping": {
            "weakest_area": "trace.metadata.weakest_area",
            "feedback": "trace.output"
        }
    },
    {
        "name": "Cost Anomaly Detection",
        "description": "Flags traces with unusually high costs",
        "enabled": True,
        "sampling_rate": 1.0,
        "model": "heuristic",
        "evaluation_type": "alert",
        "thresholds": {
            "max_cost_per_trace": 0.02,  # $0.02 max per trace
            "max_tokens_per_trace": 2000
        }
    }
]


# ============================================================================
# SETUP FUNCTIONS
# ============================================================================

def setup_online_evaluation_rules(project_name: str = "FretCoach") -> List[Dict]:
    """
    Set up online evaluation rules in Opik.

    Note: This creates the configuration. Some rules may need manual
    configuration in the Opik UI for full functionality.

    Args:
        project_name: The Opik project name (used for display)

    Returns:
        List of rule configurations
    """
    print("\n" + "=" * 60)
    print(f"Setting Up Online Evaluation Rules: {project_name}")
    print("=" * 60)

    results = []

    for rule in ONLINE_EVALUATION_RULES:
        print(f"\n📋 Rule: {rule['name']}")
        print(f"   Enabled: {rule['enabled']}")
        print(f"   Sampling Rate: {rule['sampling_rate']}")

        if rule['evaluation_type'] == 'feedback_score':
            print(f"   Score Name: {rule['score_name']}")
            print(f"   Model: {rule['model']}")

        results.append({
            "name": rule['name'],
            "status": "configured",
            "config": rule
        })

    # Save configuration
    config_file = "online_evaluation_rules.json"
    with open(config_file, "w") as f:
        json.dump(ONLINE_EVALUATION_RULES, f, indent=2)

    print(f"\n✅ Rules configuration saved to: {config_file}")
    print("\nTo activate in Opik UI:")
    print("1. Go to Project Settings → Evaluation Rules")
    print("2. Create new rule with the above configuration")
    print("3. Set sampling rate and enable the rule")

    return results


def setup_dashboards(project_name: str = "FretCoach") -> List[Dict]:
    """
    Set up production dashboards.

    Args:
        project_name: The Opik project name (used for display)

    Returns:
        List of dashboard configurations
    """
    print("\n" + "=" * 60)
    print(f"Creating Dashboard Configurations: {project_name}")
    print("=" * 60)

    results = []

    for dashboard_id, config in DASHBOARD_CONFIGS.items():
        print(f"\n📊 Dashboard: {config['name']}")
        print(f"   Widgets: {len(config['widgets'])}")

        for widget in config['widgets']:
            print(f"   - {widget['name']} ({widget['type']})")

        results.append({
            "id": dashboard_id,
            "name": config['name'],
            "status": "configured",
            "widget_count": len(config['widgets'])
        })

    # Save configurations
    config_file = "dashboard_configs.json"
    with open(config_file, "w") as f:
        json.dump(DASHBOARD_CONFIGS, f, indent=2)

    print(f"\n✅ Dashboard configurations saved to: {config_file}")
    print("\nTo create in Opik UI:")
    print("1. Go to Dashboards → Create New Dashboard")
    print("2. Add widgets using the configurations above")
    print("3. Link to FretCoach project")

    return results


def generate_monitoring_summary() -> Dict[str, Any]:
    """
    Generate a summary of all monitoring configurations.

    Returns:
        Complete monitoring configuration summary
    """
    return {
        "generated_at": datetime.now().isoformat(),
        "dashboards": list(DASHBOARD_CONFIGS.keys()),
        "evaluation_rules": [r['name'] for r in ONLINE_EVALUATION_RULES],
        "key_metrics": [
            "coaching_helpfulness",
            "recommendation_accuracy",
            "learning_progress_rate",
            "safety_score",
            "relevance_score",
            "total_cost",
            "total_tokens",
            "latency_ms"
        ],
        "sampling_rates": {
            "coaching_helpfulness": 0.1,
            "safety_check": 0.05,
            "relevance_check": 0.05,
            "cost_anomaly": 1.0
        }
    }


def main():
    """Main entry point for Phase 4 setup"""
    print("\n" + "=" * 70)
    print("PHASE 4: Production Monitoring Setup")
    print("=" * 70)
    print(f"Started: {datetime.now().isoformat()}")

    # Setup online evaluation rules
    rules = setup_online_evaluation_rules()

    # Setup dashboards
    dashboards = setup_dashboards()

    # Generate summary
    summary = generate_monitoring_summary()

    print("\n" + "=" * 70)
    print("PRODUCTION MONITORING SETUP COMPLETE")
    print("=" * 70)

    print("\n📊 Dashboards Configured:")
    for d in dashboards:
        print(f"   - {d['name']} ({d['widget_count']} widgets)")

    print("\n📋 Evaluation Rules Configured:")
    for r in rules:
        print(f"   - {r['name']}")

    print("\n📁 Generated Files:")
    print("   - online_evaluation_rules.json")
    print("   - dashboard_configs.json")

    print("\n✅ Next Steps:")
    print("1. Open Opik UI: https://www.comet.com/opik/")
    print("2. Navigate to your project")
    print("3. Create dashboards using configurations")
    print("4. Enable evaluation rules")
    print("5. Set up alerts for quality thresholds")

    return summary


if __name__ == "__main__":
    main()
