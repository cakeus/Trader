"""Baker Bun: a cream bunny pastry chef with a puffy chef hat, lop ears,
a pink shirt and a floury white apron with a strawberry patch."""
from pixelkit import hexc, ellipse, edge, rect
from portraitkit import new, eye, blush, clip, finish, GLINT

S = new()

FUR = [hexc("#fffaf2"), hexc("#f6e2cc"), hexc("#e2c2a4"), hexc("#c49c80")]
F_OUT = hexc("#6e4a3a")
EAR_IN = hexc("#f6b4b8")
HAT = [hexc("#ffffff"), hexc("#f0eef4"), hexc("#d4d0e0"), hexc("#b4aec8")]
HAT_OUT = hexc("#5a5470")
SHIRT = [hexc("#ffc4c8"), hexc("#f48c98"), hexc("#d4647a"), hexc("#b04a64")]
SH_OUT = hexc("#6a2238")
APRON = [hexc("#ffffff"), hexc("#f4f0ec"), hexc("#dcd4cc")]
AP_OUT = hexc("#7a6a66")
BERRY = hexc("#e63a40")
BERRY_D = hexc("#9c1c34")
LEAF = hexc("#5cbe4c")
FLOUR = hexc("#fffaf2")
NOSE = hexc("#e87890")

# shirt shoulders
shirt = clip(ellipse(32, 64, 27, 14))
S.blob(shirt, SHIRT, SH_OUT, cuts=(-0.5, 0.2, 0.7))
# apron bib over the shirt
apron = rect(22, 52, 21, 12)
S.blob(apron, APRON, AP_OUT, cuts=(-0.3, 0.5))
for (x, y) in ((24, 51), (23, 50), (40, 51), (41, 50)):   # neck straps
    S.set(x, y, AP_OUT)
# strawberry patch on the apron
for (x, y) in ((31, 56), (32, 56), (33, 56), (31, 57), (32, 57), (33, 57), (32, 58)):
    S.set(x, y, BERRY)
S.set(33, 57, BERRY_D)
S.set(32, 58, BERRY_D)
S.set(31, 55, LEAF)
S.set(33, 55, LEAF)
S.set(32, 55, LEAF)
S.set(31, 56, hexc("#ff9a8a"))

# lop ears hanging down beside the head
for cx in (14, 50):
    ear = ellipse(cx, 38, 5, 11)
    S.blob(ear, FUR, F_OUT, cuts=(-0.4, 0.3, 0.7))
    inner = ellipse(cx, 39, 2.5, 8) - edge(ear)
    S.fill(inner, EAR_IN)

# head
head = ellipse(32, 33, 16, 14)
S.blob(head, FUR, F_OUT, cuts=(-0.5, 0.25, 0.75))

# chef hat: puffy top and a band
puff = ellipse(24, 10, 7, 6) | ellipse(32, 7, 8, 7) | ellipse(40, 10, 7, 6)
S.blob(puff, HAT, HAT_OUT, cuts=(-0.4, 0.3, 0.75))
band = rect(20, 14, 25, 7)
S.blob(band, HAT, HAT_OUT, cuts=(-0.3, 0.4, 0.8))
for x in range(22, 43, 4):   # pleats
    S.set(x, 16, HAT[2])
    S.set(x, 17, HAT[2])
S.set(27, 4, GLINT)
S.set(28, 4, GLINT)

# face
eye(S, 24, 29, 3, 4)
eye(S, 37, 29, 3, 4)
for (x, y) in ((31, 35), (32, 35), (33, 35), (32, 36)):
    S.set(x, y, NOSE)
S.set(32, 37, F_OUT)
S.set(30, 38, F_OUT)
S.set(31, 38, F_OUT)
S.set(33, 38, F_OUT)
S.set(34, 38, F_OUT)
# buck teeth
S.set(31, 39, hexc("#ffffff"))
S.set(33, 39, hexc("#ffffff"))
S.set(32, 39, hexc("#d4ccdc"))
blush(S, 21, 35)
blush(S, 42, 35)
# flour dust on cheek and apron
for (x, y) in ((44, 30), (46, 32), (25, 60), (38, 59), (35, 62)):
    S.set(x, y, FLOUR)

finish(S, "baker_bun")
