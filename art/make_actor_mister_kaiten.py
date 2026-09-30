"""Mister Kaiten: a conveyor-belt sushi robot. A cream enamel head with a red
lacquer band, round lamp eyes and a little plate of sushi turning on his head,
sitting behind his own belt of coloured plates going round."""
from pixelkit import hexc, ellipse, edge, rect, rounded_rect
from portraitkit import new, line, blush, clip, finish, GLINT

S = new()

ENAMEL = [hexc("#fffaf0"), hexc("#f2e6d2"), hexc("#dac8b0"), hexc("#b8a48c")]
EN_OUT = hexc("#5a4638")
LACQ = [hexc("#f27a5c"), hexc("#e0503f"), hexc("#a8332f"), hexc("#822630")]
LQ_OUT = hexc("#5e1c24")
STEEL = [hexc("#eef2f8"), hexc("#b8c2d4"), hexc("#8a96ae"), hexc("#66708a")]
ST_OUT = hexc("#2a2f44")
BELT = [hexc("#6a6e86"), hexc("#50546c"), hexc("#3c3f54")]
LAMP = hexc("#2a1a2e")
LAMP_L = hexc("#ffd98a")
RICE = [hexc("#ffffff"), hexc("#f4f0e8"), hexc("#dcd4c8")]
RI_OUT = hexc("#8a7a6e")
SALMON = [hexc("#ffb48a"), hexc("#f98a5a"), hexc("#d8663e")]
TUNA = [hexc("#ff7a84"), hexc("#e0404e"), hexc("#b02a3c")]
EGG = [hexc("#fff0a0"), hexc("#ffd54a"), hexc("#e0a832")]
NORI = hexc("#23302a")
FISH_OUT = hexc("#6a2a26")
PLATES = [
    ([hexc("#a8d4ff"), hexc("#5a9ae0"), hexc("#3c70b4")], hexc("#1e3060")),
    ([hexc("#ff9a8a"), hexc("#e0503f"), hexc("#a8332f")], hexc("#5e1c24")),
    ([hexc("#fff0a0"), hexc("#f4c24a"), hexc("#c08a2a")], hexc("#6a4418")),
]


def plate(cx, cy, colors):
    ramp, out = colors
    p = ellipse(cx, cy, 7.5, 2.6)
    S.blob(p, ramp, out, cuts=(-0.3, 0.4))
    S.fill({(x, cy) for x in range(cx - 3, cx + 4)} - edge(p), ramp[2])


def nigiri(cx, cy, fish, stripe=None, nori=False):
    rice = ellipse(cx, cy, 4.6, 2.4)
    S.blob(rice, RICE, RI_OUT, cuts=(-0.2, 0.6))
    top = ellipse(cx, cy - 2.5, 5.6, 2.0)
    S.blob(top, fish, FISH_OUT, cuts=(-0.3, 0.4))
    if stripe:
        for dx in (-3, 0, 3):
            S.set(cx + dx, cy - 3, stripe)
            S.set(cx + dx + 1, cy - 2, stripe)
    if nori:
        for y in range(cy - 3, cy + 2):
            S.set(cx, y, NORI)
    S.set(cx - 3, cy - 3, GLINT)


# conveyor belt: a steel counter with a slatted belt and plates riding on it
counter = clip(rounded_rect(2, 54, 60, 12, 2))
S.blob(counter, STEEL, ST_OUT, cuts=(-0.6, 0.1, 0.7))
belt = {(x, y) for x in range(4, 60) for y in range(52, 56)}
S.fill(belt, BELT[1])
S.fill(edge(belt), ST_OUT)
for x in range(6, 58, 4):   # slats
    S.set(x, 53, BELT[2])
    S.set(x, 54, BELT[2])
for x in range(5, 59):
    S.set(x, 53, BELT[0]) if x % 4 == 1 else None
# rail and rivets on the counter front
for x in range(4, 60):
    S.set(x, 58, STEEL[0] if x < 32 else STEEL[1])
for x in (7, 20, 44, 57):
    S.set(x, 61, STEEL[3])
# little motion ticks at the ends
for (x, y) in ((1, 51), (2, 50), (62, 51), (61, 50)):
    S.set(x, y, STEEL[2])

# neck coming up from behind the belt
S.blob(rect(26, 42, 12, 10), STEEL, ST_OUT, cuts=(-0.3, 0.3, 0.8))
for y in (45, 48):
    for x in range(27, 37):
        S.set(x, y, STEEL[3])

# round speaker ears
for cx in (13, 51):
    ear = ellipse(cx, 30, 4, 5.5)
    S.blob(ear, LACQ, LQ_OUT, cuts=(-0.3, 0.3, 0.7))
    S.set(cx, 30, LQ_OUT)
    S.set(cx - 1, 28, LACQ[0])

# head: cream enamel box with a red lacquer band on top
head = rounded_rect(15, 15, 34, 29, 4)
S.blob(head, ENAMEL, EN_OUT, cuts=(-0.5, 0.2, 0.75))
band = {(x, y) for (x, y) in head - edge(head) if y <= 19}
S.blob(band, LACQ, None, cuts=(-0.4, 0.2, 0.7), center=(30, 22))
for x in range(16, 48):
    if (x, 20) in head and (x, 20) not in edge(head):
        S.set(x, 20, LQ_OUT)
for (x, y) in ((18, 22), (18, 23), (19, 22)):
    S.set(x, y, GLINT)

# face: round lamp eyes and a wide happy mouth
for ex in (24, 40):
    rim = ellipse(ex, 29, 4, 4)
    S.blob(rim, STEEL, ST_OUT, cuts=(-0.3, 0.4))
    lens = ellipse(ex, 29, 2.4, 2.4)
    S.fill(lens, LAMP)
    S.set(ex - 1, 28, GLINT)
    S.set(ex, 28, LAMP_L)
mouth = {(x, 37) for x in range(28, 37)} | {(27, 36), (37, 36)}
S.fill(mouth, EN_OUT)
S.fill({(x, 38) for x in range(29, 36)}, EN_OUT)
S.fill({(x, 37) for x in range(29, 36)}, hexc("#c85a5a"))
blush(S, 18, 34)
blush(S, 45, 34)
for (x, y) in ((17, 40), (46, 40)):
    S.set(x, y, ENAMEL[3])

# a plate of salmon nigiri turning on his head, with a spindle
S.blob(rect(30, 11, 4, 4), STEEL, ST_OUT, cuts=(-0.2, 0.5))
plate(32, 10, PLATES[0])
nigiri(32, 8, SALMON, stripe=SALMON[0])
for (x, y) in ((22, 8), (21, 9), (42, 8), (43, 9)):   # spin arcs
    S.set(x, y, STEEL[2])

# plates riding the belt
plate(12, 51, PLATES[1])
nigiri(12, 49, TUNA)
plate(32, 51, PLATES[2])
nigiri(32, 49, EGG, nori=True)
plate(52, 51, PLATES[0])
nigiri(52, 49, SALMON, stripe=SALMON[0])

finish(S, "mister_kaiten")
