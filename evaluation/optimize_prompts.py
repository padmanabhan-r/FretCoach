"""
Phase 3: Agent Optimization for FretCoach

This script performs systematic prompt optimization using Opik's evaluate_prompt API.
It compares multiple prompt variations, identifies the best performer,
and quantifies the improvement.

Usage:
    python evaluation/optimize_prompts.py
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment
load_dotenv()

import opik
from opik import Opik
from opik.evaluation import evaluate_prompt
from evaluation.custom_metrics import CoachingHelpfulness, ResponseRelevance


# ============================================================================
# PROMPT VARIATIONS FOR OPTIMIZATION
# ============================================================================

# Current production prompt (baseline)
COACHING_PROMPT_V1 = [
    {"role": "system", "content": """You are a direct guitar coach giving quick real-time feedback.

Your feedback MUST be 1-2 sentences, maximum 30 words total.

Format: "[What's good], but [what's weak] - [specific actionable fix]"

Be direct, conversational, and vary your wording. Maximum 30 words."""}
]

# Version 2: More structured with explicit metrics interpretation
COACHING_PROMPT_V2 = [
    {"role": "system", "content": """You are FretCoach, a guitar instructor providing real-time feedback.

IMPORTANT: Your feedback must be 1-2 sentences, MAXIMUM 30 WORDS.

Format: "[strength], but [weakness] - [specific actionable fix with technique]"

Metric interpretations:
- Pitch Accuracy: How cleanly notes are fretted (low = finger pressure issues)
  → Fix: "ease finger pressure" or "focus on clean fretting"

- Scale Conformity: Playing correct scale notes (low = stuck or wrong notes)
  → Fix: "explore positions 5-7" or "move up the fretboard"

- Timing Stability: Consistency of note spacing (low = rushing/dragging)
  → Fix: "use a metronome" or "slow down and count"

Example: "Great pitch accuracy, but scale conformity needs work. Move up to position 7."""}
]

# Version 3: Learning science principles with specific drills
COACHING_PROMPT_V3 = [
    {"role": "system", "content": """You are FretCoach, applying deliberate practice principles.

Your feedback: 1-2 sentences, MAX 30 WORDS.

Follow this coaching framework:
1. HIGHLIGHT one strength (build confidence)
2. IDENTIFY the limiting factor (focus attention)
3. SUGGEST one specific drill (actionable practice)

Format: "[strength], but [weakness with %] - try [specific drill: technique + action]"

Example: "Great 85% pitch accuracy, but timing dropped to 65% - try metronome at 80 BPM"

Be encouraging, specific, and always provide a clear practice action."""}
]

# Version 4: Concise and direct with percentage focus
COACHING_PROMPT_V4 = [
    {"role": "system", "content": """You are FretCoach, a guitar coach.

Keep feedback SHORT: 1-2 sentences, 25 words max.

Required elements:
- ONE specific observation about performance
- ONE actionable fix with technique name

Format: "[observation] - [technique fix]"

Good examples:
- "Timing dipped to 60% - try counting out loud at 60 BPM"
- "Great scale coverage at 90% - now work on position changes"
- "Pitch issues at frets 2-3 - ease finger pressure"""}
]

# Version 5: Skill-level adaptive
COACHING_PROMPT_V5 = [
    {"role": "system", "content": """You are FretCoach, a supportive guitar instructor.

Feedback rules:
- 1-2 sentences, MAX 25 WORDS
- Match advice to skill level
- ALWAYS include specific technique name

For beginners: Focus on fundamentals, be extra encouraging
For intermediate: Add nuance, suggest position work
For advanced: Challenge with precision focus

Format: "[skill-appropriate observation] - [specific technique]"

Examples:
- Beginner: "Great start! Focus on clean fretting at the 3rd fret - press closer to the metal"
- Intermediate: "Good 75% pitch, but position changes are slowing you - practice position 5 transitions"
- Advanced: "Excellent 92% timing precision - now push for consistent dynamics at 90 BPM"""}
]


