"""
Database Seeding Script for Demo
"""
from app.services.procurement_service import ProcurementService, db

def seed():
    print("[+] Seeding Demo Data...")
    
    # Create sample PR within budget
    pr1 = ProcurementService.create_pr(
        dept_id="DEPT-IT",
        creator_id="employee@company.com",
        title="Sam 3 Laptop Dell Vostro Workstation",
        items=[{"itemName": "Laptop Dell Vostro Workstation", "quantity": 3, "estimatedUnitPrice": 25_000_000}]
    )
    print(f"[OK] Created PR 1: {pr1['id']} (Estimated: {pr1['estimatedValue']:,.0f} VND)")

    # Approve PR1
    pr1_approved = ProcurementService.approve_pr(
        pr_id=pr1["id"],
        approver_role="MANAGER",
        approver_name="Tran Van B (Manager)",
        comments="Da duyat phuc vu du an moi"
    )
    print(f"[OK] Approved PR 1 Step 1: Status = {pr1_approved['status']}")

    print("[OK] Seeding completed successfully!")

if __name__ == "__main__":
    seed()
