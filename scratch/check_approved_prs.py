import asyncio
from app.services.db import get_prisma, connect_db, disconnect_db

async def main():
    await connect_db()
    p = get_prisma()
    prs = await p.purchaserequest.find_many(where={'status': 'APPROVED'}, include={'items': True, 'quotations': True})
    print(f"Total APPROVED PRs: {len(prs)}")
    for pr in prs:
        print(f"ID: {pr.id} | Title: {pr.title} | EstVal: {float(pr.estimatedValue)} | Quotes: {len(pr.quotations)} | Items: {len(pr.items)}")
        for it in pr.items:
            print(f"   Item: {it.itemName} | Qty: {it.quantity} | UnitPrice: {float(it.estimatedUnitPrice)}")

    # Check all existing quotations in DB
    all_quotes = await p.quotation.find_many(include={'supplier': True})
    print(f"\nTotal Quotations in DB: {len(all_quotes)}")
    for q in all_quotes:
        print(f"Quote {q.id} | PR: {q.purchaseRequestId} | Supplier: {q.supplier.name} | Total: {float(q.totalAmount)} | Qty: {q.quantity}")

    await disconnect_db()

if __name__ == '__main__':
    asyncio.run(main())
