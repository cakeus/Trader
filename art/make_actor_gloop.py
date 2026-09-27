"""Gloop: a teal blob alien tourist with an antenna, heart-pink sunglasses,
a camera, and a loud orange floral shirt."""
from pixelkit import hexc, ellipse, edge, rounded_rect, rect
from portraitkit import new, line, blush, clip, finish, GLINT

S = new()

GOO = [hexc("#c4f8e0"), hexc("#72dcb4"), hexc("#40b492"), hexc("#2c8a76")]
G_OUT = hexc("#16464a")
SHIRT = [hexc("#ffd49a"), hexc("#ffac5a"), hexc("#e8843c"), hexc("#c0622c")]
SH_OUT = hexc("#6a3014")
FLOWER = hexc("#ff7aa8")
FLOWER_C = hexc("#fff0a0")
FRAME = [hexc("#ff9ad0"), hexc("#e84a9a"), hexc("#b02e76")]
F_OUT = hexc("#5a1440")
LENS = hexc("#3a1e4a")
LENS_L = hexc("#8a6ab8")
CAM = [hexc("#d8d4e0"), hexc("#aaa4b8"), hexc("#7e7894")]
CAM_OUT = hexc("#2e2840")
MOUTH = hexc("#3a1a3a")
TONGUE = hexc("#ff8aa8")

# shirt
shirt = clip(ellipse(32, 66, 25, 14))
S.blob(shirt, SHIRT, SH_OUT, cuts=(-0.5, 0.2, 0.7))
for (fx, fy) in ((14, 58), (24, 62), (44, 57), (51, 62), (35, 61)):
    for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
        if (fx + dx, fy + dy) in shirt and (fx + dx, fy + dy) not in edge(shirt):
            S.set(fx + dx, fy + dy, FLOWER)
    S.set(fx, fy, FLOWER_C)

# antenna
S.fill(line(32, 17, 37, 7), G_OUT)
ball = ellipse(38, 5, 3, 3)
S.blob(ball, [hexc("#fff0f8"), hexc("#ff9ad0"), hexc("#e84a9a")], F_OUT, cuts=(-0.3, 0.4))

# blob head with drips
head = ellipse(32, 35, 20, 18) | ellipse(17, 50, 3, 4) | ellipse(46, 51, 2.6, 3.4)
S.blob(head, GOO, G_OUT, cuts=(-0.45, 0.2, 0.65), center=(32, 35))
S.set(18, 24, GLINT)
S.set(19, 23, GLINT)
S.set(17, 26, GLINT)

# sunglasses
for x0 in (18, 34):
    lens = rounded_rect(x0, 29, 12, 8, 2)
    S.fill(lens, LENS)
    S.fill(edge(lens), F_OUT)
    S.set(x0 + 2, 31, LENS_L)
    S.set(x0 + 3, 30, LENS_L)
    S.set(x0 + 4, 31, LENS_L)
for x in range(29, 35):
    S.set(x, 31, F_OUT)
for (x, y) in ((17, 30), (16, 30), (46, 30), (47, 30)):
    S.set(x, y, F_OUT)

# big open grin
for x in range(27, 38):
    S.set(x, 41, MOUTH)
for x in range(28, 37):
    S.set(x, 42, MOUTH)
for x in range(29, 36):
    S.set(x, 43, TONGUE if 30 <= x <= 34 else MOUTH)
blush(S, 20, 40)
blush(S, 42, 40)

# camera on a strap
S.fill(line(19, 47, 25, 53), CAM_OUT)
S.fill(line(45, 47, 39, 53), CAM_OUT)
cam = rounded_rect(24, 52, 16, 9, 1)
S.blob(cam, CAM, CAM_OUT, cuts=(-0.3, 0.4))
lens = ellipse(32, 56, 2.6, 2.6)
S.blob(lens, [hexc("#6a5a8c"), hexc("#3a2e56")], CAM_OUT, cuts=(0.2,))
S.set(31, 55, GLINT)
S.fill(rect(26, 53, 3, 1), FLOWER)

finish(S, "gloop")
