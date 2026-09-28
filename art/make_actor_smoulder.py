"""Smoulder: a chubby baby dragon (warm red-orange with a cream belly, stubby
horns and little wings) greedily hugging a crystal for her budget hoard, with
a happy puff of smoke."""
import math

from pixelkit import hexc, ellipse, edge
from portraitkit import new, poly, eye, blush, clip, finish, W, H, GLINT

S = new()

SCALE = [hexc("#ffb080"), hexc("#f07048"), hexc("#d04c3c"), hexc("#a8343a")]
SC_OUT = hexc("#5a1a24")
BELLY = [hexc("#fff4d0"), hexc("#ffe0a0"), hexc("#f0c078")]
BE_OUT = hexc("#8a4a2a")
HORN = [hexc("#fffae0"), hexc("#ffe49a"), hexc("#e8b860")]
HO_OUT = hexc("#7a4a1a")
WING = [hexc("#ffc890"), hexc("#f8a060"), hexc("#e07848")]
SMOKE = [hexc("#ffffff"), hexc("#e4e0ec"), hexc("#bcb6cc")]
SM_OUT = hexc("#6a6480")
ICE = [hexc("#f4fcff"), hexc("#c4e8fa"), hexc("#8cc4ee"), hexc("#6a94d8")]
VIO = [hexc("#f0e8ff"), hexc("#c8b8f4"), hexc("#9a84dc"), hexc("#7462bc")]
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


# little bat wings behind
for side in (-1, 1):
    pts = [(32 + side * 12, 50), (32 + side * 16, 44), (32 + side * 28, 30), (32 + side * 26, 39),
           (32 + side * 30, 42), (32 + side * 25, 46), (32 + side * 27, 51), (32 + side * 20, 54)]
    wing = poly(pts)
    S.blob(wing, WING, SC_OUT, cuts=(-0.3, 0.4))
    for t in range(1, 10):   # wing strut
        q = (32 + side * (16 + t * 11 // 10), 45 - t * 3 // 2)
        if q in wing and q not in edge(wing):
            S.set(*q, SCALE[2])

# chubby body with cream belly
body = clip(ellipse(32, 64, 21, 20))
S.blob(body, SCALE, SC_OUT, cuts=(-0.5, 0.2, 0.7))
belly = clip(ellipse(32, 66, 12, 18)) - edge(body)
S.blob(belly, BELLY, None, cuts=(-0.2, 0.6))
for y in (52, 55, 58, 61):   # belly bands
    for x in range(26, 39):
        if (x, y) in belly:
            S.set(x, y, BELLY[2])

# stubby horns
for side in (-1, 1):
    horn = poly([(32 + side * 6, 24), (32 + side * 13, 23), (32 + side * 15, 12), (32 + side * 11, 14), (32 + side * 8, 18)])
    S.blob(horn, HORN, HO_OUT, cuts=(-0.2, 0.5))

# round head with a spiky crest
for x0 in (28, 32):
    S.blob(poly([(x0, 21), (x0 + 4, 21), (x0 + 2, 16)]), SCALE, SC_OUT, cuts=(-0.2, 0.5))
head = ellipse(32, 32, 15, 12)
S.blob(head, SCALE, SC_OUT, cuts=(-0.5, 0.25, 0.75))
snout = ellipse(32, 38, 9, 5.4)
S.blob(snout, BELLY, BE_OUT, cuts=(-0.2, 0.6))
S.set(22, 25, GLINT)
S.set(23, 24, GLINT)

# big sparkly eyes
eye(S, 23, 28, 4, 5)
eye(S, 37, 28, 4, 5)
S.set(25, 31, GLINT)
S.set(39, 31, GLINT)
# nostrils + gleeful grin with a fang
S.set(29, 36, BE_OUT)
S.set(35, 36, BE_OUT)
for x in range(28, 37):
    S.set(x, 39, SC_OUT)
for x in range(29, 36):
    S.set(x, 40, hexc("#c84a5a"))
for x in range(30, 35):
    S.set(x, 41, SC_OUT)
S.set(29, 40, SC_OUT)
S.set(35, 40, SC_OUT)
S.set(30, 40, hexc("#ffffff"))
blush(S, 19, 35)
blush(S, 43, 35)

# happy smoke puffs from the nose
puff = ellipse(47, 20, 4, 3.4) | ellipse(52, 16, 3, 2.6) | ellipse(55, 11, 2.2, 2)
S.blob(puff, SMOKE, SM_OUT, cuts=(-0.2, 0.5))

# the crystal, hugged tight
for bx, ang, w, ln, ramp in ((26, -24, 3, 13, VIO), (38.5, 22, 3, 13, VIO), (32, 2, 5, 21, ICE)):
    draw_shard(shard(bx, 64, ang, w, ln, 6), ramp)
S.set(30, 46, GLINT)
S.set(30, 47, GLINT)
S.set(29, 48, GLINT)
for (cx, cy) in ((22, 56), (42, 56)):
    paw = ellipse(cx, cy, 4, 3.4)
    S.blob(paw, SCALE, SC_OUT, cuts=(-0.3, 0.4))
    S.set(cx + (2 if cx < 32 else -2), cy - 3, HORN[0])
# sparkles of glee
for (x, y) in ((12, 22), (11, 23), (13, 23), (12, 24), (18, 52)):
    S.set(x, y, hexc("#ffe07a"))

finish(S, "smoulder")
