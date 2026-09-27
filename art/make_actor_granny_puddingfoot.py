"""Granny Puddingfoot: a ginger hen in round spectacles and a lilac shawl."""
from pixelkit import hexc, ellipse, edge
from portraitkit import new, poly, eye, blush, clip, finish, GLINT

S = new()

FEATHER = [hexc("#ffdca8"), hexc("#f2aa62"), hexc("#d27c3e"), hexc("#a85a2c")]
F_OUT = hexc("#6a3418")
SHAWL = [hexc("#e6d4f4"), hexc("#c4a4e0"), hexc("#9a7ac0"), hexc("#765a9a")]
SH_OUT = hexc("#3e2a5a")
COMB = [hexc("#ff8a8a"), hexc("#e8404e"), hexc("#b82a3c")]
C_OUT = hexc("#6a1428")
BEAK = [hexc("#fff0a0"), hexc("#ffc84a"), hexc("#e09a2a")]
B_OUT = hexc("#8a5010")
GLASS = hexc("#7a4a24")
LENS = hexc("#fff4e4")

# comb (behind head)
comb = ellipse(26, 12, 3.6, 4.2) | ellipse(32, 9, 3.8, 5) | ellipse(38, 12, 3.6, 4.2)
S.blob(comb, COMB, C_OUT, cuts=(-0.3, 0.4))

# shawl shoulders
shawl = clip(ellipse(32, 62, 27, 14))
S.blob(shawl, SHAWL, SH_OUT, cuts=(-0.5, 0.2, 0.7))
# knitted dots
for y in range(52, 63, 3):
    for x in range(8 + (y % 2) * 2, 58, 5):
        if (x, y) in shawl and (x, y) not in edge(shawl):
            S.set(x, y, SHAWL[0] if x < 32 else SHAWL[1])

# breast feathers + head
breast = ellipse(32, 49, 13, 8)
S.blob(breast, FEATHER, F_OUT, cuts=(-0.4, 0.3, 0.7))
head = ellipse(32, 30, 16, 16)
S.blob(head, FEATHER, F_OUT, cuts=(-0.45, 0.25, 0.7))
# feather scallops on the chest
for x in range(24, 41, 4):
    S.set(x, 48, FEATHER[2])
    S.set(x + 1, 49, FEATHER[2])
# cheek feathers tuft
for (x, y) in ((18, 36), (17, 37), (46, 36), (47, 37)):
    S.set(x, y, FEATHER[3])

# brooch pinning the shawl
brooch = ellipse(32, 55, 2.6, 2.6)
S.blob(brooch, [hexc("#fff0a0"), hexc("#ffd24a"), hexc("#c08a2a")], hexc("#6a4414"))
S.set(31, 54, GLINT)

# eyes behind spectacles
eye(S, 24, 27, 3, 4)
eye(S, 37, 27, 3, 4)
for cx in (25.5, 38.5):
    ring = edge(ellipse(cx, 29, 5.2, 5.2))
    inner = ellipse(cx, 29, 4.2, 4.2) - ellipse(cx, 29, 3.2, 3.2)
    for (x, y) in inner:
        if (x, y) not in ring and S.get(x, y) != hexc("#2a1a2e"):
            S.set(x, y, LENS if y < 29 else S.get(x, y))
    S.fill(ring, GLASS)
    S.set(int(cx) - 2, 26, GLINT)
for x in range(30, 34):
    S.set(x, 28, GLASS)

# beak + wattle
beak = poly([(28.5, 34), (35.5, 34), (32, 40)])
S.blob(beak, BEAK, B_OUT, cuts=(-0.2, 0.5))
wattle = ellipse(32, 42.5, 2.2, 2.6)
S.blob(wattle, COMB, C_OUT, cuts=(0.0, 0.6))

blush(S, 21, 36)
blush(S, 41, 36)

finish(S, "granny_puddingfoot")
