import sqlite3
import base64

db_path = r'C:\Users\TechCare\.gemini\antigravity-ide\conversations\dd837a42-f879-4b34-a9ba-ab722eeed91e.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

for s_idx in [11775, 11776]:
    cur.execute('SELECT step_payload FROM steps WHERE idx=?', (s_idx,))
    row = cur.fetchone()
    if not row or not row[0]:
        continue
    payload = row[0]
    idx = payload.find(b'iVBORw0KGgo')
    if idx != -1:
        # find end of base64 string
        end = idx
        valid_chars = set(b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=')
        while end < len(payload) and payload[end] in valid_chars:
            end += 1
        b64_data = payload[idx:end]
        print(f"Step {s_idx}: found b64 data length {len(b64_data)}")
        img = base64.b64decode(b64_data)
        out_path = 'docs/evidence/figma-reference/comparison-figma-9-4790.png'
        with open(out_path, 'wb') as f:
            f.write(img)
        print(f"Saved {len(img)} bytes to {out_path}!")
        break

conn.close()
