"""640x480 storybook town map (top-down, 3/4 props).

Landmarks sit under the map pins (pin tip = locations.json mapPos):
  Blossom Market (150,150), Driftwood Pier (480,300), Lamplight Lane (250,340).
The sea runs down the right side; the bottom-left / bottom-right / top strip
stay calm for the bag strip, prompt panel and HUD.
"""
import math
import os
import random

from PIL import ImageDraw

from bgkit import W, H, new_bg, ramp_fill, dith, orect, oellipse, paste, seg_dist, save_bg, mock
from pixelkit import Sprite, hexc, mix, ellipse, rect, edge, PREVIEWS

R = random.Random(11)
img, d = new_bg("#96c878")
px = img.load()

# ------------------------------------------------------------------ grass ---
GRASS = [hexc("#a9d68a"), hexc("#9acb7c"), hexc("#8cbe70"), hexc("#7fb266")]


def gnoise(x, y):
    return (math.sin(x * 0.031 + y * 0.012) + math.sin(y * 0.043 - x * 0.017 + 1.3)
            + 0.6 * math.sin((x + y) * 0.09)) / 2.6 * 0.5 + 0.5


ramp_fill(img, lambda x, y: True, lambda x, y: 0.15 + gnoise(x, y) * 0.75, GRASS)

# ---------------------------------------------------------------- the sea ---


def coast(y):
    s = min(1, max(0, (y - 110) / 230))
    s = s * s * (3 - 2 * s)
    return 572 - 128 * s + 7 * math.sin(y / 23) + 4 * math.sin(y / 9 + 1)


SEA = [hexc("#a4dfe6"), hexc("#86cddc"), hexc("#6ab8d2"), hexc("#579fc4")]
SAND = [hexc("#f6e4b4"), hexc("#ecd39c")]
for y in range(H):
    cx = coast(y)
    for x in range(W):
        dx = x - cx
        if dx > 0:
            t = min(0.999, dx / 110 + 0.12 * math.sin(x * 0.05 + y * 0.03))
            n = len(SEA) - 1
            f = max(0, t) * n
            i = min(int(f), n - 1)
            px[x, y] = SEA[i + 1] if dith(x, y, f - i) else SEA[i]
            if dx < 3:
                px[x, y] = hexc("#e8f6f0")
        elif dx > -12:
            px[x, y] = SAND[1] if dx > -3 else SAND[0]
            if dx == -12 + 0 or dx <= -11:
                px[x, y] = hexc("#d8c08a")

# little wave marks
for _ in range(70):
    y = R.randint(34, H - 4)
    x = int(coast(y)) + R.randint(14, 180)
    if x < W - 4:
        for dx, dy in ((0, 1), (1, 0), (2, 0), (3, 1)):
            px[x + dx, y + dy] = hexc("#c8eef0")

# ------------------------------------------------------------------ paths ---
PATHS = [
    [(150, 162), (172, 212), (214, 262), (238, 318)],               # market -> lane
    [(300, 330), (350, 318), (405, 306), (452, 300)],               # lane -> pier
    [(186, 146), (262, 160), (350, 196), (418, 250), (448, 294)],  # market -> pier
    [(96, 146), (50, 150), (0, 160)],                               # market -> west edge
    [(150, 108), (156, 60), (170, 30)],                             # market -> north
]
for pts in PATHS:
    d.line(pts, fill=hexc("#c9a870"), width=13, joint="curve")
    for p in pts:
        d.ellipse([p[0] - 6, p[1] - 6, p[0] + 6, p[1] + 6], fill=hexc("#c9a870"))
for pts in PATHS:
    d.line(pts, fill=hexc("#ecd7a4"), width=9, joint="curve")
    for p in pts:
        d.ellipse([p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4], fill=hexc("#ecd7a4"))
# pebbles on paths
for pts in PATHS:
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        for k in range(0, int(math.hypot(bx - ax, by - ay)), 9):
            t = k / math.hypot(bx - ax, by - ay)
            x = int(ax + (bx - ax) * t + R.randint(-2, 2))
            y = int(ay + (by - ay) * t + R.randint(-2, 2))
            px[x, y] = hexc("#d6bc88")


def near_path(x, y, pad):
    return any(seg_dist(x, y, *a, *b) < pad for pts in PATHS for a, b in zip(pts, pts[1:]))


# ------------------------------------------------------------------ props ---


