import asyncio
from app.services.db import get_prisma, connect_db

async def main():
    await connect_db()
    p = get_prisma()
    sups = await p.supplier.find_many(include={'quotations': True})
    print(f"Total suppliers in DB: {len(sups)}")
    for s in sups:
        print(f"ID: {s.id} | Name: {s.name} | Tax: {s.taxCode} | Quotes: {len(s.quotations)}")

if __name__ == '__main__':
    asyncio.run(main())
