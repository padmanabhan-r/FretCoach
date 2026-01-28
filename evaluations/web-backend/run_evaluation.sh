#!/bin/bash
# Quick start script to run FretCoach Hub agent evaluation

echo "========================================"
echo "FretCoach Hub Agent Evaluation"
echo "========================================"
echo ""

# Navigate to project root
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

echo "📁 Project root: $PROJECT_ROOT"
echo ""

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    echo "🔧 Loading environment variables from .env"
    # Export variables from .env
    set -a
    source .env
    set +a
    echo "✅ Environment variables loaded"
else
    echo "⚠️  No .env file found at project root"
fi
echo ""

# Check environment variables
if [ -z "$OPIK_API_KEY" ]; then
    echo "❌ Error: OPIK_API_KEY not set"
    echo "   Add it to .env file at project root: $PROJECT_ROOT/.env"
    exit 1
fi

if [ -z "$OPIK_WORKSPACE" ]; then
    echo "❌ Error: OPIK_WORKSPACE not set"
    echo "   Add it to .env file at project root: $PROJECT_ROOT/.env"
    exit 1
fi

echo "✅ Opik environment variables set"
echo "   OPIK_WORKSPACE: $OPIK_WORKSPACE"
echo "   OPIK_PROJECT_NAME: ${OPIK_PROJECT_NAME:-FretCoach}"
echo ""

# Activate virtual environment
VENV_PATH="$PROJECT_ROOT/.venv"
if [ ! -d "$VENV_PATH" ]; then
    echo "❌ Error: Virtual environment not found at $VENV_PATH"
    exit 1
fi

echo "🔧 Activating virtual environment..."
source "$VENV_PATH/bin/activate"
echo "✅ Virtual environment activated"
echo ""

# Navigate to evaluation directory
EVAL_DIR="$PROJECT_ROOT/evaluations/web-backend"
cd "$EVAL_DIR" || exit 1

# Run evaluation
echo "🚀 Running evaluation from: $EVAL_DIR"
echo ""
python evaluate_agent.py

echo ""
echo "========================================"
echo "Evaluation script completed"
echo "========================================"
