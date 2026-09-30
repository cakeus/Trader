"""Gacha-chan: a cheerful capsule-toy (gachapon) machine. A clear dome full
of two-tone capsules, a red cabinet with a face, a big crank, a coin slot and
a capsule with a tiny lucky cat inside popping out of the chute."""
from pixelkit import hexc, ellipse, edge, rect, rounded_rect
from portraitkit import new, line, eye, blush, smile, clip, finish, GLINT

S = new()

RED = [hexc("#ff9a86"), hexc("#e8524a"), hexc("#bc3a3c"), hexc("#942a34")]
RD_OUT = hexc("#521624")
STEEL = [hexc("#ffffff"), hexc("#dfe4ee"), hexc("#aeb6c8"), hexc("#7e88a0")]
ST_OUT = hexc("#343a52")
GLASS = [hexc("#eef8ff"), hexc("#cfe6f4"), hexc("#a8cce4"), hexc("#86b0d0")]
GL_OUT = hexc("#3a5270")
HOLE = hexc("#2a1a2e")
CAPS = [
    [hexc("#ffc0d8"), hexc("#f47aa8"), hexc("#c85080")],
    [hexc("#fff0a0"), hexc("#ffd24a"), hexc("#d8a030")],
    [hexc("#b8e8ff"), hexc("#5ab4ea"), hexc("#3a84c0")],
    [hexc("#c8f4b0"), hexc("#72cc62"), hexc("#48a046")],
    [hexc("#e4ccff"), hexc("#ad86ec"), hexc("#7e5ac4")],
]
CAP_WHITE = [hexc("#ffffff"), hexc("#f0f0f4"), hexc("#d4d4e0")]
CAP_OUT = hexc("#4a3a5a")
CAT = hexc("#fffaf0")


def capsule(cx, cy, r, ramp, out=CAP_OUT, flip=False, within=None):
    m = ellipse(cx, cy, r, r)
    if within is not None:
        m &= within
    top = {(x, y) for (x, y) in m if (y <= cy) != flip}
    for part, rp in ((top, ramp), (m - top, [CAP_WHITE[0], ramp[0], ramp[1]])):
        if part:
            S.blob(part, rp, None, cuts=(-0.3, 0.4), center=(cx, cy))
    S.fill(edge(m), out)
    S.set(round(cx - r * 0.5), round(cy - r * 0.5), GLINT)


# red cabinet
body = clip(rounded_rect(13, 36, 38, 30, 3))
S.blob(body, RED, RD_OUT, cuts=(-0.5, 0.15, 0.7))
for (x, y) in ((15, 38), (16, 38), (15, 39)):
    S.set(x, y, RED[0])

# clear dome of capsules on a steel collar
dome = ellipse(32, 21, 16, 15)
S.blob(dome, GLASS, GL_OUT, cuts=(-0.5, 0.2, 0.7))
inner = dome - edge(dome)
for (cx, cy, r, k) in ((34, 9, 4.5, 1), (22, 12, 4.5, 3), (43, 13, 4.5, 4),
                       (28, 17, 4.5, 2), (38, 20, 4.5, 0), (18, 22, 4.5, 4), (46, 24, 4.5, 3),
                       (26, 26, 4.5, 1), (35, 29, 4.5, 3), (18, 30, 4.5, 2), (44, 31, 4.5, 1),
                       (27, 33, 4.5, 0), (38, 35, 4.5, 4)):
    capsule(cx, cy, r, CAPS[k], flip=(k % 2 == 1), within=inner)
S.fill(edge(dome), GL_OUT)
# glass shine
for (x, y) in ((22, 9), (21, 10), (20, 11), (19, 12), (18, 14), (23, 8), (24, 8)):
    if (x, y) in inner:
        S.set(x, y, GLINT)
# red lid on top
lid = ellipse(32, 6.5, 7, 3)
S.blob(lid, RED, RD_OUT, cuts=(-0.3, 0.4))
S.set(29, 5, RED[0])
# steel collar between dome and cabinet
collar = rounded_rect(12, 33, 40, 5, 2)
S.blob(collar, STEEL, ST_OUT, cuts=(-0.5, 0.2, 0.7))
for x in (16, 24, 40, 48):
    S.set(x, 35, STEEL[3])

# face
eye(S, 23, 40, 3, 4)
eye(S, 38, 40, 3, 4)
smile(S, 29, 44, 6, RD_OUT)
blush(S, 19, 45)
blush(S, 43, 45)

# big crank: a round steel dial with a raised bar across it
dial = ellipse(24, 55, 6.5, 6.5)
S.blob(dial, STEEL, ST_OUT, cuts=(-0.4, 0.2, 0.7))
bar = line(20, 59, 28, 51, 3)
S.blob(bar, RED, RD_OUT, cuts=(-0.3, 0.4), center=(24, 55))
S.set(24, 55, RED[0])
S.set(20, 51, GLINT)
S.set(21, 50, GLINT)
for (x, y) in ((15, 50), (15, 51), (16, 49), (17, 48)):   # turning arc
    S.set(x, y, RED[3])

# coin slot
slot = rect(34, 49, 3, 6)
S.fill(slot, STEEL[2])
S.fill(edge(slot), ST_OUT)
S.set(35, 51, HOLE)
S.set(35, 52, HOLE)

# chute with a capsule popping out (a tiny lucky cat inside)
chute = rounded_rect(39, 51, 10, 11, 2)
S.fill(chute, HOLE)
S.fill(edge(chute), RD_OUT)
for x in range(40, 48):
    S.set(x, 52, hexc("#40283a"))
capsule(44, 57, 4.2, CAPS[1])
# cat in the clear half: flip so the top is clear
m = ellipse(44, 57, 4.2, 4.2)
for (x, y) in m - edge(m):
    if y <= 57:
        S.set(x, y, hexc("#e4f2fa"))
for (x, y) in ((42, 55), (46, 55), (42, 56), (43, 56), (44, 56), (45, 56), (46, 56), (43, 57), (44, 57), (45, 57)):
    S.set(x, y, CAT)
S.set(43, 56, HOLE)
S.set(45, 56, HOLE)
S.set(47, 56, hexc("#e0503f"))
for (x, y) in ((49, 53), (50, 52), (51, 55)):   # pop sparkles
    S.set(x, y, hexc("#fff4d6"))

finish(S, "gacha_chan")
