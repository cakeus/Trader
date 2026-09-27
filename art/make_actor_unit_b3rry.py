"""Unit B-3RRY: a round mint gardening robot with a screen face,
happy ^^ eyes, and a strawberry on its antenna."""
from pixelkit import hexc, ellipse, edge, rect, rounded_rect
from portraitkit import new, line, clip, finish, GLINT

S = new()

METAL = [hexc("#e2fff0"), hexc("#a6e4cc"), hexc("#74c2aa"), hexc("#52988a")]
M_OUT = hexc("#23484c")
DARK = [hexc("#9aa0b8"), hexc("#707690"), hexc("#50566e")]
D_OUT = hexc("#262a3e")
SCREEN = hexc("#1e3440")
SCREEN_L = hexc("#2c4a56")
GLOW = hexc("#8ef0a0")
GLOW_L = hexc("#d4ffd8")
BERRY = [hexc("#ff8a7a"), hexc("#e83a48"), hexc("#b0263a")]
BE_OUT = hexc("#5c1424")
LEAF = hexc("#5cbc4c")
LEAF_OUT = hexc("#1e4a2a")
PINK = hexc("#ff8ab0")


def squircle(cx, cy, rx, ry, p=4):
    return {(x, y) for y in range(int(cy - ry) - 1, int(cy + ry) + 2)
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2)
            if abs((x - cx) / rx) ** p + abs((y - cy) / ry) ** p <= 1}


# shoulders / chassis
chassis = clip(squircle(32, 62, 22, 10))
S.blob(chassis, METAL, M_OUT, cuts=(-0.5, 0.2, 0.7))
panel = rounded_rect(26, 55, 12, 8, 1)
S.blob(panel, DARK, D_OUT, cuts=(-0.3, 0.4))
# leaf emblem
for (x, y) in ((31, 58), (32, 57), (33, 57), (31, 59), (32, 58), (30, 60)):
    S.set(x, y, LEAF)
S.set(33, 56, GLOW_L)

# neck
S.blob(rect(28, 48, 8, 5), DARK, D_OUT, cuts=(-0.2, 0.5))

# ear bolts
for x0 in (8, 51):
    bolt = rounded_rect(x0, 27, 6, 11, 1)
    S.blob(bolt, DARK, D_OUT, cuts=(-0.3, 0.4))

# antenna + strawberry
S.fill(line(32, 16, 32, 10), D_OUT)
S.set(33, 12, DARK[0])
berry = ellipse(32, 6, 3.6, 4) | {(32, 10), (31, 9), (33, 9)}
S.blob(berry, BERRY, BE_OUT, cuts=(-0.3, 0.4))
S.set(31, 5, hexc("#fff0a0"))
S.set(33, 7, hexc("#fff0a0"))
S.set(30, 4, GLINT)
for (x, y) in ((30, 2), (31, 2), (33, 2), (34, 2), (32, 1)):
    S.set(x, y, LEAF)
S.outline_around({(30, 2), (31, 2), (33, 2), (34, 2), (32, 1)} - set(S.px), LEAF_OUT)

# head
head = squircle(32, 32, 20, 17)
S.blob(head, METAL, M_OUT, cuts=(-0.5, 0.15, 0.65))
for (x, y) in ((16, 18), (17, 17), (18, 17), (15, 19)):
    S.set(x, y, GLINT)

# screen face
scr = rounded_rect(18, 24, 28, 17, 2)
S.fill(scr, SCREEN)
S.fill(edge(scr), D_OUT)
for x in range(20, 44):
    S.set(x, 25, SCREEN_L)
# happy ^ ^ eyes
for ex in (24, 36):
    for (x, y) in ((ex, 32), (ex + 1, 31), (ex + 2, 30), (ex + 3, 31), (ex + 4, 32)):
        S.set(x, y, GLOW)
    S.set(ex + 2, 29, GLOW_L)
# little mouth + cheek lights
for x in range(30, 34):
    S.set(x, 36, GLOW)
S.set(29, 35, GLOW)
S.set(34, 35, GLOW)
S.set(21, 35, PINK)
S.set(22, 35, PINK)
S.set(41, 35, PINK)
S.set(42, 35, PINK)
# rivets on the head
for (x, y) in ((16, 30), (47, 30), (16, 38), (47, 38)):
    S.set(x, y, METAL[3])

finish(S, "unit_b3rry")
