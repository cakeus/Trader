"""Yuki: a big, shy yeti with shaggy blue-white fur, little horns, a pale
blue face and very pink cheeks, squeezing a music box to his chest."""
from pixelkit import hexc, ellipse, edge, rect
import math

from portraitkit import new, poly, line, eye, blush, clip, finish, GLINT


def cloud(cx, cy, rx, ry, n, r, a0=0.0, a1=2 * math.pi):
    """Ellipse with a scalloped, shaggy rim of n small bumps between angles a0..a1."""
    m = ellipse(cx, cy, rx, ry)
    for i in range(n):
        a = a0 + (a1 - a0) * (i + 0.5) / n
        m |= ellipse(cx + math.cos(a) * rx, cy + math.sin(a) * ry, r, r)
    return m

S = new()

FUR = [hexc("#ffffff"), hexc("#e2ecfa"), hexc("#bccfe8"), hexc("#94aad2")]
F_OUT = hexc("#44548a")
SKIN = [hexc("#b8c6e2"), hexc("#98a8d0"), hexc("#7c8cbc")]
HORN = [hexc("#fff8e8"), hexc("#ecdcc0"), hexc("#c8b494")]
HN_OUT = hexc("#6a5a44")
WOOD = [hexc("#e8a86a"), hexc("#c07a44"), hexc("#98572e"), hexc("#733c22")]
WOOD_OUT = hexc("#48241a")
GOLD = [hexc("#fff4b0"), hexc("#ffd24a"), hexc("#d89a2a"), hexc("#a8701e")]
GOLD_OUT = hexc("#6a4418")
BLUSH_Y = hexc("#f48aa0")
NOTE = hexc("#7462bc")

# huge shaggy shoulders
body = clip(cloud(32, 68, 27, 20, 12, 3.2, math.pi, 2 * math.pi))
S.blob(body, FUR, F_OUT, cuts=(-0.5, 0.15, 0.6))

# little horns
for (pts, gx) in (([(16, 17), (12, 7), (15, 5), (23, 14)], 12), ([(48, 17), (52, 7), (49, 5), (41, 14)], 52)):
    horn = poly(pts)
    S.blob(horn, HORN, HN_OUT, cuts=(-0.2, 0.5))
    for dy in (9, 12):   # ridges
        for p in line(gx - 3, dy, gx + 3, dy + 1):
            if p in horn and p not in edge(horn):
                S.set(*p, HORN[2])

# big shaggy head
head = cloud(32, 29, 18, 15, 16, 3.2)
S.blob(head, FUR, F_OUT, cuts=(-0.5, 0.2, 0.7))
for (x, y) in ((20, 16), (24, 13), (40, 14), (44, 17), (16, 30), (48, 32), (18, 38)):   # shaggy tufts
    S.set(x, y, FUR[2])
    S.set(x + 1, y + 1, FUR[2])
# fringe of fur flopping over the face
face = ellipse(32, 32, 12, 9.5)
S.blob(face, SKIN, F_OUT, cuts=(-0.4, 0.3))
fringe = (poly([(19, 27), (24, 21), (32, 19), (40, 21), (45, 27), (40, 25), (36, 27), (32, 24), (28, 27), (24, 25)]))
S.blob(fringe, FUR, F_OUT, cuts=(-0.4, 0.3, 0.75))
S.set(22, 14, GLINT)
S.set(23, 13, GLINT)

# shy eyes glancing to the side, eyebrows worried
eye(S, 25, 29, 3, 4)
eye(S, 36, 29, 3, 4)
# wobbly little mouth
for (x, y) in ((29, 37), (30, 36), (31, 37), (32, 36), (33, 37), (34, 36)):
    S.set(x, y, F_OUT)
# big blush
for bx in (21, 39):
    for (dx, dy) in ((0, 0), (1, 0), (2, 0), (1, 1), (0, 1), (2, 1)):
        S.set(bx + dx, 34 + dy, BLUSH_Y)
S.set(22, 34, hexc("#ffc4d0"))
S.set(40, 34, hexc("#ffc4d0"))

# music box squeezed to his chest (closed lid, key on the side)
BX, BY = 22, 46
lid = rect(BX, BY, 20, 4)
S.blob(lid, WOOD, WOOD_OUT, lx=0.9, cuts=(-0.4, 0.3, 0.7))
box = rect(BX, BY + 4, 20, 10)
S.blob(box, WOOD, WOOD_OUT, lx=0.9, cuts=(-0.45, 0.25, 0.7))
for x in range(BX + 1, BX + 19):
    S.set(x, BY + 4, GOLD[1] if x < BX + 10 else GOLD[2])
    S.set(x, BY + 2, GOLD[2] if x % 2 else GOLD[1])
plate = rect(BX + 8, BY + 6, 4, 4)
S.blob(plate, GOLD, GOLD_OUT, cuts=(-0.1, 0.5))
S.set(BX + 9, BY + 7, GOLD[0])
S.set(BX + 10, BY + 8, WOOD_OUT)
S.set(BX + 1, BY + 1, GLINT)

# fluffy arms wrapped round it
for (cx, sgn) in ((19, 1), (45, -1)):
    arm = cloud(cx, 55, 6, 5.5, 5, 2.4)
    S.blob(arm, FUR[1:], F_OUT, cuts=(-0.4, 0.4))
    for (dx, dy) in ((0, 0), (2, 1), (4, 0)):   # fingers pressing in
        S.set(cx + sgn * 3 + dx - 2, 52 + dy, FUR[3])

# a squeezed-out note
S.rows(["..OO", "..OO", "..O.", "..O.", "OOO.", "OO.."], {"O": NOTE}, 55, 40)
S.set(55, 44, hexc("#b8a8f0"))

finish(S, "yuki")
