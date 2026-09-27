"""Pip the Beachcomber: a small orange hermit crab peeking out of a big,
sandy spiral shell decorated with a little starfish sticker."""
from pixelkit import hexc, ellipse, edge
from portraitkit import new, poly, line, spiral, eyeball, blush, finish, smile, GLINT

S = new()

SHELL = [hexc("#fff0c8"), hexc("#f4c888"), hexc("#d89a5a"), hexc("#b0703e")]
S_OUT = hexc("#5c341a")
STRIPE = hexc("#c6804a")
HOLE = hexc("#3e2230")
HOLE_L = hexc("#5a3440")
CRAB = [hexc("#ffc0a0"), hexc("#f67e5c"), hexc("#d0543e"), hexc("#a83a34")]
C_OUT = hexc("#621c20")
STAR = [hexc("#fff0f4"), hexc("#ff9ab8"), hexc("#e0628c")]
ST_OUT = hexc("#7a2448")

# big spiral shell
shell = ellipse(38, 30, 21, 22) | ellipse(52, 12, 8, 8)
S.blob(shell, SHELL, S_OUT, cuts=(-0.45, 0.2, 0.65), center=(38, 30))
inner = shell - edge(shell)
sp = spiral(44, 22, 2, 18, 1.8, start=0.6)
for (x, y) in sp:
    if (x, y) in inner:
        S.set(x, y, STRIPE)
        if (x + 1, y + 1) in inner and (x + 1, y + 1) not in sp:
            S.set(x + 1, y + 1, SHELL[3])
for (x, y) in ((24, 16), (25, 15), (23, 18), (27, 14)):
    S.set(x, y, GLINT)

# starfish sticker
star = poly([(50, 32), (52, 37), (57, 37), (53, 40), (55, 45), (50, 42), (45, 45), (47, 40), (43, 37), (48, 37)])
S.blob(star, STAR, ST_OUT, cuts=(-0.2, 0.5))

# opening
hole = ellipse(23, 45, 12, 10)
S.fill(hole, HOLE)
S.fill(edge(hole), S_OUT)
for (x, y) in hole:
    if (x, y - 2) not in hole and (x, y) not in edge(hole):
        S.set(x, y, HOLE_L)

# crab peeking out
face = ellipse(23, 49, 11, 8)
S.blob(face, CRAB, C_OUT, cuts=(-0.4, 0.3, 0.7))
for (x0, x1) in ((19, 16), (27, 30)):
    st = line(x0, 43, x1, 34, width=3)
    S.blob(st, CRAB, C_OUT, cuts=(-0.2, 0.5))
eyeball(S, 16, 33, 3.6, C_OUT, look=(0.6, 0.6))
eyeball(S, 30, 33, 3.6, C_OUT, look=(0.6, 0.6))
smile(S, 21, 50, 5, C_OUT)
blush(S, 16, 49)
blush(S, 28, 49)

# little claw in front
claw = ellipse(35, 55, 5, 4) - poly([(37, 50), (41, 50), (38, 55)])
S.blob(claw, CRAB, C_OUT, cuts=(-0.4, 0.3, 0.7))
S.set(33, 53, GLINT)
# legs
for (x0, y0, x1, y1) in ((15, 54, 12, 59), (19, 56, 17, 61), (27, 56, 28, 61)):
    S.fill(line(x0, y0, x1, y1), C_OUT)

finish(S, "pip")
