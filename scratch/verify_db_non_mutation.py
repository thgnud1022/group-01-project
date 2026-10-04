import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / "backend" / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()

import sys
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.services.db import get_prisma, connect_db, disconnect_db

async def check():
    await connect_db()
    prisma = get_prisma()
    pr = await prisma.purchaserequest.find_unique(where={"id": "PR-2026-001"})
    pos = await prisma.purchaseorder.find_many(where={"purchaseRequestId": "PR-2026-001"})
    await disconnect_db()
    assert pr is not None, "PR-2026-001 not found!"
    assert pr.status == "APPROVED", f"PR status was mutated! Found {pr.status}"
    assert len(pos) == 0, f"Autonomous PO was created! Count: {len(pos)}"
    print("Database Governance Verified: PR status is APPROVED, PO count is 0. Zero side effects.")

if __name__ == "__main__":
    asyncio.run(check())
