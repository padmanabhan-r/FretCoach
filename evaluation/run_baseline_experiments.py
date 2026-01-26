"""
Phase 3: Baseline Experiments for FretCoach

This script runs baseline experiments to establish current performance
before optimization. It provides immediate results for demonstration.

Usage:
    python evaluation/run_baseline_experiments.py
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
from evaluation.custom_metrics import CoachingHelpfulness


# ============================================================================
# COACHING TASK FUNCTIONS (Different Prompt Versions)
# ============================================================================

def coaching_task_v1(item: Dict) -> Dict[str, Any]:
    """Original production prompt (V1)"""
    input_data = item.get("input", {})
    metrics = input_data.get("metrics", {})
    weakest = input_data.get("weakest_area", "unknown")
    scale = input_data.get("scale_name", "unknown")

    prompt = f"""You are a direct guitar coach giving quick real-time feedback.

Current Performance:
- Pitch: {metrics.get('pitch', 0):.0f}%
- Scale: {metrics.get('scale', 0):.0f}%
- Timing: {metrics.get('timing', 0):.0f}%
Weakest: {weakest}

Format: "[What's good], but [what's weak] - [specific actionable fix]"

Feedback:"""

    response = _call_llm([
        {"role": "system", "content": "You are a direct guitar coach. Keep feedback to 1-2 sentences, max 30 words."},
        {"role": "user", "content": prompt}
    ])

    return {"output": response, "metadata": {"prompt_version": "v1"}}


def coaching_task_v2(item: Dict) -> Dict[str, Any]:
    """Structured metrics prompt (V2)"""
    input_data = item.get("input", {})
    metrics = input_data.get("metrics", {})
    weakest = input_data.get("weakest_area", "unknown")
    scale = input_data.get("scale_name", "unknown")
    skill = input_data.get("skill_level", "intermediate")

    prompt = f"""You are FretCoach, a guitar instructor.

Performance Analysis:
- Note accuracy (Pitch): {metrics.get('pitch', 0):.0f}%
- Scale navigation (Scale): {metrics.get('scale', 0):.0f}%
- Rhythm consistency (Timing): {metrics.get('timing', 0):.0f}%

Primary Challenge: {weakest}
Student Level: {skill}

Format: "[strength], but [weakness] - [specific drill]"
Max 30 words, encouraging tone.

Feedback:"""

    response = _call_llm([
        {"role": "system", "content": "You are a supportive guitar instructor. Provide structured, actionable feedback."},
        {"role": "user", "content": prompt}
    ])

    return {"output": response, "metadata": {"prompt_version": "v2"}}


def coaching_task_v3(item: Dict) -> Dict[str, Any]:
    """Learning science prompt (V3)"""
    input_data = item.get("input", {})
    metrics = input_data.get("metrics", {})
    weakest = input_data.get("weakest_area", "unknown")
    scale = input_data.get("scale_name", "unknown")

    prompt = f"""You are FretCoach, applying deliberate practice principles.

Performance:
- Pitch: {metrics.get('pitch', 0):.0f}% (note accuracy)
- Scale: {metrics.get('scale', 0):.0f}% (staying in scale)
- Timing: {metrics.get('timing', 0):.0f}% (rhythm)

Focus: {weakest}

Apply:
1. Highlight one strength
2. Identify the limiting factor
3. Suggest one specific drill

Format: "[strength], but [weakness] - try [specific drill]"
Max 30 words.

Feedback:"""

    response = _call_llm([
        {"role": "system", "content": "You are FretCoach using deliberate practice. Be specific and actionable."},
        {"role": "user", "content": prompt}
    ])

    return {"output": response, "metadata": {"prompt_version": "v3"}}


def coaching_task_v4(item: Dict) -> Dict[str, Any]:
    """Concise direct prompt (V4)"""
    input_data = item.get("input", {})
    metrics = input_data.get("metrics", {})
    weakest = input_data.get("weakest_area", "unknown")
    scale = input_data.get("scale_name", "unknown")

    prompt = f"""Scale: {scale}, Weakest: {weakest}
Pitch: {metrics.get('pitch', 0):.0f}%, Scale: {metrics.get('scale', 0):.0f}%, Timing: {metrics.get('timing', 0):.0f}%

