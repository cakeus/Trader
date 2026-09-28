"""640x480 Frostpine Lodge: a cozy log inn under a heavy snow roof, glowing windows,
chimney smoke, pines and far peaks.

Soft and a little hazy so the cream actor cards (slots in locations.json) pop.
The lodge's roof and chimney sit above the cards; its windows peek out between
them and the wreathed door shows below the middle card.
"""
import math
import random

from bgkit import W, H, new_bg, vgrad, dith, haze, paste, save_bg, mock
from pixelkit import Sprite, hexc, mix, ellipse, rect, edge
from snowkit import (SKY, SNOW, SNOW_OUT, PINE, WARM, WARM_HI, WARM_DEEP, MOUNTAIN_FAR, MOUNTAIN_MID,
                     pine, far_pine, mountains, snowfall, glow, snow_ground, smoke, lantern)

R = random.Random(71)
img, d = new_bg()
px = img.load()

HORIZON = 262
GROUND = 338

# ------------------------------------------------------------------- sky ---
vgrad(img, 0, 0, W, HORIZON + 20, SKY)

# -------------------------------------------------------------- mountains ---
mountains(img, HORIZON, [(70, 128, 150), (250, 96, 180), (470, 112, 160), (640, 134, 130)], MOUNTAIN_FAR)
haze(img, SKY[3], 0.35, (0, 80, W, HORIZON + 1))
mountains(img, HORIZON + 14, [(10, 190, 120), (170, 176, 140), (560, 180, 150)], MOUNTAIN_MID,
          cap_depth=0.22)
haze(img, SKY[3], 0.22, (0, 120, W, HORIZON + 18))

# distant snowfield between the foothills and the lodge
vgrad(img, 0, HORIZON + 14, W, GROUND + 4, [hexc("#dfe2f4"), hexc("#e6e8f6"), hexc("#d8dcf0")])
for x in range(-6, W + 6, 7):  # distant fir line along the foothills
    far_pine(img, x + R.randint(-2, 2), HORIZON + 16, R.randint(12, 24), hexc("#8a9ac4"))

# ------------------------------------------------------- mid pine row ------
for i, x in enumerate(range(-20, W + 20, 26)):
    h = R.randint(48, 78)
    S = pine(h, seed=i)
    paste(img, S, x + R.randint(-6, 6), GROUND - 4 - h)
haze(img, hexc("#c8cfee"), 0.38, (0, 150, W, GROUND))

# --------------------------------------------------------------- lodge ----
LX0, LX1 = 168, 472          # wall
WALL_TOP = 150
CX = (LX0 + LX1) // 2
LOG = [hexc("#d69a62"), hexc("#b87a48"), hexc("#94603a"), hexc("#6e4228")]
LOG_OUT = hexc("#4a2a20")
d.rectangle([LX0, WALL_TOP, LX1, GROUND], fill=LOG[1])
for y in range(WALL_TOP, GROUND + 1):
    k = (y - WALL_TOP) % 9
    c = LOG[0] if k == 0 else LOG[1] if k < 5 else LOG[2] if k < 8 else LOG_OUT
    for x in range(LX0, LX1 + 1):
        cc = c
        if k in (2, 3) and (x * 13 + y * 7) % 23 == 0:
            cc = LOG[2]  # knots / grain
        if x > LX1 - 30:
            cc = mix(cc, hexc("#5a3a58"), 0.18)
        px[x, y] = cc
# round log ends poking out at the corners
for y in range(WALL_TOP + 4, GROUND - 2, 9):
    for cx_ in (LX0 - 2, LX1 + 2):
        e = Sprite(10, 10)
        m = ellipse(4.5, 4.5, 4.2, 4.2)
        e.blob(m, [hexc("#f0c898"), hexc("#d8a470"), hexc("#b07a4c")], LOG_OUT, cuts=(-0.1, 0.5))
        e.set(4, 4, hexc("#b07a4c"))
        e.set(5, 4, hexc("#b07a4c"))
        paste(img, e, cx_ - 5, y)

# windows: warm 4-pane with snowy sills and flower boxes
WIN_FRAME = hexc("#5a3424")


