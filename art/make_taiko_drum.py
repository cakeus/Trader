"""32x32 taiko drum: a round-bellied wooden barrel drum, skin head on top ringed with tacks,
a brass carrying ring, and two sticks (bachi) crossed over it."""
import math

from pixelkit import Sprite, hexc, ellipse, edge

W = H = 32
S = Sprite(W, H)

WOOD = [hexc("#e89a5a"), hexc("#c0663a"), hexc("#94462a"), hexc("#6a2e1e")]
WOOD_OUT = hexc("#3e1a14")
SKIN = [hexc("#fff6dc"), hexc("#f6e2b0"), hexc("#dcc08a")]
SKIN_OUT = hexc("#6e4a2a")
TACK = hexc("#3a2a2a")
TACK_HI = hexc("#fff0c0")
BRASS = [hexc("#ffe08a"), hexc("#e0a83a"), hexc("#a8702a")]
STICK = [hexc("#f0c488"), hexc("#d0924e"), hexc("#a8683a")]
STICK_OUT = hexc("#4a2a1c")
GLINT = hexc("#fff8ee")

CX, TOP, BOT, RX, RY = 15.5, 12.0, 26.0, 10.5, 4.2


def half(y):
    t = (y - TOP) / (BOT - TOP)
    return RX + 2.2 * math.sin(math.pi * max(0.0, min(1.0, t)))


barrel = ellipse(CX, BOT, RX, RY) | {(x, y) for y in range(int(TOP), int(BOT) + 1)
                                      for x in range(32) if abs(x + 0.0 - CX) <= half(y)}
S.blob(barrel, WOOD, WOOD_OUT, lx=1.0, ly=0.1, cuts=(-0.55, 0.05, 0.6), center=(CX, 19))
inner = barrel - edge(barrel)
# a lighter stave sheen on the left, and faint stave lines
for (x, y) in inner:
    if round(x - CX + half(y)) == 3:
        S.set(x, y, WOOD[0])
# rows of tacks just under the top head and just over the bottom
for (row, yy) in (("top", TOP + 3), ("bot", BOT + 0.5)):
    for x in range(32):
        dx = (x + 0.0 - CX)
        w = half(yy) - 1
        if abs(dx) <= w - 0.5 and x % 2 == 0:
            y = round(yy + RY * 0.55 * math.sqrt(max(0, 1 - (dx / (w + 1)) ** 2)) - 1)
            if (x, y) in inner:
                S.set(x, y, TACK)
                if dx < 0 and (x, y - 1) in inner:
                    S.set(x, y - 1, WOOD[0] if dx < -3 else WOOD[1])
# brass carrying ring on the belly
ring = ellipse(CX, 21.0, 2.7, 2.4) - ellipse(CX, 21.0, 1.2, 1.0)
for (x, y) in ring:
    if (x + 1, y + 1) not in ring:
        S.set(x + 1, y + 1, WOOD[3])
S.blob(ring, BRASS, None, lx=0.7, ly=0.7, cuts=(-0.3, 0.4))
for (x, y) in ((int(CX), 18), (int(CX) + 1, 18)):
    S.set(x, y, BRASS[2])
# skin head on top
head = ellipse(CX, TOP, RX, RY)
S.fill(head, WOOD_OUT)
skin = head - edge(head)
S.blob(skin, SKIN, SKIN_OUT, lx=0.7, ly=0.6, cuts=(-0.4, 0.4))
# two sticks crossed above the drum
def stick(x0, y0, x1, y1, r=1.3):
    m = set()
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy
    for y in range(32):
        for x in range(32):
            px, py = x + 0.5, y + 0.5
            t = max(0, min(1, ((px - x0) * dx + (py - y0) * dy) / L2))
            if (px - x0 - t * dx) ** 2 + (py - y0 - t * dy) ** 2 <= r * r:
                m.add((x, y))
    return m


for s in (stick(5.5, 11.5, 20.5, 1.5, 1.75), stick(26.5, 11.5, 11.5, 1.5, 1.75)):
    S.blob(s, STICK, STICK_OUT, lx=0.6, ly=0.6, cuts=(-0.2, 0.5))
# glints
for (x, y) in ((8, 11), (9, 10), (5, 16), (5, 17)):
    S.set(x, y, GLINT)

S.center()
S.save("taiko_drum", "goods")
