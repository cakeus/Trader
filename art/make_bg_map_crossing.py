"""640x480 night map of Lantern Crossing (top-down city, 3/4 buildings).

Landmarks sit just above the map pins (pin tip = locations.json mapPos):
  Midnight Station (150,170): a platform on the elevated line, a train waiting.
  Emberglow Alley (300,350): a narrow lane of tiny bars strung with red lanterns.
  Stargazer's Lookout (480,190): a tall building with a rooftop garden and a small observatory.
A band of night sky (skyline, moon, dim stars) runs along the top; the star
positions go to map_crossing_stars.json for the game's twinkle. A scramble
crossing sits on the main avenues, and a canal cuts across the bottom right.
Firefly box for areas.json: FIREFLIES below (the rooftop garden's greenery).
"""
import json
import math
import os
import random

from PIL import ImageDraw

from bgkit import W, H, new_bg, vgrad, dith, paste, seg_dist, save_bg, mock
from pixelkit import Sprite, hexc, mix, ellipse, rect, edge, ASSETS, PREVIEWS

R = random.Random(21)
img, d = new_bg("#1f1b38")
px = img.load()

# ----------------------------------------------------------------- palette ---
SKY = [hexc("#141129"), hexc("#1b1733"), hexc("#252045"), hexc("#2f2a58"), hexc("#3d2a52"), hexc("#553a6a")]
OUT = hexc("#17142b")
ROAD = hexc("#211d3a")
ROAD_LINE = hexc("#3a3560")
WALK = hexc("#2d2848")
WALK_HI = hexc("#39335a")
ROOFS = [hexc("#39345a"), hexc("#443e66"), hexc("#3d3760"), hexc("#34304f"), hexc("#4a3d68"), hexc("#44305a"),
         hexc("#323a5c"), hexc("#4d4670")]
WIN = [hexc("#ffd98a"), hexc("#f7b861"), hexc("#b8834a")]
WIN_DARK = hexc("#1f1b36")
RED, RED_HI, RED_SH, RED_OUT = hexc("#e0503f"), hexc("#f27a5c"), hexc("#a8332f"), hexc("#5e1c24")
ORANGE, ORANGE_HI = hexc("#f59a3f"), hexc("#ffc06b")
CREAM, CREAM_SH = hexc("#ffe8b0"), hexc("#f4cf86")
GLOW, GLOW_CREAM = hexc("#ff8a4a"), hexc("#ffc070")
LEAF = [hexc("#5b8a62"), hexc("#3f6b55"), hexc("#2b4f47"), hexc("#1f3a3a")]
LEAF_OUT = hexc("#12242a")
MOON = [hexc("#fff4d6"), hexc("#f1dca6"), hexc("#cdb57e")]
STAR = [hexc("#8f88b8"), hexc("#b9b3dc"), hexc("#fff4d6")]
WATER = [hexc("#1e2a4a"), hexc("#1a2342"), hexc("#161d38")]

GROUND_Y = 74  # where the city map starts under the skyline


def glow(cx, cy, r, color, amt):
    """Soft light pool in a few stepped rings (dithered only where rings meet)."""
    for y in range(int(cy - r), int(cy + r) + 1):
        for x in range(int(cx - r), int(cx + r) + 1):
            if not (0 <= x < W and GROUND_Y - 30 <= y < H):
                continue
            dd = math.hypot(x - cx, y - cy) / r
            if dd >= 1:
                continue
            t = (1 - dd) ** 1.2 * 3
            i = int(t)
            lvl = i + (1 if dith(x, y, t - i) else 0)
            if lvl:
                px[x, y] = mix(px[x, y], color, amt * lvl / 3)


def darken(box, amt, color=hexc("#141129")):
    x0, y0, x1, y1 = box
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            if dith(x, y, 0.5) or amt > 0.2:
                px[x, y] = mix(px[x, y], color, amt)


# ------------------------------------------------------------------- sky ---
vgrad(img, 0, 0, W, GROUND_Y + 4, SKY)
MCX, MCY, MR = 594, 44, 10
for y in range(MCY - 26, MCY + 27):  # moon halo
    for x in range(MCX - 26, MCX + 27):
        dd = math.hypot(x - MCX, y - MCY)
        if MR < dd < 26 and dith(x, y, 0.55 * (1 - (dd - MR) / 16)):
            px[x, y] = mix(px[x, y], hexc("#6a5a8a"), 0.5)
moon = Sprite(2 * MR + 3, 2 * MR + 3)
mm = ellipse(MR + 1, MR + 1, MR, MR)
moon.blob(mm, MOON, hexc("#b39a6a"), lx=0.8, ly=0.6, cuts=(0.15, 0.7))
for (cx_, cy_, rr) in ((MR + 4, MR - 2, 2.2), (MR - 3, MR + 4, 1.6), (MR + 5, MR + 5, 1.2)):
    for (x, y) in ellipse(cx_, cy_, rr, rr):
        if (x, y) in mm and (x, y) not in edge(mm):
            moon.set(x, y, MOON[2] if moon.get(x, y) != MOON[0] else MOON[1])
moon.set(MR - 4, MR - 5, hexc("#ffffff"))
paste(img, moon, MCX - MR - 1, MCY - MR - 1)

# far skyline (hazy) and near skyline (darker, a few lit windows)
FAR, NEAR = hexc("#342b56"), hexc("#221d3e")
sky_top = [GROUND_Y] * W  # highest non-sky pixel per column, for the stars
x = 0
while x < W:
    w = R.randint(8, 22)
    top = R.randint(48, 62)
    if R.random() < 0.12:
        top = R.randint(40, 48)
    d.rectangle([x, top, x + w - 1, GROUND_Y + 2], fill=FAR)
    for c in range(x, min(W, x + w)):
        sky_top[c] = min(sky_top[c], top)
    x += w
# a slender broadcast tower far off, and a tiny torii on a far hill (left)
d.line([232, 30, 232, 60], fill=FAR)
d.line([230, 44, 234, 44], fill=FAR)
d.polygon([(226, 62), (232, 38), (238, 62)], fill=FAR)
for c in range(226, 239):
    sky_top[c] = min(sky_top[c], 38 if abs(c - 232) < 3 else 50)
