import os
from PIL import Image, ImageDraw, ImageFont

FIGMA_DIR = 'docs/evidence/figma-reference'
BROWSER_DIR = 'docs/evidence/browser'
OUT_DIR = 'docs/evidence/comparison'
os.makedirs(OUT_DIR, exist_ok=True)

PAIRS = [
    {
        'title': 'Approvals Queue (Node 9:1813 Flow B)',
        'figma': 'approvals-queue-figma-9-1813.png',
        'browser': 'approvals-queue-browser.png',
        'out': 'approvals-queue-comparison.png',
    },
    {
        'title': 'Approval + Budget Warning (Node 9:2010)',
        'figma': 'approval-budget-warning-figma-9-2010.png',
        'browser': 'approval-budget-warning-browser.png',
        'out': 'approval-budget-warning-comparison.png',
    },
    {
        'title': 'Edit Locked in Approval (Node 9:2321)',
        'figma': 'edit-locked-figma-9-2321.png',
        'browser': 'edit-locked-browser.png',
        'out': 'edit-locked-comparison.png',
    },
    {
        'title': 'Budget Review (Node 9:2431 Finance)',
        'figma': 'budget-review-figma-9-2431.png',
        'browser': 'budget-review-browser.png',
        'out': 'budget-review-comparison.png',
    },
    {
        'title': 'Finance Budget Decision (Node 9:2635)',
        'figma': 'finance-budget-decision-figma-9-2635.png',
        'browser': 'finance-budget-decision-browser.png',
        'out': 'finance-budget-decision-comparison.png',
    },
    {
        'title': 'Revision Required (Node 9:2928)',
        'figma': 'revision-required-figma-9-2928.png',
        'browser': 'revision-required-browser.png',
        'out': 'revision-required-comparison.png',
    },
    {
        'title': 'Edit After Revision (Node 9:3179)',
        'figma': 'edit-after-revision-figma-9-3179.png',
        'browser': 'edit-after-revision-browser.png',
        'out': 'edit-after-revision-comparison.png',
    },
    {
        'title': 'Rejected Request (Node 9:3468)',
        'figma': 'rejected-request-figma-9-3468.png',
        'browser': 'rejected-request-browser.png',
        'out': 'rejected-request-comparison.png',
    },
    {
        'title': 'Approved Request (Node 9:3745)',
        'figma': 'approved-request-figma-9-3745.png',
        'browser': 'approved-request-browser.png',
        'out': 'approved-request-comparison.png',
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
        # Standardize target height to max of both or 800
        target_height = max(img_f.height, img_b.height, 800)
        
        # Scale proportionally to match target_height
        f_scale = target_height / img_f.height
        new_f_w = int(img_f.width * f_scale)
        scaled_f = img_f.resize((new_f_w, target_height), Image.Resampling.LANCZOS)

        b_scale = target_height / img_b.height
        new_b_w = int(img_b.width * b_scale)
        scaled_b = img_b.resize((new_b_w, target_height), Image.Resampling.LANCZOS)

        total_width = new_f_w + new_b_w + (PADDING * 3)
        total_height = target_height + HEADER_HEIGHT + (PADDING * 2)

        canvas = Image.new('RGB', (total_width, total_height), color=(245, 246, 248))
        draw = ImageDraw.Draw(canvas)

        # Header background banner
        draw.rectangle([0, 0, total_width, HEADER_HEIGHT], fill=(18, 22, 28))

        # Title text
        font = None
        try:
            font = ImageFont.truetype('arial.ttf', 20)
            small_font = ImageFont.truetype('arial.ttf', 14)
        except:
            font = ImageFont.load_default()
            small_font = font

        draw.text((PADDING, 14), f"PHASE 3 VISUAL COMPARISON: {pair['title']}", fill=(255, 255, 255), font=font)

        # Labels
        f_label_x = PADDING
        f_label_y = HEADER_HEIGHT + 4
        b_label_x = PADDING * 2 + new_f_w
        b_label_y = HEADER_HEIGHT + 4

        draw.text((f_label_x, f_label_y), "[FIGMA REFERENCE DESIGN]", fill=(47, 55, 137), font=small_font)
        draw.text((b_label_x, b_label_y), "[LIVE BROWSER IMPLEMENTATION]", fill=(22, 96, 59), font=small_font)

        # Paste images
        y_offset = HEADER_HEIGHT + 24
        canvas.paste(scaled_f, (PADDING, y_offset))
        canvas.paste(scaled_b, (PADDING * 2 + new_f_w, y_offset))

        # Border around images
        draw.rectangle([PADDING - 1, y_offset - 1, PADDING + new_f_w, y_offset + target_height], outline=(228, 231, 236), width=1)
        draw.rectangle([PADDING * 2 + new_f_w - 1, y_offset - 1, PADDING * 2 + new_f_w + new_b_w, y_offset + target_height], outline=(228, 231, 236), width=1)

        canvas.save(out_path, quality=92)
        print(f"Generated comparison: {out_path} ({total_width}x{total_height}, {os.path.getsize(out_path)} bytes)")

if __name__ == '__main__':
    for p in PAIRS:
        create_comparison(p)
