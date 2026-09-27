"""DJ Mothball: a fuzzy lilac moth with feathery antennae, big glossy eyes,
mint headphones, a fluffy ruff and dusty-rose wings."""
import math

from pixelkit import hexc, ellipse, edge
from portraitkit import new, line, curve, shiny_eye, blush, clip, finish, fuzz, smile, GLINT

S = new()

WING = [hexc("#ffd8d0"), hexc("#eea2a6"), hexc("#cc7482"), hexc("#a4546a")]
W_OUT = hexc("#5a2a3e")
FUZZ = [hexc("#eee4fa"), hexc("#c8b8e8"), hexc("#9e8cc8"), hexc("#7a68a2")]
FZ_OUT = hexc("#3c2e5e")
EYE = [hexc("#5a4a8a"), hexc("#2e2450"), hexc("#1c1634")]
ANT = hexc("#c08a4a")
ANT_D = hexc("#7a4a2a")
PHONE = [hexc("#c4fff0"), hexc("#7ad8c4"), hexc("#48ae9c"), hexc("#2e8478")]
PH_OUT = hexc("#16464a")

# wings behind the shoulders
for sx in (1, -1):
    wing = ellipse(32 - sx * 19, 48, 10, 12)
    S.blob(wing, WING, W_OUT, cuts=(-0.4, 0.2, 0.7))
    spot = ellipse(32 - sx * 20, 47, 3.4, 3.4)
    S.fill(spot, WING[3])
    S.fill(ellipse(32 - sx * 20, 47, 1.4, 1.4), hexc("#fff0c0"))

# fuzzy body
body = clip(fuzz(ellipse(32, 62, 17, 10)))
S.blob(body, FUZZ, FZ_OUT, cuts=(-0.4, 0.3, 0.75))

# feathery antennae
for sx in (1, -1):
    pts = [(32 - sx * 6, 22), (32 - sx * 12, 12), (32 - sx * 20, 6), (32 - sx * 26, 5)]
    stem = curve(pts)
    for i in range(0, 22, 2):
        t = i / 22
        # sample along the curve and add barbs pointing outward/up
        seg = min(int(t * 3), 2)
        a, b = pts[seg], pts[seg + 1]
        u = t * 3 - seg
        x = a[0] + (b[0] - a[0]) * u
        y = a[1] + (b[1] - a[1]) * u
        S.fill(line(x, y, x - sx * 2, y - 3), ANT)
        S.fill(line(x, y, x + sx * 1, y - 3), ANT)
    S.fill(stem, ANT_D)

# fluffy head
head = fuzz(ellipse(32, 33, 17, 15), 2)
S.blob(head, FUZZ, FZ_OUT, cuts=(-0.45, 0.25, 0.7))
# fluff tuft on top
for (x, y) in ((30, 18), (31, 17), (32, 18), (33, 17), (34, 18)):
    S.set(x, y, FUZZ[0])
S.outline_around({(30, 18), (31, 17), (32, 18), (33, 17), (34, 18)} - set(), FZ_OUT)
for (x, y) in ((30, 18), (31, 17), (32, 18), (33, 17), (34, 18)):
    S.set(x, y, FUZZ[0])

# big glossy moth eyes
shiny_eye(S, 25, 33, 5.2, EYE, FZ_OUT)
shiny_eye(S, 39, 33, 5.2, EYE, FZ_OUT)
smile(S, 30, 41, 5, FZ_OUT)
blush(S, 19, 40)
blush(S, 44, 40)

# ruff collar
ruff = fuzz(ellipse(32, 51, 15, 5), 2)
S.blob(ruff, [FUZZ[0], hexc("#f8f2ff"), FUZZ[1], FUZZ[2]], FZ_OUT, cuts=(-0.6, 0.1, 0.6))
for x in range(20, 45, 3):
    S.set(x, 52 + (x % 2), FUZZ[2])

# headphones
band = set()
for i in range(0, 181, 2):
    a = math.radians(180 + i)
    band |= ellipse(32 + math.cos(a) * 19, 32 + math.sin(a) * 19, 1.5, 1.5)
band = {p for p in band if p[1] < 30}
S.blob(band, PHONE, PH_OUT, cuts=(-0.2, 0.4, 0.8))
for cx in (10, 48):
    cup = ellipse(cx + 3, 33, 4, 6)
    S.blob(cup, PHONE, PH_OUT, cuts=(-0.4, 0.2, 0.7))
    S.set(cx + 2, 30, GLINT)

finish(S, "dj_mothball")
