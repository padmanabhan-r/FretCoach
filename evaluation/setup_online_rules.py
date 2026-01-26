"""
Setup Online Evaluation Rules for Production Monitoring

This script configures Opik to automatically evaluate traces in production.
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

import opik
from opik import Opik


def create_online_evaluation_rules(opik_client: Opik, project_name: str = "FretCoach"):
    """Create online evaluation rules for production monitoring"""

    print("=" * 60)
    print("Setting Up Online Evaluation Rules")
    print("=" * 60)

    project = opik_client.get_project(project_name)

    rules = []

    # Rule 1: Coaching Helpfulness Auto-Scorer
    rule1 = {
        "name": "Auto-score coaching helpfulness",
        "description": "Automatically scores coaching feedback helpfulness for all traces",
        "sampling_rate": 1.0,  # 100% of traces
        "model": "gpt-4o-mini",
        "prompt": """You are evaluating coaching feedback for a guitar learning app.

Context:
- Student skill level: {{skill_level}}
- Metrics: Pitch {{metrics.pitch}}%, Scale {{metrics.scale}}%, Timing {{metrics.timing}}%
- Weakest area: {{weakest_area}}
- Coaching feedback: "{{output}}"

Evaluate:
1. Does it correctly identify the weakest area?
2. Is the advice actionable?
3. Is the tone encouraging?

Respond with JSON:
{{"score": <0.0-1.0>, "reason": "<brief>"}}""",
        "variable_mapping": {
            "skill_level": "trace.metadata.skill_level",
            "metrics": "trace.metadata.session_metrics",
            "weakest_area": "trace.metadata.weakest_area",
            "output": "trace.output"
        },
        "score_definition": {
            "name": "coaching_helpfulness_score",
            "range": [0.0, 1.0]
        }
    }

    # Rule 2: Safety & Moderation
    rule2 = {
        "name": "Safety check for coaching feedback",
        "description": "Checks coaching feedback for safety issues",
        "sampling_rate": 1.0,
        "model": "gpt-4o-mini",
        "prompt": """Check if the following text is safe and appropriate for guitar learning:

"{{output}}"

Respond with JSON:
{{"safe": <true/false>, "risk_level": <0.0-1.0>}}""",
        "variable_mapping": {
            "output": "trace.output"
        },
        "score_definition": {
            "name": "safety_score",
            "range": [0.0, 1.0]
        }
    }

    # Rule 3: Response Relevance
    rule3 = {
        "name": "Check response relevance",
        "description": "Evaluates if response addresses the user's weakest area",
        "sampling_rate": 0.5,  # 50% for cost optimization
        "model": "gpt-4o-mini",
        "prompt": """Check if the coaching feedback addresses the weakest area.

Weakest area: {{weakest_area}}
Feedback: "{{output}}"

