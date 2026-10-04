import sqlite3
import json
import base64
import re

db_path = r'C:\Users\TechCare\.gemini\antigravity-ide\conversations\dd837a42-f879-4b34-a9ba-ab722eeed91e.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cur.fetchall()]
print("Tables:", tables)

for table in tables:
    cur.execute(f"PRAGMA table_info({table})")
    cols = [c[1] for c in cur.fetchall()]
    print(f"Table {table}: {cols}")

    # Search for get_screenshot or get_design_context or base64 image data
    cur.execute(f"SELECT * FROM {table}")
    rows = cur.fetchall()
    print(f"  Rows count: {len(rows)}")
    for row in rows:
        row_str = str(row)
        if "get_screenshot" in row_str or "get_design_context" in row_str:
            print(f"  Found tool call in {table}!")
            # Find base64 image
            matches = re.findall(r'"data":\s*"([A-Za-z0-9+/=]{1000,})"', row_str)
            if matches:
                print(f"    Found {len(matches)} base64 images!")
                for idx, m in enumerate(matches):
                    img_data = base64.b64decode(m)
                    out_path = f"docs/evidence/figma-reference/comparison-figma-9-4790.png"
                    with open(out_path, "wb") as f:
                        f.write(img_data)
                    print(f"    Successfully extracted to {out_path} ({len(img_data)} bytes)!")

conn.close()
