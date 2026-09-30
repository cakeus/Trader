"""Mochi: a round calico cat who poses as a lucky cat in shop windows.
White with orange and black patches, eyes shut in a smug little smile, one
paw raised in the beckoning pose, a red collar with a gold bell, and a plain
gold coin held to her chest."""
from pixelkit import hexc, ellipse, edge, rect
from portraitkit import new, poly, line, blush, clip, finish, GLINT

S = new()

WHITE = [hexc("#ffffff"), hexc("#fbf6ee"), hexc("#ecdfd0"), hexc("#d4c2b0")]
WH_OUT = hexc("#6a5048")
ORANGE = [hexc("#ffc47a"), hexc("#f59a3f"), hexc("#d07a30"), hexc("#a85e28")]
BLACK = [hexc("#5a5068"), hexc("#3c3448"), hexc("#2a2436")]
EAR_IN = hexc("#f6b4b8")
COLLAR = [hexc("#f27a5c"), hexc("#e0503f"), hexc("#a8332f")]
CO_OUT = hexc("#5e1c24")
GOLD = [hexc("#fff4b0"), hexc("#ffd24a"), hexc("#d89a2a"), hexc("#a8701e")]
GO_OUT = hexc("#6a4418")
LINE = hexc("#4a3040")
NOSE = hexc("#f07890")


def patches(mask, spots, ramp):
    for (cx, cy, rx, ry) in spots:
        p = ellipse(cx, cy, rx, ry) & mask
        if p:
            S.blob(p, ramp, None, cuts=(-0.3, 0.3, 0.7), center=(cx - 1, cy - 1))


# round body
body = clip(ellipse(30, 66, 24, 16))
S.blob(body, WHITE, WH_OUT, cuts=(-0.5, 0.25, 0.75))
patches(body - edge(body), [(12, 60, 8, 7)], ORANGE)
patches(body - edge(body), [(46, 62, 6, 5)], BLACK)

# raised beckoning paw (her left), behind the head's edge
arm = poly([(40, 52), (47, 52), (52, 34), (46, 32)])
S.blob(arm, WHITE, WH_OUT, cuts=(-0.4, 0.3, 0.75))
paw = ellipse(50, 30, 5, 5)
S.blob(paw, WHITE, WH_OUT, cuts=(-0.4, 0.3, 0.75))
for x in (48, 50, 52):
    S.set(x, 26, WH_OUT)
    S.set(x, 27, WH_OUT)
S.fill({(49, 31), (50, 31), (51, 31), (50, 32)}, EAR_IN)
for (x, y) in ((56, 25), (57, 24), (57, 29), (58, 29)):   # beckoning ticks
    S.set(x, y, WH_OUT)

# ears
for side in (-1, 1):
    bx = 30 + side * 10
    ear = poly([(bx - 6, 24), (bx + 6, 24), (bx + side * 3, 10)])
    S.blob(ear, WHITE, WH_OUT, cuts=(-0.4, 0.3, 0.75))
    inner = poly([(bx - 3, 23), (bx + 3, 23), (bx + side * 2.5, 15)]) - edge(ear)
    S.fill(inner, EAR_IN)
# orange left ear, black right ear
S.blob(poly([(14, 24), (26, 24), (17, 10)]) - edge(poly([(14, 24), (26, 24), (17, 10)])) -
       poly([(17, 23), (23, 23), (17.5, 15)]), ORANGE, None, cuts=(-0.3, 0.3))

# head
head = ellipse(30, 31, 17, 13.5)
S.blob(head, WHITE, WH_OUT, cuts=(-0.5, 0.25, 0.75))
inner = head - edge(head)
patches(inner, [(19, 22, 8, 6)], ORANGE)
patches(inner, [(42, 22, 7, 5)], BLACK)
S.set(21, 21, GLINT)
S.set(22, 20, GLINT)

# shut, smiling eyes and a little w mouth
for ex in (21, 35):
    for (x, y) in ((ex, 31), (ex + 1, 30), (ex + 2, 30), (ex + 3, 30), (ex + 4, 31)):
        S.set(x, y, LINE)
S.fill({(29, 34), (30, 34), (31, 34), (30, 35)}, NOSE)
for (x, y) in ((28, 36), (29, 37), (30, 36), (31, 37), (32, 36)):
    S.set(x, y, LINE)
for (x, y) in ((13, 33), (14, 33), (15, 33), (13, 36), (14, 35), (45, 33), (46, 33), (47, 33), (47, 35), (46, 35)):
    S.set(x, y, WHITE[3])   # whiskers
blush(S, 19, 34)
blush(S, 40, 34)

# red collar with a gold bell
for x in range(17, 44):
    t = (x - 30) / 13
    y0 = 43 + round(3 * (1 - t * t))
    for dy, c in ((0, CO_OUT), (1, COLLAR[0] if x < 30 else COLLAR[1]), (2, COLLAR[2]), (3, CO_OUT)):
        S.set(x, y0 - 1 + dy, c)
bell = ellipse(30, 49, 3.2, 3.2)
S.blob(bell, GOLD, GO_OUT, cuts=(-0.3, 0.3, 0.7))
S.set(29, 48, GLINT)
for x in range(28, 33):
    S.set(x, 49, GOLD[3])
S.set(30, 51, GO_OUT)

# the other paw holding a plain gold coin to her chest
coin = ellipse(21, 55, 5, 6.5)
S.blob(coin, GOLD, GO_OUT, cuts=(-0.4, 0.2, 0.7))
for y in range(51, 60, 2):
    for x in range(19, 24):
        if (x, y) in coin and (x, y) not in edge(coin):
            S.set(x, y, GOLD[2])
S.set(19, 51, GLINT)
S.set(19, 52, GLINT)
hand = ellipse(26, 57, 3.6, 3.2)
S.blob(hand, WHITE, WH_OUT, cuts=(-0.4, 0.3))
S.set(24, 56, WH_OUT)
S.set(24, 58, WH_OUT)

finish(S, "mochi")
