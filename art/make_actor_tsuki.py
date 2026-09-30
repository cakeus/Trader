"""Tsuki: the moon rabbit, snow-white with long ears (one flopped), a cozy
indigo scarf, a wooden mochi mallet over her shoulder and a little full moon
glowing behind her."""
from pixelkit import hexc, ellipse, edge, rounded_rect
from portraitkit import new, poly, eye, blush, clip, finish, smile, line, GLINT

S = new()

FUR = [hexc("#ffffff"), hexc("#f2f0fa"), hexc("#d8d4ec"), hexc("#b4aed0")]
FR_OUT = hexc("#4a4270")
PINK = [hexc("#ffd0dc"), hexc("#f4a8bc"), hexc("#e088a4")]
SCARF = [hexc("#6a7ec8"), hexc("#4a5aa0"), hexc("#34407c"), hexc("#262e5c")]
SC_OUT = hexc("#141a38")
STAR = hexc("#fff4d6")
MOON = [hexc("#fff4d6"), hexc("#f1dca6"), hexc("#dcc28a"), hexc("#c0a26a")]
MN_OUT = hexc("#8a6a3a")
WOOD = [hexc("#f0c488"), hexc("#c88a4e"), hexc("#9a623a"), hexc("#7a4a2c")]
WD_OUT = hexc("#4a2a1c")
NOSE = hexc("#e87894")
MOCHI = [hexc("#ffffff"), hexc("#f6f0ea"), hexc("#e0d6cc")]

# a little full moon behind her
moon = ellipse(51, 15, 9, 9)
S.blob(moon, MOON, MN_OUT, cuts=(-0.45, 0.2, 0.7))
for (x, y) in ((53, 12), (54, 12), (48, 18), (55, 19), (56, 18)):   # soft craters
    S.set(x, y, MOON[2])

# the mochi mallet (kine) over her shoulder: long handle, barrel head up top
# shoulders and scarf
body = clip(ellipse(32, 63, 23, 14))
S.blob(body, FUR, FR_OUT, cuts=(-0.5, 0.2, 0.7))
scarf = poly([(19, 47), (45, 47), (44, 53), (20, 53)]) | ellipse(32, 50, 14, 4)
S.blob(scarf, SCARF, SC_OUT, cuts=(-0.4, 0.3, 0.75))
tail = poly([(22, 50), (28, 51), (27, 62), (20, 61)])
S.blob(tail, SCARF, SC_OUT, cuts=(-0.3, 0.3, 0.75))
for (x, y) in ((23, 49), (29, 51), (35, 49), (41, 51), (24, 57), (23, 60)):
    S.set(x, y, STAR)
# her paw on the handle
S.blob(line(43, 56, 16, 18, width=2.6), WOOD, WD_OUT, cuts=(-0.1, 0.6))
mhead = poly([(6, 18), (15, 9), (24, 17), (15, 26)])
S.blob(mhead, WOOD, WD_OUT, cuts=(-0.35, 0.2, 0.7))
for p in line(8, 18, 15, 11):
    S.set(*p, WOOD[0])
for p in line(17, 25, 23, 19):
    S.set(*p, WOOD[3])
# a dab of mochi still stuck to it
dab = ellipse(9, 22, 2.4, 2)
S.blob(dab, MOCHI, FR_OUT, cuts=(-0.1, 0.6))
paw = ellipse(43, 57, 3.8, 3.4)
S.blob(paw, FUR, FR_OUT, cuts=(-0.3, 0.4))

# long ears: left one up, right one flopped over
ear_l = poly([(22, 26), (19, 13), (20, 5), (24, 3), (27, 9), (28, 24)])
S.blob(ear_l, FUR, FR_OUT, cuts=(-0.4, 0.3, 0.75))
S.fill(poly([(22.5, 22), (21, 12), (22.5, 7), (24.5, 10), (25.5, 22)]), PINK[1])
ear_r = poly([(36, 24), (38, 14), (43, 9), (51, 10), (54, 14), (47, 15), (41, 20), (40, 26)])
S.blob(ear_r, FUR, FR_OUT, cuts=(-0.4, 0.3, 0.75))
S.fill(poly([(39, 20), (41, 15), (45, 12), (50, 12), (46, 13.5), (41, 18)]), PINK[1])

# round head
head = ellipse(32, 36, 14, 12)
S.blob(head, FUR, FR_OUT, cuts=(-0.5, 0.25, 0.75))
S.set(22, 29, GLINT)

# eyes, pink nose, tiny mouth, blush
eye(S, 25, 34, 3, 4)
eye(S, 36, 34, 3, 4)
S.set(31, 39, NOSE)
S.set(32, 39, NOSE)
S.set(31, 40, FR_OUT)
smile(S, 29, 41, 3, FR_OUT)
smile(S, 32, 41, 3, FR_OUT)
blush(S, 22, 39)
blush(S, 40, 39)

finish(S, "tsuki")
