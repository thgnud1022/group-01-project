import asyncio
from app.services.db import get_prisma

async def main():
    prisma = get_prisma()
    await prisma.connect()
    users = await prisma.user.find_many()
    print("Found users:")
    for u in users:
        print(f"ID: {u.id}, Email: {u.email}, Role: {u.role}, authUserId: {u.authUserId}")
    await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
