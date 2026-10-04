import os
from PIL import Image, ImageDraw, ImageFont

FIGMA_DIR = 'docs/evidence/figma-reference'
BROWSER_DIR = 'docs/evidence/browser'
OUT_DIR = 'docs/evidence/comparison'
os.makedirs(OUT_DIR, exist_ok=True)

pair = {
    'title': 'AI Analysis & Recommendation (Flow D / Figma 9:5291)',
    'figma': 'ai-analysis-figma-9-5291.png',
    'browser': 'ai-analysis-browser.png',
    'out': 'ai-analysis-comparison.png',
}

HEADER_HEIGHT = 50
PADDING = 16

def create_comparison():
    figma_path = os.path.join(FIGMA_DIR, pair['figma'])
    browser_path = os.path.join(BROWSER_DIR, pair['browser'])
    out_path = os.path.join(OUT_DIR, pair['out'])

    if not os.path.exists(figma_path) or not os.path.exists(browser_path):
        print(f"Missing files ({figma_path} or {browser_path})")
        return

    with Image.open(figma_path) as img_f, Image.open(browser_path) as img_b:
        target_height = max(img_f.height, img_b.height, 900)

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

        # Draw main header
        draw.text((PADDING, 14), f"PHASE 4D VISUAL QA COMPARISON: {pair['title']}", fill=(18, 22, 28), font=font_title)

        # Place Figma Image
        x_f = PADDING
        y_content = HEADER_HEIGHT + PADDING
        draw.text((x_f, HEADER_HEIGHT - 6), f"FIGMA REFERENCE ({pair['figma']})", fill=(74, 86, 210), font=font_label)
        comp.paste(img_f_resized, (x_f, y_content))

        # Place Browser Image
        x_b = x_f + img_f_resized.width + PADDING
        draw.text((x_b, HEADER_HEIGHT - 6), f"BROWSER IMPLEMENTATION ({pair['browser']})", fill=(22, 96, 59), font=font_label)
        comp.paste(img_b_resized, (x_b, y_content))

        comp.save(out_path, quality=95)
        print(f"Generated comparison: {out_path} ({os.path.getsize(out_path)} bytes)")

if __name__ == '__main__':
    create_comparison()