def get_prompt_messages_for_item(item: Dict, prompt: List[Dict]) -> List[Dict]:
    """Format the prompt messages for a specific dataset item"""
    input_data = item.get("input", {})
    metrics = input_data.get("metrics", {})
    weakest = input_data.get("weakest_area", "unknown")
    scale = input_data.get("scale_name", "unknown")
    skill = input_data.get("skill_level", "intermediate")

    # Build user message
    user_content = f"""Student Information:
- Scale: {scale}
- Skill Level: {skill}
- Pitch Accuracy: {metrics.get('pitch', 0):.0%}
- Scale Conformity: {metrics.get('scale', 0):.0%}
- Timing Stability: {metrics.get('timing', 0):.0%}
- Weakest Area: {weakest}

Provide feedback:"""

    # Combine system and user messages
    messages = [{"role": "system", "content": prompt[0]["content"]}]
    messages.append({"role": "user", "content": user_content})

    return messages


def evaluate_prompt_variant(
    opik_client: Opik,
    dataset_name: str,
    prompt: List[Dict],
    variant_name: str,
    model: str = "gpt-4o-mini",
    nb_samples: Optional[int] = None
) -> Dict[str, Any]:
    """Evaluate a single prompt variant using Opik's evaluate_prompt"""

    print(f"\n{'='*60}")
    print(f"Evaluating: {variant_name}")
    print(f"{'='*60}")

    try:
        dataset = opik_client.get_dataset(dataset_name)

        # Use custom task function that applies the prompt
        def task_fn(item):
            messages = get_prompt_messages_for_item(item, prompt)
            return _call_llm(messages, model)

        # Run evaluation
        result = evaluate_prompt(
            dataset=dataset,
            messages=prompt,
            model=model,
            scoring_metrics=[CoachingHelpfulness(model=model)],
            experiment_name=f"Prompt Optimization - {variant_name}",
            experiment_config={"variant": variant_name, "model": model},
            nb_samples=nb_samples,
            verbose=1
        )

        # Get aggregate score
        scores = result.aggregate_evaluation_scores()
        # Access aggregated_scores attribute and get mean from ScoreStatistics
        coaching_stats = scores.aggregated_scores.get("coaching_helpfulness")
        avg_score = coaching_stats.mean if coaching_stats else 0
        sample_count = len(coaching_stats.values) if coaching_stats else 0

        print(f"  -> Average Score: {avg_score:.4f}")
        print(f"  -> Samples Evaluated: {sample_count}")

        return {
            "name": variant_name,
            "avg_score": avg_score,
            "sample_count": sample_count,
            "prompt": prompt,
            "result": result
        }

    except Exception as e:
        print(f"  -> ERROR: {e}")
        return {
            "name": variant_name,
            "avg_score": 0,
            "sample_count": 0,
            "prompt": prompt,
            "error": str(e)
        }


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


