#!/bin/bash
# ContextMed — Startup Script
# Usage: bash run_server.sh

set -e

echo "============================================"
echo "  ContextMed — Globally Informed. Locally Accurate."
echo "============================================"
echo ""

# Check .env
if [ ! -f .env ]; then
  echo "[ERROR] .env file not found. Copy .env.example to .env and fill in your keys."
  echo "  cp .env.example .env"
  exit 1
fi

# Install backend deps
echo "[1/4] Installing backend dependencies..."
pip install -q -r requirements.txt 2>&1 | tail -1

# Install frontend deps
echo "[2/4] Installing frontend dependencies..."
cd frontend
npm install --silent 2>&1 | tail -1
cd ..

# Build frontend
echo "[3/4] Building frontend..."
cd frontend
npm run build 2>&1 | tail -3
cd ..

# Start both servers
echo "[4/4] Starting servers..."
echo ""

# Start frontend on port 3000 in background
cd frontend
PORT=3000 npm run start &
FRONTEND_PID=$!
cd ..

# Start backend on port 8000
echo "============================================"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:3000"
echo "  API Docs: http://localhost:8000/docs"
echo "============================================"
echo ""
echo "Loading MedGemma model (this takes 1-2 minutes)..."
echo ""

python3 -c "
from contextmed.agent import ContextMedAgent
from contextmed.server import create_app
import uvicorn

agent = ContextMedAgent()
agent.load_model()
app = create_app(agent)
uvicorn.run(app, host='0.0.0.0', port=8000)
"

# Cleanup
kill $FRONTEND_PID 2>/dev/null