def tree(r=7, kind=0):
    S = Sprite(2 * r + 6, 2 * r + 8)
    cx = r + 2.5
    trunk = rect(int(cx) - 1, 2 * r, 3, 5)
    S.blob(trunk, [hexc("#b07a4a"), hexc("#8a5a38")], hexc("#4a2a1c"), lx=1, ly=0)
    ramps = [
        [hexc("#b6e08a"), hexc("#7cc062"), hexc("#5aa052"), hexc("#3f8048")],
        [hexc("#c8e89a"), hexc("#94cc6c"), hexc("#6aac5a"), hexc("#4a8a4e")],
        [hexc("#ffd0dc"), hexc("#f4a8c0"), hexc("#dc84a4"), hexc("#b86888")],  # blossom
    ]
    outl = [hexc("#2a5a3a"), hexc("#2f5f3a"), hexc("#7a3a5a")][kind]
    can = ellipse(cx, r + 1.5, r, r * 0.92)
    S.blob(can, ramps[kind], outl, cuts=(-0.35, 0.2, 0.6))
    S.set(int(cx) - r // 2, r // 2 + 1, ramps[kind][0])
    S.set(int(cx) - r // 2 + 1, r // 2, hexc("#f4fbe0"))
    return S


def shadow(x, y, w, h=4):
    d.ellipse([x, y, x + w, y + h], fill=hexc("#6c9e5c"))


def house(roof, wall=hexc("#fbeed4"), w=22):
    S = Sprite(w + 2, 24)
    ro = mix(roof, (40, 20, 40, 255), 0.55)
    body = rect(2, 11, w - 3, 11)
    S.blob(body, [wall, mix(wall, (200, 170, 150, 255), 0.25)], hexc("#6a4a4a"), lx=1, ly=0.2, cuts=(0.3,))
    rows = []
    for i in range(10):
        inset = max(0, 4 - i)
        rows.append({(x, i + 1) for x in range(inset, w + 1 - inset)})
    roofm = set().union(*rows)
    S.blob(roofm, [mix(roof, (255, 255, 255, 255), 0.3), roof, mix(roof, (60, 30, 50, 255), 0.25)], ro,
           lx=0.8, ly=0.5, cuts=(-0.3, 0.4))
    door = rect(w // 2 - 1, 16, 4, 6)
    S.fill(door, hexc("#8a5a38"))
    S.fill(edge(door) & rect(w // 2 - 1, 16, 4, 1), hexc("#6a4030"))
    for wx in (5, w - 6):
        S.fill(rect(wx, 14, 3, 3), hexc("#ffe08a"))
        S.set(wx, 14, hexc("#fff6d0"))
    return S


def stall(stripe, w=28):
    S = Sprite(w + 2, 24)
    # counter
    S.blob(rect(2, 13, w - 3, 9), [hexc("#d8a068"), hexc("#b07a4a"), hexc("#8a5a38")], hexc("#4a2a1c"),
           cuts=(-0.2, 0.5))
    # goods on counter
    for i, c in enumerate(("#e8534e", "#ffd24a", "#8ecf5a", "#f4a8c0", "#e8534e", "#ffd24a")):
        x = 4 + i * 4
        if x < w - 3:
            S.set(x, 13, hexc(c))
            S.set(x + 1, 13, hexc(c))
    # posts
    S.fill(rect(3, 8, 1, 6), hexc("#6a4030"))
    S.fill(rect(w - 3, 8, 1, 6), hexc("#6a4030"))
    # striped awning with scalloped edge
    aw = rect(1, 1, w, 7) | {(x, 8) for x in range(1, w + 1) if x % 4 in (1, 2)}
    for (x, y) in aw:
        on = (x // 4) % 2 == 0
        c = stripe if on else hexc("#fff4e4")
        if y <= 2:
            c = mix(c, (255, 255, 255, 255), 0.35)
        elif y >= 6:
            c = mix(c, (80, 40, 60, 255), 0.18)
        S.set(x, y, c)
    for p in edge(aw):
        S.set(*p, mix(stripe, (40, 20, 40, 255), 0.6))
    return S


def lamp():
    S = Sprite(7, 14)
    S.fill(rect(3, 5, 1, 9), hexc("#3b2f55"))
    S.fill(rect(2, 13, 3, 1), hexc("#3b2f55"))
    S.fill(rect(1, 0, 5, 5), hexc("#3b2f55"))
    S.fill(rect(2, 1, 3, 3), hexc("#ffe08a"))
    S.set(2, 1, hexc("#fff8e0"))
    return S


def boat():
    S = Sprite(22, 20)
    hull = {(x, y) for y in range(13, 18) for x in range(2 + (y - 13), 20 - (y - 13))}
    S.blob(hull, [hexc("#f4a070"), hexc("#d8744e"), hexc("#a8543c")], hexc("#5a2a24"), cuts=(-0.2, 0.5))
    S.fill(rect(10, 2, 1, 11), hexc("#6a4030"))
    sail = {(x, y) for y in range(2, 12) for x in range(11, 11 + (y - 1) * 7 // 10 + 1)}
    S.blob(sail, [hexc("#fffaf0"), hexc("#f0e4d0"), hexc("#d8c8b8")], hexc("#6a5a6a"), cuts=(0, 0.5))
    S.fill(rect(11, 7, 5, 1), hexc("#e8534e"))
    return S


# ---- Blossom Market plaza (pin tip 150,150) ----
d.ellipse([88, 96, 212, 166], fill=hexc("#c9a870"))
d.ellipse([90, 98, 210, 164], fill=hexc("#e6d2a8"))
for _ in range(90):  # plaza cobble flecks
    x, y = R.randint(96, 204), R.randint(102, 160)
    if ((x - 150) / 58) ** 2 + ((y - 131) / 31) ** 2 < 1:
        px[x, y] = hexc("#d4bc90")
for (sx, sy, col) in ((100, 104, "#e8534e"), (136, 96, "#5a9ad8"), (172, 104, "#f0a030"),
                      (112, 128, "#8ec060"), (160, 126, "#e878a0")):
    shadow(sx + 2, sy + 21, 28, 3)
    paste(img, stall(hexc(col)), sx, sy)
# a little fountain in the middle
oellipse(d, 142, 124, 158, 133, hexc("#9ad6e2"), hexc("#5a7a9a"))
px[150, 126] = hexc("#e8f6f0")
px[149, 125] = hexc("#e8f6f0")

# ---- Lamplight Lane (pin tip 250,340) ----
lane_y0, lane_y1 = 318, 338
d.rectangle([170, lane_y0 - 1, 336, lane_y1 + 1], fill=hexc("#7a7090"))
for y in range(lane_y0, lane_y1 + 1):
    for x in range(171, 336):
        row = (y - lane_y0) // 3
        off = (row % 2) * 2
        edgep = (y - lane_y0) % 3 == 2 or (x + off) % 4 == 3
        px[x, y] = hexc("#8e86a4") if edgep else (hexc("#c4bccf") if (x * 7 + y * 3) % 5 else hexc("#b2aac2"))
for i, col in enumerate(("#e8534e", "#5a9ad8", "#8e6ac8", "#3f9a8a", "#f0a030", "#e878a0")):
    x = 172 + i * 27
    shadow(x + 1, 312, 24, 3)
    paste(img, house(hexc(col)), x, 292)
for lx in (184, 226, 274, 318):
    for gx in range(-5, 6):
        for gy in range(-4, 5):
            if gx * gx + gy * gy * 1.6 < 22:
                x, y = lx + 3 + gx, lane_y1 + 1 + gy
                if dith(x, y, 0.35):
                    px[x, y] = mix(px[x, y], hexc("#ffe8a0"), 0.5)
    paste(img, lamp(), lx, lane_y1 - 10)

# ---- Driftwood Pier (pin tip 480,300) ----
PL, PR, PT, PB = int(coast(300)) - 10, 604, 294, 305
for x in range(PL + 6, PR, 9):  # posts poking out of the water under the pier
    d.rectangle([x, PB + 1, x + 1, PB + 4], fill=hexc("#5a3624"))
    px[x - 1, PB + 4] = hexc("#c8eef0")
    px[x + 2, PB + 4] = hexc("#c8eef0")
orect(d, PL, PT, PR, PB, hexc("#c08858"), hexc("#5a3624"))
for x in range(PL + 3, PR, 4):
    d.line([x, PT + 1, x, PB - 1], fill=hexc("#9a6840"))
d.line([PL + 1, PT + 1, PR - 1, PT + 1], fill=hexc("#dca878"))
orect(d, PR - 8, PT - 8, PR + 14, PB + 8, hexc("#c08858"), hexc("#5a3624"))
for x in range(PR - 5, PR + 14, 4):
    d.line([x, PT - 7, x, PB + 7], fill=hexc("#9a6840"))
d.line([PR - 7, PT - 7, PR + 13, PT - 7], fill=hexc("#dca878"))
# a crate & a barrel on the platform, and a tiny beach hut
orect(d, PR + 2, PT - 5, PR + 7, PT, hexc("#d8a068"), hexc("#5a3624"))
oellipse(d, PR + 7, PB + 1, PR + 12, PB + 6, hexc("#b07a4a"), hexc("#4a2a1c"))
paste(img, house(hexc("#5ab0c8"), w=18), int(coast(270)) - 32, 262)
shadow(int(coast(270)) - 30, 283, 18, 3)
paste(img, boat(), 560, 356)
paste(img, boat(), 596, 150)

# ---- pond ----
oellipse(d, 44, 262, 104, 296, hexc("#86cddc"), hexc("#4a7a9a"))
d.ellipse([50, 266, 90, 280], fill=hexc("#a4dfe6"))
for (x, y) in ((64, 284), (86, 276), (74, 270)):
    d.ellipse([x, y, x + 5, y + 3], fill=hexc("#7cc062"), outline=hexc("#3f8048"))

# ---- houses scattered around ----
HOUSES = ((34, 100, "#e8534e"), (258, 92, "#8e6ac8"), (300, 250, "#f0a030"), (22, 190, "#5a9ad8"),
          (366, 120, "#e878a0"), (230, 42, "#3f9a8a"), (382, 382, "#e8534e"))
for (x, y, c) in HOUSES:
    shadow(x + 1, y + 20, 22, 3)
    paste(img, house(hexc(c)), x, y)

# ---- trees & flowers (avoid landmarks, paths, sea, calm zones) ----
KEEP_OUT = [(84, 88, 216, 180), (160, 280, 346, 372), (int(coast(300)) - 40, 256, 640, 330),
            (40, 258, 108, 300), (0, 0, W, 34), (0, 414, 330, H)]
placed = []
KEEP_OUT += [(x - 4, y - 6, x + 28, y + 26) for (x, y, _c) in HOUSES]


def free(x, y, w, h, pad=4):
    if any(x < b[2] and x + w > b[0] and y < b[3] and y + h > b[1] for b in KEEP_OUT):
        return False
    if x + w > coast(y + h) - 16 or x + w > coast(y) - 16:
        return False
    if near_path(x + w / 2, y + h - 3, 11) or near_path(x + w / 2, y + h / 2, 10):
        return False
    return all(abs(x - px_) > w + pad or abs(y - py_) > h + pad - 6 for px_, py_ in placed)


for _ in range(3000):
    r = R.choice((6, 7, 8, 9))
    kind = R.choice((0, 0, 1, 1, 2))
    x, y = R.randint(0, W - 20), R.randint(30, H - 20)
    if free(x, y, 2 * r + 6, 2 * r + 8):
        placed.append((x, y))
        shadow(x + 3, y + 2 * r + 5, 2 * r, 3)
        paste(img, tree(r, kind), x, y)
    if len(placed) > 72:
        break

# houses also count as placed so flowers don't sit on them
for _ in range(260):
    x, y = R.randint(4, W - 8), R.randint(36, H - 8)
    if free(x, y, 3, 3, pad=1) and px[x, y][1] > 150:
        c = R.choice(("#ffd24a", "#ff9ab0", "#fffaf0", "#c8a0f0"))
        px[x, y] = hexc(c)
        px[x, y + 1] = hexc("#5aa052")

img = save_bg(img, "map")

# mock with pins/labels for checking
m = img.copy()
md = ImageDraw.Draw(m)
for (x, y, name) in ((150, 150, "Blossom Market"), (480, 300, "Driftwood Pier"), (250, 340, "Lamplight Lane")):
    md.ellipse([x - 5, y - 16, x + 5, y - 6], fill=hexc("#e8534e"), outline=hexc("#5a1a2a"))
    md.rectangle([x - 45, y + 4, x + 45, y + 26], fill=hexc("#fbf1dc"), outline=hexc("#5a3a3e"))
m.save(os.path.join(PREVIEWS, "_mock_map_pins.png"))
mock(img, "map")
