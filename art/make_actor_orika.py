"""Orika: an origami crane folded from soft pink paper, all crisp flat facets,
wings raised, a tiny dot eye and blush, with a little cream paper lantern
dangling from her beak on a thread."""
from pixelkit import hexc, ellipse, edge, rounded_rect
from portraitkit import new, poly, blush, finish, line, GLINT

S = new()

P = [hexc("#fff0f2"), hexc("#ffd2da"), hexc("#f7a8b8"), hexc("#e07890"), hexc("#b85a78")]
OUT = hexc("#6a2440")
DOT = hexc("#fff8f8")
EYE = hexc("#2a1a2e")
THREAD = hexc("#8a5a4a")
LANT = [hexc("#fff4d0"), hexc("#ffe8b0"), hexc("#f4cf86")]
LA_OUT = hexc("#6a3a22")
LRING = hexc("#a8332f")


def facet(points, c, drawn):
    m = poly(points)
    S.fill(m, c)
    drawn |= m
    return m


shape = set()
facets = []

# the far wing (behind, in shade)
facets.append(facet([(34, 44), (54, 4), (58, 8), (47, 44)], P[3], shape))
facets.append(facet([(34, 44), (54, 4), (46, 28)], P[4], shape))
# tail, rising to the right
facets.append(facet([(38, 52), (62, 34), (49, 55)], P[2], shape))
facets.append(facet([(38, 52), (62, 34), (60, 39), (44, 50)], P[3], shape))
# body: a plump folded diamond
facets.append(facet([(16, 53), (32, 39), (32, 63)], P[1], shape))
facets.append(facet([(32, 39), (48, 53), (32, 63)], P[3], shape))
facets.append(facet([(25, 47), (32, 40), (39, 47), (32, 54)], P[2], shape))
# neck, rising to the left, and a round-ish head folded down into a beak
facets.append(facet([(21, 52), (8, 27), (14, 25), (30, 48)], P[1], shape))
facets.append(facet([(21, 52), (10, 29), (27, 51)], P[2], shape))
facets.append(facet([(5, 23), (12, 18), (18, 22), (17, 28), (6, 38), (4, 31)], P[1], shape))
facets.append(facet([(17, 22), (17, 28), (6, 38), (10, 28)], P[2], shape))
# the near wing, raised up in front
facets.append(facet([(26, 47), (14, 3), (20, 2), (40, 43)], P[0], shape))
facets.append(facet([(26, 47), (20, 2), (27, 18), (40, 43)], P[1], shape))
facets.append(facet([(29, 46), (27, 18), (40, 43)], P[2], shape))

# crisp outlines around the whole silhouette and along the main folds
S.fill(edge(shape), OUT)
for a, b in (((26, 47), (20, 3)), ((32, 41), (32, 62)), ((34, 44), (52, 7)), ((21, 51), (10, 28)),
             ((38, 52), (60, 36))):
    for p in line(a[0], a[1], b[0], b[1]):
        if p in shape and p not in edge(shape):
            S.set(*p, P[3] if p[0] < 32 else P[4])
# washi dots on the near wing
for (x, y) in ((19, 9), (22, 15), (20, 21), (25, 26), (23, 32), (28, 36), (31, 40), (26, 41)):
    if (x, y) in shape:
        S.set(x, y, DOT)
S.set(16, 5, GLINT)
S.set(17, 7, GLINT)

# a tiny eye and blush on the head
for (x, y) in ((10, 23), (11, 23), (10, 24), (11, 24)):
    S.set(x, y, EYE)
S.set(10, 23, GLINT)
blush(S, 13, 26)

# a little paper lantern dangling from her beak
S.fill(line(6, 39, 6, 45), THREAD)
lant = rounded_rect(1, 46, 11, 11, 3)
S.blob(lant, LANT, LA_OUT, cuts=(-0.2, 0.5))
for x in range(3, 10):
    S.set(x, 46, LRING)
    S.set(x, 47, LRING)
    S.set(x, 55, LRING)
    S.set(x, 56, LRING)
for y in (49, 51, 53):
    for x in range(2, 11):
        if (x, y) in lant and (x, y) not in edge(lant):
            S.set(x, y, LANT[2])
S.set(3, 49, GLINT)

finish(S, "orika")
