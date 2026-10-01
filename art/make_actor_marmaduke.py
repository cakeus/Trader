"""Foreman Marmaduke: a chubby golden marmot mine boss in an orange hard hat
with a headlamp, a hi-vis vest, a whistle and a clipboard of lost mittens."""
from pixelkit import hexc, ellipse, edge, rect
from portraitkit import new, poly, line, eye, blush, clip, finish, GLINT

S = new()

FUR = [hexc("#f0c888"), hexc("#d49e5a"), hexc("#b07a40"), hexc("#8a5a2e")]
F_OUT = hexc("#40240e")
MUZ = [hexc("#fff0d8"), hexc("#f0d4b0"), hexc("#d4b08c")]
HAT = [hexc("#ffc890"), hexc("#ff8a3a"), hexc("#e0602a"), hexc("#b04420")]
H_OUT = hexc("#5a1e0e")
LAMP = [hexc("#fffce0"), hexc("#ffe46a"), hexc("#e8b43a")]
METAL = [hexc("#e8ecf4"), hexc("#b0b8c8"), hexc("#80889c")]
MT_OUT = hexc("#343848")
SHIRT = [hexc("#9a8ac8"), hexc("#6e5ea8"), hexc("#524486")]
SH_OUT = hexc("#221a44")
VEST = [hexc("#ffe07a"), hexc("#ffb43a"), hexc("#ec8a2a"), hexc("#c86a20")]
V_OUT = hexc("#5a2a0e")
REFLECT = hexc("#fffae0")
REFLECT_D = hexc("#d8d8c8")
BOARD = [hexc("#d8a870"), hexc("#b08050"), hexc("#8a6038")]
BD_OUT = hexc("#3e2410")
PAPER = hexc("#fffaf0")
INK = hexc("#6a6a8a")
TOOTH = hexc("#fffaf0")
TOOTH_D = hexc("#d8ccb4")
CORD = hexc("#e04a4a")

# purple shirt shoulders under a hi-vis vest
shirt = clip(ellipse(32, 64, 27, 14))
S.blob(shirt, SHIRT, SH_OUT, cuts=(-0.5, 0.2, 0.7))
for side in (-1, 1):
    panel = poly([(32 + side * 4, 51), (32 + side * 21, 53), (32 + side * 26, 64), (32 + side * 5, 64)])
    S.blob(panel & shirt, VEST, V_OUT, cuts=(-0.4, 0.2, 0.7))
    for y in (57, 58):
        for x in range(64):
            if (x, y) in panel and (x, y) in shirt and (x, y) not in edge(panel & shirt):
                S.set(x, y, REFLECT if y == 57 else REFLECT_D)

# whistle on a red cord
for (x, y) in line(24, 49, 31, 56) | line(40, 49, 33, 56):
    S.set(x, y, CORD)
wh = rect(29, 55, 6, 4)
S.blob(wh, METAL, MT_OUT, cuts=(-0.2, 0.5))
S.set(30, 56, GLINT)

# clipboard in his paw
board = rect(41, 50, 12, 14)
S.blob(board, BOARD, BD_OUT, cuts=(-0.3, 0.4))
paper = rect(43, 52, 8, 12)
S.fill(paper, PAPER)
for y in (54, 57, 60):   # tally marks of lost mittens
    for x in (44, 46, 48):
        S.set(x, y, INK)
        S.set(x, y + 1, INK)
    S.set(50, y, INK)
    S.set(43, y + 1, INK)
clip_ = rect(45, 49, 4, 2)
S.blob(clip_, METAL, MT_OUT)
paw = ellipse(41, 57, 3.4, 3)
S.blob(paw, FUR, F_OUT, cuts=(-0.2, 0.5))

# small round ears
for cx in (15, 49):
    ear = ellipse(cx, 27, 3.8, 3.4)
    S.blob(ear, FUR, F_OUT, cuts=(-0.2, 0.5))
    S.set(cx, 27, FUR[3])

# chubby head with puffy cheeks
head = ellipse(32, 35, 17, 14) | ellipse(21, 40, 7, 6) | ellipse(43, 40, 7, 6)
S.blob(head, FUR, F_OUT, cuts=(-0.5, 0.25, 0.75), center=(32, 35))
muz = ellipse(32, 41, 8, 5.5) - edge(head)
S.blob(muz, MUZ, None, cuts=(-0.1, 0.6))

# orange hard hat with a headlamp
dome = ellipse(32, 23, 15, 11) & {(x, y) for x in range(64) for y in range(0, 24)}
S.blob(dome, HAT, H_OUT, cuts=(-0.4, 0.3, 0.75))
brim = ellipse(32, 24, 20, 3)
S.blob(brim, HAT, H_OUT, cuts=(-0.3, 0.4, 0.8))
for y in range(12, 17):   # ridge
    S.set(32, y, HAT[2])
S.set(25, 17, GLINT)
S.set(26, 16, GLINT)
lamp_base = rect(28, 16, 9, 6)
S.blob(lamp_base, METAL, MT_OUT, cuts=(-0.2, 0.5))
lens = ellipse(32, 19, 2.6, 2)
S.blob(lens, LAMP, None, cuts=(-0.2, 0.5))
S.set(31, 18, GLINT)
for (x, y) in ((32, 12), (32, 11), (26, 13), (25, 12), (38, 13), (39, 12)):   # a little beam
    S.set(x, y, LAMP[1])

# face
eye(S, 24, 30, 3, 4)
eye(S, 37, 30, 3, 4)
nose = poly([(29, 36), (36, 36), (32.5, 39)])
S.fill(nose, F_OUT)
S.set(30, 36, GLINT)
S.set(32, 39, F_OUT)
for x in range(29, 36):
    S.set(x, 41 if x in (29, 35) else 42, F_OUT)
for x in (30, 31, 33, 34):
    for y in (43, 44):
        S.set(x, y, TOOTH)
S.set(32, 43, F_OUT)
S.set(32, 44, F_OUT)
S.set(31, 44, TOOTH_D)
S.set(34, 44, TOOTH_D)
for x in range(30, 35):
    S.set(x, 45, F_OUT)
for y in (43, 44):
    S.set(29, y, F_OUT)
    S.set(35, y, F_OUT)
# whisker dots
for (x, y) in ((25, 40), (26, 42), (39, 40), (38, 42)):
    S.set(x, y, FUR[2])
blush(S, 19, 37)
blush(S, 44, 37)

finish(S, "marmaduke")
