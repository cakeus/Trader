"""640x480 Icicle Station: a tiny mountain cable-car stop. A red station house with
icicles on its eaves and the bullwheel peeking out, a gondola climbing the cable
past a lattice pylon toward the peaks, and a snowy rail line in front.

Soft and hazy so the cream actor cards (slots in locations.json) pop. The
gondola hangs in the clear band above the cards on the right.
"""
import math
import random

from bgkit import W, H, new_bg, vgrad, dith, haze, paste, save_bg, mock
from pixelkit import Sprite, hexc, mix, ellipse, rect, rounded_rect, edge
from snowkit import (SKY, SNOW, SNOW_OUT, WARM, WARM_HI, MOUNTAIN_FAR, MOUNTAIN_MID,
                     pine, far_pine, mountains, snowfall, glow, snow_ground, lantern)

R = random.Random(83)
img, d = new_bg()
px = img.load()

HORIZON = 250
GROUND = 332

# ------------------------------------------------------------------- sky ---
vgrad(img, 0, 0, W, HORIZON + 20, SKY)
# a pale winter sun behind thin haze
for y in range(20, 120):
    for x in range(40, 160):
        r = math.hypot(x - 96, y - 66)
        if r < 15:
            px[x, y] = hexc("#fffaf0") if r < 13 else hexc("#fbeede")
        elif r < 44 and dith(x, y, 0.3 * (1 - (r - 15) / 29)):
            px[x, y] = mix(px[x, y], hexc("#fff4e8"), 0.5)

# -------------------------------------------------------------- mountains ---
mountains(img, HORIZON, [(150, 92, 170), (380, 44, 210), (610, 70, 170)], MOUNTAIN_FAR, cap_depth=0.34)
haze(img, SKY[3], 0.3, (0, 40, W, HORIZON + 1))
mountains(img, HORIZON + 16, [(40, 170, 120), (270, 160, 150), (500, 150, 140), (660, 180, 110)], MOUNTAIN_MID,
          cap_depth=0.25)
vgrad(img, 0, HORIZON + 14, W, GROUND + 4, [hexc("#dfe2f4"), hexc("#e6e8f6"), hexc("#d8dcf0")])
for x in range(-6, W + 6, 6):
    far_pine(img, x + R.randint(-2, 2), HORIZON + 18, R.randint(10, 22), hexc("#8a9ac4"))
haze(img, SKY[3], 0.2, (0, 100, W, HORIZON + 20))

# mid pines
for i, x in enumerate(range(240, W + 20, 24)):
    h = R.randint(44, 70)
    paste(img, pine(h, seed=i), x + R.randint(-6, 6), GROUND - 2 - h)
haze(img, hexc("#c8cfee"), 0.4, (0, 150, W, GROUND))

# ------------------------------------------------------------- the cable ---
CA = (236, 146)   # leaves the station here
CB = (640, 34)


def cable_y(x, off=0):
    t = (x - CA[0]) / (CB[0] - CA[0])
    sag = 10 * math.sin(math.pi * min(1, max(0, t)))
    return CA[1] + (CB[1] - CA[1]) * t + sag + off


# lattice pylon
PYX = 560
ptop = int(cable_y(PYX)) - 4
for y in range(ptop, GROUND + 2):
    f = (y - ptop) / (GROUND - ptop)
    half = 5 + f * 16
    l, r = int(PYX - half), int(PYX + half)
    px[l, y] = hexc("#6a7098")
    px[r, y] = hexc("#565c86")
    if (y - ptop) % 14 == 0:
        d.line([l, y, r, y], fill=hexc("#6a7098"))
for y in range(ptop, GROUND - 13, 14):  # cross bracing
    f0 = (y - ptop) / (GROUND - ptop)
    f1 = (y + 14 - ptop) / (GROUND - ptop)
    d.line([PYX - 5 - f0 * 16, y, PYX + 5 + f1 * 16, y + 14], fill=hexc("#7a80a8"))
    d.line([PYX + 5 + f0 * 16, y, PYX - 5 - f1 * 16, y + 14], fill=hexc("#7a80a8"))
d.rectangle([PYX - 22, ptop - 2, PYX + 22, ptop + 3], fill=hexc("#6a7098"), outline=hexc("#3e4468"))
d.rectangle([PYX - 22, ptop - 5, PYX + 22, ptop - 2], fill=SNOW[0], outline=SNOW_OUT)
for wx in (PYX - 16, PYX + 12):
    d.ellipse([wx - 3, ptop + 2, wx + 3, ptop + 8], fill=hexc("#8a90b8"), outline=hexc("#3e4468"))

