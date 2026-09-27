"""640x480 Driftwood Pier: sunset sea, distant lighthouse, gulls, plank deck.

Soft, slightly hazy palette so the cream actor cards pop; the busy bits
(sun, lighthouse, railing) sit around the horizon and deck edge.
"""
import math
import random

from bgkit import W, H, new_bg, vgrad, dith, haze, paste, save_bg, mock
from pixelkit import Sprite, hexc, mix, ellipse, rect, edge

R = random.Random(31)
img, d = new_bg()
px = img.load()

HORIZON = 252
DECK = 364

# ------------------------------------------------------------------- sky ---
vgrad(img, 0, 0, W, HORIZON, [hexc("#a89cd0"), hexc("#d4a8c8"), hexc("#f4b8b8"), hexc("#fcd0a8"),
                              hexc("#fde6c0")])

# sun: big half disc with retro gaps, sitting on the horizon
SX, SR = 422, 44
for y in range(HORIZON - SR, HORIZON):
    for x in range(SX - SR, SX + SR + 1):
        if (x - SX) ** 2 + (y - HORIZON) ** 2 <= SR * SR:
            gap = y > HORIZON - 22 and (HORIZON - y) % 6 < (3 if y > HORIZON - 12 else 2)
            if not gap:
                t = (HORIZON - y) / SR
                px[x, y] = hexc("#fff4d0") if dith(x, y, t) else hexc("#ffe0a0")

# long streaky clouds
for (x0, y0, w, col) in ((20, 70, 180, "#e8b8d0"), (250, 48, 140, "#f0c0cc"), (470, 96, 170, "#f4c4c0"),
                         (90, 150, 120, "#f8d0bc"), (330, 176, 200, "#f8d8c0"), (560, 196, 90, "#fbe0c4")):
    c = hexc(col)
    hi = mix(c, hexc("#fff4ec"), 0.5)
    sh = mix(c, hexc("#a080a8"), 0.25)
    for i in range(3):
        yy = y0 + i * 4
        xa = x0 + i * 12 + R.randint(-4, 4)
        xb = x0 + w - i * 18 + R.randint(-4, 4)
        d.rectangle([xa, yy, xb, yy + 3], fill=c)
        d.line([xa + 2, yy, xb - 6, yy], fill=hi)
        d.line([xa + 4, yy + 3, xb, yy + 3], fill=sh)

# gulls
for (x, y) in ((150, 110), (172, 124), (520, 60), (540, 72), (300, 30), (600, 140)):
    for dx, dy in ((-3, -1), (-2, 0), (-1, 0), (0, 1), (1, 0), (2, 0), (3, -1)):
        px[x + dx, y + dy] = hexc("#6a5078")

# distant hills and the lighthouse island
for x in range(W):
    hh = 10 + 6 * math.sin(x / 40) + 4 * math.sin(x / 13 + 2)
    if x < 250:
        for y in range(int(HORIZON - hh), HORIZON):
            px[x, y] = hexc("#b89cc0") if y > HORIZON - hh + 1 else hexc("#c8acc8")
LX = 606
for x in range(LX - 44, min(W, LX + 40)):
    t = (x - (LX - 44)) / 84
    hh = int(12 * math.sin(math.pi * t) ** 0.6)
    for y in range(HORIZON - hh, HORIZON):
        px[x, y] = hexc("#a88cb4") if y > HORIZON - hh + 1 else hexc("#bca0c4")
