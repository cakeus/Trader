"""Brunhilde: a badger blacksmith in a red polka-dot headscarf and a leather
apron, a soot smudge on her cheek and a heavy pickaxe over her shoulder."""
import math

from pixelkit import hexc, ellipse, edge, rect
from portraitkit import new, poly, eye, blush, clip, finish, smile, GLINT

S = new()

FACE = [hexc("#ffffff"), hexc("#f2eef0"), hexc("#d8d0d8"), hexc("#b8aebc")]
FC_OUT = hexc("#4a3e50")
STRIPE = [hexc("#6a6070"), hexc("#4a4250"), hexc("#3a3440")]
GREY = [hexc("#c8c4cc"), hexc("#a09aa8"), hexc("#7e7888"), hexc("#625c6c")]
SCARF = [hexc("#ff9a8a"), hexc("#e8404a"), hexc("#b82a3c"), hexc("#8a1e34")]
SC_OUT = hexc("#4a0e1e")
DOT = hexc("#fff4e4")
SHIRT = [hexc("#a8d8e0"), hexc("#6aa8b8"), hexc("#4a8098"), hexc("#386478")]
SH_OUT = hexc("#16303e")
APRON = [hexc("#d09a64"), hexc("#a8703e"), hexc("#86542c"), hexc("#663e20")]
AP_OUT = hexc("#3a2010")
RIVET = hexc("#ffd24a")
SOOT = hexc("#8a8290")
NOSE = hexc("#3a2a36")
WOOD = [hexc("#f0c488"), hexc("#d0924e"), hexc("#a8683a"), hexc("#7e4a2a")]
WOOD_OUT = hexc("#4a2a1c")
STEEL = [hexc("#e4eef8"), hexc("#a8bcd4"), hexc("#7890b0"), hexc("#566a8c")]
STEEL_OUT = hexc("#27304a")
WRAP = [hexc("#8ab8c8"), hexc("#5a8aa0"), hexc("#3e6478")]


def pickaxe(S, base, top, half=11.0, bend=4.0, thick=2.4, hw=1.4):
    """A pickaxe like the good's icon: handle from base to top, curved head at top."""
    L = math.hypot(top[0] - base[0], top[1] - base[1])
    D = ((top[0] - base[0]) / L, (top[1] - base[1]) / L)
    N = (-D[1], D[0])

    def frame(x, y):
        dx, dy = x + 0.5 - base[0], y + 0.5 - base[1]
        return dx * D[0] + dy * D[1], dx * N[0] + dy * N[1]

    def region(test):
        return {(x, y) for y in range(64) for x in range(64) if test(*frame(x, y))}

    def hc(v):
        t = min(1.0, abs(v) / half)
        return L - bend * t * t

    handle = region(lambda u, v: 0 <= u <= L and abs(v) <= hw)
    wrap = region(lambda u, v: 1 <= u <= 6 and abs(v) <= hw + 0.4)
    head = region(lambda u, v: abs(v) <= half and
                  abs(u - hc(v)) <= thick * (1 - min(1, abs(v) / half) ** 1.6) + 0.55)
    collar = region(lambda u, v: L - 2.8 <= u <= L + 1.8 and abs(v) <= hw + 1.2)
    S.blob(handle, WOOD, WOOD_OUT, lx=0.6, ly=0.6)
    S.blob(wrap, WRAP, WOOD_OUT, lx=0.6, ly=0.6, cuts=(-0.2, 0.5))
    S.blob(head, STEEL, STEEL_OUT, lx=0.65, ly=0.65, cuts=(-0.4, 0.15, 0.6))
    S.blob(collar, STEEL[1:], STEEL_OUT, lx=0.6, ly=0.6, cuts=(-0.2, 0.4))
    for (x, y) in head - edge(head):
        u, v = frame(x, y)
        if u - hc(v) > 0.5 and abs(v) < half - 2.5:
            S.set(x, y, STEEL[0])


