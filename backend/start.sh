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

# Seed authUserId bindings so every deploy has correct UUID -> User mapping.
# This is idempotent and non-fatal — server starts regardless.
echo "[STARTUP] Seeding authUserId bindings for application users..."
python scripts/seed_auth_users.py || echo "[STARTUP] Seed encountered an error (non-fatal), continuing..."

# Start FastAPI application
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
