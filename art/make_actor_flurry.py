"""Flurry: a nervous snowman selling hot cocoa at arm's length. Coal eyes with
worried brows, a carrot nose, pink earmuffs, a teal scarf, a sweat drop, and a
twig arm holding a steaming red mug as far away from himself as it will go."""
from pixelkit import hexc, ellipse, edge, rect, rounded_rect
from portraitkit import new, poly, line, eye, blush, clip, finish, GLINT

S = new()

SNOW = [hexc("#ffffff"), hexc("#eef2fc"), hexc("#d2dcf0"), hexc("#aebcdc")]
SN_OUT = hexc("#5a6a9a")
COAL = hexc("#2e2a3e")
CARROT = [hexc("#ffb060"), hexc("#f07a2a"), hexc("#c8541c")]
CA_OUT = hexc("#7a2e10")
MUFF = [hexc("#ffc8dc"), hexc("#f890b4"), hexc("#d86890"), hexc("#b04c74")]
MU_OUT = hexc("#6a2444")
BAND = hexc("#8a5a7a")
SCARF = [hexc("#9ae8d8"), hexc("#48b8a8"), hexc("#2e8a80"), hexc("#206a64")]
SC_OUT = hexc("#0e3a38")
TWIG = hexc("#7a5238")
TWIG_D = hexc("#4e3222")
MUG = [hexc("#ff8a7a"), hexc("#e0474c"), hexc("#b83244"), hexc("#8c2238")]
MUG_OUT = hexc("#5a1626")
MUG_BAND = hexc("#fff0e0")
COCOA = hexc("#8a4e32")
STEAM = hexc("#e4dcf4")
STEAM_D = hexc("#b4aad4")
DROP = [hexc("#e8f8ff"), hexc("#9ad4f4"), hexc("#5aa0d8")]
DROP_OUT = hexc("#2e5a8a")

# lower snowball (the bust)
body = clip(ellipse(28, 66, 24, 17))
S.blob(body, SNOW, SN_OUT, cuts=(-0.4, 0.25, 0.7))
for (x, y) in ((27, 55), (28, 60)):   # coal buttons
    S.fill(ellipse(x, y, 1.6, 1.4), COAL)
    S.set(x - 1, y - 1, hexc("#6a6480"))

# twig arm reaching out to the right, holding the mug at arm's length
arm = line(44, 54, 54, 44, width=2)
S.fill(arm, TWIG)
for p in line(45, 55, 55, 45):
    S.set(*p, TWIG_D)
for p in line(49, 49, 49, 45):   # little twig fork
    S.set(*p, TWIG)

# the mug (out at the far right, a bit shaky)
MX, MY = 50, 32
handle = {p for p in ellipse(MX, MY + 6, 3.6, 3.6) - ellipse(MX, MY + 6, 1.6, 1.6) if p[0] <= MX}
S.blob(handle, MUG, MUG_OUT, cuts=(-0.1, 0.5))
mug = rounded_rect(MX, MY, 12, 12, r=2)
S.blob(mug, MUG, MUG_OUT, lx=1.0, ly=0.25, cuts=(-0.55, 0.25, 0.75))
for x in range(MX + 1, MX + 11):
    S.set(x, MY + 6, MUG_BAND)
rim = ellipse(MX + 5.5, MY, 6, 2)
S.blob(rim, [MUG[0], MUG[0], MUG[1]], MUG_OUT, cuts=(0.2,))
S.fill(ellipse(MX + 5.5, MY + 0.3, 4.2, 1), COCOA)
S.set(MX + 2, MY + 3, GLINT)
S.set(MX + 2, MY + 4, GLINT)
# twig fingers wrapped round it
for (x, y) in ((MX + 3, MY + 11), (MX + 4, MY + 12), (MX + 6, MY + 12)):
    S.set(x, y, TWIG)
for (x, y) in ((MX + 4, MY - 3), (MX + 3, MY - 4), (MX + 3, MY - 5), (MX + 4, MY - 6),
               (MX + 5, MY - 7), (MX + 5, MY - 8)):
    S.set(x, y, STEAM)
    S.set(x + 1, y, STEAM_D)
for (x, y) in ((MX + 8, MY - 3), (MX + 9, MY - 4), (MX + 9, MY - 5), (MX + 8, MY - 6)):
    S.set(x, y, STEAM)
# shaky wobble lines
for (x, y) in ((MX - 3, MY + 1), (MX - 3, MY + 2), (MX + 14, MY + 1), (MX + 14, MY + 2)):
    S.set(x, y, SN_OUT)

# teal scarf between the snowballs, tail flapping left
scarf = ellipse(28, 45, 15, 4)
S.blob(scarf, SCARF, SC_OUT, cuts=(-0.4, 0.3, 0.75))
tail = poly([(14, 46), (20, 46), (17, 57), (11, 55)])
S.blob(tail, SCARF, SC_OUT, cuts=(-0.3, 0.4, 0.8))
for x in range(15, 42, 3):
    S.set(x, 45, SCARF[2])
for (x, y) in ((12, 56), (14, 57), (16, 58)):
    S.set(x, y, SCARF[3])

# head snowball
head = ellipse(28, 28, 16, 14.5)
S.blob(head, SNOW, SN_OUT, cuts=(-0.4, 0.25, 0.7))

# earmuffs: band over the top, fluffy pads on the sides
band = {p for p in ellipse(28, 27, 17.5, 16.5) - ellipse(28, 27, 16, 15) if p[1] <= 22}
S.fill(band, BAND)
for cx in (12, 44):
    pad = ellipse(cx, 27, 4.4, 5.4)
    S.blob(pad, MUFF, MU_OUT, cuts=(-0.3, 0.3, 0.7))
    S.set(cx - 1, 25, GLINT)

# worried coal eyes with slanted brows
for ex in (20, 32):
    S.fill(ellipse(ex + 1.5, 26.5, 2.2, 2.6), COAL)
    S.set(ex + 1, 25, GLINT)
# brows tilted up in the middle
for (x, y) in ((18, 21), (19, 21), (20, 20), (21, 20), (22, 19)):
    S.set(x, y, COAL)
for (x, y) in ((33, 19), (34, 20), (35, 20), (36, 21), (37, 21)):
    S.set(x, y, COAL)

# carrot nose poking out
nose = poly([(26, 29), (27, 34), (38, 32)])
nose |= {(26, 30), (26, 31), (26, 32), (26, 33), (27, 29)}
S.blob(nose, CARROT, CA_OUT, cuts=(-0.2, 0.5))
S.set(30, 32, CARROT[2])

# wobbly nervous mouth of coal dots
for (x, y) in ((22, 38), (23, 37), (24, 37), (25, 38), (26, 38), (27, 37), (28, 37),
               (29, 38), (30, 38), (31, 37)):
    S.set(x, y, COAL)
blush(S, 17, 32)
blush(S, 38, 34)

# sweat drop (or melt drop) on the brow
drop = ellipse(10, 17, 2, 2.6) | {(10, 13), (10, 14)}
S.blob(drop, DROP, DROP_OUT, cuts=(-0.1, 0.5))
S.set(9, 16, GLINT)

finish(S, "flurry")
