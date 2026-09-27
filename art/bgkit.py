"""Helpers for 640x480 pixel-art backgrounds (no anti-aliasing).

Backgrounds are drawn on a plain RGBA Image with ImageDraw (which never
anti-aliases) plus ordered (Bayer) dithering for soft gradients. Small
props are built as pixelkit Sprites and pasted in.
"""
import json
import math
import os

from PIL import Image, ImageDraw

from pixelkit import ASSETS, PREVIEWS, hexc, mix

W, H = 640, 480

BAYER4 = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def new_bg(color="#000000"):
    img = Image.new("RGBA", (W, H), hexc(color) if isinstance(color, str) else color)
    return img, ImageDraw.Draw(img)


def dith(x, y, t):
    """True if a pixel at (x, y) should take the 'next' color for blend t in [0,1]."""
    return t * 16 > BAYER4[y & 3][x & 3] + 0.5


def vgrad(img, x0, y0, x1, y1, stops):
    """Vertical dithered gradient through a list of RGBA stops."""
    px = img.load()
    n = len(stops) - 1
    for y in range(max(0, y0), min(img.height, y1)):
        t = (y - y0) / max(1, (y1 - y0 - 1)) * n
        i = min(int(t), n - 1)
        f = t - i
        a, b = stops[i], stops[i + 1]
        for x in range(max(0, x0), min(img.width, x1)):
            px[x, y] = b if dith(x, y, f) else a


def ramp_fill(img, mask_fn, value_fn, colors, box=(0, 0, W, H)):
    """Fill pixels where mask_fn(x,y) with a dithered ramp picked by value_fn(x,y) in [0,1]."""
    px = img.load()
    n = len(colors) - 1
    x0, y0, x1, y1 = box
    for y in range(max(0, y0), min(img.height, y1)):
        for x in range(max(0, x0), min(img.width, x1)):
            if not mask_fn(x, y):
                continue
            t = max(0.0, min(0.9999, value_fn(x, y))) * n
            i = min(int(t), n - 1)
            px[x, y] = colors[i + 1] if dith(x, y, t - i) else colors[i]


def haze(img, color, amount, box=None):
    """Blend a flat color over the image (or a box) to push it back / soften contrast."""
    box = box or (0, 0, img.width, img.height)
    region = img.crop(box)
    over = Image.new("RGBA", region.size, color)
    img.paste(Image.blend(region, over, amount), box[:2])


def orect(d, x0, y0, x1, y1, fill, outline):
    d.rectangle([x0, y0, x1, y1], fill=fill, outline=outline)


def oellipse(d, x0, y0, x1, y1, fill, outline):
    d.ellipse([x0, y0, x1, y1], fill=fill, outline=outline)


def paste(img, sprite, x, y):
    """Paste a pixelkit Sprite (or RGBA image) with its top-left at (x, y)."""
    im = sprite.image() if hasattr(sprite, "image") else sprite
    img.alpha_composite(im, (int(x), int(y)))


def seg_dist(px_, py_, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    t = max(0, min(1, ((px_ - ax) * dx + (py_ - ay) * dy) / (dx * dx + dy * dy or 1)))
    return math.hypot(px_ - (ax + t * dx), py_ - (ay + t * dy))


def save_bg(img, name):
    from pixelkit import save_image
    img = img.convert("RGBA")
    save_image(img, name, "bg", scale=2)
    return img


def mock(img, name, loc_id=None):
    """Composite UI stand-ins (HUD, cards, banner, bag, button) for a readability check."""
    m = img.copy()
    d = ImageDraw.Draw(m)
    d.rectangle([0, 0, W, 29], fill=hexc("#3b2f55"))
    d.rectangle([8, 424, 8 + 300, 472], fill=hexc("#3b2f55"))
    if loc_id:
        locs = json.load(open(os.path.join(ASSETS, "..", "data", "locations.json")))
        loc = next(l for l in locs if l["id"] == loc_id)
        for s in loc["slots"]:
            d.rectangle([s["x"], s["y"], s["x"] + 107, s["y"] + 103], fill=hexc("#fbf1dc"), outline=hexc("#5a3a3e"))
            d.rectangle([s["x"] + 22, s["y"] + 8, s["x"] + 85, s["y"] + 71], fill=hexc("#8ecf8a"))
        d.rectangle([8, 38, 200, 70], fill=hexc("#3b2f55"))
        d.rectangle([W - 136, H - 50, W - 8, H - 12], fill=hexc("#f5b66a"), outline=hexc("#6e3a2c"))
    else:
        d.rectangle([W - 330, H - 44, W - 8, H - 8], fill=hexc("#3b2f55"))
    m.save(os.path.join(PREVIEWS, f"_mock_{name}.png"))
