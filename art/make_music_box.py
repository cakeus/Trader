"""32x32 music box: a wooden box, lid open on velvet and a mirror, gold trim, wind-up key."""
from pixelkit import Sprite, hexc, rect, ellipse

W = H = 32
S = Sprite(W, H)

WOOD = [hexc("#e8a86a"), hexc("#c07a44"), hexc("#98572e"), hexc("#733c22")]
WOOD_OUT = hexc("#48241a")
VELVET = [hexc("#f08094"), hexc("#c84a6a"), hexc("#962e52")]
GOLD = [hexc("#fff4b0"), hexc("#ffd24a"), hexc("#d89a2a"), hexc("#a8701e")]
GOLD_OUT = hexc("#6a4418")
DARK = hexc("#4a2a22")
NOTE = hexc("#7462bc")
MIRROR = [hexc("#eef8ff"), hexc("#bcdcf0"), hexc("#8cb4d8")]
KP = {"O": hexc("#6a4418"), "G": GOLD[1], "g": GOLD[2], "d": GOLD[3]}
GLINT = hexc("#fff6e8")

# lid, open and leaning back: we see its velvet lining
lid = rect(4, 5, 22, 10)
S.blob(lid, WOOD, WOOD_OUT, lx=0.8, ly=0.4, cuts=(-0.4, 0.3, 0.7))
lining = rect(6, 7, 18, 6)
S.blob(lining, VELVET, None, lx=0.7, ly=0.6, cuts=(-0.2, 0.5))
# an oval mirror in the lining, with a glint
mirror = ellipse(15, 9.5, 4.2, 2.6)
S.blob(mirror, MIRROR, GOLD[2], lx=0.8, ly=0.6, cuts=(-0.3, 0.4))
S.set(13, 8, hexc("#ffffff"))
S.set(14, 8, MIRROR[0])
# box opening: dark inside with a brass cylinder and a steel comb
S.fill(rect(4, 15, 22, 3), WOOD_OUT)
S.fill(rect(5, 16, 20, 2), DARK)
for x in range(7, 18):
    S.set(x, 16, GOLD[1] if x % 2 else GOLD[0])
    S.set(x, 17, GOLD[2])
for x in range(19, 24):
    S.set(x, 16, hexc("#c8d0dc"))
    S.set(x, 17, hexc("#8a96a8"))
# box front
front = rect(3, 18, 24, 11)
S.blob(front, WOOD, WOOD_OUT, lx=0.9, ly=0.5, cuts=(-0.45, 0.25, 0.7))
# wood grain
for x in range(6, 25, 5):
    S.set(x, 24, WOOD[2])
    S.set(x + 1, 24, WOOD[2])
# gold trim along the top of the front and at the bottom corners
for x in range(4, 26):
    S.set(x, 19, GOLD[1] if x < 16 else GOLD[2])
for (x, y) in ((4, 27), (5, 27), (25, 27), (24, 27)):
    S.set(x, y, GOLD[2])
# keyhole plate
plate = rect(13, 21, 4, 5)
S.blob(plate, GOLD, GOLD_OUT, cuts=(-0.1, 0.5))
S.set(14, 22, GOLD[0])
S.set(15, 23, DARK)
S.set(15, 24, DARK)
# little feet
for fx in (4, 23):
    S.fill(rect(fx, 29, 3, 1), WOOD_OUT)
# wind-up key on the right side: a stem out of the box and a two-lobed grip
S.fill(rect(27, 22, 2, 2), GOLD[2])
S.set(27, 22, GOLD[1])
lobe = [".OOO.", "OGgdO", "OgddO", ".OOO."]
S.rows(lobe, KP, 27, 17)
S.rows(lobe, KP, 27, 24)
S.fill(rect(29, 20, 1, 5), GOLD_OUT)
S.fill(rect(28, 21, 1, 3), GOLD[1])
S.set(28, 18, GOLD[0])
# a floating music note
S.rows(["..OO", "..OO", "..O.", "..O.", "OOO.", "OO.."], {"O": NOTE}, 27, 2)
S.set(27, 6, hexc("#b8a8f0"))
# glints
for (x, y) in ((5, 6), (6, 6), (5, 7), (4, 20)):
    S.set(x, y, GLINT)

S.center()
S.save("music_box", "goods")
