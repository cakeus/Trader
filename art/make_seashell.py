"""32x32 scallop seashell: peachy-pink fan with radiating ridges."""
import math

from pixelkit import Sprite, hexc, edge

W = H = 32
S = Sprite(W, H)

OUT = hexc("#7a2e4a")      # deep berry outline
RAMP = [hexc("#ffe4d6"), hexc("#fbb9a4"), hexc("#e98a86"), hexc("#bf5f72")]
RIDGE = hexc("#d9737a")
RIDGE_D = hexc("#a84d66")
GLINT = hexc("#fffaf2")
EAR = [hexc("#fbd0bc"), hexc("#f0a294"), hexc("#d67b80"), hexc("#b25c70")]

PX, PY = 15.5, 25.0         # fan pivot (hinge)
N_RIDGES = 7
SPREAD = math.radians(56)   # half-angle of the fan


def fan_r(a):
    # scalloped rim: small bumps between ridges
    t = (a + SPREAD) / (2 * SPREAD) * N_RIDGES
    return 15.6 + 1.1 * abs(math.cos(math.pi * t))


fan = set()
for y in range(H):
    for x in range(W):
        dx, dy = x - PX, PY - y
        if dy < -1:
            continue
        a = math.atan2(dx, dy)      # 0 = straight up
        if abs(a) <= SPREAD and math.hypot(dx, dy) <= fan_r(a):
            fan.add((x, y))

# little "ears" at the hinge
ears = set()
EAR_ROWS = ["..##########..",
            ".############.",
            "##############",
            "##############",
            ".############."]
for y, row in enumerate(EAR_ROWS):
    for x, ch in enumerate(row):
        if ch == "#":
            ears.add((int(PX) - 6 + x, 24 + y))
ears -= fan

S.blob(ears, EAR, OUT, lx=0.9, ly=0.3)
S.blob(fan, RAMP, OUT, lx=0.8, ly=0.35, cuts=(-0.35, 0.2, 0.6), center=(PX, 16))

# ridges: radiating lines, each with a light line on its left side
inner = fan - edge(fan)
for i in range(1, N_RIDGES):
    a = -SPREAD + 2 * SPREAD * i / N_RIDGES
    for r10 in range(40, 160):
        r = r10 / 10
        x = round(PX + math.sin(a) * r)
        y = round(PY - math.cos(a) * r)
        if (x, y) in inner:
            dark = x > PX + 3 or y > 21
            S.set(x, y, RIDGE_D if dark else RIDGE)
            if (x - 1, y) in inner and S.get(x - 1, y) not in (RIDGE, RIDGE_D):
                S.set(x - 1, y, RAMP[0] if x < PX else RAMP[1])

# specular glint upper-left
for (x, y) in ((9, 10), (10, 9), (9, 11), (12, 8)):
    if (x, y) in inner:
        S.set(x, y, GLINT)

S.center()
S.save("seashell", "goods")
