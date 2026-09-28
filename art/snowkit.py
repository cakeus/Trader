"""Shared snowy palette and props for the Frostpine Peaks backgrounds and map.

Pale blue / lavender sky, white and blue-grey snow, dark teal pines,
warm orange window glow. Everything is drawn without anti-aliasing.
"""
import math

from bgkit import W, H, dith, paste
from pixelkit import Sprite, hexc, mix, edge

SKY = [hexc("#9fb2e0"), hexc("#b4c2ea"), hexc("#cbcff0"), hexc("#e2dcf2"), hexc("#f2e6f0")]
SNOW = [hexc("#f8faff"), hexc("#e8eef8"), hexc("#d4ddf0"), hexc("#bcc6e2")]
SNOW_OUT = hexc("#8e9ac4")
SNOW_SHADOW = hexc("#c4cce6")
PINE = [hexc("#4e9290"), hexc("#347276"), hexc("#265a62"), hexc("#1d4650")]
PINE_OUT = hexc("#16343e")
TRUNK = [hexc("#9a6a4e"), hexc("#74482e")]
WARM = hexc("#ffc46e")
WARM_HI = hexc("#fff0b8")
WARM_DEEP = hexc("#f09848")
MOUNTAIN_FAR = hexc("#b6bee6")
MOUNTAIN_MID = hexc("#9ea8d8")
CAP = hexc("#f4f4fc")
CAP_SHADE = hexc("#d6d8f0")


