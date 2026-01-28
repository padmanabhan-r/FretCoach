# FretCoach Hub Agent Evaluation

This directory contains evaluation scripts and metrics for the FretCoach Hub LangGraph agent.

## Overview

The evaluation system tests the AI coach agent using production traces to ensure:
- Response quality and relevance
- Accurate practice plan generation
- Helpful and actionable recommendations
- No hallucinations or unsupported claims

## Dataset

**Name:** `FretCoach Hub AI Coach Chat`

The dataset contains 10 real production traces from the FretCoach Hub web application. Each item includes:
- User queries (input messages)
- Agent responses (expected outputs)
- Full conversation context
- Tool execution traces
- Metadata and usage statistics

## Evaluation Metrics

### Built-in Opik Metrics

1. **Answer Relevance**
   - Measures how relevant the agent's response is to the user's query
   - Score: 0-1 (higher is better)

2. **Hallucination Detection**
   - Detects if the response contains unsupported or fabricated information
   - Score: 0-1 (higher means more grounded in context)

### Custom Metrics

3. **Practice Plan Quality** (`metrics/practice_plan_quality.py`)
   - Validates practice plan JSON structure
   - Checks required fields: focus_area, current_score, suggested_scale, etc.
   - Validates data types and value ranges
   - Score: 0-1 (1.0 = perfect practice plan)

4. **Response Completeness** (`metrics/response_completeness.py`)
   - Evaluates if responses are helpful and actionable
   - Checks for error indicators
   - Measures response detail and actionability
   - Score: 0-1 (higher is more complete)

## Files

```
evaluations/
├── README.md                       # This file
├── inspect_dataset.py              # Inspect dataset structure
├── evaluate_agent.py               # Main evaluation script
└── metrics/
    ├── __init__.py                 # Metrics module
    ├── practice_plan_quality.py    # Custom metric for practice plans
    └── response_completeness.py    # Custom metric for response quality
```

## Usage

### 1. Set Environment Variables

```bash
export OPIK_API_KEY="your_opik_api_key"
export OPIK_WORKSPACE="your_workspace"
```

These should already be set if you're running the web backend.

### 2. Inspect Dataset

To understand the dataset structure:

```bash
cd /Users/paddy/Documents/Github/FretCoach
source .venv/bin/activate
cd evaluations/web-backend
python inspect_dataset.py
```

Or use the run script:
```bash
cd /Users/paddy/Documents/Github/FretCoach
./evaluations/web-backend/run_evaluation.sh
```

### 3. Run Evaluation

To run the full evaluation (easiest method):

```bash
cd /Users/paddy/Documents/Github/FretCoach
./evaluations/web-backend/run_evaluation.sh
```

This script automatically:
- Loads environment variables from `.env` at project root
- Activates the virtual environment
- Runs the evaluation
- Shows progress and results

This will:
1. Load the dataset from Opik
2. Run the agent on each test case
3. Apply all 4 evaluation metrics
4. Log results to Opik dashboard

### 4. View Results

After running the evaluation:
1. Open Opik dashboard
2. Navigate to **Experiments**
3. Open **FretCoach Hub Agent Evaluation v1**
4. Review scores, compare with baselines, and analyze failures

## Evaluation Task Flow

For each dataset item, the evaluation:

1. **Extract** the user's query from the conversation
2. **Invoke** the agent with a fresh conversation (no thread state)
3. **Capture** the agent's response and tool calls
4. **Score** the response using all 4 metrics
5. **Log** results with input, output, reference, and context

## Metrics Explained

### When Practice Plan Quality Applies

This metric only scores responses that contain practice plan JSON. If no practice plan is found, it scores 0.0 with reason "No practice plan JSON found".

For responses with practice plans, it validates:
- JSON is parseable
- All required fields present
- Field types are correct
- Values are reasonable (e.g., score 0-100)
- Exercises list is non-empty

### Response Completeness Scoring

- **1.0** - Complete, actionable, and detailed (≥100 chars)
- **0.8** - Actionable but could be more detailed
- **0.7** - Detailed but lacks clear action items
- **0.6** - Could be more complete and actionable
- **0.4** - Too short (<50 chars)
- **0.2** - Contains error indicators
- **0.0** - Empty or error during evaluation

## Iterating on the Agent

After running evaluations:

1. **Analyze failures** - Look at low-scoring items
2. **Identify patterns** - Common issues across test cases
3. **Update prompts/logic** - Improve system prompts or tools
4. **Re-run evaluation** - Use same dataset to measure improvement
5. **Compare experiments** - Track progress over iterations

## Adding New Metrics

To add a custom metric:

1. Create a new file in `metrics/` directory
2. Extend `opik.evaluation.metrics.base_metric.BaseMetric`
3. Implement the `score()` method
4. Return `score_result.ScoreResult` with value (0-1) and reason
5. Add to `metrics/__init__.py`
6. Add to metrics list in `evaluate_agent.py`

Example:

```python
from opik.evaluation.metrics import base_metric, score_result

class MyCustomMetric(base_metric.BaseMetric):
    def __init__(self, name: str = "my_metric"):
        super().__init__(name=name)
        self.name = name

    def score(self, output: str, **kwargs):
        # Your scoring logic here
        return score_result.ScoreResult(
            name=self.name,
            value=0.85,
            reason="Explanation of score"
        )
```

## Best Practices

1. **Version your experiments** - Use descriptive names like "v1", "v2", "prompt-update-v3"
2. **Keep dataset stable** - Don't modify the dataset between experiment runs
3. **Document changes** - Note what changed between experiment versions
4. **Track regressions** - Ensure new changes don't hurt existing metrics
5. **Run regularly** - Evaluate after significant code changes

## Troubleshooting

### "Dataset not found"
- Check `OPIK_API_KEY` and `OPIK_WORKSPACE` are set
- Verify dataset name matches exactly: "FretCoach Hub AI Coach Chat"

### "Module not found" errors
- Ensure you're running from `/web/web-backend` directory
- Activate the virtual environment first

### Agent invocation fails
- Check database connection environment variables
- Verify LLM API keys (Google Gemini, Anthropic)
- Review `langgraph_workflow.py` for any issues

## Future Enhancements

Potential improvements to the evaluation system:

- [ ] Add tool selection accuracy metric
- [ ] Add SQL query quality metric
- [ ] Test multi-turn conversations
- [ ] Add cost tracking per evaluation
- [ ] Create automated CI/CD evaluation pipeline
- [ ] Add A/B testing between model versions
- [ ] Expand dataset with synthetic test cases
