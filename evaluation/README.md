# FretCoach Evaluation Framework

## Overview
This package provides comprehensive evaluation capabilities for FretCoach AI services using Opik.

## Structure

```
evaluation/
├── __init__.py           # Package exports
├── custom_metrics.py     # Domain-specific evaluation metrics
├── create_datasets.py    # Dataset generation from production data
├── run_experiments.py    # Experiment runner for prompt/model comparison
├── setup_online_rules.py # Production monitoring rules and dashboards
└── README.md            # This file
```

## Quick Start

### 1. Create Evaluation Datasets
```bash
python evaluation/create_datasets.py
```

This creates three datasets in Opik:
- `coaching_feedback_evaluation` - For coaching quality evaluation
- `recommendation_accuracy_evaluation` - For recommendation accuracy
- `learning_progress_tracking` - For progress rate measurement

### 2. Run Experiments
```bash
python evaluation/run_experiments.py
```

Compares:
- 3 coaching prompt versions
- Historical recommendation accuracy
- Model performance (gpt-4o-mini vs gemini-2.5-flash)

### 3. Setup Production Monitoring
```bash
python evaluation/setup_online_rules.py
```

Creates:
- Auto-scoring rules for production traces
- Learning progress dashboard
- AI quality monitoring dashboard
- System health dashboard

## Custom Metrics

### CoachingHelpfulness
Evaluates if coaching feedback is effective for guitar learners.

```python
from evaluation import CoachingHelpfulness

metric = CoachingHelpfulness(model="gpt-4o-mini")
result = metric.score(
    input={
        "metrics": {"pitch": 0.75, "scale": 0.60, "timing": 0.85},
        "weakest_area": "scale",
        "skill_level": "intermediate"
    },
    output="Great timing, but scale conformity needs work. Try positions 5-7."
)
# result.value: 0.0-1.0
# result.reason: Explanation of score
```

### RecommendationAccuracy
Measures if recommendations lead to improvement.

```python
from evaluation import RecommendationAccuracy

metric = RecommendationAccuracy()
result = metric.score(
    input={
        "user_history": {"pitch_accuracy": 0.70},
        "recommended_focus": "pitch"
    },
    output={"execution_metrics": {"pitch_accuracy": 0.82}}
)
# result.value: 0.0-1.0 (improvement-based)
```

## Integration with Opik

### Manual Evaluation
```python
import opik
from opik.evaluation import evaluate
from evaluation import CoachingHelpfulness

opik_client = opik.Opik()
dataset = opik_client.get_dataset("coaching_feedback_evaluation")

metric = CoachingHelpfulness()
results = evaluate(
    dataset=dataset,
    task=my_coaching_function,
    scoring_metrics=[metric],
    experiment_name="My Experiment"
)
```

### Online Evaluation
Configure rules in Opik UI:
1. Go to Project → Rules
2. Add rule with metric prompt
3. Set sampling rate (1.0 = 100%)
4. Configure variable mapping to trace fields

## Supported Trace Fields

The metrics expect these fields in Opik traces:

### Coaching Traces
- `trace.metadata.session_metrics` - {pitch, scale, timing}
- `trace.metadata.weakest_area` - "pitch", "scale", or "timing"
- `trace.metadata.skill_level` - "beginner", "intermediate", "advanced"
- `trace.output` - The coaching feedback text

### Recommendation Traces
- `trace.metadata.user_context` - Historical metrics
- `trace.input.recommended_focus` - Focus area
- `trace.output.execution_metrics` - Post-recommendation metrics

### Cost Tracking
- `trace.metadata.total_cost` - USD cost
- `trace.metadata.total_tokens` - Token count
- `trace.metadata.model` - Model name

## Running in CI/CD

```yaml
# .github/workflows/eval.yml
- name: Run Evaluation
  run: |
    python evaluation/run_experiments.py
    echo "::set-output name=score::$(cat results/latest_score.txt)"
```

## Metrics Reference

| Metric | Type | Description | Score Range |
|--------|------|-------------|-------------|
| CoachingHelpfulness | LLM-as-Judge | Feedback quality | 0.0-1.0 |
| RecommendationAccuracy | Heuristic | Improvement tracking | 0.0-1.0 |
| PracticePlanCompletionRate | Heuristic | Plan execution rate | 0.0-1.0 |
| LearningProgressRate | Heuristic | Velocity measurement | 0.0-1.0 |
| ResponseRelevance | LLM-as-Judge | Context alignment | 0.0-1.0 |
| SafetyModeration | API | Safety check | 0.0-1.0 |