def pine(h, seed=0, snowy=True, ramp=PINE, outline=PINE_OUT):
    """Tiered fir tree sprite (width ~0.6h), snow resting on each tier."""
    w = int(h * 0.62) | 1
    S = Sprite(w + 2, h + 2)
    cx = w / 2 + 0.5
    trunk_h = max(3, h // 9)
    tiers = 4 if h >= 40 else 3
    top = 1
    body_h = h - trunk_h
    mask = set()
    # tier heights grow toward the bottom; each tier overlaps the one above
    weights = [1 + 0.35 * k for k in range(tiers)]
    ov = 0.5
    hems = []
    fk = {}
    total = weights[0] + sum(wt * (1 - ov) for wt in weights[1:])
    unit = body_h / total
    s0 = top
    prev_b = 0.6
    for k in range(tiers):
        th = weights[k] * unit
        t0 = s0 if k == 0 else s0 - th * ov
        t1 = t0 + th
        a = 0.6 if k == 0 else prev_b * 0.28
        b = (w / 2) * (0.42 + 0.58 * (k + 1) / tiers)
        for y in range(int(t0), int(round(t1))):
            f = (y - t0) / max(1, t1 - t0)
            half = a + (b - a) * max(0.0, f) ** 1.25
            for x in range(w + 2):
                if abs(x + 0.5 - cx) <= half:
                    mask.add((x, y))
                    fk[(x, y)] = (k, f, half)
        s0 = t1
        prev_b = b
        hems.append((int(round(t1)), b))
    tr = {(x, y) for x in range(int(cx) - max(1, w // 12), int(cx) + max(1, w // 12) + 1)
          for y in range(top + body_h - 1, h + 1)}
    S.blob(tr, TRUNK, hexc("#4a2c22"), lx=1, ly=0, cuts=(0.2,))
    S.blob(mask, ramp, outline, lx=0.85, ly=0.35, cuts=(-0.35, 0.15, 0.55), center=(cx, top + body_h * 0.6))
    # a dark band of shadow under each tier's hem
    inner0 = mask - edge(mask)
    for (hy, hb) in hems[:-1]:
        for x in range(w + 2):
            if abs(x + 0.5 - cx) < hb - 0.5:
                for yy in (hy, hy + 1):
                    if (x, yy) in inner0:
                        S.set(x, yy, ramp[3] if x > cx - hb * 0.5 else ramp[2])
    if snowy:
        inner = mask - edge(mask)
        for (x, y) in inner:
            k, f, half = fk.get((x, y), (0, 1, 1))
            dist = half - abs(x + 0.5 - cx)
            lump = (x * 7 + y * 3 + seed) % 5
            if (x, y - 2) not in mask or (k == 0 and f < 0.22)                     or (f > 0.45 and dist < 1.2 + (lump % 3) * 0.6 + f * 1.5):
                S.set(x, y, SNOW[0] if x < cx + 1 else SNOW[2])
        for (x, y) in edge(mask):
            if (x, y + 1) in inner and S.get(x, y + 1) in (SNOW[0], SNOW[2]):
                S.set(x, y, SNOW_OUT)
    return S


def far_pine(img, x, base, h, color):
    """Flat silhouette fir for distant rows (with a pale snowy tip line)."""
    px = img.load()
    for y in range(base - h, base + 1):
        f = (y - (base - h)) / h
        half = 0.5 + f * h * 0.3
        # zig-zag tier notches
        half -= (int(f * h) % max(3, h // 4)) * 0.18
        for xx in range(int(x - half), int(x + half) + 1):
            if 0 <= xx < img.width and 0 <= y < img.height:
                px[xx, y] = color


def mountains(img, base, peaks, color, cap=CAP, cap_shade=CAP_SHADE, cap_depth=0.3):
    """Ridge of triangular peaks: list of (x, top_y, half_width). Snow caps with a lit left face."""
    px = img.load()
    for x in range(img.width):
        best = None
        for (mx, my, hw) in peaks:
            y = my + abs(x - mx) * (base - my) / hw
            y += 3 * math.sin(x * 0.21 + mx) * min(1, abs(x - mx) / 20)
            if best is None or y < best[0]:
                best = (y, mx, my, hw)
        y0, mx, my, hw = best
        for y in range(max(0, int(y0)), base + 1):
            depth = (y - my) / (base - my)
            jag = 0.05 * math.sin(x * 0.7) + 0.04 * math.sin(x * 0.23 + 2)
            if depth < cap_depth + jag:
                c = cap if x < mx + (y - my) * 0.15 else cap_shade
            else:
                c = color if x < mx else mix(color, hexc("#6a6aa0"), 0.12)
            px[x, y] = c


def snowfall(img, R, n, box=(0, 0, W, H), color=hexc("#ffffff")):
    px = img.load()
    x0, y0, x1, y1 = box
    for _ in range(n):
        x, y = R.randint(x0, x1 - 2), R.randint(y0, y1 - 2)
        a = R.choice((0.55, 0.75, 0.9))
        px[x, y] = mix(px[x, y], color, a)
        if R.random() < 0.18:
            px[x + 1, y] = mix(px[x + 1, y], color, a * 0.8)
            px[x, y + 1] = mix(px[x, y + 1], color, a * 0.8)
            px[x + 1, y + 1] = mix(px[x + 1, y + 1], color, a * 0.5)


def glow(img, cx, cy, rx, ry, strength, color):
    px = img.load()
    for yy in range(max(0, int(cy - ry)), min(img.height, int(cy + ry) + 1)):
        for xx in range(max(0, int(cx - rx)), min(img.width, int(cx + rx) + 1)):
            r = math.hypot((xx - cx) / rx, (yy - cy) / ry)
            if r < 1:
                t = strength * (1 - r) ** 1.4
                px[xx, yy] = mix(px[xx, yy], color, min(0.55, t * 1.4)) if dith(xx, yy, min(1, t * 2.2)) \
                    else mix(px[xx, yy], color, t * 0.5)


def snow_ground(img, y0, y1=H, drift=None):
    """Snowy ground: brighter near the top edge (lit), bluer toward the viewer, gentle drift waves."""
    px = img.load()
    for y in range(y0, y1):
        for x in range(img.width):
            top = y0 + (drift(x) if drift else 0)
            if y < top:
                continue
            t = 0.1 + 0.55 * (y - y0) / max(1, y1 - y0) + 0.18 * math.sin(x * 0.013 + y * 0.04) \
                + 0.1 * math.sin(x * 0.047 - y * 0.02)
            t = max(0.0, min(0.999, t)) * (len(SNOW) - 2)
            i = int(t)
            px[x, y] = SNOW[i + 1] if dith(x, y, t - i) else SNOW[i]
            if y - top < 2:
                px[x, y] = SNOW[0]


def smoke(img, R, x, y, n=7, color=hexc("#eef0fa")):
    """Soft puffs drifting up and to the right from a chimney at (x, y)."""
    from pixelkit import ellipse
    for i in range(n):
        r = 4 + i * 1.6
        cx = x + i * 5 + 3 * math.sin(i * 1.3)
        cy = y - 8 - i * 11
        S = Sprite(int(2 * r + 4), int(2 * r + 4))
        m = ellipse(r + 1.5, r + 1.5, r, r * 0.8)
        S.blob(m, [color, mix(color, hexc("#c0c4e4"), 0.4)], None, lx=0.5, ly=0.7, cuts=(0.3,))
        im = S.image()
        # fade out as it rises
        a = int(235 - i * 26)
        im.putalpha(im.getchannel("A").point(lambda v: min(v, a)))
        img.alpha_composite(im, (int(cx - r), int(cy - r)))


def lantern(h=20):
    """Little hanging-style post lantern with a warm window (sprite)."""
    S = Sprite(9, h)
    post = {(4, y) for y in range(9, h)}
    S.fill(post, hexc("#3e3a62"))
    S.fill({(3, h - 1), (5, h - 1)}, hexc("#3e3a62"))
    S.fill({(x, y) for x in range(1, 8) for y in range(1, 9)}, hexc("#3e3a62"))
    S.fill({(x, y) for x in range(2, 7) for y in range(3, 8)}, WARM)
    S.fill({(x, 3) for x in range(2, 7)}, WARM_HI)
    S.set(2, 4, WARM_HI)
    S.fill({(x, 0) for x in range(2, 7)}, SNOW[0])
    S.fill({(1, 1), (7, 1)}, SNOW[1])
    return S
