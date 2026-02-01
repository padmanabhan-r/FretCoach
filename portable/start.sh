#!/bin/bash
# FretCoach Portable - Startup Script
# Activates the virtual environment and starts the application

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Activate the virtual environment
source "$PROJECT_ROOT/.venv/bin/activate"

# Change to project root for correct relative imports
cd "$PROJECT_ROOT"

# Run the portable application
python portable/main.py "$@"
