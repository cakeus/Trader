"""32x32 paper lantern: a round red chochin with bamboo ribs, black lacquered top and bottom
rings, a hanging loop and a little tassel. No writing on it."""
from pixelkit import Sprite, hexc, ellipse, rounded_rect, edge

W = H = 32
S = Sprite(W, H)

RED = [hexc("#ffb08a"), hexc("#f27a5c"), hexc("#e0503f"), hexc("#a8332f")]
RED_OUT = hexc("#5e1c24")
RIB = hexc("#b83a34")
RIB_DEEP = hexc("#86262a")
CAP = [hexc("#7e78a0"), hexc("#4e4870"), hexc("#34304f")]
CAP_OUT = hexc("#17142b")
GOLD = [hexc("#ffe08a"), hexc("#e0a83a"), hexc("#a8702a")]
GLINT = hexc("#fff4ee")

CX = 15.5
TOP, BOT = 6, 23          # paper rows (the caps cover the ends)
body = {(x, y) for (x, y) in ellipse(CX, 14.5, 11.0, 10.4) if TOP <= y <= BOT}
S.blob(body, RED, RED_OUT, lx=1.0, ly=0.3, cuts=(-0.65, -0.05, 0.6))
inner = body - edge(body)
# bamboo ribs: every third row, darker on the shaded side
for (x, y) in inner:
    if (y - TOP) % 3 == 0:
        c = S.get(x, y)
        S.set(x, y, RIB_DEEP if c in (RED[3],) else RIB)
# top and bottom lacquer rings
top = rounded_rect(9, 3, 14, 4, r=1)
bot = rounded_rect(9, 22, 14, 4, r=1)
for m in (top, bot):
    S.blob(m, CAP, CAP_OUT, lx=0.9, ly=0.3, cuts=(-0.35, 0.45))
    y0 = min(y for x, y in m)
    for x in range(11, 21):
        if x < 14:
            S.set(x, y0 + 1, CAP[0])
# hanging loop
S.rows([".Gg.",
        "G..g",
        "g..g"], {"G": GOLD[0], "g": GOLD[2]}, 14, 0)
# a little tassel under the bottom ring
S.rows([".Gg.",
        "RRrr",
        "RRrr",
        "Rrrr",
        ".R.r"], {"g": GOLD[2], "G": GOLD[0], "R": RED[2], "r": RED[3]}, 14, 26)
# glints on the paper, upper-left
for (x, y) in ((8, 9), (8, 10), (9, 8), (7, 12)):
    S.set(x, y, GLINT)

S.center()
S.save("paper_lantern", "goods")
