"""
Database Base Seeding Script for Prisma (PostgreSQL / Supabase)
Course: Thuc hanh lap trinh ung dung trong doanh nghiep bang AI
Group: Group 01 - Branch: final-delivery
Task: TASK-003 STEP 2B - Base Seed Only (Department, Supplier, User, Budget)

Human Decisions Enforced:
- HD-REQ-05: Demo password "password123" bcrypt-hashed into User.passwordHash.
             NO plaintext password is stored in the database.
- HD-REQ-06: Initial Budget Period: fiscalYear = 2026, quarter = 1
             (Human-approved technical convention for initial seed data).

Idempotency:
- All operations use `upsert` matching unique constraints / business keys.
- Re-running this script produces no duplicates.
"""

import asyncio
import logging
import sys
from decimal import Decimal
from pathlib import Path
from typing import Dict, Any

import bcrypt
import dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("seed")

# Ensure DATABASE_URL is loaded from environment files regardless of CWD
for env_path in [
    Path.cwd() / "backend" / ".env",
    Path.cwd() / ".env",
    Path(__file__).resolve().parent.parent / ".env",
    Path(__file__).resolve().parent.parent.parent / ".env",
]:
    if env_path.is_file():
        dotenv.load_dotenv(env_path)
        break

from prisma import Prisma

# Raw base data specifications (verified by source code and human decisions)
DEPARTMENTS = [
    {
        "id": "DEPT-IT",
        "name": "Phòng Công nghệ Thông tin",
    },
    {
        "id": "DEPT-HR",
        "name": "Phòng Nhân sự",
    },
]

SUPPLIERS = [
    {
        "id": "SUP-01",
        "name": "Công ty TNHH Tin học Phong Vũ",
        "taxCode": "0301234567",
    },
    {
        "id": "SUP-02",
        "name": "Công ty TNHH Máy tính Trần Anh",
        "taxCode": "0107654321",
    },
    {
        "id": "SUP-03",
        "name": "Công ty Cổ phần Máy tính FPT",
        "taxCode": "0101234999",
    },
]

DEMO_PASSWORD_RAW = "password123"

USERS = [
    {
        "email": "employee@company.com",
        "name": "Nguyễn Văn A",
        "role": "EMPLOYEE",
        "departmentId": "DEPT-IT",
    },
    {
        "email": "manager@company.com",
        "name": "Trần Văn B",
        "role": "MANAGER",
        "departmentId": "DEPT-IT",
    },
    {
        "email": "procurement@company.com",
        "name": "Lê Thị C",
        "role": "PROCUREMENT",
        "departmentId": "DEPT-IT",
    },
    {
        "email": "finance@company.com",
        "name": "Phạm Văn D",
        "role": "FINANCE",
        "departmentId": "DEPT-IT",
    },
    {
        "email": "admin@company.com",
        "name": "Quản Trị Viên",
        "role": "ADMIN",
        "departmentId": "DEPT-IT",
    },
]

BUDGETS = [
    {
        "departmentId": "DEPT-IT",
        "fiscalYear": 2026,
        "quarter": 1,
        "allocatedAmount": Decimal("500000000.00"),
        "spentAmount": Decimal("150000000.00"),
        "tempReservedAmount": Decimal("0.00"),
    },
    {
        "departmentId": "DEPT-HR",
        "fiscalYear": 2026,
        "quarter": 1,
        "allocatedAmount": Decimal("200000000.00"),
        "spentAmount": Decimal("50000000.00"),
        "tempReservedAmount": Decimal("0.00"),
    },
]


def hash_password(plaintext: str) -> str:
    """Generate bcrypt hash for user password. Salt rounds default to 12."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(plaintext.encode("utf-8"), salt)
    return hashed.decode("utf-8")


async def seed_departments(prisma: Prisma) -> int:
    logger.info("Seeding Departments (2 records)...")
    count = 0
    for dept in DEPARTMENTS:
        await prisma.department.upsert(
            where={"id": dept["id"]},
            data={
                "create": {
                    "id": dept["id"],
                    "name": dept["name"],
                },
                "update": {
                    "name": dept["name"],
                },
            },
        )
        count += 1
    logger.info(f"Seeded {count} Departments successfully.")
    return count


async def seed_suppliers(prisma: Prisma) -> int:
    logger.info("Seeding Suppliers (3 records)...")
    count = 0
    for sup in SUPPLIERS:
        await prisma.supplier.upsert(
            where={"id": sup["id"]},
            data={
                "create": {
                    "id": sup["id"],
                    "name": sup["name"],
                    "taxCode": sup["taxCode"],
                },
                "update": {
                    "name": sup["name"],
                    "taxCode": sup["taxCode"],
                },
            },
        )
        count += 1
    logger.info(f"Seeded {count} Suppliers successfully.")
    return count


async def seed_users(prisma: Prisma) -> int:
    logger.info("Seeding Users (5 demo accounts, bcrypt hash, NO plaintext)...")
    count = 0
    password_hash = hash_password(DEMO_PASSWORD_RAW)

    for user in USERS:
        await prisma.user.upsert(
            where={"email": user["email"]},
            data={
                "create": {
                    "email": user["email"],
                    "name": user["name"],
                    "role": user["role"],
                    "departmentId": user["departmentId"],
                    "passwordHash": password_hash,
                },
                "update": {
                    "name": user["name"],
                    "role": user["role"],
                    "departmentId": user["departmentId"],
                    "passwordHash": password_hash,
                },
            },
        )
        count += 1
    logger.info(f"Seeded {count} Users successfully.")
    return count


async def seed_budgets(prisma: Prisma) -> int:
    logger.info("Seeding Budgets (2 records, FY2026 Q1)...")
    count = 0
    for b in BUDGETS:
        where_key = {
            "departmentId_fiscalYear_quarter": {
                "departmentId": b["departmentId"],
                "fiscalYear": b["fiscalYear"],
                "quarter": b["quarter"],
            }
        }
        await prisma.budget.upsert(
            where=where_key,
            data={
                "create": {
                    "departmentId": b["departmentId"],
                    "fiscalYear": b["fiscalYear"],
                    "quarter": b["quarter"],
                    "allocatedAmount": b["allocatedAmount"],
                    "spentAmount": b["spentAmount"],
                    "tempReservedAmount": b["tempReservedAmount"],
                },
                "update": {
                    "allocatedAmount": b["allocatedAmount"],
                    "spentAmount": b["spentAmount"],
                    "tempReservedAmount": b["tempReservedAmount"],
                },
            },
        )
        count += 1
    logger.info(f"Seeded {count} Budgets successfully.")
    return count


async def run_seed() -> Dict[str, int]:
    prisma = Prisma()
    await prisma.connect()
    try:
        dept_count = await seed_departments(prisma)
        sup_count = await seed_suppliers(prisma)
        user_count = await seed_users(prisma)
        budget_count = await seed_budgets(prisma)

        return {
            "departments": dept_count,
            "suppliers": sup_count,
            "users": user_count,
            "budgets": budget_count,
        }
    finally:
        await prisma.disconnect()


def main():
    logger.info("Starting TASK-003 STEP 2B Base Database Seeding...")
    results = asyncio.run(run_seed())
    logger.info(f"Database seeding completed successfully: {results}")


if __name__ == "__main__":
    main()