def window(x, y, w=40, h=38):
    glow(img, x + w / 2, y + h / 2, w * 0.95, h * 0.95, 0.35, WARM)
    d.rectangle([x - 3, y - 3, x + w + 2, y + h + 2], fill=hexc("#8a5a3a"), outline=WIN_FRAME)
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=WARM, outline=WIN_FRAME)
    for yy in range(y + 1, y + h - 1):
        for xx in range(x + 1, x + w - 1):
            if yy > y + h * 0.55 and dith(xx, yy, (yy - y - h * 0.55) / (h * 0.45) * 0.6):
                px[xx, yy] = WARM_DEEP
    d.line([x + w // 2, y, x + w // 2, y + h - 1], fill=WIN_FRAME, width=2)
    d.line([x, y + h // 2, x + w - 1, y + h // 2], fill=WIN_FRAME, width=2)
    d.line([x + 2, y + 2, x + 8, y + 2], fill=WARM_HI)
    d.line([x + 2, y + 3, x + 4, y + 3], fill=WARM_HI)
    d.line([x + w // 2 + 3, y + 2, x + w // 2 + 8, y + 2], fill=WARM_HI)
    # tiny silhouettes of mugs on the inner sill
    for mx in (x + 6, x + w - 12):
        d.rectangle([mx, y + h - 6, mx + 4, y + h - 2], fill=hexc("#c0584a"))
        px[mx + 5, y + h - 4] = hexc("#c0584a")
    # snowy sill
    d.rectangle([x - 5, y + h + 3, x + w + 4, y + h + 6], fill=SNOW[0], outline=SNOW_OUT)
    d.line([x - 4, y + h + 6, x + w + 3, y + h + 6], fill=SNOW[2])
    for i in range(3):
        dx = R.randint(2, w - 2)
        d.line([x + dx, y + h + 7, x + dx, y + h + 8 + R.randint(0, 3)], fill=hexc("#dce8fa"))


for (wx, wy) in ((188, 190), (412, 190), (188, 262), (412, 262)):
    window(wx, wy)

# gable end: vertical boards and a round glowing window
PEAK = (CX, 62)
EAVE_Y = WALL_TOP
for y in range(PEAK[1] + 18, EAVE_Y):
    half = (y - PEAK[1]) * 1.02
    for x in range(int(CX - half), int(CX + half) + 1):
        if LX0 - 6 <= x <= LX1 + 6:
            c = LOG[1] if (x - CX) % 10 else LOG[3]
            if (x - CX) % 10 == 1:
                c = LOG[0]
            px[x, y] = mix(c, hexc("#5a3a58"), 0.12 if x > CX else 0)
glow(img, CX, 112, 30, 30, 0.35, WARM)
oval = ellipse(CX, 112, 13, 13)
for (x, y) in oval:
    r = math.hypot(x - CX, y - 112)
    px[x, y] = WIN_FRAME if r > 11 else (WARM_HI if (x < CX - 3 and y < 108) else WARM)
for (x, y) in oval:
    if abs(x - CX) < 1 or abs(y - 112) < 1:
        if math.hypot(x - CX, y - 112) < 11:
            px[x, y] = WIN_FRAME

# chimney (stone) on the right slope
CH_X0, CH_X1, CH_TOP = 394, 422, 60
d.rectangle([CH_X0, CH_TOP, CH_X1, 128], fill=hexc("#9a96b4"), outline=hexc("#4e4a6a"))
for yy in range(CH_TOP + 2, 128, 6):
    off = 0 if (yy // 6) % 2 else 5
    for xx in range(CH_X0 + 1 + off, CH_X1, 10):
        d.rectangle([xx, yy, xx + 8, yy + 4], fill=hexc("#b4b0cc") if xx < CH_X0 + 12 else hexc("#8c88aa"))
        d.line([xx, yy, xx + 7, yy], fill=hexc("#d0cce4"))
d.rectangle([CH_X0 - 3, CH_TOP - 4, CH_X1 + 3, CH_TOP + 1], fill=hexc("#7c78a0"), outline=hexc("#4e4a6a"))
d.rectangle([CH_X0 - 3, CH_TOP - 9, CH_X1 + 3, CH_TOP - 4], fill=SNOW[0], outline=SNOW_OUT)
d.ellipse([CH_X0 - 1, CH_TOP - 13, CH_X1 + 1, CH_TOP - 5], fill=SNOW[0], outline=SNOW_OUT)
d.line([CH_X0 + 1, CH_TOP - 5, CH_X1 - 1, CH_TOP - 5], fill=SNOW[0])

# roof: heavy snow blanket over a dark wood fascia
RX0, RX1 = LX0 - 22, LX1 + 22
for x in range(RX0, RX1 + 1):
    top = PEAK[1] + abs(x - CX) * (EAVE_Y - PEAK[1]) / (CX - RX0)
    thick = 16 + 3 * math.sin(x * 0.11) + 2 * math.sin(x * 0.37)
    for y in range(int(top) - 1, int(top + thick)):
        if y < 0 or y >= H:
            continue
        depth = (y - top) / thick
        if depth < 0.12:
            c = SNOW_OUT if y == int(top) - 1 else SNOW[0]
        elif depth < 0.7:
            c = SNOW[0] if x < CX else SNOW[1]
            if depth > 0.5:
                c = SNOW[1] if x < CX else SNOW[2]
        else:
            c = SNOW[2] if x < CX else SNOW[3]
        px[x, y] = c
    # fascia board and shadow under the snow
    by = int(top + thick)
    for y in range(by, by + 5):
        if y < H:
            px[x, y] = hexc("#6e4228") if y < by + 3 else hexc("#4a2a20")
    px[x, by] = SNOW_OUT
# icicles along the eaves
for x in range(RX0 + 4, RX1 - 2, 5):
    top = PEAK[1] + abs(x - CX) * (EAVE_Y - PEAK[1]) / (CX - RX0)
    y0 = int(top + 16 + 3 * math.sin(x * 0.11) + 2 * math.sin(x * 0.37)) + 5
    ln = R.choice((3, 5, 7, 9))
    for i in range(ln):
        px[x, y0 + i] = hexc("#f4faff") if i < ln - 2 else hexc("#b8d4f0")
        if i < ln // 2:
            px[x + 1, y0 + i] = hexc("#b8d4f0")
# snow ridge cap at the peak
d.ellipse([CX - 10, PEAK[1] - 6, CX + 10, PEAK[1] + 6], fill=SNOW[0], outline=SNOW_OUT)
d.rectangle([CX - 9, PEAK[1] + 1, CX + 9, PEAK[1] + 6], fill=SNOW[0])

smoke(img, R, (CH_X0 + CH_X1) // 2, CH_TOP - 8, n=6)

# porch roof and door (below the middle card)
DOOR_X0, DOOR_X1, DOOR_TOP = CX - 20, CX + 20, 264
glow(img, CX, GROUND + 10, 70, 22, 0.55, WARM)
d.rectangle([DOOR_X0 - 4, DOOR_TOP - 4, DOOR_X1 + 4, GROUND], fill=hexc("#6e4228"), outline=LOG_OUT)
d.rectangle([DOOR_X0, DOOR_TOP, DOOR_X1, GROUND], fill=hexc("#a8543c"), outline=LOG_OUT)
for x in range(DOOR_X0 + 5, DOOR_X1, 8):
    d.line([x, DOOR_TOP + 1, x, GROUND], fill=hexc("#8a4030"))
d.line([DOOR_X0 + 2, DOOR_TOP + 2, DOOR_X0 + 2, GROUND], fill=hexc("#c8704e"))
d.rectangle([CX - 7, DOOR_TOP + 8, CX + 7, DOOR_TOP + 18], fill=WARM, outline=LOG_OUT)
d.line([CX, DOOR_TOP + 8, CX, DOOR_TOP + 18], fill=LOG_OUT)
px[DOOR_X1 - 6, DOOR_TOP + 40] = hexc("#ffe08a")
px[DOOR_X1 - 6, DOOR_TOP + 41] = hexc("#d89a2a")
# wreath
wreath = Sprite(24, 24)
ring = ellipse(11.5, 11.5, 10, 10) - ellipse(11.5, 11.5, 5, 5)
wreath.blob(ring, [hexc("#5aa27a"), hexc("#3a7e62"), hexc("#2a5e4c")], hexc("#1c3c34"), cuts=(-0.3, 0.4))
for (x, y) in ((4, 8), (15, 4), (18, 14), (7, 17), (11, 3), (3, 13)):
    wreath.set(x, y, hexc("#e8534e"))
    wreath.set(x + 1, y, hexc("#ff8a7a"))
wreath.fill({(10, 18), (11, 18), (12, 18), (13, 18), (11, 19), (12, 19)}, hexc("#e8534e"))
paste(img, wreath, CX - 12, DOOR_TOP + 22)
# lanterns either side of the door
for lx in (DOOR_X0 - 18, DOOR_X1 + 10):
    glow(img, lx + 4, DOOR_TOP + 24, 16, 16, 0.5, WARM)
    paste(img, lantern(14), lx, DOOR_TOP + 18)

haze(img, hexc("#d8d6f0"), 0.12, (0, 40, W, GROUND))

# ---------------------------------------------------------------- ground ---
snow_ground(img, GROUND, H, drift=lambda x: int(3 * math.sin(x * 0.03) + 2 * math.sin(x * 0.09 + 1)) - 2)
# a packed-snow path from the door toward the viewer
for y in range(GROUND, H):
    t = (y - GROUND) / (H - GROUND)
    half = 22 + t * 70
    c0 = CX + math.sin(t * 2.2) * 30
    for x in range(int(c0 - half), int(c0 + half) + 1):
        if 0 <= x < W:
            e = abs(x - c0) / half
            if e > 0.9:
                px[x, y] = mix(px[x, y], SNOW[3], 0.5)
            else:
                px[x, y] = mix(px[x, y], hexc("#d8cfe4"), 0.45) if dith(x, y, 0.5) else mix(px[x, y], hexc(
                    "#e6dff0"), 0.4)
    # footprints
    if y % 14 == 0:
        fx = int(c0 + (8 if (y // 14) % 2 else -8))
        d.ellipse([fx - 2, y, fx + 2, y + 3], fill=SNOW[3])
glow(img, CX, GROUND + 12, 90, 24, 0.35, WARM)
# lodge's snow drift along its base
for x in range(LX0 - 12, LX1 + 13):
    hh = 5 + int(3 * math.sin(x * 0.2) + 2 * math.sin(x * 0.07))
    for y in range(GROUND - hh, GROUND + 2):
        if DOOR_X0 - 6 <= x <= DOOR_X1 + 6:
            continue
        px[x, y] = SNOW[0] if y < GROUND - hh + 2 else SNOW[1]
    px[x, GROUND - hh - 1] = SNOW_OUT if not (DOOR_X0 - 6 <= x <= DOOR_X1 + 6) else px[x, GROUND - hh - 1]

# firewood stack at the lodge's right
for row in range(4):
    for i in range(5 - row % 2):
        cx_, cy_ = 488 + i * 9 + (row % 2) * 4, GROUND - 6 - row * 8
        e = Sprite(10, 10)
        e.blob(ellipse(4.5, 4.5, 4.2, 4.2), [hexc("#f0c898"), hexc("#d8a470"), hexc("#b07a4c")], LOG_OUT,
               cuts=(-0.1, 0.5))
        e.set(4, 4, hexc("#b07a4c"))
        paste(img, e, cx_ - 5, cy_ - 5)
d.rectangle([481, GROUND - 42, 536, GROUND - 37], fill=SNOW[0], outline=SNOW_OUT)

# fence posts with snow caps
for fx in list(range(20, 150, 22)) + list(range(548, 640, 22)):
    d.rectangle([fx, GROUND + 6, fx + 5, GROUND + 30], fill=LOG[2], outline=LOG_OUT)
    d.line([fx + 1, GROUND + 7, fx + 1, GROUND + 29], fill=LOG[1])
    d.rectangle([fx - 1, GROUND + 3, fx + 6, GROUND + 6], fill=SNOW[0], outline=SNOW_OUT)
for (a, b) in ((20, 150), (548, 640)):
    for ry in (GROUND + 12, GROUND + 22):
        d.line([a, ry, b, ry], fill=LOG[2])
        d.line([a, ry - 1, b, ry - 1], fill=SNOW[0])

# foreground pines framing the edges
for (x, h, s) in ((-26, 150, 1), (18, 104, 2), (578, 140, 3), (612, 176, 4)):
    S = pine(h, seed=s)
    paste(img, S, x, GROUND + 26 - h)

# a little red sled by the path, with its rope trailing in the snow
sled = Sprite(62, 22)
sled.blob(rect(4, 4, 50, 8), [hexc("#ff8a7a"), hexc("#e0474c"), hexc("#b83244"), hexc("#8c2238")],
          hexc("#5a1626"), cuts=(-0.4, 0.2, 0.7))
for x in range(8, 52, 7):
    sled.fill({(x, y) for y in range(6, 11)}, hexc("#b83244"))
sled.fill({(x, 4) for x in range(5, 53)} | {(x, 5) for x in range(6, 50, 3)}, SNOW[0])
RUN = hexc("#5e5a84")
for x in (10, 44):
    sled.fill({(x, y) for y in range(12, 17)} | {(x + 1, y) for y in range(12, 17)}, RUN)
sled.fill({(x, 17) for x in range(3, 58)} | {(x, 18) for x in range(4, 56)}, RUN)
sled.fill({(58, 16), (59, 15), (60, 14), (59, 14), (2, 16), (1, 15)}, RUN)
sled.fill({(x, 17) for x in range(6, 50, 9)}, hexc("#9a96c0"))
paste(img, sled, 398, 366)
for i in range(22):  # rope
    px[398 - i, 376 + int(3 * math.sin(i / 5))] = hexc("#c89a6a")

snowfall(img, R, 520, (0, 30, W, H))
haze(img, hexc("#eeeaf8"), 0.06)

img = save_bg(img, "frostpine_lodge")
mock(img, "frostpine_lodge", "frostpine_lodge")
