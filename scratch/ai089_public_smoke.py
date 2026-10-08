import urllib.request
import urllib.error
import json
import sys

RAILWAY_URL = 'https://group-01-project-production.up.railway.app'
SUPABASE_URL = 'https://oogcmsouczrmbwughnfb.supabase.co'
ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9vZ2Ntc291Y3pybWJ3dWdobmZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQ3MjIwNzMsImV4cCI6MjEwMDI5ODA3M30.qvLLoL-yhrKluw8Yu0GwqUfRA4FQ4doFUb-opnv3sBc'

def get_token(email, password='password123'):
    payload = json.dumps({'email': email, 'password': password}).encode('utf-8')
    req = urllib.request.Request(
        f'{SUPABASE_URL}/auth/v1/token?grant_type=password',
        data=payload,
        headers={'apikey': ANON_KEY, 'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))['access_token']

def api_call(method, path, token=None, body=None):
    headers = {'Origin': 'https://group-01-project.vercel.app'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    data = None
    if body is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(body).encode('utf-8')
    req = urllib.request.Request(f'{RAILWAY_URL}{path}', data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            resp_data = resp.read().decode('utf-8')
            return resp.status, json.loads(resp_data) if resp_data else {}
    except urllib.error.HTTPError as e:
        err_data = e.read().decode('utf-8')
        try:
            parsed = json.loads(err_data)
        except Exception:
            parsed = {'raw': err_data}
        return e.code, parsed

def run_suite():
    print('==================================================')
    print('AI-089 — PUBLIC RELEASE SMOKE SUITE EXECUTION')
    print('Frontend URL: https://group-01-project.vercel.app')
    print('Backend URL:  https://group-01-project-production.up.railway.app')
    print('==================================================')

    # 1. Health check
    code, res = api_call('GET', '/api/health')
    print(f'[1] /api/health -> HTTP {code} | status: {res.get("status")} | db: {res.get("database")}')
    assert code == 200, f'Expected 200, got {code}'
    assert res.get('status') == 'ok', 'Status not ok'

    # 2. Supabase Auth
    emp_tok = get_token('employee@company.com')
    mgr_tok = get_token('manager@company.com')
    proc_tok = get_token('procurement@company.com')
    admin_tok = get_token('admin@company.com')
    print('[2] Supabase Auth -> Successfully authenticated 4 test accounts.')

    # 3. /api/auth/me
    code, me_emp = api_call('GET', '/api/auth/me', emp_tok)
    print(f'[3] /api/auth/me -> HTTP {code} | email: {me_emp.get("email")} | role: {me_emp.get("role")}')
    assert code == 200
    assert me_emp.get('email') == 'employee@company.com'
    assert me_emp.get('role') == 'EMPLOYEE'

    # 4. Unauthenticated access -> 401
    code, _ = api_call('GET', '/api/auth/me')
    print(f'[4] Unauthenticated /api/auth/me -> HTTP {code} (Security Guard: 401)')
    assert code == 401

    # 5. RBAC Denial -> 403
    code, _ = api_call('POST', '/api/pr/PR-2026-001/approve', emp_tok, {'comments': 'bad'})
    print(f'[5] Server-side RBAC Guard (Employee approving PR) -> HTTP {code} (Security Guard: 403)')
    assert code == 403

    # 6. Critical Business Workflow Happy Path
    # 6a. Employee creates PR (within remaining IT available budget 3,750,000 VND)
    code, new_pr = api_call('POST', '/api/pr', emp_tok, {
        'title': 'AI-089 Public Smoke Test PR',
        'departmentId': 'DEPT-IT',
        'items': [{'itemName': 'Bàn phím cơ công thái học', 'quantity': 1, 'estimatedUnitPrice': 1000000}]
    })
    pr_id = new_pr.get('id')
    print(f'[6a] Create PR -> HTTP {code} | PR ID: {pr_id} | status: {new_pr.get("status")}')
    assert code in [200, 201]

    # 6b. Manager approves PR
    code, app_res = api_call('POST', f'/api/pr/{pr_id}/approve', mgr_tok, {'comments': 'Approved by IT Manager for AI-089'})
    print(f'[6b] Manager Approve -> HTTP {code} | status: {app_res.get("status")}')
    assert code == 200
    assert app_res.get('status') == 'APPROVED'

    # 6c. Sourcing: collect quotation
    code, supps = api_call('GET', '/api/suppliers', proc_tok)
    supp_id = supps[0]['id'] if isinstance(supps, list) and len(supps) > 0 else 'SUP-01'
    code, quote_res = api_call('POST', '/api/quotations', proc_tok, {
        'purchaseRequestId': pr_id,
        'supplierId': supp_id,
        'quantity': 1,
        'unitPrice': 950000,
        'totalAmount': 950000,
        'deliveryDays': 3,
        'warrantyTerms': '24 tháng chính hãng',
        'fileUrl': 'quotes/ai089-smoke.pdf'
    })
    quote_id = quote_res.get('id')
    print(f'[6c] Submit Quotation -> HTTP {code} | Quote ID: {quote_id} | Supplier: {supp_id}')
    assert code in [200, 201]

    # 6d. Human Award & Create PO (POST /api/po)
    code, po_res = api_call('POST', '/api/po', proc_tok, {
        'purchaseRequestId': pr_id,
        'quotationId': quote_id,
    })
    po_id = po_res.get('id')
    po_num = po_res.get('poNumber')
    print(f'[6d] Human Award & Create PO -> HTTP {code} | PO ID: {po_id} | PO Number: {po_num}')
    assert code in [200, 201]

    # 6e. Failure Path Guard: Attempt to close PR before receiving -> Must be BLOCKED (400)
    code, fail_close = api_call('POST', f'/api/pr/{pr_id}/close', admin_tok)
    print(f'[6e] Failure Path Guard (Close before Goods Receipt) -> HTTP {code} (Expected 400)')
    assert code == 400

    # 6f. Goods Receiving (POST /api/receiving)
    code, rec_res = api_call('POST', '/api/receiving', proc_tok, {
        'purchaseOrderId': po_id,
        'receivedQty': 1,
        'fileUrl': 'receipts/ai089-delivery-verified.pdf'
    })
    print(f'[6f] Goods Receiving Completed -> HTTP {code} | Received Qty: {rec_res.get("receivedQty")}')
    assert code in [200, 201]

    # 6g. Final PR Close (Admin/Finance)
    code, close_res = api_call('POST', f'/api/pr/{pr_id}/close', admin_tok)
    print(f'[6g] PR Final Close & Settlement -> HTTP {code} | final_status: {close_res.get("status")}')
    assert code == 200
    assert close_res.get('status') == 'CLOSED'

    # 7. Persistence Verification
    code, final_pr = api_call('GET', f'/api/pr/{pr_id}', emp_tok)
    print(f'[7] Data Persistence Check -> HTTP {code} | PR {pr_id} status: {final_pr.get("status")}')
    assert code == 200
    assert final_pr.get('status') == 'CLOSED'

    print('==================================================')
    print('ALL SMOKE TEST CHECKS PASSED ON LIVE PUBLIC STACK!')
    print('==================================================')

if __name__ == '__main__':
    run_suite()
