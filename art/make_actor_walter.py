"""Walter the Walrus: a retired sailor who weaves straw hats, with long tusks, a bristly
moustache, one of his own straw hats (red band) and a cable-knit sweater."""
from pixelkit import hexc, ellipse, edge
from portraitkit import new, poly, line, eye, blush, clip, finish, GLINT

S = new()

HIDE = [hexc("#e8c0a8"), hexc("#c48e78"), hexc("#a06a5a"), hexc("#7c4e44")]
HD_OUT = hexc("#40221e")
MUZ = [hexc("#fff0e4"), hexc("#f0d0bc"), hexc("#d4ac98")]
STRAW = [hexc("#fff0b8"), hexc("#f5d27a"), hexc("#dcaa52"), hexc("#b27c36")]
ST_OUT = hexc("#6b4220")
WEAVE = hexc("#e6bb62")
BAND = [hexc("#ff9a86"), hexc("#e8524a"), hexc("#b0343a")]
SWEATER = [hexc("#fff8ec"), hexc("#ece0cc"), hexc("#d0c0a8"), hexc("#b0a088")]
SW_OUT = hexc("#6a5a48")
TUSK = [hexc("#ffffff"), hexc("#fff4dc"), hexc("#e0d0b0")]
TK_OUT = hexc("#7a6a4a")

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

# straw hat: a rounded crown with a red band, then the wide brim in front of its base
crown = ellipse(32, 15, 13, 9) & {(x, y) for x in range(64) for y in range(0, 21)}
S.blob(crown, STRAW, ST_OUT, cuts=(-0.45, 0.25, 0.7))
for (x, y) in crown - edge(crown):
    if y in (9, 12) and S.get(x, y) != STRAW[0]:
        S.set(x, y, WEAVE)
    if 14 <= y <= 17:
        t = (x - 32) / 13
        S.set(x, y, BAND[0] if t < -0.5 else BAND[2] if t > 0.45 else BAND[1])
brim = ellipse(32, 20, 25, 4.6)
brim -= {(x, y) for (x, y) in brim if y < 19 and abs(x - 32) < 13}
S.blob(brim, STRAW, ST_OUT, lx=0.9, ly=0.4, cuts=(-0.55, 0.2, 0.7))
for x in range(9, 56, 3):
    if S.get(x, 21) in STRAW[1:3]:
        S.set(x, 21, WEAVE)
S.set(25, 7, GLINT)
S.set(24, 8, GLINT)

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
