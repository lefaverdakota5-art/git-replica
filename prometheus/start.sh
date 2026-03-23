#!/usr/bin/env bash
set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROMETHEUS_DIR="$REPO_ROOT/prometheus"

echo "⚡ PROMETHEUS — Starting up..."
echo ""

# Install Python deps
echo "→ Installing backend dependencies…"
pip install -r "$PROMETHEUS_DIR/backend/requirements.txt" -q

# Install git_replica package
echo "→ Installing git-replica package…"
pip install -e "$REPO_ROOT" -q

# Install frontend deps
echo "→ Installing frontend dependencies…"
cd "$PROMETHEUS_DIR/frontend"
npm install --silent

echo ""
echo "⚡ Starting services…"
echo ""

# Start backend in background
cd "$REPO_ROOT"
PYTHONPATH="$REPO_ROOT" uvicorn prometheus.backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Start frontend
cd "$PROMETHEUS_DIR/frontend"
npm run dev &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚡ PROMETHEUS is running!"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000"
echo "   API docs: http://localhost:8000/docs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Press Ctrl+C to stop."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
