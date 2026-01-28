# Quick Start Guide - FretCoach Evaluations

## TL;DR

```bash
cd /Users/paddy/Documents/Github/FretCoach
./evaluations/web-backend/run_evaluation.sh
```

That's it! The script will:
- ✅ Load environment variables from `.env`
- ✅ Activate virtual environment
- ✅ Run the evaluation
- ✅ Log results to Opik dashboard

## Requirements

1. **Virtual Environment** at project root (`.venv/`)
2. **Environment Variables** in `.env` at project root:
   - `OPIK_API_KEY`
   - `OPIK_WORKSPACE`
   - `OPIK_PROJECT_NAME`
3. **Dataset** created in Opik: "FretCoach Hub AI Coach Chat"

## View Results

After running:
1. Open https://www.comet.com/opik/api
2. Go to **Experiments**
3. Find **"FretCoach Hub Agent Evaluation v1"**
4. Review scores and insights

## What Gets Evaluated

- **Answer Relevance** - Is the response relevant to the query?
- **Hallucination Detection** - Any unsupported claims?
- **Practice Plan Quality** - Valid JSON structure?
- **Response Completeness** - Helpful and actionable?

## Need Help?

- Full docs: `evaluations/web-backend/README.md`
- Setup details: `evaluations/web-backend/EVALUATION_SUMMARY.md`
- Main overview: `evaluations/README.md`
