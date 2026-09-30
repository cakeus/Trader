"""Kabuto: a rhinoceros beetle drum carver with a glossy mahogany shell, a big
curved horn with wood shavings caught on it, a canvas work apron and a
little mallet."""
from pixelkit import hexc, ellipse, edge, rect, rounded_rect
from portraitkit import new, poly, eyeball, blush, clip, finish, line, curve, GLINT

S = new()

SHELL = [hexc("#c07a5e"), hexc("#8a4636"), hexc("#64302c"), hexc("#482024")]
SH_OUT = hexc("#180a10")
HEAD = [hexc("#7a4e4a"), hexc("#553436"), hexc("#40262c"), hexc("#2e1c22")]
HORN = [hexc("#b08478"), hexc("#6a4446"), hexc("#4a2e34"), hexc("#34202a")]
FACE = [hexc("#ffe8c8"), hexc("#f4cc9c"), hexc("#dca87a")]
FC_OUT = hexc("#5a2a22")
APRON = [hexc("#f4e8c8"), hexc("#dcc89a"), hexc("#b8a070"), hexc("#94804e")]
AP_OUT = hexc("#4a3a1e")
SHAV = [hexc("#fff0c4"), hexc("#f0c67e"), hexc("#c8904e")]
SV_OUT = hexc("#6a4420")
WOOD = [hexc("#f0c488"), hexc("#c88a4e"), hexc("#9a623a")]
WD_OUT = hexc("#4a2a1c")
LEG = hexc("#3a1a1e")

# shell shoulders: two glossy wing cases meeting in the middle
for side in (-1, 1):
    case = clip(ellipse(32 + side * 12, 64, 15, 17))
    case = {p for p in case if (p[0] - 32) * side >= 0}
    S.blob(case, SHELL, SH_OUT, cuts=(-0.45, 0.2, 0.7))
    for (x, y) in ((32 + side * 6, 51), (32 + side * 7, 50), (32 + side * 7, 52)):
        S.set(x, y, SHELL[0] if side < 0 else SHELL[1])
S.fill({(32, y) for y in range(47, 64)}, SH_OUT)

# canvas apron over the front with a pocket full of chisels
apron = poly([(22, 53), (42, 53), (44, 64), (20, 64)])
S.blob(apron, APRON, AP_OUT, cuts=(-0.3, 0.3, 0.75))
for (x, y) in ((22, 52), (21, 51), (20, 50), (42, 52), (43, 51), (44, 50)):
    S.set(x, y, AP_OUT)
pocket = rect(27, 57, 10, 6)
S.blob(pocket, APRON[1:], AP_OUT, cuts=(-0.2, 0.5))
for x, c in ((29, hexc("#a8bcd4")), (32, WOOD[1]), (35, hexc("#a8bcd4"))):
    S.set(x, 56, c)
    S.set(x, 55, c)
    S.set(x, 57, AP_OUT)

# little mallet held upright in his foreleg
S.blob(line(48, 60, 48, 47, width=2.4), WOOD, WD_OUT, cuts=(-0.1, 0.6))
mhead = rounded_rect(42, 41, 13, 7, 2)
S.blob(mhead, WOOD, WD_OUT, cuts=(-0.3, 0.3, 0.8))
for y in (42, 43, 44, 45, 46):
    S.set(44, y, WOOD[2])
    S.set(52, y, WOOD[2])
S.set(43, 42, WOOD[0])
claw = ellipse(48, 56, 3.6, 3.2)
S.blob(claw, HEAD, SH_OUT, cuts=(-0.3, 0.4))
S.set(47, 55, HEAD[0])

# little feelers
for side in (-1, 1):
    S.fill(curve([(32 + side * 10, 28), (32 + side * 15, 22), (32 + side * 19, 21)]), SH_OUT)
    S.fill(ellipse(32 + side * 19.5, 21, 1.2, 1.2), HEAD[1])

# glossy round head
head = ellipse(32, 36, 15, 12)
S.blob(head, HEAD, SH_OUT, cuts=(-0.5, 0.2, 0.7))
for (x, y) in ((21, 30), (22, 29), (23, 28), (24, 28), (25, 27), (20, 31)):
    S.set(x, y, HORN[0])
S.set(22, 30, GLINT)
S.set(23, 29, GLINT)

# the big horn, rising from his face and hooking over
horn = set()
for (cx, cy, r) in ((32, 28, 5.2), (32, 23, 4.4), (32, 18.5, 3.7), (32, 14.5, 3.1), (32, 11, 2.7)):
    horn |= ellipse(cx, cy, r, r)
for side in (-1, 1):   # the fork
    horn |= ellipse(32 + side * 2.5, 8, 1.8, 1.8) | ellipse(32 + side * 4.5, 5.5, 1.5, 1.5) | ellipse(32 + side * 5.5, 3.5, 1.1, 1.1)
S.blob(horn, HORN, SH_OUT, cuts=(-0.4, 0.2, 0.65), center=(32, 16))
S.fill({(32, y) for y in range(5, 9)} - edge(horn), SH_OUT)
S.set(32, 8, SH_OUT)
for y in range(12, 28):   # long glossy highlight
    S.set(30 if y > 18 else 31, y, HORN[0])
S.set(30, 25, GLINT)
S.set(30, 24, GLINT)
S.set(29, 6, HORN[0])
# a wood shaving curled around the horn
shav = curve([(36, 16), (37, 18), (35, 20), (33, 20)], width=2) | ellipse(36, 15.5, 1.5, 1.5)
S.blob(shav, SHAV, SV_OUT, cuts=(-0.2, 0.5))

# big round eyes either side of the horn
eyeball(S, 24, 35, 4, SH_OUT, look=(0.5, 0.5))
eyeball(S, 40, 35, 4, SH_OUT, look=(0.5, 0.5))
# happy little smile
for (x, y) in ((28, 41), (29, 42), (30, 43), (31, 43), (32, 43), (33, 43), (34, 42), (35, 41)):
    S.set(x, y, FACE[1])
blush(S, 20, 41)
blush(S, 43, 41)

finish(S, "kabuto")
