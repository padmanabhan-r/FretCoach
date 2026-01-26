# FretCoach Opik Integration

## Overview

Opik provides observability and evaluation for FretCoach's AI features:
- AI Practice Recommendations
- Live Coaching Feedback
- AI Chat Coach

We needed to know if our AI actually helps users learn guitar better, so we integrated Opik to track, measure, and improve AI quality systematically.

## Implementation

### 1. Enhanced Tracing

**What we added:**
- Token counting and cost tracking for all LLM calls
- User context in traces (skill level, session history, performance metrics)
- Tool execution monitoring (database queries with timing and results)

**Why:**
- See which features are expensive ($0.0002 per recommendation)
- Filter traces by skill level to debug personalization
- Track SQL query performance and catch slow operations

**Example trace metadata:**
```json
{
  "user": "intermediate (12 sessions, avg 68% performance)",
  "weakest_area": "timing",
  "cost": "$0.00018 USD",
  "tokens": "150 input, 45 output",
  "duration": "1.2s"
}
```

### 2. Evaluation Framework

**What we built:**
- Production datasets: 85 coaching scenarios, 15 recommendation→outcome pairs
- Custom metrics:
  - `CoachingHelpfulness` (LLM-as-Judge) - evaluates feedback quality
  - `RecommendationAccuracy` (heuristic) - measures improvement after following advice
  - `LearningProgressRate` (heuristic) - tracks user progress over time
  - `SafetyModeration` (API) - content safety checks
- Experiment pipeline to compare different prompts with quantified scores

**Why:**
- Move from "this looks good" to "scored 0.85 on helpfulness across 85 examples"
- Measure if recommendations actually help users improve
- Test prompt changes systematically instead of manually

**Example evaluation:**
```
Student: Intermediate, Pitch 62%, Scale 51%, Timing 48%
Feedback: "Good pitch at 62%! But timing at 48% needs work - try metronome at 60 BPM."

LLM-as-Judge Score: 0.85/1.00
✓ Identified weakness correctly
✓ Actionable advice (specific BPM)
✗ Could be more encouraging
✓ Appropriate for skill level
```

### 3. Agent Graph Visualization

LangGraph workflow visualization enabled in `web/web-backend/langgraph_workflow.py` - shows how the AI decides which tools to use and helps debug conversation flow.

## Results

**Visibility:**
- 100% AI call coverage with rich metadata
- 85+ production examples captured

**Measurability:**
- Coaching helpfulness: 0.78-0.81 average
- Cost tracking: $0.0001-0.0002 per interaction
- Can run 85-example experiments in ~3 minutes

**Use Cases:**

*Debugging:* Filter traces by user_id to see why someone got unexpected recommendations - often reveals correct classification (e.g., 15 sessions but still beginner-level performance).

*Testing improvements:* Compare prompt variants on 85 examples, get quantified scores showing 5% improvement, then deploy with confidence.

*Cost optimization:* Identified 4,877 tokens per response, implemented two-tier prompting, achieved 92% reduction.

## Technical Details

**Files:**
- `backend/core/llm_utils.py` - Cost tracking utilities
- `backend/api/services/ai_agent_service.py` - Enhanced tracing
- `backend/api/services/live_coach_service.py` - Enhanced tracing
- `evaluation/custom_metrics.py` - Custom domain metrics
- `evaluation/create_datasets.py` - Dataset generation
- `evaluation/run_experiments.py` - Experiment runner

**Code patterns:**
```python
# Cost tracking
llm_metadata = track_llm_call(prompt, response, "gpt-4o-mini")
opik_context.update_current_trace(metadata=llm_metadata)

# User context in traces
OpikTracer(tags=["ai-mode", f"skill-{skill_level}"], metadata=user_context)

# Custom metrics
metric = CoachingHelpfulness(model="gpt-4o-mini")
result = metric.score(input={...}, output="feedback text")

# Experiments
evaluate(dataset, task_fn, scoring_metrics=[...], experiment_name="Test V2")
```

## Summary

| Before | After |
|--------|-------|
| "Is our AI helpful?" | "Scores 0.78-0.81 on helpfulness" |
| "Which prompt is better?" | "V2 is 5% better (0.82 vs 0.78)" |
| "What does this cost?" | "$0.0002 per recommendation" |
| "Why did this fail?" | "SQL query took 2.3s, here's the trace" |

Opik transformed FretCoach from guessing about AI quality to measuring and improving it with data.
