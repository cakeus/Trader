"""32x32 tools icon: a claw hammer lying on the diagonal (head upper-right)."""
import math

from pixelkit import Sprite, hexc, edge

W = H = 32
S = Sprite(W, H)

WOOD = [hexc("#f0c488"), hexc("#d0924e"), hexc("#a8683a"), hexc("#7e4a2a")]
WOOD_OUT = hexc("#4a2a1c")
STEEL = [hexc("#eef3f8"), hexc("#bac6d2"), hexc("#8a98aa"), hexc("#5e6a7c")]
STEEL_OUT = hexc("#2c3444")
GRIP = [hexc("#ff8a7a"), hexc("#e0474c"), hexc("#a83040")]
GLINT = hexc("#ffffff")

# axis along the handle (pointing to upper-right) and its normal
D = (1 / math.sqrt(2), -1 / math.sqrt(2))
N = (1 / math.sqrt(2), 1 / math.sqrt(2))
BASE = (6.0, 26.0)  # butt of the handle


def frame(x, y):
    """(u, v): u along the handle from the butt, v across it."""
    dx, dy = x + 0.5 - BASE[0], y + 0.5 - BASE[1]
    return dx * D[0] + dy * D[1], dx * N[0] + dy * N[1]


def region(test):
    return {(x, y) for y in range(H) for x in range(W) if test(*frame(x, y))}


handle = region(lambda u, v: -0.5 <= u <= 22 and abs(v) <= 2.6)
grip = region(lambda u, v: -0.5 <= u <= 8 and abs(v) <= 3.1)
# head: a bar across the top of the handle; the face (v < 0) is blunt, the claw (v > 0) tapers
head = region(lambda u, v: 17.5 <= u <= 26 and -9 <= v <= 3.5) | region(
    lambda u, v: 3.5 < v <= 10.5 and 17.5 + (v - 3.5) * 0.6 <= u <= 26 - (v - 3.5) * 0.35)
claw_gap = region(lambda u, v: 7.5 < v <= 11 and 20.5 <= u <= 23)
head -= claw_gap

S.blob(handle, WOOD, WOOD_OUT, lx=0.6, ly=0.6)
S.blob(grip, GRIP, WOOD_OUT, lx=0.6, ly=0.6, cuts=(-0.2, 0.5))
# grip wrap lines
for (x, y) in grip - edge(grip):
    u, v = frame(x, y)
    if int(u) % 3 == 0:
        S.set(x, y, GRIP[2])
S.blob(head, STEEL, STEEL_OUT, lx=0.7, ly=0.6, cuts=(-0.35, 0.2, 0.6))

# glints: along the top of the head and on the handle
for (x, y) in head - edge(head):
    u, v = frame(x, y)
    if 24 <= u <= 25.2 and -7.5 <= v <= 1.5:
        S.set(x, y, STEEL[0])
for (x, y) in handle - edge(handle) - grip:
    u, v = frame(x, y)
    if v < -1.2 and 10 <= u <= 16:
        S.set(x, y, WOOD[0])

S.center()
S.save("tools", "goods")
