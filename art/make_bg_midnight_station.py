"""640x480 Midnight Station: a late-night elevated train platform, seen from our
platform edge across empty tracks to the far platform. The far platform has a
canopy strung with red and cream paper lanterns, pendant lamps, a clock and a
plain hanging sign, two glowing vending machines and a bench. Behind it the
city skyline with lit windows, a distant train on another viaduct, and a night
sky with a moon and dim stars (open on the right, past the canopy).

Soft and dim so the cream actor cards (slots in locations.json) pop. No text
on any sign. Also writes the baked star positions to
assets/bg/midnight_station_stars.json for the game's twinkle overlay.
"""
import json
import math
import os
import random

from bgkit import W, H, new_bg, vgrad, dith, haze, paste, save_bg, mock
from pixelkit import ASSETS, Sprite, hexc, mix, ellipse, rect, rounded_rect, edge
from snowkit import glow

R = random.Random(2107)
img, d = new_bg()
px = img.load()

NAME = "midnight_station"
SLOTS = [(70, 166), (270, 212), (466, 160)]
DEALER = (516, 304)
CARD_W, CARD_H = 108, 104

# shared night palette
SKY = [hexc("#141129"), hexc("#1b1733"), hexc("#252045"), hexc("#2f2a58"), hexc("#3d2a52"), hexc("#553a6a")]
BLD = [hexc("#2a2744"), hexc("#34304f"), hexc("#403a5e"), hexc("#4d4670")]
BLD_OUT = hexc("#17142b")
WIN = [hexc("#ffd98a"), hexc("#f7b861"), hexc("#b8834a")]
RED = [hexc("#f27a5c"), hexc("#e0503f"), hexc("#a8332f")]
RED_OUT = hexc("#5e1c24")
CREAM = [hexc("#fff4d0"), hexc("#ffe8b0"), hexc("#f4cf86"), hexc("#d4a860")]
CREAM_OUT = hexc("#7a4e2e")
GLOW = hexc("#ff9a4a")
GLOW_CREAM = hexc("#ffe3a8")
MOON = [hexc("#fff4d6"), hexc("#f1dca6"), hexc("#cdb57e")]

HORIZON = 330      # city base (hidden behind the far platform)
FAR_FLOOR = 336    # far platform's top face
TRACK_TOP = 356
NEAR_EDGE = 400    # our platform's edge

# ------------------------------------------------------------------- sky ---
vgrad(img, 0, 0, W, HORIZON, SKY)
# city glow rising from below
for y in range(200, HORIZON):
    t = (y - 200) / (HORIZON - 200)
    for x in range(W):
        if dith(x, y, t * 0.45):
            px[x, y] = mix(px[x, y], hexc("#7a4a6a"), 0.35)
sky_ref = img.copy()

# moon, lit from the upper-left, with a soft halo
MX, MY, MR = 560, 82, 17
for y in range(MY - 60, MY + 60):
    for x in range(MX - 60, MX + 60):
        r = math.hypot(x - MX, y - MY)
        if r <= MR:
            v = ((x - MX) * 0.7 + (y - MY) * 0.6) / MR
            c = MOON[0] if v < -0.2 else MOON[1] if v < 0.45 else MOON[2]
            if r > MR - 1:
                c = MOON[2] if v > -0.3 else MOON[1]
            px[x, y] = c
        elif r < 58 and dith(x, y, 0.35 * (1 - (r - MR) / (58 - MR)) ** 1.5):
            px[x, y] = mix(px[x, y], hexc("#6a5a8a"), 0.6)
for (cx, cy, cr) in ((565, 88, 3), (553, 77, 2), (568, 75, 1.5), (558, 93, 1.5)):  # soft craters
    for y in range(int(cy - cr), int(cy + cr) + 1):
        for x in range(int(cx - cr), int(cx + cr) + 1):
            if math.hypot(x - cx, y - cy) <= cr and px[x, y] != MOON[2]:
                px[x, y] = MOON[2] if px[x, y] == MOON[1] else MOON[1]
