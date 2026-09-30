"""Old Chochin: a chochin-obake, a hundred-year-old paper lantern come to
life. Aged cream paper glowing warm from inside, dark ribs, lacquered red top
and bottom rings, one big friendly eye, a patched tear and a long red tongue
lolling out of a grin."""
from pixelkit import hexc, ellipse, edge, rect, rounded_rect
from portraitkit import new, poly, eye, blush, clip, finish, curve, GLINT

S = new()

PAPER = [hexc("#fff4d0"), hexc("#ffe8b0"), hexc("#f4cf86"), hexc("#dcaa62")]
PA_OUT = hexc("#6a3a22")
RIB = hexc("#c8904e")
RING = [hexc("#f27a5c"), hexc("#e0503f"), hexc("#a8332f"), hexc("#86282a")]
RG_OUT = hexc("#5e1c24")
GLOW = hexc("#fffae4")
PATCH = [hexc("#fff8e4"), hexc("#f0dcb0")]
TONGUE = [hexc("#ffb0b8"), hexc("#f07088"), hexc("#c84a64")]
TG_OUT = hexc("#6a1a30")
MOUTH = hexc("#5a1a28")
EYEW = [hexc("#ffffff"), hexc("#f8f0e4"), hexc("#e0d0c0")]
IRIS = hexc("#2a1a2e")
METAL = [hexc("#e8d8b0"), hexc("#b8a078"), hexc("#806a4a")]
MT_OUT = hexc("#3a2a1a")

CX, CY, RX, RY = 32, 36, 21, 20

# wire hook on top
hook = curve([(32, 13), (32, 9), (33, 6), (35, 5), (37, 6), (37, 8)])
S.fill(hook, MT_OUT)
S.set(33, 7, METAL[0])

# the lantern body: round paper, lit from inside (brightest toward the middle-left)
body = ellipse(CX, CY, RX, RY)
be = edge(body)
for (x, y) in body:
    if (x, y) in be:
        S.set(x, y, PA_OUT)
        continue
    d = ((x - (CX - 3)) / RX) ** 2 + ((y - (CY - 2)) / RY) ** 2
    c = PAPER[0] if d < 0.2 else PAPER[1] if d < 0.55 else PAPER[2] if d < 0.85 else PAPER[3]
    S.set(x, y, c)
# bamboo ribs, gently curved around the round body
for y0 in range(20, 55, 4):
    for x in range(CX - RX, CX + RX + 1):
        dx = (x + 0.5 - CX) / RX
        y = y0 + round(1.2 * (1 - dx * dx))
        if (x, y) in body and (x, y) not in be:
            S.set(x, y, RIB)
# a patched tear, with little stitch marks
patch = rect(43, 25, 5, 4)
S.blob(patch, PATCH, PA_OUT, cuts=(-0.1, 0.8))
S.set(42, 26, PA_OUT)
S.set(48, 28, PA_OUT)

# lacquered rings top and bottom
top = rounded_rect(20, 13, 25, 5, 2)
S.blob(top, RING, RG_OUT, cuts=(-0.4, 0.2, 0.7))
bottom = rounded_rect(20, 54, 25, 6, 2)
S.blob(bottom, RING, RG_OUT, cuts=(-0.4, 0.2, 0.7))
S.set(22, 14, GLINT)
S.set(22, 55, GLINT)

# one big friendly eye
white = ellipse(32, 30, 8, 7.2)
S.blob(white, EYEW, PA_OUT, cuts=(-0.2, 0.6))
iris = ellipse(33, 31, 4, 4.4)
S.fill(iris, IRIS)
S.set(31, 28, GLINT)
S.set(32, 28, GLINT)
S.set(31, 29, GLINT)
S.set(35, 33, hexc("#5a4a6a"))
# a friendly brow of old ink
for (x, y) in ((26, 21), (27, 20), (28, 20), (29, 20), (30, 20), (31, 20), (32, 20), (33, 20), (34, 20), (35, 20), (36, 20), (37, 21)):
    S.set(x, y, PA_OUT)

# the grin where the paper splits, and the tongue lolling out
grin = poly([(19, 41), (45, 41), (40, 47), (24, 47)])
S.fill(grin, MOUTH)
S.fill(edge(grin), PA_OUT)
tongue = poly([(28, 44), (37, 44), (38, 51), (37, 59), (34, 62), (31, 61), (30, 55), (29, 49)])
S.blob(tongue, TONGUE, TG_OUT, cuts=(-0.3, 0.35))
for y in range(47, 58):
    S.set(33, y, TONGUE[2])
S.set(31, 47, TONGUE[0])
S.set(31, 48, TONGUE[0])
blush(S, 18, 35)
blush(S, 45, 35)

finish(S, "old_chochin")
