"""
Run Systematic Experiments for FretCoach AI

This script runs experiments comparing different prompt versions
and configurations to find optimal settings.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment
load_dotenv()

import opik
from opik import Opik
from opik.evaluation import evaluate
from evaluation.custom_metrics import CoachingHelpfulness, RecommendationAccuracy


def coaching_task_v1(item: Dict) -> str:
    """Original coaching prompt (baseline)"""
    metrics = item["input"]["metrics"]
    weakest = item["input"]["weakest_area"]

    prompt = f"""You are a guitar coach. Provide feedback on the student's performance.

Performance:
- Pitch: {metrics.get('pitch', 0):.0%}
- Scale: {metrics.get('scale', 0):.0%}
- Timing: {metrics.get('timing', 0):.0%}

Weakest area: {weakest}

Provide encouraging, specific feedback in 1-2 sentences:"""

    # Call LLM (simplified - in production use actual LLM)
    return _call_llm(prompt, system_prompt="You are a supportive guitar coach.")


def coaching_task_v2(item: Dict) -> str:
    """More specific and structured feedback format"""
    metrics = item["input"]["metrics"]
    weakest = item["input"]["weakest_area"]
    skill = item["input"]["skill_level"]

    prompt = f"""You are FretCoach, a guitar instructor.

Current Performance:
- Pitch (note accuracy): {metrics.get('pitch', 0):.0%}
- Scale (staying in scale): {metrics.get('scale', 0):.0%}
- Timing (rhythm): {metrics.get('timing', 0):.0%}

Primary Challenge: {weakest}
Student Level: {skill}

Format: "[strength], but [weakness] - [actionable fix]"
Keep to 1-2 sentences, max 30 words. Be encouraging."""

    return _call_llm(prompt)


def coaching_task_v3(item: Dict) -> str:
    """Learning science principles applied"""
    metrics = item["input"]["metrics"]
    weakest = item["input"]["weakest_area"]
    skill = item["input"]["skill_level"]

    prompt = f"""You are FretCoach, applying deliberate practice principles.

Performance Analysis:
- Note accuracy (Pitch): {metrics.get('pitch', 0):.0%}
- Scale navigation (Scale): {metrics.get('scale', 0):.0%}
- Rhythm consistency (Timing): {metrics.get('timing', 0):.0%}

Focus Area: {weakest}
Skill Level: {skill}

Apply these principles:
1. Highlight one strength (build confidence)
2. Identify the limiting factor (focus attention)
3. Suggest one specific drill (actionable practice)

