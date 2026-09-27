"""640x480 Lamplight Lane: dusk street, glowing lamps, shop fronts, a record shop.

Evening palette, but kept soft (no near-black) so the cream actor cards pop.
"""
import math
import random

from bgkit import W, H, new_bg, vgrad, dith, haze, paste, save_bg, mock
from pixelkit import Sprite, hexc, mix, ellipse, rect, edge

R = random.Random(41)
img, d = new_bg()
px = img.load()

WALK = 352     # sidewalk top
STREET = 370   # cobbles start

# ------------------------------------------------------------------- sky ---
vgrad(img, 0, 0, W, 240, [hexc("#3e3c74"), hexc("#5a4c8c"), hexc("#8a64a0"), hexc("#c880a4"),
                          hexc("#eea4a0")])
for _ in range(90):
    x, y = R.randint(0, W - 1), R.randint(32, 150)
    px[x, y] = mix(px[x, y], hexc("#fff4d8"), R.choice((0.5, 0.8, 1.0)))
for (x, y) in ((96, 60), (410, 44), (300, 90), (520, 120)):  # twinkly crosses
    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
        px[x + dx, y + dy] = hexc("#fff4d8")
# crescent moon
moon = ellipse(560, 70, 16, 16) - ellipse(567, 64, 14, 14)
for (x, y) in moon:
    px[x, y] = hexc("#fff0c0") if x < 552 else hexc("#f8dca0")
for (x, y) in edge(moon):
    px[x, y] = hexc("#e8c088")
for y in range(40, 102):  # soft halo
    for x in range(528, 594):
        r = math.hypot(x - 560, y - 70)
        if 17 < r < 30 and dith(x, y, 0.28 * (1 - (r - 17) / 13)):
            px[x, y] = mix(px[x, y], hexc("#fff0c0"), 0.35)

