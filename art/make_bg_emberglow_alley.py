"""640x480 Emberglow Alley: a yokocho lane of tiny two-storey bars at night.

Rows of red lanterns (akachochin) at the eaves, plain noren curtains with slits
(no writing anywhere), warm counters with stools, grill smoke curling up, crates
and potted plants, utility poles with sagging wires, and a strip of starry night
sky above the rooftops. Kept soft and dim so the cream actor cards pop.

Also writes emberglow_alley_stars.json: the baked twinkle-star positions (only
stars still in open sky once everything else is drawn).
"""
import json
import math
import os
import random

from bgkit import W, H, new_bg, vgrad, dith, haze, paste, save_bg, mock
from pixelkit import ASSETS, Sprite, hexc, mix, ellipse, rect, edge
from snowkit import glow

R = random.Random(314)
img, d = new_bg()
px = img.load()

GROUND = 352   # lane starts
EAVE = 236     # ground-floor eave line

OUTLINE = hexc("#17142b")
LIT = hexc("#ffd98a")
LIT2 = hexc("#f7b861")
LIT_DIM = hexc("#b8834a")
RED = [hexc("#f27a5c"), hexc("#e0503f"), hexc("#a8332f")]
RED_OUT = hexc("#5e1c24")
GLOW = hexc("#ff9a4a")
CREAM = hexc("#ffe3a8")
IN1 = mix(LIT, LIT_DIM, 0.22)   # interiors, a touch dimmer than the cards
IN2 = mix(LIT2, LIT_DIM, 0.3)

# ------------------------------------------------------------------- sky ---
vgrad(img, 0, 0, W, 200, [hexc("#141129"), hexc("#1b1733"), hexc("#252045"), hexc("#2f2a58"),
                          hexc("#3d2a52"), hexc("#553a6a")])
# faint warm city glow low in the sky
for y in range(110, 200):
    t = (y - 110) / 90
    for x in range(W):
        if dith(x, y, t * 0.35):
            px[x, y] = mix(px[x, y], hexc("#8a4a5e"), 0.35)
sky_only = img.copy()

# baked stars: (x, y, bright). Export candidates are the brighter ones.
STARS = []
for _ in range(120):
    x, y = R.randint(2, W - 3), R.randint(32, 150)
    b = R.random()
    STARS.append((x, y, b))
for (x, y, b) in STARS:
    if b > 0.93:
        c = hexc("#fff4d6")
    elif b > 0.6:
        c = hexc("#b9b3dc")
    else:
        c = hexc("#8f88b8")
    px[x, y] = mix(px[x, y], c, 0.55 + 0.4 * b)
    if b > 0.93:  # tiny cross on the brightest
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            px[x + dx, y + dy] = mix(px[x + dx, y + dy], c, 0.35)
sky_stars = img.copy()

# ------------------------------------------------------ far city blocks ---
FAR = hexc("#2a2548")
for (fx, fw, ft) in ((-4, 70, 118), (120, 46, 96), (300, 58, 124), (408, 40, 104), (560, 90, 112)):
    d.rectangle([fx, ft, fx + fw, 200], fill=FAR)
    d.line([fx, ft, fx + fw, ft], fill=mix(FAR, hexc("#553a6a"), 0.5))
    for wy in range(ft + 8, 200, 10):
        for wx in range(fx + 5, fx + fw - 4, 8):
            if 0 <= wx < W - 2 and R.random() < 0.22:
                d.rectangle([wx, wy, wx + 2, wy + 3], fill=mix(FAR, LIT_DIM, 0.55))
d.line([438, 104, 438, 88], fill=FAR)  # antenna mast
px[438, 87] = hexc("#c0504a")

# ---------------------------------------------------------- the bars -------
LANTERN_POS = []   # (x, y, big) drawn after everything so they sit on top


