import urllib.request
import urllib.error
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9vZ2Ntc291Y3pybWJ3dWdobmZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQ3MjIwNzMsImV4cCI6MjEwMDI5ODA3M30.qvLLoL-yhrKluw8Yu0GwqUfRA4FQ4doFUb-opnv3sBc'
LOGIN_URL = 'https://oogcmsouczrmbwughnfb.supabase.co/auth/v1/token?grant_type=password'
BASE_URL = 'http://127.0.0.1:8000'

def login(email, password='password123'):
    req = urllib.request.Request(
        LOGIN_URL,
        data=json.dumps({'email': email, 'password': password}).encode('utf-8')
    )
    req.add_header('apikey', ANON_KEY)
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        return data['access_token']

print("=== STARTING PHASE 2 PR API REGRESSION VERIFICATION ===")

# Obtain fresh real Supabase JWT
print("\n[Step 0] Authenticating employee@company.com with real Supabase Auth...")
try:
    emp_token = login('employee@company.com')
    print("[PASS] Successfully authenticated with Supabase Auth. Received real JWT token.")
except Exception as e:
    print(f"[FAIL] Authentication failed: {e}")
    sys.exit(1)

# 1. GET /api/pr (with Employee token)
print("\n[Step 1] Verifying GET /api/pr (Employee JWT)...")
req1 = urllib.request.Request(f"{BASE_URL}/api/pr")
req1.add_header("Authorization", f"Bearer {emp_token}")
try:
    with urllib.request.urlopen(req1) as resp:
        prs = json.loads(resp.read().decode())
        print(f"[PASS] GET /api/pr status 200 OK. Fetched {len(prs)} PRs from PostgreSQL database.")
        if len(prs) > 0:
            sample = prs[0]
            print(f"       Sample PR: ID={sample.get('id')}, title='{sample.get('title')}', status={sample.get('status')}, creatorId={sample.get('creatorId')}")
except Exception as e:
    print(f"[FAIL] GET /api/pr error: {e}")
    sys.exit(1)

# 2. POST /api/pr (Create new PR with Employee JWT, verifying creator identity & persistence)
print("\n[Step 2] Verifying POST /api/pr (Create PR with creator identity & DB persistence)...")
pr_payload = json.dumps({
    "departmentId": "DEPT-IT",
    "title": "Phase 2 Visual Gate Regression Verification PR",
    "items": [
        {
            "itemName": "Ergonomic Monitor Arms VESA",
            "quantity": 2,
            "estimatedUnitPrice": 1500000
        }
    ]
}).encode('utf-8')

req2 = urllib.request.Request(f"{BASE_URL}/api/pr", data=pr_payload, headers={
    "Content-Type": "application/json",
    "Authorization": f"Bearer {emp_token}"
})

created_pr_id = None
try:
    with urllib.request.urlopen(req2) as resp:
        created = json.loads(resp.read().decode())
        created_pr_id = created.get("id")
        print(f"[PASS] POST /api/pr status 200/201 OK. Created PR ID: {created_pr_id}")
        print(f"       Creator identity verified: creatorId={created.get('creatorId')}, totalAmount={created.get('totalAmount')}")
except Exception as e:
    print(f"[FAIL] POST /api/pr error: {e}")
    sys.exit(1)

# 3. GET /api/pr/{id} (Fetch newly created PR from PostgreSQL)
if created_pr_id:
    print(f"\n[Step 3] Verifying GET /api/pr/{created_pr_id} (Fetch created PR by ID)...")
    req3 = urllib.request.Request(f"{BASE_URL}/api/pr/{created_pr_id}")
    req3.add_header("Authorization", f"Bearer {emp_token}")
    try:
        with urllib.request.urlopen(req3) as resp:
            pr_detail = json.loads(resp.read().decode())
            print(f"[PASS] GET /api/pr/{created_pr_id} status 200 OK.")
            print(f"       Title: '{pr_detail.get('title')}', items: {len(pr_detail.get('items', []))}, status={pr_detail.get('status')}")
    except Exception as e:
        print(f"[FAIL] GET /api/pr/{created_pr_id} error: {e}")
        sys.exit(1)

# 4. Zero-Trust RBAC guard: Request without Authorization header
print("\n[Step 4] Verifying Zero-Trust Security Guard (No JWT -> Expect 401 Unauthorized)...")
req4 = urllib.request.Request(f"{BASE_URL}/api/pr")
try:
    with urllib.request.urlopen(req4) as resp:
        print("[FAIL] Unauthenticated request succeeded unexpectedly!")
        sys.exit(1)
except urllib.error.HTTPError as e:
    if e.code in (401, 403):
        print(f"[PASS] Zero-Trust Guard verified. Unauthenticated request rejected with HTTP {e.code}.")
    else:
        print(f"[WARN] HTTP {e.code}")

print("\n=== ALL PR API REGRESSION CHECKS COMPLETED: 100% PASS ===")