# the two cables (up and down line)
for off in (0, 12):
    prev = None
    for x in range(CA[0], W):
        y = int(round(cable_y(x, off)))
        if prev is not None and abs(y - prev) > 1:
            for yy in range(min(y, prev) + 1, max(y, prev)):
                px[x, yy] = hexc("#4e4a70")
        px[x, y] = hexc("#4e4a70")
        prev = y

# gondola
GX = 404
gy = cable_y(GX + 18)
G = Sprite(48, 70)
# carriage on the cable and a hanger arm
G.blob(rounded_rect(12, 0, 22, 7, 2), [hexc("#9aa0c4"), hexc("#7a80a8"), hexc("#5a6088")], hexc("#34385a"),
       cuts=(-0.2, 0.5))
G.set(17, 3, hexc("#34385a"))
G.set(28, 3, hexc("#34385a"))
G.fill(rect(22, 7, 3, 16), hexc("#4e4a70"))
G.fill(rect(23, 7, 1, 16), hexc("#7a80a8"))
# cabin
cab = rounded_rect(4, 22, 40, 36, 4)
G.blob(cab, [hexc("#ff9a82"), hexc("#e8584e"), hexc("#c03e44"), hexc("#962c3c")], hexc("#5a1a2a"),
       lx=0.9, ly=0.3, cuts=(-0.5, 0.2, 0.7))
for wx in (8, 19, 30):  # windows
    G.fill(rect(wx, 28, 9, 14), hexc("#5a1a2a"))
    G.fill(rect(wx + 1, 29, 7, 12), hexc("#bcd8f0"))
    G.fill(rect(wx + 1, 29, 7, 3), hexc("#e8f4ff"))
    G.fill(rect(wx + 1, 37, 7, 4), hexc("#ffd890"))
    G.set(wx + 2, 30, hexc("#ffffff"))
G.fill(rect(5, 45, 38, 2), hexc("#fff4e8"))       # white stripe
G.fill(rect(5, 47, 38, 1), hexc("#d8c8c8"))
# snow on the roof
roof = {(x, y) for x in range(3, 45) for y in range(19, 24)
        if y >= 22 - (1 if 6 < x < 40 else 0) - (1 if (x * 3) % 7 < 3 and 8 < x < 38 else 0)}
G.fill(roof, SNOW[0])
for (x, y) in edge(roof):
    if (x, y - 1) not in roof:
        G.set(x, y, SNOW_OUT)
for x in (7, 15, 26, 36, 41):  # little icicles under the cabin
    G.set(x, 58, hexc("#dcecfc"))
    G.set(x, 59, hexc("#b8d4f0"))
paste(img, G, GX, int(gy) - 2)

# ------------------------------------------------------- station house ----
SX0, SX1, S_TOP = 22, 246, 136
WALL = [hexc("#e88a7a"), hexc("#d0685c"), hexc("#b0504a"), hexc("#8a3a3c")]
TRIM = hexc("#fbf1e4")
S_OUT = hexc("#5a2430")
d.rectangle([SX0, S_TOP, SX1, GROUND], fill=WALL[1], outline=S_OUT)
for x in range(SX0 + 1, SX1):   # vertical boards
    if (x - SX0) % 8 == 0:
        d.line([x, S_TOP + 1, x, GROUND], fill=WALL[2])
    elif (x - SX0) % 8 == 1:
        d.line([x, S_TOP + 1, x, GROUND], fill=WALL[0])
d.rectangle([SX1 - 12, S_TOP + 1, SX1 - 1, GROUND], fill=mix(WALL[2], hexc("#5a3a58"), 0.1))
d.rectangle([SX0, S_TOP, SX0 + 5, GROUND], fill=TRIM, outline=S_OUT)
d.rectangle([SX1 - 5, S_TOP, SX1, GROUND], fill=mix(TRIM, hexc("#8a88b0"), 0.3), outline=S_OUT)

