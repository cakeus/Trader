"""640x480 Stargazer's Lookout: a rooftop garden high above the city at night,
for moon viewing (tsukimi).

A big sky with a full moon and many dim baked stars, the city's lights glowing
far below along the horizon, seen through the rooftop railing. A little dome
observatory and a telescope stand between the cards; planters with shrubs and
pampas grass (susuki) line the parapet, a bench waits on the wooden deck, and
strings of cream paper lanterns swag overhead.

Also writes the baked star positions to assets/bg/stargazers_lookout_stars.json
(only stars in open sky, never on the moon, props, cards or HUD) so the game can
twinkle them.
"""
import json
import math
import os
import random

from bgkit import W, H, new_bg, vgrad, dith, haze, paste, save_bg, mock
from pixelkit import ASSETS, Sprite, hexc, mix, ellipse, rect

NAME = "stargazers_lookout"
R = random.Random(314)
img, d = new_bg()
px = img.load()

# ------------------------------------------------------------- palette -----
SKY = [hexc("#141129"), hexc("#1b1733"), hexc("#221d40"), hexc("#2a2450"), hexc("#342a58"), hexc("#46335f"),
       hexc("#5a3c68")]
BLD = [hexc("#2a2744"), hexc("#34304f"), hexc("#403a5e"), hexc("#4d4670")]
BLD_OUT = hexc("#17142b")
LIT = [hexc("#ffd98a"), hexc("#f7b861"), hexc("#b8834a")]
GLOW = hexc("#ff9a4a")
CREAM = hexc("#ffe3a8")
LEAF = [hexc("#5b8a62"), hexc("#3f6b55"), hexc("#2b4f47"), hexc("#1f3a3a")]
LEAF_OUT = hexc("#142628")
MOON = [hexc("#fff4d6"), hexc("#f1dca6"), hexc("#cdb57e")]
WOOD = [hexc("#8a6a6a"), hexc("#6e5260"), hexc("#553f54"), hexc("#3e2e44")]
WOOD_OUT = hexc("#221a30")
STONE = [hexc("#5a5378"), hexc("#4d4670"), hexc("#403a5e"), hexc("#34304f")]
METAL = [hexc("#8a86b0"), hexc("#5e5a84"), hexc("#403a5e")]
GRASS = [hexc("#f4e6c0"), hexc("#d8c79a"), hexc("#a8976e"), hexc("#6e6450")]

HORIZON = 250      # where the far city meets the sky
PARAPET = 272      # top of the low rooftop wall
DECK = 300         # rooftop deck starts
MOON_C, MOON_R = (548, 92), 30


def glow(cx, cy, rx, ry, strength, color):
    """Soft dithered light halo blended over what's there."""
    for yy in range(max(0, int(cy - ry)), min(H, int(cy + ry) + 1)):
        for xx in range(max(0, int(cx - rx)), min(W, int(cx + rx) + 1)):
            r = math.hypot((xx - cx) / rx, (yy - cy) / ry)
            if r < 1:
                t = strength * (1 - r) ** 1.5
                px[xx, yy] = mix(px[xx, yy], color, min(0.5, t * 1.3)) if dith(xx, yy, min(1, t * 2)) \
                    else mix(px[xx, yy], color, t * 0.5)


# ------------------------------------------------------------------- sky ---
vgrad(img, 0, 0, W, HORIZON + 4, SKY)
# a couple of thin, dim cloud wisps drifting low across the sky
for (cy, x0, x1, amp, c) in ((176, 330, 640, 3, hexc("#3a2d5c")), (184, 380, 610, 2, hexc("#43335f")),
                             (208, 0, 250, 3, hexc("#4a3662")), (214, 40, 200, 2, hexc("#523b66"))):
    for x in range(x0, x1):
        e = min(x - x0, x1 - x) / 40
        th = amp * min(1, e) + math.sin(x * 0.05) * 0.8
        yc = cy + math.sin(x * 0.018 + cy) * 3
        for y in range(int(yc - th), int(yc + th) + 1):
            if dith(x, y, min(1, e) * 0.8):
                px[x, y] = c
