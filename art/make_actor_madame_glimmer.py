"""Madame Glimmer: an arctic fox fortune teller in a rose headscarf trimmed
with gold coins and a crystal gem, a gold hoop earring, a teal shawl, and a
(slightly cracked) crystal ball in front of her."""
from pixelkit import hexc, ellipse, edge
from portraitkit import new, poly, line, eye, blush, clip, finish, fuzz, GLINT, EYE_DARK

S = new()

FUR = [hexc("#ffffff"), hexc("#eef2fa"), hexc("#cdd6ea"), hexc("#a8b4d0")]
F_OUT = hexc("#48547a")
EAR_IN = hexc("#f4b8c8")
SCARF = [hexc("#ff9ab8"), hexc("#e8507e"), hexc("#bc3466"), hexc("#8e2450")]
SC_OUT = hexc("#4a0e2a")
SHAWL = [hexc("#7ad8c8"), hexc("#3aa89c"), hexc("#2a8080"), hexc("#1e6064")]
SW_OUT = hexc("#0e3438")
GOLD = [hexc("#fff0a0"), hexc("#ffd24a"), hexc("#d89a2c")]
G_OUT = hexc("#6a4414")
BALL = [hexc("#f4fcff"), hexc("#c4e8fa"), hexc("#8cc4ee"), hexc("#6a94d8")]
B_OUT = hexc("#3a2c6a")
MIST = hexc("#c8b8f4")

# teal shawl with a coin fringe
shawl = clip(ellipse(32, 66, 28, 14))
S.blob(shawl, SHAWL, SW_OUT, cuts=(-0.5, 0.2, 0.7))
for x in range(9, 56, 4):
    y = 55 + abs(x - 32) // 6
    if (x, y) in shawl:
        S.set(x, y, GOLD[1])
        S.set(x, y + 1, GOLD[2])

# big ears (behind the scarf, poking out on top)
for side in (-1, 1):
    ear = poly([(32 + side * 4, 22), (32 + side * 18, 27), (32 + side * 18, 5)])
    S.blob(ear, FUR, F_OUT, cuts=(-0.2, 0.4, 0.8))
    inner = poly([(32 + side * 9, 21), (32 + side * 15.5, 23), (32 + side * 16, 10)]) - edge(ear)
    S.fill(inner, EAR_IN)

# heart-shaped fox face with cheek ruffs, tapering to a pointed snout
face = ellipse(32, 32, 15, 11) | poly([(17, 32), (47, 32), (54, 40), (46, 40), (49, 44), (40, 45),
                                          (34, 50), (30, 50), (24, 45), (15, 44), (18, 40), (10, 40)])
S.blob(face, FUR, F_OUT, cuts=(-0.35, 0.3, 0.75), center=(32, 34))
muzzle = poly([(25, 41), (39, 41), (34, 49), (30, 49)]) - edge(face)
S.fill(muzzle - {(x, y) for (x, y) in muzzle if x > 34}, FUR[0])
for (x, y) in ((16, 41), (19, 42), (48, 41), (45, 42)):   # fluff tufts
    S.set(x, y, FUR[2])

# rose headscarf over the crown, knotted at the side
scarf = ellipse(32, 29, 16, 11) & {(x, y) for x in range(64) for y in range(0, 30)}
S.blob(scarf, SCARF, SC_OUT, cuts=(-0.4, 0.25, 0.7))
for x in range(22, 44, 4):   # polka dots
    S.set(x, 23 if x % 8 else 25, SCARF[0])
knot = ellipse(48, 29, 3.4, 3) | poly([(48, 29), (54, 33), (52, 38), (49, 32)])
S.blob(knot, SCARF, SC_OUT, cuts=(-0.2, 0.5))
for x in range(18, 47, 3):   # coin trim
    S.set(x, 29, GOLD[1])
    S.set(x + 1, 29, GOLD[2])
S.set(23, 22, GLINT)
S.set(24, 21, GLINT)
# crystal gem on the brow
gem = {(32, 24), (31, 25), (32, 25), (33, 25), (31, 26), (32, 26), (33, 26), (32, 27)}
S.outline_around(gem, G_OUT)
S.fill(gem, BALL[2])
S.set(31, 25, BALL[0])
S.set(32, 24, BALL[1])

# gold hoop earring hanging below the scarf
for p in ((16, 31), (15, 32), (15, 33), (15, 34), (16, 35), (17, 35), (18, 34)):
    S.set(*p, GOLD[1])
S.set(15, 32, GOLD[0])

# mysterious eyes with a flick of lash at the outer corners
IRIS = hexc("#5aa8e0")
for ex in (23, 37):
    eye(S, ex, 32, 4, 5)
    S.set(ex + 1, 35, IRIS)
    S.set(ex + 2, 35, IRIS)
    S.set(ex + 2, 34, IRIS)
S.set(22, 32, F_OUT)
S.set(21, 31, F_OUT)
S.set(41, 32, F_OUT)
S.set(42, 31, F_OUT)
# pointy snout: nose at the tip, sly smile
nose = ellipse(32, 44, 2.4, 1.6)
S.fill(nose, EYE_DARK)
S.set(31, 43, GLINT)
for p in ((32, 46), (31, 47), (30, 46), (33, 47), (34, 46)):
    S.set(*p, F_OUT)
blush(S, 20, 39)
blush(S, 42, 39)

# the crystal ball on a gold stand, with a little crack and some mist
stand = poly([(24, 64), (40, 64), (37, 59), (27, 59)])
S.blob(stand, GOLD, G_OUT, cuts=(-0.3, 0.4))
ball = ellipse(32, 53, 8, 7.5)
S.blob(ball, BALL, B_OUT, cuts=(-0.45, 0.1, 0.6))
for p in ((28, 54), (29, 55), (30, 54), (31, 55), (30, 53), (34, 56), (35, 57), (33, 57)):
    S.set(*p, MIST)
for p in ((36, 48), (35, 49), (36, 50), (35, 51)):   # crack
    S.set(*p, B_OUT)
S.set(28, 49, GLINT)
S.set(29, 48, GLINT)
S.set(28, 50, GLINT)
# paws cupping the ball
for cx in (23, 41):
    paw = ellipse(cx, 56, 3.6, 3.2)
    S.blob(paw, FUR, F_OUT, cuts=(-0.3, 0.4))

finish(S, "madame_glimmer")
