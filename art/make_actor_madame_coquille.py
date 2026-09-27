"""Madame Coquille: a pastel-green snail couturier with a pink spiral shell,
a tilted plum hat with a golden feather, and pearls."""
from pixelkit import hexc, ellipse, edge, rect
from portraitkit import new, line, curve, spiral, eyeball, blush, clip, finish, smile, GLINT

S = new()

SHELL = [hexc("#ffd6e6"), hexc("#f59cc2"), hexc("#d26a9c"), hexc("#a44a7c")]
SH_OUT = hexc("#5a1e44")
BODY = [hexc("#d4f0b4"), hexc("#a6d886"), hexc("#7cb866"), hexc("#5a9050")]
B_OUT = hexc("#2e5430")
HAT = [hexc("#9a78c8"), hexc("#6e4e9e"), hexc("#503880"), hexc("#3a2862")]
HAT_OUT = hexc("#221440")
RIBBON = hexc("#f56a9a")
FEATHER = [hexc("#fff0a8"), hexc("#ffd24a"), hexc("#d8a02c")]
PEARL = hexc("#fffaf0")
PEARL_S = hexc("#d8ccd8")

# shell behind, to the right
shell = ellipse(42, 36, 19, 19)
S.blob(shell, SHELL, SH_OUT, cuts=(-0.45, 0.2, 0.65))
inner = shell - edge(shell)
sp = spiral(43, 37, 1.5, 15.5, 2.2, start=3.4)
for (x, y) in sp:
    if (x, y) in inner:
        S.set(x, y, SHELL[3])
        if (x - 1, y - 1) in inner and (x - 1, y - 1) not in sp:
            S.set(x - 1, y - 1, SHELL[0])
S.set(30, 25, GLINT)
S.set(31, 24, GLINT)

# neck + head
body = clip(ellipse(22, 60, 16, 14)) | ellipse(22, 47, 10, 10) | ellipse(22, 35, 12, 11)
S.blob(body, BODY, B_OUT, cuts=(-0.45, 0.25, 0.7), center=(22, 40))

# eye stalks + eyes
for (x0, y0, x1, y1) in ((16, 28, 11, 13), (27, 27, 31, 11)):
    st = line(x0, y0, x1, y1, width=3)
    S.blob(st, BODY, B_OUT, cuts=(-0.2, 0.5))
eyeball(S, 11, 11, 3.6, B_OUT, look=(0.6, 0.4))
eyeball(S, 31, 9, 3.6, B_OUT, look=(0.6, 0.4))
# lashes
for (x, y) in ((8, 8), (9, 7), (34, 6), (33, 5)):
    S.set(x, y, B_OUT)

# tilted hat on the head
brim = ellipse(21, 25.5, 10.5, 2.4)
crown = rect(15, 19, 11, 6) | ellipse(20.5, 19.5, 5.5, 2.2)
S.blob(crown, HAT, HAT_OUT, cuts=(-0.4, 0.3))
S.blob(brim, HAT, HAT_OUT, cuts=(-0.3, 0.4))
for x in range(16, 26):
    if S.get(x, 23) not in (HAT_OUT,):
        S.set(x, 23, RIBBON)
fe = curve([(24, 22), (28, 16), (34, 13), (38, 14)], width=2)
S.blob(fe, FEATHER, hexc("#7a5410"), cuts=(-0.2, 0.5))

# face
smile(S, 19, 40, 5, B_OUT)
blush(S, 13, 38)
blush(S, 28, 38)

# pearl necklace
for i, x in enumerate(range(13, 32, 2)):
    y = 49 + round(((x - 22) / 9.5) ** 2 * -3) + 3
    S.set(x, y, PEARL)
    S.set(x, y + 1, PEARL_S)

finish(S, "madame_coquille")
