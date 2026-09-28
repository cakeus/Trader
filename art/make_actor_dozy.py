"""Dozy: a dormouse refusing to hibernate on principle. Big round ears,
heavy half-lidded eyes with bags under them, a droopy striped nightcap with a
pompom, and a lavender mug of cocoa clutched in both paws."""
from pixelkit import hexc, ellipse, edge, rect, rounded_rect
from portraitkit import new, poly, eye, blush, clip, finish, fuzz, GLINT, EYE_DARK

S = new()

FUR = [hexc("#f4c890"), hexc("#dca060"), hexc("#b87a44"), hexc("#94602e")]
F_OUT = hexc("#4a2a14")
BELLY = [hexc("#fff6e4"), hexc("#f8e4c4"), hexc("#e4c8a0")]
EAR_IN = hexc("#f4a8a0")
CAP = [hexc("#e0f4dc"), hexc("#a8d8a0"), hexc("#78b478"), hexc("#588c5c")]
CAP_OUT = hexc("#24442a")
STRIPE = [hexc("#fff8ec"), hexc("#f0e6d4"), hexc("#d8ccb8")]
POM = [hexc("#fffaf0"), hexc("#f4ecdc"), hexc("#d8ccb8")]
POM_OUT = hexc("#7a6a58")
PJ = [hexc("#c8d8ff"), hexc("#98acec"), hexc("#7488cc"), hexc("#5a6aa8")]
PJ_OUT = hexc("#262e5a")
MUG = [hexc("#e4d4ff"), hexc("#b8a0f0"), hexc("#9078d0"), hexc("#6e58ac")]
MUG_OUT = hexc("#32225a")
COCOA = hexc("#8a4e32")
MALLOW = hexc("#fffaf4")
STEAM = hexc("#e4dcf4")
STEAM_D = hexc("#b4aad4")
BAGS = hexc("#c08aa0")

# pyjama shoulders with little buttons
body = clip(ellipse(32, 66, 25, 15))
S.blob(body, PJ, PJ_OUT, cuts=(-0.5, 0.2, 0.7))
for x in range(12, 54, 4):   # pinstripes
    for y in range(52, 64):
        if (x, y) in body and (x, y) not in edge(body):
            S.set(x, y, PJ[2] if x > 32 else PJ[1])

# big round ears
for cx in (13, 51):
    ear = ellipse(cx, 22, 8, 7.6)
    S.blob(ear, FUR, F_OUT, cuts=(-0.3, 0.3, 0.7))
    S.blob(ellipse(cx, 22.5, 4.6, 4.4), [EAR_IN, EAR_IN, hexc("#dc8a88")], None, cuts=(0.3,))

# round fluffy head
head = fuzz(ellipse(32, 33, 16, 14), period=4)
S.blob(head, FUR, F_OUT, cuts=(-0.5, 0.2, 0.7))
face = ellipse(32, 39, 9, 6) - edge(head)
S.blob(face, BELLY, None, cuts=(-0.2, 0.6))

# droopy striped nightcap flopping over to the right
cap = poly([(16, 26), (48, 26), (46, 17), (40, 11), (32, 9), (24, 11), (18, 18)])
tip = poly([(40, 11), (46, 17), (52, 22), (56, 30), (54, 33), (50, 26), (44, 20)])
S.blob(cap | tip, CAP, CAP_OUT, cuts=(-0.45, 0.2, 0.7), center=(30, 18))
inner = (cap | tip) - edge(cap | tip)
for (x, y) in inner:
    if (x + y) % 6 in (0, 1):
        S.set(x, y, STRIPE[0] if x < 32 else STRIPE[1] if x < 44 else STRIPE[2])
cuff = poly([(15, 23), (49, 23), (49, 28), (15, 28)])
S.blob(cuff, STRIPE, POM_OUT, cuts=(-0.3, 0.4))
pom = fuzz(ellipse(55, 34, 3.4, 3.4), period=2)
S.blob(pom, POM, POM_OUT, cuts=(-0.2, 0.5))
S.set(25, 13, GLINT)

# sleepy half-lidded eyes with bags underneath
for ex in (22, 37):
    for x in range(ex, ex + 5):
        S.set(x, 32, EYE_DARK)
        S.set(x, 33, EYE_DARK)
    S.set(ex, 32, F_OUT)
    S.set(ex + 4, 32, F_OUT)
    for x in range(ex - 1, ex + 6):   # heavy lid
        S.set(x, 31, FUR[3])
    S.set(ex + 1, 33, GLINT)
    for x in range(ex, ex + 5):       # bags
        S.set(x, 35, BAGS)

# tiny nose and a yawning mouth
S.fill(ellipse(32, 37, 1.8, 1.3), hexc("#c85a6a"))
S.set(31, 36, GLINT)
S.fill({(31, 40), (32, 40), (33, 40), (31, 41), (32, 41), (33, 41)}, hexc("#8a3a4a"))
S.set(32, 42, hexc("#8a3a4a"))
blush(S, 20, 38)
blush(S, 42, 38)

# lavender mug held in both paws
MX, MY = 24, 46
mug = rounded_rect(MX, MY, 16, 14, r=2)
S.blob(mug, MUG, MUG_OUT, lx=1.0, ly=0.25, cuts=(-0.55, 0.25, 0.75))
S.rows(["zzzz", "..z.", ".z..", "zzzz"], {"z": MUG[3]}, MX + 6, MY + 5)   # a big Z on the mug
rim = ellipse(MX + 7.5, MY, 8, 2.4)
S.blob(rim, [MUG[0], MUG[0], MUG[1]], MUG_OUT, cuts=(0.2,))
S.fill(ellipse(MX + 7.5, MY + 0.4, 6, 1.2), COCOA)
S.fill({(MX + 5, MY), (MX + 6, MY), (MX + 5, MY - 1), (MX + 6, MY - 1)}, MALLOW)
S.set(MX + 2, MY + 3, GLINT)
S.set(MX + 2, MY + 4, GLINT)
for cx in (MX, MX + 15):
    paw = ellipse(cx, MY + 8, 3.6, 3.4)
    S.blob(paw, FUR, F_OUT, cuts=(-0.2, 0.5))

finish(S, "dozy")
