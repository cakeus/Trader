"""32x32 straw hat: a wide woven brim seen from a little above, a rounded crown and a red
ribbon band with a bow trailing off the right side."""
from pixelkit import Sprite, hexc, ellipse, rect, edge

W = H = 32
S = Sprite(W, H)

STRAW = [hexc("#fff0b8"), hexc("#f5d27a"), hexc("#dcaa52"), hexc("#b27c36")]
STRAW_OUT = hexc("#6b4220")
WEAVE = hexc("#e6bb62")        # coil lines on the lit straw
WEAVE_DEEP = hexc("#a06c2e")   # coil lines in shade
RED = [hexc("#ff9a86"), hexc("#e8524a"), hexc("#b0343a")]
RED_OUT = hexc("#5e1c24")
GLINT = hexc("#fffbea")

CX = 15.5

# brim: a wide flat oval, coiled straw in rings
brim = ellipse(CX, 19.5, 15.0, 6.6)
S.blob(brim, STRAW, STRAW_OUT, lx=0.8, ly=0.5, cuts=(-0.55, 0.2, 0.7))
for (x, y) in brim - edge(brim):
    r = (((x - CX) / 15.0) ** 2 + ((y - 19.5) / 6.6) ** 2) ** 0.5
    if 0.62 < r < 0.72 or 0.86 < r < 0.94:
        c = S.get(x, y)
        S.set(x, y, WEAVE_DEEP if c in (STRAW[2], STRAW[3]) else WEAVE)

# crown: a rounded dome whose base follows the brim's curve
crown = {(x, y) for (x, y) in ellipse(CX, 13.0, 7.5, 5.6) if y <= 14}
crown |= {(x, y) for (x, y) in rect(8, 13, 16, 5) if 7.5 <= x <= 23.5}
crown |= {(x, y) for (x, y) in ellipse(CX, 17.0, 8.0, 2.6) if y >= 17}
S.blob(crown, STRAW, STRAW_OUT, lx=0.9, ly=0.35, cuts=(-0.6, 0.1, 0.6))
for (x, y) in crown - edge(crown):
    if y in (10, 12) and S.get(x, y) != STRAW[0]:
        c = S.get(x, y)
        S.set(x, y, WEAVE_DEEP if c in (STRAW[2], STRAW[3]) else WEAVE)

# ribbon band round the base of the crown
for (x, y) in crown - edge(crown):
    if 14 <= y <= 16 + (1 if abs(x - CX) < 5 else 0):
        t = (x - CX) / 8.0
        S.set(x, y, RED[0] if t < -0.55 else RED[2] if t > 0.45 else RED[1])

# bow on the right of the band, tails trailing over the brim
bow = {(21, 13), (22, 13), (21, 14), (22, 14), (23, 14), (24, 13), (25, 13), (24, 14), (25, 14),
       (25, 15), (23, 15), (22, 16), (22, 17), (24, 16), (24, 17), (25, 18), (21, 18)}
for (x, y) in bow:
    S.set(x, y, RED[2] if x >= 24 or y >= 17 else RED[1])
for (x, y) in ((21, 13), (24, 13)):
    S.set(x, y, RED[0])
S.set(23, 15, RED_OUT)  # the knot
for (x, y) in {(x + dx, y + dy) for (x, y) in bow for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - bow:
    if S.get(x, y) not in RED:
        S.set(x, y, RED_OUT)

# glints on the crown and the front of the brim, upper-left
for (x, y) in ((11, 9), (10, 10), (12, 8), (4, 19), (5, 18)):
    S.set(x, y, GLINT)

S.center()
S.save("straw_hat", "goods")
