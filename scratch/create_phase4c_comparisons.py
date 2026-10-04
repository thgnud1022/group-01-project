import os
from PIL import Image, ImageDraw, ImageFont

FIGMA_DIR = 'docs/evidence/figma-reference'
BROWSER_DIR = 'docs/evidence/browser'
OUT_DIR = 'docs/evidence/comparison'
os.makedirs(OUT_DIR, exist_ok=True)

PAIRS = [
    {
        'title': 'Comparison Not Ready (Node 9:4373 State A)',
        'figma': 'comparison-not-ready-figma-9-4373.png',
        'browser': 'comparison-not-ready-browser.png',
        'out': 'comparison-not-ready-comparison.png',
    },
    {
        'title': 'Quotation Comparison Ready (Node 9:4790 State B)',
        'figma': 'comparison-figma-9-4790.png',
        'browser': 'comparison-browser.png',
        'out': 'comparison-comparison.png',
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
        target_height = max(img_f.height, img_b.height, 800)
        
        # Scale to same height while preserving aspect ratio
        def resize_to_h(img, h):
            ratio = h / img.height
            w = int(img.width * ratio)
            return img.resize((w, h), Image.Resampling.LANCZOS)

        img_f_resized = resize_to_h(img_f, target_height)
        img_b_resized = resize_to_h(img_b, target_height)

        total_width = img_f_resized.width + img_b_resized.width + PADDING * 3
        canvas_height = target_height + HEADER_HEIGHT + PADDING * 2

        comp = Image.new('RGB', (total_width, canvas_height), color=(245, 246, 248))
        draw = ImageDraw.Draw(comp)

        try:
            font_title = ImageFont.truetype("arial.ttf", 20)
            font_label = ImageFont.truetype("arialbd.ttf", 14)
        except Exception:
            font_title = ImageFont.load_default()
            font_label = ImageFont.load_default()

        # Draw main title
        draw.text((PADDING, 14), f"PHASE 4C VISUAL GATE: {pair['title']}", fill=(18, 22, 28), font=font_title)

        # Draw Figma label & image
        x_figma = PADDING
        y_figma = HEADER_HEIGHT + PADDING
        draw.text((x_figma, HEADER_HEIGHT - 6), "FIGMA SPECIFICATION (REFERENCE)", fill=(74, 86, 210), font=font_label)
        comp.paste(img_f_resized, (x_figma, y_figma))

        # Draw Browser label & image
        x_browser = x_figma + img_f_resized.width + PADDING
        y_browser = HEADER_HEIGHT + PADDING
        draw.text((x_browser, HEADER_HEIGHT - 6), "ACTUAL BROWSER IMPLEMENTATION (REACT + POSTGRESQL)", fill=(22, 96, 59), font=font_label)
        comp.paste(img_b_resized, (x_browser, y_browser))

        comp.save(out_path, quality=90)
        print(f"Created: {out_path} ({total_width}x{canvas_height})")

for p in PAIRS:
    create_comparison(p)
