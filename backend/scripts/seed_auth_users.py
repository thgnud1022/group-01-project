"""
Seed script: Binds Supabase Auth UUIDs to Application Users in PostgreSQL.
This script is run at every container startup (start.sh) to ensure
all test accounts are correctly mapped — even after a redeploy.

The UUID_MAP was established by inspecting Supabase Auth user records.
This script is idempotent: it only UPDATEs if authUserId is missing.
"""

import asyncio
import os
import sys

# UUID mapping: email -> Supabase Auth UUID (sub claim)
# These were collected from Supabase Auth dashboard and live JWT tokens.
UUID_MAP = {
    "employee@company.com":    "d4539429-c3ba-4e3f-9baf-413311d5b317",
    "manager@company.com":     "f196d40f-c87f-4bd5-b63c-4f9aeeb87b83",
    "procurement@company.com": "af7e0b69-1070-4a2d-b88f-3ee99962007b",
    "finance@company.com":     "3b638d43-b12d-4adc-abea-c6b1e1f74f2a",
    "admin@company.com":       "293c1230-7728-4bb2-917a-39c5dbc43233",
}


async def seed():
    from prisma import Prisma

    db = Prisma()
    await db.connect()

    try:
        print("[SEED] Starting authUserId binding for all application users...")
        users = await db.user.find_many()
        bound = 0
        skipped = 0

        for user in users:
            target_uuid = UUID_MAP.get(user.email)
            if not target_uuid:
                print(f"[SEED]   SKIP {user.email}: Not in UUID_MAP")
                skipped += 1
                continue

            if user.authUserId == target_uuid:
                print(f"[SEED]   OK   {user.email}: Already bound to {target_uuid}")
                skipped += 1
                continue

            await db.user.update(
                where={"id": user.id},
                data={"authUserId": target_uuid}
            )
            print(f"[SEED]   BIND {user.email} -> {target_uuid}")
            bound += 1

        print(f"[SEED] Complete: {bound} bound, {skipped} skipped.")
    except Exception as e:
        print(f"[SEED] ERROR during seeding: {e}", file=sys.stderr)
        # Non-fatal: server still starts even if seeding fails
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(seed())
