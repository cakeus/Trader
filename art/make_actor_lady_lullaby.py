"""Lady Lullaby: the lodge's resident ghost since 1893. A pale lavender lady
with a tall updo, a lace collar and cameo, serene closed eyes, holding a small
open music box with a wind-up key."""
from pixelkit import hexc, ellipse, edge, rect
from portraitkit import new, poly, line, blush, clip, finish, GLINT

S = new()

GHOST = [hexc("#f8f4ff"), hexc("#e2daf6"), hexc("#c4b8e8"), hexc("#a496d4")]
GH_OUT = hexc("#5a4a90")
HAIR = [hexc("#d8f4ec"), hexc("#aee0d4"), hexc("#84c4b8"), hexc("#62a49c")]
HR_OUT = hexc("#2e6460")
GOWN = [hexc("#c8b8f0"), hexc("#9e8ad8"), hexc("#7c68bc"), hexc("#5e4c9c")]
GW_OUT = hexc("#33245e")
LACE = [hexc("#ffffff"), hexc("#f0f0fa"), hexc("#d4d0ec")]
LC_OUT = hexc("#7a70a8")
CAMEO = [hexc("#fff0f4"), hexc("#f4b8c8"), hexc("#d88aa4")]
LASH = hexc("#4a3a7c")
LBLUSH = hexc("#f4a8c8")
WOOD = [hexc("#e8a86a"), hexc("#c07a44"), hexc("#98572e"), hexc("#733c22")]
WOOD_OUT = hexc("#48241a")
VELVET = [hexc("#f08094"), hexc("#c84a6a"), hexc("#962e52")]
GOLD = [hexc("#fff4b0"), hexc("#ffd24a"), hexc("#d89a2a"), hexc("#a8701e")]
GOLD_OUT = hexc("#6a4418")
NOTE = hexc("#7462bc")

# gown shoulders
gown = clip(ellipse(32, 63, 24, 17))
S.blob(gown, GOWN, GW_OUT, cuts=(-0.5, 0.2, 0.7))
# ghostly wisps drifting off the shoulders
for (pts, c) in (([(9, 54), (6, 50), (8, 46), (5, 42)], GHOST[2]),
                 ([(55, 54), (58, 50), (56, 46), (59, 42)], GHOST[2])):
    for p in line(*pts[0], *pts[1]) | line(*pts[1], *pts[2]) | line(*pts[2], *pts[3]):
        S.set(*p, c)
S.set(5, 41, GHOST[1])
S.set(59, 41, GHOST[1])

# tall hair updo behind the head, with a bun on top
bun = ellipse(32, 9, 7, 5.5)
S.blob(bun, HAIR, HR_OUT, cuts=(-0.4, 0.3, 0.75))
back = ellipse(32, 24, 15, 13)
S.blob(back, HAIR, HR_OUT, cuts=(-0.5, 0.2, 0.7))

# pale face
face = ellipse(32, 30, 11, 11.5)
S.blob(face, GHOST, GH_OUT, cuts=(-0.5, 0.25, 0.75))
# swept fringe over the forehead
fringe = poly([(20, 26), (23, 18), (30, 14), (38, 15), (43, 20), (44, 26), (39, 22), (33, 20), (26, 22)])
S.blob(fringe, HAIR, HR_OUT, cuts=(-0.4, 0.3, 0.75))
for p in line(30, 15, 25, 22):
    if p not in edge(fringe):
        S.set(*p, HAIR[2])
S.set(29, 6, GLINT)
S.set(30, 5, GLINT)
S.set(25, 19, GLINT)
# a little ribbon in the bun
for (x, y) in ((37, 11), (38, 10), (39, 11), (38, 12), (40, 10), (40, 12)):
    S.set(x, y, VELVET[1])

# serene closed eyes (downturned arcs) with lashes
for ex in (24, 36):
    for (dx, dy) in ((0, 0), (1, 1), (2, 1), (3, 1), (4, 0)):
        S.set(ex + dx, 29 + dy, LASH)
    S.set(ex - 1 if ex < 32 else ex + 5, 28, LASH)
# soft smile
S.set(30, 35, GH_OUT)
S.set(31, 36, GH_OUT)
S.set(32, 36, GH_OUT)
S.set(33, 35, GH_OUT)
blush(S, 23, 32, LBLUSH)
blush(S, 39, 32, LBLUSH)

# lace collar: a scalloped ruff with a cameo
collar = set()
for i, cx in enumerate(range(20, 46, 5)):
    collar |= ellipse(cx, 43 + (1 if i in (0, 5) else 0), 3.2, 3)
collar |= rect(20, 40, 25, 3)
S.blob(collar, LACE, LC_OUT, cuts=(-0.3, 0.5))
for cx in range(20, 46, 5):
    S.set(cx, 44, LACE[2])
cam = ellipse(32, 43, 2.6, 3)
S.blob(cam, CAMEO, GOLD[2], cuts=(-0.2, 0.5))
S.set(32, 42, hexc("#ffffff"))

# small open music box held in front, with ghostly little hands
LX, LY = 23, 48
lid = rect(LX + 1, LY, 16, 5)
S.blob(lid, WOOD, WOOD_OUT, cuts=(-0.4, 0.3, 0.7))
S.fill(rect(LX + 3, LY + 1, 12, 3), VELVET[1])
S.fill(rect(LX + 3, LY + 1, 5, 1), VELVET[0])
S.fill(rect(LX, LY + 5, 18, 1), WOOD_OUT)
box = rect(LX, LY + 6, 18, 7)
S.blob(box, WOOD, WOOD_OUT, lx=0.9, cuts=(-0.45, 0.25, 0.7))
for x in range(LX + 1, LX + 17):
    S.set(x, LY + 7, GOLD[1] if x < LX + 9 else GOLD[2])
S.set(LX + 9, LY + 9, GOLD_OUT)
S.set(LX + 9, LY + 10, GOLD_OUT)
S.set(LX + 1, LY + 1, GLINT)
# wind-up key sticking out on the right
S.fill(rect(LX + 18, LY + 8, 2, 1), GOLD[2])
key = ["OOO", "OGO", "O.O", "OGO", "OOO"]
S.rows(key, {"O": GOLD_OUT, "G": GOLD[1]}, LX + 20, LY + 6)
# hands
for hx in (LX - 2, LX + 16):
    hand = ellipse(hx + 2, LY + 10, 3, 2.6)
    S.blob(hand, GHOST, GH_OUT, cuts=(-0.2, 0.5))

# floating notes
S.rows(["..OO", "..OO", "..O.", "..O.", "OOO.", "OO.."], {"O": NOTE}, 48, 17)
S.set(48, 21, hexc("#b8a8f0"))
S.rows([".OO", ".O.", ".O.", "OO.", "OO."], {"O": NOTE}, 12, 12)

finish(S, "lady_lullaby")
