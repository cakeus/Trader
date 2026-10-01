"""32x32 capsule toy: a gachapon capsule with a clear aqua top and a coral bottom, a tiny yellow
chick figure peeking through the clear half. No writing on it."""
from pixelkit import Sprite, hexc, ellipse, edge, mix

W = H = 32
S = Sprite(W, H)

CLEAR = [hexc("#d4f4f0"), hexc("#c8f0ec"), hexc("#9cd8da"), hexc("#78bcc8")]
CLEAR_OUT = hexc("#2e5a6a")
CORAL = [hexc("#ffb0a0"), hexc("#f6766e"), hexc("#d2505a"), hexc("#a0384a")]
CORAL_OUT = hexc("#5a1c30")
TINT = hexc("#9cd8da")
CHICK = [hexc("#fff4a0"), hexc("#ffd44a"), hexc("#e8a830")]
CHICK_OUT = hexc("#8a5a1e")
BEAK = hexc("#f28a3a")
EYE = hexc("#3a2a2a")
GLINT = hexc("#ffffff")

CX, CY, R = 15.5, 15.5, 12.4
ball = ellipse(CX, CY, R, R)
SEAM = 17  # first row of the coral half
top = {(x, y) for (x, y) in ball if y < SEAM}
bottom = {(x, y) for (x, y) in ball if y >= SEAM}

# clear dome, shaded for upper-left light around the whole ball
S.blob(ball, CLEAR, CLEAR_OUT, lx=0.6, ly=0.6, cuts=(-0.45, 0.15, 0.6))

# the chick figure inside, seen through the plastic (colors pulled toward the shell's tint)
def seen(c):
    return mix(c, TINT, 0.18)

chick = ellipse(15.5, 12.8, 4.4, 4.0)
S.blob(chick, [seen(c) for c in CHICK], seen(CHICK_OUT), lx=0.7, ly=0.6, cuts=(-0.35, 0.35, 0.9))
# tuft on top
for (x, y) in ((15, 7), (16, 7), (16, 8)):
    S.set(x, y, seen(CHICK_OUT))
S.set(15, 8, seen(CHICK[0]))
# eyes, beak and blush
S.set(14, 12, seen(EYE))
S.set(17, 12, seen(EYE))
S.set(15, 13, seen(BEAK))
S.set(16, 13, seen(BEAK))
S.set(16, 14, seen(hexc("#c8642a")))
for (x, y) in ((12, 14), (19, 14)):
    S.set(x, y, seen(hexc("#ff9a8a")))

# coral bottom half, with a lip along the seam that overlaps the clear half
S.blob(bottom, CORAL, CORAL_OUT, lx=0.6, ly=0.6, center=(CX, CY), cuts=(-0.6, 0.35, 0.8))
lip = [x for (x, y) in bottom if y == SEAM]
x0, x1 = min(lip), max(lip)
for x in range(x0, x1 + 1):
    S.set(x, SEAM - 1, CORAL_OUT)
    S.set(x, SEAM, CORAL[0] if x < 16 else CORAL[1])
    S.set(x, SEAM + 1, CORAL[2])
S.set(x0 - 1, SEAM, CORAL_OUT)
S.set(x1 + 1, SEAM, CORAL_OUT)
S.set(x0 - 1, SEAM + 1, CORAL_OUT)
S.set(x1 + 1, SEAM + 1, CORAL_OUT)
for x in (x0, x1):
    S.set(x, SEAM + 1, CORAL_OUT)

# glints: a curved streak on the dome, a dot beside it, and a soft one on the coral
for (x, y) in ((7, 11), (7, 10), (8, 9), (8, 8), (9, 7), (10, 6), (11, 6)):
    S.set(x, y, GLINT)
S.set(10, 9, GLINT)
for (x, y) in ((7, 20), (8, 21)):
    S.set(x, y, CORAL[0])
S.set(7, 19, GLINT)

S.center()
S.save("capsule_toy", "goods")