Format: "[strength], but [weakness] - try [specific drill]"
Max 30 words, encouraging tone."""

    return _call_llm(prompt)


def _call_llm(user_prompt: str, system_prompt: str = None) -> str:
    """Helper to call LLM (simplified for demo)"""
    try:
        from openai import OpenAI
        client = OpenAI()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=100
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"[Error: {str(e)}]"


def run_coaching_experiments(opik_client: Opik, dataset_name: str = "coaching_feedback_evaluation"):
    """Run experiments comparing coaching prompt versions"""

    print("\n" + "=" * 60)
    print("EXPERIMENT: Coaching Prompt Comparison")
    print("=" * 60)

    try:
        dataset = opik_client.get_dataset(dataset_name)
    except Exception as e:
        print(f"Dataset '{dataset_name}' not found. Run create_datasets.py first.")
        return None

    metric = CoachingHelpfulness(model="gpt-4o-mini")

    # Define experiments
    experiments = [
        ("Coaching V1 - Baseline", coaching_task_v1),
        ("Coaching V2 - Structured", coaching_task_v2),
        ("Coaching V3 - Learning Science", coaching_task_v3),
    ]

    results = []

    for name, task in experiments:
        print(f"\nRunning: {name}...")

        try:
            eval_result = evaluate(
                dataset=dataset,
                task=task,
                scoring_metrics=[metric],
                experiment_name=name,
                experiment_config={"prompt_version": name.split()[-1], "model": "gpt-4o-mini"}
            )

            # Get aggregate score
            scores = eval_result.aggregate_evaluation_scores()
            avg_score = scores.get("coaching_helpfulness", {}).get("value", 0)

            print(f"   -> Avg Score: {avg_score:.3f}")

            results.append({
                "name": name,
                "avg_score": avg_score,
                "sample_count": scores.get("coaching_helpfulness", {}).get("count", 0)
            })

        except Exception as e:
            print(f"   -> Error: {e}")
            results.append({"name": name, "avg_score": 0, "error": str(e)})

    return results


def run_recommendation_experiments(opik_client: Opik, dataset_name: str = "recommendation_accuracy_evaluation"):
    """Run experiments comparing recommendation approaches"""

    print("\n" + "=" * 60)
    print("EXPERIMENT: Recommendation Accuracy")
    print("=" * 60)

    try:
        dataset = opik_client.get_dataset(dataset_name)
    except Exception as e:
        print(f"Dataset '{dataset_name}' not found. Run create_datasets.py first.")
        return None

    metric = RecommendationAccuracy()

    # For recommendations, we evaluate existing outputs
    # This shows the accuracy of past recommendations
    print("\nEvaluating historical recommendation accuracy...")

    try:
        eval_result = evaluate(
            dataset=dataset,
            task=lambda item: json.dumps(item["output"]),
            scoring_metrics=[metric],
            experiment_name="Recommendation Accuracy - Historical",
            experiment_config={"evaluation_type": "historical"}
        )

        scores = eval_result.aggregate_evaluation_scores()
        avg_score = scores.get("recommendation_accuracy", {}).get("value", 0)

        print(f"   -> Historical Recommendation Accuracy: {avg_score:.3f}")

        return [{"name": "Historical Accuracy", "avg_score": avg_score}]

    except Exception as e:
        print(f"   -> Error: {e}")
        return [{"name": "Historical Accuracy", "avg_score": 0, "error": str(e)}]


def compare_models(opik_client: Opik, dataset_name: str = "coaching_feedback_evaluation"):
    """Compare different models for coaching"""

    print("\n" + "=" * 60)
    print("EXPERIMENT: Model Comparison")
    print("=" * 60)

    try:
        dataset = opik_client.get_dataset(dataset_name)
    except Exception as e:
        print(f"Dataset '{dataset_name}' not found.")
        return None

    models = [
        ("gpt-4o-mini", "gpt-4o-mini"),
        ("gemini-2.5-flash", "gemini-2.5-flash"),
    ]

    results = []

    for model_name, api_model in models:
        print(f"\nTesting with {model_name}...")

        metric = CoachingHelpfulness(model=api_model)

        try:
            eval_result = evaluate(
                dataset=dataset,
                task=lambda item: coaching_task_v2(item),  # Use V2 prompt
                scoring_metrics=[metric],
                experiment_name=f"Model - {model_name}",
                experiment_config={"model": api_model, "prompt": "v2"}
            )

            scores = eval_result.aggregate_evaluation_scores()
            avg_score = scores.get("coaching_helpfulness", {}).get("value", 0)

            print(f"   -> Avg Score: {avg_score:.3f}")

            results.append({
                "name": model_name,
                "avg_score": avg_score
            })

        except Exception as e:
            print(f"   -> Error: {e}")
            results.append({"name": model_name, "avg_score": 0, "error": str(e)})

    return results


def main():
    """Main entry point for experiments"""
    print("=" * 60)
    print("FretCoach Opik Experiments")
    print("=" * 60)
    print(f"Started: {datetime.now().isoformat()}")

    # Initialize Opik client
    opik_client = Opik()

    # Run experiments
    coaching_results = run_coaching_experiments(opik_client)
    recommendation_results = run_recommendation_experiments(opik_client)
    model_results = compare_models(opik_client)

    # Summary
    print("\n" + "=" * 60)
    print("EXPERIMENT SUMMARY")
    print("=" * 60)

    if coaching_results:
        print("\nCoaching Prompt Comparison:")
        best = max(coaching_results, key=lambda x: x.get("avg_score", 0))
        for r in coaching_results:
            score = r.get("avg_score", 0)
            marker = " <-- BEST" if r == best else ""
            print(f"  {r['name']}: {score:.3f}{marker}")

    if model_results:
        print("\nModel Comparison:")
        for r in model_results:
            print(f"  {r['name']}: {r.get('avg_score', 0):.3f}")

    print("\n" + "=" * 60)
    print("Experiments complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
