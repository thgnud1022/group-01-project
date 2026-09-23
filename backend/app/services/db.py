import asyncio
import logging
import os
from pathlib import Path
from typing import Any, Dict
import dotenv
from prisma import Prisma

logger = logging.getLogger("app.db")

# Ensure DATABASE_URL is loaded from environment files regardless of CWD
for env_path in [
    Path.cwd() / "backend" / ".env",
    Path.cwd() / ".env",
    Path(__file__).resolve().parent.parent.parent / ".env",
]:
    if env_path.is_file():
        dotenv.load_dotenv(env_path)
        break

# Shared Prisma Client Singleton instance
prisma = Prisma()
_last_connected_loop = None


def get_prisma() -> Prisma:
    """Return the shared Prisma Client singleton instance."""
    return prisma


async def connect_db() -> None:
    """Connect the shared Prisma Client to PostgreSQL if not already connected."""
    global _last_connected_loop
    current_loop = asyncio.get_running_loop()
    if not prisma.is_connected():
        logger.info("Connecting to Supabase PostgreSQL via Prisma Client...")
        await prisma.connect()
        _last_connected_loop = current_loop
        logger.info("Prisma Client connected successfully.")
    else:
        # Check if the active event loop has changed (common with TestClient / AnyIO on Windows)
        if _last_connected_loop != current_loop:
            engine = getattr(prisma, "_internal_engine", None)
            session = getattr(engine, "session", None)
            if session is not None:
                try:
                    session.open()
                    _last_connected_loop = current_loop
                except Exception:
                    pass


async def disconnect_db() -> None:
    """Disconnect the shared Prisma Client from PostgreSQL if connected."""
    if prisma.is_connected():
        logger.info("Disconnecting Prisma Client...")
        await prisma.disconnect()
        logger.info("Prisma Client disconnected.")


async def check_db_health() -> Dict[str, Any]:
    """
    Execute a lightweight raw query against PostgreSQL to verify real connectivity.
    Returns status dictionary reflecting actual database responsiveness.
    """
    try:
        if not prisma.is_connected():
            await connect_db()
        result = await prisma.query_raw("SELECT 1 as health_check")
        return {
            "healthy": True,
            "connected": True,
            "database": "PostgreSQL (Supabase)",
            "query_result": result,
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "healthy": False,
            "connected": prisma.is_connected(),
            "database": "PostgreSQL (Supabase)",
            "error": str(e),
        }