One sentence feedback with specific technique:"""

    response = _call_llm([
        {"role": "system", "content": "You are a guitar coach. Be concise. Maximum 25 words. Always include a technique name."},
        {"role": "user", "content": prompt}
    ])

    return {"output": response, "metadata": {"prompt_version": "v4"}}


def _call_llm(messages: List[Dict], model: str = "gpt-4o-mini") -> str:
    """Call LLM with messages"""
    try:
        from openai import OpenAI
        client = OpenAI()

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=100
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"[Error: {str(e)}]"


def run_baseline_experiments(
    opik_client: Opik,
    dataset_name: str = "coaching_feedback_evaluation",
    model: str = "gpt-4o-mini",
    nb_samples: int = 20
) -> Dict[str, Any]:
    """
    Run baseline experiments to establish current performance
    """
    print("\n" + "="*70)
    print("BASELINE EXPERIMENTS - FretCoach Coaching Prompts")
    print("="*70)
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Dataset: {dataset_name}")
    print(f"Model: {model}")
    print(f"Samples: {nb_samples}")
    print("="*70)

    try:
        dataset = opik_client.get_dataset(dataset_name)
    except Exception as e:
        print(f"\n❌ Dataset not found: {dataset_name}")
        print("Run 'python evaluation/create_datasets.py' first")
        return {"error": str(e)}

    metric = CoachingHelpfulness(model=model)

    # Define experiments
    experiments = [
        ("Baseline V1 - Original", coaching_task_v1),
        ("Structured V2 - Metrics", coaching_task_v2),
        ("Learning Science V3", coaching_task_v3),
        ("Concise V4 - Direct", coaching_task_v4),
    ]

    results = []

    for name, task in experiments:
        print(f"\n📊 Running: {name}...")

        try:
            eval_result = evaluate(
                dataset=dataset,
                task=task,
                scoring_metrics=[metric],
                experiment_name=name,
                experiment_config={"prompt_version": name.split()[1], "model": model},
                nb_samples=nb_samples,
                verbose=0
            )

            scores = eval_result.aggregate_evaluation_scores()
            # Access aggregated_scores attribute and get mean from ScoreStatistics
            coaching_stats = scores.aggregated_scores.get("coaching_helpfulness")
            avg_score = coaching_stats.mean if coaching_stats else 0
            sample_count = len(coaching_stats.values) if coaching_stats else 0

            print(f"   ✅ Score: {avg_score:.4f} (n={sample_count})")

            results.append({
                "name": name,
                "avg_score": avg_score,
                "sample_count": sample_count,
                "variant": name.split()[1]
            })

        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({"name": name, "avg_score": 0, "error": str(e)})

    # Sort by score
    valid_results = [r for r in results if r.get("error") is None]
    sorted_results = sorted(valid_results, key=lambda x: x.get("avg_score", 0), reverse=True)

    # Summary
    print("\n" + "="*70)
    print("📈 BASELINE EXPERIMENT RESULTS")
    print("="*70)

    print("\n🏆 Rankings:")
    print("-" * 50)
    for i, r in enumerate(sorted_results, 1):
        marker = " ⭐ BEST" if i == 1 else ""
        print(f"  {i}. {r['name']}: {r.get('avg_score', 0):.4f}{marker}")

    if len(sorted_results) >= 2:
        best = sorted_results[0]
        worst = sorted_results[-1]
        improvement = best["avg_score"] - worst["avg_score"]
        improvement_pct = (improvement / worst["avg_score"]) * 100 if worst["avg_score"] > 0 else 0

        print(f"\n📊 Comparison:")
        print(f"   Best: {best['name']} = {best.get('avg_score', 0):.4f}")
        print(f"   Worst: {worst['name']} = {worst.get('avg_score', 0):.4f}")
        print(f"   Gap: {improvement:.4f} ({improvement_pct:.1f}%)")

    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "dataset": dataset_name,
        "model": model,
        "samples": nb_samples,
        "results": sorted_results
    }

    with open("baseline_experiments.json", "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n✅ Results saved to: baseline_experiments.json")

    return output


def main():
    """Main entry point"""
    print("\n" + "="*70)
    print("🎸 FretCoach Baseline Experiments")
    print("="*70)

    opik_client = Opik()
    result = run_baseline_experiments(opik_client)

    if "error" not in result:
        print("\n" + "="*70)
        print("✅ Experiments Complete!")
        print("="*70)
        print("\nNext Steps:")
        print("1. Review baseline_experiments.json")
        print("2. Run 'python evaluation/optimize_prompts.py' for full optimization")
        print("3. Deploy best prompt to production")
    else:
        print(f"\n❌ Error: {result['error']}")


if __name__ == "__main__":
    main()
