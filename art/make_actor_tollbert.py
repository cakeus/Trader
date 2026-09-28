"""Tollbert: a big, dopey, mossy bridge troll with a bulbous nose, underbite
tusks and shaggy hair, and a rope-tied bundle of toll pickaxes on his back."""
import math

from pixelkit import hexc, ellipse, edge, rect
from portraitkit import new, poly, eye, blush, clip, finish, fuzz, GLINT

S = new()

SKIN = [hexc("#c4e0cc"), hexc("#90bca8"), hexc("#6c9a8c"), hexc("#517c74")]
SK_OUT = hexc("#1c3638")
HAIR = [hexc("#9aa65a"), hexc("#74823e"), hexc("#56622e"), hexc("#404a22")]
HR_OUT = hexc("#232a14")
TUNIC = [hexc("#dcbc8c"), hexc("#b8946a"), hexc("#94704e"), hexc("#74563c")]
TN_OUT = hexc("#3a2a1a")
PATCH = [hexc("#a0b8e0"), hexc("#7090c0"), hexc("#50709c")]
ROPE = [hexc("#f0d890"), hexc("#d0b060"), hexc("#a08440")]
RP_OUT = hexc("#54401a")
TUSK = [hexc("#ffffff"), hexc("#fff4dc"), hexc("#e0d0b0")]
TK_OUT = hexc("#7a6a4a")
MOUTH = hexc("#3a1a2a")
SHROOM = [hexc("#ff9a8a"), hexc("#e8404a"), hexc("#b82a3c")]
SHROOM_OUT = hexc("#4a0e1e")
WOOD = [hexc("#f0c488"), hexc("#d0924e"), hexc("#a8683a"), hexc("#7e4a2a")]
WOOD_OUT = hexc("#4a2a1c")
STEEL = [hexc("#e4eef8"), hexc("#a8bcd4"), hexc("#7890b0"), hexc("#566a8c")]
STEEL_OUT = hexc("#27304a")


def pickaxe(S, base, top, half=11.0, bend=4.0, thick=2.4, hw=1.4):
    """A pickaxe like the good's icon: handle from base to top, curved head at top."""
    L = math.hypot(top[0] - base[0], top[1] - base[1])
    D = ((top[0] - base[0]) / L, (top[1] - base[1]) / L)
    N = (-D[1], D[0])

    def frame(x, y):
        dx, dy = x + 0.5 - base[0], y + 0.5 - base[1]
        return dx * D[0] + dy * D[1], dx * N[0] + dy * N[1]

    def region(test):
        return {(x, y) for y in range(64) for x in range(64) if test(*frame(x, y))}

    def hc(v):
        t = min(1.0, abs(v) / half)
        return L - bend * t * t

    handle = region(lambda u, v: 0 <= u <= L and abs(v) <= hw)
    head = region(lambda u, v: abs(v) <= half and
                  abs(u - hc(v)) <= thick * (1 - min(1, abs(v) / half) ** 1.6) + 0.55)
    collar = region(lambda u, v: L - 2.8 <= u <= L + 1.8 and abs(v) <= hw + 1.2)
    S.blob(handle, WOOD, WOOD_OUT, lx=0.6, ly=0.6)
    S.blob(head, STEEL, STEEL_OUT, lx=0.65, ly=0.65, cuts=(-0.4, 0.15, 0.6))
    S.blob(collar, STEEL[1:], STEEL_OUT, lx=0.6, ly=0.6, cuts=(-0.2, 0.4))
    for (x, y) in head - edge(head):
        u, v = frame(x, y)
        if u - hc(v) > 0.5 and abs(v) < half - 2.5:
            S.set(x, y, STEEL[0])


# the toll: a fan of pickaxes slung over his back, heads up
pickaxe(S, (16, 56), (4, 16), half=8, bend=3)
pickaxe(S, (16, 56), (19, 5), half=9, bend=3.5)
pickaxe(S, (18, 56), (12, 9), half=8.5, bend=3.2)

# big patched tunic shoulders
tunic = clip(ellipse(32, 65, 30, 15))
S.blob(tunic, TUNIC, TN_OUT, cuts=(-0.5, 0.2, 0.7))
patch = rect(40, 56, 7, 6)
S.blob(patch, PATCH, TN_OUT, cuts=(-0.2, 0.5))
for (x, y) in ((41, 55), (43, 55), (45, 55), (48, 57), (48, 59)):   # stitches
    S.set(x, y, TN_OUT)
# rope strap across the chest holding the bundle
strap = poly([(9, 50), (13, 47), (46, 64), (39, 64)])
S.blob(strap, ROPE, RP_OUT, cuts=(-0.3, 0.4))
for (x, y) in strap - edge(strap):
    if (x + y) % 4 == 0:
        S.set(x, y, ROPE[2])

# big pointy ears
for side in (-1, 1):
    ear = poly([(34 + side * 15, 29), (34 + side * 24, 25), (34 + side * 16, 38)])
    S.blob(ear, SKIN, SK_OUT, cuts=(-0.3, 0.4, 0.8))
    S.set(34 + side * 19, 29, SKIN[3])
    S.set(34 + side * 18, 30, SKIN[3])

# big lumpy head
head = ellipse(34, 35, 18, 14) | ellipse(34, 44, 15, 6)
S.blob(head, SKIN, SK_OUT, cuts=(-0.5, 0.2, 0.7))
for (x, y) in ((20, 39), (21, 40), (48, 36), (46, 45)):   # warts
    S.set(x, y, SKIN[3])

# shaggy mossy hair, with a little mushroom growing in it
hair = fuzz(ellipse(34, 23, 17, 7) | ellipse(22, 27, 5, 4) | ellipse(46, 27, 5, 4), period=2)
S.blob(hair, HAIR, HR_OUT, cuts=(-0.4, 0.3, 0.75))
for (x, y) in ((28, 21), (33, 19), (38, 22), (42, 25), (25, 26), (31, 24), (36, 25)):
    S.set(x, y, HAIR[3])
S.set(27, 19, HAIR[0])
S.set(30, 18, HAIR[0])
stem = rect(41, 15, 2, 3)
S.blob(stem, [hexc("#fff4dc"), hexc("#e8d8b8")], TK_OUT)
cap = ellipse(42, 14, 4, 2.4)
S.blob(cap, SHROOM, SHROOM_OUT, cuts=(-0.2, 0.5))
S.set(41, 13, hexc("#fff4e4"))
S.set(43, 14, hexc("#fff4e4"))

# heavy brow, small friendly eyes
for x in range(23, 46):
    if x not in (33, 34, 35):
        S.set(x, 30, SKIN[3])
eye(S, 26, 31, 3, 4)
eye(S, 40, 31, 3, 4)

# big bulbous nose
nose = ellipse(34, 38, 5.5, 4.5)
S.blob(nose, SKIN, SK_OUT, cuts=(-0.4, 0.2, 0.7))
S.set(32, 36, GLINT)
S.set(31, 37, SKIN[0])

# wide underbite with two tusks poking up
for x in range(25, 44):
    S.set(x, 46 if 28 <= x <= 40 else 45, MOUTH)
S.set(24, 44, MOUTH)
S.set(44, 44, MOUTH)
for tx in (27, 41):
    tusk = poly([(tx - 2.6, 49), (tx + 2.6, 49), (tx + 1.2, 39.5), (tx - 0.6, 39.5)])
    S.blob(tusk, TUSK, TK_OUT, cuts=(-0.2, 0.5))
blush(S, 21, 38)
blush(S, 46, 38)

finish(S, "tollbert")
