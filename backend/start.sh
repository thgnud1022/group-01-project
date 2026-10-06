#!/bin/sh
set -e

# Resolve port from Railway environment or fallback to 8080
PORT="${PORT:-8080}"
echo "[STARTUP] Starting Uvicorn server on host 0.0.0.0 and port $PORT..."

# Ensure Prisma client is ready
if [ -d "prisma" ]; then
    echo "[STARTUP] Ensuring Prisma client is generated..."
    prisma generate || true
fi

# Start FastAPI application
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
