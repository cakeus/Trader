"""32x32 old vinyl record peeking out of a mustard sleeve."""
from pixelkit import Sprite, hexc, ellipse, rect, edge

W = H = 32
S = Sprite(W, H)

# vinyl: deep indigo, not black
V_OUT = hexc("#1e1630")
V_RAMP = [hexc("#6a5a8c"), hexc("#46395f"), hexc("#342a4a"), hexc("#2a2140")]
GROOVE = hexc("#221a36")
SHEEN = hexc("#9a8cc0")
LABEL = [hexc("#ff9a8a"), hexc("#e8534e"), hexc("#b83a44")]
HOLE = hexc("#1e1630")

# sleeve: mustard card with a little sun print
S_OUT = hexc("#6e4a1c")
S_RAMP = [hexc("#ffe08a"), hexc("#f5c35a"), hexc("#dc9c3c"), hexc("#b87a2c")]
SUN = [hexc("#fff4d8"), hexc("#ff8a5c"), hexc("#d85a44")]
STRIPE = hexc("#3f8f8a")
STRIPE_L = hexc("#6cc2b4")
GLINT = hexc("#fffaf0")

CX, CY, R = 20.0, 11.0, 10.6
disc = ellipse(CX, CY, R, R)
S.blob(disc, V_RAMP, V_OUT, lx=0.7, ly=0.7, cuts=(-0.5, 0.1, 0.6))

inner = disc - edge(disc)
# grooves: concentric rings
for rr in (8.2, 6.0):
    for (x, y) in inner:
        d = ((x - CX) ** 2 + (y - CY) ** 2) ** 0.5
        if abs(d - rr) < 0.5:
            S.set(x, y, GROOVE)
# sheen arc on upper-left
for (x, y) in inner:
    d = ((x - CX) ** 2 + (y - CY) ** 2) ** 0.5
    if 6.6 < d < 7.6 and x < CX - 2 and y < CY - 2:
        S.set(x, y, SHEEN)
# label
label = ellipse(CX, CY, 3.2, 3.2)
S.blob(label, LABEL, None, lx=0.7, ly=0.7, cuts=(-0.2, 0.5))
S.set(int(CX), int(CY), HOLE)

# sleeve in front
sleeve = rect(2, 12, 18, 18)
S.blob(sleeve, S_RAMP, S_OUT, lx=0.6, ly=0.6, cuts=(-0.6, 0.35, 0.8))
# sunset print: a half sun sitting on teal sea stripes
sun = {p for p in ellipse(11, 23, 5.6, 5.6) if p[1] < 23}
S.blob(sun, SUN, None, lx=0.7, ly=0.9, cuts=(-0.4, 0.3))
for x in range(3, 19):
    S.set(x, 23, STRIPE_L)
    S.set(x, 24, STRIPE)
    S.set(x, 26, STRIPE)
for x in range(5, 17, 3):
    S.set(x, 25, STRIPE_L)
# glint on sleeve corner
for (x, y) in ((3, 13), (4, 13), (3, 14)):
    S.set(x, y, GLINT)

S.center()
S.save("old_record", "goods")