# heavy pickaxe resting on her right shoulder, head up behind her
pickaxe(S, (44, 63), (53, 9), half=14, bend=5, thick=3.0, hw=1.6)

# shirt shoulders with rolled sleeves, leather apron bib
shirt = clip(ellipse(32, 64, 27, 14))
S.blob(shirt, SHIRT, SH_OUT, cuts=(-0.5, 0.2, 0.7))
apron = poly([(21, 52), (43, 52), (45, 64), (19, 64)])
S.blob(apron, APRON, AP_OUT, cuts=(-0.3, 0.3, 0.75))
for (x, y) in ((22, 51), (21, 50), (20, 49), (42, 51), (43, 50), (44, 49)):   # neck strap
    S.set(x, y, AP_OUT)
pocket = rect(27, 57, 11, 6)
S.blob(pocket, APRON[1:], AP_OUT, cuts=(-0.2, 0.5))
for (x, y) in ((22, 54), (42, 54), (28, 58), (36, 58)):
    S.set(x, y, RIVET)
# her paw gripping the handle
paw = ellipse(46, 52, 4.4, 3.6)
S.blob(paw, GREY, FC_OUT, cuts=(-0.3, 0.3, 0.75))
for x in (44, 46, 48):   # knuckles
    S.set(x, 50, GREY[3])
    S.set(x, 51, GREY[3])

# small round ears with pale rims
for cx in (17, 47):
    ear = ellipse(cx, 27, 3.8, 3.6)
    S.blob(ear, GREY, FC_OUT, cuts=(-0.2, 0.5))
    S.set(cx, 27, STRIPE[2])

# grey cheeks behind a white face
head = ellipse(32, 35, 16, 13)
S.blob(head, GREY, FC_OUT, cuts=(-0.5, 0.25, 0.75))
face = ellipse(32, 37, 11, 11) - edge(head)
S.blob(face, FACE, None, cuts=(-0.3, 0.3, 0.75))
# the two dark stripes running up over the eyes
for sx in (-1, 1):
    stripe = poly([(32 + sx * 2.5, 41), (32 + sx * 3, 22), (32 + sx * 10, 22), (32 + sx * 6.5, 41)])
    S.blob(stripe & head - edge(head), STRIPE, None, cuts=(-0.6, 0.6))
# white blaze down the middle stays white; nose at the bottom
nose = ellipse(32, 42, 3, 2.2)
S.fill(nose, NOSE)
S.set(31, 41, GLINT)
smile(S, 29, 45, 7, FC_OUT)

# headscarf knotted at the side
scarf = ellipse(32, 26, 17, 9) & {(x, y) for x in range(64) for y in range(0, 28)}
S.blob(scarf, SCARF, SC_OUT, cuts=(-0.4, 0.3, 0.75))
band = poly([(15, 25), (49, 25), (49, 29), (15, 29)]) & (ellipse(32, 27, 17.5, 9))
S.blob(band, SCARF, SC_OUT, cuts=(-0.2, 0.5, 0.85))
for (x, y) in ((22, 21), (28, 18), (35, 20), (41, 22), (25, 25), (39, 26), (31, 23), (18, 27), (45, 27)):
    if (x, y) in scarf or (x, y) in band:
        S.set(x, y, DOT)
knot = ellipse(13, 27, 3.4, 3) | ellipse(11, 32, 2.4, 3.2) | ellipse(15, 32, 2, 3)
S.blob(knot, SCARF, SC_OUT, cuts=(-0.3, 0.4, 0.8))
S.set(24, 19, GLINT)
S.set(25, 18, GLINT)

# eyes sit in the stripes
EYE = hexc("#140a18")
for ex in (26, 36):
    eye(S, ex, 33, 3, 3, dark=EYE)
    S.set(ex + 1, 33, GLINT)
blush(S, 21, 39)
blush(S, 42, 39)
# soot smudge
for (x, y) in ((40, 41), (41, 41), (42, 42), (40, 42)):
    S.set(x, y, SOOT)

finish(S, "brunhilde")
