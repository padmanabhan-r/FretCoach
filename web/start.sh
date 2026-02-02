#!/bin/bash

# FretCoach Web - Start Script
# Starts both backend and frontend servers

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   FretCoach Web - Starting Services${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Get the project root directory (parent of web/)
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WEB_DIR="$PROJECT_ROOT/web"

# Cleanup function to kill background processes
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        echo -e "${YELLOW}Stopping backend (PID: $BACKEND_PID)...${NC}"
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        echo -e "${YELLOW}Stopping frontend (PID: $FRONTEND_PID)...${NC}"
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    echo -e "${GREEN}Services stopped.${NC}"
    exit 0
}

# Register cleanup function for script termination
trap cleanup SIGINT SIGTERM EXIT

# 1. Activate virtual environment
echo -e "${BLUE}[1/3] Activating virtual environment...${NC}"
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo -e "${RED}Error: Virtual environment not found at $PROJECT_ROOT/.venv${NC}"
    echo -e "${YELLOW}Please create a virtual environment first:${NC}"
    echo -e "  cd $PROJECT_ROOT"
    echo -e "  python3 -m venv .venv"
    echo -e "  source .venv/bin/activate"
    echo -e "  pip install -r web/web-backend/requirements.txt"
    exit 1
fi

source "$PROJECT_ROOT/.venv/bin/activate"
echo -e "${GREEN}✓ Virtual environment activated${NC}\n"

# 2. Start backend
echo -e "${BLUE}[2/3] Starting backend server...${NC}"
cd "$WEB_DIR/web-backend"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file not found in web-backend/${NC}"
    echo -e "${YELLOW}Backend may not work correctly without environment variables.${NC}\n"
fi

# Start backend in background
uvicorn main:app --host 0.0.0.0 --port 8000 --reload > "$WEB_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID) - Logs: $WEB_DIR/backend.log${NC}"
echo -e "${GREEN}  URL: http://localhost:8000${NC}\n"

# Wait a bit for backend to start
sleep 2

# 3. Start frontend
echo -e "${BLUE}[3/3] Starting frontend server...${NC}"
cd "$WEB_DIR/web-frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}node_modules not found. Installing dependencies...${NC}"
    npm install
    echo -e "${GREEN}✓ Dependencies installed${NC}\n"
fi

# Start frontend in background
npm run dev > "$WEB_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID) - Logs: $WEB_DIR/frontend.log${NC}"
echo -e "${GREEN}  URL: http://localhost:5173${NC}\n"

# Wait a bit for frontend to start
sleep 3

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   All services started successfully!${NC}"
echo -e "${GREEN}========================================${NC}\n"
echo -e "${BLUE}Frontend:${NC} http://localhost:5173"
echo -e "${BLUE}Backend:${NC}  http://localhost:8000"
echo -e "${BLUE}API Docs:${NC} http://localhost:8000/docs\n"
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}\n"

# Show logs
echo -e "${BLUE}Tailing logs (Ctrl+C to stop)...${NC}\n"

# Tail both log files
tail -f "$WEB_DIR/backend.log" "$WEB_DIR/frontend.log"
