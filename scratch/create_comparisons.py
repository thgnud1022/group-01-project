import os
from PIL import Image, ImageDraw, ImageFont

FIGMA_DIR = 'docs/evidence/figma-reference'
BROWSER_DIR = 'docs/evidence/browser'
OUT_DIR = 'docs/evidence/comparison'
os.makedirs(OUT_DIR, exist_ok=True)

PAIRS = [
    {
        'title': 'Purchase Requests (Node 9:317)',
        'figma': 'purchase-requests-figma-9-317.png',
        'browser': 'purchase-requests-browser.png',
        'out': 'purchase-requests-comparison.png',
    },
    {
        'title': 'New Request - Flow A (Node 9:645)',
        'figma': 'new-request-figma-9-645.png',
        'browser': 'new-request-browser.png',
        'out': 'new-request-comparison.png',
    },
    {
        'title': 'Draft Request Detail (Node 9:1006)',
        'figma': 'draft-request-figma-9-1006.png',
        'browser': 'draft-request-browser.png',
        'out': 'draft-request-comparison.png',
    },
    {
        'title': 'Edit Draft Request (Node 9:1237)',
        'figma': 'edit-draft-figma-9-1237.png',
        'browser': 'edit-draft-browser.png',
        'out': 'edit-draft-comparison.png',
    },
    {
        'title': 'Submission Error Detail (Node 9:1563)',
        'figma': 'submission-error-figma-9-1563.png',
        'browser': 'submission-error-browser.png',
        'out': 'submission-error-comparison.png',
    },
]

HEADER_HEIGHT = 50
PADDING = 16

def create_comparison(pair):
    figma_path = os.path.join(FIGMA_DIR, pair['figma'])
    browser_path = os.path.join(BROWSER_DIR, pair['browser'])
    out_path = os.path.join(OUT_DIR, pair['out'])

    if not os.path.exists(figma_path) or not os.path.exists(browser_path):
        print(f"Skipping {pair['title']}: missing files ({figma_path} or {browser_path})")
        return

    with Image.open(figma_path) as img_f, Image.open(browser_path) as img_b:
        # Standardize target height to max of both or browser height
        target_height = max(img_f.height, img_b.height, 800)
        
        # Scale proportionally to match target_height
        f_scale = target_height / img_f.height
        new_f_w = int(img_f.width * f_scale)
        f_resized = img_f.resize((new_f_w, target_height), Image.Resampling.LANCZOS)

        b_scale = target_height / img_b.height
        new_b_w = int(img_b.width * b_scale)
        b_resized = img_b.resize((new_b_w, target_height), Image.Resampling.LANCZOS)

        total_width = new_f_w + new_b_w + PADDING * 3
        canvas_height = target_height + HEADER_HEIGHT + PADDING * 2

        comp = Image.new('RGB', (total_width, canvas_height), color=(245, 246, 248))
        draw = ImageDraw.Draw(comp)

        # Header background
        draw.rectangle([(0, 0), (total_width, HEADER_HEIGHT)], fill=(18, 22, 28))

        # Title text
        font = ImageFont.load_default()
        draw.text((PADDING, 16), f"PHASE 2 VISUAL GATE: {pair['title']}", fill=(255, 255, 255), font=font)
        
        left_label = f"FIGMA REFERENCE ({pair['figma']})"
        right_label = f"BROWSER IMPLEMENTATION ({pair['browser']})"
        
        f_x = PADDING
        f_y = HEADER_HEIGHT + PADDING
        comp.paste(f_resized, (f_x, f_y))

        b_x = new_f_w + PADDING * 2
        b_y = HEADER_HEIGHT + PADDING
        comp.paste(b_resized, (b_x, b_y))

        # Labels
        draw.rectangle([(f_x, f_y - 20), (f_x + 300, f_y)], fill=(74, 86, 210))
        draw.text((f_x + 8, f_y - 16), left_label, fill=(255, 255, 255), font=font)

        draw.rectangle([(b_x, b_y - 20), (b_x + 300, b_y)], fill=(22, 96, 59))
        draw.text((b_x + 8, b_y - 16), right_label, fill=(255, 255, 255), font=font)

        comp.save(out_path, format='PNG')
        print(f"[OK] Generated comparison: {out_path} ({total_width}x{canvas_height})")

def main():
    print("=== GENERATING SIDE-BY-SIDE VISUAL COMPARISON ARTIFACTS ===")
    for p in PAIRS:
        create_comparison(p)
    print("=== FINISHED GENERATING ALL COMPARISONS ===")

if __name__ == '__main__':
    main()