px[MX - 8, MY - 9] = hexc("#ffffff")
px[MX - 9, MY - 8] = hexc("#ffffff")

# ------------------------------------------------------------- skyline ---
# far layer: flat silhouettes
x = -6
while x < W:
    w = R.randint(16, 40)
    top = R.randint(196, 238)
    col = mix(SKY[3], BLD[0], 0.5)
    d.rectangle([x, top, x + w, HORIZON], fill=col)
    for wy in range(top + 5, HORIZON, 7):
        for wx in range(x + 3, x + w - 2, 5):
            if R.random() < 0.13 and 0 <= wx < W:
                px[wx, wy] = mix(col, WIN[2], 0.6)
    x += w + R.randint(-4, 2)
# a slim far tower with a red beacon
TX = 452
for y in range(150, 240):
    half = 1 + (y - 150) * 0.07
    for xx in range(int(TX - half), int(TX + half) + 1):
        px[xx, y] = mix(SKY[3], BLD[0], 0.5)
d.rectangle([TX - 4, 176, TX + 4, 181], fill=mix(SKY[3], BLD[0], 0.5))
px[TX, 148] = hexc("#e0503f")
px[TX, 149] = hexc("#a8332f")
haze(img, SKY[4], 0.25, (0, 140, W, HORIZON))


def building(x0, top, w, ramp, lit=0.4):
    """Near building with outline, a lit left edge and a window grid."""
    d.rectangle([x0, top, x0 + w, HORIZON + 4], fill=ramp[1], outline=BLD_OUT)
    d.line([x0 + 1, top + 1, x0 + 1, HORIZON + 4], fill=ramp[2])
    d.line([x0 + 1, top + 1, x0 + w - 1, top + 1], fill=ramp[2])
    kind = R.random()
    for wy in range(top + 6, HORIZON, 9):
        for wx in range(x0 + 4, x0 + w - 4, 7 if kind < 0.5 else 6):
            ww, wh = (3, 4) if kind < 0.5 else (4, 3)
            if R.random() < lit:
                c = R.choice((WIN[0], WIN[1], WIN[1], WIN[2]))
                d.rectangle([wx, wy, wx + ww - 1, wy + wh - 1], fill=c)
                if c == WIN[0]:
                    px[wx, wy] = hexc("#fff0c0")
            else:
                d.rectangle([wx, wy, wx + ww - 1, wy + wh - 1], fill=ramp[0])
    # rooftop bits
    if R.random() < 0.5 and w > 20:
        tx = x0 + R.randint(4, w - 14)
        d.rectangle([tx, top - 7, tx + 8, top - 1], fill=ramp[1], outline=BLD_OUT)  # water tank
        d.line([tx + 1, top - 6, tx + 7, top - 6], fill=ramp[2])
    elif w > 14:
        ax = x0 + w // 2
        d.line([ax, top - 12, ax, top], fill=BLD_OUT)
        px[ax, top - 13] = hexc("#e0503f")


NEAR = [BLD[0], mix(BLD[0], BLD[1], 0.5), BLD[2]]
NEAR2 = [mix(BLD[0], SKY[1], 0.3), mix(BLD[0], SKY[2], 0.3), BLD[1]]
x = -10
i = 0
while x < W:
    w = R.randint(24, 52)
    top = R.randint(222, 262) if i % 2 else R.randint(238, 276)
    building(x, top, w, NEAR if i % 2 else NEAR2, lit=0.3 + 0.2 * R.random())
    x += w + R.randint(2, 10)
    i += 1

# distant elevated line with a little lit train
VY = 272
d.rectangle([0, VY, W, VY + 5], fill=hexc("#1e1a36"))
d.line([0, VY, W, VY], fill=BLD[2])
for vx in range(20, W, 64):
    d.rectangle([vx, VY + 6, vx + 5, HORIZON], fill=hexc("#1e1a36"))
