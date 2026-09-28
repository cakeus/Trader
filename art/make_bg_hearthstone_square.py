"""640x480 Hearthstone Square: a snowy town square at blue hour. Gabled houses with
warm windows, a big decorated fir, market stalls with snow-dusted striped awnings,
string lights, lanterns, a snowman and the stone hearth glowing in the middle.

Soft and hazy so the cream actor cards (slots in locations.json) pop. The fir's
star rises above the middle card; the hearth sits just below it.
"""
import math
import random

from bgkit import W, H, new_bg, vgrad, dith, haze, paste, save_bg, mock
from pixelkit import Sprite, hexc, mix, ellipse, rect, rounded_rect, edge
from snowkit import (SKY, SNOW, SNOW_OUT, WARM, WARM_HI, WARM_DEEP, MOUNTAIN_FAR,
                     pine, mountains, snowfall, glow, lantern, smoke)

R = random.Random(97)
img, d = new_bg()
px = img.load()

HORIZON = 230
GROUND = 330

# ------------------------------------------------------------------- sky ---
vgrad(img, 0, 0, W, HORIZON + 40, [hexc("#98a8dc"), hexc("#aab4e6"), hexc("#c4c4ee"), hexc("#dccfee"),
                                   hexc("#f0dcec")])
mountains(img, HORIZON, [(90, 110, 170), (330, 86, 190), (560, 104, 170)], MOUNTAIN_FAR, cap_depth=0.32)
haze(img, SKY[3], 0.38, (0, 0, W, HORIZON + 1))

# --------------------------------------------------------- far rooftops ---
FAR = [hexc("#b8b8e0"), hexc("#aaaed8")]
x = -12
while x < W:
    w = R.randint(36, 56)
    top = R.randint(168, 190)
    peak = top - R.randint(14, 22)
    col = FAR[R.randint(0, 1)]
    for yy in range(peak, GROUND):
        for xx in range(x, x + w):
            if 0 <= xx < W:
                roof_y = peak + abs(xx - (x + w / 2)) * (top - peak) / (w / 2)
                if yy >= roof_y:
                    px[xx, yy] = col if yy > roof_y + 4 else hexc("#eceefa")
    for wx in range(x + 7, x + w - 7, 11):
        for wy in range(top + 8, GROUND, 16):
            if 0 <= wx < W - 4 and R.random() < 0.55:
                d.rectangle([wx, wy, wx + 3, wy + 5], fill=mix(col, WARM, 0.55))
    x += w + R.randint(-4, 4)
haze(img, hexc("#d4d0f0"), 0.3, (0, 130, W, GROUND))

# ---------------------------------------------------------- near houses ---
HOUSE_COLS = [hexc("#8fa6cf"), hexc("#d49a9a"), hexc("#e8d4a8"), hexc("#9cc0b0"), hexc("#b8a0d0"),
              hexc("#d8a888")]


def house(x, w, top, col):
    outl = mix(col, hexc("#2a2448"), 0.6)
    shade = mix(col, hexc("#3a3060"), 0.22)
    light = mix(col, hexc("#fff6ee"), 0.25)
    d.rectangle([x, top, x + w - 1, GROUND], fill=col, outline=outl)
    d.line([x + 1, top + 1, x + 1, GROUND], fill=light)
    d.rectangle([x + w - 6, top + 1, x + w - 2, GROUND], fill=shade)
    peak = top - int(w * 0.42)
    # snowy gable roof
    for xx in range(x - 5, x + w + 5):
        ry = peak + abs(xx - (x + w / 2)) * (top - peak) / (w / 2 + 5)
        for yy in range(int(ry), top + 5):
            depth = yy - ry
            if 0 <= xx < W:
                if depth < 1:
                    c = SNOW_OUT
                elif depth < 7 + 2 * math.sin(xx * 0.3):
                    c = SNOW[0] if xx < x + w / 2 else SNOW[1]
                else:
                    c = mix(col, hexc("#6a4a6a"), 0.45)
                px[xx, yy] = c
    for xx in range(x - 5, x + w + 5):  # snow lip along the eave
        if 0 <= xx < W:
            px[xx, top + 4] = SNOW[1]
            px[xx, top + 5] = SNOW_OUT if (xx * 7) % 5 else SNOW[2]
    # windows
    for wx in range(x + 9, x + w - 16, 20):
        for wy in range(top + 14, GROUND - 40, 28):
            lit = R.random() < 0.75
            glow(img, wx + 5, wy + 7, 14, 14, 0.25 if lit else 0, WARM)
            d.rectangle([wx, wy, wx + 10, wy + 14], fill=WARM if lit else hexc("#7a80b0"), outline=outl)
            d.line([wx + 5, wy, wx + 5, wy + 14], fill=outl)
            d.line([wx + 1, wy + 1, wx + 3, wy + 1], fill=WARM_HI if lit else hexc("#a8b0d8"))
            d.rectangle([wx - 2, wy + 15, wx + 12, wy + 16], fill=SNOW[0])
    # chimney
    cx_ = x + w - 18
    cy_ = peak + int((cx_ - (x + w / 2)) * (top - peak) / (w / 2 + 5)) - 10
    d.rectangle([cx_, cy_, cx_ + 7, cy_ + 16], fill=mix(col, hexc("#6a4a6a"), 0.3), outline=outl)
    d.rectangle([cx_ - 1, cy_ - 3, cx_ + 8, cy_], fill=SNOW[0], outline=SNOW_OUT)
    return cx_ + 3, cy_ - 3


