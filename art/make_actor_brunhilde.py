"""Brunhilde: a badger knitter in a red polka-dot headscarf and a leather apron, holding up
a big ball of yarn with two knitting needles stuck through it."""
from pixelkit import hexc, ellipse, edge, rect
from portraitkit import new, poly, line, eye, blush, clip, finish, smile, GLINT

S = new()

FACE = [hexc("#ffffff"), hexc("#f2eef0"), hexc("#d8d0d8"), hexc("#b8aebc")]
FC_OUT = hexc("#4a3e50")
STRIPE = [hexc("#6a6070"), hexc("#4a4250"), hexc("#3a3440")]
GREY = [hexc("#c8c4cc"), hexc("#a09aa8"), hexc("#7e7888"), hexc("#625c6c")]
SCARF = [hexc("#ff9a8a"), hexc("#e8404a"), hexc("#b82a3c"), hexc("#8a1e34")]
SC_OUT = hexc("#4a0e1e")
DOT = hexc("#fff4e4")
SHIRT = [hexc("#a8d8e0"), hexc("#6aa8b8"), hexc("#4a8098"), hexc("#386478")]
SH_OUT = hexc("#16303e")
APRON = [hexc("#d09a64"), hexc("#a8703e"), hexc("#86542c"), hexc("#663e20")]
AP_OUT = hexc("#3a2010")
RIVET = hexc("#ffd24a")
NOSE = hexc("#3a2a36")
YARN = [hexc("#e4d4ff"), hexc("#b49ae8"), hexc("#8a70c4"), hexc("#6a52a0")]
YN_OUT = hexc("#2e2252")
NEEDLE = [hexc("#f0c488"), hexc("#a8683a")]
KNOB = hexc("#e8524a")

# two knitting needles crossing behind the yarn, up past her shoulder
for (x0, y0, x1, y1) in ((48, 50, 55, 28), (54, 50, 60, 31)):
    for p in line(x0, y0, x1, y1, width=2):
        S.set(*p, NEEDLE[1])
    for p in line(x0, y0, x1, y1):
        S.set(*p, NEEDLE[0])
    for (dx, dy) in ((-1, -1), (0, -1), (-1, 0), (0, 0)):
        S.set(x1 + dx, y1 + dy - 1, KNOB)
    S.set(x1 - 1, y1 - 2, hexc("#ff9a86"))

# shirt shoulders with rolled sleeves, leather apron bib
shirt = clip(ellipse(32, 64, 27, 14))
S.blob(shirt, SHIRT, SH_OUT, cuts=(-0.5, 0.2, 0.7))
apron = poly([(21, 52), (43, 52), (45, 64), (19, 64)])
S.blob(apron, APRON, AP_OUT, cuts=(-0.3, 0.3, 0.75))
for (x, y) in ((22, 51), (21, 50), (20, 49), (42, 51), (43, 50), (44, 49)):   # neck strap
    S.set(x, y, AP_OUT)
pocket = rect(27, 57, 11, 6)
S.blob(pocket, APRON[1:], AP_OUT, cuts=(-0.2, 0.5))
for (x, y) in ((22, 54), (42, 54), (28, 58), (36, 58)):
    S.set(x, y, RIVET)
# a big ball of yarn held up in her paw, its strands wound round
ball = ellipse(52, 45, 7, 6.5)
S.blob(ball, YARN, YN_OUT, cuts=(-0.45, 0.2, 0.7))
for (x, y) in ball - edge(ball):   # wound strands: arcs round a point off to the upper-left
    d = ((x - 49) ** 2 + (y - 42) ** 2) ** 0.5
    if 3.4 < d < 4.4 or 6.4 < d < 7.4:
        S.set(x, y, YARN[2] if S.get(x, y) in (YARN[0], YARN[1]) else YARN[3])
S.set(48, 41, GLINT)
S.set(49, 40, YARN[0])
# the loose end trailing down
for (x, y) in ((45, 48), (44, 49), (44, 50), (43, 51)):
    S.set(x, y, YARN[1])
# her paw holding it
paw = ellipse(46, 52, 4.4, 3.6)
S.blob(paw, GREY, FC_OUT, cuts=(-0.3, 0.3, 0.75))
for x in (44, 46, 48):   # knuckles
    S.set(x, 50, GREY[3])
    S.set(x, 51, GREY[3])

# small round ears with pale rims
for cx in (17, 47):
    ear = ellipse(cx, 27, 3.8, 3.6)
    S.blob(ear, GREY, FC_OUT, cuts=(-0.2, 0.5))
    S.set(cx, 27, STRIPE[2])

# grey cheeks behind a white face
head = ellipse(32, 35, 16, 13)
S.blob(head, GREY, FC_OUT, cuts=(-0.5, 0.25, 0.75))
face = ellipse(32, 37, 11, 11) - edge(head)
S.blob(face, FACE, None, cuts=(-0.3, 0.3, 0.75))
# the two dark stripes running up over the eyes
for sx in (-1, 1):
    stripe = poly([(32 + sx * 2.5, 41), (32 + sx * 3, 22), (32 + sx * 10, 22), (32 + sx * 6.5, 41)])
    S.blob(stripe & head - edge(head), STRIPE, None, cuts=(-0.6, 0.6))
# white blaze down the middle stays white; nose at the bottom
nose = ellipse(32, 42, 3, 2.2)
S.fill(nose, NOSE)
S.set(31, 41, GLINT)
smile(S, 29, 45, 7, FC_OUT)

# headscarf knotted at the side
scarf = ellipse(32, 26, 17, 9) & {(x, y) for x in range(64) for y in range(0, 28)}
S.blob(scarf, SCARF, SC_OUT, cuts=(-0.4, 0.3, 0.75))
band = poly([(15, 25), (49, 25), (49, 29), (15, 29)]) & (ellipse(32, 27, 17.5, 9))
S.blob(band, SCARF, SC_OUT, cuts=(-0.2, 0.5, 0.85))
for (x, y) in ((22, 21), (28, 18), (35, 20), (41, 22), (25, 25), (39, 26), (31, 23), (18, 27), (45, 27)):
    if (x, y) in scarf or (x, y) in band:
        S.set(x, y, DOT)
knot = ellipse(13, 27, 3.4, 3) | ellipse(11, 32, 2.4, 3.2) | ellipse(15, 32, 2, 3)
S.blob(knot, SCARF, SC_OUT, cuts=(-0.3, 0.4, 0.8))
S.set(24, 19, GLINT)
S.set(25, 18, GLINT)

# eyes sit in the stripes
EYE = hexc("#140a18")
for ex in (26, 36):
    eye(S, ex, 33, 3, 3, dark=EYE)
    S.set(ex + 1, 33, GLINT)
blush(S, 21, 39)
blush(S, 42, 39)

finish(S, "brunhilde")