sky_top[232] = 30
px[232, 29] = hexc("#e0503f")
d.ellipse([10, 54, 70, 76], fill=FAR)
for c in range(10, 71):
    sky_top[c] = min(sky_top[c], 54 if 22 < c < 58 else 60)
TORII = hexc("#6a2e3a")
d.line([36, 51, 36, 55], fill=TORII)
d.line([42, 51, 42, 55], fill=TORII)
d.line([34, 50, 44, 50], fill=TORII)
d.line([35, 52, 43, 52], fill=TORII)
for c in range(34, 45):
    sky_top[c] = min(sky_top[c], 50)
x = 0
while x < W:
    w = R.randint(10, 30)
    top = R.randint(56, 68)
    if 560 < x < 620:
        top = max(top, 60)
    d.rectangle([x, top, x + w - 1, GROUND_Y + 2], fill=NEAR)
    d.line([x, top, x + w - 1, top], fill=hexc("#2c2650"))
    for c in range(x, min(W, x + w)):
        sky_top[c] = min(sky_top[c], top)
    for wy in range(top + 3, GROUND_Y, 3):
        for wx in range(x + 2, x + w - 2, 3):
            if R.random() < 0.12:
                px[wx, wy] = WIN[2] if R.random() < 0.6 else WIN[1]
    x += w

# stars: only where the pixel is still open sky, clear of the moon
stars = []
tries = 0
while len(stars) < 64 and tries < 5000:
    tries += 1
    sx = R.randint(2, W - 3)
    # most stars below the HUD strip (y >= 31), a few above
    sy = R.randint(31, 58) if R.random() < 0.72 else R.randint(4, 30)
    if sy > sky_top[sx] - 4 or any(sky_top[c] - 4 < sy for c in range(max(0, sx - 2), min(W, sx + 3))):
        continue
    if math.hypot(sx - MCX, sy - MCY) < MR + 8:
        continue
    if any(abs(sx - a) + abs(sy - b) < 9 for a, b in stars):
        continue
    stars.append((sx, sy))
    r_ = R.random()
    px[sx, sy] = STAR[2] if r_ < 0.12 else STAR[1] if r_ < 0.5 else STAR[0]

# ------------------------------------------------------------ city ground ---
d.rectangle([0, GROUND_Y, W, H], fill=ROAD)
d.line([0, GROUND_Y, W, GROUND_Y], fill=OUT)

VMAIN = (378, 406)   # main avenue (north-south)
HMAIN = (244, 272)   # main avenue (east-west)
BANDS = [  # (y0, y1, vertical minor roads as (x0, x1))
    (GROUND_Y + 2, 104, [(92, 98), (200, 206), (292, 298), (470, 476), (560, 566)]),
    (110, 196, [(70, 76), (222, 228), (300, 306), (530, 536), (598, 604)]),
    (204, HMAIN[0], [(50, 56), (140, 146), (250, 256), (470, 476), (560, 566)]),
    (HMAIN[1], 366, [(56, 62), (150, 156), (222, 228), (470, 476), (566, 572)]),
    (374, 436, [(90, 96), (180, 186), (280, 286), (490, 496), (580, 586)]),
    (444, H + 4, [(50, 56), (150, 156), (250, 256)]),
]

# canal (bottom right)
CANAL = [(404, 490), (446, 456), (516, 424), (588, 404), (650, 396)]
CANAL_HW = 13


def canal_d(x, y):
    return min(seg_dist(x, y, *a, *b) for a, b in zip(CANAL, CANAL[1:]))


# landmark plots: generic buildings stay out of these
STATION = (84, 112, 218, 170)
ALLEY = (230, 282, 374, 352)
LOOKOUT = (432, 94, 530, 192)
ZONES = [STATION, ALLEY, LOOKOUT]


def hits(box, zones):
    x0, y0, x1, y1 = box
    return any(x0 < z[2] and x1 > z[0] and y0 < z[3] and y1 > z[1] for z in zones)


def building(x0, y0, x1, y1, fh, roof, rr):
    """3/4 city block building: flat roof on top, lit south front below it."""
    front = mix(roof, hexc("#141129"), 0.4)
    ry1 = y1 - fh
    d.rectangle([x0, y0, x1, ry1], fill=roof, outline=OUT)
    d.line([x0 + 1, y0 + 1, x1 - 1, y0 + 1], fill=mix(roof, hexc("#8f88b8"), 0.22))
    d.line([x0 + 1, y0 + 1, x0 + 1, ry1 - 1], fill=mix(roof, hexc("#8f88b8"), 0.14))
    d.rectangle([x0, ry1 + 1, x1, y1], fill=front, outline=OUT)
    d.line([x0 + 1, ry1 + 1, x1 - 1, ry1 + 1], fill=mix(front, hexc("#141129"), 0.4))
    # windows
    lit_rate = rr.choice((0.2, 0.35, 0.5))
    for wy in range(ry1 + 3, y1 - 2, 3):
        for wx in range(x0 + 2, x1 - 1, 3):
            r_ = rr.random()
            c = WIN[0] if r_ < lit_rate * 0.5 else WIN[1] if r_ < lit_rate else WIN[2] if r_ < lit_rate + 0.12 else WIN_DARK
            px[wx, wy] = c
    # a lit shop front at street level on some
    if fh >= 7 and rr.random() < 0.45 and x1 - x0 > 9:
        sx0 = x0 + 2 + rr.randint(0, max(0, (x1 - x0) - 9))
        d.rectangle([sx0, y1 - 2, sx0 + 5, y1 - 1], fill=rr.choice((WIN[1], CREAM_SH, WIN[0])))
        shopglow.append((sx0 + 3, y1 + 1))
    # roof clutter
    rw, rh = x1 - x0, ry1 - y0
    if rw > 14 and rh > 12 and rr.random() < 0.1:  # a plain glowing rooftop sign (no lettering)
        sc = rr.choice((hexc("#e07aa0"), hexc("#7ac8d8"), hexc("#f59a3f"), hexc("#b98ae0")))
        sx0, sy0 = x0 + 3 + rr.randint(0, rw - 12), y0 + 3
        signs.append((sx0 + 3, sy0 + 1, sc))
        d.rectangle([sx0, sy0, sx0 + 7, sy0 + 3], fill=mix(sc, hexc("#141129"), 0.25), outline=OUT)
        d.line([sx0 + 1, sy0 + 1, sx0 + 6, sy0 + 1], fill=sc)
        d.line([sx0 + 1, sy0 + 2, sx0 + 6, sy0 + 2], fill=mix(sc, hexc("#ffffff"), 0.35))
    for _ in range(rr.randint(0, 2)):
        if rw < 8 or rh < 7:
            break
        kind = rr.random()
        ax, ay = rr.randint(x0 + 2, x1 - 5), rr.randint(y0 + 2, ry1 - 4)
        if kind < 0.5:  # AC unit
            d.rectangle([ax, ay, ax + 3, ay + 2], fill=mix(roof, hexc("#8f88b8"), 0.3), outline=OUT)
        elif kind < 0.75 and rw > 10 and rh > 9:  # water tank
            d.ellipse([ax, ay, ax + 4, ay + 4], fill=mix(roof, hexc("#b9b3dc"), 0.25), outline=OUT)
            px[ax + 1, ay + 1] = mix(roof, hexc("#d8d2f0"), 0.4)
        else:  # potted plants
            for k in range(rr.randint(1, 3)):
                qx = ax + k * 2
                if qx < x1 - 1:
                    px[qx, ay] = LEAF[1]
                    px[qx, ay + 1] = LEAF[3]


