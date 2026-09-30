"""32x32 sushi roll: one fat maki slice seen from above-front, a dark nori wrap around white rice
with a tuna-red center and a sliver of cucumber."""
import random

from pixelkit import Sprite, hexc, ellipse, rect, edge

W = H = 32
S = Sprite(W, H)

NORI = [hexc("#4c6a58"), hexc("#2f4a40"), hexc("#223830"), hexc("#182a26")]
NORI_OUT = hexc("#0f1c1c")
RICE = [hexc("#fffdf6"), hexc("#f4eedf"), hexc("#dcd2bf")]
RICE_DOT = hexc("#cfc3ac")
TUNA = [hexc("#ff8e8a"), hexc("#e8505a"), hexc("#b83246")]
TUNA_OUT = hexc("#7a1e34")
CUKE = [hexc("#a8e07a"), hexc("#5cae4c")]
GLINT = hexc("#ffffff")

CX, TOP, BOT, RX, RY = 15.5, 11.0, 19.0, 13.0, 8.0

# the whole roll: top ellipse, a straight side, a bottom ellipse, all nori
body = ellipse(CX, TOP, RX, RY) | ellipse(CX, BOT, RX, RY) | \
    {(x, y) for (x, y) in rect(0, int(TOP), 32, int(BOT - TOP) + 1) if abs(x - CX) <= RX}
S.blob(body, NORI, NORI_OUT, lx=1.0, ly=0.15, cuts=(-0.6, 0.0, 0.6))
# a sheen and a few seaweed flecks down the side
for (x, y) in body - edge(body):
    if y > TOP + 3:
        if round(x - CX) in (-9, -8) and (x, y) not in ellipse(CX, TOP, RX, RY):
            S.set(x, y, NORI[0])
        elif (x * 7 + y * 3) % 17 == 0 and x > CX - 6:
            S.set(x, y, NORI[3])
# the cut face: nori rim, rice, filling
face = ellipse(CX, TOP, RX, RY)
S.fill(edge(face), NORI_OUT)
rim = face - edge(face)
S.fill(edge(rim), NORI[1])
rice = rim - edge(rim)
S.blob(rice, RICE, None, lx=0.7, ly=0.6, cuts=(-0.35, 0.45))
rnd = random.Random(3)
for (x, y) in sorted(rice):
    if rnd.random() < 0.13:
        S.set(x, y, RICE_DOT)
        if (x - 1, y) in rice and rnd.random() < 0.5:
            S.set(x - 1, y, RICE[0])
# filling: tuna with a little cucumber on its right
cuke = ellipse(CX + 4.5, TOP, 2.7, 2.5)
S.blob(cuke, CUKE, hexc("#2c5a30"), lx=0.7, ly=0.6, cuts=(0.2,))
tuna = ellipse(CX - 1.5, TOP, 5.3, 3.4)
S.blob(tuna, TUNA, TUNA_OUT, lx=0.7, ly=0.6, cuts=(-0.3, 0.4))
for (x, y) in ((int(CX) - 5, int(TOP) - 1), (int(CX) - 4, int(TOP) - 2)):
    S.set(x, y, GLINT)
# glint on the rice, upper-left
for (x, y) in ((7, 8), (8, 7), (6, 9)):
    S.set(x, y, GLINT)

S.center()
S.save("sushi_roll", "goods")
