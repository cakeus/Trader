"""Herr Kuckuck: a cuckoo-bird clockmaker in an alpine green felt hat with a
feather, a brass jeweller's loupe over one eye, and lederhosen braces."""
from pixelkit import hexc, ellipse, edge, rect
from portraitkit import new, poly, line, eye, blush, clip, finish, GLINT

S = new()

FEATH = [hexc("#d8a070"), hexc("#a8704a"), hexc("#845236"), hexc("#643c28")]
FT_OUT = hexc("#3a2218")
CREAM = [hexc("#fff6e4"), hexc("#f2e0c0"), hexc("#dcc49c")]
BARS = hexc("#9c7a5a")
BEAK = [hexc("#ffe08a"), hexc("#f4b43c"), hexc("#d0862a")]
BK_OUT = hexc("#7a4214")
HAT = [hexc("#9ad08a"), hexc("#5a9a58"), hexc("#3e7644"), hexc("#2c5634")]
HT_OUT = hexc("#18321e")
BAND = hexc("#8a3a2a")
PLUME = [hexc("#fff0f0"), hexc("#f4a0a8"), hexc("#d06078")]
SHIRT = [hexc("#ffffff"), hexc("#eeeaf2"), hexc("#d0cadc")]
SH_OUT = hexc("#6a6480")
LEATHER = [hexc("#a8744a"), hexc("#7e5030"), hexc("#5e3a22")]
LE_OUT = hexc("#341c10")
BRASS = [hexc("#fff4b0"), hexc("#ffd24a"), hexc("#d89a2a"), hexc("#a8701e")]
BR_OUT = hexc("#6a4418")
LENS = [hexc("#eef8ff"), hexc("#bcdcf0"), hexc("#8cb4d8")]

# white shirt shoulders with braces and a chest strap
shirt = clip(ellipse(32, 63, 24, 14))
S.blob(shirt, SHIRT, SH_OUT, cuts=(-0.5, 0.3, 0.8))
for sx in (22, 41):
    strap = {(x, y) for y in range(49, 64) for x in range(sx, sx + 3)} & shirt
    S.blob(strap, LEATHER, LE_OUT, cuts=(-0.3, 0.5))
chest = {(x, y) for x in range(22, 44) for y in (56, 57, 58)} & shirt
S.blob(chest, LEATHER, LE_OUT, cuts=(-0.3, 0.5))
S.set(32, 57, hexc("#e8e0c8"))   # edelweiss on the chest strap
for (x, y) in ((31, 57), (33, 57), (32, 56), (32, 58)):
    S.set(x, y, hexc("#fffaf0"))
S.set(32, 57, BRASS[1])

# round bird head with a cream barred breast
head = ellipse(32, 36, 17, 15)
S.blob(head, FEATH, FT_OUT, cuts=(-0.5, 0.2, 0.7))
face = ellipse(32, 42, 11, 9) - edge(head)
S.blob(face, CREAM, None, cuts=(-0.2, 0.6))
for (x, y) in ((27, 47), (29, 48), (31, 47), (33, 48), (35, 47), (37, 48), (25, 45), (39, 45), (29, 50), (33, 50), (35, 50)):
    if (x, y) in face:
        S.set(x, y, BARS)
# cheek feather tufts
for (x, y) in ((15, 34), (15, 37), (49, 34), (49, 37)):
    S.set(x, y, FT_OUT)
    S.set(x + (-1 if x < 32 else 1), y + 1, FT_OUT)

# alpine felt hat with a pinched crown, band and pink feather
crown = poly([(20, 24), (44, 24), (41, 12), (34, 10), (32, 13), (30, 10), (23, 12)])
S.blob(crown, HAT, HT_OUT, cuts=(-0.4, 0.3, 0.75))
brim = ellipse(32, 24, 19, 3.2)
S.blob(brim, HAT, HT_OUT, cuts=(-0.3, 0.4, 0.8))
for x in range(22, 43):
    if (x, 21) in crown and (x, 21) not in edge(crown):
        S.set(x, 21, BAND)
        S.set(x, 20, BAND)
plume = poly([(40, 21), (43, 21), (49, 11), (51, 4), (48, 6), (42, 14)])
S.blob(plume, PLUME, hexc("#8a3048"), cuts=(-0.2, 0.4), center=(44, 12))
for p in line(42, 20, 49, 7):
    if p in plume and p not in edge(plume):
        S.set(*p, PLUME[2])
S.set(25, 14, GLINT)
S.set(26, 13, GLINT)

# left eye plain, right eye behind a brass loupe
eye(S, 24, 32, 3, 4)
loupe = ellipse(40, 33.5, 5.2, 5.2)
S.blob(loupe, BRASS, BR_OUT, cuts=(-0.3, 0.3, 0.7))
lens = ellipse(40, 33.5, 3.4, 3.4)
S.blob(lens, LENS, None, cuts=(-0.3, 0.4))
eye(S, 39, 32, 3, 4)       # magnified eye
S.set(38, 31, GLINT)
S.set(37, 31, GLINT)
# strap of the loupe going round the head
for p in line(45, 31, 49, 28):
    S.set(*p, LE_OUT)

# little hooked beak
beak = poly([(28, 37), (36, 37), (33, 43), (31, 43)])
S.blob(beak, BEAK, BK_OUT, cuts=(-0.2, 0.5))
S.set(30, 38, GLINT)
blush(S, 20, 39)
blush(S, 43, 40)

finish(S, "herr_kuckuck")
