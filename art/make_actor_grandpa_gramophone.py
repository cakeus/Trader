"""Grandpa Gramophone: an old tortoise record collector with bushy white brows,
round glasses, a mustard cardigan, and his shell peeking over his shoulders."""
from pixelkit import hexc, ellipse, edge, rect
from portraitkit import new, eye, blush, clip, finish, smile, GLINT

S = new()

SKIN = [hexc("#d4e4a4"), hexc("#a8c47a"), hexc("#80a058"), hexc("#607c44")]
SK_OUT = hexc("#2e3e1e")
SHELL = [hexc("#c8a070"), hexc("#9c7448"), hexc("#7a5634"), hexc("#5a3e26")]
SHL_OUT = hexc("#2e1e12")
CARD = [hexc("#ffe08a"), hexc("#e8b64a"), hexc("#c48e30"), hexc("#9a6a22")]
CD_OUT = hexc("#5a3a10")
BROW = [hexc("#ffffff"), hexc("#ece6f0"), hexc("#c8c0d0")]
GLASS = hexc("#4a3a2e")
LENS = hexc("#e8f4f0")
BTN = hexc("#7a4a24")

# shell dome behind the shoulders
shell = clip(ellipse(32, 56, 30, 17))
S.blob(shell, SHELL, SHL_OUT, cuts=(-0.5, 0.2, 0.7))
for (x0, y0) in ((10, 48), (20, 43), (40, 43), (50, 48)):   # scute seams
    for i in range(5):
        S.set(x0 + i - 2, y0 - (2 - abs(i - 2)), SHELL[3])

# cardigan in front
card = clip(ellipse(32, 67, 23, 13))
S.blob(card, CARD, CD_OUT, cuts=(-0.5, 0.2, 0.7))
for y in range(55, 64):   # v-neck opening + placket
    S.set(32, y, CD_OUT)
for y in (57, 60, 63):
    S.set(34, y, BTN)
# shirt collar in the v
for (x, y) in ((29, 55), (30, 55), (34, 55), (35, 55), (30, 56), (34, 56)):
    S.set(x, y, hexc("#fff4e4"))

# neck with wrinkle lines
neck = rect(26, 42, 13, 13)
S.blob(neck, SKIN, SK_OUT, cuts=(-0.3, 0.4, 0.8))
for x in range(28, 37, 2):
    S.set(x, 47, SKIN[3])
    S.set(x + 1, 50, SKIN[3])

# head
head = ellipse(32, 30, 14, 14)
S.blob(head, SKIN, SK_OUT, cuts=(-0.45, 0.25, 0.7))
for (x, y) in ((26, 20), (29, 18), (34, 18)):   # age spots
    S.set(x, y, SKIN[2])

# eyes behind round glasses
eye(S, 25, 30, 2, 3)
eye(S, 37, 30, 2, 3)
for cx in (26, 38):
    ring = edge(ellipse(cx, 31, 4.6, 4.6))
    for (x, y) in ellipse(cx, 31, 3.6, 3.6):
        if y < 30 and S.get(x, y) != hexc("#2a1a2e"):
            S.set(x, y, LENS)
    S.fill(ring, GLASS)
    S.set(cx - 2, 29, GLINT)
for x in range(30, 35):
    S.set(x, 30, GLASS)

# bushy white brows
for cx in (25, 39):
    brow = ellipse(cx, 25, 5.2, 2.4)
    S.blob(brow, BROW, hexc("#8a8494"), cuts=(-0.2, 0.5))

# beaky tortoise mouth
smile(S, 28, 38, 9, SK_OUT)
S.set(32, 36, SK_OUT)
blush(S, 20, 35)
blush(S, 43, 35)

finish(S, "grandpa_gramophone")