sky_only = img.copy()          # for finding open sky when placing stars

# moon: big halo, then the disk with soft maria and upper-left light
glow(*MOON_C, 96, 96, 0.30, hexc("#7a6aa0"))
glow(*MOON_C, 52, 52, 0.40, hexc("#c8b8d8"))
mx, my = MOON_C
for y in range(my - MOON_R, my + MOON_R + 1):
    for x in range(mx - MOON_R, mx + MOON_R + 1):
        r = math.hypot(x - mx, y - my)
        if r > MOON_R - 0.5:
            continue
        v = ((x - mx) * 0.6 + (y - my) * 0.5) / MOON_R * 0.55 + (r / MOON_R) ** 3 * 0.6
        c = MOON[0]
        if v > 0.3:
            c = MOON[1] if dith(x, y, min(1, (v - 0.3) * 5)) else MOON[0]
        if v > 0.62:
            c = MOON[2] if dith(x, y, min(1, (v - 0.62) * 4)) else MOON[1]
        if r > MOON_R - 1.5:
            c = MOON[2]
        px[x, y] = c
# soft maria (just shapes, faint)
for (cx, cy, rx, ry, t) in ((-8, -6, 9, 7, 0.7), (6, 4, 8, 6, 0.6), (-4, 12, 6, 4, 0.5), (12, -10, 4, 3, 0.5),
                            (-14, 6, 4, 5, 0.45)):
    for (x, y) in ellipse(mx + cx, my + cy, rx, ry):
        if math.hypot(x - mx, y - my) < MOON_R - 2:
            px[x, y] = mix(px[x, y], MOON[2], t * 0.5)
for (x, y) in ((mx - 18, my - 16), (mx - 17, my - 16), (mx - 18, my - 15), (mx - 14, my - 20)):
    px[x, y] = hexc("#fffbea")

# ------------------------------------------------------- the far city ------
# a faint far ridge, then rows of distant buildings with lit windows
for x in range(W):
    top = HORIZON - 6 + int(4 * math.sin(x * 0.011 + 1) + 2 * math.sin(x * 0.037))
    for y in range(top, HORIZON + 30):
        px[x, y] = hexc("#2c2446") if dith(x, y, 0.5) else hexc("#30284c")
glow(320, HORIZON + 14, 420, 40, 0.45, GLOW)


