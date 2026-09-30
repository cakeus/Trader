"""Ponpoko: a round tanuki with warm brown fur, dark drooping eye patches and
dark shoulders, a leaf perched on his head, patting his big round belly like
a drum (it's a little pink from all the practice)."""
from pixelkit import hexc, ellipse, edge
from portraitkit import new, poly, eye, blush, clip, finish, smile, fuzz, GLINT

S = new()

FUR = [hexc("#f4d2a0"), hexc("#d8a468"), hexc("#b07a48"), hexc("#8a5a38")]
FR_OUT = hexc("#3e2418")
DARK = [hexc("#7a5a4a"), hexc("#5a4038"), hexc("#46302c"), hexc("#36241f")]
DK_OUT = hexc("#1e1210")
CREAM = [hexc("#fffaf0"), hexc("#fbecd0"), hexc("#ecd2aa"), hexc("#d8b68a")]
CR_OUT = hexc("#6a4430")
LEAF = [hexc("#b8e08a"), hexc("#7cbc5a"), hexc("#4e9446"), hexc("#3a7038")]
LF_OUT = hexc("#1e3a1e")
NOSE = hexc("#2a1a18")
PINK = hexc("#f4a8a0")

# dark shoulders and arms (tanuki have dark legs)
body = clip(ellipse(32, 64, 27, 18))
S.blob(body, DARK, DK_OUT, cuts=(-0.5, 0.2, 0.7))
# the big round belly
belly = clip(ellipse(32, 61, 15, 13))
S.blob(belly, CREAM, CR_OUT, cuts=(-0.45, 0.2, 0.7))
for (x, y) in ((28, 55), (29, 54), (35, 54), (36, 55), (31, 57), (33, 57)):   # rosy from drumming
    S.set(x, y, PINK)
S.set(24, 52, GLINT)
S.set(25, 51, GLINT)
# paws mid-pat on the belly, with little motion ticks
for (cx, cy) in ((18, 56), (46, 56)):
    paw = ellipse(cx, cy, 4.2, 3.6)
    S.blob(paw, DARK, DK_OUT, cuts=(-0.3, 0.3, 0.75))
    S.set(cx - 1, cy - 2, DARK[0])
for (x, y) in ((12, 49), (11, 48), (13, 51), (52, 49), (53, 48), (51, 51)):
    S.set(x, y, FR_OUT)

# round ears with dark backs
for cx in (18, 46):
    ear = ellipse(cx, 21, 5, 4.6)
    S.blob(ear, DARK, DK_OUT, cuts=(-0.3, 0.4))
    S.fill(ellipse(cx, 22, 2.4, 2), FUR[1])

# head: soft fluffy cheeks
head = fuzz(ellipse(32, 34, 17, 13), 3)
S.blob(head, FUR, FR_OUT, cuts=(-0.5, 0.2, 0.7))
inner = head - edge(head)
# the tanuki mask: dark patches that droop down and out under the eyes
for side in (-1, 1):
    patch = poly([(32 + side * 3, 30), (32 + side * 10, 28), (32 + side * 15, 34),
                  (32 + side * 14, 40), (32 + side * 8, 38), (32 + side * 4, 35)]) & inner
    S.blob(patch, DARK, None, cuts=(-0.4, 0.4))
# pale brow and muzzle
for (x, y) in ((24, 27), (25, 27), (26, 27), (38, 27), (39, 27), (40, 27)):
    S.set(x, y, FUR[0])
muz = ellipse(32, 39, 6.5, 5)
S.blob(muz, CREAM, None, cuts=(-0.2, 0.6))
nose = ellipse(32, 36.6, 2.4, 1.7)
S.fill(nose, NOSE)
S.set(31, 36, GLINT)
S.set(32, 38, CR_OUT)
smile(S, 29, 40, 7, CR_OUT)
# eyes shine out of the mask
for ex in (24, 37):
    eye(S, ex, 31, 3, 4, dark=hexc("#120a08"))
    S.set(ex + 1, 31, hexc("#fff4e4"))
    S.set(ex, 31, hexc("#fff4e4"))
blush(S, 20, 41)
blush(S, 43, 41)

# the leaf on his head
leaf = poly([(28, 22), (31, 15), (36, 12), (38, 14), (36, 19), (31, 23)])
S.blob(leaf, LEAF, LF_OUT, cuts=(-0.3, 0.3, 0.75))
for (x, y) in ((31, 20), (32, 19), (33, 18), (34, 16), (35, 15)):
    S.set(x, y, LEAF[3])
S.set(27, 23, LF_OUT)
S.set(26, 24, LF_OUT)

finish(S, "ponpoko")
