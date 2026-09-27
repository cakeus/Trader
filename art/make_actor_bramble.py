"""Bramble the Beaver: a carpenter in a yellow hard hat, red plaid flannel
and suspenders, flashing big buck teeth."""
from pixelkit import hexc, ellipse, edge
from portraitkit import new, poly, eye, blush, clip, finish, GLINT

S = new()

FUR = [hexc("#d09a6a"), hexc("#a86c3e"), hexc("#86502c"), hexc("#663a20")]
F_OUT = hexc("#341a0e")
MUZ = [hexc("#f4dcc0"), hexc("#dcb898"), hexc("#bc947a")]
PLAID = [hexc("#ff8a7a"), hexc("#e0443e"), hexc("#b02c34"), hexc("#882234")]
PL_OUT = hexc("#4a1018")
PLAID_LINE = hexc("#6a1a2a")
SUSP = hexc("#3b4a7a")
HAT = [hexc("#fff4a0"), hexc("#ffd23a"), hexc("#e8a020"), hexc("#c07a14")]
H_OUT = hexc("#6a4410")
TOOTH = hexc("#fffaf0")
TOOTH_D = hexc("#d8ccb4")

# plaid flannel shoulders
shirt = clip(ellipse(32, 64, 27, 14))
S.blob(shirt, PLAID, PL_OUT, cuts=(-0.5, 0.2, 0.7))
inner = shirt - edge(shirt)
for (x, y) in inner:
    if x % 6 == 0 or y % 5 == 0:
        S.set(x, y, PLAID_LINE if (x % 6 == 0 and y % 5 == 0) else PLAID[3] if x > 32 else PLAID[2])
# suspenders
for y in range(51, 64):
    for x in (22 + (y - 51) // 5, 42 - (y - 51) // 5):
        if (x, y) in shirt:
            S.set(x, y, SUSP)
            S.set(x + 1, y, SUSP)

# small round ears
for cx in (17, 47):
    ear = ellipse(cx, 24, 3.6, 3.4)
    S.blob(ear, FUR, F_OUT, cuts=(-0.2, 0.5))

# head
head = ellipse(32, 34, 17, 15)
S.blob(head, FUR, F_OUT, cuts=(-0.5, 0.25, 0.75))

# hard hat
dome = ellipse(32, 22, 14, 10) & {(x, y) for x in range(64) for y in range(0, 23)}
S.blob(dome, HAT, H_OUT, cuts=(-0.4, 0.3, 0.75))
brim = ellipse(32, 23, 19, 3)
S.blob(brim, HAT, H_OUT, cuts=(-0.3, 0.4, 0.8))
for y in range(13, 22):   # ridge
    S.set(32, y, HAT[2])
S.set(25, 16, GLINT)
S.set(26, 15, GLINT)

# face
eye(S, 24, 29, 3, 4)
eye(S, 37, 29, 3, 4)
muz = ellipse(32, 39, 9, 6)
S.blob(muz, MUZ, None, cuts=(-0.1, 0.6))
nose = poly([(29, 34), (35, 34), (32, 37)])
S.fill(nose, F_OUT)
S.set(30, 34, GLINT)
for x in range(29, 36):
    S.set(x, 40, F_OUT)
# big buck teeth
for x in (30, 31, 33, 34):
    for y in (41, 42, 43):
        S.set(x, y, TOOTH)
for y in (41, 42, 43):
    S.set(32, y, F_OUT)
S.set(31, 43, TOOTH_D)
S.set(34, 43, TOOTH_D)
for x in range(30, 35):
    S.set(x, 44, F_OUT)
blush(S, 20, 36)
blush(S, 43, 36)

finish(S, "bramble")
