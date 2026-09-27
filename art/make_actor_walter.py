"""Walter the Walrus: a retired shipwright with long tusks, a bristly
moustache, a navy knit beanie with a pencil tucked in, and a cable-knit sweater."""
from pixelkit import hexc, ellipse, edge
from portraitkit import new, poly, line, eye, blush, clip, finish, GLINT

S = new()

HIDE = [hexc("#e8c0a8"), hexc("#c48e78"), hexc("#a06a5a"), hexc("#7c4e44")]
HD_OUT = hexc("#40221e")
MUZ = [hexc("#fff0e4"), hexc("#f0d0bc"), hexc("#d4ac98")]
BEANIE = [hexc("#7a8ad0"), hexc("#4a5aa4"), hexc("#36447e"), hexc("#28325e")]
BN_OUT = hexc("#161a3a")
SWEATER = [hexc("#fff8ec"), hexc("#ece0cc"), hexc("#d0c0a8"), hexc("#b0a088")]
SW_OUT = hexc("#6a5a48")
TUSK = [hexc("#ffffff"), hexc("#fff4dc"), hexc("#e0d0b0")]
TK_OUT = hexc("#7a6a4a")
PENCIL = hexc("#ffd24a")
PENCIL_D = hexc("#c08a2a")

# sweater with cable knit
sweater = clip(ellipse(32, 65, 28, 14))
S.blob(sweater, SWEATER, SW_OUT, cuts=(-0.5, 0.2, 0.7))
for cx in (20, 32, 44):
    for y in range(54, 64, 2):
        S.set(cx - 1, y, SWEATER[2])
        S.set(cx + 1, y + 1, SWEATER[2])

# big head
head = ellipse(32, 33, 22, 16)
S.blob(head, HIDE, HD_OUT, cuts=(-0.5, 0.2, 0.7))
for (x, y) in ((16, 38), (18, 42), (47, 40), (45, 43)):   # wrinkles
    S.set(x, y, HIDE[3])

# beanie with folded cuff
cap = ellipse(32, 20, 17, 11) & {(x, y) for x in range(64) for y in range(0, 22)}
S.blob(cap, BEANIE, BN_OUT, cuts=(-0.4, 0.3, 0.75))
cuff = poly([(14, 17), (50, 17), (50, 24), (14, 24)])
S.blob(cuff, BEANIE, BN_OUT, cuts=(-0.3, 0.4, 0.8))
for x in range(16, 49, 2):   # ribbing
    for y in (19, 20, 21):
        S.set(x, y, BEANIE[2])
S.set(26, 11, GLINT)
S.set(27, 10, GLINT)

# pencil tucked into the cuff
pencil = line(45, 13, 55, 24, width=2)
S.fill(pencil, PENCIL)
for p in line(46, 14, 55, 24):
    S.set(*p, PENCIL_D)
S.set(45, 12, hexc("#f28a8a"))
S.set(44, 12, hexc("#f28a8a"))
S.set(56, 25, hexc("#3b2f55"))

# small eyes
eye(S, 23, 28, 3, 3)
eye(S, 38, 28, 3, 3)

# tusks (drawn before the muzzle so they tuck under it)
for (x0, x1) in ((27, 26), (37, 38)):
    tusk = line(x0, 42, x1, 55, width=3)
    S.blob(tusk, TUSK, TK_OUT, cuts=(-0.2, 0.5))

# bristly muzzle
muz = ellipse(26, 39, 7.5, 5) | ellipse(38, 39, 7.5, 5)
S.blob(muz, MUZ, HD_OUT, cuts=(-0.2, 0.6))
for (x, y) in ((22, 38), (25, 37), (28, 39), (24, 41), (36, 37), (39, 38), (42, 40), (37, 41)):
    S.set(x, y, HIDE[2])
nose = ellipse(32, 34.5, 3.4, 2.2)
S.fill(nose, HD_OUT)
S.set(31, 34, GLINT)
blush(S, 17, 34)
blush(S, 45, 34)

finish(S, "walter")
