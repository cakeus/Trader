"""Kirara: a sparkly hamster pop idol. Golden fur with a cream face and
round cheeks, big shining eyes, a headset mic, a pink bow with a star, a
frilly pink stage outfit, and sparkles all around (kira-kira)."""
from pixelkit import hexc, ellipse, edge, rect
from portraitkit import new, poly, line, blush, clip, finish, GLINT, EYE_DARK

S = new()

FUR = [hexc("#ffd89a"), hexc("#f4b45e"), hexc("#d8924a"), hexc("#b0703a")]
FU_OUT = hexc("#5a3018")
CREAM = [hexc("#fffaf0"), hexc("#fdf0dc"), hexc("#f0dcc0"), hexc("#dcc2a0")]
EAR_IN = hexc("#f6a8b4")
DRESS = [hexc("#ffd0e4"), hexc("#ff94c0"), hexc("#e0669c"), hexc("#b84a80")]
DR_OUT = hexc("#6a1e48")
FRILL = [hexc("#ffffff"), hexc("#fff0f6"), hexc("#f4d0e0")]
FR_OUT = hexc("#9a5a7a")
BOW = [hexc("#ffa8cc"), hexc("#ff6aa4"), hexc("#d84886")]
STAR = [hexc("#fffbe0"), hexc("#ffe066"), hexc("#f4b43c")]
ST_OUT = hexc("#8a5a18")
MIC = [hexc("#e0e4f0"), hexc("#9aa0b8"), hexc("#6a7090")]
MI_OUT = hexc("#2a2e44")
SPARK = hexc("#fff4d6")
SPARK2 = hexc("#ffc0e0")
IRIS = [hexc("#b890ff"), hexc("#7a58d0"), hexc("#4a3494")]


def sparkle(cx, cy, big=False, c=SPARK):
    S.set(cx, cy, hexc("#ffffff"))
    for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        S.set(cx + d[0], cy + d[1], c)
    if big:
        for d in ((2, 0), (-2, 0), (0, 2), (0, -2)):
            S.set(cx + d[0], cy + d[1], c)


def star(cx, cy, r):
    import math
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    m = poly(pts)
    S.blob(m, STAR, ST_OUT, cuts=(-0.2, 0.5))
    return m


# frilly pink stage outfit
dress = clip(ellipse(32, 66, 25, 15))
S.blob(dress, DRESS, DR_OUT, cuts=(-0.5, 0.2, 0.7))
for (x, y) in ((14, 60), (18, 57), (46, 57), (50, 60)):   # puff-sleeve seams
    S.set(x, y, DRESS[3])
    S.set(x, y + 1, DRESS[3])
# ruffled white collar
frill = set()
for i, x in enumerate(range(18, 47, 4)):
    frill |= ellipse(x + 1.5, 52 + (1 if i % 2 else 0), 3, 2.6)
S.blob(frill, FRILL, FR_OUT, cuts=(-0.3, 0.5), center=(30, 51))
# bow at the chest
for side in (-1, 1):
    wing = poly([(32, 57), (32 + side * 6, 54), (32 + side * 6, 61)])
    S.blob(wing, BOW, DR_OUT, cuts=(-0.3, 0.4))
S.blob(rect(31, 56, 3, 3), BOW, DR_OUT, cuts=(-0.3, 0.4))
for (x, y) in ((22, 61), (41, 62), (28, 63), (37, 60)):   # sequins
    S.set(x, y, SPARK)

# (head drawn on its own layer, then set down onto the collar)
body_layer = S
S = new()

# round ears
for cx in (17, 45):
    ear = ellipse(cx, 19, 5, 5)
    S.blob(ear, FUR, FU_OUT, cuts=(-0.4, 0.2, 0.7))
    S.fill(ellipse(cx, 19.5, 2.5, 2.5), EAR_IN)

# head: golden with a big cream face and puffy cheeks
head = ellipse(31, 33, 17, 15) | ellipse(17, 38, 7, 7) | ellipse(45, 38, 7, 7)
S.blob(head, FUR, FU_OUT, cuts=(-0.5, 0.2, 0.7), center=(31, 33))
face = (ellipse(31, 39, 11, 8) | ellipse(19, 39, 5.5, 5.5) | ellipse(43, 39, 5.5, 5.5)) & (head - edge(head))
S.blob(face, CREAM, None, cuts=(-0.3, 0.4, 0.8), center=(29, 37))
# forehead stripe
for y in range(19, 27):
    S.set(31, y, FUR[2])
S.set(22, 21, GLINT)
S.set(23, 20, GLINT)

# bow with a star on her head
for side in (-1, 1):
    loop = poly([(37, 16), (37 + side * 8, 10), (37 + side * 8, 22)])
    S.blob(loop, BOW, DR_OUT, cuts=(-0.3, 0.4), center=(37, 16))
    S.set(37 + side * 5, 16, BOW[2])
star(37, 16, 5.6)
S.set(36, 14, GLINT)

# big shining eyes
for ex in (24, 38):
    m = ellipse(ex, 32, 3.5, 4.2)
    S.fill(m, EYE_DARK)
    inner = m - edge(m)
    S.fill({(x, y) for (x, y) in inner if y >= 32}, IRIS[1])
    S.fill({(x, y) for (x, y) in inner if y >= 34}, IRIS[0])
    for (x, y) in ((ex - 2, 30), (ex - 1, 30), (ex - 2, 31), (ex - 1, 31)):
        S.set(x, y, GLINT)
    S.set(ex + 1, 34, GLINT)
    S.set(ex + 4, 29, EYE_DARK) if ex > 30 else S.set(ex - 4, 29, EYE_DARK)   # outer lash
# nose, open happy mouth, buck teeth
S.fill({(30, 38), (31, 38), (32, 38)}, hexc("#e87890"))
S.set(31, 39, FU_OUT)
for (x, y) in ((29, 40), (30, 41), (31, 41), (32, 41), (33, 40)):
    S.set(x, y, FU_OUT)
S.fill({(30, 42), (31, 42), (32, 42), (31, 43)}, hexc("#f28a9a"))
blush(S, 18, 38)
blush(S, 43, 38)
S.set(19, 37, hexc("#ffc0c0"))

# headset mic along her cheek
arm = line(14, 34, 22, 44)
S.fill(arm, MI_OUT)
band = {(x, y) for (x, y) in line(12, 30, 15, 22, 2)}
S.fill(band, MIC[2])
pad = ellipse(13, 32, 2.6, 3.2)
S.blob(pad, MIC, MI_OUT, cuts=(-0.3, 0.4))
bulb = ellipse(23.5, 45, 2, 1.8)
S.blob(bulb, MIC, MI_OUT, cuts=(-0.3, 0.4))

S.shift(0, 2)
for k, v in S.px.items():
    if k not in body_layer.px or k[1] < 52:
        body_layer.px[k] = v
S = body_layer
# redraw the ruffle over the chin
S.blob(frill, FRILL, FR_OUT, cuts=(-0.3, 0.5), center=(30, 51))

# kira-kira sparkles
sparkle(6, 14, big=True)
sparkle(56, 26, big=True, c=SPARK2)
sparkle(9, 46)
sparkle(55, 8)
sparkle(52, 46, c=SPARK2)

finish(S, "kirara")
