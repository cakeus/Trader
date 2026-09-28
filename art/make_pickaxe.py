"""32x32 pickaxe: long wooden handle (butt lower-right), curved grey-blue steel head upper-left."""
import math

from pixelkit import Sprite, hexc, edge

W = H = 32
S = Sprite(W, H)

WOOD = [hexc("#f0c488"), hexc("#d0924e"), hexc("#a8683a"), hexc("#7e4a2a")]
WOOD_OUT = hexc("#4a2a1c")
STEEL = [hexc("#e4eef8"), hexc("#a8bcd4"), hexc("#7890b0"), hexc("#566a8c")]
STEEL_OUT = hexc("#27304a")
WRAP = [hexc("#8ab8c8"), hexc("#5a8aa0"), hexc("#3e6478")]

D = (-1 / math.sqrt(2), -1 / math.sqrt(2))    # along the handle, towards the head
N = (-1 / math.sqrt(2), 1 / math.sqrt(2))     # across it
BASE = (27.0, 28.0)


def frame(x, y):
    dx, dy = x + 0.5 - BASE[0], y + 0.5 - BASE[1]
    return dx * D[0] + dy * D[1], dx * N[0] + dy * N[1]


def region(test):
    return {(x, y) for y in range(H) for x in range(W) if test(*frame(x, y))}


L = 15.5


def head_center(v):
    t = min(1.0, abs(v) / L)
    return 24.5 - 7.0 * t * t                # the ends curve back towards the grip


def head_test(u, v):
    t = min(1.0, abs(v) / L)
    half = 2.8 * (1 - t ** 1.6) + 0.55
    return abs(v) <= L and abs(u - head_center(v)) <= half


handle = region(lambda u, v: -0.5 <= u <= 26 and abs(v) <= 2.2)
wrap = region(lambda u, v: 1.5 <= u <= 8 and abs(v) <= 2.7)
pommel = region(lambda u, v: -1 <= u <= 1.5 and abs(v) <= 2.7)
head = region(head_test)
collar = region(lambda u, v: 21 <= u <= 27.3 and abs(v) <= 3.4)

S.blob(handle, WOOD, WOOD_OUT, lx=0.6, ly=0.6)
S.blob(wrap, WRAP, WOOD_OUT, lx=0.6, ly=0.6, cuts=(-0.2, 0.5))
for (x, y) in wrap - edge(wrap):
    u, v = frame(x, y)
    if int(u) % 3 == 0:
        S.set(x, y, WRAP[2])
S.blob(pommel, WOOD, WOOD_OUT, lx=0.6, ly=0.6, cuts=(-0.1, 0.5))
S.blob(head, STEEL, STEEL_OUT, lx=0.65, ly=0.65, cuts=(-0.4, 0.15, 0.6))
S.blob(collar, [STEEL[1], STEEL[2], STEEL[3]], STEEL_OUT, lx=0.6, ly=0.6, cuts=(-0.2, 0.4))
# highlight along the head's outer edge, and on the handle
for (x, y) in head - edge(head):
    u, v = frame(x, y)
    if u - head_center(v) > 0.6 and abs(v) < L - 3 and v < 4:
        S.set(x, y, STEEL[0])
for (x, y) in handle - edge(handle) - wrap:
    u, v = frame(x, y)
    if v < -0.9 and 11 <= u <= 17:
        S.set(x, y, WOOD[0])

S.center()
S.save("pickaxe", "goods")
