import asyncio
from app.services.db import get_prisma, connect_db, disconnect_db

async def main():
    await connect_db()
    p = get_prisma()
    users = await p.user.find_many()
    print("CURRENT USERS IN POSTGRESQL:")
    for u in users:
        print(f"ID: {u.id} | Email: {u.email} | Role: {u.role} | authUserId: {u.authUserId}")
    
    # Check if procurement user exists
    proc = await p.user.find_first(where={'email': 'procurement@company.com'})
    if proc:
        print(f"\nUpdating procurement@company.com authUserId to af7e0b69-1070-4a2d-b88f-3ee99962007b...")
        updated = await p.user.update(
            where={'id': proc.id},
            data={'authUserId': 'af7e0b69-1070-4a2d-b88f-3ee99962007b'}
        )
        print(f"Updated: {updated.id} -> {updated.authUserId}")
    else:
        print("Creating procurement user...")
        created = await p.user.create(
            data={
                'id': 'USER-PROC-01',
                'email': 'procurement@company.com',
                'name': 'Procurement Officer',
                'role': 'PROCUREMENT',
                'departmentId': 'DEPT-PROC',
                'authUserId': 'af7e0b69-1070-4a2d-b88f-3ee99962007b'
            }
        )
        print(f"Created: {created.id}")

    await disconnect_db()

if __name__ == '__main__':
    asyncio.run(main())
