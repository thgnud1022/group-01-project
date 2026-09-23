"""
Database Connection Verification Script
Prepared for TASK-001 Step 6 Verification.

Safety:
    - Never logs or exposes credentials, passwords, or full connection strings.
    - Reports only masked host and connection status.
    - Sanitizes any error messages to prevent accidental credential leakage.
"""
import asyncio
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


def load_env_file():
    """Attempt to load backend/.env if present without external dependencies."""
    candidates = [
        Path(__file__).resolve().parent.parent / ".env",
        Path.cwd() / "backend" / ".env",
        Path.cwd() / ".env",
    ]
    for env_path in candidates:
        if env_path.is_file():
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip("'\"")
                            if k not in os.environ:
                                os.environ[k] = v
                break
            except Exception:
                pass


def get_masked_host(url: str) -> str:
    """Safely extract and mask the hostname and port from the URL."""
    try:
        parsed = urlparse(url)
        host = parsed.hostname or "unknown"
        port = f":{parsed.port}" if parsed.port else ""
        if len(host) > 10:
            masked = host[:3] + "***" + host[-8:]
        else:
            masked = "***"
        return f"{masked}{port}"
    except Exception:
        return "***"


def sanitize_message(msg: str, raw_url: str) -> str:
    """Mask any passwords or sensitive DSN fragments from error messages."""
    sanitized = re.sub(r"://([^:]+):([^@]+)@", r"://\1:***@", msg)
    try:
        parsed = urlparse(raw_url)
        if parsed.password and parsed.password in sanitized:
            sanitized = sanitized.replace(parsed.password, "***")
    except Exception:
        pass
    return sanitized


async def main():
    load_env_file()
    db_url = os.getenv("DATABASE_URL")

    if not db_url or "YOUR-PASSWORD" in db_url or "YOUR-PROJECT-REF" in db_url:
        print("DATABASE_URL = NOT CONFIGURED")
        print("[INFO] Please configure DATABASE_URL in backend/.env.")
        sys.exit(1)

    masked_host = get_masked_host(db_url)
    print("DATABASE_URL = CONFIGURED")
    print(f"[INFO] Host target: {masked_host}")

    try:
        from prisma import Prisma
        print("[INFO] Prisma Client package loaded successfully.")
    except ImportError:
        print("[ERROR] Prisma Python client is not installed in this environment.")
        sys.exit(2)

    db = Prisma(datasource={"url": db_url})
    print("[INFO] Attempting PostgreSQL connection via Prisma Client...")
    try:
        await db.connect()
        print("[SUCCESS] Prisma database connection established.")
        
        result = await db.query_raw("SELECT 1 as result")
        print(f"[SUCCESS] SELECT 1 query response received: {result}")
        
        await db.disconnect()
        print("[SUCCESS] Disconnected gracefully from database.")
        sys.exit(0)
    except Exception as e:
        clean_err = sanitize_message(f"{type(e).__name__}: {str(e)}", db_url)
        print(f"[ERROR] Database connection failed: {clean_err}")
        if db.is_connected():
            try:
                await db.disconnect()
            except Exception:
                pass
        sys.exit(3)


if __name__ == "__main__":
    asyncio.run(main())
