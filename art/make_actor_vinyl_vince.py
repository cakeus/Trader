"""Vinyl Vince: a raccoon in a bandit mask, red headphones and a green hoodie."""
import math

from pixelkit import hexc, ellipse, edge, rounded_rect
from portraitkit import new, poly, blush, clip, finish, smile, GLINT

S = new()

FUR = [hexc("#e2dee8"), hexc("#aea8bc"), hexc("#868098"), hexc("#665e7c")]
FUR_OUT = hexc("#352c46")
MASK = hexc("#3e3452")
MASK_L = hexc("#544868")
MUZZLE = [hexc("#ffffff"), hexc("#f2eef4"), hexc("#d4ccdc")]
HOOD = [hexc("#aee0a0"), hexc("#72bc6a"), hexc("#4e9650"), hexc("#3a7440")]
HOOD_OUT = hexc("#1e3e24")
PHONES = [hexc("#ff9a8a"), hexc("#e8504e"), hexc("#b83040"), hexc("#8a2436")]
PH_OUT = hexc("#521424")
PINK = hexc("#f2a0b0")

# hoodie
hood = clip(ellipse(32, 64, 27, 14))
S.blob(hood, HOOD, HOOD_OUT, cuts=(-0.5, 0.2, 0.7))
for (x, y) in ((28, 54), (28, 55), (28, 56), (36, 54), (36, 55), (36, 56)):   # drawstrings
    S.set(x, y, hexc("#fff4e4"))

# ears
for sx in (1, -1):
    ear = poly([(32 - sx * 18, 24), (32 - sx * 14, 5), (32 - sx * 4, 16)])
    S.blob(ear, FUR, FUR_OUT, cuts=(-0.3, 0.3, 0.7))
    inner = poly([(32 - sx * 15.5, 19), (32 - sx * 14, 10), (32 - sx * 8.5, 16)])
    S.fill(inner, PINK)

# head
head = ellipse(32, 33, 20, 15)
S.blob(head, FUR, FUR_OUT, cuts=(-0.5, 0.2, 0.7))
inner = head - edge(head)
# forehead stripe
for y in range(19, 26):
    S.set(32, y, FUR[2])
    S.set(31, y, FUR[2])
# bandit mask
mask = (ellipse(23, 31, 9, 5) | ellipse(41, 31, 9, 5)) & inner
S.fill(mask, MASK)
for (x, y) in mask:
    if (x, y - 1) not in mask:
        S.set(x, y, MASK_L)
# eyes (light on the dark mask)
for ex in (22, 39):
    for (x, y) in ((ex, 29), (ex + 1, 29), (ex, 30), (ex + 1, 30), (ex, 31), (ex + 1, 31)):
        S.set(x, y, hexc("#fff4e4"))
    S.set(ex + 1, 30, hexc("#2a1a2e"))
    S.set(ex + 1, 31, hexc("#2a1a2e"))
    S.set(ex, 31, hexc("#2a1a2e"))
# muzzle
muz = ellipse(32, 40, 9, 6)
S.blob(muz, MUZZLE, None, cuts=(-0.1, 0.6))
nose = ellipse(32, 36.5, 2.6, 1.8)
S.fill(nose, FUR_OUT)
S.set(31, 36, GLINT)
smile(S, 29, 41, 7, FUR_OUT)
S.set(32, 38, FUR_OUT)
S.set(32, 39, FUR_OUT)
blush(S, 20, 38)
blush(S, 43, 38)

# headphones: band over the head, cups on the sides
band = set()
for i in range(0, 181):
    a = math.radians(180 + i)
    x = 32 + math.cos(a) * 21
    y = 31 + math.sin(a) * 22
    band |= ellipse(x, y, 1.6, 1.6)
band = {p for p in band if p[1] < 28}
S.blob(band, PHONES, PH_OUT, cuts=(-0.2, 0.4, 0.8))
for cx in (9, 49):
    cup = rounded_rect(cx, 25, 7, 13, 2)
    S.blob(cup, PHONES, PH_OUT, cuts=(-0.4, 0.2, 0.7))
    S.set(cx + 2, 27, GLINT)

finish(S, "vinyl_vince")
