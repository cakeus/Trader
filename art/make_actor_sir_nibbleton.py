"""Sir Nibbleton: a seagull knight with a silver helmet, red plume,
big yellow beak and polished pauldrons."""
from pixelkit import hexc, ellipse, edge, rect
from portraitkit import new, poly, curve, eye, blush, clip, finish, GLINT

S = new()

FEATHER = [hexc("#ffffff"), hexc("#e6ebf2"), hexc("#bcc6d4"), hexc("#94a0b4")]
F_OUT = hexc("#48546e")
STEEL = [hexc("#f4f6fa"), hexc("#c4c9d8"), hexc("#969cb2"), hexc("#6c7290")]
ST_OUT = hexc("#343852")
BEAK = [hexc("#fff0a0"), hexc("#ffcc4a"), hexc("#e49a2a")]
B_OUT = hexc("#8a5414")
PLUME = [hexc("#ff9a8a"), hexc("#e8404e"), hexc("#b02a3c")]
P_OUT = hexc("#5e1426")
TABARD = [hexc("#7ab4f0"), hexc("#4a84d0"), hexc("#3464a8")]
GOLD = hexc("#ffd24a")

# armour shoulders
arm = clip(ellipse(32, 66, 27, 14))
S.blob(arm, STEEL, ST_OUT, cuts=(-0.5, 0.15, 0.7))
for x in range(8, 58):
    if (x, 58) in arm and (x, 58) not in edge(arm):
        S.set(x, 58, STEEL[3])
tab = rect(25, 55, 14, 9)
S.blob(tab, TABARD, hexc("#1c3a6a"), cuts=(-0.3, 0.4))
for (x, y) in ((32, 57), (31, 58), (32, 58), (33, 58), (32, 59), (32, 60)):
    S.set(x, y, GOLD)

# plume (behind the helmet)
plume = curve([(30, 18), (24, 10), (16, 8), (9, 11), (6, 16)], width=5)
S.blob(plume, PLUME, P_OUT, cuts=(-0.3, 0.3))

# head
head = ellipse(30, 36, 15, 14) | ellipse(30, 50, 10, 5)
S.blob(head, FEATHER, F_OUT, cuts=(-0.35, 0.3, 0.75), center=(30, 38))
# grey wing-tip feathers on the back of the head
for (x, y) in ((17, 40), (18, 42), (17, 43), (19, 44)):
    S.set(x, y, FEATHER[3])

# helmet dome + visor band
dome = {p for p in ellipse(30, 30, 16, 13) if p[1] <= 29}
S.blob(dome, STEEL, ST_OUT, cuts=(-0.45, 0.2, 0.65))
for x in range(14, 47):
    if (x, 28) in dome:
        S.set(x, 28, STEEL[3])
        S.set(x, 27, STEEL[2] if x > 30 else STEEL[1])
for (x, y) in ((20, 22), (21, 21), (22, 20)):
    S.set(x, y, GLINT)
# rivets
for x in (18, 30, 42):
    S.set(x, 25, STEEL[3])

# beak
beak = poly([(38, 33), (58, 36), (57, 40), (52, 42), (38, 42)])
S.blob(beak, BEAK, B_OUT, cuts=(-0.3, 0.4))
for x in range(40, 56):
    S.set(x, 38, B_OUT) if (x, 38) in beak and x > 44 else None
S.set(53, 40, hexc("#e8404e"))
S.set(54, 40, hexc("#e8404e"))

# eye with a determined brow
eye(S, 33, 31, 3, 4)
for (x, y) in ((32, 30), (33, 30), (34, 29), (35, 29)):
    S.set(x, y, F_OUT)
blush(S, 28, 38)

finish(S, "sir_nibbleton")
