"""Goro: a little thunder imp (a cute Kaminari-sama) with sky-blue skin, two
stubby yellow horns, a puff of storm-cloud hair, a tiger-stripe sash, a ring
of little drums behind him and a drumstick in his fist."""
import math

from pixelkit import hexc, ellipse, edge, rounded_rect
from portraitkit import new, poly, eye, blush, clip, finish, line, fuzz, GLINT

S = new()

SKIN = [hexc("#d8f0ff"), hexc("#94ccf0"), hexc("#6aa4d8"), hexc("#4e80b8")]
SK_OUT = hexc("#1e3462")
HAIR = [hexc("#8a84a8"), hexc("#625c84"), hexc("#48426a"), hexc("#363052")]
HA_OUT = hexc("#1c1834")
HORN = [hexc("#fffae0"), hexc("#ffe07a"), hexc("#e8b450")]
HO_OUT = hexc("#6a4418")
TIGER = [hexc("#ffe08a"), hexc("#f8b848"), hexc("#e08c30"), hexc("#b86a24")]
TG_OUT = hexc("#5a2c14")
STRIPE = hexc("#3a2418")
DRUM = [hexc("#ff9a7a"), hexc("#e0503f"), hexc("#a8332f"), hexc("#86282a")]
DR_OUT = hexc("#5e1c24")
SKINHEAD = [hexc("#fff4dc"), hexc("#f4dcae"), hexc("#dcbc88")]
RIVET = hexc("#ffd24a")
ROPE = hexc("#e8c070")
WOOD = [hexc("#f0c488"), hexc("#c88a4e"), hexc("#9a623a")]
WD_OUT = hexc("#4a2a1c")
MOUTH = hexc("#c84a5a")
BOLT = hexc("#ffe46a")

# ring of little drums behind him, strung on a rope
ring_pts = []
for deg in (190, 220, 250, 270, 290, 320, 350):
    a = math.radians(deg)
    ring_pts.append((32 + math.cos(a) * 26, 37 + math.sin(a) * 27))
for a, b in zip(ring_pts, ring_pts[1:]):
    if abs(a[0] - 32) < 5 or abs(b[0] - 32) < 5:
        continue
    S.fill(line(a[0], a[1], b[0], b[1]), ROPE)
ring_pts = [p for p in ring_pts if abs(p[0] - 32) > 5]
for (cx, cy) in ring_pts:
    body = ellipse(cx, cy, 4.6, 4.6)
    S.blob(body, DRUM, DR_OUT, cuts=(-0.4, 0.2, 0.7))
    face = ellipse(cx, cy, 3.2, 3.2) - edge(body)
    S.blob(face, SKINHEAD, None, cuts=(-0.2, 0.6))
    S.fill(edge(face) - edge(body), DRUM[2])
    S.set(round(cx) - 1, round(cy) - 1, GLINT)
    S.set(round(cx), round(cy), SKINHEAD[1])

# shoulders with a tiger-stripe sash
body = clip(ellipse(32, 63, 22, 14))
S.blob(body, SKIN, SK_OUT, cuts=(-0.5, 0.2, 0.7))
sash = poly([(14, 55), (22, 51), (48, 64), (37, 64)]) & body
S.blob(sash, TIGER, TG_OUT, cuts=(-0.3, 0.3, 0.75))
for t in range(4):
    x0, y0 = 20 + t * 6, 54 + t * 3
    for k in range(3):
        S.set(x0 + k, y0 - 2 + k, STRIPE)
# fist with a drumstick (bachi) raised
stick = line(46, 55, 54, 39, width=2.6)
S.blob(stick, WOOD, WD_OUT, cuts=(-0.1, 0.6))
fist = ellipse(47, 55, 4, 3.6)
S.blob(fist, SKIN, SK_OUT, cuts=(-0.3, 0.3, 0.75))
for x in (45, 47):
    S.set(x, 54, SKIN[2])


# round head
head = ellipse(32, 35, 14, 12)
S.blob(head, SKIN, SK_OUT, cuts=(-0.5, 0.25, 0.75))
for cx in (17, 47):   # little pointed ears
    ear = poly([(cx - 3, 31), (cx + 3, 31), (cx + (-4 if cx < 32 else 4), 26)])
    ear |= ellipse(cx, 33, 3, 3)
    S.blob(ear, SKIN, SK_OUT, cuts=(-0.3, 0.4))

# stubby horns poking out of the cloud
for side in (-1, 1):
    horn = poly([(32 + side * 2, 21), (32 + side * 8, 21), (32 + side * 7, 7), (32 + side * 4, 10)])
    S.blob(horn, HORN, HO_OUT, cuts=(-0.2, 0.5))

# puffy storm-cloud hair on top
for (cx, cy, r) in ((21, 27, 4.2), (43, 27, 4.2), (26, 22, 5), (38, 22, 5), (32, 20, 5.4),
                   (25, 27, 4.4), (39, 27, 4.4), (32, 26, 5)):
    puff = ellipse(cx, cy, r, r * 0.9)
    S.blob(puff, HAIR, HA_OUT, cuts=(-0.35, 0.3, 0.75))
    S.set(round(cx - r * 0.4), round(cy - r * 0.45), HAIR[0])
# a tiny lightning bolt tucked in the cloud
for (x, y) in ((33, 22), (32, 23), (33, 23), (34, 24), (33, 25)):
    S.set(x, y, BOLT)

# bushy brows, big eyes, cheeky open grin with a fang
for (x, y) in ((24, 30), (25, 29), (26, 29), (27, 30), (37, 30), (38, 29), (39, 29), (40, 30)):
    S.set(x, y, HA_OUT)
eye(S, 24, 32, 4, 5)
eye(S, 37, 32, 4, 5)
S.set(26, 35, GLINT)
S.set(39, 35, GLINT)
for x in range(29, 36):
    S.set(x, 40, SK_OUT)
for x in range(30, 35):
    S.set(x, 41, MOUTH)
for x in range(31, 34):
    S.set(x, 42, SK_OUT)
S.set(29, 41, SK_OUT)
S.set(35, 41, SK_OUT)
S.set(30, 41, hexc("#ffffff"))
S.set(34, 41, hexc("#ffffff"))
blush(S, 20, 38)
blush(S, 43, 38)
S.set(22, 27, GLINT)

finish(S, "goro")