TRX0, TRX1 = 384, 512
d.rectangle([TRX0, VY - 9, TRX1, VY - 1], fill=hexc("#5a5a84"), outline=BLD_OUT)
d.line([TRX0 + 1, VY - 8, TRX1 - 1, VY - 8], fill=hexc("#8a88b0"))
for wx in range(TRX0 + 3, TRX1 - 3, 5):
    if (wx - TRX0) % 32 < 28:
        d.rectangle([wx, VY - 6, wx + 2, VY - 4], fill=WIN[0] if (wx // 5) % 3 else WIN[1])
d.line([TRX0 + 1, VY - 2, TRX1 - 1, VY - 2], fill=hexc("#6a9ab0"))
haze(img, SKY[4], 0.18, (0, 180, W, HORIZON))

# ------------------------------------------------------- far platform ---
# back railing (city shows through)
RAIL_TOP = 296
d.rectangle([0, RAIL_TOP, W, RAIL_TOP + 3], fill=BLD[2], outline=BLD_OUT)
d.line([0, RAIL_TOP + 1, W, RAIL_TOP + 1], fill=BLD[3])
for rx in range(2, W, 7):
    d.line([rx, RAIL_TOP + 4, rx, FAR_FLOOR], fill=BLD[1])
d.line([0, RAIL_TOP + 20, W, RAIL_TOP + 20], fill=BLD[1])
# floor top face with the far tactile strip, front face and shadow
vgrad(img, 0, FAR_FLOOR, W, FAR_FLOOR + 7, [BLD[2], BLD[3]])
for xx in range(W):
    px[xx, FAR_FLOOR + 4] = hexc("#b8973e") if dith(xx, FAR_FLOOR + 4, 0.8) else hexc("#8a7240")
d.line([0, FAR_FLOOR + 7, W, FAR_FLOOR + 7], fill=hexc("#8a86b0"))
d.rectangle([0, FAR_FLOOR + 8, W, TRACK_TOP - 1], fill=BLD[1])
d.line([0, TRACK_TOP - 1, W, TRACK_TOP - 1], fill=BLD_OUT)
for xx in range(0, W, 40):
    d.line([xx, FAR_FLOOR + 9, xx, TRACK_TOP - 2], fill=BLD[0])

# ----------------------------------------------------------------- canopy ---
CX1 = 440          # canopy ends here; open sky to the right
ROOF_TOP, FASCIA_TOP, FASCIA_BOT = 86, 96, 108
PILLARS = (26, 180, 428)
for pxx in PILLARS:
    d.rectangle([pxx, FASCIA_BOT, pxx + 6, FAR_FLOOR], fill=BLD[1], outline=BLD_OUT)
    d.line([pxx + 1, FASCIA_BOT + 1, pxx + 1, FAR_FLOOR - 1], fill=BLD[3])
    d.line([pxx + 5, FASCIA_BOT + 1, pxx + 5, FAR_FLOOR - 1], fill=BLD[0])
    for k in range(10):  # brackets
        px[pxx - 1 - k, FASCIA_BOT + 10 - k] = BLD[2]
        px[pxx + 7 + k, FASCIA_BOT + 10 - k] = BLD[2]
    d.rectangle([pxx - 2, FAR_FLOOR - 3, pxx + 8, FAR_FLOOR], fill=BLD[2], outline=BLD_OUT)
# roof: a thin sloped slab and a fascia band
for xx in range(0, CX1 + 1):
    top = ROOF_TOP + (2 if xx > CX1 - 3 else 0)
    for y in range(top, FASCIA_TOP):
        px[xx, y] = BLD_OUT if y == top else (BLD[3] if y == top + 1 else BLD[2])
d.rectangle([-1, FASCIA_TOP, CX1, FASCIA_BOT], fill=BLD[1], outline=BLD_OUT)
d.line([0, FASCIA_TOP + 1, CX1 - 1, FASCIA_TOP + 1], fill=BLD[3])
d.line([0, FASCIA_BOT - 2, CX1 - 1, FASCIA_BOT - 2], fill=hexc("#8a3a44"))   # red accent stripe
d.line([0, FASCIA_BOT - 3, CX1 - 1, FASCIA_BOT - 3], fill=hexc("#6a2e40"))
d.rectangle([0, FASCIA_BOT + 1, CX1, FASCIA_BOT + 2], fill=hexc("#1e1a36"))   # underside shadow

# ---------------------------------------------------- hanging bits under it ---
# pendant lamps
for lx in (118, 356):
    glow(img, lx, 132, 34, 30, 0.35, GLOW_CREAM)
    d.line([lx, FASCIA_BOT + 3, lx, 122], fill=BLD_OUT)
    d.polygon([(lx - 6, 128), (lx - 3, 122), (lx + 3, 122), (lx + 6, 128)], fill=BLD[2], outline=BLD_OUT)
    d.line([lx - 5, 129, lx + 5, 129], fill=GLOW_CREAM)
    d.rectangle([lx - 2, 130, lx + 2, 131], fill=hexc("#fff4d0"))
    px[lx - 3, 124] = BLD[3]

# station clock (plain face, two hands)
CKX, CKY = 222, 144
d.line([CKX - 5, FASCIA_BOT + 3, CKX - 5, CKY - 10], fill=BLD_OUT)
d.line([CKX + 5, FASCIA_BOT + 3, CKX + 5, CKY - 10], fill=BLD_OUT)
d.ellipse([CKX - 11, CKY - 11, CKX + 11, CKY + 11], fill=BLD[2], outline=BLD_OUT)
d.ellipse([CKX - 9, CKY - 9, CKX + 9, CKY + 9], fill=hexc("#e8e2d4"), outline=hexc("#8a86a0"))
for k in range(12):
    a = math.radians(k * 30)
    px[int(round(CKX + 7 * math.cos(a))), int(round(CKY + 7 * math.sin(a)))] = hexc("#6a6488")
d.line([CKX, CKY, CKX, CKY - 6], fill=hexc("#2a2744"))        # minute hand at 12
d.line([CKX, CKY, CKX - 4, CKY + 2], fill=hexc("#2a2744"))    # hour hand near 8
px[CKX, CKY] = hexc("#a8332f")
px[CKX - 6, CKY - 5] = hexc("#ffffff")

# a plain hanging sign (colour blocks and an arrow, no writing)
SG = (272, 134, 332, 150)
d.line([SG[0] + 6, FASCIA_BOT + 3, SG[0] + 6, SG[1]], fill=BLD_OUT)
d.line([SG[2] - 6, FASCIA_BOT + 3, SG[2] - 6, SG[1]], fill=BLD_OUT)
d.rectangle(SG, fill=hexc("#2e4a6a"), outline=hexc("#15223a"))
d.line([SG[0] + 1, SG[1] + 1, SG[2] - 1, SG[1] + 1], fill=hexc("#4a6a8e"))
d.rectangle([SG[0] + 4, SG[1] + 4, SG[0] + 11, SG[3] - 4], fill=hexc("#4a9a6a"))     # line colour chip
d.rectangle([SG[0] + 16, SG[1] + 7, SG[2] - 14, SG[1] + 8], fill=hexc("#aab8cc"))    # blank bars
d.rectangle([SG[0] + 16, SG[1] + 10, SG[2] - 22, SG[1] + 10], fill=hexc("#7a8ca6"))
ax, ay = SG[2] - 9, (SG[1] + SG[3]) // 2                                           # arrow
d.line([ax - 3, ay, ax + 3, ay], fill=hexc("#e8eef8"))
d.line([ax + 1, ay - 2, ax + 3, ay], fill=hexc("#e8eef8"))
d.line([ax + 1, ay + 2, ax + 3, ay], fill=hexc("#e8eef8"))


def paper_lantern(ramp, out, h=18, w=13):
    """Round ribbed paper lantern with dark caps and a tassel (no writing)."""
    S = Sprite(w + 2, h + 8)
    cap = hexc("#2a1a24")
    body = ellipse(w / 2, 2 + h / 2, w / 2, h / 2)
    S.blob(body, ramp, out, lx=0.8, ly=0.4, cuts=(-0.35, 0.35))
    for y in range(4, h, 3):   # ribs
        for xx in range(1, w):
            if (xx, y) in body and S.get(xx, y) != out:
                S.set(xx, y, mix(S.get(xx, y), out, 0.35))
    S.fill(rect(int(w / 2) - 2, 1, 5, 2), cap)
    S.fill(rect(int(w / 2) - 2, h + 1, 5, 2), cap)
    S.set(int(w / 2), 0, cap)
    for y in range(h + 3, h + 7):
        S.set(int(w / 2), y, ramp[-1])
    S.set(int(w / 2) - 1, h + 6, ramp[-1])
    S.set(int(w / 2) + 1, h + 6, ramp[-1])
    S.set(int(w / 2) - 2, 5, hexc("#fff8e8"))
    return S


# lantern string sagging along the fascia
HOOKS = list(range(10, CX1 - 4, 36))
for a, b in zip(HOOKS, HOOKS[1:]):
    for xx in range(a, b + 1):
        t = (xx - a) / (b - a)
        px[xx, int(FASCIA_BOT + 3 + 6 * math.sin(math.pi * t))] = hexc("#1e1a36")
for k, (a, b) in enumerate(zip(HOOKS, HOOKS[1:])):
    lx = (a + b) // 2
    red = k % 2 == 0
    glow(img, lx, 126, 19, 17, 0.4, GLOW if red else GLOW_CREAM)
for k, (a, b) in enumerate(zip(HOOKS, HOOKS[1:])):
    lx = (a + b) // 2
    red = k % 2 == 0
    L = paper_lantern(RED if red else CREAM[:3], RED_OUT if red else CREAM_OUT)
    paste(img, L, lx - 7, FASCIA_BOT + 7)

# ----------------------------------------------------- vending machines ---


def vending(body, body_out, seed):
    VR = random.Random(seed)
    S = Sprite(38, 84)
    S.blob(rounded_rect(0, 0, 36, 84, 2), body, body_out, lx=0.9, ly=0.2, cuts=(-0.5, 0.6))
    S.fill(rect(33, 2, 2, 80), body[-1])                       # side face
    S.fill(rect(3, 4, 28, 44), hexc("#9aa6c4"))                # lit display window
    S.fill(rect(4, 5, 26, 42), hexc("#d4dcef"))
    S.fill(rect(4, 5, 26, 2), hexc("#eef2fb"))
    cans = [hexc("#e0503f"), hexc("#f59a3f"), hexc("#4a9a6a"), hexc("#3e6a98"), hexc("#ffe8b0"),
            hexc("#8a4a8a"), hexc("#c8a040")]
    for row in range(3):
        y0 = 8 + row * 13
        for col in range(5):
            c = VR.choice(cans)
            S.fill(rect(6 + col * 5, y0, 3, 7), c)
            S.set(6 + col * 5, y0, mix(c, hexc("#ffffff"), 0.5))
            S.set(6 + col * 5 + 1, y0 + 9, hexc("#e0503f") if VR.random() < 0.3 else hexc("#6ac08a"))
        S.fill(rect(4, y0 + 8, 26, 1), hexc("#aab4cc"))
    S.fill(rect(24, 52, 7, 9), body[-1])                       # coin panel
    S.fill(rect(26, 54, 3, 1), hexc("#ffd98a"))
    S.fill(rect(26, 57, 3, 2), hexc("#1e1a36"))
    S.fill(rect(4, 66, 26, 9), hexc("#1e1a36"))                # dispense slot
    S.fill(rect(5, 67, 24, 1), body[-1])
    S.set(1, 1, body[0])
    return S


glow(img, 226, 300, 78, 58, 0.3, hexc("#cfdcff"))
VEND_Y = FAR_FLOOR - 82
paste(img, vending([hexc("#e8706a"), hexc("#c24a4c"), hexc("#963640"), hexc("#6e2a3a")], hexc("#3e1624"), 5),
      188, VEND_Y)
paste(img, vending([hexc("#e2e6f2"), hexc("#b8bed6"), hexc("#8a90b0"), hexc("#686e92")], hexc("#34385a"), 9),
      228, VEND_Y)
# light spilling on the floor in front
for xx in range(186, 268):
    for y in range(FAR_FLOOR, FAR_FLOOR + 7):
        if dith(xx, y, 0.55 - abs(xx - 227) / 90):
            px[xx, y] = mix(px[xx, y], hexc("#cfdcff"), 0.35)

# bench (wooden slats, iron legs) with a forgotten umbrella
BX0, BX1, BY = 386, 458, FAR_FLOOR - 13
d.rectangle([BX0, BY - 10, BX1, BY - 7], fill=hexc("#7a5040"), outline=hexc("#3a2028"))   # back rest
d.line([BX0 + 1, BY - 9, BX1 - 1, BY - 9], fill=hexc("#9a6a50"))
d.rectangle([BX0 - 2, BY, BX1 + 2, BY + 3], fill=hexc("#7a5040"), outline=hexc("#3a2028"))  # seat
d.line([BX0 - 1, BY + 1, BX1 + 1, BY + 1], fill=hexc("#9a6a50"))
for bx in (BX0 + 3, BX1 - 5):
    d.rectangle([bx, BY - 7, bx + 2, FAR_FLOOR], fill=hexc("#2a2744"))
    d.line([bx, BY - 7, bx, FAR_FLOOR], fill=BLD[2])
for k in range(14):   # umbrella leaning on the bench
    px[BX1 - 14 + k // 3, BY - 6 + k] = hexc("#3e6a98") if k > 1 else hexc("#1e1a36")
    if 3 < k < 12:
        px[BX1 - 13 + k // 3, BY - 6 + k] = hexc("#2a4a78")
px[BX1 - 15, BY - 7] = hexc("#1e1a36")

# a pair of little bins at the left end
for (bx, c, cd) in ((126, hexc("#3e6a98"), hexc("#2a4a78")), (144, hexc("#4a9a6a"), hexc("#2f6e4e"))):
    d.rectangle([bx, FAR_FLOOR - 22, bx + 14, FAR_FLOOR], fill=c, outline=BLD_OUT)
    d.line([bx + 1, FAR_FLOOR - 21, bx + 1, FAR_FLOOR - 1], fill=mix(c, hexc("#ffffff"), 0.25))
    d.rectangle([bx + 10, FAR_FLOOR - 21, bx + 13, FAR_FLOOR - 1], fill=cd)
    d.rectangle([bx + 4, FAR_FLOOR - 18, bx + 10, FAR_FLOOR - 17], fill=hexc("#1e1a36"))

# ------------------------------------------------------------ the tracks ---
vgrad(img, 0, TRACK_TOP, W, NEAR_EDGE, [hexc("#1b1733"), hexc("#221d3c"), hexc("#1b1733")])
for y in range(TRACK_TOP, NEAR_EDGE):   # ballast speckle
    for xx in range(W):
        if (xx * 7 + y * 13 + (xx * y) % 5) % 11 == 0:
            px[xx, y] = hexc("#2c2748")
for y in range(TRACK_TOP, TRACK_TOP + 5):   # shadow under the far platform
    for xx in range(W):
        if dith(xx, y, 1 - (y - TRACK_TOP) / 5):
            px[xx, y] = hexc("#110e22")
for sx in range(-2, W, 13):   # sleepers
    d.rectangle([sx, 366, sx + 6, 394], fill=hexc("#2f2a48"), outline=hexc("#15122a"))
    d.line([sx + 1, 367, sx + 5, 367], fill=hexc("#3d3858"))
for ry in (371, 387):
    d.line([0, ry, W, ry], fill=hexc("#8a86b0"))
    d.line([0, ry + 1, W, ry + 1], fill=hexc("#4d4670"))
    d.line([0, ry + 2, W, ry + 2], fill=hexc("#2a2744"))
    for gx in (118, 226, 356, 560):   # glints of lamp and moon light
        for k in range(-5, 6):
            if abs(k) < 3 or dith(gx + k, ry, 0.5):
                px[gx + k, ry] = hexc("#d8d0e8") if abs(k) < 2 else hexc("#b0a8cc")

# ------------------------------------------------------- our platform ---
vgrad(img, 0, NEAR_EDGE, W, H, [hexc("#4a4468"), hexc("#3d3858"), hexc("#34304f"), hexc("#2f2a48")])
d.line([0, NEAR_EDGE, W, NEAR_EDGE], fill=hexc("#17142b"))
d.line([0, NEAR_EDGE + 1, W, NEAR_EDGE + 1], fill=hexc("#8a86b0"))
d.line([0, NEAR_EDGE + 2, W, NEAR_EDGE + 2], fill=hexc("#c8c4dc"))
d.line([0, NEAR_EDGE + 3, W, NEAR_EDGE + 3], fill=hexc("#6a6490"))
# yellow tactile strip with raised dots
TS0, TS1 = NEAR_EDGE + 10, NEAR_EDGE + 21
d.rectangle([0, TS0, W, TS1], fill=hexc("#c9a43e"))
d.line([0, TS0, W, TS0], fill=hexc("#e2c060"))
d.line([0, TS1, W, TS1], fill=hexc("#8a6a34"))
d.line([0, TS1 + 1, W, TS1 + 1], fill=hexc("#2a2440"))
for row, dy in enumerate((TS0 + 3, TS0 + 7)):
    for dx in range(2 + row * 3, W, 6):
        px[dx, dy] = hexc("#f0d478")
        px[dx + 1, dy] = hexc("#e2c060")
        px[dx, dy + 1] = hexc("#a88838")
        px[dx + 1, dy + 1] = hexc("#8a6a34")

# ------------------------------------------------------------- finish ---
haze(img, hexc("#1b1733"), 0.08, (0, 0, W, H))
sky_ref = sky_ref.copy()
haze(sky_ref, hexc("#1b1733"), 0.08, (0, 0, W, H))

# baked stars, only on untouched sky pixels, clear of the HUD, cards and moon
ref = sky_ref.load()
blocked = [(0, 0, W, 32), (0, 34, 212, 76), (0, FASCIA_TOP, CX1 + 4, 160)]
blocked += [(sx - 3, sy - 3, sx + CARD_W + 3, sy + CARD_H + 3) for sx, sy in SLOTS]


def free(x, y, pad=2):
    if not (2 <= x < W - 2 and 2 <= y < H - 2):
        return False
    if any(b[0] <= x <= b[2] and b[1] <= y <= b[3] for b in blocked):
        return False
    if math.hypot(x - MX, y - MY) < MR + 10:
        return False
    return all(px[x + i, y + j] == ref[x + i, y + j] for i in range(-pad, pad + 1) for j in range(-pad, pad + 1))


stars = []
tries = 0
while len(stars) < 46 and tries < 20000:
    tries += 1
    sx, sy = R.randint(0, W - 1), R.randint(34, 250)
    if R.random() < (sy - 34) / 260:      # thinner toward the city glow
        continue
    if not free(sx, sy) or any(abs(sx - a) + abs(sy - b) < 22 for a, b in stars):
        continue
    stars.append((sx, sy))
for k, (sx, sy) in enumerate(stars):
    if k % 9 == 0:
        c = hexc("#fff4d6")
        for (ox, oy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            px[sx + ox, sy + oy] = mix(px[sx + ox, sy + oy], hexc("#b9b3dc"), 0.45)
    else:
        c = hexc("#b9b3dc") if k % 3 == 0 else hexc("#8f88b8")
    px[sx, sy] = c

img = save_bg(img, NAME)
with open(os.path.join(ASSETS, "bg", f"{NAME}_stars.json"), "w") as f:
    json.dump([list(s) for s in stars], f)
print(f"{len(stars)} stars")
mock(img, NAME, NAME)