# lighthouse
LB = HORIZON - 10
for y in range(LB - 46, LB):
    half = 5 + (y - (LB - 46)) * 3 // 46
    band = ((y - (LB - 46)) // 8) % 2
    for x in range(LX - half, LX + half + 1):
        c = hexc("#e87070") if band else hexc("#fbf1e4")
        if x > LX + half - 2:
            c = mix(c, hexc("#7a5a80"), 0.3)
        if x in (LX - half, LX + half):
            c = hexc("#6a4a6a")
        px[x, y] = c
d.rectangle([LX - 7, LB - 56, LX + 7, LB - 47], fill=hexc("#6a4a6a"))
d.rectangle([LX - 5, LB - 55, LX + 5, LB - 48], fill=hexc("#fff0a0"))
d.polygon([(LX - 8, LB - 57), (LX, LB - 64), (LX + 8, LB - 57)], fill=hexc("#6a4a6a"))
# lighthouse beam glow
for y in range(LB - 64, LB - 40):
    for x in range(LX - 60, min(W, LX + 60)):
        dist = math.hypot((x - LX) / 3, y - (LB - 52))
        if 3 < dist < 18 and dith(x, y, 0.25 * (1 - dist / 18)) and abs(y - (LB - 52)) < 5:
            px[x, y] = mix(px[x, y], hexc("#fff8d8"), 0.6)

# ------------------------------------------------------------------- sea ---
vgrad(img, 0, HORIZON, W, H, [hexc("#f4c8b8"), hexc("#c8a8c8"), hexc("#8ea0cc"), hexc("#7088b8"),
                              hexc("#6278a8")])
d.line([0, HORIZON, W, HORIZON], fill=hexc("#fff0d8"))
# sun reflection: broken horizontal streaks under the sun
for y in range(HORIZON + 2, DECK, 3):
    spread = 30 + (y - HORIZON) * 0.4
    for _ in range(3):
        w = R.randint(4, 18)
        x = int(SX + R.uniform(-spread, spread))
        c = hexc("#fff0c8") if y < HORIZON + 40 else hexc("#f8d8c0")
        d.line([x, y, x + w, y], fill=c)
# sparkles / ripples across the sea
for _ in range(160):
    x, y = R.randint(0, W - 10), R.randint(HORIZON + 4, H - 2)
    w = R.randint(3, 8)
    d.line([x, y, x + w, y], fill=mix(px[x, y], hexc("#e8e0f0"), 0.45))

# a little sailboat
boat = Sprite(30, 28)
hull = {(x, y) for y in range(19, 25) for x in range(3 + (y - 19), 27 - (y - 19))}
boat.blob(hull, [hexc("#f4a070"), hexc("#d8744e"), hexc("#a8543c")], hexc("#5a2a3a"), cuts=(-0.2, 0.5))
boat.fill(rect(14, 2, 1, 17), hexc("#5a3a3a"))
sail = {(x, y) for y in range(3, 18) for x in range(15, 15 + (y - 2) * 9 // 16 + 1)}
boat.blob(sail, [hexc("#fffaf0"), hexc("#f4e4d8"), hexc("#dcc8c8")], hexc("#7a5a70"), cuts=(0, 0.5))
paste(img, boat, 196, HORIZON - 14)
haze(img, hexc("#f6e4dc"), 0.18, (0, 0, W, DECK))

# ------------------------------------------------ boathouse on stilts, left ---
BH = Sprite(90, 150)
# stilts
for sx in (8, 36, 64, 80):
    BH.blob(rect(sx, 70, 5, 80), [hexc("#a07058"), hexc("#805040"), hexc("#603830")], hexc("#402028"),
            lx=1, ly=0, cuts=(-0.2, 0.5))
# walls
walls = rect(2, 34, 84, 40)
BH.blob(walls, [hexc("#b8d8d8"), hexc("#98c0c8"), hexc("#80a8b8")], hexc("#3a4a60"), cuts=(-0.5, 0.4))
for xx in range(6, 86, 6):
    for yy in range(35, 73):
        BH.set(xx, yy, hexc("#88b0bc"))
# roof
roof = {(x, y) for y in range(10, 35) for x in range(max(0, 44 - (y - 8) * 2), min(90, 46 + (y - 8) * 2))}
BH.blob(roof, [hexc("#f09a8a"), hexc("#d8746a"), hexc("#b05858")], hexc("#5a2a3a"), lx=0.8, ly=0.5,
        cuts=(-0.2, 0.4))
# window & door
BH.fill(rect(12, 44, 14, 12), hexc("#ffe8a8"))
BH.fill(edge(rect(11, 43, 16, 14)), hexc("#3a4a60"))
BH.set(13, 45, hexc("#fff8e0"))
BH.fill(rect(50, 46, 14, 28), hexc("#806070"))
BH.fill(edge(rect(49, 45, 16, 29)), hexc("#3a4a60"))
# lifebuoy
buoy = ellipse(75, 52, 6, 6) - ellipse(75, 52, 2.6, 2.6)
for (x, y) in buoy:
    ang = math.atan2(y - 52, x - 75)
    BH.set(x, y, hexc("#e8534e") if int((ang + math.pi) / (math.pi / 2)) % 2 else hexc("#fbf1e4"))
paste(img, BH, -8, DECK - 146)

# ------------------------------------------------------------------ deck ---
for y in range(DECK, H):
    depth = (y - DECK) / (H - DECK)
    rowh = 8 + int(depth * 6)
    base = mix(hexc("#d8a880"), hexc("#b88a68"), depth)
    for x in range(W):
        yy = (y - DECK)
        # plank rows get taller toward the viewer
        row = int(math.sqrt(yy * 2.2))
        edge_row = int(math.sqrt((yy + 1) * 2.2)) != row
        off = (row * 37) % 60
        seam = (x + off) % 60 == 0
        if edge_row:
            c = mix(base, hexc("#6a4038"), 0.55)
        elif seam:
            c = mix(base, hexc("#7a5040"), 0.45)
        else:
            grain = (x * 3 + row * 17) % 23 == 0
            c = mix(base, hexc("#a07058"), 0.3) if grain else base
            if (x + off) % 60 == 1:
                c = mix(base, hexc("#fff0d8"), 0.25)
        px[x, y] = c
# nails
for y in range(DECK + 4, H, 9):
    for x in range(R.randint(0, 20), W, 60):
        px[x, y] = hexc("#6a5058")

# back edge + railing posts with sagging rope
d.rectangle([0, DECK - 3, W, DECK], fill=hexc("#a07058"))
d.line([0, DECK - 3, W, DECK - 3], fill=hexc("#e0b890"))
POSTS = [x for x in range(28, W, 96)]
for i, x in enumerate(POSTS):
    post = Sprite(10, 44)
    post.blob(rect(1, 4, 8, 40), [hexc("#c89878"), hexc("#a07058"), hexc("#805040"), hexc("#603838")],
              hexc("#402028"), lx=1, ly=0.1, cuts=(-0.4, 0.2, 0.6))
    post.blob(rect(0, 0, 10, 5), [hexc("#e0b890"), hexc("#c09070")], hexc("#402028"), cuts=(0.2,))
    paste(img, post, x - 5, DECK - 40)
for a, b in zip(POSTS, POSTS[1:] + [W + 60]):
    for x in range(a + 4, min(W, b - 4)):
        t = (x - a) / (b - a)
        y = int(DECK - 32 + 9 * 4 * t * (1 - t))
        px[x, y] = hexc("#8a6a58")
        px[x, y + 1] = hexc("#e8d0b0")

# props on deck: crates, barrel, fishing rod, bucket
crate = Sprite(26, 22)
crate.blob(rect(1, 1, 24, 20), [hexc("#e8c090"), hexc("#d0a070"), hexc("#b08050")], hexc("#604030"),
           cuts=(-0.3, 0.4))
for xx in (8, 17):
    for yy in range(2, 21):
        crate.set(xx, yy, hexc("#b08050"))
for i in range(22):
    crate.set(2 + i, 2 + i * 18 // 22, hexc("#a07048"))
paste(img, crate, 360, DECK - 12)
paste(img, crate, 382, DECK - 6)
barrel = Sprite(20, 26)
bm = rect(2, 1, 16, 24) | rect(1, 4, 18, 18)
barrel.blob(bm, [hexc("#c89070"), hexc("#a87050"), hexc("#886048")], hexc("#503038"), lx=1, ly=0.2,
            cuts=(-0.3, 0.4))
for yy in (6, 18):
    for xx in range(1, 19):
        barrel.set(xx, yy, hexc("#6a6070"))
paste(img, barrel, 222, DECK - 10)
# fishing rod leaning on a post
for i in range(70):
    x = POSTS[4] + 6 + i * 3 // 4
    y = DECK - 8 - i
    if 0 <= x < W:
        px[x, y] = hexc("#5a3a3a")
line_x = POSTS[4] + 6 + 52
d.line([line_x, DECK - 78, line_x + 40, DECK + 0], fill=hexc("#e8e0f0"))

# warm sunset wash over the deck to keep contrast low
haze(img, hexc("#f8d8c0"), 0.14, (0, DECK - 44, W, H))
haze(img, hexc("#fbece0"), 0.06)

img = save_bg(img, "driftwood_pier")
mock(img, "driftwood_pier", "driftwood_pier")