HOUSES = [(-10, 84, 176), (74, 76, 190), (150, 88, 172), (238, 70, 196), (400, 80, 182), (480, 72, 196),
          (552, 96, 170)]
chims = []
for i, (hx, hw, ht) in enumerate(HOUSES):
    chims.append(house(hx, hw, ht, HOUSE_COLS[i % len(HOUSE_COLS)]))
for (cx_, cy_) in chims[1::3]:
    smoke(img, R, cx_, cy_, n=4)
haze(img, hexc("#c8c4ec"), 0.2, (0, 90, W, GROUND))

# ------------------------------------------------ the big decorated fir ----
TX = 320
tree = pine(190, seed=11)
tw = tree.w
paste(img, tree, TX - tw // 2, GROUND - 188)
tpx = img.load()
BULBS = [hexc("#ffd24a"), hexc("#ff8a7a"), hexc("#8ad8f0"), hexc("#fff4c8")]
for i in range(70):
    yy = R.randint(GROUND - 170, GROUND - 16)
    f = (yy - (GROUND - 188)) / 176
    xx = TX + R.randint(-int(f * 50), int(f * 50))
    r, g, b, a = tpx[xx, yy]
    if g > 60 and b > 60 and r < 120:  # only on the needles
        c = BULBS[i % 4]
        tpx[xx, yy] = c
        glow(img, xx, yy, 4, 4, 0.4, c)
# star on top
star = Sprite(15, 15)
star.rows([
    ".......O.......",
    "......OYO......",
    "......OYO......",
    ".....OYWYO.....",
    "OOOOOYYWYYOOOOO",
    ".OYYYYWWYYYYYO.",
    "..OYYYYYYYYYO..",
    "...OYYYYYYyO...",
    "....OYYYYYyO...",
    "...OYYyOYYyO...",
    "...OYyO.OyyO...",
    "..OYyO...OyO...",
    "..OOO.....OO...",
], {"O": hexc("#a8701e"), "Y": hexc("#ffd24a"), "W": hexc("#fff8d0"), "y": hexc("#e0a030")})
glow(img, TX, GROUND - 190, 22, 22, 0.55, hexc("#fff0b0"))
paste(img, star, TX - 7, GROUND - 198)

# ------------------------------------------------------------- stalls ------


def stall(x, w, stripe, goods):
    top = GROUND - 78
    S = Sprite(w + 4, 84)
    so = mix(stripe, hexc("#402030"), 0.55)
    # back cloth
    for yy in range(22, 58):
        c = mix(mix(stripe, hexc("#fff4e4"), 0.65), mix(stripe, hexc("#503a58"), 0.3), (yy - 22) / 36)
        for xx in range(4, w):
            S.set(xx, yy, c)
    for pxx in (3, w - 3):
        S.blob(rect(pxx, 12, 3, 72), [hexc("#c89868"), hexc("#a07048"), hexc("#805838")], hexc("#503028"),
               lx=1, ly=0, cuts=(-0.2, 0.5))
    # awning with scallops
    aw = rect(1, 8, w + 2, 14) | {(xx, 22) for xx in range(1, w + 3) if (xx - 1) % 8 in (1, 2, 3, 4, 5)} \
        | {(xx, 23) for xx in range(1, w + 3) if (xx - 1) % 8 in (2, 3, 4)}
    for (xx, yy) in aw:
        on = ((xx - 1) // 8) % 2 == 0
        c = stripe if on else hexc("#fff4e8")
        c = mix(c, hexc("#503a58"), 0.22 * (yy - 8) / 15)
        S.set(xx, yy, c)
    for p in edge(aw):
        S.set(*p, so)
    # snow dusting on the awning, with a few drips
    for xx in range(0, w + 4):
        hh = 3 + int(1.5 + 1.5 * math.sin(xx * 0.5 + x) + math.sin(xx * 0.17))
        for yy in range(9 - hh, 10):
            S.set(xx, yy, SNOW[0] if xx < w * 0.6 else SNOW[1])
        S.set(xx, 9 - hh - 1, SNOW_OUT)
        if xx % 9 == 4:
            S.set(xx, 10, SNOW[1])
            S.set(xx, 11, SNOW[2])
    # counter
    S.blob(rect(0, 58, w + 4, 22), [hexc("#d8a068"), hexc("#b07a4a"), hexc("#8a5a38")], hexc("#4a2a1c"),
           lx=0.3, ly=1, cuts=(-0.3, 0.5))
    for yy in (65, 72):
        for xx in range(2, w + 2):
            S.set(xx, yy, hexc("#8a5a38"))
    for xx in range(1, w + 3):
        S.set(xx, 58, SNOW[0])
        S.set(xx, 57, SNOW_OUT if xx % 4 else SNOW[1])
    # goods on the counter
    gx = 6
    while gx < w - 6:
        kind = goods[(gx // 8) % len(goods)]
        if kind == "mug":
            S.fill(rect(gx, 51, 5, 6), hexc("#e0474c"))
            S.fill(rect(gx, 51, 5, 1), hexc("#8a4e32"))
            S.set(gx + 5, 53, hexc("#e0474c"))
            S.set(gx + 1, 52, hexc("#ff8a7a"))
            S.set(gx + 2, 49, hexc("#e0dcf4"))
            S.set(gx + 1, 48, hexc("#e0dcf4"))
        elif kind == "crystal":
            S.fill({(gx + 2, 50), (gx + 1, 51), (gx + 2, 51), (gx + 3, 51)}, hexc("#c4e8fa"))
            S.fill(rect(gx, 52, 5, 5), hexc("#8cc4ee"))
            S.fill(rect(gx, 52, 2, 5), hexc("#e8f6ff"))
        elif kind == "box":
            S.fill(rect(gx, 51, 6, 6), hexc("#c07a44"))
            S.fill(rect(gx, 51, 6, 1), hexc("#ffd24a"))
            S.set(gx + 2, 54, hexc("#ffd24a"))
        else:  # scarf / mittens
            S.fill(rect(gx, 50, 5, 7), stripe)
            S.fill({(gx + i, 52) for i in range(5)} | {(gx + i, 55) for i in range(5)}, hexc("#fff4e8"))
        gx += 8
    paste(img, S, x, top)


for (sx, sw, col, goods) in ((-14, 86, hexc("#e0584e"), ("mug", "scarf")),
                             (170, 92, hexc("#4e8ab8"), ("crystal", "box")),
                             (382, 88, hexc("#3f9a7a"), ("scarf", "mug")),
                             (566, 90, hexc("#9a6ac8"), ("box", "crystal"))):
    stall(sx, sw, col, goods)

# string lights swooping between the stalls and the tree
for (ax, ay, bx, by) in ((0, 150, TX - 60, 170), (TX + 60, 170, W, 150), (40, 206, 250, 214),
                         (390, 214, 610, 206)):
    for i in range(0, 101):
        t = i / 100
        x = int(ax + (bx - ax) * t)
        y = int(ay + (by - ay) * t + 22 * math.sin(math.pi * t))
        if 0 <= x < W:
            px[x, y] = hexc("#4a4a70")
        if i % 7 == 3 and 0 <= x < W - 1:
            c = BULBS[(i // 7) % 4]
            glow(img, x, y + 2, 5, 5, 0.5, c)
            px[x, y + 1] = c
            px[x, y + 2] = c
            px[x + 1, y + 1] = mix(c, hexc("#ffffff"), 0.4)

haze(img, hexc("#d8d6f0"), 0.1, (0, 40, W, GROUND))

# -------------------------------------------------------- square ground ---
d.rectangle([0, GROUND, W, H], fill=hexc("#8a88ac"))
y = GROUND + 1
row = 0
while y < H:
    rh = 6 + row // 3
    x = -((row * 9) % 18)
    while x < W:
        sw = R.randint(12, 18)
        base = hexc(R.choice(["#aeaccb", "#a4a2c4", "#b6b4d2", "#9c9abc"]))
        for sy in range(y + 1, min(H, y + rh - 1)):
            for sx in range(x + 1, x + sw - 1):
                if 0 <= sx < W:
                    c = base
                    if sy == y + 1 or sx == x + 1:
                        c = mix(base, hexc("#eceaf8"), 0.35)
                    elif sy == y + rh - 2 or sx == x + sw - 2:
                        c = mix(base, hexc("#4a4470"), 0.2)
                    px[sx, sy] = c
        x += sw
    y += rh
    row += 1


# snow lying over the cobbles: thick at the edges and in drifts, swept clear around the hearth
HX, HY = 320, 372


def snow_amt(x, y):
    """~1 = deep snow, ~0 = bare cobbles. Swept clear in a wide oval around the hearth."""
    n = 1.0 + 0.12 * math.sin(x * 0.019 + y * 0.03) + 0.08 * math.sin(x * 0.051 - y * 0.04 + 2)
    clear = math.hypot((x - HX) / 190, (y - HY) / 62)
    n -= max(0, 1.25 - clear) * 0.95
    n += max(0, 1 - (y - GROUND) / 10) * 0.6  # heaped against the stalls
    return n


for y in range(GROUND, H):
    for x in range(W):
        a = snow_amt(x, y)
        if a > 0.62:
            px[x, y] = SNOW[0] if a > 0.95 and (y - GROUND) < 60 else SNOW[1] if a > 0.8 else SNOW[2]
            if a > 0.95 and (y - GROUND) >= 60:
                px[x, y] = SNOW[1] if dith(x, y, min(1, (y - GROUND - 60) / 100)) else SNOW[0]
        elif a > 0.45 and dith(x, y, (a - 0.45) / 0.17):
            px[x, y] = SNOW[2]
        elif a > 0.4 and dith(x, y, 0.25):
            px[x, y] = mix(px[x, y], SNOW[2], 0.5)

# the hearth: a round stone fire pit with a warm fire
glow(img, HX, HY - 6, 120, 56, 0.55, WARM)
glow(img, HX, HY - 14, 46, 36, 0.6, hexc("#ffd890"))
pit = Sprite(80, 40)
outer = ellipse(39.5, 22, 38, 14)
pit.blob(outer, [hexc("#c8c4dc"), hexc("#a6a2c2"), hexc("#86829e"), hexc("#6a6682")], hexc("#3e3a58"),
         cuts=(-0.4, 0.15, 0.6))
for a in range(0, 360, 24):  # stone joints
    r_x, r_y = 38 * 0.82, 14 * 0.82
    pit.set(int(39.5 + r_x * math.cos(math.radians(a))), int(22 + r_y * math.sin(math.radians(a))),
            hexc("#5e5a78"))
inner = ellipse(39.5, 19, 27, 8)
pit.blob(inner, [hexc("#6a4a4a"), hexc("#4a3040"), hexc("#3a2438")], hexc("#3e3a58"), cuts=(0.1, 0.5))
for sx in range(4, 76, 6):  # snow on the rim, lit side
    for yy in range(8, 14):
        if (sx, yy) in edge(outer) or ((sx, yy) in outer and (sx, yy - 1) not in outer):
            pit.set(sx, yy, SNOW[0])
            pit.set(sx + 1, yy, SNOW[0])
            break
paste(img, pit, HX - 40, HY - 22)
fire = Sprite(40, 40)
fire.rows([
    "..............Y.........",
    ".............YY.........",
    "......Y......YO.....Y...",
    "......YY....YOO....YY...",
    ".....YOY....YOOY...YO...",
    ".....YOOY..YORRO..YOY...",
    "....YORROYYORRROY.YOOY..",
    "...YORRRROYORRRRROYORY..",
    "...YORRRROYORRRRRROORRY.",
    "..YORRRRRROORRRRRRRORRY.",
    "..YORRRRRRROORRRRRRRROY.",
    "..YOORRRRRRRRRRRRRRROOY.",
    "...YOOORRRRRRRRRRRROOY..",
    "....YYOOOOOOOOOOOOOYY...",
], {"Y": hexc("#ffe890"), "O": hexc("#ffb050"), "R": hexc("#f06a3a")}, 8, 12)
fire.fill({(x, 25) for x in range(12, 32)} | {(x, 26) for x in range(10, 34)}, hexc("#8a5a38"))
fire.fill({(x, 27) for x in range(14, 30)}, hexc("#6e4228"))
paste(img, fire, HX - 20, HY - 34)

# lantern posts
for lx in (218, 424, 22, 606):
    glow(img, lx + 4, GROUND + 6, 26, 20, 0.45, WARM)
    paste(img, lantern(40), lx, GROUND - 22)

# snowman to the right of the hearth
sm = Sprite(40, 60)
sm.blob(ellipse(19.5, 44, 15, 13), [SNOW[0], SNOW[1], SNOW[2], SNOW[3]], SNOW_OUT, cuts=(-0.3, 0.25, 0.65))
sm.blob(ellipse(19.5, 25, 11, 10), [SNOW[0], SNOW[1], SNOW[2], SNOW[3]], SNOW_OUT, cuts=(-0.3, 0.25, 0.65))
sm.blob(ellipse(19.5, 11, 8, 7.5), [SNOW[0], SNOW[1], SNOW[2], SNOW[3]], SNOW_OUT, cuts=(-0.3, 0.25, 0.65))
# hat
sm.blob(rect(13, 0, 13, 5), [hexc("#6a6aa0"), hexc("#4a4a80"), hexc("#34346a")], hexc("#22224a"), cuts=(-0.2, 0.5))
sm.fill({(x, 5) for x in range(10, 30)}, hexc("#22224a"))
sm.fill({(x, 4) for x in range(14, 25)}, hexc("#e0474c"))
# face
for (x, y) in ((16, 9), (22, 9)):
    sm.set(x, y, hexc("#34304a"))
sm.fill({(19, 12), (20, 12), (21, 12), (22, 13)}, hexc("#f0883a"))
sm.set(19, 11, hexc("#ffb060"))
for x in (16, 18, 20, 22):
    sm.set(x, 15 + (1 if x in (18, 20) else 0), hexc("#5a5070"))
# scarf
sm.fill({(x, y) for x in range(11, 29) for y in (17, 18)}, hexc("#3f9a7a"))
sm.fill({(x, y) for x in range(22, 26) for y in range(19, 26)}, hexc("#3f9a7a"))
sm.fill({(x, 17) for x in range(11, 29, 3)} | {(22, 23), (23, 23), (24, 23), (25, 23)}, hexc("#8ad0b0"))
# buttons and twig arms
for y in (22, 27, 32):
    sm.set(19, y, hexc("#34304a"))
    sm.set(20, y, hexc("#34304a"))
for i in range(8):
    sm.set(8 - i, 24 - i // 2, hexc("#7a4a2e"))
    sm.set(31 + i, 24 - i // 2, hexc("#7a4a2e"))
sm.set(3, 19, hexc("#7a4a2e"))
sm.set(36, 19, hexc("#7a4a2e"))
paste(img, sm, 452, 340)
d.ellipse([452, 394, 492, 402], fill=SNOW[2])

# a little stack of presents by the tree
for (bx, by, bw, bh, c) in ((252, 316, 14, 12, "#e0474c"), (266, 320, 12, 9, "#4e8ab8"), (374, 318, 12, 10, "#ffd24a")):
    d.rectangle([bx, by, bx + bw, by + bh], fill=hexc(c), outline=mix(hexc(c), hexc("#2a2040"), 0.55))
    d.line([bx + bw // 2, by, bx + bw // 2, by + bh], fill=hexc("#fff4e8"))
    d.line([bx, by + bh // 2, bx + bw, by + bh // 2], fill=hexc("#fff4e8"))
    d.line([bx + 1, by, bx + bw - 1, by], fill=SNOW[0])

snowfall(img, R, 560, (0, 30, W, H))
haze(img, hexc("#eeeaf8"), 0.06)

img = save_bg(img, "hearthstone_square")
mock(img, "hearthstone_square", "hearthstone_square")
