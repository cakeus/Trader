"""Hachi: a warm, loyal red shiba who meets the last train every night.
Russet fur with the cream cheeks, brow dots and chest, pointy ears, a happy
grin, a navy scarf against the night chill, and a little paper lantern on a
bamboo stick to light the platform."""
from pixelkit import hexc, ellipse, edge, rect
from portraitkit import new, poly, line, eye, blush, clip, finish, GLINT

S = new()

FUR = [hexc("#f8b070"), hexc("#e08840"), hexc("#bc6a2e"), hexc("#94502a")]
FU_OUT = hexc("#4a2414")
CREAM = [hexc("#fffaf0"), hexc("#fbecd4"), hexc("#ecd4b0"), hexc("#d4b88e")]
EAR_IN = hexc("#f6c6a8")
NOSE = hexc("#2e1a22")
TONGUE = hexc("#f28a9a")
SCARF = [hexc("#6a82c0"), hexc("#46599a"), hexc("#34427a"), hexc("#262f5e")]
SC_OUT = hexc("#141a3a")
BAMBOO = [hexc("#e8d49a"), hexc("#c4a868"), hexc("#94784a")]
BA_OUT = hexc("#4a3a20")
PAPER = [hexc("#fffbe6"), hexc("#ffe8b0"), hexc("#f4cf86"), hexc("#dca860")]
PA_OUT = hexc("#8a5a2a")
RED = [hexc("#f27a5c"), hexc("#e0503f"), hexc("#a8332f")]
RD_OUT = hexc("#5e1c24")

# russet shoulders with a cream chest
body = clip(ellipse(30, 66, 27, 15))
S.blob(body, FUR, FU_OUT, cuts=(-0.5, 0.2, 0.7))
chest = clip(ellipse(30, 67, 12, 13)) - edge(body)
S.blob(chest, CREAM, None, cuts=(-0.3, 0.3, 0.7))

# pointy ears
for side in (-1, 1):
    bx = 30 + side * 9
    ear = poly([(bx - 7, 25), (bx + 7, 25), (bx + side * 3, 11)])
    S.blob(ear, FUR, FU_OUT, cuts=(-0.4, 0.2, 0.7))
    inner = poly([(bx - 3.5, 24), (bx + 3.5, 24), (bx + side * 2.5, 15)]) - edge(ear)
    S.fill(inner, EAR_IN)

# head: russet with the cream mask on cheeks and muzzle
head = ellipse(30, 31, 16, 13.5)
S.blob(head, FUR, FU_OUT, cuts=(-0.5, 0.2, 0.7))
inner = head - edge(head)
mask = (ellipse(22, 37, 7, 6) | ellipse(38, 37, 7, 6) | ellipse(30, 38, 7, 6)) & inner
S.blob(mask, CREAM, None, cuts=(-0.3, 0.4, 0.8), center=(28, 36))
S.set(20, 22, GLINT)
S.set(21, 21, GLINT)
# cream brow dots
for (x, y) in ((23, 25), (24, 25), (36, 25), (37, 25)):
    S.set(x, y, CREAM[1])

# happy eyes, nose and open grin
eye(S, 22, 27, 3, 4)
eye(S, 36, 27, 3, 4)
nose = ellipse(30, 34, 2.6, 1.8)
S.fill(nose, NOSE)
S.set(29, 33, hexc("#6a4a5a"))
S.set(30, 36, FU_OUT)
for (x, y) in ((27, 37), (28, 38), (29, 38), (31, 38), (32, 38), (33, 37)):
    S.set(x, y, FU_OUT)
for (x, y) in ((29, 39), (30, 39), (31, 39), (30, 40)):
    S.set(x, y, TONGUE)
S.set(31, 40, hexc("#c86a7a"))
blush(S, 18, 33)
blush(S, 41, 33)

# navy scarf tied at the neck
scarf = poly([(15, 43), (45, 43), (46, 48), (30, 51), (14, 48)])
S.blob(scarf, SCARF, SC_OUT, cuts=(-0.4, 0.2, 0.7))
tail = poly([(19, 46), (25, 47), (24, 58), (18, 57)])
S.blob(tail, SCARF, SC_OUT, cuts=(-0.4, 0.2, 0.7))
for x in (19, 21, 23):
    S.set(x, 58, SCARF[1])
for x in range(17, 44, 5):
    S.set(x, 46, SCARF[3])

# bamboo stick held in a paw, with a paper lantern hanging from it
S.fill(line(44, 56, 50, 22, 2), BAMBOO[1])
for (x, y) in line(45, 56, 51, 22):
    S.set(x, y, BAMBOO[2])
for (x, y) in line(43, 56, 49, 22):
    S.set(x, y, BAMBOO[0])
for (x, y) in line(50, 21, 57, 22, 2):   # crook at the top
    S.set(x, y, BAMBOO[1])
S.set(57, 23, BA_OUT)
for y in (33, 45):
    for (x, yy) in line(43, 56, 51, 22, 2):
        if yy == y:
            S.set(x, y, BA_OUT)
paw = ellipse(44, 55, 4, 3.5)
S.blob(paw, CREAM, FU_OUT, cuts=(-0.3, 0.4))
S.set(46, 54, FU_OUT)
S.set(46, 56, FU_OUT)
# string and lantern
for y in range(24, 28):
    S.set(57, y, BA_OUT)
lantern = ellipse(57, 36, 5.5, 7)
S.blob(lantern, PAPER, PA_OUT, cuts=(-0.6, 0.1, 0.6))
for y in (31, 34, 37, 40):   # ribs
    for x in range(51, 64):
        if (x, y) in lantern and (x, y) not in edge(lantern):
            S.set(x, y, PAPER[2] if x > 57 else PAPER[1])
core = ellipse(56, 35, 2, 3)
S.fill(core - edge(lantern), hexc("#ffffff"))
for cy in (29, 43):   # red caps top and bottom
    cap = rect(53, cy - 1, 9, 3)
    S.blob(cap, RED, RD_OUT, cuts=(-0.3, 0.4))
for (x, y) in ((57, 45), (57, 46), (56, 47), (58, 47), (57, 48)):   # tassel
    S.set(x, y, RED[1])
S.set(57, 48, RED[2])

finish(S, "hachi")