def round_tree(tx, ty, s, seed):
    S = Sprite(s + 3, s + 4)
    m = ellipse(s / 2 + 0.5, s / 2 + 0.5, s / 2, s / 2 - 0.5)
    S.blob(m, LEAF, LEAF_OUT, lx=0.8, ly=0.6, cuts=(-0.35, 0.1, 0.55))
    rr_ = random.Random(seed)
    for _ in range(s // 3):
        qx, qy = rr_.randint(1, s - 1), rr_.randint(1, s // 2)
        if (qx, qy) in m and (qx, qy) not in edge(m):
            S.set(qx, qy, hexc("#7aa878"))
    d.ellipse([tx + 1, ty + s - 2, tx + s + 1, ty + s + 2], fill=hexc("#16242a"))
    paste(img, S, tx, ty)


def park(x0, y0, x1, y1):
    """A little pocket park: dark lawn, a path, round trees and one lamp."""
    x1, y1 = min(x1, W - 1), min(y1, H - 1)
    d.rectangle([x0, y0, x1, y1], fill=hexc("#1e3034"), outline=hexc("#16242a"))
    for y in range(y0 + 1, y1):
        for x in range(x0 + 1, x1):
            if dith(x, y, 0.3):
                px[x, y] = hexc("#213638")
    my = (y0 + y1) // 2
    d.rectangle([x0 + 1, my - 1, x1 - 1, my + 1], fill=hexc("#3a3656"))
    rr = random.Random(x0 * 31 + y0)
    spots = []
    for _ in range(60):
        s = rr.choice((7, 8, 9, 10))
        tx, ty = rr.randint(x0 + 1, x1 - s - 2), rr.randint(y0 + 1, y1 - s - 3)
        if abs(ty + s / 2 - my) < s / 2 + 2 or any(abs(tx - a) < 8 and abs(ty - b) < 7 for a, b in spots):
            continue
        spots.append((tx, ty))
        if len(spots) > (x1 - x0) * (y1 - y0) // 120:
            break
    for (tx, ty) in sorted(spots, key=lambda p: p[1]):
        round_tree(tx, ty, rr.choice((7, 8, 9)), tx * 13 + ty)
    lamps_extra.append(((x0 + x1) // 2, my))


def parking(x0, y0, x1, y1):
    x1, y1 = min(x1, W - 1), min(y1, H - 1)
    d.rectangle([x0, y0, x1, y1], fill=hexc("#2a2644"), outline=OUT)
    rr = random.Random(x0 + y0 * 7)
    for row_y in range(y0 + 3, y1 - 8, 12):
        for x in range(x0 + 3, x1 - 3, 7):
            d.line([x, row_y, x, row_y + 7], fill=hexc("#4a4470"))
            if rr.random() < 0.55 and x + 6 < x1 - 2:
                c = rr.choice((hexc("#6a5a8a"), hexc("#3f6b7a"), hexc("#8a4a5a"), hexc("#b9b3dc"), hexc("#4a4a6a")))
                d.rectangle([x + 2, row_y + 1, x + 5, row_y + 6], fill=c, outline=OUT)
                px[x + 3, row_y + 2] = mix(c, hexc("#ffffff"), 0.3)


SPECIAL = {(204, 146): "park", (374, 186): "park", (GROUND_Y + 2, 298): "parking",
           (374, 96): "parking", (110, 604): "park"}
lamps_extra = []
shopglow = []
signs = []
for (by0, by1, vroads) in BANDS:
    cuts = sorted(vroads + [VMAIN])
    xs = [(-4, cuts[0][0])] + [(a[1], b[0]) for a, b in zip(cuts, cuts[1:])] + [(cuts[-1][1], W + 4)]
    for (bx0, bx1) in xs:
        if bx1 - bx0 < 6:
            continue
        # sidewalk
        d.rectangle([bx0, by0, bx1 - 1, by1 - 1], fill=WALK)
        d.line([bx0, by0, bx1 - 1, by0], fill=WALK_HI)
        special = SPECIAL.get((by0, bx0))
        if special == "park":
            park(bx0 + 2, by0 + 2, bx1 - 3, by1 - 3)
            continue
        if special == "parking":
            parking(bx0 + 2, by0 + 2, bx1 - 3, by1 - 3)
            continue
        # rows of buildings
        ih = by1 - by0 - 4
        nrows = 1 if ih < 40 else 2 if ih < 80 else 3
        rows = []
        yy = by0 + 2
        for k in range(nrows):
            h_ = ih // nrows
            rows.append((yy, yy + h_ - 1))
            yy += h_
        for (ry0, ry1) in rows:
            x = bx0 + 2
            while x < bx1 - 3:
                w = R.randint(12, 30)
                xe = min(bx1 - 3, x + w)
                if bx1 - 3 - xe < 10:
                    xe = bx1 - 3
                box = (x, ry0, xe, ry1)
                cx_, cy_ = (x + xe) / 2, (ry0 + ry1) / 2
                ok = not hits(box, ZONES) and all(
                    canal_d(qx, qy) > CANAL_HW + 6 for qx in (x, xe, cx_) for qy in (ry0, ry1, cy_))
                if ok and xe - x >= 6:
                    fh = R.randint(5, max(5, min(14, (ry1 - ry0) - 6)))
                    building(x, ry0, xe, ry1, fh, R.choice(ROOFS), R)
                x = xe + 1

# pale road markings: lane dashes on the avenues
for x in range(0, W, 10):
    if not (VMAIN[0] - 10 < x < VMAIN[1] + 6):
        d.line([x, 258, x + 4, 258], fill=ROAD_LINE)
for y in range(GROUND_Y + 4, H, 10):
    if not (HMAIN[0] - 10 < y < HMAIN[1] + 6) and canal_d(392, y) > CANAL_HW + 2:
        d.line([392, y, 392, y + 4], fill=ROAD_LINE)

# ---------------------------------------------------------- scramble crossing ---
ZEB = hexc("#6e6898")
X0, X1, Y0, Y1 = VMAIN[0], VMAIN[1], HMAIN[0], HMAIN[1]
for k in range(X0 + 2, X1 - 1, 3):  # north / south zebra bands
    d.line([k, Y0 - 8, k, Y0 - 2], fill=ZEB)
    d.line([k, Y1 + 2, k, Y1 + 8], fill=ZEB)
for k in range(Y0 + 2, Y1 - 1, 3):  # west / east bands
    d.line([X0 - 8, k, X0 - 2, k], fill=ZEB)
    d.line([X1 + 2, k, X1 + 8, k], fill=ZEB)
for t in range(3, 26, 3):  # the diagonal "X" of the scramble
    for (ax, ay, sx, sy) in ((X0 + 1, Y0 + 1, 1, 1), (X1 - 1, Y0 + 1, -1, 1)):
        qx, qy = ax + sx * t, ay + sy * t
        if X0 < qx < X1 and Y0 < qy < Y1:
            px[qx, qy] = ZEB
            if X0 < qx + sx < X1:
                px[qx + sx, qy] = ZEB
# people crossing: tiny warm/cool dots
for _ in range(16):
    qx, qy = R.randint(X0 - 6, X1 + 6), R.randint(Y0 - 6, Y1 + 6)
    if X0 - 8 <= qx <= X1 + 8 and Y0 - 8 <= qy <= Y1 + 8:
        px[qx, qy] = R.choice((hexc("#d8d0ee"), hexc("#e0503f"), hexc("#f4cf86"), hexc("#8ec0d8")))
        px[qx, qy + 1] = OUT

# --------------------------------------------------------------- canal ----
for y in range(300, H):
    for x in range(360, W):
        c = canal_d(x, y)
        if c < CANAL_HW:
            t = min(0.999, c / CANAL_HW) * 2
            i = int(t)
            px[x, y] = WATER[i + 1] if dith(x, y, t - i) else WATER[i]
        elif c < CANAL_HW + 2:
            px[x, y] = hexc("#4d4670") if c < CANAL_HW + 1 else OUT
        elif c < CANAL_HW + 8:
            px[x, y] = WALK if c < CANAL_HW + 7 else WALK_HI
# ripples and lantern reflections
for _ in range(90):
    x, y = R.randint(380, W - 4), R.randint(380, H - 2)
    if canal_d(x, y) < CANAL_HW - 3:
        for k in range(R.randint(2, 4)):
            if canal_d(x + k, y) < CANAL_HW - 2:
                px[x + k, y] = hexc("#2f3f66")
REFLECT = []
for (x, y) in ((470, 444), (530, 420), (600, 402), (440, 466), (570, 410)):
    REFLECT.append((x, y))
    for k in range(0, 9, 2):
        if canal_d(x, y + k) < CANAL_HW - 1:
            px[x, y + k] = ORANGE if k < 4 else hexc("#a8603f")
            if k < 3:
                px[x + 1, y + k] = hexc("#a8603f")
# a small bridge where the band-4/5 street meets the canal
BR_Y0, BR_Y1 = 436, 444
bx_hits = [x for x in range(380, W) if canal_d(x, 440) < CANAL_HW + 2]
if bx_hits:
    bx0, bx1 = bx_hits[0] - 3, bx_hits[-1] + 3
    d.rectangle([bx0, BR_Y0 - 1, bx1, BR_Y1 + 1], fill=hexc("#4d4670"), outline=OUT)
    d.rectangle([bx0 + 1, BR_Y0 + 1, bx1 - 1, BR_Y1 - 1], fill=ROAD)
    d.line([bx0, BR_Y1 + 2, bx1, BR_Y1 + 2], fill=hexc("#16142c"))
    for k in range(bx0 + 1, bx1, 4):
        px[k, BR_Y0 - 2] = hexc("#6e6898")
# willows / trees along the canal bank
for (tx, ty) in ((436, 420), (492, 398), (560, 382), (618, 370), (410, 452)):
    S = Sprite(12, 12)
    S.blob(ellipse(5.5, 5.5, 5, 4.5), LEAF, LEAF_OUT, cuts=(-0.35, 0.1, 0.55))
    d.ellipse([tx - 1, ty + 7, tx + 11, ty + 11], fill=hexc("#16142c"))
    paste(img, S, tx, ty)

# station forecourt: paving, a taxi rank, a tree either side
d.rectangle([STATION[0] - 4, 112, STATION[2] - 2, 193], fill=hexc("#34304f"))
for y in range(112, 194):
    for x in range(STATION[0] - 4, STATION[2] - 1):
        if (x % 8 == 0 or y % 8 == 0) and dith(x, y, 0.5):
            px[x, y] = hexc("#2d2848")
for (tx_, ty_) in ((96, 176), (108, 176), (186, 176)):
    d.rectangle([tx_, ty_, tx_ + 7, ty_ + 4], fill=hexc("#3f6b55") if tx_ != 108 else hexc("#e0a040"), outline=OUT)
    d.line([tx_ + 2, ty_ + 1, tx_ + 5, ty_ + 1], fill=hexc("#a8c8b0") if tx_ != 108 else hexc("#ffe0a0"))
    px[tx_ + 3, ty_ - 1] = CREAM
round_tree(204, 168, 9, 5)
round_tree(86, 162, 8, 6)

# ----------------------------------------------------- elevated train line ---
TRACK = [(-4, 132), (240, 132), (300, 126), (360, 108), (420, 90), (470, 86), (650, 86)]
DECK_HW = 6
# shadow on the ground under the viaduct
for y in range(GROUND_Y + 2, 200):
    for x in range(W):
        dd = min(seg_dist(x, y - 12, *a, *b) for a, b in zip(TRACK, TRACK[1:]))
        if dd < 5 and dith(x, y, 0.7):
            px[x, y] = mix(px[x, y], hexc("#100d22"), 0.45)
# pillars
L_total = 0
for (ax, ay), (bx, by) in zip(TRACK, TRACK[1:]):
    L = math.hypot(bx - ax, by - ay)
    for k in range(int((-L_total) % 34), int(L), 34):
        t = k / L
        qx, qy = int(ax + (bx - ax) * t), int(ay + (by - ay) * t)
        if STATION[0] - 4 < qx < STATION[2] + 4:
            continue
        d.rectangle([qx - 1, qy + DECK_HW, qx + 2, qy + DECK_HW + 9], fill=hexc("#3a3458"), outline=OUT)
        d.line([qx, qy + DECK_HW + 1, qx, qy + DECK_HW + 8], fill=hexc("#4d4670"))
    L_total += L
# deck side (south face) then deck top
d.line(TRACK, fill=OUT, width=2 * DECK_HW + 6, joint="curve")
d.line([(x, y + 3) for x, y in TRACK], fill=hexc("#2a2744"), width=2 * DECK_HW, joint="curve")
d.line(TRACK, fill=hexc("#4a4468"), width=2 * DECK_HW - 1, joint="curve")
for off, col in ((-4, hexc("#8a84ae")), (-2, hexc("#8a84ae")), (2, hexc("#8a84ae")), (4, hexc("#8a84ae"))):
    d.line([(x, y + off) for x, y in TRACK], fill=col, width=1)
# sleepers between the rails (dark ticks)
for (ax, ay), (bx, by) in zip(TRACK, TRACK[1:]):
    L = math.hypot(bx - ax, by - ay)
    for k in range(0, int(L), 3):
        t = k / L
        qx, qy = int(ax + (bx - ax) * t), int(ay + (by - ay) * t)
        if 0 <= qx < W:
            for o in (-3, 3):
                if 0 <= qy + o < H:
                    px[qx, qy + o] = hexc("#3a3458")
# signal lights along the line
for (sx, sy) in ((40, 125), (330, 108), (560, 79)):
    px[sx, sy] = hexc("#8fe0a0")
    glow(sx, sy, 4, hexc("#8fe0a0"), 0.35)

# ---------------------------------------------------- Midnight Station ------
# platform on the south side of the tracks, a canopy, and the station front
PX0, PX1 = 92, 210
d.rectangle([PX0, 139, PX1, 154], fill=hexc("#57517c"), outline=OUT)            # platform top
d.line([PX0 + 1, 140, PX1 - 1, 140], fill=hexc("#c9a24a"))                        # tactile line
for k in range(PX0 + 2, PX1 - 1, 2):
    if k % 4 == 0:
        px[k, 141] = hexc("#8a7040")
d.rectangle([PX0 + 6, 143, PX1 - 6, 150], fill=hexc("#3d3760"), outline=OUT)        # canopy roof
d.line([PX0 + 7, 144, PX1 - 7, 144], fill=hexc("#6a6494"))
for k in range(PX0 + 12, PX1 - 8, 16):  # canopy lamps
    px[k, 151] = CREAM
    px[k + 1, 151] = CREAM_SH
d.rectangle([PX0, 155, PX1, 166], fill=hexc("#2e2a4c"), outline=OUT)             # station front
d.line([PX0 + 1, 155, PX1 - 1, 155], fill=hexc("#1f1b36"))
for wx in range(PX0 + 4, PX1 - 4, 4):
    if abs(wx - 150) > 9:
        px[wx, 158] = WIN[0] if (wx // 4) % 3 else WIN[1]
        px[wx + 1, 158] = WIN[1]
        px[wx, 161] = WIN[2] if (wx // 4) % 2 else WIN[0]
# the entrance: a warm lit opening with a round clock above it
d.rectangle([142, 159, 158, 166], fill=hexc("#f7b861"), outline=OUT)
d.rectangle([144, 161, 156, 166], fill=hexc("#ffd98a"))
d.line([150, 160, 150, 166], fill=hexc("#b8834a"))
d.ellipse([146, 150, 154, 158], fill=CREAM, outline=OUT)
px[150, 152] = OUT
px[150, 153] = OUT
px[151, 154] = OUT
glow(150, 168, 14, GLOW_CREAM, 0.35)
for k in range(PX0 + 12, PX1 - 8, 16):
    glow(k, 152, 6, GLOW_CREAM, 0.25)


def train_car(x0, first=False, last=False):
    x1 = x0 + 33
    body = [x0, 125, x1, 138]
    d.rectangle(body, fill=hexc("#cfc8e6"), outline=OUT)
    d.rectangle([x0 + 1, 126, x1 - 1, 129], fill=hexc("#e6e0f6"))   # roof
    d.line([x0 + 1, 130, x1 - 1, 130], fill=hexc("#9a93c0"))
    d.line([x0 + 1, 137, x1 - 1, 137], fill=hexc("#3f8a6a"))          # line stripe
    for wx in range(x0 + 3, x1 - 3, 5):                                # lit windows
        d.rectangle([wx, 132, wx + 2, 134], fill=WIN[0])
        px[wx, 132] = hexc("#fff4d6")
    for dx_ in (10, 24):
        d.line([x0 + dx_, 131, x0 + dx_, 136], fill=hexc("#8a84ae"))
    if first:
        d.rectangle([x0, 125, x0 + 2, 138], fill=hexc("#3f8a6a"), outline=OUT)
        px[x0 + 1, 134] = CREAM
    if last:
        d.rectangle([x1 - 2, 125, x1, 138], fill=hexc("#3f8a6a"), outline=OUT)
        px[x1 - 1, 134] = RED


for i, cx0 in enumerate(range(100, 200, 35)):
    train_car(cx0, first=i == 0, last=cx0 + 35 >= 200)
glow(98, 134, 10, GLOW_CREAM, 0.3)  # headlight

# ---------------------------------------------------- Emberglow Alley -------
AX0, AX1 = 234, 370
LANE_Y0, LANE_Y1 = 326, 340
d.rectangle([AX0 - 4, 282, AX1 + 4, 352], fill=hexc("#2a2340"))
d.rectangle([AX0 - 2, LANE_Y0, AX1 + 2, LANE_Y1], fill=hexc("#4a3448"))   # warm paved lane
for _ in range(120):
    qx, qy = R.randint(AX0, AX1), R.randint(LANE_Y0 + 1, LANE_Y1 - 1)
    px[qx, qy] = R.choice((hexc("#553a50"), hexc("#3f2c40"), hexc("#5e4052")))
BAR_ROOFS = [hexc("#3d2a52"), hexc("#4a3050"), hexc("#35294a"), hexc("#553a6a"), hexc("#43304e")]
BAR_FRONT = [hexc("#4a2e2a"), hexc("#3e2a30"), hexc("#533426")]
NOREN = [hexc("#2f3f66"), hexc("#6a2e3a"), hexc("#ffe8b0"), hexc("#3f6b55")]
lanterns_alley = []
x = AX0
while x < AX1 - 6:
    w = R.randint(12, 17)
    xe = min(AX1, x + w)
    roof = R.choice(BAR_ROOFS)
    # north row: roof then front facing the lane
    d.rectangle([x, 290, xe, 314], fill=roof, outline=OUT)
    for k in range(x + 1, xe, 2):  # corrugated roof ribs
        d.line([k, 291, k, 313], fill=mix(roof, hexc("#141129"), 0.25))
    d.line([x + 1, 291, xe - 1, 291], fill=mix(roof, hexc("#b9b3dc"), 0.25))
    d.rectangle([x, 315, xe, 326], fill=R.choice(BAR_FRONT), outline=OUT)
    d.line([x + 1, 316, xe - 1, 316], fill=hexc("#2a1a20"))       # eave shadow
    dx0 = x + 3
    d.rectangle([dx0, 319, dx0 + 5, 326], fill=hexc("#f7b861"), outline=OUT)  # lit doorway
    nc = R.choice(NOREN)
    for k in range(dx0 + 1, dx0 + 5):   # short split curtain
        px[k, 320] = nc
        if k != dx0 + 2:
            px[k, 321] = nc
    if xe - x > 13:
        px[xe - 3, 320] = WIN[0]
        px[xe - 4, 320] = WIN[1]
    lanterns_alley.append((xe - 2 if xe - x > 13 else dx0 + 7, 318))
    # south row: low roofs (backs of the next lane's bars)
    d.rectangle([x, 341, xe, 350], fill=mix(roof, hexc("#141129"), 0.15), outline=OUT)
    d.line([x + 1, 342, xe - 1, 342], fill=mix(roof, hexc("#b9b3dc"), 0.18))
    x = xe + 1
# grill smoke wisps rising from a couple of roofs
for (sx, sy) in ((262, 288), (318, 288), (352, 289)):
    for k in range(7):
        qx = sx + int(1.5 * math.sin(k * 0.9))
        if dith(qx, sy - k, 0.6):
            px[qx, sy - k] = mix(px[qx, sy - k], hexc("#8f88b8"), 0.45)


def lantern(x, y, kind="red"):
    """2x4 chochin: dark rings top and bottom, lit ribbed body."""
    if kind == "red":
        body, hi, sh, ring_ = RED, RED_HI, RED_SH, RED_OUT
    elif kind == "orange":
        body, hi, sh, ring_ = ORANGE, ORANGE_HI, hexc("#c0702f"), hexc("#5e2c1c")
    else:
        body, hi, sh, ring_ = CREAM_SH, CREAM, hexc("#d8a860"), hexc("#5e3c24")
    px[x, y] = ring_
    px[x + 1, y] = ring_
    px[x, y + 1] = hi
    px[x + 1, y + 1] = body
    px[x, y + 2] = body
    px[x + 1, y + 2] = sh
    px[x, y + 3] = ring_
    px[x + 1, y + 3] = ring_


def lantern_string(p0, p1, sag, step, kinds=("red",), halo=0.18, wire=hexc("#4a3a50")):
    (ax, ay), (bx, by) = p0, p1
    L = max(1, int(math.hypot(bx - ax, by - ay)))
    pts = []
    for k in range(L + 1):
        t = k / L
        x = ax + (bx - ax) * t
        y = ay + (by - ay) * t + sag * 4 * t * (1 - t)
        pts.append((int(round(x)), int(round(y))))
    for (x, y) in pts:
        if 0 <= x < W and 0 <= y < H:
            px[x, y] = wire
    spots = pts[step // 2::step]
    for i, (x, y) in enumerate(spots):
        k = kinds[i % len(kinds)]
        glow(x + 1, y + 2, 5, GLOW if k != "cream" else GLOW_CREAM, halo)
    for i, (x, y) in enumerate(spots):
        if 0 <= x < W - 1 and 0 <= y < H - 4:
            lantern(x, y + 1, kinds[i % len(kinds)])


# lane glow, door lanterns and strings across the lane
for x in range(AX0, AX1, 12):
    glow(x + 6, LANE_Y0 + 6, 13, GLOW, 0.3)
for (lx, ly) in lanterns_alley:
    glow(lx + 1, ly + 3, 7, GLOW, 0.3)
for (lx, ly) in lanterns_alley:
    px[lx, ly - 1] = RED_OUT
    d.rectangle([lx - 1, ly, lx + 1, ly + 4], fill=RED)
    d.line([lx - 1, ly, lx + 1, ly], fill=RED_OUT)
    d.line([lx - 1, ly + 4, lx + 1, ly + 4], fill=RED_OUT)
    px[lx - 1, ly + 1] = RED_HI
    px[lx + 1, ly + 3] = RED_SH
    px[lx, ly + 2] = RED_SH
lantern_string((AX0 - 2, 312), (AX1 + 2, 312), 3, 10, ("red", "red", "cream"), halo=0.15)
lantern_string((AX0 - 2, 339), (AX1 + 2, 339), 4, 11, ("red", "cream"), halo=0.12)

# ---------------------------------------------------- Stargazer's Lookout ---
LX0, LX1 = 440, 520
ROOF_Y0, ROOF_Y1, BASE_Y = 100, 144, 186
# the tower casts a long shadow to the east
for y in range(ROOF_Y0 + 8, BASE_Y + 2):
    for x in range(LX1 + 1, LX1 + 16):
        if dith(x, y, 0.8):
            px[x, y] = mix(px[x, y], hexc("#100d22"), 0.4)
d.rectangle([LX0 - 4, BASE_Y - 4, LX1 + 4, BASE_Y + 6], fill=WALK, outline=None)
# facade: tall, lots of windows
d.rectangle([LX0, ROOF_Y1, LX1, BASE_Y], fill=hexc("#2b2a4c"), outline=OUT)
d.line([LX0 + 1, ROOF_Y1 + 1, LX1 - 1, ROOF_Y1 + 1], fill=hexc("#1b1733"))
for wy in range(ROOF_Y1 + 4, BASE_Y - 6, 4):
    for wx in range(LX0 + 3, LX1 - 3, 4):
        r_ = R.random()
        c = WIN[0] if r_ < 0.3 else WIN[1] if r_ < 0.5 else WIN[2] if r_ < 0.62 else WIN_DARK
        d.rectangle([wx, wy, wx + 1, wy + 1], fill=c)
        if c == WIN[0]:
            px[wx, wy] = hexc("#fff4d6")
for k in range(LX0 + 1, LX1, 10):  # pilasters
    d.line([k, ROOF_Y1 + 2, k, BASE_Y - 1], fill=hexc("#36345a"))
# lobby entrance
d.rectangle([472, BASE_Y - 7, 488, BASE_Y], fill=hexc("#ffd98a"), outline=OUT)
d.line([480, BASE_Y - 6, 480, BASE_Y], fill=hexc("#b8834a"))
d.line([470, BASE_Y - 8, 490, BASE_Y - 8], fill=hexc("#3f6b55"))
glow(480, BASE_Y + 2, 12, GLOW_CREAM, 0.3)
# roof: parapet then the garden
d.rectangle([LX0, ROOF_Y0, LX1, ROOF_Y1], fill=hexc("#58507a"), outline=OUT)
d.rectangle([LX0 + 2, ROOF_Y0 + 2, LX1 - 2, ROOF_Y1 - 2], fill=hexc("#3a3e4a"), outline=hexc("#28283a"))
d.line([LX0 + 1, ROOF_Y0 + 1, LX1 - 1, ROOF_Y0 + 1], fill=hexc("#7a72a0"))
# lawn with a stepping-stone path
GRASS = [hexc("#2b4f47"), hexc("#26463f"), hexc("#1f3a3a")]
for y in range(ROOF_Y0 + 3, ROOF_Y1 - 2):
    for x in range(LX0 + 3, LX1 - 2):
        t = (x - LX0) / 80 * 0.9 + (y - ROOF_Y0) / 44 * 0.9
        t = min(1.999, t)
        i = int(t)
        px[x, y] = GRASS[i + 1] if dith(x, y, t - i) else GRASS[i]
for (qx, qy) in ((452, 136), (458, 132), (465, 129), (472, 127), (480, 126), (488, 128)):
    d.rectangle([qx, qy, qx + 3, qy + 1], fill=hexc("#8a84a0"), outline=None)
    px[qx, qy] = hexc("#b0aac4")
    px[qx + 3, qy + 1] = hexc("#5a5470")
# grass tufts
for _ in range(60):
    qx, qy = R.randint(LX0 + 4, LX1 - 4), R.randint(ROOF_Y0 + 4, ROOF_Y1 - 4)
    if px[qx, qy] in GRASS:
        px[qx, qy] = LEAF[1] if R.random() < 0.6 else LEAF[0]
# the observatory: a little dome with its slit open, on the east side
OBS = Sprite(24, 22)
OBS.blob(rect(2, 11, 20, 9), [hexc("#b9b3dc"), hexc("#9a93c0"), hexc("#7a72a0")], hexc("#2f2a50"), cuts=(-0.2, 0.5))
dome = {(x, y) for (x, y) in ellipse(11.5, 11.5, 10, 10) if y <= 11}
OBS.blob(dome, [hexc("#e6e0f6"), hexc("#cfc8e6"), hexc("#a8a0cc"), hexc("#8a82b4")], hexc("#2f2a50"),
         lx=0.8, ly=0.5, cuts=(-0.2, 0.25, 0.6))
for y in range(2, 12):
    OBS.set(12, y, hexc("#1b1733"))
    OBS.set(13, y, hexc("#1b1733"))
for (x, y) in ((14, 3), (15, 2), (16, 1)):  # telescope tip peeking out
    OBS.set(x, y, hexc("#d8a860"))
OBS.set(6, 5, hexc("#ffffff"))
OBS.fill(rect(9, 15, 5, 5), hexc("#2f2a50"))
OBS.fill(rect(10, 16, 3, 4), WIN[0])
d.ellipse([494, 120, 520, 128], fill=hexc("#1a2c2e"))
paste(img, OBS, 496, 104)
# trees and shrubs (the greenery the fireflies gather around)
TREES = [(444, 104, 13), (456, 106, 10), (445, 118, 9), (484, 102, 11), (468, 102, 9), (446, 130, 8),
         (500, 131, 9), (466, 134, 8), (510, 134, 7)]
for (tx, ty, s) in sorted(TREES, key=lambda t: t[1]):
    S = Sprite(s + 3, s + 4)
    m = ellipse(s / 2 + 0.5, s / 2 + 0.5, s / 2, s / 2 - 0.5)
    S.blob(m, LEAF, LEAF_OUT, lx=0.8, ly=0.6, cuts=(-0.35, 0.1, 0.55))
    rr_ = random.Random(tx * 7 + ty)
    for _ in range(s // 3):
        qx, qy = rr_.randint(1, s - 1), rr_.randint(1, s // 2)
        if (qx, qy) in m and (qx, qy) not in edge(m):
            S.set(qx, qy, hexc("#7aa878"))
    d.ellipse([tx + 1, ty + s - 2, tx + s + 1, ty + s + 2], fill=hexc("#1a2c2e"))
    paste(img, S, tx, ty)
# a bench and a string of cream lanterns along the south railing
d.rectangle([476, 136, 486, 138], fill=hexc("#8a5a38"), outline=hexc("#3a2418"))
d.line([477, 136, 485, 136], fill=hexc("#b07a4a"))
for x in range(LX0 + 1, LX1):  # railing
    px[x, ROOF_Y1 - 1] = hexc("#8a84ae") if x % 3 else hexc("#58507a")
lantern_string((LX0 + 2, ROOF_Y1 - 3), (LX1 - 2, ROOF_Y1 - 3), 3, 9, ("cream", "orange"), halo=0.14,
               wire=hexc("#6a5a70"))
FIREFLIES = (440, 98, 80, 46)   # x, y, w, h of the rooftop garden

# ------------------------------------------------- lanterns along the city ---
# strings of red and cream lanterns along the avenues' sidewalks (not across the crossing)
for yline in (HMAIN[0] + 1, HMAIN[1] - 5):
    x = 0
    while x < W:
        x2 = x + 36
        if not (x2 > VMAIN[0] - 10 and x < VMAIN[1] + 10):
            lantern_string((x, yline), (x2, yline), 3, 8, ("red", "cream"), halo=0.14)
        x = x2
for xline in (VMAIN[0] + 1, VMAIN[1] - 3):
    y = 300
    while y < 420:
        lantern_string((xline, y), (xline, y + 30), 0, 10, ("red", "orange"), halo=0.14)
        y += 34
# along a few side streets, and the canal promenade
lantern_string((150, 368), (228, 370), 4, 9, ("orange", "red"), halo=0.14)
lantern_string((60, 200), (136, 200), 4, 10, ("cream", "red"), halo=0.12)
lantern_string((236, 200), (300, 200), 3, 10, ("red", "red", "cream"), halo=0.12)
lantern_string((560, 200), (636, 200), 3, 10, ("cream", "red"), halo=0.12)
lantern_string((100, 438), (176, 440), 3, 10, ("red", "cream"), halo=0.12)
lantern_string((428, 404), (500, 380), 4, 9, ("cream", "orange", "red"), halo=0.14)
lantern_string((520, 376), (606, 360), 4, 9, ("cream", "orange", "red"), halo=0.14)
lantern_string((0, 106), (90, 106), 3, 10, ("red", "cream"), halo=0.12)

# street lamps: cream dots with a soft pool
LAMPS = [(60, 240), (140, 240), (250, 240), (330, 276), (440, 276), (540, 240), (620, 276), (70, 106),
         (214, 106), (330, 106), (540, 106), (74, 372), (190, 440), (290, 372), (410, 190), (410, 150),
         (374, 60 + 170), (374, 330), (410, 400), (60, 200), (256, 440), (620, 200)]
for (lx, ly) in LAMPS + lamps_extra:
    if hits((lx - 1, ly - 1, lx + 1, ly + 1), ZONES):
        continue
    glow(lx, ly, 9, GLOW_CREAM, 0.28)
    px[lx, ly] = CREAM
    px[lx, ly + 1] = hexc("#5a5070")
for (sx, sy, sc) in signs:
    glow(sx, sy, 8, sc, 0.18)
# the shop fronts spill a little warm light onto the sidewalk
for (sx, sy) in shopglow:
    glow(sx, sy, 5, GLOW, 0.16)

# cars on the avenues: two lights and a body
for (cx_, cy_, dirx) in ((40, 252, 1), (180, 264, -1), (300, 252, 1), (470, 264, -1), (600, 252, 1)):
    d.rectangle([cx_, cy_ - 2, cx_ + 7, cy_ + 2], fill=R.choice((hexc("#6a5a8a"), hexc("#3f6b7a"), hexc("#8a4a5a"))),
                outline=OUT)
    d.line([cx_ + 2, cy_ - 1, cx_ + 5, cy_ - 1], fill=hexc("#a8a0cc"))
    hx = cx_ + 8 if dirx > 0 else cx_ - 1
    tx = cx_ - 1 if dirx > 0 else cx_ + 8
    px[hx, cy_ - 1] = CREAM
    px[hx, cy_ + 1] = CREAM
    px[tx, cy_ - 1] = RED
    px[tx, cy_ + 1] = RED
    glow(hx + 3 * dirx, cy_, 6, GLOW_CREAM, 0.2)
for (cx_, cy_, diry) in ((386, 180, 1), (398, 330, -1), (386, 420, 1)):
    d.rectangle([cx_ - 2, cy_, cx_ + 2, cy_ + 7], fill=R.choice((hexc("#6a5a8a"), hexc("#3f6b7a"))), outline=OUT)
    hy = cy_ + 8 if diry > 0 else cy_ - 1
    ty = cy_ - 1 if diry > 0 else cy_ + 8
    px[cx_ - 1, hy] = CREAM
    px[cx_ + 1, hy] = CREAM
    px[cx_ - 1, ty] = RED
    px[cx_ + 1, ty] = RED
    glow(cx_, hy + 3 * diry, 6, GLOW_CREAM, 0.2)

# ------------------------------------------------------------------ save ---
img = save_bg(img, "map_crossing")
with open(os.path.join(ASSETS, "bg", "map_crossing_stars.json"), "w") as f:
    json.dump([[x, y] for x, y in sorted(stars)], f, separators=(",", ":"))
print(f"stars: {len(stars)}; fireflies: {FIREFLIES}")

m = img.copy()
md = ImageDraw.Draw(m)
for (x, y, name) in ((150, 170, "Midnight Station"), (300, 350, "Emberglow Alley"), (480, 190, "Stargazer's Lookout")):
    md.ellipse([x - 5, y - 16, x + 5, y - 6], fill=hexc("#e8534e"), outline=hexc("#5a1a2a"))
    md.rectangle([x - 45, y + 4, x + 45, y + 26], fill=hexc("#fbf1dc"), outline=hexc("#5a3a3e"))
m.save(os.path.join(PREVIEWS, "_mock_map_crossing_pins.png"))
mock(img, "map_crossing")
