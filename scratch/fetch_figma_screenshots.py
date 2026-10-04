import urllib.request
import json
import base64
import os

MCP_URL = 'http://127.0.0.1:3845/mcp'
OUT_DIR = r'docs/evidence/figma-reference'
os.makedirs(OUT_DIR, exist_ok=True)

HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json, text/event-stream'
}

# 1. Initialize
init_data = json.dumps({
    'jsonrpc': '2.0',
    'id': 1,
    'method': 'initialize',
    'params': {
        'protocolVersion': '2024-11-05',
        'capabilities': {},
        'clientInfo': {'name': 'figma-fetcher', 'version': '1.0'}
    }
}).encode('utf-8')

req = urllib.request.Request(MCP_URL, data=init_data, headers=HEADERS)
with urllib.request.urlopen(req) as resp:
    session_id = resp.headers.get('mcp-session-id')
    print(f"Connected to Figma MCP. Session ID: {session_id}")

call_headers = {
    **HEADERS,
    'mcp-session-id': session_id
}

# 2. Initialized notification
notif_data = json.dumps({
    'jsonrpc': '2.0',
    'method': 'notifications/initialized'
}).encode('utf-8')
urllib.request.urlopen(urllib.request.Request(MCP_URL, data=notif_data, headers=call_headers))

# Target frames to fetch
FRAMES = [
    ('9:317', 'purchase-requests-figma-9-317.png'),
    ('9:645', 'new-request-figma-9-645.png'),
    ('9:1006', 'draft-request-figma-9-1006.png'),
    ('9:1237', 'edit-draft-figma-9-1237.png'),
    ('9:1563', 'submission-error-figma-9-1563.png')
]

for req_id, (node_id, filename) in enumerate(FRAMES, start=2):
    print(f"\nFetching screenshot for node {node_id} -> {filename}...")
    call_data = json.dumps({
        'jsonrpc': '2.0',
        'id': req_id,
        'method': 'tools/call',
        'params': {
            'name': 'get_screenshot',
            'arguments': {'nodeId': node_id}
        }
    }).encode('utf-8')

    try:
        call_req = urllib.request.Request(MCP_URL, data=call_data, headers=call_headers)
        with urllib.request.urlopen(call_req) as resp:
            raw = resp.read().decode('utf-8')
            # Parse SSE or json
            lines = raw.strip().split('\n')
            for line in lines:
                if line.startswith('data: '):
                    payload = json.loads(line[6:])
                    result = payload.get('result', {})
                    for content in result.get('content', []):
                        if content.get('type') == 'image':
                            img_b64 = content.get('data')
                            img_bytes = base64.b64decode(img_b64)
                            dest = os.path.join(OUT_DIR, filename)
                            with open(dest, 'wb') as f:
                                f.write(img_bytes)
                            print(f"[OK] Saved {dest} ({len(img_bytes)} bytes)")
    except Exception as e:
        print(f"Error fetching {node_id}: {e}")

print("\n=== COMPLETED FETCHING FIGMA REFERENCE SCREENSHOTS ===")
