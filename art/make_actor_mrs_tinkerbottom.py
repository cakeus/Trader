"""Mrs. Tinkerbottom: a fawn mouse tinkerer with big round ears, brass goggles
pushed up on her head, a teal blouse and a leather apron with a wrench."""
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
BRASS = [hexc("#fff0a0"), hexc("#e8b64a"), hexc("#b0802a")]
BR_OUT = hexc("#5a3a10")
LENS = [hexc("#c8f4ff"), hexc("#7ad0e8"), hexc("#4a98b8")]
STEEL = [hexc("#f0f0f8"), hexc("#b8bccc"), hexc("#868aa0")]
ST_OUT = hexc("#3a3a4e")
NOSE = hexc("#e87890")

# blouse + apron bib
blouse = clip(ellipse(32, 64, 26, 14))
S.blob(blouse, BLOUSE, BL_OUT, cuts=(-0.5, 0.2, 0.7))
apron = rect(23, 53, 19, 11)
S.blob(apron, APRON, AP_OUT, cuts=(-0.3, 0.5))
for (x, y) in ((24, 52), (23, 51), (40, 52), (41, 51)):
    S.set(x, y, AP_OUT)
# wrench poking out of the apron pocket
wr = line(36, 48, 36, 58, width=2)
S.blob(wr, STEEL, ST_OUT, cuts=(-0.1, 0.6))
jaw = ellipse(36, 47, 2.6, 2.6)
S.blob(jaw, STEEL, ST_OUT, cuts=(-0.1, 0.6))
S.set(36, 46, BL_OUT)
S.set(36, 45, BL_OUT)
pocket = rect(31, 56, 10, 5)
S.blob(pocket, APRON, AP_OUT, cuts=(0.0, 0.6))

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

# goggles on the forehead
strap = {(x, 25) for x in range(18, 47)} | {(x, 26) for x in range(18, 47)}
for p in strap:
    if p in head:
        S.set(*p, AP_OUT)
for cx in (26, 38):
    rim = ellipse(cx, 25, 5, 4.4)
    S.blob(rim, BRASS, BR_OUT, cuts=(-0.2, 0.5))
    glass = ellipse(cx, 25, 3, 2.6)
    S.blob(glass, LENS, None, cuts=(-0.2, 0.5))
    S.set(cx - 1, 24, GLINT)

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
