#!/usr/bin/env python3
"""Generate basic icons for GitHub Pages."""
from PIL import Image, ImageDraw, ImageFont

def make_favicon(size=(64, 64)):
    img = Image.new('RGBA', size, (10, 14, 23, 255))
    draw = ImageDraw.Draw(img)
    # Draw a simple "ZP" monogram in purple on dark background
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size[0]//2)
    except Exception:
        font = None
    
    if font:
        bbox = draw.textbbox((0, 0), "ZP", font=font)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
        x = (size[0] - tw) // 2
        y = (size[1] - th) // 2
        draw.text((x, y), "ZP", fill=(168, 85, 247), font=font)
    
    img.save('/root/github/zph0713.github.io/favicon.ico', 'PNG')
    print("favicon.png created")

def make_avatar(size=(300, 300)):
    # Gradient avatar with purple/cyan
    img = Image.new('RGBA', size)
    draw = ImageDraw.Draw(img)
    
    for i in range(size[0]):
        r = int(168 * (i / size[0])) + int(10 * ((size[0]-i) / size[0]))
        g = int(55 * (i / size[0])) + int(211 * ((size[0]-i) / size[0]))
        b = int(247 * (i / size[0])) + int(38 * ((size[0]-i) / size[0]))
        draw.line([(i, 0), (i, size[1])], fill=(r, g, b))
    
    img.save('/root/github/zph0713.github.io/img/avatar.png', 'PNG')
    print("avatar.png created")

make_favicon()
make_avatar()
