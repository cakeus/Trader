"""640x480 Blossom Market: sunny morning, striped stalls, bunting, flower carts.

Kept soft and a little hazy so the cream actor cards (slots in locations.json)
pop in front of it. Interest lives in the stall band and the skyline.
"""
import math
import random

from bgkit import W, H, new_bg, vgrad, dith, haze, paste, save_bg, mock
from pixelkit import Sprite, hexc, mix, ellipse, rect, edge

R = random.Random(21)
img, d = new_bg()
px = img.load()

HORIZON = 232
GROUND = 344

# ------------------------------------------------------------------- sky ---
vgrad(img, 0, 0, W, HORIZON, [hexc("#a8dcec"), hexc("#c4e8ee"), hexc("#e4f2e6"), hexc("#fbecd6")])


def cloud(cx, cy, w):
    S = Sprite(w + 8, w // 2 + 8)
    m = set()
    for i in range(4):
        r = w / 5 + R.random() * w / 8
        m |= ellipse(4 + w * (0.2 + 0.2 * i), 4 + w / 4 + (1 if i % 2 else -1) * 1.5, r, r * 0.7)
    flat = max(y for _, y in m) - 1
    m = {p for p in m if p[1] <= flat}
    S.blob(m, [hexc("#fffdf6"), hexc("#fbf4ec"), hexc("#ece4ec")], None, lx=0.3, ly=0.9, cuts=(0.1, 0.6))
    paste(img, S, cx - w // 2, cy)


for (x, y, w) in ((120, 44, 70), (330, 30, 90), (540, 70, 60), (430, 120, 44), (40, 132, 40)):
    cloud(x, y, w)

# --------------------------------------------------------- far skyline ---
FAR = [hexc("#c8d8e0"), hexc("#b4c8d8")]
x = -10
while x < W:
    w = R.randint(34, 58)
    top = R.randint(150, 178)
    peak = top - R.randint(10, 18)
    col = FAR[R.randint(0, 1)]
    for yy in range(peak, HORIZON + 10):
        for xx in range(x, x + w):
            if 0 <= xx < W:
                # gable roof
                half = w / 2
                roof_y = peak + abs(xx - (x + half)) * (top - peak) / half
                if yy >= roof_y:
                    px[xx, yy] = col
    # windows
    for wx in range(x + 6, x + w - 6, 10):
        for wy in range(top + 8, HORIZON, 14):
            if 0 <= wx < W - 3:
                for a in range(3):
                    for b in range(4):
                        px[wx + a, wy + b] = mix(col, hexc("#fff4dc"), 0.45)
    if R.random() < 0.5 and 0 <= x + 8 < W - 4:  # chimney
        for a in range(4):
            for b in range(8):
                px[x + 8 + a, peak + 4 - b + (top - peak) * 8 // (w // 2) // 2] = col
    x += w + R.randint(-4, 6)

# a clock tower centred behind the market
tx = 322
for yy in range(96, HORIZON):
    for xx in range(tx - 14, tx + 14):
        px[xx, yy] = hexc("#bcccd8") if xx < tx + 6 else hexc("#aebfd0")
for yy in range(76, 96):
    half = (yy - 76) * 16 // 20
    for xx in range(tx - half, tx + half):
        px[xx, yy] = hexc("#c8a8b8")
d.ellipse([tx - 8, 108, tx + 8, 124], fill=hexc("#fbf4ec"), outline=hexc("#98a8bc"))
d.line([tx, 116, tx, 110], fill=hexc("#6a7a90"))
d.line([tx, 116, tx + 4, 116], fill=hexc("#6a7a90"))

haze(img, hexc("#f4efe6"), 0.28, (0, 60, W, HORIZON + 10))

# --------------------------------------------------- near shopfronts -----
NEAR = [hexc("#f2c8b8"), hexc("#f4dca8"), hexc("#c8dcc0"), hexc("#d8c8e8"), hexc("#f0d0d8"), hexc("#c8d8e8")]
x = -6
i = 0
while x < W:
    w = R.randint(62, 86)
    top = R.randint(186, 204)
    col = NEAR[i % len(NEAR)]
    shade = mix(col, hexc("#806070"), 0.22)
    outl = mix(col, hexc("#403040"), 0.5)
    d.rectangle([x, top, x + w - 1, GROUND], fill=col, outline=outl)
    d.rectangle([x + w - 6, top + 1, x + w - 2, GROUND], fill=shade)
    # cornice
    d.rectangle([x - 2, top - 5, x + w + 1, top], fill=mix(col, hexc("#ffffff"), 0.35), outline=outl)
    # upper windows with sills
    for wx in range(x + 8, x + w - 14, 18):
        if wx < 0 or wx > W - 12:
            continue
        d.rectangle([wx, top + 10, wx + 9, top + 22], fill=hexc("#9cc4d8"), outline=outl)
        d.line([wx + 1, top + 11, wx + 3, top + 11], fill=hexc("#e8f6f8"))
        d.rectangle([wx - 1, top + 23, wx + 10, top + 24], fill=mix(col, hexc("#ffffff"), 0.4))
        if R.random() < 0.6:  # window box flowers
            for k in range(0, 10, 2):
                if 0 <= wx + k < W:
                    px[wx + k, top + 22] = R.choice([hexc("#f08ab0"), hexc("#ffd24a"), hexc("#e8534e")])
    x += w
    i += 1
haze(img, hexc("#f6efe4"), 0.22, (0, 170, W, GROUND))

# ---------------------------------------------------------- mid: trees ---


def blossom_tree(x, base, r):
    S = Sprite(2 * r + 12, 2 * r + 40)
    trunk = rect(r + 3, 2 * r - 4, 5, 40)
    S.blob(trunk, [hexc("#b08070"), hexc("#906058"), hexc("#704848")], hexc("#503038"), lx=1, ly=0, cuts=(-0.3, 0.4))
    can = set()
    for (cx, cy, rr) in ((r + 5, r, r), (r * 0.6, r * 1.3, r * 0.65), (r * 1.5 + 4, r * 1.3, r * 0.65)):
        can |= ellipse(cx, cy, rr, rr * 0.85)
    S.blob(can, [hexc("#ffe4ec"), hexc("#f8c4d4"), hexc("#e8a4bc"), hexc("#d088a4")], hexc("#a0607c"),
           cuts=(-0.35, 0.15, 0.55))
    paste(img, S, x - r - 5, base - (2 * r + 36))



# ---------------------------------------------------------- stalls ------


def stall(x, w, top, stripe, goods):
    """Market stall: striped awning, posts, counter with produce."""
    base = GROUND + 6
    S = Sprite(w + 4, base - top + 2)
    ox, oy = 2, 0
    so = mix(stripe, hexc("#402030"), 0.55)
    # back cloth (down to the counter), shaded toward the bottom
    cloth_h = (base - top) - 30 - 18
    for yy in range(cloth_h):
        c = mix(mix(stripe, hexc("#fff4e4"), 0.7), mix(stripe, hexc("#604050"), 0.25), yy / cloth_h)
        for xx in range(ox + 3, ox + w - 3):
            S.set(xx, oy + 18 + yy, c)
    # posts
    for pxx in (ox + 2, ox + w - 5):
        S.blob(rect(pxx, oy + 10, 3, base - top - 10), [hexc("#c89868"), hexc("#a07048"), hexc("#805838")],
               hexc("#503028"), lx=1, ly=0, cuts=(-0.2, 0.5))
    # awning
    aw = rect(ox, oy + 4, w, 14) | {(xx, oy + 18) for xx in range(ox, ox + w) if (xx - ox) % 8 in (1, 2, 3, 4, 5)} \
        | {(xx, oy + 19) for xx in range(ox, ox + w) if (xx - ox) % 8 in (2, 3, 4)}
    for (xx, yy) in aw:
        on = ((xx - ox) // 8) % 2 == 0
        c = stripe if on else hexc("#fff4e4")
        if yy <= oy + 6:
            c = mix(c, hexc("#ffffff"), 0.35)
        elif yy >= oy + 15:
            c = mix(c, hexc("#603040"), 0.15)
        S.set(xx, yy, c)
    for p in edge(aw):
        S.set(*p, so)
    # roof ridge
    ridge = rect(ox + 4, oy, w - 8, 5)
    S.blob(ridge, [mix(stripe, hexc("#ffffff"), 0.3), stripe], so, lx=0, ly=1, cuts=(0.2,))
    # counter
    cy = oy + (base - top) - 30
    counter = rect(ox + 1, cy, w - 2, 30)
    S.blob(counter, [hexc("#e0b080"), hexc("#c89060"), hexc("#a87048"), hexc("#886040")], hexc("#503028"),
           lx=0.5, ly=0.8, cuts=(-0.6, 0.1, 0.6))
    for yy in range(cy + 9, cy + 30, 8):
        for xx in range(ox + 2, ox + w - 2):
            S.set(xx, yy, hexc("#9a6a48"))
    # produce piles on the counter
    gx = ox + 5
    for g in goods:
        pile = set()
        for i in range(5):
            pile |= ellipse(gx + 2 + i * 3, cy - 2 - (i % 2) * 2, 2.6, 2.4)
        S.blob(pile, g, mix(g[-1], hexc("#301828"), 0.5), cuts=(-0.2, 0.5))
        gx += 20
        if gx > ox + w - 18:
            break
    paste(img, S, x - 2, top)


BERRY = [hexc("#ff8a8a"), hexc("#e8534e"), hexc("#b83a44")]
LEMON = [hexc("#fff4a0"), hexc("#ffd24a"), hexc("#e0a030")]
APPLE = [hexc("#c8f09a"), hexc("#8ecf5a"), hexc("#5a9a44")]
PLUM = [hexc("#d8b0f0"), hexc("#a878d0"), hexc("#7a54a8")]
PEACH = [hexc("#ffd8b0"), hexc("#ffb080"), hexc("#e08858")]
stall(-10, 96, 236, hexc("#e8676a"), [BERRY, LEMON, APPLE, BERRY])
stall(104, 110, 222, hexc("#6aa8d8"), [PLUM, PEACH, APPLE, LEMON, PLUM])
stall(232, 100, 240, hexc("#f0a848"), [APPLE, BERRY, PEACH, BERRY])
stall(350, 112, 226, hexc("#8ec06a"), [LEMON, PLUM, BERRY, APPLE, PEACH])
stall(480, 100, 238, hexc("#e888b0"), [PEACH, APPLE, LEMON, BERRY])
stall(596, 90, 224, hexc("#9a84d0"), [BERRY, PLUM, LEMON])

blossom_tree(14, GROUND + 6, 30)
blossom_tree(630, GROUND + 4, 28)

# --------------------------------------------------------- bunting ------
FLAGS = [hexc("#f4a0a8"), hexc("#ffe08a"), hexc("#a8d8f0"), hexc("#b8e0a0"), hexc("#d8b8f0")]
for (y0, sag, phase) in ((78, 26, 0), (104, 20, 2)):
    pts = []
    for x in range(0, W):
        t = (x % 320) / 320
        y = y0 + sag * 4 * t * (1 - t)
        pts.append((x, int(y)))
        px[x, int(y)] = hexc("#8a7078")
    for i, x in enumerate(range(8 + phase * 7, W - 6, 16)):
        _, y = pts[x]
        c = FLAGS[(i + phase) % len(FLAGS)]
        oc = mix(c, hexc("#402838"), 0.5)
        for row in range(9):
            half = (9 - row) * 5 // 9
            for dx in range(-half, half + 1):
                xx, yy = x + dx, y + 1 + row
                edge_ = abs(dx) == half or row == 0
                px[xx, yy] = oc if edge_ else (mix(c, hexc("#ffffff"), 0.3) if dx < 0 and row < 3 else c)

# ----------------------------------------------------------- ground -----
for y in range(GROUND, H):
    band = (y - GROUND) // 7
    off = (band % 2) * 9
    for x in range(W):
        yy = (y - GROUND) % 7
        xx = (x + off) % 18
        depth = (y - GROUND) / (H - GROUND)
        base = mix(hexc("#ecd6b4"), hexc("#dcc09c"), depth)
        if yy == 6 or xx == 17:
            c = mix(base, hexc("#a88870"), 0.45)
        elif yy == 0:
            c = mix(base, hexc("#fff4e0"), 0.4)
        else:
            h = (x // 18 * 7 + band * 13) % 5
            c = mix(base, hexc("#d0b090"), 0.12 * h / 4)
        px[x, y] = c
# shadow band under the stalls
for y in range(GROUND, GROUND + 8):
    for x in range(W):
        if dith(x, y, 1 - (y - GROUND) / 8):
            px[x, y] = mix(px[x, y], hexc("#8a6a68"), 0.35)

# -------------------------------------------------------- flower carts ---


def flower_cart(x, y, flip=False):
    S = Sprite(96, 64)
    box = rect(6, 26, 78, 22)
    S.blob(box, [hexc("#e8b888"), hexc("#c89060"), hexc("#a07048"), hexc("#805838")], hexc("#503028"),
           cuts=(-0.5, 0.2, 0.7))
    for xx in range(10, 82, 10):
        for yy in range(28, 47):
            S.set(xx, yy, hexc("#a87850"))
    # handle
    for i in range(14):
        S.set(84 + i // 2, 30 - i // 3, hexc("#503028"))
    # wheels
    for wx in (22, 66):
        wm = ellipse(wx, 52, 9, 9)
        S.blob(wm, [hexc("#b08060"), hexc("#906048"), hexc("#704838")], hexc("#402828"), cuts=(-0.2, 0.5))
        inner = ellipse(wx, 52, 5.5, 5.5)
        for p in edge(inner):
            S.set(*p, hexc("#503028"))
        S.set(wx, 52, hexc("#e0b080"))
    # flowers: little pots of blossoms
    cols = [(hexc("#ffc8d8"), hexc("#f08ab0")), (hexc("#fff0a0"), hexc("#f0c040")),
            (hexc("#e0d0ff"), hexc("#a888e0")), (hexc("#ffd0b0"), hexc("#f09060"))]
    for i in range(8):
        fx = 10 + i * 9 + R.randint(-1, 1)
        fy = 14 + R.randint(-3, 3)
        light, base = cols[i % 4]
        for sy in range(fy + 4, 27):
            S.set(fx + 2, sy, hexc("#5a9a44"))
        S.set(fx + 3, fy + 8, hexc("#8ecf5a"))
        S.set(fx + 1, fy + 10, hexc("#8ecf5a"))
        bloom = ellipse(fx + 2, fy + 2, 3.4, 3)
        S.blob(bloom, [light, base], mix(base, hexc("#502838"), 0.5), cuts=(0.1,))
        S.set(fx + 2, fy + 2, hexc("#fff4c0"))
    im = S.image()
    if flip:
        im = im.transpose(0)
    img.alpha_composite(im, (x, y))


flower_cart(196, GROUND - 22)
flower_cart(560, GROUND + 18, flip=True)

# a few crates & baskets on the ground
for (x, y) in ((396, GROUND + 4), (412, GROUND - 4), (22, GROUND + 22)):
    crate = Sprite(20, 16)
    crate.blob(rect(1, 1, 18, 14), [hexc("#e8c090"), hexc("#d0a070"), hexc("#b08050")], hexc("#604030"),
               cuts=(-0.3, 0.4))
    for xx in (6, 12):
        for yy in range(2, 15):
            crate.set(xx, yy, hexc("#b08050"))
    for i in range(4):
        crate.set(3 + i * 4, 1, hexc("#e8534e"))
        crate.set(4 + i * 4, 1, hexc("#e8534e"))
    paste(img, crate, x, y)

# fallen petals
for _ in range(120):
    x, y = R.randint(0, W - 2), R.randint(GROUND + 6, H - 2)
    px[x, y] = R.choice([hexc("#f8c4d4"), hexc("#ffe4ec"), hexc("#e8a4bc")])

# overall softening so cards pop
haze(img, hexc("#fbf1e4"), 0.05)

img = save_bg(img, "blossom_market")
mock(img, "blossom_market", "blossom_market")
