"""Mama Mugsworth: a big brown bear who runs the cocoa cart, in a red knit
scarf, holding up a steaming mug of cocoa topped with a marshmallow."""
from pixelkit import hexc, ellipse, edge, rect, rounded_rect
from portraitkit import new, poly, eye, blush, clip, finish, smile, GLINT

S = new()

FUR = [hexc("#d09a6a"), hexc("#a8703e"), hexc("#86542e"), hexc("#643c22")]
F_OUT = hexc("#3a2014")
MUZ = [hexc("#fbe6c8"), hexc("#ecc89c"), hexc("#d0a678")]
APRON = [hexc("#fff8ec"), hexc("#f0e2cc"), hexc("#d8c4a6")]
AP_OUT = hexc("#7a6248")
SCARF = [hexc("#ff9a8a"), hexc("#e0474c"), hexc("#b83244"), hexc("#8c2238")]
SC_OUT = hexc("#5a1626")
MUG = [hexc("#fff0a0"), hexc("#f4c24a"), hexc("#d89a2c"), hexc("#b07620")]
MUG_OUT = hexc("#5e3a12")
COCOA = [hexc("#b0704a"), hexc("#8a4e32"), hexc("#6a3624")]
MALLOW = [hexc("#fffaf4"), hexc("#f8e4e8"), hexc("#e8c0cc")]
MALLOW_OUT = hexc("#9a6070")
STEAM = hexc("#e4dcf4")
STEAM_D = hexc("#b4aad4")

# body with a cream apron
body = clip(ellipse(32, 66, 29, 16))
S.blob(body, FUR, F_OUT, cuts=(-0.5, 0.2, 0.7))
apron = clip(poly([(22, 52), (42, 52), (46, 64), (18, 64)]))
S.blob(apron, APRON, AP_OUT, cuts=(-0.4, 0.3, 0.75))

# round ears
for cx in (15, 49):
    ear = ellipse(cx, 19, 6, 5.6)
    S.blob(ear, FUR, F_OUT, cuts=(-0.3, 0.3, 0.7))
    inner = ellipse(cx, 19.5, 3, 2.8)
    S.fill(inner, MUZ[2])

# big round head
head = ellipse(32, 31, 19, 16)
S.blob(head, FUR, F_OUT, cuts=(-0.5, 0.2, 0.7))

# chunky knit scarf around the neck
scarf = ellipse(32, 48, 20, 5)
S.blob(scarf, SCARF, SC_OUT, cuts=(-0.4, 0.3, 0.75))
for x in range(15, 50, 3):
    S.set(x, 48, SCARF[2])
    S.set(x + 1, 49, SCARF[2])
tail = poly([(40, 49), (47, 49), (48, 60), (41, 60)])
S.blob(tail, SCARF, SC_OUT, cuts=(-0.3, 0.4, 0.8))
for y in range(52, 59, 2):
    S.set(43, y, SCARF[2])
    S.set(45, y + 1, SCARF[2])
for x in range(42, 48, 2):   # fringe
    S.set(x, 61, SCARF[3])

# a little daisy tucked behind her right ear
PET = [hexc("#ffffff"), hexc("#f8eef4"), hexc("#e0ccd8")]
for (dx, dy) in ((0, -2), (2, 0), (0, 2), (-2, 0)):
    S.blob(ellipse(50 + dx, 14 + dy, 1.8, 1.8), PET, hexc("#9a6a80"), cuts=(0.0, 0.7))
S.fill(ellipse(50, 14, 1.2, 1.2), hexc("#ffd24a"))
S.set(50, 14, hexc("#e8a22c"))

# muzzle, eyes, nose
muz = ellipse(32, 38, 9, 6.5)
S.blob(muz, MUZ, F_OUT, cuts=(-0.3, 0.5))
eye(S, 22, 28, 3, 4)
eye(S, 39, 28, 3, 4)
nose = ellipse(32, 35, 3.6, 2.4)
S.fill(nose, F_OUT)
S.set(31, 34, GLINT)
S.set(32, 38, F_OUT)
smile(S, 29, 39, 7, F_OUT)
blush(S, 18, 35)
blush(S, 44, 35)

# steaming mug held up in her paw, lower left
MX, MY = 7, 43
handle = {p for p in ellipse(MX + 17.5, MY + 7, 4.4, 4.4) - ellipse(MX + 17.5, MY + 7, 2, 2) if p[0] >= MX + 16}
S.blob(handle, MUG, MUG_OUT, cuts=(-0.1, 0.5))
mug = rounded_rect(MX, MY, 17, 15, r=2)
S.blob(mug, MUG, MUG_OUT, lx=1.0, ly=0.25, cuts=(-0.55, 0.25, 0.75))
for x in range(MX + 3, MX + 15, 3):   # little stripe band
    S.set(x, MY + 8, SCARF[1])
    S.set(x + 1, MY + 8, SCARF[1])
rim = ellipse(MX + 8, MY, 8.5, 2.6)
S.blob(rim, [MUG[0], MUG[0], MUG[1]], MUG_OUT, cuts=(0.2,))
S.fill(ellipse(MX + 8, MY + 0.4, 6.6, 1.3), COCOA[1])
mallow = rect(MX + 5, MY - 4, 6, 5)
S.blob(mallow, MALLOW, MALLOW_OUT, cuts=(-0.1, 0.6))
S.set(MX + 2, MY + 3, GLINT)
S.set(MX + 2, MY + 4, GLINT)
# paw wrapped round the mug
paw = ellipse(MX + 15, MY + 12, 4, 3.5)
S.blob(paw, FUR, F_OUT, cuts=(-0.2, 0.5))
# steam curl
for (x, y) in ((MX + 6, MY - 6), (MX + 5, MY - 7), (MX + 5, MY - 8), (MX + 6, MY - 9),
               (MX + 7, MY - 10), (MX + 7, MY - 11), (MX + 6, MY - 12)):
    S.set(x, y, STEAM)
    S.set(x + 1, y, STEAM_D)

finish(S, "mama_mugsworth")
