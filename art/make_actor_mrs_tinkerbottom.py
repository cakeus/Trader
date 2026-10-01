"""Mrs. Tinkerbottom: a fawn mouse milliner with big round ears, a little straw hat of her
own making perched between them, a teal blouse, a tape measure round her neck and a leather
apron with a spool of thread and a needle in the pocket."""
from pixelkit import hexc, ellipse, edge, rect
from portraitkit import new, line, eye, blush, clip, finish, smile, GLINT

S = new()

FUR = [hexc("#f4dcbc"), hexc("#dcb48a"), hexc("#bc8e66"), hexc("#98704e")]
F_OUT = hexc("#4a2e1e")
EAR_IN = hexc("#f6b0b8")
BLOUSE = [hexc("#a8ece0"), hexc("#5cc8b8"), hexc("#3a9c94"), hexc("#2a7a76")]
BL_OUT = hexc("#123a3a")
APRON = [hexc("#c89a6a"), hexc("#a0703e"), hexc("#7a5230")]
AP_OUT = hexc("#3e2410")
STRAW = [hexc("#fff0b8"), hexc("#f5d27a"), hexc("#dcaa52"), hexc("#b27c36")]
SW_OUT = hexc("#6b4220")
RIBBON = [hexc("#ffb0c0"), hexc("#f27a96"), hexc("#c84a6e")]
TAPE = [hexc("#fff0a0"), hexc("#f2c84a"), hexc("#c8962a")]
TP_OUT = hexc("#6a4a12")
THREAD = [hexc("#ff9a86"), hexc("#e8524a"), hexc("#b0343a")]
STEEL = [hexc("#f0f0f8"), hexc("#868aa0")]
NOSE = hexc("#e87890")

# blouse + apron bib
blouse = clip(ellipse(32, 64, 26, 14))
S.blob(blouse, BLOUSE, BL_OUT, cuts=(-0.5, 0.2, 0.7))
apron = rect(23, 53, 19, 11)
S.blob(apron, APRON, AP_OUT, cuts=(-0.3, 0.5))
for (x, y) in ((24, 52), (23, 51), (40, 52), (41, 51)):
    S.set(x, y, AP_OUT)
# a spool of red thread in the apron pocket, with a needle beside it
spool = rect(33, 50, 5, 7)
S.blob(spool, THREAD, AP_OUT, cuts=(-0.3, 0.5))
for x in range(32, 39):
    S.set(x, 49, APRON[2])
    S.set(x, 57, APRON[2])
for y in range(51, 56, 2):
    S.set(35, y, THREAD[2])
for p in line(40, 49, 40, 57):
    S.set(*p, STEEL[0] if p[1] < 52 else STEEL[1])
pocket = rect(31, 56, 10, 5)
S.blob(pocket, APRON, AP_OUT, cuts=(0.0, 0.6))
# tape measure draped round the neck, hanging down both sides of the bib
for x0 in (19, 43):
    tape = rect(x0, 47, 3, 17)
    S.blob(tape, TAPE, TP_OUT, cuts=(-0.2, 0.6))
    for y in range(49, 63, 3):
        S.set(x0 + 1, y, TP_OUT)

# big round ears
for cx in (13, 51):
    ear = ellipse(cx, 20, 9, 9)
    S.blob(ear, FUR, F_OUT, cuts=(-0.4, 0.3, 0.7))
    inner = ellipse(cx, 21, 5.5, 5.5) - edge(ear)
    S.fill(inner, EAR_IN)
    S.set(cx - 3, 17, hexc("#ffd4d8"))

# head
head = ellipse(32, 34, 15, 13)
S.blob(head, FUR, F_OUT, cuts=(-0.5, 0.25, 0.75))

# a little straw hat perched on top, with a pink ribbon
crown = ellipse(32, 20, 7, 5) & {(x, y) for x in range(64) for y in range(0, 22)}
S.blob(crown, STRAW, SW_OUT, cuts=(-0.45, 0.25, 0.7))
for (x, y) in crown - edge(crown):
    if y in (19, 20):
        S.set(x, y, RIBBON[0] if x < 29 else RIBBON[2] if x > 35 else RIBBON[1])
brim = ellipse(32, 22, 13, 2.6)
brim -= {(x, y) for (x, y) in brim if y < 22 and abs(x - 32) < 7}
S.blob(brim, STRAW, SW_OUT, lx=0.9, ly=0.4, cuts=(-0.55, 0.2, 0.7))
S.set(29, 16, GLINT)

# face
eye(S, 25, 32, 3, 4)
eye(S, 37, 32, 3, 4)
nose = ellipse(32, 39, 2, 1.6)
S.fill(nose, NOSE)
S.set(31, 38, GLINT)
smile(S, 30, 41, 5, F_OUT)
for (x, y) in ((22, 39), (21, 41), (42, 39), (43, 41)):   # whiskers
    S.set(x, y, FUR[3])
blush(S, 22, 37)
blush(S, 41, 37)

finish(S, "mrs_tinkerbottom")
