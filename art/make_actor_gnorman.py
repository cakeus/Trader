"""Gnorman the Gnome: a garden-gnome handyman with a tall red pointy hat,
a big fluffy white beard, a round nose and blue overalls."""
from pixelkit import hexc, ellipse, edge, rect
from portraitkit import new, poly, eye, blush, clip, finish, fuzz, GLINT

S = new()

SKIN = [hexc("#ffe0c8"), hexc("#f4b89a"), hexc("#dc947a"), hexc("#b87060")]
SK_OUT = hexc("#6a3028")
HAT = [hexc("#ff9a8a"), hexc("#e8404a"), hexc("#b82a3c"), hexc("#8a1e34")]
H_OUT = hexc("#4a0e1e")
BEARD = [hexc("#ffffff"), hexc("#f0eef4"), hexc("#d8d4e4"), hexc("#b8b2c8")]
BD_OUT = hexc("#6a6480")
OVER = [hexc("#8ac0f0"), hexc("#4a8ad0"), hexc("#3468a8"), hexc("#264e84")]
OV_OUT = hexc("#12264a")
SHIRT = [hexc("#c8f0a0"), hexc("#8ed070"), hexc("#62a850")]
SH_OUT = hexc("#24461c")
BUCKLE = hexc("#ffd24a")

# green shirt shoulders + blue overalls bib
shirt = clip(ellipse(32, 64, 26, 14))
S.blob(shirt, SHIRT, SH_OUT, cuts=(-0.5, 0.3))
bib = rect(20, 54, 25, 10)
S.blob(bib, OVER, OV_OUT, cuts=(-0.4, 0.3, 0.75))
for sx in (16, 44):   # straps
    for y in range(50, 57):
        S.set(sx + (y - 50) // 3 * (1 if sx < 32 else -1), y, OV_OUT)
        S.set(sx + 1 + (y - 50) // 3 * (1 if sx < 32 else -1), y, OVER[1])
S.set(22, 56, BUCKLE)
S.set(42, 56, BUCKLE)

# face
face = ellipse(32, 34, 12, 11)
S.blob(face, SKIN, SK_OUT, cuts=(-0.5, 0.25, 0.75))

# big fluffy beard over the chest
beard = fuzz(poly([(18, 34), (46, 34), (44, 48), (38, 57), (32, 59), (26, 57), (20, 48)]), period=2)
S.blob(beard, BEARD, BD_OUT, cuts=(-0.4, 0.3, 0.75), center=(32, 42))
for (x, y) in ((26, 46), (30, 50), (34, 47), (38, 51), (29, 54), (35, 55)):   # curls
    S.set(x, y, BEARD[2])
# moustache
mous = ellipse(27, 37, 5, 2.4) | ellipse(37, 37, 5, 2.4)
S.blob(mous, BEARD, BD_OUT, cuts=(-0.2, 0.5))

# tall pointy hat
hat = poly([(17, 29), (47, 29), (40, 16), (33, 4), (30, 1), (27, 3), (24, 16)])
S.blob(hat, HAT, H_OUT, cuts=(-0.45, 0.2, 0.7), center=(32, 18))
S.set(27, 8, GLINT)
S.set(26, 11, GLINT)

# eyes + round nose
eye(S, 25, 30, 3, 3)
eye(S, 37, 30, 3, 3)
nose = ellipse(32, 34.5, 3.4, 3)
S.blob(nose, SKIN, SK_OUT, cuts=(-0.3, 0.4))
S.set(31, 33, GLINT)
blush(S, 22, 33)
blush(S, 41, 33)

finish(S, "gnorman")