Is the feedback relevant to the weakest area? Respond with JSON:
{{"relevant": <true/false>, "score": <0.0-1.0>}}""",
        "variable_mapping": {
            "weakest_area": "trace.metadata.weakest_area",
            "output": "trace.output"
        },
        "score_definition": {
            "name": "relevance_score",
            "range": [0.0, 1.0]
        }
    }

    # Rule 4: Cost Efficiency Check
    rule4 = {
        "name": "Cost efficiency monitoring",
        "description": "Flags traces with unusually high costs",
        "sampling_rate": 1.0,
        "model": "heuristic",  # No LLM needed
        "prompt": None,
        "variable_mapping": {
            "total_cost": "trace.metadata.total_cost",
            "total_tokens": "trace.metadata.total_tokens"
        },
        "score_definition": {
            "name": "cost_efficiency",
            "range": [0.0, 1.0],
            "heuristic": "if total_cost > 0.01: return 0.5 else: return 1.0"
        }
    }

    all_rules = [rule1, rule2, rule3, rule4]

    for rule in all_rules:
        try:
            # Create rule via Opik API
            created = opik_client.api_client.create_evaluation_rule(
                project_id=project.id,
                name=rule["name"],
                description=rule["description"],
                sampling_rate=rule["sampling_rate"],
                model=rule.get("model"),
                prompt=rule.get("prompt"),
                variable_mapping=rule["variable_mapping"],
                score_definition=rule["score_definition"]
            )
            print(f"Created rule: {rule['name']}")
            rules.append({"name": rule["name"], "status": "created"})
        except Exception as e:
            # Rule might already exist or API different
            print(f"Note: {rule['name']} - {str(e)}")
            rules.append({"name": rule["name"], "status": "skipped", "error": str(e)})

    return rules


def create_dashboards(opik_client: Opik, project_name: str = "FretCoach"):
    """Create production dashboards for monitoring"""

    print("\n" + "=" * 60)
    print("Creating Production Dashboards")
    print("=" * 60)

    dashboards = []

    # Dashboard 1: Learning Progress
    dash1 = {
        "name": "FretCoach Learning Progress",
        "description": "Track user improvement over time",
        "widgets": [
            {
                "type": "line_chart",
                "name": "Avg Performance Over Time",
                "query": "SELECT date_trunc('day', trace.created_at) as date, AVG(trace.metadata.overall_performance) as avg_score FROM traces WHERE project_id = ? GROUP BY date ORDER BY date",
                "metrics": ["avg_score"]
            },
            {
                "type": "stats",
                "name": "Total Sessions",
                "query": "SELECT COUNT(*) as count FROM traces WHERE trace.name = 'live-coach-feedback'"
            },
            {
                "type": "bar_chart",
                "name": "Skill Level Distribution",
                "query": "SELECT trace.metadata.skill_level as skill, COUNT(*) as count FROM traces GROUP BY skill"
            }
        ]
    }

    # Dashboard 2: AI Quality Monitoring
    dash2 = {
        "name": "FretCoach AI Quality",
        "description": "Monitor AI coaching and recommendation quality",
        "widgets": [
            {
                "type": "line_chart",
                "name": "Coaching Helpfulness Over Time",
                "query": "SELECT date_trunc('day', trace.created_at) as date, AVG(feedback_scores.value) as avg_score FROM traces JOIN feedback_scores ON traces.id = feedback_scores.trace_id WHERE feedback_scores.name = 'coaching_helpfulness_score' GROUP BY date"
            },
            {
                "type": "stats",
                "name": "Avg Helpfulness Score",
                "query": "SELECT AVG(feedback_scores.value) as avg FROM feedback_scores WHERE name = 'coaching_helpfulness_score'"
            },
            {
                "type": "line_chart",
                "name": "Cost Per Session",
                "query": "SELECT date_trunc('day', trace.created_at) as date, SUM(trace.metadata.total_cost) as daily_cost FROM traces GROUP BY date"
            }
        ]
    }

    # Dashboard 3: System Health
    dash3 = {
        "name": "FretCoach System Health",
        "description": "Monitor system performance and errors",
        "widgets": [
            {
                "type": "line_chart",
                "name": "Trace Volume",
                "query": "SELECT date_trunc('hour', created_at) as hour, COUNT(*) as count FROM traces GROUP BY hour"
            },
            {
                "type": "stats",
                "name": "Error Rate",
                "query": "SELECT COUNT(CASE WHEN error IS NOT NULL THEN 1 END) * 100.0 / COUNT(*) as rate FROM traces"
            },
            {
                "type": "line_chart",
                "name": "Avg Latency (ms)",
                "query": "SELECT date_trunc('minute', created_at) as minute, AVG(span.metadata.duration_ms) as avg_latency FROM spans WHERE span.name = 'generate_coaching_feedback' GROUP BY minute"
            }
        ]
    }

    all_dashboards = [dash1, dash2, dash3]

    for dash in all_dashboards:
        try:
            created = opik_client.create_dashboard(
                name=dash["name"],
                description=dash["description"],
                project_id=opik_client.get_project(project_name).id
            )
            print(f"Created dashboard: {dash['name']}")
            dashboards.append({"name": dash["name"], "status": "created"})
        except Exception as e:
            print(f"Note: {dash['name']} - {str(e)}")
            dashboards.append({"name": dash["name"], "status": "skipped", "error": str(e)})

    return dashboards


def main():
    """Main entry point"""
    print("=" * 60)
    print("FretCoach Online Evaluation Setup")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)

    # Initialize Opik client
    opik_client = Opik()

    # Create rules
    rules = create_online_evaluation_rules(opik_client)

    # Create dashboards
    dashboards = create_dashboards(opik_client)

    # Summary
    print("\n" + "=" * 60)
    print("SETUP COMPLETE")
    print("=" * 60)

    print(f"\nRules Created: {len([r for r in rules if r['status'] == 'created'])}")
    print(f"Dashboards Created: {len([d for d in dashboards if d['status'] == 'created'])}")

    print("\nNext Steps:")
    print("1. Visit Opik UI to configure dashboard widgets")
    print("2. Adjust sampling rates as needed")
    print("3. Set up alerts for quality thresholds")


if __name__ == "__main__":
    main()
