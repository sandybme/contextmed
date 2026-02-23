#!/bin/bash
# ContextMed — Backend Server
# Usage: bash run_server.sh

set -e

echo "============================================"
echo "  ContextMed — Backend Server"
echo "============================================"

if [ ! -f .env ]; then
  echo "[ERROR] .env not found. Copy .env.example to .env and fill in your keys."
  exit 1
fi

echo ""
echo "  http://localhost:8000"
echo "  http://localhost:8000/docs"
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