# far rooftops silhouette with chimneys
for x in range(W):
    h = 176 + int(10 * math.sin(x / 31) + 6 * math.sin(x / 11 + 1))
    if (x // 46) % 3 == 0:
        h -= 14 - abs((x % 46) - 23) // 2
    for y in range(h, 250):
        px[x, y] = hexc("#6a5288")
for cx in (40, 150, 262, 380, 470, 600):
    d.rectangle([cx, 160, cx + 6, 186], fill=hexc("#6a5288"))
    d.rectangle([cx - 1, 158, cx + 7, 161], fill=hexc("#7a62a0"))
haze(img, hexc("#c890b4"), 0.12, (0, 150, W, 250))

# --------------------------------------------------------------- shops ---
LIT = hexc("#ffd88a")
LIT_HI = hexc("#fff4c8")
DARKWIN = hexc("#4a4a7a")


def building(x, w, top, col, awning=None, sign=None, roof="flat"):
    outl = mix(col, hexc("#241a3a"), 0.6)
    shade = mix(col, hexc("#3a2a58"), 0.3)
    light = mix(col, hexc("#fff0e0"), 0.18)
    d.rectangle([x, top, x + w - 1, WALK], fill=col, outline=outl)
    d.line([x + 1, top + 1, x + 1, WALK], fill=light)
    d.rectangle([x + w - 5, top + 1, x + w - 2, WALK], fill=shade)
    if roof == "gable":
        d.polygon([(x - 3, top), (x + w // 2, top - 22), (x + w + 2, top)], fill=mix(col, hexc("#3a2a58"), 0.45),
                  outline=outl)
        d.line([x + 2, top - 1, x + w // 2, top - 20], fill=mix(col, hexc("#fff0e0"), 0.1))
    else:
        d.rectangle([x - 3, top - 6, x + w + 2, top], fill=mix(col, hexc("#fff0e0"), 0.1), outline=outl)
    # upper windows
    for wy in range(top + 12, WALK - 72, 30):
        for wx in range(x + 10, x + w - 18, 22):
            lit = R.random() < 0.62
            d.rectangle([wx, wy, wx + 11, wy + 16], fill=LIT if lit else DARKWIN, outline=outl)
            d.line([wx + 6, wy + 1, wx + 6, wy + 15], fill=outl)
            d.line([wx + 1, wy + 8, wx + 10, wy + 8], fill=outl)
            if lit:
                d.line([wx + 1, wy + 1, wx + 4, wy + 1], fill=LIT_HI)
            d.rectangle([wx - 1, wy + 17, wx + 12, wy + 18], fill=light)
    # shop window + door on the ground floor
    sw_top = WALK - 44
    d.rectangle([x + 8, sw_top, x + w - 30, WALK - 8], fill=LIT, outline=outl)
    d.line([x + 9, sw_top + 1, x + 16, sw_top + 1], fill=LIT_HI)
    # little things in the window
    for ix in range(x + 12, x + w - 36, 9):
        c = R.choice([hexc("#c8704e"), hexc("#8a5a8a"), hexc("#5a8a7a"), hexc("#d89a5a")])
        hgt = R.randint(5, 12)
        d.rectangle([ix, WALK - 9 - hgt, ix + 5, WALK - 9], fill=mix(c, LIT, 0.25))
    d.rectangle([x + w - 24, WALK - 38, x + w - 10, WALK], fill=mix(col, hexc("#241a3a"), 0.4), outline=outl)
    if x + w - 13 < W:
        px[x + w - 13, WALK - 20] = LIT
    if awning:
        a0 = sw_top - 12
        for ax in range(max(0, x + 4), min(W, x + w - 4)):
            on = ((ax - x) // 7) % 2 == 0
            c = awning if on else hexc("#f4e4d8")
            for ay in range(a0, a0 + 9):
                cc = mix(c, hexc("#3a2a58"), 0.25 * (ay - a0) / 9)
                px[ax, ay] = cc
            if (ax - x) % 7 in (2, 3, 4):
                px[ax, a0 + 9] = mix(c, hexc("#3a2a58"), 0.25)
        d.line([x + 4, a0 - 1, x + w - 5, a0 - 1], fill=outl)
    if sign:
        sign(x, w, sw_top)


def record_sign(x, w, sw_top):
    """Hanging vinyl-disc sign for the record shop."""
    cx, cy = x + w - 6, sw_top - 44
    d.line([x + w - 20, cy - 16, cx + 12, cy - 16], fill=hexc("#2a2040"))
    d.line([cx, cy - 16, cx, cy - 13], fill=hexc("#2a2040"))
    disc = Sprite(28, 28)
    m = ellipse(13.5, 13.5, 12.6, 12.6)
    disc.blob(m, [hexc("#6a5a8c"), hexc("#46395f"), hexc("#342a4a")], hexc("#1e1630"), cuts=(-0.4, 0.3))
    for p in edge(ellipse(13.5, 13.5, 8.5, 8.5)):
        disc.set(*p, hexc("#2a2140"))
    disc.blob(ellipse(13.5, 13.5, 4, 4), [hexc("#ff9a8a"), hexc("#e8534e")], None, cuts=(0.2,))
    disc.set(13, 13, hexc("#1e1630"))
    disc.set(6, 7, hexc("#b8a8e0"))
    disc.set(7, 6, hexc("#b8a8e0"))
    paste(img, disc, cx - 14, cy - 13)


def cafe_sign(x, w, sw_top):
    """Little teacup sign."""
    cx, cy = x + 26, sw_top - 30
    d.rectangle([cx - 14, cy - 10, cx + 14, cy + 8], fill=hexc("#f4e4d8"), outline=hexc("#5a3a4a"))
    d.rectangle([cx - 7, cy - 4, cx + 5, cy + 4], fill=hexc("#e8888a"), outline=hexc("#7a3a4a"))
    d.rectangle([cx + 6, cy - 2, cx + 8, cy + 2], outline=hexc("#7a3a4a"))
    for i, sx in enumerate((cx - 4, cx, cx + 3)):
        px[sx, cy - 7 - i % 2] = hexc("#b8a8c0")


SHOPS = [
    (-6, 96, 128, hexc("#7a8cb8"), hexc("#d8746a"), None, "flat"),
    (90, 86, 150, hexc("#b88a9a"), hexc("#6aa89a"), cafe_sign, "gable"),
    (176, 110, 118, hexc("#8aa89a"), None, None, "flat"),
    (286, 104, 138, hexc("#c89a78"), hexc("#8a74c0"), record_sign, "flat"),
    (390, 92, 160, hexc("#9a84b8"), hexc("#e0a050"), None, "gable"),
    (482, 84, 124, hexc("#a8788a"), None, None, "flat"),
    (566, 90, 142, hexc("#7aa0b0"), hexc("#d8746a"), None, "gable"),
]
for (x, w, top, col, aw, sign, roof) in SHOPS:
    building(x, w, top, col, aw, sign, roof)

# dusk haze on the facades
haze(img, hexc("#8a6aa0"), 0.16, (0, 100, W, WALK))

# ------------------------------------------------------------- sidewalk ---
for y in range(WALK, STREET):
    for x in range(W):
        seam = (x % 32 == 0) or (y - WALK) % 9 == 8
        c = hexc("#9c90b0") if not seam else hexc("#7a6e94")
        if (y - WALK) % 9 == 0 and not seam:
            c = hexc("#b4a8c4")
        px[x, y] = c
d.rectangle([0, STREET - 3, W, STREET - 1], fill=hexc("#b8acc8"))
d.line([0, STREET - 1, W, STREET - 1], fill=hexc("#5e5480"))

# ------------------------------------------------------------- cobbles ---
d.rectangle([0, STREET, W, H], fill=hexc("#5a5078"))
y = STREET + 1
row = 0
while y < H:
    rh = 7 + row // 3
    x = -((row * 9) % 18)
    while x < W:
        sw = R.randint(12, 17)
        tone = R.choice(["#8a80a8", "#8078a0", "#948ab0", "#7a7098"])
        base = hexc(tone)
        stone = {(sx, sy) for sx in range(x + 1, x + sw - 1) for sy in range(y + 1, y + rh - 1)}
        stone -= {(x + 1, y + 1), (x + sw - 2, y + 1), (x + 1, y + rh - 2), (x + sw - 2, y + rh - 2)}
        for (sx, sy) in stone:
            if 0 <= sx < W and sy < H:
                c = base
                if sy == y + 1 or sx == x + 1:
                    c = mix(base, hexc("#d8d0e8"), 0.35)
                elif sy == y + rh - 2 or sx == x + sw - 2:
                    c = mix(base, hexc("#3a2a58"), 0.25)
                px[sx, sy] = c
        x += sw
    y += rh
    row += 1

# ---------------------------------------------------------------- lamps ---
LAMPS = [22, 214, 426, 616]


def glow(cx, cy, rx, ry, strength, color):
    for yy in range(max(0, int(cy - ry)), min(H, int(cy + ry) + 1)):
        for xx in range(max(0, int(cx - rx)), min(W, int(cx + rx) + 1)):
            r = math.hypot((xx - cx) / rx, (yy - cy) / ry)
            if r < 1:
                t = strength * (1 - r) ** 1.4
                px[xx, yy] = mix(px[xx, yy], color, min(0.55, t * 1.4)) if dith(xx, yy, min(1, t * 2.2)) \
                    else mix(px[xx, yy], color, t * 0.5)


for lx in LAMPS:
    glow(lx, STREET + 18, 64, 20, 0.7, hexc("#ffd88a"))   # pool of light on the ground
    glow(lx, 238, 40, 40, 0.55, hexc("#ffe0a0"))          # halo around the lamp head
for lx in LAMPS:
    lamp = Sprite(22, 130)
    post = rect(9, 20, 4, 108)
    lamp.blob(post, [hexc("#5a5a8a"), hexc("#3e3c6a"), hexc("#2c2a50")], hexc("#1c1a38"), lx=1, ly=0,
              cuts=(-0.3, 0.4))
    lamp.blob(rect(6, 122, 10, 7), [hexc("#5a5a8a"), hexc("#3e3c6a")], hexc("#1c1a38"), cuts=(0.2,))
    lamp.blob(rect(7, 60, 8, 4), [hexc("#5a5a8a"), hexc("#3e3c6a")], hexc("#1c1a38"), cuts=(0.2,))
    # lantern head
    head = {(x, y) for y in range(6, 20) for x in range(4 + (y < 9) * (9 - y), 18 - (y < 9) * (9 - y))}
    lamp.fill(head, hexc("#1c1a38"))
    glass = {(x, y) for y in range(9, 18) for x in range(6, 16)}
    lamp.blob(glass, [hexc("#fffae0"), hexc("#ffe8a0"), hexc("#ffd070")], None, cuts=(-0.2, 0.5))
    lamp.fill({(10, y) for y in range(9, 18)} | {(11, y) for y in range(9, 18)}, hexc("#3e3c6a"))
    lamp.fill(rect(8, 2, 6, 4), hexc("#1c1a38"))
    lamp.set(10, 1, hexc("#1c1a38"))
    paste(img, lamp, lx - 11, 228)

# a cat on the sidewalk, and a few leaves blowing
cat = Sprite(18, 12)
body = ellipse(8, 7, 6, 3.6) | ellipse(13, 4, 3, 2.8)
cat.blob(body, [hexc("#4a4270"), hexc("#3a3460"), hexc("#2c2850")], hexc("#1c1a38"), cuts=(-0.2, 0.5))
cat.set(12, 1, hexc("#1c1a38"))
cat.set(15, 1, hexc("#1c1a38"))
cat.set(14, 4, hexc("#ffe08a"))
for i in range(5):
    cat.set(2 - i // 3, 7 - i, hexc("#2c2850"))
paste(img, cat, 344, WALK - 2)
for _ in range(26):
    x, y = R.randint(0, W - 2), R.randint(STREET + 4, H - 2)
    c = R.choice([hexc("#e8a060"), hexc("#d8746a"), hexc("#f0c070")])
    px[x, y] = c
    px[x + 1, y] = mix(c, hexc("#3a2a58"), 0.3)

haze(img, hexc("#e8c8d8"), 0.06)

img = save_bg(img, "lamplight_lane")
mock(img, "lamplight_lane", "lamplight_lane")
