"""Pirouette: an ermine ballerina in her white winter coat. Arms raised in
fifth position, a pink leotard and tutu, a little tiara, and a black-tipped
tail curling up beside her."""
from pixelkit import hexc, ellipse, edge, rect
from portraitkit import new, poly, curve, eye, blush, clip, finish, smile, GLINT

S = new()

FUR = [hexc("#fffcf6"), hexc("#f6ece2"), hexc("#e4d2c4"), hexc("#ccb4a4")]
F_OUT = hexc("#86625e")
TIP = [hexc("#6a5460"), hexc("#4a3844"), hexc("#34262e")]
TIP_OUT = hexc("#1e141c")
PINK = [hexc("#ffd4e0"), hexc("#f8a0bc"), hexc("#e0709a"), hexc("#bc4e7c")]
PK_OUT = hexc("#6e2446")
TUTU = [hexc("#fff0f6"), hexc("#ffc8dc"), hexc("#f4a0c0"), hexc("#dc7aa4")]
EAR_IN = hexc("#f4b0c0")
NOSE = hexc("#e0708c")
GOLD = [hexc("#fff4b0"), hexc("#ffd24a"), hexc("#d89a2a")]
GEM = hexc("#8ad8f0")
NOTE = hexc("#7462bc")

# tail curling up the right side, black tip at the top
tail = curve([(46, 60), (56, 55), (59, 45), (58, 37)], width=5)
S.blob(tail, FUR, F_OUT, cuts=(-0.4, 0.3, 0.7))
tip = ellipse(58, 32, 3.4, 5)
S.blob(tip, TIP, TIP_OUT, cuts=(-0.3, 0.4))
S.set(57, 29, hexc("#8a7482"))

# tutu: layered frill at the bottom, and a slim pink leotard
tutu = clip(ellipse(32, 62, 26, 5))
S.blob(tutu, TUTU, PK_OUT, cuts=(-0.4, 0.2, 0.7))
for x in range(8, 57, 3):
    S.set(x, 60 + (x % 2), TUTU[3])
body = clip(poly([(22, 46), (42, 46), (40, 58), (24, 58)]))
S.blob(body, PINK, PK_OUT, cuts=(-0.4, 0.25, 0.7))
S.set(25, 48, GLINT)
tutu_top = clip(ellipse(32, 58, 18, 3.2))
S.blob(tutu_top, TUTU, PK_OUT, cuts=(-0.3, 0.4))
# fur neck poking above the leotard
neck = ellipse(32, 45, 7, 3)
S.blob(neck, FUR, F_OUT, cuts=(-0.3, 0.5))

# arms raised in an oval over the head (fifth position)
larm = curve([(22, 47), (13, 38), (13, 23), (20, 12), (29, 8)], width=5)
rarm = curve([(42, 47), (51, 38), (51, 23), (44, 12), (35, 8)], width=5)
S.blob(larm, FUR, F_OUT, cuts=(-0.4, 0.3, 0.7))
S.blob(rarm, FUR, F_OUT, cuts=(-0.4, 0.3, 0.7))
for cx in (30, 34):   # paws meeting at the top
    paw = ellipse(cx, 8, 3, 2.8)
    S.blob(paw, FUR, F_OUT, cuts=(-0.3, 0.5))

# small rounded ears
for cx in (22, 42):
    ear = ellipse(cx, 25, 3, 2.8)
    S.blob(ear, FUR, F_OUT, cuts=(-0.2, 0.5))
    S.set(cx, 25, EAR_IN)

# long-ish stoat head
head = ellipse(32, 31, 11, 9.5)
S.blob(head, FUR, F_OUT, cuts=(-0.5, 0.25, 0.75))

# tiara
S.rows(["..G.G.G..", ".GGgGgGG.", "GGGGGGGGG"], {"G": GOLD[1], "g": GEM}, 28, 20)
S.set(28, 22, GOLD[2])
S.set(36, 22, GOLD[2])
S.set(29, 21, GOLD[0])

# face
eye(S, 25, 29, 3, 4)
eye(S, 36, 29, 3, 4)
S.set(24, 29, F_OUT)   # lashes
S.set(39, 29, F_OUT)
nose = {(31, 35), (32, 35), (31, 34), (32, 34)}
S.fill(nose, NOSE)
S.set(31, 34, GLINT)
smile(S, 29, 36, 6, F_OUT)
blush(S, 23, 34)
blush(S, 39, 34)

# floating notes
S.rows(["..OO", "..OO", "..O.", "..O.", "OOO.", "OO.."], {"O": NOTE}, 5, 14)
S.set(5, 18, hexc("#b8a8f0"))

finish(S, "pirouette")
