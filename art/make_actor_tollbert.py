"""Tollbert: a big, dopey, mossy bridge troll with a bulbous nose, underbite
tusks and shaggy hair, and a rope-tied bundle of toll mittens on his back (none of
them match)."""
from pixelkit import hexc, ellipse, edge, rect
from portraitkit import new, poly, line, eye, blush, clip, finish, fuzz, GLINT

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
CUFF = [hexc("#fffbea"), hexc("#f2e2c0"), hexc("#c2a67c")]
MITTENS = [  # (ramp, outline): none of them match
    ([hexc("#ff9a86"), hexc("#e8524a"), hexc("#b8383c"), hexc("#8a2630")], hexc("#5e1c24")),
    ([hexc("#a8d0ff"), hexc("#5c8ce0"), hexc("#3e64b0"), hexc("#2c4a88")], hexc("#16244e")),
    ([hexc("#fff0a0"), hexc("#f2c84a"), hexc("#c8962a"), hexc("#a07020")], hexc("#5a3a10")),
    ([hexc("#c4f0a8"), hexc("#74c45c"), hexc("#4a9a44"), hexc("#347a3a")], hexc("#163a1e")),
]


def mitten(S, ox, oy, ramp, out, flip=False):
    """A small upright mitten, 10 wide by 13 tall, its top-left corner at (ox, oy)."""
    def fx(x):
        return ox + (9 - x if flip else x)
    shape = {(x, y) for (x, y) in ellipse(3.5, 4.0, 3.5, 4.0) if y <= 4} | rect(0, 4, 8, 5)
    shape |= ellipse(8.2, 5.2, 1.6, 2.4) | {(7, 8)}
    body = {(fx(x), oy + y) for (x, y) in shape}
    S.blob(body, ramp, out, cuts=(-0.5, 0.25, 0.7))
    for y in range(4, 7):
        S.set(fx(7), oy + y, out)
    cuff = {(fx(x), oy + y) for (x, y) in rect(0, 9, 8, 4)}
    S.blob(cuff, CUFF, out, cuts=(-0.4, 0.5))
    return fx(4), oy + 12


# the toll: a bundle of odd mittens tied on cords over his back
ends = []
for i, (ox, oy, flip) in enumerate(((1, 20, False), (6, 8, True), (16, 2, False), (2, 33, True))):
    ramp, out = MITTENS[i]
    ends.append(mitten(S, ox, oy, ramp, out, flip))
for (x, y) in ends:
    for p in line(x, y, 12, 48):
        if S.get(*p) is None:
            S.set(*p, ROPE[1])

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
