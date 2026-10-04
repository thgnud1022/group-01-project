import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Ensure backend/.env is loaded
env_path = Path(__file__).resolve().parent.parent / "backend" / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()

import httpx
from app.services.db import get_prisma, connect_db, disconnect_db

SUPABASE_URL = "https://oogcmsouczrmbwughnfb.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9vZ2Ntc291Y3pybWJ3dWdobmZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQ3MjIwNzMsImV4cCI6MjEwMDI5ODA3M30.qvLLoL-yhrKluw8Yu0GwqUfRA4FQ4doFUb-opnv3sBc"

TEST_USERS = [
    "employee@company.com",
    "manager@company.com",
    "procurement@company.com",
    "finance@company.com",
    "admin@company.com",
]

async def get_supabase_sub(email: str, password: str = "password123"):
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Content-Type": "application/json"
            },
            json={"email": email, "password": password}
        )
        if res.status_code == 200:
            data = res.json()
            return data["user"]["id"]
        else:
            print(f"Failed to authenticate {email}: {res.status_code} - {res.text}")
            return None

async def main():
    await connect_db()
    p = get_prisma()

    for email in TEST_USERS:
        sub = await get_supabase_sub(email)
        if sub:
            print(f"User {email} -> Supabase UUID: {sub}")
            user = await p.user.find_first(where={"email": email})
            if user:
                await p.user.update(
                    where={"id": user.id},
                    data={"authUserId": sub}
                )
                print(f"  [OK] Updated User {user.id} ({user.email}) authUserId = {sub}")
            else:
                print(f"  [MISSING] User {email} not found in PostgreSQL")

    await disconnect_db()

if __name__ == "__main__":
    asyncio.run(main())
