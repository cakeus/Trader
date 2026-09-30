"""Taisho: a big-hearted boar who runs an izakaya. Bristly brown fur, little
tusks, a twisted white headband, a navy work jacket and apron, and a red
lantern glowing behind him to say he's open."""
from pixelkit import hexc, ellipse, edge, rounded_rect
from portraitkit import new, poly, eye, blush, clip, finish, fuzz, line, GLINT

S = new()

FUR = [hexc("#d4a07a"), hexc("#a8704e"), hexc("#86543a"), hexc("#66402e")]
FR_OUT = hexc("#2e1a16")
MANE = [hexc("#6a4a3a"), hexc("#4e342a"), hexc("#3a2620")]
SNOUT = [hexc("#f8c8b0"), hexc("#e8a088"), hexc("#c87a6a")]
SN_OUT = hexc("#5a2a26")
TUSK = [hexc("#fffaf0"), hexc("#f0e4cc")]
BAND = [hexc("#ffffff"), hexc("#eeeaf2"), hexc("#ccc6d8")]
BD_OUT = hexc("#3a3450")
JACKET = [hexc("#6a7ea8"), hexc("#46587e"), hexc("#34425f"), hexc("#263048")]
JK_OUT = hexc("#121828")
APRON = [hexc("#4a5a8a"), hexc("#34406a"), hexc("#262e50")]
SHIRT = [hexc("#fff8ea"), hexc("#f0e4cc")]
LANT = [hexc("#f27a5c"), hexc("#e0503f"), hexc("#a8332f"), hexc("#86282a")]
LN_OUT = hexc("#5e1c24")
LGLOW = hexc("#ffc06b")
RING = [hexc("#4a3a4a"), hexc("#2e2432")]
TASSEL = hexc("#f7b861")

# the red lantern hanging behind him, glowing
lant = rounded_rect(43, 6, 17, 22, 6)
S.blob(lant, LANT, LN_OUT, cuts=(-0.5, 0.15, 0.65))
for (x, y) in lant - edge(lant):   # warm glow from the flame inside
    d = ((x - 50) / 5) ** 2 + ((y - 17) / 7) ** 2
    if d < 0.35:
        S.set(x, y, LGLOW)
    elif d < 1:
        S.set(x, y, LANT[0])
for y in (10, 14, 18, 22):   # ribs
    for x in range(44, 59):
        if (x, y) in lant and (x, y) not in edge(lant):
            S.set(x, y, LANT[1] if S.get(x, y) in (LGLOW, LANT[0]) else LANT[3] if x > 50 else LANT[2])
for (y0, h) in ((4, 3), (27, 3)):   # dark rings top and bottom
    ring = rounded_rect(45, y0, 13, h, 1)
    S.blob(ring, RING, FR_OUT, cuts=(0.0,))
S.fill(line(51, 30, 51, 34), TASSEL)
S.fill(line(50, 32, 50, 34), TASSEL)
S.fill(line(52, 32, 52, 34), TASSEL)
S.fill(line(51, 0, 51, 3), FR_OUT)
S.set(46, 9, GLINT)

# jacket shoulders, white undershirt at the collar, navy apron
body = clip(ellipse(32, 66, 28, 16))
S.blob(body, JACKET, JK_OUT, cuts=(-0.5, 0.2, 0.7))
vee = poly([(26, 50), (38, 50), (32, 58)])
S.blob(vee, SHIRT, JK_OUT, cuts=(0.3,))
for side in (-1, 1):   # jacket lapels
    for t in range(9):
        S.set(32 + side * (6 - t * 6 // 9), 50 + t, JK_OUT)
        S.set(32 + side * (7 - t * 6 // 9), 50 + t, JACKET[0] if side < 0 else JACKET[2])
apron = poly([(19, 57), (45, 57), (47, 64), (17, 64)])
S.blob(apron, APRON, JK_OUT, cuts=(-0.3, 0.4))
for x in range(19, 46):
    S.set(x, 58, APRON[2])
# a hand towel over one shoulder
towel = poly([(13, 53), (19, 51), (21, 62), (15, 63)])
S.blob(towel, BAND, BD_OUT, cuts=(-0.2, 0.6))
S.set(16, 56, BAND[2])
S.set(18, 59, BAND[2])

# small pointed ears
for side in (-1, 1):
    ear = poly([(32 + side * 5, 26), (32 + side * 17, 13), (32 + side * 14, 29)])
    S.blob(ear, FUR, FR_OUT, cuts=(-0.3, 0.4))
    S.fill(poly([(32 + side * 11, 22), (32 + side * 16, 16), (32 + side * 14.5, 23)]), SNOUT[2])

# bristly head
head = fuzz(ellipse(32, 36, 17, 14), 2)
S.blob(head, FUR, FR_OUT, cuts=(-0.5, 0.2, 0.7))
# darker bristly crest down the middle
for (x, y) in ((31, 21), (32, 21), (33, 22), (30, 23), (32, 24), (34, 23)):
    S.set(x, y, MANE[1])
S.set(20, 29, FUR[0])
S.set(21, 28, FUR[0])

# twisted headband (hachimaki) with a knot at the side
band = poly([(15, 27), (49, 27), (49, 31), (15, 31)]) & fuzz(ellipse(32, 36, 17.5, 14.5), 2)
S.blob(band, BAND, BD_OUT, cuts=(-0.3, 0.3, 0.75))
for x in range(17, 48, 3):   # the twist
    S.set(x, 29, BAND[2])
    S.set(x + 1, 28, BAND[2])
knot = ellipse(15, 30, 2.6, 2.2) | poly([(14, 30), (8, 34), (10, 36)]) | poly([(14, 30), (7, 29), (8, 32)])
S.blob(knot, BAND, BD_OUT, cuts=(-0.2, 0.5))

# happy squint eyes, big snout, little tusks
for ex in (23, 37):
    for (dx, dy) in ((0, 1), (1, 0), (2, 0), (3, 1)):
        S.set(ex + dx, 34 + dy, FR_OUT)
snout = ellipse(32, 41, 7, 5)
S.blob(snout, SNOUT, SN_OUT, cuts=(-0.3, 0.4))
for (x, y) in ((29, 40), (29, 41), (35, 40), (35, 41)):
    S.set(x, y, SN_OUT)
S.set(28, 39, GLINT)
for (x, y) in ((24, 45), (25, 46), (40, 45), (39, 46)):   # grin at the corners
    S.set(x, y, FR_OUT)
for x in range(26, 39):
    S.set(x, 47, FR_OUT)
for side in (-1, 1):
    tx = 32 + side * 9
    for y in range(43, 47):
        S.set(tx, y, TUSK[0])
        S.set(tx + side, y, TUSK[1])
    S.set(tx, 42, SN_OUT)
    S.set(tx + side, 42, SN_OUT)
    S.set(tx - side, 43, SN_OUT)
    S.set(tx + 2 * side, 44, SN_OUT)
blush(S, 19, 40)
blush(S, 44, 40)

finish(S, "taisho")
