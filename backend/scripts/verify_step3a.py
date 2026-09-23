import asyncio
import sys
from prisma import Prisma
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('backend/.env')

async def main():
    db = Prisma()
    await db.connect()

    # 1. Check column existence and nullable in information_schema
    cols = await db.query_raw('''
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'User' AND table_schema = 'public'
        ORDER BY ordinal_position
    ''')
    print('=== 1. COLUMNS IN TABLE User ===')
    auth_col = None
    for c in cols:
        print(f"  {c['column_name']}: {c['data_type']}, nullable={c['is_nullable']}, default={c['column_default']}")
        if c['column_name'] == 'authUserId':
            auth_col = c

    # 2. Check unique indexes on User
    indexes = await db.query_raw('''
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE tablename = 'User' AND schemaname = 'public'
    ''')
    print('\n=== 2. INDEXES ON TABLE User ===')
    auth_idx = None
    for idx in indexes:
        print(f"  {idx['indexname']}: {idx['indexdef']}")
        if 'authUserId' in idx['indexdef']:
            auth_idx = idx

    # 3. Query all users from User table
    users = await db.user.find_many(order={'email': 'asc'})
    print(f'\n=== 3. USER RECORDS IN DB (Total: {len(users)}) ===')
    for u in users:
        print(f'  ID: {u.id} | Email: {u.email} | authUserId: {u.authUserId} | Role: {u.role} | Name: {u.name} | Dept: {u.departmentId}')

    # 4. Summary assertions
    assert auth_col is not None, 'authUserId column missing!'
    assert auth_col['is_nullable'] == 'YES', f"authUserId is not nullable: {auth_col['is_nullable']}"
    assert auth_col['column_default'] is None, f"authUserId has default: {auth_col['column_default']}"
    assert auth_idx is not None, 'authUserId unique index missing!'
    assert 'UNIQUE' in auth_idx['indexdef'], f"Index is not UNIQUE: {auth_idx['indexdef']}"
    assert len(users) == 5, f'User count mismatch: expected 5, got {len(users)}'
    for u in users:
        assert u.authUserId is None, f'Expected authUserId to be None for {u.email}, got {u.authUserId}'

    print('\nALL DATABASE VERIFICATION CHECKS PASSED 100%!')
    await db.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
