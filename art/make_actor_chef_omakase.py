"""Chef Omakase: a stern old grey heron who has run the same sushi counter
for forty years. White head with the black brow stripe running back into
trailing crest plumes, a long yellow bill, a streaked neck and a crisp white
chef's coat with a navy collar."""
from pixelkit import hexc, ellipse, edge, rect
from portraitkit import new, poly, line, curve, clip, finish, GLINT, EYE_DARK

S = new()

GREY = [hexc("#d6dcea"), hexc("#aab4c8"), hexc("#8490a8"), hexc("#646e88")]
GR_OUT = hexc("#2a3048")
WHITE = [hexc("#ffffff"), hexc("#f2f2f6"), hexc("#dcdce6"), hexc("#bcbccc")]
WH_OUT = hexc("#5a5a72")
BLACK = hexc("#23202e")
BLACK_L = hexc("#3e3a50")
BILL = [hexc("#fff2a0"), hexc("#f4c84a"), hexc("#d4982e"), hexc("#a8701e")]
BL_OUT = hexc("#6a4418")
COAT = [hexc("#ffffff"), hexc("#f4f2ee"), hexc("#dcd8d0"), hexc("#bcb6ac")]
CT_OUT = hexc("#5c5650")
NAVY = [hexc("#4a5a8a"), hexc("#2f3c68"), hexc("#222c50")]
NV_OUT = hexc("#141a34")
IRIS = hexc("#f4d45a")

# chef's coat shoulders, wrapped closed, with navy trim along the collar
coat = clip(ellipse(32, 68, 30, 17))
S.blob(coat, COAT, CT_OUT, cuts=(-0.5, 0.25, 0.75))
for (x, y) in line(24, 52, 34, 64) | line(40, 52, 30, 60):
    S.set(x, y, NAVY[1])
    S.set(x + 1, y, NAVY[2])
for (x, y) in line(36, 58, 44, 64):   # wrap-over front edge
    S.set(x, y, CT_OUT)
for (x, y) in ((45, 58), (46, 58), (45, 61), (46, 61)):   # cloth toggles
    S.set(x, y, NAVY[1])

# neck: grey sides, white front with dark streaks
neck = poly([(23, 58), (42, 58), (39, 44), (38, 34), (26, 34), (25, 44)])
S.blob(neck, GREY, GR_OUT, cuts=(-0.4, 0.2, 0.7))
front = poly([(28, 57), (37, 57), (36, 44), (35, 36), (30, 36), (28, 44)]) - edge(neck)
S.blob(front, WHITE, None, cuts=(-0.3, 0.3, 0.8))
for (x, y) in ((31, 40), (31, 41), (33, 43), (33, 44), (30, 46), (30, 47), (32, 49), (32, 50),
               (34, 47), (34, 48), (31, 53), (31, 54)):
    S.set(x, y, BLACK_L)
# coat collar wrapping over the neck base, navy-trimmed (left over right)
lapel_r = poly([(43, 51), (47, 53), (36, 62), (33, 60)])
lapel_l = poly([(21, 51), (17, 53), (34, 66), (37, 62)])
for lap in (lapel_r, lapel_l):
    S.blob(lap, COAT, CT_OUT, cuts=(-0.5, 0.25, 0.75), center=(32, 58))
for (x, y) in line(22, 53, 36, 63):
    S.set(x, y, NAVY[1])
    S.set(x, y + 1, NAVY[2])
for (x, y) in line(42, 53, 35, 59):
    S.set(x, y, NAVY[1])
    S.set(x, y + 1, NAVY[2])

# trailing black crest plumes behind the head
for pts, w in (([(22, 16), (15, 12), (9, 12), (4, 15), (2, 19)], 2),
               ([(21, 18), (14, 16), (9, 18), (6, 22)], 1)):
    S.fill(curve(pts, w), BLACK)
S.set(10, 11, BLACK_L)
S.set(11, 11, BLACK_L)

# head
head = ellipse(31, 26, 14, 12.5)
S.blob(head, WHITE, WH_OUT, cuts=(-0.5, 0.25, 0.75))
S.set(22, 20, GLINT)
S.set(21, 21, GLINT)
S.set(22, 21, WHITE[0])
# black stripe from above the eye back into the crest
stripe = (line(32, 23, 26, 19, 2) | line(26, 19, 20, 15, 2) | line(20, 15, 17, 16)) & head
S.fill(stripe, BLACK)
for (x, y) in ((27, 19), (24, 17)):
    if (x, y) in stripe:
        S.set(x, y, BLACK_L)

# stern eye: yellow iris, dark pupil, flat heavy lid
eyem = ellipse(36.5, 25.5, 2.6, 2.6)
S.fill(eyem, IRIS)
for (x, y) in ((36, 25), (37, 25), (36, 26), (37, 26)):
    S.set(x, y, EYE_DARK)
S.set(36, 25, GLINT)
for x in range(33, 41):
    S.set(x, 23, BLACK)
for x in range(34, 40):
    S.set(x, 24, BLACK_L)

# long closed bill pointing to the right
bill = poly([(41, 24), (45, 22.5), (63, 28), (63, 29.5), (45, 33), (41, 31)])
S.blob(bill, BILL, BL_OUT, cuts=(-0.3, 0.3, 0.75))
for x in range(44, 60):
    S.set(x, 29, BL_OUT)
S.set(45, 24, GLINT)
S.set(46, 24, BILL[0])
S.set(47, 25, BILL[0])
# white wisps of old-man beard under the chin
for (x, y) in ((33, 38), (34, 39), (34, 40), (36, 38), (37, 39), (37, 40), (38, 41)):
    S.set(x, y, WHITE[0])
for (x, y) in ((35, 40), (35, 41), (38, 42)):
    S.set(x, y, WHITE[3])
# faint cheek
S.set(28, 30, hexc("#e8a4a8"))
S.set(29, 30, hexc("#e8a4a8"))

finish(S, "chef_omakase")
