"""32x32 lucky cat: a gold maneki-neko waving both paws, with a red collar and bell."""
from pixelkit import Sprite, hexc, ellipse, edge

W = H = 32
S = Sprite(W, H)

GOLD = [hexc("#fff2a8"), hexc("#ffd552"), hexc("#e8a93a"), hexc("#b87426")]
GOLD_OUT = hexc("#6e4216")
EAR_IN = hexc("#e8605a")
RED = [hexc("#f27a5c"), hexc("#e0503f"), hexc("#a8332f")]
RED_OUT = hexc("#5e1c24")
FACE = hexc("#5a3212")
PINK = hexc("#ff9a9a")
GLINT = hexc("#ffffff")


def tri(ax, ay, bx, by, cx, cy):
    m = set()
    for y in range(32):
        for x in range(32):
            px, py = x + 0.5, y + 0.5
            d1 = (px - bx) * (ay - by) - (ax - bx) * (py - by)
            d2 = (px - cx) * (by - cy) - (bx - cx) * (py - cy)
            d3 = (px - ax) * (cy - ay) - (cx - ax) * (py - ay)
            neg = d1 < 0 or d2 < 0 or d3 < 0
            pos = d1 > 0 or d2 > 0 or d3 > 0
            if not (neg and pos):
                m.add((x, y))
    return m


def limb(x0, y0, x1, y1, r):
    m = set()
    for y in range(32):
        for x in range(32):
            px, py = x + 0.5, y + 0.5
            dx, dy = x1 - x0, y1 - y0
            t = max(0, min(1, ((px - x0) * dx + (py - y0) * dy) / (dx * dx + dy * dy)))
            if (px - x0 - t * dx) ** 2 + (py - y0 - t * dy) ** 2 <= r * r:
                m.add((x, y))
    return m


CX = 16.0
body = ellipse(15.5, 23.5, 9.3, 7.0)
head = ellipse(15.5, 12.5, 9.0, 6.4)
ears = [tri(6.5, 11, 8.5, 2.5, 15, 7.5), tri(25.5, 11, 23.5, 2.5, 17, 7.5)]
arms = [limb(9.5, 22, 5.0, 10.5, 2.4), limb(22.5, 22, 27.0, 10.5, 2.4)]
paws = [ellipse(4.5, 8.5, 3.2, 3.0), ellipse(26.5, 8.5, 3.2, 3.0)]

S.blob(body, GOLD, GOLD_OUT, lx=0.7, ly=0.5)
for a, p in zip(arms, paws):
    S.blob(a | p, GOLD, GOLD_OUT, lx=0.6, ly=0.6, cuts=(-0.35, 0.3, 0.8))
    # paw pad and toe beans, facing us
    px = round(sum(x for x, y in p) / len(p))
    py = round(sum(y for x, y in p) / len(p))
    for (x, y) in ((px - 1, py - 1), (px + 1, py - 1), (px - 1, py + 1), (px, py + 1), (px + 1, py + 1)):
        S.set(x, y, PINK)
for e in ears:
    S.blob(e, GOLD, GOLD_OUT, lx=0.6, ly=0.6)
S.blob(head, GOLD, GOLD_OUT, lx=0.7, ly=0.6, cuts=(-0.4, 0.3, 0.75))
# inner ears
for (x, y) in ((9, 5), (9, 6), (10, 6), (10, 7), (11, 7), (22, 5), (22, 6), (21, 6), (21, 7), (20, 7)):
    S.set(x, y, EAR_IN)
# face: happy closed eyes, pink nose, little w mouth, blush
for (x, y) in ((10, 13), (11, 12), (12, 12), (13, 13), (18, 13), (19, 12), (20, 12), (21, 13)):
    S.set(x, y, FACE)
S.set(15, 15, PINK)
S.set(16, 15, PINK)
S.set(15, 16, GOLD[1])
S.set(16, 16, GOLD[1])
for (x, y) in ((14, 16), (15, 16), (16, 16), (17, 16)):
    S.set(x, y, FACE)
for (x, y) in ((9, 15), (10, 15), (21, 15), (22, 15)):
    S.set(x, y, hexc("#f4a060"))
# whiskers
for (x, y) in ((6, 14), (6, 16), (25, 14), (25, 16)):
    S.set(x, y, GOLD_OUT)
# red collar and a gold bell
for x in range(9, 23):
    S.set(x, 19, RED[0] if x < 13 else RED[1])
    S.set(x, 20, RED[2])
for y in (19, 20):
    S.set(8, y, RED_OUT)
    S.set(23, y, RED_OUT)
S.rows([".OOO.",
        "OWYyO",
        "OYyyO",
        "OyOdO",
        ".OOO."], {"O": GOLD_OUT, "W": GOLD[0], "Y": GOLD[1], "y": GOLD[2], "d": GOLD[3]}, 13, 21)
# glints
for (x, y) in ((10, 9), (9, 10), (11, 23), (3, 7)):
    S.set(x, y, GLINT)

S.center()
S.save("lucky_cat", "goods")