# open bay at the right end with the bullwheel
BAY = (184, 142, 240, 212)
d.rectangle(BAY, fill=hexc("#4a3a58"), outline=S_OUT)
for y in range(BAY[1] + 1, BAY[3]):
    for x in range(BAY[0] + 1, BAY[2]):
        if dith(x, y, (y - BAY[1]) / (BAY[3] - BAY[1]) * 0.5):
            px[x, y] = hexc("#3e3050")
wheel = Sprite(44, 44)
wm = ellipse(21.5, 21.5, 20, 20)
wheel.blob(wm, [hexc("#b4b8d8"), hexc("#8a90b8"), hexc("#6a7098")], hexc("#34385a"), cuts=(-0.2, 0.5))
wheel.fill(ellipse(21.5, 21.5, 16, 16), hexc("#4a3a58"))
for a in range(0, 360, 45):
    for r_ in range(3, 17):
        wheel.set(int(21.5 + r_ * math.cos(math.radians(a))), int(21.5 + r_ * math.sin(math.radians(a))),
                  hexc("#7a80a8"))
wheel.blob(ellipse(21.5, 21.5, 4, 4), [hexc("#d8dcf0"), hexc("#9aa0c4")], hexc("#34385a"), cuts=(0.2,))
paste(img, wheel, 190, 150)
d.line([212, 151, CA[0], CA[1]], fill=hexc("#4e4a70"))
d.line([212, 193, CA[0], int(cable_y(CA[0], 12))], fill=hexc("#4e4a70"))

# windows (between cards) and a door
for (wx, wy) in ((188, 236),):
    glow(img, wx + 18, wy + 16, 36, 30, 0.3, WARM)
    d.rectangle([wx - 3, wy - 3, wx + 38, wy + 30], fill=TRIM, outline=S_OUT)
    d.rectangle([wx, wy, wx + 35, wy + 27], fill=WARM, outline=S_OUT)
    d.line([wx + 17, wy, wx + 17, wy + 27], fill=S_OUT, width=2)
    d.line([wx + 2, wy + 2, wx + 8, wy + 2], fill=WARM_HI)
    d.rectangle([wx - 5, wy + 31, wx + 40, wy + 34], fill=SNOW[0], outline=SNOW_OUT)
d.rectangle([34, 282, 60, GROUND], fill=hexc("#8a4a3a"), outline=S_OUT)
d.rectangle([38, 288, 56, 302], fill=WARM, outline=S_OUT)
px[55, 312] = hexc("#ffe08a")

# roof: shallow gable buried in snow, with icicles hanging from the eaves
RX0, RX1, RPEAK = SX0 - 16, SX1 + 16, 96
RC = (SX0 + SX1) // 2
for x in range(RX0, RX1 + 1):
    top = RPEAK + abs(x - RC) * (S_TOP - 8 - RPEAK) / (RC - RX0)
    thick = 13 + 2 * math.sin(x * 0.13) + 1.5 * math.sin(x * 0.41)
    for y in range(int(top) - 1, int(top + thick)):
        depth = (y - top) / thick
        c = SNOW_OUT if y == int(top) - 1 else SNOW[0] if depth < 0.5 else (SNOW[1] if depth < 0.8 else SNOW[2])
        if x > RC and depth >= 0.2:
            c = SNOW[1] if depth < 0.7 else SNOW[3]
        px[x, y] = c
    by = int(top + thick)
    for y in range(by, by + 4):
        px[x, y] = S_OUT if y == by + 3 else TRIM if y == by else mix(TRIM, hexc("#9a98c0"), 0.35)
    # icicles
    if x % 3 == 0 and RX0 + 2 < x < RX1 - 2:
        ln = R.choice((2, 3, 4, 6, 8, 11, 5))
        for i in range(ln):
            px[x, by + 4 + i] = hexc("#f4faff") if i < ln - 2 else hexc("#a8c8ec")
            if i < ln // 2:
                px[x + 1, by + 4 + i] = hexc("#c4dcf4")
# sign board on the roof gable: a snowflake emblem
d.rectangle([RC - 30, 106, RC + 30, 124], fill=hexc("#3e5a8a"), outline=hexc("#243a60"))
d.rectangle([RC - 29, 107, RC + 29, 108], fill=hexc("#5a7aaa"))
for k in range(6):
    a = math.radians(k * 60)
    for r_ in range(1, 7):
        px[int(RC + r_ * math.cos(a)), int(115 + r_ * math.sin(a))] = hexc("#f4faff")
