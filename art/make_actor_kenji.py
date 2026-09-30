"""Kenji the Kaiju: a big, round, gentle sea creature in soft lavender with
a cream tummy, a row of rounded plates on his back that glow lantern-orange,
and two tiny drumsticks pinched very, very carefully in his claws."""
from pixelkit import hexc, ellipse, edge
from portraitkit import new, poly, eye, blush, clip, finish, line, GLINT

S = new()

HIDE = [hexc("#d8c8f4"), hexc("#ab94dc"), hexc("#8670c0"), hexc("#6a56a0")]
HD_OUT = hexc("#2e2254")
BELLY = [hexc("#fff4dc"), hexc("#ffe4b4"), hexc("#f0c890")]
BE_OUT = hexc("#6a4a5a")
GLOW = [hexc("#fff0b8"), hexc("#ffc06b"), hexc("#f59a3f"), hexc("#d8702c")]
GL_OUT = hexc("#8a3a1e")
WOOD = [hexc("#f0c488"), hexc("#c88a4e"), hexc("#9a623a")]
WD_OUT = hexc("#4a2a1c")
MOUTH = hexc("#c84a5a")

# rounded glowing back plates peeking up behind his head (soft bulbs, not spikes)
plates = [(32, 16, 4.6, 5.8), (21.5, 19, 4.2, 5.2), (42.5, 19, 4.2, 5.2), (13.5, 28, 3.8, 4.6), (50.5, 28, 3.8, 4.6)]
for (cx, cy, rx, ry) in plates:
    p = ellipse(cx, cy, rx, ry)
    S.blob(p, GLOW, GL_OUT, cuts=(-0.35, 0.25, 0.7))
    S.set(round(cx - rx * 0.4), round(cy - ry * 0.45), GLINT)
    S.set(round(cx - rx * 0.4), round(cy - ry * 0.45) + 1, GLOW[0])
# a little warm sparkle off the glow
for (x, y) in ((26, 10), (38, 10), (15, 21), (49, 21), (9, 24), (55, 24)):
    S.set(x, y, GLOW[1])

# chubby shoulders and a big round head
body = clip(ellipse(32, 66, 27, 20))
S.blob(body, HIDE, HD_OUT, cuts=(-0.5, 0.2, 0.7))
belly = clip(ellipse(32, 66, 13, 16)) - edge(body)
S.blob(belly, BELLY, BE_OUT, cuts=(-0.2, 0.55))
for y in (53, 57, 61):
    for x in range(18, 47):
        if (x, y) in belly and (x, y - 1) in belly:
            S.set(x, y, BELLY[2])
head = ellipse(32, 34, 18, 15)
S.blob(head, HIDE, HD_OUT, cuts=(-0.5, 0.2, 0.7))
# soft freckles on his crown
for (x, y) in ((25, 23), (28, 21), (37, 22), (40, 24), (32, 21)):
    S.set(x, y, HIDE[2])
S.set(19, 27, GLINT)
S.set(20, 26, GLINT)
S.set(21, 25, HIDE[0])

# wide cream snout
snout = ellipse(32, 41, 8.5, 5)
S.blob(snout, BELLY, BE_OUT, cuts=(-0.2, 0.6))
S.set(29, 38, BE_OUT)
S.set(35, 38, BE_OUT)
# gentle smile with two little tooth nubs
for x in range(29, 36):
    S.set(x, 42, BE_OUT)
S.set(28, 41, BE_OUT)
S.set(36, 41, BE_OUT)
for x in range(31, 34):
    S.set(x, 43, MOUTH)
S.set(30, 43, BE_OUT)
S.set(34, 43, BE_OUT)
for x in range(31, 34):
    S.set(x, 44, BE_OUT)

# big soft eyes
eye(S, 22, 30, 4, 5)
eye(S, 38, 30, 4, 5)
S.set(24, 33, GLINT)
S.set(40, 33, GLINT)
blush(S, 18, 37)
blush(S, 45, 37)

# stubby claws pinching two tiny drumsticks, oh so gently
for (cx, sx) in ((16, -1), (48, 1)):
    S.blob(line(cx, 55, cx - sx * 4, 46, width=1.8), WOOD, WD_OUT, cuts=(-0.1, 0.6))
    paw = ellipse(cx, 56, 4.4, 3.6)
    S.blob(paw, HIDE, HD_OUT, cuts=(-0.3, 0.3, 0.75))
    for dx in (-2, 0, 2):
        S.set(cx + dx, 59, BELLY[0])

finish(S, "kenji")
