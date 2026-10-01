"""32x32 kimono: a summer cotton kimono (yukata-style) laid flat, indigo with little pink and
white blossoms, wide sleeves, a cream collar and a coral obi with a cord.

The wearer's left panel goes over the right (right over left is only for the dead), so seen
from the front the collar makes a "y": the long stroke runs from the upper right down to the
lower left, and the short one from the upper left meets it. No writing on it."""
from pixelkit import Sprite, hexc, rect, rounded_rect, edge

W = H = 32
S = Sprite(W, H)

INDIGO = [hexc("#7d8fe0"), hexc("#4c5cb4"), hexc("#36448c"), hexc("#28336c")]
INDIGO_OUT = hexc("#161a3c")
SEAM = hexc("#222b5e")
CREAM = [hexc("#fffbea"), hexc("#f0dcbc")]
OBI = [hexc("#ffb0b8"), hexc("#f2727e"), hexc("#c84a5e")]
OBI_OUT = hexc("#5e1c34")
CORD = hexc("#ffe08a")
PINK = hexc("#ffb6c8")
WHITE = hexc("#f4f0ff")
GLINT = hexc("#fffbea")

# wide sleeves hanging off each side, then the body in front of them
sleeves = rounded_rect(1, 4, 9, 14, r=2) | rounded_rect(22, 4, 9, 14, r=2)
sleeves |= rect(1, 4, 9, 3) | rect(22, 4, 9, 3)
S.blob(sleeves, INDIGO, INDIGO_OUT, lx=0.85, ly=0.35, cuts=(-0.55, 0.2, 0.7))
for y in range(5, 17):           # the seam where each sleeve meets the body
    S.set(9, y, SEAM)
    S.set(22, y, SEAM)

body = rect(9, 3, 14, 27) | {(x, 2) for x in range(11, 21)}
S.blob(body, INDIGO, INDIGO_OUT, lx=0.9, ly=0.25, cuts=(-0.6, 0.25, 0.75))

# blossoms scattered over the cloth: a pink 5-pixel flower or a single white dot
for (x, y) in ((4, 8), (6, 13), (26, 7), (28, 12), (11, 23), (19, 25), (13, 6), (20, 21)):
    if all(S.get(x + dx, y + dy) in INDIGO for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            S.set(x + dx, y + dy, PINK)
        S.set(x, y, WHITE)
for (x, y) in ((3, 15), (7, 6), (24, 15), (29, 9), (15, 27), (21, 28), (10, 27)):
    if S.get(x, y) in INDIGO:
        S.set(x, y, WHITE)

# collar: the short stroke from the upper left, then the long stroke (the top panel's edge)
# from the upper right down past the obi to the hem
for (x, y) in ((12, 2), (12, 3), (13, 4), (13, 5), (14, 6), (14, 7), (15, 8)):
    S.set(x, y, CREAM[1])
    S.set(x + 1, y, CREAM[1])
long_stroke = [(20, 2), (19, 3), (19, 4), (18, 5), (18, 6), (17, 7), (17, 8), (16, 9), (16, 10),
               (15, 11), (15, 12), (14, 13)]
for (x, y) in long_stroke:
    S.set(x, y, CREAM[0])
    S.set(x - 1, y, CREAM[0])
    S.set(x + 1, y, SEAM)        # shadow under the collar's edge
# the panel's edge below the obi
for y in range(19, 29):
    S.set(13, y, SEAM)
S.set(13, 29, INDIGO_OUT)

# obi: a wide coral sash with a yellow cord across it
obi = rect(9, 13, 14, 6)
S.blob(obi, OBI, OBI_OUT, lx=0.9, ly=0.3, cuts=(-0.6, 0.45))
for x in range(9, 23):
    S.set(x, 16, CORD)
S.set(16, 16, OBI_OUT)
S.set(17, 16, OBI_OUT)

# glints, upper-left
for (x, y) in ((2, 6), (3, 5), (10, 4)):
    S.set(x, y, GLINT)

S.center()
S.save("kimono", "goods")