def run_optimization(
    opik_client: Opik,
    dataset_name: str = "coaching_feedback_evaluation",
    model: str = "gpt-4o-mini"
) -> Dict[str, Any]:
    """
    Run comprehensive prompt optimization

    Returns:
        Dictionary with optimization results and best prompt
    """

    print("\n" + "="*70)
    print("PHASE 3: AGENT OPTIMIZATION - FretCoach Coaching Prompts")
    print("="*70)
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Dataset: {dataset_name}")
    print(f"Model: {model}")
    print("="*70)

    # Define all prompt variants to test
    variants = [
        ("V1 - Current Production", COACHING_PROMPT_V1),
        ("V2 - Structured Metrics", COACHING_PROMPT_V2),
        ("V3 - Learning Science", COACHING_PROMPT_V3),
        ("V4 - Concise Direct", COACHING_PROMPT_V4),
        ("V5 - Skill Adaptive", COACHING_PROMPT_V5),
    ]

    # Evaluate each variant
    results = []
    for name, prompt in variants:
        result = evaluate_prompt_variant(
            opik_client=opik_client,
            dataset_name=dataset_name,
            prompt=prompt,
            variant_name=name,
            model=model
        )
        results.append(result)

    # Find best variant
    valid_results = [r for r in results if r.get("error") is None and r.get("avg_score", 0) > 0]
    if valid_results:
        best = max(valid_results, key=lambda x: x.get("avg_score", 0))
        baseline = min(valid_results, key=lambda x: x.get("avg_score", 1))

        improvement = best["avg_score"] - baseline["avg_score"]
        improvement_pct = (improvement / baseline["avg_score"]) * 100 if baseline["avg_score"] > 0 else 0
    else:
        best = {"name": "None", "avg_score": 0, "prompt": []}
        baseline = {"name": "None", "avg_score": 0}
        improvement = 0
        improvement_pct = 0

    # Print summary
    print("\n" + "="*70)
    print("OPTIMIZATION RESULTS SUMMARY")
    print("="*70)

    print("\n📊 All Variants Ranked:")
    print("-" * 50)
    sorted_results = sorted(valid_results, key=lambda x: x.get("avg_score", 0), reverse=True)
    for i, r in enumerate(sorted_results, 1):
        marker = " 🏆 BEST" if r == best else ""
        print(f"  {i}. {r['name']}: {r.get('avg_score', 0):.4f}{marker}")

    print("\n" + "="*70)
    print("🏆 WINNING PROMPT")
    print("="*70)
    print(f"Name: {best['name']}")
    print(f"Score: {best.get('avg_score', 0):.4f}")
    print(f"\nPrompt Content:")
    print("-" * 50)
    for msg in best.get("prompt", []):
        print(f"[{msg['role'].upper()}]")
        print(msg['content'][:200] + "..." if len(msg['content']) > 200 else msg['content'])
        print()

    print("="*70)
    print("📈 IMPROVEMENT METRICS")
    print("="*70)
    print(f"Baseline (Worst): {baseline['name']} = {baseline.get('avg_score', 0):.4f}")
    print(f"Best: {best['name']} = {best.get('avg_score', 0):.4f}")
    print(f"Absolute Improvement: +{improvement:.4f}")
    print(f"Relative Improvement: +{improvement_pct:.1f}%")

    # Save results
    optimization_result = {
        "timestamp": datetime.now().isoformat(),
        "dataset": dataset_name,
        "model": model,
        "best_variant": best['name'],
        "best_score": best.get('avg_score', 0),
        "baseline_score": baseline.get('avg_score', 0),
        "improvement_absolute": improvement,
        "improvement_percentage": improvement_pct,
        "all_results": [
            {"name": r['name'], "score": r.get('avg_score', 0)} for r in sorted_results
        ],
        "best_prompt": best.get("prompt", [])
    }

    # Save to file
    with open("optimization_results.json", "w") as f:
        json.dump(optimization_result, f, indent=2, default=str)

    print(f"\n✅ Results saved to: optimization_results.json")

    return optimization_result


def deploy_best_prompt(optimization_result: Dict[str, Any]) -> None:
    """
    Generate production-ready code for the best prompt
    """
    best_prompt = optimization_result.get("best_prompt", [])

    if not best_prompt:
        print("No best prompt found to deploy")
        return

    # Generate the updated live_coach_service.py code
    print("\n" + "="*70)
    print("📝 DEPLOYMENT: Update to live_coach_service.py")
    print("="*70)

    # Extract system prompt
    system_prompt = best_prompt[0]["content"] if best_prompt else ""

    deployment_code = f'''
# Auto-generated by optimize_prompts.py on {optimization_result["timestamp"]}
# Best Variant: {optimization_result["best_variant"]}
# Score: {optimization_result["best_score"]:.4f} (+{optimization_result["improvement_percentage"]:.1f}%)

COACHING_SYSTEM_PROMPT = """{system_prompt.strip()}
"""
'''

    with open("optimized_coaching_prompt.py", "w") as f:
        f.write(deployment_code)

    print(f"\n✅ Optimized prompt saved to: optimized_coaching_prompt.py")
    print("\nTo deploy:")
    print("1. Copy the COACHING_SYSTEM_PROMPT to live_coach_service.py")
    print("2. Replace the existing COACHING_SYSTEM_PROMPT")
    print("3. Deploy to production")


def main():
    """Main entry point for Phase 3 optimization"""
    print("\n" + "="*70)
    print("🎸 FretCoach Phase 3: Agent Optimization")
    print("="*70)

    # Initialize Opik client
    opik_client = Opik()

    # Run optimization
    result = run_optimization(opik_client)

    # Generate deployment files
    deploy_best_prompt(result)

    print("\n" + "="*70)
    print("✅ Phase 3 Complete!")
    print("="*70)
    print("\nNext Steps:")
    print("1. Review optimization_results.json")
    print("2. Copy optimized prompt to live_coach_service.py")
    print("3. Deploy to production")
    print("4. Continue to Phase 4: Production Monitoring")


if __name__ == "__main__":
    main()
