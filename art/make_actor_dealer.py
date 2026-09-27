"""Nox the Night Owl (the star Dealer): a plum-feathered owl with ear tufts,
big golden eyes, a tiny beak, and a midnight cloak dotted with gold stars,
clasped with a star brooch."""
from pixelkit import hexc, ellipse, edge
from portraitkit import new, poly, shiny_eye, blush, clip, finish, GLINT

S = new()

FEATHER = [hexc("#c8a8e0"), hexc("#9a78c0"), hexc("#7458a0"), hexc("#553e80")]
F_OUT = hexc("#2c1e48")
FACE = [hexc("#fbeedc"), hexc("#ecd6c0"), hexc("#d2b49c")]
FACE_OUT = hexc("#7a5a6a")
CLOAK = [hexc("#5a6ac8"), hexc("#3c4aa0"), hexc("#2c367c"), hexc("#20285c")]
C_OUT = hexc("#121838")
IRIS = [hexc("#fff4b0"), hexc("#ffd24a"), hexc("#e8a22c")]
BEAK = [hexc("#ffd49a"), hexc("#f0a04a"), hexc("#c0702c")]
B_OUT = hexc("#6a3a14")
GOLD = hexc("#ffd24a")
GOLD_D = hexc("#c08a1c")

# cloak over the shoulders, with gold stars
cloak = clip(ellipse(32, 67, 28, 15))
S.blob(cloak, CLOAK, C_OUT, cuts=(-0.5, 0.15, 0.7))
inside = cloak - edge(cloak)
for (sx, sy) in ((12, 59), (21, 63), (46, 58), (53, 63), (39, 62)):
    for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
        if (sx + dx, sy + dy) in inside:
            S.set(sx + dx, sy + dy, GOLD_D)
    S.set(sx, sy, GOLD)
S.set(16, 56, hexc("#fff4e4"))
S.set(28, 60, hexc("#fff4e4"))

# ear tufts (behind the head)
for pts in (((14, 26), (11, 9), (24, 19)), ((50, 26), (53, 9), (40, 19))):
    tuft = poly(list(pts))
    S.blob(tuft, FEATHER, F_OUT, cuts=(-0.3, 0.3, 0.7))

# round head
head = ellipse(32, 33, 20, 18) | ellipse(32, 50, 13, 6)
S.blob(head, FEATHER, F_OUT, cuts=(-0.4, 0.25, 0.7), center=(32, 34))
S.set(17, 24, GLINT)
S.set(18, 23, GLINT)

# heart-shaped pale face disc
face = ellipse(24, 34, 9, 10) | ellipse(40, 34, 9, 10) | ellipse(32, 42, 10, 7)
face = face & head
S.blob(face, FACE, FACE_OUT, cuts=(-0.2, 0.5))

# big golden eyes
shiny_eye(S, 24, 33, 5, IRIS, F_OUT)
shiny_eye(S, 40, 33, 5, IRIS, F_OUT)
for (cx) in (24, 40):
    for (x, y) in ((cx, 33), (cx + 1, 33), (cx, 34), (cx + 1, 34), (cx, 32), (cx + 1, 32)):
        S.set(x, y, hexc("#2a1a2e"))
    S.set(cx - 2, 31, GLINT)
    S.set(cx - 1, 30, GLINT)

# tiny beak
BEAK_ROWS = ["OOOOOO",
             "OLBBBO",
             ".OBBO.",
             ".OBSO.",
             "..OO.."]
S.rows(BEAK_ROWS, {"O": B_OUT, "L": BEAK[0], "B": BEAK[1], "S": BEAK[2]}, 29, 39)
blush(S, 17, 41)
blush(S, 45, 41)

# star brooch at the cloak clasp
star = {(32, 51), (31, 52), (32, 52), (33, 52), (30, 53), (31, 53), (32, 53), (33, 53), (34, 53),
        (31, 54), (32, 54), (33, 54), (31, 55), (33, 55)}
S.outline_around(star, B_OUT)
S.fill(star, GOLD)
S.set(31, 53, hexc("#fff4b0"))
S.set(32, 52, hexc("#fff4b0"))
S.set(33, 54, GOLD_D)

finish(S, "dealer")
