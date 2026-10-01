"""Scramble: a shaggy white mountain goat ice-climber with curled horns,
goggles pushed up, a rope coil on her shoulder and a mitten dangling from her mouth, a bite
already out of it."""
from pixelkit import hexc, ellipse, edge, rect
from portraitkit import new, poly, curve, eye, blush, clip, finish, fuzz, GLINT

S = new()

FUR = [hexc("#ffffff"), hexc("#eef0f6"), hexc("#d4d6e4"), hexc("#b0b2c8")]
F_OUT = hexc("#54567a")
HORN = [hexc("#f0e2c4"), hexc("#ccb48c"), hexc("#a48a64"), hexc("#7e6848")]
HN_OUT = hexc("#3e3020")
JACKET = [hexc("#9ae0d8"), hexc("#4ab8b0"), hexc("#2e8c8c"), hexc("#226a6e")]
J_OUT = hexc("#0e3638")
ROPE = [hexc("#ffc090"), hexc("#f07048"), hexc("#c0443a"), hexc("#94303a")]
RP_OUT = hexc("#521820")
STRAP = [hexc("#c8a0f0"), hexc("#9a6ad0"), hexc("#7048a8")]
ST_OUT = hexc("#2e1a52")
LENS = [hexc("#e0fcff"), hexc("#7ad8f0"), hexc("#3e98c8"), hexc("#2a6a9c")]
RIM = hexc("#2e1a52")
NOSE = hexc("#8a6a80")
MOUTH = hexc("#54567a")
MIT = [hexc("#ff9a86"), hexc("#e8524a"), hexc("#b8383c"), hexc("#8a2630")]
MIT_OUT = hexc("#5e1c24")
CUFF = [hexc("#fffbea"), hexc("#f2e2c0"), hexc("#c2a67c")]


# puffy climbing jacket
jacket = clip(ellipse(32, 64, 28, 13))
S.blob(jacket, JACKET, J_OUT, cuts=(-0.5, 0.2, 0.7))
for y in (56, 60):   # puffer quilting
    for x in range(64):
        if (x, y) in jacket and (x, y) not in edge(jacket):
            S.set(x, y, JACKET[3] if x > 32 else JACKET[2])
for y in range(52, 64):   # zip
    S.set(32, y, J_OUT)

# rope coil slung over her shoulder
for i, (dx, dy, rx, ry) in enumerate(((0, 0, 9.5, 7), (2, -1, 9, 6.5), (4, -2, 8.5, 6))):
    cx, cy = 13 + dx, 56 + dy
    loop = ellipse(cx, cy, rx, ry) - ellipse(cx, cy, rx - 2.6, ry - 2.6)
    S.blob(loop, ROPE, RP_OUT, cuts=(-0.5, 0.3, 0.8), center=(cx, cy))


# curling horns, sweeping back and out
for side in (-1, 1):
    pts = [(32 + side * 6, 22), (32 + side * 9, 13), (32 + side * 15, 8),
           (32 + side * 20, 10), (32 + side * 21, 15)]
    horn = curve(pts[:3], width=7.5) | curve(pts[2:], width=5)
    S.blob(horn, HORN, HN_OUT, cuts=(-0.4, 0.2, 0.7))
    for i, (x, y) in enumerate(curve(pts[:4], width=1)):
        if i % 3 == 0 and (x, y) in horn - edge(horn):
            S.set(x, y, HORN[3])

# floppy sideways ears
for side in (-1, 1):
    ear = ellipse(32 + side * 17, 30, 6.5, 3)
    S.blob(ear, FUR, F_OUT, cuts=(-0.2, 0.5))
    S.set(32 + side * 18, 30, hexc("#f6b0b8"))
    S.set(32 + side * 17, 30, hexc("#f6b0b8"))

# long shaggy head
head = fuzz(ellipse(32, 31, 13, 11) | ellipse(32, 40, 10, 8), period=3)
S.blob(head, FUR, F_OUT, cuts=(-0.5, 0.25, 0.75), center=(32, 34))
for (x, y) in ((27, 38), (36, 39), (29, 42), (35, 43)):   # tufts
    S.set(x, y, FUR[2])

# little beard
beard = fuzz(poly([(27, 46), (37, 46), (35, 54), (32, 57), (29, 54)]), period=2)
S.blob(beard, FUR, F_OUT, cuts=(-0.3, 0.4, 0.8))

# goggles pushed up on the forehead
strap = rect(19, 20, 27, 3)
S.blob(strap, STRAP, ST_OUT, cuts=(-0.2, 0.5))
for cx in (26, 38):
    lens = ellipse(cx, 21, 5, 4)
    S.blob(lens, LENS, RIM, cuts=(-0.4, 0.2, 0.7))
    S.set(cx - 2, 22, GLINT)
    S.set(cx - 1, 21, GLINT)

# face
eye(S, 25, 29, 3, 3)
eye(S, 37, 29, 3, 3)
S.set(26, 32, hexc("#2a1a2e"))
S.set(38, 32, hexc("#2a1a2e"))
for x in (29, 35):
    S.set(x, 39, NOSE)
    S.set(x, 40, NOSE)
blush(S, 21, 35)
blush(S, 41, 35)

# a mitten dangling from her mouth by its cuff, upside down, with a bite out of the bottom
hand = rect(30, 46, 9, 5) | {(x, y) for (x, y) in ellipse(34.0, 50.5, 4.5, 5.5) if y >= 51}
thumb = ellipse(40.6, 49.4, 2.2, 3.2) | {(39, 47), (39, 48)}
hand -= ellipse(30.5, 55.5, 2.4, 2.4)   # the bite
S.blob(hand | thumb, MIT, MIT_OUT, cuts=(-0.5, 0.25, 0.7))
for y in range(49, 53):   # the gap between thumb and hand
    S.set(39, y, MIT_OUT)
for (x, y) in ((32, 47), (31, 48)):
    S.set(x, y, MIT[0])
for x in range(31, 39):   # the cream knit stripe, as on the good's icon
    S.set(x, 50, CUFF[0] if x < 33 else CUFF[1])
    S.set(x, 51, CUFF[1] if x % 2 else MIT[1])
cuff = rect(30, 42, 10, 5)
S.blob(cuff, CUFF, MIT_OUT, cuts=(-0.4, 0.5))
for x in range(31, 39, 2):
    S.set(x, 45, CUFF[2])
for x in range(27, 30):   # lips either side of the cuff
    S.set(x, 44, MOUTH)
S.set(40, 44, MOUTH)
S.set(26, 43, MOUTH)
S.set(41, 43, MOUTH)

finish(S, "scramble")
