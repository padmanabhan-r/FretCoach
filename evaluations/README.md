# FretCoach Evaluations

This directory contains evaluation frameworks for different components of the FretCoach system.

## Structure

```
evaluations/
├── README.md              # This file
└── web-backend/          # Web backend agent evaluations
    ├── README.md         # Detailed documentation
    ├── EVALUATION_SUMMARY.md  # Quick start guide
    ├── run_evaluation.sh # One-command execution
    ├── evaluate_agent.py # Main evaluation script
    ├── inspect_dataset.py # Dataset inspection
    ├── test_metrics.py   # Metric testing
    └── metrics/          # Custom evaluation metrics
        ├── practice_plan_quality.py
        └── response_completeness.py
```

## Components

### Web Backend
Evaluates the FretCoach Hub LangGraph AI Coach agent.

**Dataset:** "FretCoach Hub AI Coach Chat" (10 production traces)

**Metrics:**
- Answer Relevance (built-in)
- Hallucination Detection (built-in)
- Practice Plan Quality (custom)
- Response Completeness (custom)

**Quick Start:**
```bash
cd /Users/paddy/Documents/Github/FretCoach
./evaluations/web-backend/run_evaluation.sh
```

**Documentation:** See [web-backend/README.md](./web-backend/README.md)

## Setup

### Prerequisites

1. **Virtual Environment** - Install at project root:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Environment Variables** - Add to `.env` at project root:
   ```bash
   OPIK_API_KEY=your_api_key
   OPIK_WORKSPACE=your_workspace
   OPIK_PROJECT_NAME=FretCoach
   ```

3. **Dataset** - Create or upload datasets in Opik dashboard

### Running Evaluations

Each component has its own `run_evaluation.sh` script that:
- Loads environment variables from project root `.env`
- Activates the virtual environment
- Runs the evaluation
- Logs results to Opik dashboard

## Evaluation Workflow

1. **Create dataset** - From production traces or synthetic data
2. **Run evaluation** - Execute the evaluation script
3. **Review results** - Check Opik dashboard for scores
4. **Identify issues** - Find low-scoring test cases
5. **Improve agent** - Update prompts, tools, or logic
6. **Re-evaluate** - Measure improvement
7. **Compare** - Track progress across experiment versions

## Adding New Components

To add evaluations for a new component:

1. Create a new directory (e.g., `evaluations/mobile-app/`)
2. Copy the structure from `web-backend/`
3. Update imports and paths in scripts
4. Create component-specific metrics
5. Update this README

## Best Practices

- **Version experiments** - Use descriptive names: "v1", "v2", "prompt-update-v3"
- **Keep datasets stable** - Don't modify datasets between experiment runs
- **Document changes** - Note what changed between versions
- **Track regressions** - Ensure improvements don't hurt other metrics
- **Run regularly** - Evaluate after significant changes

## Integration with CI/CD

Future enhancement: Add evaluation runs to CI/CD pipeline to catch regressions before deployment.

## Resources

- [Opik Documentation](https://www.comet.com/docs/opik/)
- [Opik Dashboard](https://www.comet.com/opik/api)
- Project Opik Docs: `/.backup/opik-detailed-docs/`
- Opik Cookbooks: `/.backup/opik-cookbook/`
