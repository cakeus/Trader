"""32x32 crystal cluster: pale blue/violet faceted shards on a little lavender rock."""
import math

from pixelkit import Sprite, hexc, ellipse, edge

W = H = 32
S = Sprite(W, H)

ICE = [hexc("#f4fcff"), hexc("#c4e8fa"), hexc("#8cc4ee"), hexc("#6a94d8")]
VIO = [hexc("#f0e8ff"), hexc("#c8b8f4"), hexc("#9a84dc"), hexc("#7462bc")]
OUT = hexc("#3a2c6a")
ROCK = [hexc("#b8aec8"), hexc("#948aa8"), hexc("#6e6688")]
ROCK_OUT = hexc("#3e3654")
GLINT = hexc("#ffffff")


def shard(bx, by, ang, w, length, tip):
    """Faceted prism from (bx, by) pointing at `ang` degrees (0 = up, + = right)."""
    a = math.radians(ang)
    dx, dy = math.sin(a), -math.cos(a)      # along
    nx, ny = -dy, dx                         # across (points right)
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
                cells[(x, y)] = (u, v, half)
    return cells


def draw(cells, ramp):
    m = set(cells)
    e = edge(m)
    for p, (u, v, half) in cells.items():
        if p in e:
            S.set(*p, OUT)
            continue
        f = v / max(0.5, half)
        c = ramp[0] if f < -0.45 else ramp[1] if f < 0.1 else ramp[2] if f < 0.6 else ramp[3]
        S.set(*p, c)
    return m


# rock base
rock = ellipse(16, 27, 12, 3.6)
S.blob(rock, ROCK, ROCK_OUT, cuts=(-0.2, 0.45))
shards = [
    (shard(8.5, 27, -32, 3.0, 13, 4), VIO),
    (shard(23.5, 27, 30, 3.0, 14, 4), VIO),
    (shard(19.5, 27.5, 12, 3.2, 17, 5), ICE),
    (shard(13.5, 28, -6, 4.2, 24, 6), ICE),
    (shard(10.5, 28.5, -55, 2.4, 8, 3), ICE),
]
for cells, ramp in shards:
    draw(cells, ramp)
# glints: a streak on the big shard's lit face, and a couple of sparkles
for (x, y) in ((11, 13), (11, 14), (12, 11), (11, 16)):
    S.set(x, y, GLINT)
for (x, y) in ((18, 16), (18, 17), (6, 20)):
    S.set(x, y, GLINT)
for (x, y) in ((25, 6), (24, 7), (26, 7), (25, 8), (3, 12)):
    S.set(x, y, hexc("#fff8d0"))
S.set(25, 7, GLINT)

S.center()
S.save("crystal", "goods")
