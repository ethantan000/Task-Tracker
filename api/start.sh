#!/bin/bash
# Start FastAPI server

echo "🚀 Starting Task-Tracker API on http://localhost:8000"
echo "📡 WebSocket endpoint: ws://localhost:8000/ws/activity"
echo "📚 API docs: http://localhost:8000/docs"
echo ""

cd "$(dirname "$0")"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
