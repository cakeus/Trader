"""Kyu the Kappa: a little green river kappa with the water dish on his
head ringed by a shaggy fringe, a yellow beak, a turtle shell on his back,
proudly holding up a cucumber roll (kappa maki, named after him)."""
from pixelkit import hexc, ellipse, edge, rect
from portraitkit import new, poly, eye, blush, clip, finish, fuzz, GLINT

S = new()

SKIN = [hexc("#c8f0a0"), hexc("#8ed070"), hexc("#62ac56"), hexc("#468a48")]
SK_OUT = hexc("#1c4230")
SHELL = [hexc("#c8b070"), hexc("#a08a4c"), hexc("#7c6a38"), hexc("#5c4e2a")]
SH_OUT = hexc("#2e2614")
BELLY = [hexc("#fff4b8"), hexc("#f4dc86"), hexc("#d8bc62")]
BE_OUT = hexc("#6a5424")
HAIR = [hexc("#4a7488"), hexc("#35566a"), hexc("#243e50")]
HR_OUT = hexc("#132430")
DISH = [hexc("#fffaf0"), hexc("#f0e6d0"), hexc("#d4c6a8")]
DI_OUT = hexc("#6a5c48")
WATER = [hexc("#d8f4ff"), hexc("#8ccfee"), hexc("#5aa6d4")]
BEAK = [hexc("#fff0a0"), hexc("#f8c84a"), hexc("#dc9a32")]
BK_OUT = hexc("#6a4418")
NORI = [hexc("#3a4a40"), hexc("#26322c"), hexc("#18201c")]
RICE = hexc("#ffffff")
RICE_S = hexc("#e4ded4")
CUKE = hexc("#7ccf5a")
CUKE_D = hexc("#3e8a3a")

# turtle shell showing behind the shoulders
shell = clip(ellipse(32, 60, 29, 14))
S.blob(shell, SHELL, SH_OUT, cuts=(-0.5, 0.2, 0.7))
for (x, y) in ((10, 54), (11, 53), (12, 52), (13, 52), (52, 52), (53, 53), (54, 54), (51, 52),
               (8, 58), (7, 59), (56, 58), (57, 59)):
    S.set(x, y, SH_OUT)
# green body with a yellow belly plate
body = clip(ellipse(32, 64, 20, 12))
S.blob(body, SKIN, SK_OUT, cuts=(-0.5, 0.2, 0.7))
belly = clip(ellipse(32, 66, 11, 11)) - edge(body)
S.blob(belly, BELLY, BE_OUT, cuts=(-0.3, 0.4))
for y in (59, 62):
    for x in range(24, 41):
        if (x, y) in belly and (x, y) not in edge(belly):
            S.set(x, y, BELLY[2])

# head
head = ellipse(32, 31, 16, 14)
S.blob(head, SKIN, SK_OUT, cuts=(-0.5, 0.2, 0.7))

# shaggy fringe ringing the dish
hair = ellipse(32, 19, 17, 5.5)
for i, x in enumerate(range(15, 50, 4)):   # pointed locks hanging over the brow
    ln = 4 if abs(x - 32) > 10 else 3
    top = 21 if abs(x - 32) > 12 else 22
    hair |= poly([(x - 0.5, top), (x + 3.5, top), (x + 1.5, top + ln + (i % 2))])
S.blob(hair, HAIR, HR_OUT, cuts=(-0.4, 0.2, 0.7), center=(30, 20))
for x in range(19, 46, 4):   # strands
    S.set(x, 20, HAIR[0])
    S.set(x + 1, 21, HAIR[2])

# the water dish on top
dish = ellipse(32, 16, 10, 3.6)
S.blob(dish, DISH, DI_OUT, cuts=(-0.3, 0.4))
water = ellipse(32, 16, 7, 1.8)
S.blob(water, WATER, None, cuts=(-0.3, 0.4))
S.set(29, 15, GLINT)
S.set(30, 15, GLINT)
S.set(37, 11, WATER[1])   # little splash drop
S.set(38, 10, WATER[0])

# big eyes and a cheerful beak
eye(S, 23, 28, 4, 5)
eye(S, 37, 28, 4, 5)
S.set(24, 30, GLINT)
S.set(38, 30, GLINT)
beak = ellipse(32, 37, 6, 3.2)
S.blob(beak, BEAK, BK_OUT, cuts=(-0.3, 0.4))
for x in range(28, 37):
    S.set(x, 37, BK_OUT)
S.set(27, 36, BK_OUT)
S.set(37, 36, BK_OUT)
S.set(29, 35, GLINT)
blush(S, 19, 34)
blush(S, 43, 34)

# hands holding up a big cucumber roll
roll = ellipse(32, 50, 7.5, 7)
S.blob(roll, NORI, hexc("#0e1410"), cuts=(-0.3, 0.4))
rice = ellipse(32, 50, 5.5, 5)
S.fill(rice, RICE)
for (x, y) in ((35, 53), (36, 52), (34, 54), (36, 51)):
    S.set(x, y, RICE_S)
for (x, y) in ((28, 48), (29, 53), (35, 47), (30, 46)):
    S.set(x, y, RICE_S)
core = rect(30, 48, 4, 4) - {(30, 48), (33, 51)}
S.fill(core, CUKE)
S.set(33, 50, CUKE_D)
S.set(32, 51, CUKE_D)
S.set(31, 49, hexc("#c8f4a0"))
for cx in (22, 42):
    hand = ellipse(cx, 51, 3.5, 3.2)
    S.blob(hand, SKIN, SK_OUT, cuts=(-0.4, 0.3))
    for dy in (-1, 1):
        S.set(cx + (2 if cx < 32 else -2), 51 + dy, SK_OUT)
S.set(27, 44, GLINT)

finish(S, "kyu")
