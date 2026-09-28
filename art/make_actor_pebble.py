"""Pebble: a tiny cave golem of blue-grey stone with glowing eyes, crystal
clusters growing out of his head and shoulder like moss, and a little moss too."""
import math

from pixelkit import hexc, ellipse, edge
from portraitkit import new, poly, blush, clip, finish, fuzz, W, H, GLINT

S = new()

STONE = [hexc("#b8c4d4"), hexc("#8e9cb4"), hexc("#6c7a96"), hexc("#525e7a")]
ST_OUT = hexc("#262c44")
CRACK = hexc("#44506c")
MOSS = [hexc("#b8e080"), hexc("#86c060"), hexc("#5a9848")]
M_OUT = hexc("#24461c")
GLOW = [hexc("#ffffff"), hexc("#bff4ff"), hexc("#6cd8f0")]
ICE = [hexc("#f4fcff"), hexc("#c4e8fa"), hexc("#8cc4ee"), hexc("#6a94d8")]
VIO = [hexc("#f0e8ff"), hexc("#c8b8f4"), hexc("#9a84dc"), hexc("#7462bc")]
C_OUT = hexc("#3a2c6a")
BLUSH_S = hexc("#d898b0")


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


# chunky boulder shoulders
body = clip(poly([(4, 64), (6, 54), (12, 49), (24, 47), (40, 47), (52, 49), (58, 54), (60, 64)]))
S.blob(body, STONE, ST_OUT, cuts=(-0.45, 0.2, 0.7))
for pts in (((14, 55), (17, 58), (16, 61)), ((46, 56), (49, 58))):   # cracks
    for (x, y) in pts:
        S.set(x, y, CRACK)

# crystals on the left shoulder (behind nothing, in front of body)
draw_shard(shard(12, 53, -30, 2.4, 10, 4), VIO)
draw_shard(shard(15, 52, -8, 3, 13, 4), ICE)

# boulder head
head = poly([(17, 24), (22, 19), (42, 19), (47, 24), (48, 40), (44, 46), (20, 46), (16, 40)])
S.blob(head, STONE, ST_OUT, cuts=(-0.45, 0.2, 0.7))
for (x, y) in ((21, 27), (22, 28), (22, 29), (43, 35), (44, 36), (42, 41), (43, 42)):   # cracks
    S.set(x, y, CRACK)
S.set(21, 22, GLINT)
S.set(22, 21, STONE[0])

# crystal cluster sprouting from the crown
for bx, ang, w, ln, ramp in ((25, -34, 2.6, 11, VIO), (39, 30, 2.6, 12, VIO),
                              (35, 10, 3.0, 15, ICE), (29, -8, 3.6, 18, ICE)):
    draw_shard(shard(bx, 22, ang, w, ln, 5), ramp)
S.set(28, 9, GLINT)
S.set(28, 10, GLINT)

# moss tufts on the head and right shoulder
for m in (fuzz(ellipse(41, 21, 5, 2.2), period=2), fuzz(ellipse(50, 50, 6, 2.4), period=2)):
    S.blob(m, MOSS, M_OUT, cuts=(-0.2, 0.5))

# glowing eyes
for ex in (23, 36):
    for (x, y) in ((ex - 1, 30), (ex - 1, 33), (ex + 4, 30), (ex + 4, 33), (ex, 28), (ex + 3, 28), (ex, 35), (ex + 3, 35)):
        S.set(x, y, STONE[0])   # faint glow on the stone around each eye
    for dy in range(-1, 5):
        for dx in range(4):
            if dy in (-1, 4) and dx in (0, 3):
                continue
            S.set(ex + dx, 29 + dy, GLOW[2] if dy >= 3 or dx == 3 else GLOW[1])
    S.set(ex, 29, GLOW[0])
    S.set(ex + 1, 29, GLOW[0])
    S.set(ex, 30, GLOW[0])

# small content mouth
S.set(30, 38, ST_OUT)
S.set(31, 39, ST_OUT)
S.set(32, 39, ST_OUT)
S.set(33, 38, ST_OUT)
blush(S, 19, 37, BLUSH_S)
blush(S, 43, 37, BLUSH_S)

finish(S, "pebble")
