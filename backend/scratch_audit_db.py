import asyncio
import dotenv
dotenv.load_dotenv('backend/.env')
from prisma import Prisma

async def main():
    p = Prisma()
    await p.connect()
    try:
        res = await p.query_raw("SELECT enumlabel FROM pg_enum JOIN pg_type ON pg_enum.enumtypid = pg_type.oid WHERE pg_type.typname = 'PRStatus' ORDER BY enumsortorder;")
        print("PG_ENUMS:", [r['enumlabel'] for r in res])
        
        pr_counts = await p.query_raw('SELECT status, count(*)::int as count FROM "PurchaseRequest" GROUP BY status;')
        print("PR_COUNTS:", pr_counts)
        
        approvals = await p.query_raw('SELECT decision, count(*)::int as count FROM "Approval" GROUP BY decision;')
        print("APPROVAL_DECISIONS:", approvals)
    finally:
        await p.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
