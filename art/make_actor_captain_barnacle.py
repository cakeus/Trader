"""Captain Barnacle: a retired crab pirate with a tricorn hat, an eyepatch
on one stalk eye, raised claws and a navy coat."""
from pixelkit import hexc, ellipse, edge
from portraitkit import new, poly, line, eyeball, blush, clip, finish, smile, GLINT

S = new()

SHELL = [hexc("#ffb48c"), hexc("#f06c4a"), hexc("#c8483a"), hexc("#9a3030")]
S_OUT = hexc("#561a1e")
COAT = [hexc("#7a8ad0"), hexc("#4a5aa4"), hexc("#36447e"), hexc("#28325e")]
C_OUT = hexc("#161a3a")
HAT = [hexc("#5a4a6e"), hexc("#3e3050"), hexc("#2c2240")]
H_OUT = hexc("#140e20")
GOLD = hexc("#ffd24a")
GOLD_D = hexc("#c08a2a")
BONE = hexc("#fff4e4")
SPOT = hexc("#ffd8b0")

# coat
coat = clip(ellipse(32, 66, 27, 14))
S.blob(coat, COAT, C_OUT, cuts=(-0.5, 0.2, 0.7))
for y in (57, 61):
    for x in (27, 37):
        S.set(x, y, GOLD)
        S.set(x + 1, y + 1, GOLD_D)
# lapels
for i in range(6):
    S.set(29 - i // 2, 54 + i, C_OUT)
    S.set(35 + i // 2, 54 + i, C_OUT)

# arms + claws
for sx in (1, -1):
    arm = line(32 - sx * 16, 48, 32 - sx * 21, 38, width=4)
    S.blob(arm, SHELL, S_OUT, cuts=(-0.3, 0.3, 0.7))
    cx = 32 - sx * 22
    claw = ellipse(cx, 30, 6, 7.5) - poly([(cx - 3, 20), (cx + 3, 20), (cx, 29)])
    S.blob(claw, SHELL, S_OUT, cuts=(-0.4, 0.2, 0.7))
    S.set(cx - 3, 27, GLINT)

# body
body = ellipse(32, 43, 20, 12)
S.blob(body, SHELL, S_OUT, cuts=(-0.5, 0.2, 0.7))
for (x, y) in ((22, 40), (25, 37), (42, 38), (44, 42), (20, 45)):
    S.set(x, y, SPOT)
    S.set(x, y + 1, SHELL[3])

# eye stalks + eyes
for (x0, x1) in ((24, 19), (40, 45)):
    st = line(x0, 34, x1, 22, width=3)
    S.blob(st, SHELL, S_OUT, cuts=(-0.2, 0.5))
eyeball(S, 19, 19, 4.6, S_OUT, look=(0.8, 0.6))
# right eye wears the patch
patch = ellipse(45, 19, 4.6, 4.6)
S.blob(patch, HAT, H_OUT, cuts=(-0.2, 0.5))
S.set(44, 17, hexc("#7a6a90"))
strap = line(40, 14, 50, 24)
for p in strap:
    if p not in patch:
        S.set(*p, H_OUT)

# tricorn hat perched on top
hat = poly([(20, 32), (44, 32), (41, 25), (36, 22), (32, 24), (28, 22), (23, 25)])
S.blob(hat, HAT, H_OUT, cuts=(-0.3, 0.4))
for x in range(22, 43):
    if (x, 30) in hat and (x, 30) not in edge(hat):
        S.set(x, 30, GOLD)
# tiny skull
for (x, y) in ((31, 26), (32, 26), (33, 26), (31, 27), (33, 27), (32, 28)):
    S.set(x, y, BONE)

smile(S, 29, 45, 7, S_OUT)
blush(S, 23, 44)
blush(S, 40, 44)

finish(S, "captain_barnacle")