for (x, y) in ((RC - 22, 115), (RC + 22, 115), (RC - 14, 115), (RC + 14, 115)):
    d.rectangle([x - 2, y - 1, x + 2, y + 1], fill=hexc("#cfe2fa"))
d.rectangle([RC - 31, 102, RC + 31, 105], fill=SNOW[0], outline=SNOW_OUT)

haze(img, hexc("#d8d6f0"), 0.12, (0, 40, W, GROUND))

# ---------------------------------------------------------------- ground ---
snow_ground(img, GROUND, H, drift=lambda x: int(2 * math.sin(x * 0.04) + 2 * math.sin(x * 0.11)) - 1)
# wooden platform in front of the station
PL_Y = GROUND + 2
d.rectangle([0, PL_Y, 300, PL_Y + 14], fill=hexc("#b07a4c"), outline=hexc("#4a2a20"))
for x in range(4, 300, 10):
    d.line([x, PL_Y + 1, x, PL_Y + 13], fill=hexc("#8a5a38"))
d.line([1, PL_Y + 1, 299, PL_Y + 1], fill=hexc("#d8a470"))
for x in range(0, 300):
    hh = 2 + int(1.5 + 1.5 * math.sin(x * 0.19) + math.sin(x * 0.07))
    for y in range(PL_Y - hh, PL_Y + 1):
        px[x, y] = SNOW[0] if y > PL_Y - hh else SNOW_OUT
for x in range(8, 300, 40):  # posts under the platform
    d.rectangle([x, PL_Y + 15, x + 4, PL_Y + 24], fill=hexc("#6e4228"))

# a bench with a suitcase, and a lamp
d.rectangle([90, PL_Y - 14, 138, PL_Y - 11], fill=hexc("#8a5a38"), outline=hexc("#4a2a20"))
d.rectangle([90, PL_Y - 16, 138, PL_Y - 14], fill=SNOW[0])
for bx in (94, 132):
    d.rectangle([bx, PL_Y - 11, bx + 2, PL_Y - 2], fill=hexc("#4a2a20"))
case = Sprite(22, 18)
case.blob(rect(1, 4, 20, 13), [hexc("#8ab8d8"), hexc("#5a8ab8"), hexc("#3e6a98")], hexc("#243a60"), cuts=(-0.2, 0.5))
case.fill({(x, 2) for x in range(8, 14)} | {(8, 3), (13, 3)}, hexc("#243a60"))
case.fill({(x, 9) for x in range(2, 20)}, hexc("#d8a470"))
paste(img, case, 146, PL_Y - 17)
glow(img, 258, PL_Y - 40, 22, 22, 0.5, WARM)
paste(img, lantern(44), 254, PL_Y - 46)

# snowy rail line crossing the foreground
RAIL_Y = 392
for x in range(-4, W, 12):  # sleepers
    d.rectangle([x, RAIL_Y - 2, x + 5, RAIL_Y + 10], fill=hexc("#9a8a98"), outline=hexc("#6a5a70"))
    d.line([x + 1, RAIL_Y - 1, x + 4, RAIL_Y - 1], fill=SNOW[0])
for ry in (RAIL_Y, RAIL_Y + 8):
    d.line([0, ry, W, ry], fill=hexc("#6a6a90"))
    d.line([0, ry - 1, W, ry - 1], fill=hexc("#dce0f0"))
    d.line([0, ry + 1, W, ry + 1], fill=hexc("#4a4a70"))
# a signal post by the tracks
SGX = 526
d.rectangle([SGX, 330, SGX + 3, RAIL_Y - 4], fill=hexc("#4e4a70"))
d.ellipse([SGX - 5, 318, SGX + 8, 331], fill=hexc("#34385a"))
d.ellipse([SGX - 2, 321, SGX + 5, 328], fill=hexc("#8ae0a8"))
px[SGX - 1, 322] = hexc("#e8fff0")
d.rectangle([SGX - 6, 315, SGX + 9, 318], fill=SNOW[0], outline=SNOW_OUT)

# foreground pines framing the right
for (x, h, s) in ((440, 88, 5), (586, 130, 6), (-30, 100, 7)):
    paste(img, pine(h, seed=s), x, GROUND + 22 - h)

snowfall(img, R, 520, (0, 30, W, H))
haze(img, hexc("#eeeaf8"), 0.06)

img = save_bg(img, "icicle_station")
mock(img, "icicle_station", "icicle_station")