def lantern_sprite(big=True):
    """Akachochin: a round ribbed red paper lantern with dark caps (no writing)."""
    w, h = (13, 18) if big else (7, 9)
    S = Sprite(w, h)
    cap = 2 if big else 1
    body = ellipse((w - 1) / 2, (h - 1) / 2, w / 2 - 0.2, (h - 2 * cap) / 2 + 0.6)
    body = {p for p in body if cap <= p[1] < h - cap}
    S.blob(body, RED, RED_OUT, lx=0.8, ly=0.4, cuts=(-0.35, 0.35))
    if big:
        for ry in range(cap + 3, h - cap - 1, 3):  # ribs
            for rx in range(w):
                if (rx, ry) in body and (rx, ry) not in edge(body):
                    S.set(rx, ry, mix(S.get(rx, ry), RED_OUT, 0.45))
        S.set(3, cap + 2, hexc("#ffc0a0"))
        S.set(3, cap + 3, hexc("#ffc0a0"))
    else:
        S.set(2, 3, hexc("#ffb090"))
    cw = w // 2 - (1 if big else 0)
    for yy in list(range(cap)) + list(range(h - cap, h)):
        for xx in range((w - cw) // 2, (w - cw) // 2 + cw + (1 if big else 0)):
            S.set(xx, yy, hexc("#2a1c28"))
    return S


BIG_LANTERN = lantern_sprite(True)
SMALL_LANTERN = lantern_sprite(False)


def noren(x0, x1, top, bottom, col):
    """Plain cloth door curtain with vertical slits and a rod on top."""
    shade = mix(col, hexc("#141129"), 0.35)
    light = mix(col, hexc("#ffe3a8"), 0.18)
    n = max(2, round((x1 - x0) / 14))
    pw = (x1 - x0) / n
    d.line([x0 - 2, top - 1, x1 + 2, top - 1], fill=hexc("#6a4a3a"))
    for i in range(n):
        a = int(x0 + i * pw) + (1 if i else 0)
        b = int(x0 + (i + 1) * pw) - 1
        drop = bottom + (1 if i % 2 else 0)
        for yy in range(top, drop + 1):
            for xx in range(a, b + 1):
                c = col
                if xx == a:
                    c = light
                elif xx >= b - 1:
                    c = shade
                if yy == drop:
                    c = shade
                if 0 <= xx < W:
                    px[xx, yy] = c
        # a single light band near the top: simple, no lettering
        for xx in range(a + 1, b):
            if 0 <= xx < W:
                px[xx, top + 3] = mix(col, hexc("#ffe8b0"), 0.35)


def stool(x, y, seat):
    """Little round bar stool with its seat top at y."""
    leg = hexc("#3a3048")
    d.rectangle([x - 5, y, x + 5, y + 2], fill=seat, outline=mix(seat, OUTLINE, 0.6))
    d.line([x - 4, y, x + 2, y], fill=mix(seat, hexc("#ffe3a8"), 0.3))
    d.line([x - 3, y + 3, x - 4, GROUND - 1], fill=leg)
    d.line([x + 3, y + 3, x + 4, GROUND - 1], fill=leg)
    d.line([x - 3, y + 12, x + 3, y + 12], fill=leg)


def bar(x, w, top, col, noren_col, opts):
    outl = mix(col, OUTLINE, 0.65)
    shade = mix(col, hexc("#141129"), 0.3)
    light = mix(col, hexc("#ffe3a8"), 0.12)
    d.rectangle([x, top, x + w - 1, GROUND], fill=col, outline=outl)
    d.line([x + 1, top + 1, x + 1, GROUND], fill=light)
    d.rectangle([x + w - 5, top + 1, x + w - 2, GROUND], fill=shade)
    # parapet / roof edge
    if opts.get("roof") == "tile":
        for xx in range(x - 4, x + w + 4):
            for yy in range(top - 10, top + 2):
                ry = top - 10 + max(0, 6 - (xx - (x - 4))) if xx < x + 2 else top - 10
                ry = max(ry, top - 10 + max(0, (xx - (x + w - 2))))
                if yy >= ry and 0 <= xx < W:
                    c = hexc("#3a3a5c") if (xx - x) % 4 else hexc("#2a2744")
                    if yy == ry:
                        c = hexc("#5a5680")
                    px[xx, yy] = c
        d.line([x - 4, top + 2, x + w + 3, top + 2], fill=OUTLINE)
    else:
        d.rectangle([x - 2, top - 4, x + w + 1, top], fill=mix(col, hexc("#8a7ab0"), 0.25), outline=outl)
    # roof clutter
    if opts.get("tank"):
        tx = x + w - 30
        d.rectangle([tx, top - 18, tx + 16, top - 5], fill=hexc("#3a3658"), outline=OUTLINE)
        d.line([tx + 1, top - 17, tx + 1, top - 6], fill=hexc("#5a5680"))
        d.line([tx + 3, top - 4, tx + 3, top - 1], fill=OUTLINE)
        d.line([tx + 13, top - 4, tx + 13, top - 1], fill=OUTLINE)
    if opts.get("aerial"):
        ax = x + 18
        d.line([ax, top - 26, ax, top - 5], fill=OUTLINE)
        for i, yy in enumerate((top - 24, top - 19, top - 14)):
            d.line([ax - 7 + i, yy, ax + 7 - i, yy], fill=OUTLINE)
    # upper floor windows
    for (wx, ww, kind) in opts.get("windows", []):
        wx += x
        wy = top + 22
        wh = 30
        if kind == "lit":
            glow(img, wx + ww / 2, wy + wh / 2, ww, wh * 0.9, 0.18, GLOW)
            d.rectangle([wx, wy, wx + ww, wy + wh], fill=LIT2, outline=outl)
            d.line([wx + 1, wy + 1, wx + 1 + ww // 3, wy + 1], fill=LIT)
            d.line([wx + ww // 2, wy + 1, wx + ww // 2, wy + wh - 1], fill=mix(LIT2, outl, 0.5))
        elif kind == "blind":  # sudare: bamboo blind lit from behind
            glow(img, wx + ww / 2, wy + wh / 2, ww, wh * 0.9, 0.14, GLOW)
            d.rectangle([wx, wy, wx + ww, wy + wh], fill=LIT_DIM, outline=outl)
            for yy in range(wy + 2, wy + wh, 2):
                d.line([wx + 1, yy, wx + ww - 1, yy], fill=mix(LIT_DIM, hexc("#6a4a3a"), 0.6))
            d.line([wx + 1, wy + 1, wx + ww - 1, wy + 1], fill=LIT2)
        else:  # dark
            d.rectangle([wx, wy, wx + ww, wy + wh], fill=hexc("#2a2744"), outline=outl)
            d.line([wx + ww // 2, wy + 1, wx + ww // 2, wy + wh - 1], fill=outl)
            d.line([wx + 2, wy + 2, wx + 5, wy + 2], fill=hexc("#4d4670"))
        d.rectangle([wx - 2, wy + wh + 1, wx + ww + 2, wy + wh + 2], fill=light)
        if opts.get("plant_sill") == wx - x:
            for i in range(3):
                bx = wx + 2 + i * 6
                d.rectangle([bx, wy + wh - 3, bx + 3, wy + wh], fill=hexc("#8a5a44"))
                for (lx, ly) in ((0, -5), (1, -6), (2, -4), (3, -6), (-1, -3), (4, -3), (1, -4), (2, -7)):
                    px[bx + lx, wy + wh - 1 + ly] = hexc("#3f6b55") if (lx + ly) % 2 else hexc("#2b4f47")
    # AC unit
    if "ac" in opts:
        ax, ay = x + opts["ac"], top + 60
        d.rectangle([ax, ay, ax + 18, ay + 12], fill=hexc("#5a5678"), outline=OUTLINE)
        d.line([ax + 1, ay + 1, ax + 17, ay + 1], fill=hexc("#7a76a0"))
        d.ellipse([ax + 3, ay + 2, ax + 11, ay + 10], outline=hexc("#3a3658"))
        d.line([ax + 14, ay + 3, ax + 14, ay + 10], fill=hexc("#3a3658"))
    # vertical light box sign: plain cream panel with a red band (no writing)
    if "signbox" in opts:
        sx, sy = x + opts["signbox"], top + 14
        glow(img, sx + 5, sy + 24, 20, 34, 0.3, CREAM)
        d.rectangle([sx, sy, sx + 11, sy + 48], fill=hexc("#ffe8b0"), outline=RED_OUT)
        d.rectangle([sx + 1, sy + 1, sx + 10, sy + 6], fill=RED[1])
        d.rectangle([sx + 1, sy + 42, sx + 10, sy + 47], fill=RED[1])
        d.line([sx + 1, sy + 7, sx + 1, sy + 41], fill=hexc("#fff4d6"))
        d.rectangle([sx - 4, sy + 10, sx - 1, sy + 11], fill=OUTLINE)
        d.rectangle([sx - 4, sy + 38, sx - 1, sy + 39], fill=OUTLINE)
    # drainpipe
    if "pipe" in opts:
        pxx = x + opts["pipe"]
        d.rectangle([pxx, top + 2, pxx + 2, GROUND - 1], fill=hexc("#3a3658"))
        d.line([pxx, top + 2, pxx, GROUND - 1], fill=hexc("#5a5680"))
    # eave: small slate pent roof over the ground floor
    for xx in range(x - 3, x + w + 3):
        for yy in range(EAVE - 6, EAVE + 5):
            if 0 <= xx < W:
                c = hexc("#3d3860") if (xx - x) % 5 else hexc("#2c2848")
                if yy == EAVE - 6:
                    c = hexc("#5e5888")
                if yy >= EAVE + 3:
                    c = OUTLINE
                px[xx, yy] = c
    # a row of small lanterns hanging along the eave
    for lx in range(x + 6, x + w - 6, opts.get("lspace", 16)):
        LANTERN_POS.append((lx, EAVE + 5, False))
    # ground floor opening with warm interior
    o0, o1 = x + opts["open"][0], x + opts["open"][1]
    otop = EAVE + 10
    glow(img, (o0 + o1) / 2, GROUND + 12, (o1 - o0) * 0.9, 34, 0.5, GLOW)
    for yy in range(otop, GROUND):
        t = (yy - otop) / (GROUND - otop)
        for xx in range(o0, o1):
            if 0 <= xx < W:
                a, b = (IN2, IN1) if t < 0.5 else (IN1, IN2)
                px[xx, yy] = b if dith(xx, yy, 0.5 - abs(t - 0.5)) else a
    d.rectangle([o0 - 1, otop - 1, o1, GROUND], outline=hexc("#4a3040"))
    # back shelf with bottles / bowls
    for bx in range(o0 + 4, o1 - 4, 5):
        c = R.choice([hexc("#7a5a3a"), hexc("#5a7a5a"), hexc("#a86a3a"), hexc("#e8d4b0")])
        hh = R.randint(3, 7)
        d.rectangle([bx, otop + 38 - hh, bx + 2, otop + 38], fill=mix(c, LIT, 0.2))
    d.line([o0, otop + 39, o1 - 1, otop + 39], fill=hexc("#8a5a3a"))
    # counter
    ct = GROUND - 36
    d.rectangle([o0 - 2, ct, o1 + 1, ct + 4], fill=hexc("#c88a52"), outline=hexc("#5a3428"))
    d.line([o0 - 1, ct + 1, o1, ct + 1], fill=hexc("#f0b878"))
    d.rectangle([o0, ct + 5, o1 - 1, GROUND - 1], fill=hexc("#6a4034"))
    for vx in range(o0 + 3, o1 - 2, 6):
        d.line([vx, ct + 6, vx, GROUND - 2], fill=hexc("#5a3428"))
    # little dishes and cups on the counter
    for cx in range(o0 + 6, o1 - 6, 11):
        if R.random() < 0.7:
            d.rectangle([cx, ct - 3, cx + 4, ct - 1], fill=hexc("#f4e8d0"), outline=hexc("#8a6a5a"))
        else:
            d.rectangle([cx + 1, ct - 5, cx + 3, ct - 1], fill=hexc("#e8c070"), outline=hexc("#7a5030"))
    # noren over the top of the opening
    noren(o0 + 1, o1 - 2, otop, otop + 30, noren_col)
    # stools at the counter
    for sx in range(o0 + 8, o1 - 4, 16):
        stool(sx, ct + 12, hexc("#c0504a") if opts.get("red_stools") else hexc("#8a6a5a"))
    # big lanterns either side of the opening
    LANTERN_POS.append((o0 - 9, otop - 2, True))
    LANTERN_POS.append((o1 + 9, otop - 2, True))
    return o0, o1


BARS = [
    # x, w, top, wall, noren, opts
    (-6, 92, 132, hexc("#403a5e"), hexc("#2e3a6a"),
     dict(open=(18, 76), windows=[(14, 24, "lit"), (52, 22, "dark")], ac=60, roof="tile", plant_sill=14)),
    (86, 94, 116, hexc("#4a3a50"), hexc("#b8443c"),
     dict(open=(18, 78), windows=[(12, 30, "blind"), (56, 20, "lit")], tank=True, pipe=88, red_stools=True)),
    (180, 84, 140, hexc("#34304f"), hexc("#e8dcc0"),
     dict(open=(14, 66), windows=[(34, 22, "lit")], signbox=6, roof="tile", ac=60, grill=True)),
    (264, 116, 108, hexc("#4d4670"), hexc("#3a5a4a"),
     dict(open=(22, 94), windows=[(14, 24, "dark"), (46, 24, "lit"), (80, 24, "blind")], aerial=True,
          lspace=18)),
    (380, 90, 128, hexc("#453650"), hexc("#b8443c"),
     dict(open=(16, 74), windows=[(40, 30, "blind")], signbox=12, pipe=86, plant_sill=40, red_stools=True)),
    (470, 90, 114, hexc("#3a3658"), hexc("#2e3a6a"),
     dict(open=(16, 74), windows=[(14, 22, "lit"), (52, 24, "dark")], tank=True, roof="tile")),
    (560, 86, 136, hexc("#4a3a50"), hexc("#e8dcc0"),
     dict(open=(14, 70), windows=[(12, 22, "blind"), (46, 22, "lit")], ac=50)),
]
OPENINGS = []
for (bx, bw, bt, col, ncol, opts) in BARS:
    OPENINGS.append(bar(bx, bw, bt, col, ncol, opts))

# gaps between bars: dark slivers of back-alley
for (bx, bw, bt, col, ncol, opts) in BARS[1:]:
    d.line([bx, bt + 2, bx, GROUND], fill=OUTLINE)

# ------------------------------------------------------ utility poles ----
POLE = hexc("#2a2440")
POLES = [(176, 92), (466, 86)]
for (pxx, ptop) in POLES:
    d.rectangle([pxx - 2, ptop, pxx + 2, GROUND + 2], fill=POLE, outline=OUTLINE)
    d.line([pxx - 1, ptop + 1, pxx - 1, GROUND + 1], fill=hexc("#403a5e"))
    d.rectangle([pxx - 16, ptop + 8, pxx + 16, ptop + 10], fill=POLE, outline=OUTLINE)
    for ix in (pxx - 13, pxx - 5, pxx + 5, pxx + 13):
        d.rectangle([ix, ptop + 5, ix + 1, ptop + 7], fill=hexc("#8a86a8"))
    d.rectangle([pxx + 3, ptop + 30, pxx + 10, ptop + 42], fill=hexc("#3a3658"), outline=OUTLINE)  # transformer

WIRE = hexc("#120f24")


def wire(ax, ay, bx, by, sag):
    n = int(abs(bx - ax)) + 1
    last = None
    for i in range(n + 1):
        t = i / n
        x = int(round(ax + (bx - ax) * t))
        y = int(round(ay + (by - ay) * t + sag * math.sin(math.pi * t)))
        if last and abs(y - last[1]) > 1:
            for yy in range(min(y, last[1]) + 1, max(y, last[1])):
                if 0 <= x < W and 0 <= yy < H:
                    px[x, yy] = WIRE
        if 0 <= x < W and 0 <= y < H:
            px[x, y] = WIRE
        last = (x, y)


p0, p1 = POLES
wire(-2, 70, p0[0] - 13, p0[1] + 5, 10)
wire(-2, 84, p0[0] - 5, p0[1] + 5, 8)
wire(p0[0] - 13, p0[1] + 5, p1[0] - 13, p1[1] + 5, 22)
wire(p0[0] + 5, p0[1] + 5, p1[0] + 5, p1[1] + 5, 30)
wire(p0[0] + 13, p0[1] + 5, p1[0] + 13, p1[1] + 5, 16)
wire(p1[0] + 13, p1[1] + 5, W + 2, 66, 12)
wire(p1[0] + 5, p1[1] + 5, W + 2, 90, 16)
wire(p0[0] + 3, p0[1] + 36, 250, 160, 4)   # drops to the buildings
wire(p1[0] - 3, p1[1] + 36, 520, 150, 3)
wire(p0[0], p0[1] + 20, p1[0], p1[1] + 20, 40)

# ------------------------------------------------------------- lane --------
for y in range(GROUND, H):
    t = (y - GROUND) / (H - GROUND)
    for x in range(W):
        a, b = hexc("#3a3350"), hexc("#2f2a48")
        px[x, y] = b if dith(x, y, t * 0.9) else a
# old asphalt: sparse speckles, a few patched seams and cracks
LR = random.Random(7)
for _ in range(2600):
    x, y = LR.randint(0, W - 1), LR.randint(GROUND + 4, H - 1)
    px[x, y] = mix(px[x, y], hexc("#4d4670") if LR.random() < 0.6 else hexc("#221e38"), 0.5)
for (x0, y0, x1, y1) in ((0, 392, 640, 396), (0, 446, 640, 452)):  # patched seams
    d.line([x0, y0, x1, y1], fill=hexc("#2a2540"))
for (cx, cy) in ((96, 380), (228, 430), (470, 372), (560, 440)):
    x, y = cx, cy
    for i in range(14):
        px[x, y] = hexc("#252039")
        x += LR.choice((1, 1, 2))
        y += LR.choice((-1, 0, 0, 1))
# manhole cover (plain ring pattern)
MX, MY = 400, 432
d.ellipse([MX - 22, MY - 8, MX + 22, MY + 8], fill=hexc("#2e2944"), outline=hexc("#1e1a32"))
d.ellipse([MX - 16, MY - 5, MX + 16, MY + 5], outline=hexc("#433c60"))
d.ellipse([MX - 8, MY - 2, MX + 8, MY + 2], outline=hexc("#433c60"))
d.line([MX - 18, MY - 6, MX - 6, MY - 8], fill=hexc("#4d4670"))
# gutter along the building fronts
d.rectangle([0, GROUND, W, GROUND + 3], fill=hexc("#2a2540"))
d.line([0, GROUND, W, GROUND], fill=hexc("#4d4670"))
# warm light spilling onto the lane from each opening
for (o0, o1) in OPENINGS:
    glow(img, (o0 + o1) / 2, GROUND + 22, (o1 - o0) * 0.75 + 10, 34, 0.42, GLOW)
    glow(img, (o0 + o1) / 2, GROUND + 10, (o1 - o0) * 0.45, 12, 0.3, CREAM)
# the damp lane mirrors the big lanterns as soft red smudges
for (lx, ly, big) in LANTERN_POS:
    if big:
        glow(img, lx, GROUND + 16, 5, 13, 0.32, RED[1])
# ----------------------------------------------------------- props ---------


def crate(x, y, col):
    """Stackable plastic crate, seen from the front (top-left at x, y)."""
    out = mix(col, OUTLINE, 0.6)
    d.rectangle([x, y, x + 17, y + 11], fill=col, outline=out)
    d.line([x + 1, y + 1, x + 16, y + 1], fill=mix(col, hexc("#ffe3a8"), 0.3))
    for hx in (x + 3, x + 8, x + 13):
        d.rectangle([hx, y + 4, hx + 1, y + 8], fill=out)


def pot(x, y, big=False):
    ramp = [hexc("#b8704a"), hexc("#8a5038"), hexc("#6a3a2e")]
    pw = 12 if big else 9
    S = Sprite(pw + 10, 30)
    S.blob(rect(5, 20, pw, 9), ramp, hexc("#3e2020"), cuts=(-0.2, 0.5))
    leaves = set()
    for i in range(7 if big else 5):
        ang = -math.pi / 2 + (i - (3 if big else 2)) * 0.45
        ln = 13 if big else 9
        for s in range(ln):
            lx = int(5 + pw / 2 + math.cos(ang) * s + (1 if s > ln / 2 else 0) * (i % 2))
            ly = int(20 + math.sin(ang) * s)
            leaves |= {(lx, ly), (lx + 1, ly)}
    S.fill(leaves, hexc("#2b4f47"))
    S.fill({p for p in leaves if (p[0] + p[1]) % 3 == 0}, hexc("#3f6b55"))
    S.fill({p for p in leaves if p[1] < 12 and p[0] < 5 + pw / 2}, hexc("#5b8a62"))
    S.outline_around(leaves, hexc("#1f3a3a"))
    paste(img, S, x, y - 30)


# crates stacked in the gaps and at the edges
crate(84, GROUND - 12, hexc("#4a6a8a"))
crate(84, GROUND - 24, hexc("#a8843e"))
crate(452, GROUND - 12, hexc("#8a4a4a"))
crate(622, GROUND - 12, hexc("#4a6a8a"))
crate(256, GROUND - 12, hexc("#6a5a8a"))
d.rectangle([438, GROUND - 22, 450, GROUND - 1], fill=hexc("#5a4a3e"), outline=OUTLINE)  # a small barrel
d.line([438, GROUND - 16, 450, GROUND - 16], fill=hexc("#3a2e2a"))
d.line([438, GROUND - 7, 450, GROUND - 7], fill=hexc("#3a2e2a"))
d.line([440, GROUND - 21, 440, GROUND - 2], fill=hexc("#7a6454"))
pot(-2, GROUND + 1, big=True)
pot(158, GROUND + 1)
pot(372, GROUND + 1, big=True)
pot(546, GROUND + 1)

# the grill at the bar with the white noren: charcoal box, smoke curling up
GX, GY = OPENINGS[2][1] + 4, GROUND - 18
glow(img, GX + 8, GY + 2, 18, 12, 0.55, hexc("#ff7a3a"))
d.rectangle([GX, GY, GX + 16, GY + 7], fill=hexc("#4a4058"), outline=OUTLINE)
for i in range(0, 15, 2):
    px[GX + 1 + i, GY + 1] = hexc("#ff8a4a") if i % 4 else hexc("#ffd08a")
d.line([GX + 2, GY + 8, GX + 2, GROUND - 1], fill=OUTLINE)
d.line([GX + 14, GY + 8, GX + 14, GROUND - 1], fill=OUTLINE)
for i in range(3):  # skewers
    d.line([GX + 2 + i * 5, GY - 1, GX + 5 + i * 5, GY - 1], fill=hexc("#c8864a"))


def smoke_curl(x, y, n):
    """Soft translucent puffs drifting up in a lazy S-curve."""
    for i in range(n):
        r = 3 + i * 1.1
        cx = x + 9 * math.sin(i * 0.55) + i * 0.8
        cy = y - 6 - i * 7
        S = Sprite(int(2 * r + 4), int(2 * r + 4))
        m = ellipse(r + 1.5, r + 1.5, r, r * 0.8)
        col = mix(hexc("#d8c8d8"), hexc("#8a7aa0"), i / n)
        S.blob(m, [mix(col, hexc("#ffe3a8"), 0.25 * (1 - i / n)), col], None, lx=0.5, ly=0.7, cuts=(0.3,))
        im = S.image()
        a = int(95 - i * (80 / n))
        im.putalpha(im.getchannel("A").point(lambda v: min(v, a)))
        img.alpha_composite(im, (int(cx - r), int(cy - r)))


smoke_curl(GX + 8, GY, 16)
smoke_curl(OPENINGS[5][0] + 30, EAVE + 8, 7)   # a thinner wisp from a vent on the right

# ------------------------------------------------- lanterns on top ---------
for (lx, ly, big) in LANTERN_POS:
    if big:
        glow(img, lx, ly + 12, 20, 22, 0.45, GLOW)
    else:
        glow(img, lx, ly + 5, 8, 9, 0.35, GLOW)
for (lx, ly, big) in LANTERN_POS:
    S = BIG_LANTERN if big else SMALL_LANTERN
    d.line([lx, ly - 3, lx, ly], fill=OUTLINE)
    paste(img, S, lx - S.w // 2, ly)

# ------------------------------------------ stars still in open sky --------
sky_now = img.load()
ref = sky_stars.load()


def open_sky(x, y):
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            xx, yy = x + dx, y + dy
            if 0 <= xx < W and 0 <= yy < H and sky_now[xx, yy] != ref[xx, yy]:
                return False
    return True


keep = []
for (x, y, b) in sorted(STARS, key=lambda s: -s[2]):
    if b > 0.55 and y >= 34 and open_sky(x, y):
        if all(abs(x - kx) + abs(y - ky) > 10 for (kx, ky) in keep):
            keep.append((x, y))
    if len(keep) >= 36:
        break
keep.sort()
with open(os.path.join(ASSETS, "bg", "emberglow_alley_stars.json"), "w") as f:
    json.dump([[x, y] for (x, y) in keep], f)
print(f"stars exported: {len(keep)}")

# soften everything a touch (not the sky, so the baked stars stay crisp)
haze(img, hexc("#3d2a52"), 0.08, (0, 100, W, H))

img = save_bg(img, "emberglow_alley")
mock(img, "emberglow_alley", "emberglow_alley")