def skyline(base, hmin, hmax, colors, win_p, seed, wmin=8, wmax=22):
    rr = random.Random(seed)
    x = -rr.randint(0, 10)
    while x < W:
        w = rr.randint(wmin, wmax)
        h = rr.randint(hmin, hmax)
        if rr.random() < 0.08:
            h += rr.randint(10, 22)  # an occasional tower
        top = base - h
        d.rectangle([x, top, x + w - 1, base + 40], fill=colors[0])
        d.line([x + w - 1, top, x + w - 1, base + 40], fill=colors[1])
        if h > hmax + 6:
            px[x + w // 2, top - 1] = hexc("#e0503f")  # red aviation light
            px[x + w // 2, top - 2] = hexc("#7a3040")
        for wy in range(top + 2, base + 40, 3):
            for wx in range(x + 1, x + w - 2, 2):
                if rr.random() < win_p:
                    px[wx, wy] = rr.choice(LIT) if rr.random() < 0.7 else LIT[2]
        x += w + rr.randint(0, 3)


skyline(HORIZON + 4, 6, 18, [hexc("#2f2850"), hexc("#282242")], 0.10, 1, 6, 14)
haze(img, hexc("#4a3462"), 0.35, (0, HORIZON - 30, W, HORIZON + 40))
skyline(HORIZON + 14, 8, 22, [hexc("#27213f"), hexc("#211c38")], 0.16, 2)
glow(320, HORIZON + 24, 400, 26, 0.35, GLOW)
# streetlight strings far below
for (y0, amp) in ((HORIZON + 22, 3), (HORIZON + 28, 2)):
    for x in range(0, W, 3):
        y = int(y0 + amp * math.sin(x * 0.02 + y0))
        if R.random() < 0.8:
            px[x, y] = LIT[0] if R.random() < 0.4 else LIT[1]

# ---------------------------------------------------- rooftop railing ------
RAIL_TOP = 238
for x in range(0, W, 18):  # posts
    d.rectangle([x, RAIL_TOP, x + 2, PARAPET], fill=METAL[1], outline=None)
    d.line([x, RAIL_TOP, x, PARAPET], fill=METAL[0])
    d.line([x + 2, RAIL_TOP, x + 2, PARAPET], fill=METAL[2])
for x in range(0, W, 6):  # thin balusters
    if x % 18:
        d.line([x, RAIL_TOP + 4, x, PARAPET], fill=hexc("#3a345a"))
d.rectangle([0, RAIL_TOP - 1, W, RAIL_TOP + 2], fill=METAL[1], outline=None)
d.line([0, RAIL_TOP - 1, W, RAIL_TOP - 1], fill=METAL[0])
d.line([0, RAIL_TOP + 2, W, RAIL_TOP + 2], fill=hexc("#2a2744"))
d.line([0, RAIL_TOP + 16, W, RAIL_TOP + 16], fill=METAL[2])

# parapet wall
d.rectangle([0, PARAPET, W, DECK], fill=STONE[2])
d.line([0, PARAPET, W, PARAPET], fill=STONE[0])
d.line([0, PARAPET + 1, W, PARAPET + 1], fill=STONE[1])
d.line([0, DECK - 1, W, DECK - 1], fill=STONE[3])
d.line([0, DECK, W, DECK], fill=BLD_OUT)
for x in range(0, W, 32):
    d.line([x, PARAPET + 2, x, DECK - 2], fill=STONE[3])
    for y in range(PARAPET + 3, DECK - 2):
        if dith(x + 1, y, 0.3):
            px[x + 1, y] = STONE[1]

# ------------------------------------------------------------ the deck -----
PLANK = [hexc("#4a3a56"), hexc("#43344f"), hexc("#3c2f48")]
for y in range(DECK + 1, H):
    t = (y - DECK) / (H - DECK)
    band = int(((y - DECK) ** 0.85) / 5)
    base = PLANK[band % 3]
    for x in range(W):
        c = base
        if (y - DECK) > 2 and int(((y - DECK) ** 0.85)) % 5 == 0:
            c = hexc("#2a2238")  # seam between boards
        else:
            joint = (x + band * 53) % 150
            if joint == 0:
                c = hexc("#2a2238")
            elif (x * 7 + y * 13) % 41 == 0:
                c = mix(base, hexc("#2a2238"), 0.4)
        if dith(x, y, t * 0.5):
            c = mix(c, hexc("#221a30"), 0.35)
        px[x, y] = c

# ---------------------------------------------------------- plant props ----


def shrub(w, h, seed):
    """Round clipped shrub made of overlapping leafy lumps."""
    rr = random.Random(seed)
    S = Sprite(w + 2, h + 2)
    mask = set()
    for _ in range(max(3, w // 7)):
        cx = rr.uniform(w * 0.25, w * 0.75)
        cy = rr.uniform(h * 0.4, h * 0.7)
        rx = rr.uniform(w * 0.22, w * 0.34)
        mask |= ellipse(cx, cy, rx, rx * rr.uniform(0.75, 0.95))
    mask |= ellipse(w / 2, h * 0.62, w * 0.46, h * 0.38)
    mask = {(x, y) for (x, y) in mask if 0 <= x <= w and 0 <= y <= h}
    S.blob(mask, LEAF, LEAF_OUT, cuts=(-0.35, 0.15, 0.6))
    for _ in range(w * h // 30):  # leaf flecks
        x, y = rr.randint(1, w - 1), rr.randint(1, h - 1)
        if (x, y) in mask and (x, y - 1) in mask and S.get(x, y) != LEAF_OUT:
            S.set(x, y, LEAF[0] if y < h * 0.5 and x < w * 0.6 else LEAF[1])
            if S.get(x, y + 1) not in (None, LEAF_OUT):
                S.set(x, y + 1, LEAF[2])
    return S


def susuki(h, seed, lean=1):
    """Pampas grass (susuki): long thin blades and soft feathery plumes."""
    rr = random.Random(seed)
    w = h
    S = Sprite(w, h + 2)
    bx = w // 2
    for i in range(9):  # blades
        ang = rr.uniform(-1.0, 1.0)
        ln = rr.uniform(0.35, 0.6) * h
        for k in range(int(ln)):
            t = k / ln
            x = bx + ang * t * t * ln * 0.8
            y = h - k
            S.set(int(x), int(y), LEAF[1] if t < 0.6 else LEAF[2])
    for i in range(5):  # stems with plumes
        ang = rr.uniform(-0.35, 0.35) + 0.12 * lean
        ln = rr.uniform(0.7, 0.98) * h
        pts = []
        for k in range(int(ln)):
            t = k / ln
            x = bx + ang * t * t * ln * 0.7 + i - 2
            y = h - k
            pts.append((int(x), int(y)))
        for (x, y) in pts[: int(len(pts) * 0.62)]:
            S.set(x, y, GRASS[3])
        # feathery plume: a soft drooping tuft along the stem's top
        for j, (x, y) in enumerate(pts[int(len(pts) * 0.62):]):
            s = 1 if j % 2 else 0
            S.set(x, y, GRASS[1])
            S.set(x + 1 + s * lean, y + 1, GRASS[2])
            if j % 3 == 0:
                S.set(x - 1, y + 1, GRASS[2])
                S.set(x + 2 * lean, y + 2, GRASS[3])
            if j > 2 and j % 4 == 1:
                S.set(x - 1, y, GRASS[0])
        tx, ty = pts[-1]
        S.set(tx, ty, GRASS[0])
        S.set(tx + lean, ty + 1, GRASS[1])
    return S


def planter(w, h):
    """Wooden planter box with a lit top edge."""
    S = Sprite(w, h)
    S.blob(rect(0, 0, w, h), WOOD, WOOD_OUT, cuts=(-0.5, 0.2, 0.7))
    for y in range(3, h - 1, 5):
        S.fill({(x, y) for x in range(1, w - 1)}, WOOD[2])
    S.fill({(x, 1) for x in range(1, w - 1)}, WOOD[0])
    for x in (3, w - 4):
        S.fill({(x, y) for y in range(1, h - 1)}, WOOD[3])
    return S


def lantern_sprite():
    """Round cream paper lantern: ribs, dark caps and a short tassel. 11x17."""
    S = Sprite(11, 17)
    body = ellipse(5, 7.5, 5, 5.6)
    S.blob(body, [hexc("#fff4d0"), hexc("#ffe8b0"), hexc("#f4cf86"), hexc("#d9a860")], hexc("#8a5a3a"),
           cuts=(-0.3, 0.25, 0.7))
    for y in (5, 8, 11):
        for x in range(1, 10):
            if (x, y) in body and S.get(x, y) != hexc("#8a5a3a"):
                S.set(x, y, hexc("#e8bf78"))
    S.set(3, 4, hexc("#ffffff"))
    S.set(3, 5, hexc("#fff8e4"))
    S.fill({(x, 1) for x in range(3, 8)} | {(x, 2) for x in range(3, 8)}, hexc("#3e2a30"))
    S.fill({(x, 13) for x in range(3, 8)} | {(x, 14) for x in range(4, 7)}, hexc("#3e2a30"))
    S.fill({(5, 0), (5, 15), (5, 16)}, hexc("#e0503f"))
    S.set(4, 16, hexc("#a8332f"))
    return S


# a long planter bed along the parapet: shrubs, susuki and little flowers
BED_TOP = DECK - 14


def flowers(x0, x1, y, seed, cols):
    rr = random.Random(seed)
    for _ in range((x1 - x0) // 6):
        fx, fy = max(1, min(W - 2, rr.randint(x0, x1))), y - rr.randint(0, 10)
        c = rr.choice(cols)
        for k in range(1, rr.randint(3, 7)):
            px[fx, fy + k] = LEAF[2]
        px[fx, fy] = c[0]
        px[fx + 1, fy] = c[1]
        px[fx, fy - 1] = c[1]
        px[fx - 1, fy] = c[1]
        px[fx, fy + 1] = c[1] if px[fx, fy + 1] == LEAF[2] else px[fx, fy + 1]


FLOWER = [(hexc("#c9b8f4"), hexc("#8c78c8")), (hexc("#f4e6f0"), hexc("#c0a8c8")),
          (hexc("#f27a5c"), hexc("#a8332f"))]
beds = [(-8, 176), (266, 648)]
for bi, (x0, x1) in enumerate(beds):
    rr = random.Random(40 + bi)
    x = x0
    items = []
    while x < x1 - 20:
        w = rr.randint(26, 44)
        items.append((x, w))
        x += w - rr.randint(6, 12)
    for i, (x, w) in enumerate(items):
        if rr.random() < 0.5:
            gh = rr.randint(44, 64)
            paste(img, susuki(gh, x * 3 + i, lean=rr.choice((-1, 1))), x + w // 2 - gh // 2, BED_TOP + 6 - gh)
    for i, (x, w) in enumerate(items):
        h = int(w * rr.uniform(0.6, 0.8))
        paste(img, shrub(w, h, x * 7 + i), x, BED_TOP - h + 8)
    flowers(x0 + 6, x1 - 6, BED_TOP, 7 + bi, FLOWER)
    bed = Sprite(x1 - x0, 16)
    bed.blob(rect(0, 0, x1 - x0, 16), WOOD, WOOD_OUT, cuts=(-0.9, 0.2, 0.8))
    bed.fill({(x, 1) for x in range(1, x1 - x0 - 1)}, WOOD[0])
    bed.fill({(x, 8) for x in range(1, x1 - x0 - 1)}, WOOD[2])
    for x in range(40, x1 - x0, 48):
        bed.fill({(x, y) for y in range(2, 15)}, WOOD[3])
    paste(img, bed, x0, BED_TOP + 4)

# ------------------------------------------------- the dome observatory ----
OX0, OX1 = 180, 262
OBS_TOP = 214
OCX = (OX0 + OX1) / 2
# drum walls
d.rectangle([OX0, OBS_TOP, OX1, DECK + 6], fill=hexc("#9c94c0"), outline=hexc("#3a345a"))
for x in range(OX0 + 1, OX1):
    t = (x - OX0) / (OX1 - OX0)
    c = hexc("#b8b0d4") if t < 0.18 else hexc("#9c94c0") if t < 0.62 else hexc("#7e76a6") if t < 0.88 \
        else hexc("#665e8e")
    for y in range(OBS_TOP + 1, DECK + 6):
        px[x, y] = c
d.line([OX0 + 1, OBS_TOP + 22, OX1 - 1, OBS_TOP + 22], fill=hexc("#665e8e"))
# door with a warm crack of light
d.rectangle([OCX - 11, OBS_TOP + 40, OCX + 11, DECK + 5], fill=hexc("#6e5260"), outline=hexc("#3a345a"))
d.line([OCX, OBS_TOP + 41, OCX, DECK + 4], fill=hexc("#3e2e44"))
d.line([OCX - 10, OBS_TOP + 41, OCX - 10, DECK + 4], fill=hexc("#8a6a6a"))
px[OCX + 5, OBS_TOP + 62] = LIT[0]
px[OCX - 5, OBS_TOP + 62] = LIT[0]
# round porthole window glowing warm
glow(OX0 + 16, OBS_TOP + 32, 16, 16, 0.4, GLOW)
for (x, y) in ellipse(OX0 + 16, OBS_TOP + 32, 5, 5):
    r = math.hypot(x - OX0 - 16, y - OBS_TOP - 32)
    px[x, y] = hexc("#3a345a") if r > 4 else (LIT[0] if y < OBS_TOP + 31 else LIT[1])
# the dome
DOME_R = 42
for (x, y) in ellipse(OCX, OBS_TOP, DOME_R, 34):
    if y > OBS_TOP:
        continue
    nx, ny = (x - OCX) / DOME_R, (y - OBS_TOP) / 34
    v = nx * 0.8 + ny * 0.4
    c = hexc("#c8c2e0") if v < -0.55 else hexc("#aaa2cc") if v < -0.05 else hexc("#8a82b4") if v < 0.45 \
        else hexc("#6c6496")
    px[x, y] = c
ELL = ellipse(OCX, OBS_TOP, DOME_R, 34)
for (x, y) in ELL:  # outline
    if y <= OBS_TOP and not all((x + dx, y + dy) in ELL for (dx, dy) in ((1, 0), (-1, 0), (0, -1))):
        px[x, y] = hexc("#3a345a")
for ang in (-0.55, 0.55):
    for k in range(34):
        y = OBS_TOP - k
        half = DOME_R * math.sqrt(max(0, 1 - (k / 34) ** 2))
        x = int(OCX + math.sin(ang) * half)
        if k < 32:
            px[x, y] = hexc("#76709e")
d.line([OX0 - 2, OBS_TOP, OX1 + 2, OBS_TOP], fill=hexc("#5e5a84"))
d.line([OX0 - 2, OBS_TOP + 1, OX1 + 2, OBS_TOP + 1], fill=hexc("#3a345a"))
# the open slit with the telescope poking out toward the moon
for k in range(4, 34):
    y = OBS_TOP - k
    for x in range(int(OCX + 6), int(OCX + 14)):
        if (x, y) in ELL:
            px[x, y] = hexc("#231e3c")
for k in range(24):
    x, y = int(OCX + 8 + k * 0.7), int(OBS_TOP - 8 - k)
    d.rectangle([x, y, x + 3, y + 1], fill=METAL[1])
    px[x, y] = METAL[0]
d.rectangle([int(OCX + 24), OBS_TOP - 36, int(OCX + 28), OBS_TOP - 31], fill=METAL[0], outline=hexc("#3a345a"))

# ------------------------------------------------ the brass telescope ------
TX, TY = 400, 318        # tripod head
TR = [hexc("#f2d08a"), hexc("#d8a95a"), hexc("#a8773c"), hexc("#6e4a2a")]
for (fx, fy) in ((380, TY + 40), (420, TY + 40), (404, TY + 44)):
    d.line([TX, TY, fx, fy], fill=hexc("#5e4a3a"), width=2)
    d.line([TX - 1, TY, fx - 1, fy], fill=hexc("#8a6a4a"))
tube = Sprite(56, 40)
m = set()
for k in range(50):
    cx_, cy_ = 4 + k * 0.92, 34 - k * 0.6
    rr_ = 2.2 + k * 0.05
    m |= ellipse(cx_, cy_, rr_, rr_)
tube.blob(m, TR, hexc("#4a2e1e"), lx=0.5, ly=0.8, cuts=(-0.4, 0.2, 0.7))
for k in (14, 30):  # brass rings
    cx_, cy_ = 4 + k * 0.92, 34 - k * 0.6
    for j in range(-4, 5):
        tube.set(int(cx_ + j * 0.55), int(cy_ + j * 0.85), TR[3])
paste(img, tube, TX - 26, TY - 28)
d.rectangle([TX - 2, TY - 4, TX + 2, TY + 1], fill=TR[2], outline=hexc("#4a2e1e"))

# ------------------------------------------- lantern strings overhead -----
POLE = [hexc("#5a4658"), hexc("#3e2e44")]
poles = [(8, 104), (322, 108), (632, 104)]
for (x, top) in poles:
    d.rectangle([x - 2, top, x + 2, RAIL_TOP + 20], fill=POLE[0], outline=WOOD_OUT)
    d.line([x - 1, top + 1, x - 1, RAIL_TOP + 19], fill=hexc("#7a6070"))
    d.rectangle([x - 3, top - 2, x + 3, top + 1], fill=POLE[1], outline=WOOD_OUT)
lanterns = []
for (a, b, sag) in ((poles[0], poles[1], 34), (poles[1], poles[2], 30)):
    (x0, y0), (x1, y1) = a, b
    prev = None
    for x in range(x0 + 2, x1 - 1):
        t = (x - x0) / (x1 - x0)
        y = int(y0 + (y1 - y0) * t + sag * 4 * t * (1 - t))
        if prev is not None and abs(y - prev) > 1:
            for yy in range(min(y, prev) + 1, max(y, prev)):
                px[x, yy] = hexc("#5a4a6e")
        px[x, y] = hexc("#5a4a6e")
        prev = y
    n = 8
    for i in range(1, n):
        t = i / n
        x = int(x0 + (x1 - x0) * t)
        y = int(y0 + (y1 - y0) * t + sag * 4 * t * (1 - t))
        lanterns.append((x, y))
LANT = lantern_sprite()
for (x, y) in lanterns:
    glow(x, y + 10, 20, 18, 0.45, CREAM)
for (x, y) in lanterns:
    px[x, y + 1] = hexc("#5a4a6e")
    paste(img, LANT, x - 5, y + 2)

# ------------------------------------------------- foreground garden ------
# bench on the deck, facing the moon
BX0, BY = 214, 356
bench = Sprite(112, 40)
seat = rect(0, 12, 112, 6)
bench.blob(seat, WOOD, WOOD_OUT, cuts=(-0.6, 0.3, 0.8))
bench.fill({(x, 13) for x in range(1, 111)}, WOOD[0])
back = rect(4, 0, 104, 5) | rect(4, 6, 104, 3)
bench.blob(back, WOOD, WOOD_OUT, cuts=(-0.6, 0.3, 0.8))
bench.fill({(x, 1) for x in range(5, 107)}, WOOD[0])
for lx in (8, 100):
    bench.blob(rect(lx, 0, 4, 12), WOOD[1:], WOOD_OUT)
    bench.blob(rect(lx, 18, 4, 20), WOOD[1:], WOOD_OUT)
for lx in (52,):
    bench.blob(rect(lx, 18, 4, 18), WOOD[1:], WOOD_OUT)
paste(img, bench, BX0, BY)
# soft shadow under it
for y in range(BY + 36, BY + 42):
    for x in range(BX0 + 4, BX0 + 110):
        if dith(x, y, 0.45):
            px[x, y] = mix(px[x, y], hexc("#1b1530"), 0.5)
# a folded blanket and a teacup on the bench
d.rectangle([BX0 + 16, BY + 7, BX0 + 40, BY + 12], fill=hexc("#c0584a"), outline=hexc("#5e1c24"))
d.line([BX0 + 17, BY + 8, BX0 + 39, BY + 8], fill=hexc("#f27a5c"))
d.line([BX0 + 17, BY + 10, BX0 + 39, BY + 10], fill=hexc("#ffe8b0"))
d.rectangle([BX0 + 84, BY + 7, BX0 + 89, BY + 11], fill=hexc("#e8e4f4"), outline=hexc("#5e5a84"))
px[BX0 + 90, BY + 9] = hexc("#5e5a84")

# tall vase of susuki beside the bench (the moon-viewing grass)
VX, VY = 344, 352
vase = Sprite(18, 34)
vm = ellipse(8.5, 22, 8, 11) | rect(5, 6, 8, 8)
vase.blob(vm, [hexc("#7d8fc4"), hexc("#5e6ea8"), hexc("#46528a"), hexc("#343e6e")], hexc("#1e2448"))
vase.fill({(x, 20) for x in range(1, 17)}, hexc("#e8e4f4"))
vase.fill({(x, 21) for x in range(1, 17) if x % 3 == 0}, hexc("#b9b3dc"))
vase.set(4, 16, hexc("#c8d0f0"))
vase.set(4, 17, hexc("#a8b4e0"))
paste(img, susuki(62, 99, lean=-1), VX + 9 - 31, VY - 56)
paste(img, susuki(54, 17, lean=1), VX + 9 - 27, VY - 46)
paste(img, vase, VX, VY)

# big foreground planters at the edges, with shrubs and grass
for (x, y, pw, (sw, sh), gh) in ((-10, 356, 70, (58, 44), 78), (444, 370, 64, (48, 36), 0)):
    if gh:
        paste(img, susuki(gh, y, lean=1), x + pw - 30 - gh // 2 + 20, y + 4 - gh)
    paste(img, shrub(sw, sh, x + y), x + (pw - sw) // 2, y - sh + 12)
    paste(img, planter(pw, 30), x, y)
    for yy in range(y + 30, y + 35):
        for xx in range(x + 2, x + pw):
            if 0 <= xx < W and dith(xx, yy, 0.45):
                px[xx, yy] = mix(px[xx, yy], hexc("#1b1530"), 0.5)
# a low stone lantern-light on the deck (a simple post light, warm)
for (lx, ly) in ((170, 330), (500, 322)):
    glow(lx + 3, ly + 3, 26, 18, 0.5, GLOW)
    d.rectangle([lx, ly - 6, lx + 6, ly + 12], fill=STONE[1], outline=BLD_OUT)
    d.rectangle([lx + 1, ly - 4, lx + 5, ly + 1], fill=LIT[0])
    d.line([lx + 1, ly - 4, lx + 5, ly - 4], fill=hexc("#fff4d6"))
    d.rectangle([lx - 1, ly - 8, lx + 7, ly - 6], fill=STONE[0], outline=BLD_OUT)

# warm lamplight pooling on the deck under the lantern strings
glow(320, 380, 300, 70, 0.18, GLOW)

# ------------------------------------------------------------- stars ------
# find open sky: pixels unchanged since the sky pass, with a clear margin
cards = []
locs = json.load(open(os.path.join(ASSETS, "..", "data", "locations.json")))
loc = next(l for l in locs if l["id"] == NAME)
for s in loc["slots"] + [loc["dealerSlot"]]:
    cards.append((s["x"] - 3, s["y"] - 3, s["x"] + 111, s["y"] + 107))
cards += [(0, 0, W, 32), (0, 34, 206, 76)]      # HUD bar, location banner
sky_px = sky_only.load()


def open_sky(x, y, m=3):
    for yy in range(y - m, y + m + 1):
        for xx in range(x - m, x + m + 1):
            if not (0 <= xx < W and 0 <= yy < H) or px[xx, yy] != sky_px[xx, yy]:
                return False
    return not any(a <= x <= b and c <= y <= e for (a, c, b, e) in cards)


stars = []
tries = 0
while len(stars) < 104 and tries < 20000:
    tries += 1
    x, y = R.randint(4, W - 5), int(R.random() ** 1.5 * (HORIZON - 30))
    if not open_sky(x, y) or any(abs(x - a) + abs(y - b) < 14 for (a, b) in stars):
        continue
    stars.append((x, y))
DIM, MID, BRIGHT = hexc("#8f88b8"), hexc("#b9b3dc"), hexc("#fff4d6")
for i, (x, y) in enumerate(stars):
    k = i % 13
    if k == 0:   # a few brighter ones with a tiny cross
        px[x, y] = BRIGHT
        for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            px[x + dx, y + dy] = mix(sky_px[x + dx, y + dy], MID, 0.55)
    elif k in (1, 2, 3, 4):
        px[x, y] = MID
    else:
        px[x, y] = mix(sky_px[x, y], DIM, 0.85)
# plus a faint dust of tiny extra-dim stars (not twinkled)
for _ in range(160):
    x, y = R.randint(0, W - 1), int(R.random() ** 1.3 * (HORIZON - 20))
    if open_sky(x, y, 1) and all(abs(x - a) + abs(y - b) > 3 for (a, b) in stars):
        px[x, y] = mix(sky_px[x, y], DIM, 0.4)

haze(img, hexc("#2a2450"), 0.06)

img = save_bg(img, NAME)
with open(os.path.join(ASSETS, "bg", NAME + "_stars.json"), "w") as f:
    json.dump([[x, y] for (x, y) in stars], f)
print(f"stars: {len(stars)}")
mock(img, NAME, NAME)
