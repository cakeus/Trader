"""Mortimer Mole: a velvety prospector mole in a yellow miner's helmet with a
lamp, pink star nose and squinty eyes, holding up a crystal with mild
disappointment (he was looking for worms)."""
import math

from pixelkit import hexc, ellipse, edge
from portraitkit import new, poly, line, blush, clip, finish, W, H, GLINT

S = new()

FUR = [hexc("#b4a4b0"), hexc("#8e7e8e"), hexc("#6e6072"), hexc("#554a5a")]
F_OUT = hexc("#2e2434")
SNOUT = [hexc("#ecc4c8"), hexc("#d49ca6"), hexc("#b07a88")]
STAR = [hexc("#ffb4c8"), hexc("#f07a9a"), hexc("#c85478")]
ST_OUT = hexc("#6a2440")
HELM = [hexc("#fff0a0"), hexc("#ffd24a"), hexc("#e8a22c"), hexc("#c07a1c")]
H_OUT = hexc("#6a4414")
LAMP = [hexc("#ffffff"), hexc("#fff6c0"), hexc("#ffe07a")]
VEST = [hexc("#d89a68"), hexc("#b0744a"), hexc("#8a5636"), hexc("#6a3e26")]
V_OUT = hexc("#3a2014")
SHIRT = [hexc("#b8d8f0"), hexc("#88b0d8"), hexc("#6a8cbc")]
SH_OUT = hexc("#2a3a5a")
CLAW = hexc("#f4e4dc")
VIO = [hexc("#f0e8ff"), hexc("#c8b8f4"), hexc("#9a84dc"), hexc("#7462bc")]
ICE = [hexc("#f4fcff"), hexc("#c4e8fa"), hexc("#8cc4ee"), hexc("#6a94d8")]
C_OUT = hexc("#3a2c6a")


def shard(bx, by, ang, w, length, tip):
    a = math.radians(ang)
    dx, dy = math.sin(a), -math.cos(a)
    nx, ny = -dy, dx
    cells = {}
    for y in range(H):
        for x in range(W):
            px, py = x + 0.5 - bx, y + 0.5 - by
            u = px * dx + py * dy
            v = px * nx + py * ny
            if u < -1 or u > length:
                continue
            half = w if u < length - tip else w * (length - u) / tip
            if abs(v) <= half:
                cells[(x, y)] = (v, half)
    return cells


def draw_shard(cells, ramp):
    e = edge(set(cells))
    for p, (v, half) in cells.items():
        if p in e:
            S.set(*p, C_OUT)
            continue
        f = v / max(0.5, half)
        S.set(*p, ramp[0] if f < -0.45 else ramp[1] if f < 0.1 else ramp[2] if f < 0.6 else ramp[3])


# shirt + vest
shirt = clip(ellipse(32, 65, 27, 14))
S.blob(shirt, SHIRT, SH_OUT, cuts=(-0.5, 0.3))
for side in (-1, 1):
    panel = clip(poly([(32 + side * 4, 52), (32 + side * 27, 60), (32 + side * 27, 64), (32 + side * 4, 64)]))
    S.blob(panel, VEST, V_OUT, cuts=(-0.4, 0.3, 0.75))
for y in (56, 60):   # buttons
    S.set(37, y, hexc("#ffd24a"))

# round velvety head
head = ellipse(32, 39, 17, 13.5)
S.blob(head, FUR, F_OUT, cuts=(-0.55, 0.2, 0.7))
for (x, y) in ((22, 33), (24, 30), (41, 31), (44, 35), (20, 40)):   # velvet sheen
    S.set(x, y, FUR[0])

# helmet dome + brim + lamp
dome = ellipse(32, 30, 14, 13) & {(x, y) for x in range(64) for y in range(0, 30)}
S.blob(dome, HELM, H_OUT, cuts=(-0.4, 0.3, 0.75))
brim = ellipse(32, 29.5, 19, 2.8)
S.blob(brim, HELM, H_OUT, cuts=(-0.3, 0.4, 0.8))
S.set(23, 23, GLINT)
S.set(24, 21, GLINT)
lamp = ellipse(32, 23, 4, 4)
S.blob(lamp, LAMP, H_OUT, cuts=(-0.2, 0.5))
S.set(30, 21, GLINT)
S.set(31, 21, GLINT)
for (x, y) in ((25, 13), (32, 11), (39, 13), (26, 12), (38, 12)):   # little light rays
    S.set(x, y, LAMP[2])

# squinty, unimpressed eyes: flat lids
for ex in (24, 37):
    for i in range(4):
        S.set(ex + i, 35, F_OUT)
    S.set(ex + 1, 36, F_OUT)
    S.set(ex + 2, 36, F_OUT)

# pale snout, pink star nose, little frown
snout = ellipse(32, 43, 8, 5)
S.blob(snout, SNOUT, FUR[3], cuts=(-0.2, 0.6))
star = ellipse(32, 41, 4, 3)
for p in ((27, 41), (37, 41), (32, 37), (28, 38), (36, 38), (28, 44), (36, 44)):   # star tendrils
    star.add(p)
S.blob(star, STAR, ST_OUT, cuts=(-0.2, 0.5))
S.set(30, 40, GLINT)
S.set(31, 39, GLINT)
for x in range(30, 35):
    S.set(x, 47, F_OUT)
S.set(29, 48, F_OUT)
S.set(35, 48, F_OUT)
blush(S, 20, 41)
blush(S, 43, 41)

# held-up crystal and a big digging paw
draw_shard(shard(48, 48, -28, 2.6, 11, 4), VIO)
draw_shard(shard(55, 48, 26, 2.6, 11, 4), VIO)
draw_shard(shard(51.5, 48, 4, 4.2, 18, 6), ICE)
S.set(49, 36, GLINT)
S.set(49, 37, GLINT)
S.set(50, 35, GLINT)
paw = ellipse(51.5, 50, 6, 4.2)
S.blob(paw, FUR, F_OUT, cuts=(-0.3, 0.4))
for cx in (47, 50, 53, 56):
    S.set(cx, 47, CLAW)
# a worm-less sigh of dust
for (x, y) in ((10, 44), (8, 42), (11, 41)):
    S.set(x, y, hexc("#c8b8a8"))

finish(S, "mortimer")
