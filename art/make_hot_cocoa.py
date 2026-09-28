"""32x32 hot cocoa: a red mug with a cream band, two marshmallows and a curl of steam."""
from pixelkit import Sprite, hexc, ellipse, rect, rounded_rect, edge

W = H = 32
S = Sprite(W, H)

MUG = [hexc("#ff8a7a"), hexc("#e0474c"), hexc("#b83244"), hexc("#8c2238")]
MUG_OUT = hexc("#5a1626")
BAND = [hexc("#fff6e8"), hexc("#f4e0c8"), hexc("#dcc0a8")]
COCOA = [hexc("#b0704a"), hexc("#8a4e32"), hexc("#6a3624")]
MALLOW = [hexc("#fffaf4"), hexc("#f8e4e8"), hexc("#e8c0cc")]
MALLOW_OUT = hexc("#9a6070")
STEAM = [hexc("#fbf8ff"), hexc("#d4ccf0"), hexc("#a49ccc")]
GLINT = hexc("#fff4ee")

CX = 13.5
# handle first so the body overlaps it
handle = {p for p in ellipse(22.5, 20.5, 5.2, 5.0) - ellipse(22.5, 20.5, 2.4, 2.3) if p[0] >= 21}
S.blob(handle, MUG, MUG_OUT, lx=0.5, ly=0.8, cuts=(-0.1, 0.5))

body = rounded_rect(4, 13, 20, 17, r=3)
S.blob(body, MUG, MUG_OUT, lx=1.0, ly=0.25, cuts=(-0.55, 0.25, 0.75))
# cream band with little red dots
inner = body - edge(body)
for (x, y) in inner:
    if y in (19, 20, 21):
        t = (x - CX) / 9
        S.set(x, y, BAND[0] if t < -0.45 else BAND[1] if t < 0.5 else BAND[2])
for x in range(7, 22, 4):
    S.set(x, 20, MUG[1])
    S.set(x + 1, 20, MUG[2])
# rim and cocoa surface
rim = ellipse(CX, 13, 10, 3.2)
S.blob(rim, [MUG[0], MUG[0], MUG[1]], MUG_OUT, lx=0.9, ly=0.2, cuts=(0.2,))
cocoa = ellipse(CX, 13.5, 7.6, 1.9)
S.blob(cocoa, COCOA, None, lx=0.6, ly=0.6, cuts=(-0.3, 0.4))
# marshmallows: two little cubes bobbing in the cocoa
for (mx, my) in ((8, 10), (14, 11)):
    m = rect(mx, my, 5, 4)
    S.blob(m, MALLOW, MALLOW_OUT, lx=0.7, ly=0.7, cuts=(-0.1, 0.6))
    S.set(mx + 1, my + 1, hexc("#ffffff"))
# steam: a soft S-curl above the mug
curl = [
    "......aab...",
    ".....abbc...",
    "....abc.....",
    "....ab......",
    ".....bb.....",
    "......bbc...",
    ".......bc...",
    "......bbc...",
    ".....bbc....",
]
SP = {"a": STEAM[0], "b": STEAM[1], "c": STEAM[2]}
S.rows(curl, SP, 10, 0)
S.rows(["ab.", "b..", "bb.", ".bc"], SP, 19, 3)
# glint on the upper-left of the mug
for (x, y) in ((6, 17), (6, 18), (7, 16), (6, 23)):
    S.set(x, y, GLINT)

S.center()
S.save("hot_cocoa", "goods")
