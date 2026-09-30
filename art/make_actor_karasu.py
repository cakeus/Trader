"""Karasu: a tired salaryman crow who has missed the last train again.
Blue-black feathers with a sheen and a stray cowlick, heavy-lidded eyes with
bags under them, a big grey beak, a grey suit, a loosened plum tie, and a tiny
lucky cat peeking out of his breast pocket."""
from pixelkit import hexc, ellipse, edge, rect
from portraitkit import new, poly, line, blush, clip, finish, GLINT, EYE_DARK

S = new()

FEATH = [hexc("#6a7098"), hexc("#454a6e"), hexc("#30334e"), hexc("#23253a")]
FE_OUT = hexc("#121324")
SHEEN = hexc("#8a9ad0")
BEAK = [hexc("#a8acbc"), hexc("#7c8094"), hexc("#5a5e72"), hexc("#44475a")]
BK_OUT = hexc("#1e2030")
SUIT = [hexc("#aab0c0"), hexc("#868ca0"), hexc("#686e84"), hexc("#50556a")]
SU_OUT = hexc("#262a3a")
SHIRT = [hexc("#ffffff"), hexc("#eeeef4"), hexc("#d4d4e2")]
SH_OUT = hexc("#6a6a80")
TIE = [hexc("#c46a8a"), hexc("#9a4468"), hexc("#72304e")]
TI_OUT = hexc("#3a1428")
BAGS = hexc("#5a4a7a")
LID = hexc("#3a3e5e")
CAT = [hexc("#ffffff"), hexc("#f4ece0"), hexc("#dccab4")]
CA_OUT = hexc("#6a5048")
SWEAT = [hexc("#e8f6ff"), hexc("#a8d8f4")]

# suit shoulders
suit = clip(ellipse(32, 66, 28, 15))
S.blob(suit, SUIT, SU_OUT, cuts=(-0.5, 0.2, 0.7))
# shirt V and lapels
shirt = poly([(24, 50), (40, 50), (32, 64)])
S.blob(shirt, SHIRT, SH_OUT, cuts=(-0.3, 0.5))
for side in (-1, 1):
    lapel = poly([(32 + side * 8, 50), (32 + side * 12, 51), (32 + side * 3, 64), (32 + side * 1, 62)])
    S.blob(lapel, SUIT, SU_OUT, cuts=(-0.5, 0.2, 0.7), center=(28, 56))
# loosened tie, knot pulled down and a little askew
knot = poly([(30, 53), (35, 53), (34, 56), (31, 56)])
S.blob(knot, TIE, TI_OUT, cuts=(-0.3, 0.4))
blade = poly([(31, 56), (34, 56), (36, 63), (33, 64), (30, 62)])
S.blob(blade, TIE, TI_OUT, cuts=(-0.3, 0.4))
for (x, y) in ((32, 58), (33, 60), (34, 62)):
    S.set(x, y, TIE[0])
# collar points open
for (x, y) in ((27, 51), (28, 52), (37, 51), (36, 52)):
    S.set(x, y, SHIRT[0])
# breast pocket with a tiny lucky cat
pocket = rect(40, 57, 8, 7)
S.blob(pocket, SUIT[1:], SU_OUT, cuts=(-0.2, 0.5))
cat = ellipse(44, 55, 3.2, 2.8)
S.blob(cat, CAT, CA_OUT, cuts=(-0.3, 0.4))
for (x, y) in ((41, 52), (41, 53), (47, 52), (47, 53)):
    S.set(x, y, CA_OUT)
S.set(43, 55, EYE_DARK)
S.set(45, 55, EYE_DARK)
S.set(44, 56, hexc("#f07890"))
S.set(48, 54, CAT[1])   # little raised paw
S.set(48, 53, CA_OUT)
S.set(49, 54, CA_OUT)

# round crow head with a stray cowlick
# (head drawn on its own layer, then set down onto the collar)
body_layer = S
S = new()
head = ellipse(31, 33, 16, 15)
S.blob(head, FEATH, FE_OUT, cuts=(-0.5, 0.15, 0.65))
cow = poly([(29, 19), (32, 19), (35, 11), (33, 13)]) | poly([(31, 19), (34, 19), (40, 14), (36, 15)])
S.blob(cow, FEATH, FE_OUT, cuts=(-0.3, 0.3), center=(33, 14))
for (x, y) in ((22, 23), (23, 22), (24, 22), (21, 24), (20, 26)):
    S.set(x, y, SHEEN)
S.set(24, 21, GLINT)
# cheek feathers ruffled
for (x, y) in ((15, 37), (14, 38), (47, 37), (48, 38)):
    S.set(x, y, FE_OUT)

# tired, heavy-lidded eyes with bags
for ex in (20, 34):
    white = rect(ex, 30, 6, 3) - {(ex, 32), (ex + 5, 32)}
    S.fill(white, hexc("#ece8f4"))
    for x in range(ex, ex + 6):
        S.set(x, 29, LID)
        S.set(x, 28, FE_OUT)
    for (x, y) in ((ex + 2, 30), (ex + 3, 30), (ex + 2, 31), (ex + 3, 31), (ex + 2, 32), (ex + 3, 32)):
        S.set(x, y, EYE_DARK)
    S.set(ex + 2, 30, hexc("#8a88a8"))
    for x in range(ex + 1, ex + 5):
        S.set(x, 34, BAGS)

# big crow beak, pointing down to the right
beak = poly([(27, 35), (33, 34), (45, 40), (47, 43), (38, 43), (29, 41)])
S.blob(beak, BEAK, BK_OUT, cuts=(-0.3, 0.2, 0.7))
for (x, y) in line(30, 39, 44, 42):
    S.set(x, y, BK_OUT)
S.set(30, 36, GLINT)
S.set(31, 36, BEAK[0])
S.set(32, 36, BEAK[0])
S.set(33, 37, hexc("#2a2c3e"))   # nostril

# a sweat drop of fatigue
drop = {(50, 23), (50, 24), (49, 25), (50, 25), (51, 25), (49, 26), (50, 26), (51, 26), (50, 27)}
S.fill(drop, SWEAT[1])
S.set(49, 25, SWEAT[0])
S.outline_around(drop, hexc("#3a6a8a"))

S.shift(0, 3)
body_layer.px.update(S.px)
S = body_layer
finish(S, "karasu")
