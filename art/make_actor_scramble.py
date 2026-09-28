"""Scramble: a shaggy white mountain goat ice-climber with curled horns,
goggles pushed up, a rope coil on her shoulder and a pickaxe handle to chew."""
import math

from pixelkit import hexc, ellipse, edge, rect
from portraitkit import new, poly, curve, eye, blush, clip, finish, fuzz, GLINT

S = new()

FUR = [hexc("#ffffff"), hexc("#eef0f6"), hexc("#d4d6e4"), hexc("#b0b2c8")]
F_OUT = hexc("#54567a")
HORN = [hexc("#f0e2c4"), hexc("#ccb48c"), hexc("#a48a64"), hexc("#7e6848")]
HN_OUT = hexc("#3e3020")
JACKET = [hexc("#9ae0d8"), hexc("#4ab8b0"), hexc("#2e8c8c"), hexc("#226a6e")]
J_OUT = hexc("#0e3638")
ROPE = [hexc("#ffc090"), hexc("#f07048"), hexc("#c0443a"), hexc("#94303a")]
RP_OUT = hexc("#521820")
STRAP = [hexc("#c8a0f0"), hexc("#9a6ad0"), hexc("#7048a8")]
ST_OUT = hexc("#2e1a52")
LENS = [hexc("#e0fcff"), hexc("#7ad8f0"), hexc("#3e98c8"), hexc("#2a6a9c")]
RIM = hexc("#2e1a52")
NOSE = hexc("#8a6a80")
MOUTH = hexc("#54567a")
WOOD = [hexc("#f0c488"), hexc("#d0924e"), hexc("#a8683a"), hexc("#7e4a2a")]
WOOD_OUT = hexc("#4a2a1c")
STEEL = [hexc("#e4eef8"), hexc("#a8bcd4"), hexc("#7890b0"), hexc("#566a8c")]
STEEL_OUT = hexc("#27304a")


def pickaxe(S, base, top, half=11.0, bend=4.0, thick=2.4, hw=1.4):
    """A pickaxe like the good's icon: handle from base to top, curved head at top."""
    L = math.hypot(top[0] - base[0], top[1] - base[1])
    D = ((top[0] - base[0]) / L, (top[1] - base[1]) / L)
    N = (-D[1], D[0])

    def frame(x, y):
        dx, dy = x + 0.5 - base[0], y + 0.5 - base[1]
        return dx * D[0] + dy * D[1], dx * N[0] + dy * N[1]

    def region(test):
        return {(x, y) for y in range(64) for x in range(64) if test(*frame(x, y))}

    def hc(v):
        t = min(1.0, abs(v) / half)
        return L - bend * t * t

    handle = region(lambda u, v: 0 <= u <= L and abs(v) <= hw)
    head = region(lambda u, v: abs(v) <= half and
                  abs(u - hc(v)) <= thick * (1 - min(1, abs(v) / half) ** 1.6) + 0.55)
    collar = region(lambda u, v: L - 2.8 <= u <= L + 1.8 and abs(v) <= hw + 1.2)
    S.blob(handle, WOOD, WOOD_OUT, lx=0.6, ly=0.6)
    S.blob(head, STEEL, STEEL_OUT, lx=0.65, ly=0.65, cuts=(-0.4, 0.15, 0.6))
    S.blob(collar, STEEL[1:], STEEL_OUT, lx=0.6, ly=0.6, cuts=(-0.2, 0.4))
    for (x, y) in head - edge(head):
        u, v = frame(x, y)
        if u - hc(v) > 0.5 and abs(v) < half - 2.5:
            S.set(x, y, STEEL[0])
    return handle


# puffy climbing jacket
jacket = clip(ellipse(32, 64, 28, 13))
S.blob(jacket, JACKET, J_OUT, cuts=(-0.5, 0.2, 0.7))
for y in (56, 60):   # puffer quilting
    for x in range(64):
        if (x, y) in jacket and (x, y) not in edge(jacket):
            S.set(x, y, JACKET[3] if x > 32 else JACKET[2])
for y in range(52, 64):   # zip
    S.set(32, y, J_OUT)

# rope coil slung over her shoulder
for i, (dx, dy, rx, ry) in enumerate(((0, 0, 9.5, 7), (2, -1, 9, 6.5), (4, -2, 8.5, 6))):
    cx, cy = 13 + dx, 56 + dy
    loop = ellipse(cx, cy, rx, ry) - ellipse(cx, cy, rx - 2.6, ry - 2.6)
    S.blob(loop, ROPE, RP_OUT, cuts=(-0.5, 0.3, 0.8), center=(cx, cy))


# curling horns, sweeping back and out
for side in (-1, 1):
    pts = [(32 + side * 6, 22), (32 + side * 9, 13), (32 + side * 15, 8),
           (32 + side * 20, 10), (32 + side * 21, 15)]
    horn = curve(pts[:3], width=7.5) | curve(pts[2:], width=5)
    S.blob(horn, HORN, HN_OUT, cuts=(-0.4, 0.2, 0.7))
    for i, (x, y) in enumerate(curve(pts[:4], width=1)):
        if i % 3 == 0 and (x, y) in horn - edge(horn):
            S.set(x, y, HORN[3])

# floppy sideways ears
for side in (-1, 1):
    ear = ellipse(32 + side * 17, 30, 6.5, 3)
    S.blob(ear, FUR, F_OUT, cuts=(-0.2, 0.5))
    S.set(32 + side * 18, 30, hexc("#f6b0b8"))
    S.set(32 + side * 17, 30, hexc("#f6b0b8"))

# long shaggy head
head = fuzz(ellipse(32, 31, 13, 11) | ellipse(32, 40, 10, 8), period=3)
S.blob(head, FUR, F_OUT, cuts=(-0.5, 0.25, 0.75), center=(32, 34))
for (x, y) in ((27, 38), (36, 39), (29, 42), (35, 43)):   # tufts
    S.set(x, y, FUR[2])

# little beard
beard = fuzz(poly([(27, 46), (37, 46), (35, 54), (32, 57), (29, 54)]), period=2)
S.blob(beard, FUR, F_OUT, cuts=(-0.3, 0.4, 0.8))

# goggles pushed up on the forehead
strap = rect(19, 20, 27, 3)
S.blob(strap, STRAP, ST_OUT, cuts=(-0.2, 0.5))
for cx in (26, 38):
    lens = ellipse(cx, 21, 5, 4)
    S.blob(lens, LENS, RIM, cuts=(-0.4, 0.2, 0.7))
    S.set(cx - 2, 22, GLINT)
    S.set(cx - 1, 21, GLINT)

# face
eye(S, 25, 29, 3, 3)
eye(S, 37, 29, 3, 3)
S.set(26, 32, hexc("#2a1a2e"))
S.set(38, 32, hexc("#2a1a2e"))
for x in (29, 35):
    S.set(x, 39, NOSE)
    S.set(x, 40, NOSE)
blush(S, 21, 35)
blush(S, 41, 35)

# pickaxe handle stuck in her mouth, being chewed, head poking out to the right
handle = pickaxe(S, (28, 44.5), (56, 39), half=11, bend=3.5, thick=3.4, hw=1.4)
for (x, y) in ((28, 43), (29, 43), (28, 45)):   # bite marks
    S.set(x, y, WOOD_OUT)
for x in range(27, 37):   # lips over the handle
    if (x, 44) not in handle:
        S.set(x, 44, MOUTH)
S.set(26, 43, MOUTH)
S.set(37, 43, MOUTH)

finish(S, "scramble")
