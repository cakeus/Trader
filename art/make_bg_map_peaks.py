"""640x480 storybook map of Frostpine Peaks (top-down, 3/4 props).

Landmarks sit under the map pins (pin tip = locations.json mapPos):
  Frostpine Lodge (170,160), Icicle Station (470,180), Hearthstone Square (300,340).
A mountain range fills the top-right (the station's cable climbs into it) and a
frozen lake sits bottom-right; the top strip and bottom strip stay calm for the
HUD, bag strip and prompt panel.
"""
import math
import os
import random

from PIL import ImageDraw

from bgkit import W, H, new_bg, ramp_fill, dith, orect, oellipse, paste, seg_dist, save_bg, mock
from pixelkit import Sprite, hexc, mix, ellipse, rect, edge, ring, PREVIEWS
from snowkit import SNOW, SNOW_OUT, PINE, PINE_OUT, WARM, WARM_HI, smoke

R = random.Random(13)
img, d = new_bg("#eef2fa")
px = img.load()

# --------------------------------------------------------------- snowfield ---
FIELD = [hexc("#f6f8fe"), hexc("#eef2fa"), hexc("#e4eaf6"), hexc("#d8e0f2")]


def gnoise(x, y):
    return (math.sin(x * 0.029 + y * 0.013) + math.sin(y * 0.041 - x * 0.019 + 1.3)
            + 0.6 * math.sin((x + y) * 0.085)) / 2.6 * 0.5 + 0.5


ramp_fill(img, lambda x, y: True, lambda x, y: 0.1 + gnoise(x, y) * 0.8, FIELD)
# wind ripples: short pale-blue drift strokes
for _ in range(260):
    x, y = R.randint(0, W - 8), R.randint(34, H - 4)
    for k in range(R.randint(3, 7)):
        px[x + k, y + (1 if k in (0, 6) else 0)] = hexc("#d4dcf0")

# ----------------------------------------------------------- mountains ----
ROCK = [hexc("#b8bcdc"), hexc("#9ca2cc"), hexc("#7e86b6"), hexc("#646c9e")]
ROCK_OUT = hexc("#454a7c")


def peak(cx, base, h, bw, seed):
    """3/4 mountain: lit left face, shaded right face, jagged snow cap."""
    rr = random.Random(seed)
    S = Sprite(bw + 4, h + 6)
    ax = bw // 2 + 2 + rr.randint(-3, 3)
    mask = set()
    for y in range(h + 1):
        f = y / h
        l = ax - f * (ax - 2) - 1.5 * math.sin(y * 0.6 + seed)
        r = ax + f * (bw + 1 - ax) + 1.5 * math.sin(y * 0.5 + seed * 2)
        for x in range(int(l), int(r) + 1):
            mask.add((x, y + 2))
    gullies = [ax - bw * 0.22 + rr.randint(-2, 2), ax + bw * 0.12 + rr.randint(-2, 2)]
    for (x, y) in mask:
        ridge_x = ax + (y - 2) * 0.12 + 2 * math.sin(y * 0.3 + seed)
        left = x < ridge_x
        f = (y - 2) / h
        cap = f < 0.42 + 0.08 * math.sin(x * 0.7 + seed) + 0.05 * math.sin(x * 0.23)
        if cap:
            c = SNOW[0] if left else SNOW[2]
        else:
            c = (ROCK[0] if f < 0.6 else ROCK[1]) if left else (ROCK[2] if f < 0.75 else ROCK[3])
            # a couple of snowy gullies running down from the cap
            for gx0 in gullies:
                if abs(x - (gx0 + (y - 2) * 0.25)) < 0.8 and f < 0.8:
                    c = SNOW[1] if left else SNOW[3]
        S.set(x, y, c)
    for (x, y) in edge(mask):
        S.set(x, y, ROCK_OUT if S.get(x, y) in ROCK else SNOW_OUT)
    # snowy skirt at the foot
    for x in range(bw + 4):
        for y in range(h - 2, h + 3):
            if (x, y) in mask and y > h - 1 + math.sin(x * 0.5 + seed):
                S.set(x, y, SNOW[1])
    paste(img, S, cx - bw // 2 - 2, base - h - 2)


PEAKS = [(352, 74, 40, 70), (420, 70, 56, 92), (512, 66, 66, 110), (604, 76, 64, 100), (640, 126, 70, 100),
         (470, 104, 44, 74), (566, 122, 58, 94), (318, 104, 30, 54), (392, 116, 38, 66), (616, 184, 62, 94),
         (630, 250, 50, 78), (270, 76, 26, 46)]
for i, (cx, base, h, bw) in enumerate(sorted(PEAKS, key=lambda p: p[1])):
    peak(cx, base, h, bw, i * 7 + 3)

# a frozen lake bottom-right
LCX, LCY, LRX, LRY = 505, 334, 92, 44


def lake_r(x, y):
    a = math.atan2(y - LCY, x - LCX)
    k = 1 + 0.07 * math.sin(a * 3 + 1) + 0.05 * math.sin(a * 5)
    return math.hypot((x - LCX) / (LRX * k), (y - LCY) / (LRY * k))


ICE = [hexc("#d8eef8"), hexc("#c0e0f2"), hexc("#a8d0ec"), hexc("#94c0e4")]
for y in range(LCY - LRY - 8, LCY + LRY + 8):
    for x in range(LCX - LRX - 10, LCX + LRX + 10):
        r = lake_r(x, y)
        if r < 1:
            t = min(0.999, 0.15 + (y - (LCY - LRY)) / (2 * LRY) * 0.6 + 0.25 * r)
            t *= len(ICE) - 1
            i = int(t)
            px[x, y] = ICE[i + 1] if dith(x, y, t - i) else ICE[i]
            if r > 0.94:
                px[x, y] = hexc("#7aa4d0")
        elif r < 1.08:
            px[x, y] = SNOW[0] if y < LCY else SNOW[1]
# shine streaks and a few cracks
for (sx, sy, ln) in ((452, 314, 22), (470, 324, 12), (520, 306, 16), (540, 346, 10)):
    for k in range(ln):
        px[sx + k, sy - k // 3] = hexc("#f4fcff")
for (sx, sy) in ((500, 340), (560, 330), (450, 350)):
    x, y = sx, sy
    for k in range(14):
        px[x, y] = hexc("#7ea8d4")
        x += R.choice((1, 1, 2))
        y += R.choice((-1, 0, 1))
# skate loops
for k in range(120):
    a = k / 120 * math.tau
    x = int(LCX - 30 + 18 * math.cos(a))
    y = int(LCY + 8 + 8 * math.sin(a * 2))
    px[x, y] = hexc("#eef8ff")

# ------------------------------------------------------------------ paths ---
PATHS = [
    [(176, 170), (204, 222), (246, 272), (284, 312)],               # lodge -> square
    [(330, 324), (372, 286), (412, 240), (452, 196), (462, 182)],   # square -> station
    [(206, 150), (282, 150), (360, 164), (430, 176)],               # lodge -> station
    [(126, 150), (70, 156), (0, 170)],                              # lodge -> west edge
    [(300, 360), (296, 396), (282, 420)],                           # square -> south
    [(260, 330), (180, 340), (100, 370), (40, 400)],                # square -> southwest
]
for pts in PATHS:
    d.line(pts, fill=hexc("#a4acd0"), width=13, joint="curve")
    for p in pts:
        d.ellipse([p[0] - 6, p[1] - 6, p[0] + 6, p[1] + 6], fill=hexc("#a4acd0"))
for pts in PATHS:
    d.line(pts, fill=hexc("#d6d6ea"), width=9, joint="curve")
    for p in pts:
        d.ellipse([p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4], fill=hexc("#d6d6ea"))
# footprints / sled tracks
for pts in PATHS:
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        L = math.hypot(bx - ax, by - ay)
        for k in range(0, int(L), 6):
            t = k / L
            x = int(ax + (bx - ax) * t + (1 if (k // 6) % 2 else -1) * 2)
            y = int(ay + (by - ay) * t)
            px[x, y] = hexc("#b8bcd8")


def near_path(x, y, pad):
    return any(seg_dist(x, y, *a, *b) < pad for pts in PATHS for a, b in zip(pts, pts[1:]))


# ------------------------------------------------------------------ props ---


def map_pine(tiers=3):
    """Little top-down-ish fir: stacked tiers, snow on each tier's top rows."""
    rows = []
    for i in range(tiers):
        w0 = 1 + 2 * i
        for j in range(2 + i):
            rows.append((i, j, w0 + 2 * j))
    wmax = max(r[2] for r in rows)
    S = Sprite(wmax + 4, len(rows) + 6)
    cx = (wmax + 4) // 2
    mask = set()
    for y, (i, j, w) in enumerate(rows):
        for x in range(cx - w // 2, cx + w // 2 + 1):
            rel = (x - cx) / max(1, w / 2)
            if j == 0 or (j == 1 and rel < -0.2 and (x + y) % 2 == 0):
                c = SNOW[0] if rel <= 0.2 else SNOW[2]
            else:
                c = PINE[0] if rel < -0.45 else PINE[1] if rel < 0.25 else PINE[2]
            S.set(x, y + 1, c)
            mask.add((x, y + 1))
    for (x, y) in ring(mask):
        below = S.get(x, y + 1)
        S.set(x, y, SNOW_OUT if below in (SNOW[0], SNOW[2]) and (x, y - 1) not in mask else PINE_OUT)
    ty = len(rows) + 1
    S.fill({(cx, ty + 1), (cx, ty + 2)}, hexc("#74482e"))
    return S


def shadow(x, y, w, h=4):
    d.ellipse([x, y, x + w, y + h], fill=hexc("#c8d0ea"))


def cottage(roof, wall=hexc("#f4e8d8"), w=22):
    S = Sprite(w + 2, 26)
    body = rect(2, 13, w - 3, 11)
    S.blob(body, [wall, mix(wall, (200, 170, 150, 255), 0.25)], hexc("#6a4a5a"), lx=1, ly=0.2, cuts=(0.3,))
    rows = []
    for i in range(11):
        inset = max(0, 4 - i)
        rows.append({(x, i + 2) for x in range(inset, w + 1 - inset)})
    roofm = set().union(*rows)
    ro = mix(roof, (40, 20, 40, 255), 0.55)
    S.blob(roofm, [mix(roof, (255, 255, 255, 255), 0.3), roof, mix(roof, (60, 30, 50, 255), 0.25)], ro,
           lx=0.8, ly=0.5, cuts=(-0.3, 0.4))
    # snow blanket on the roof
    for (x, y) in roofm:
        if y < 8 + (x % 3 == 0) and (x, y) not in edge(roofm):
            S.set(x, y, SNOW[0] if x < w // 2 + 2 else SNOW[2])
    for (x, y) in edge(roofm):
        if y < 7:
            S.set(x, y, SNOW_OUT)
    door = rect(w // 2 - 1, 18, 4, 6)
    S.fill(door, hexc("#8a5a38"))
    for wx in (5, w - 6):
        S.fill(rect(wx, 16, 3, 3), WARM)
        S.set(wx, 16, WARM_HI)
    S.fill(rect(w - 7, 0, 3, 4), hexc("#8a7a9a"))
    S.fill(rect(w - 7, 0, 3, 1), SNOW[0])
    return S


# ---- Frostpine Lodge (pin tip 170,160): a big log lodge in a pine clearing ----
d.ellipse([112, 110, 228, 176], fill=hexc("#dce2f2"))
d.ellipse([114, 112, 226, 174], fill=hexc("#f4f6fc"))
LOG = [hexc("#d69a62"), hexc("#b87a48"), hexc("#94603a")]
lodge = Sprite(64, 50)
wall = rect(6, 24, 52, 22)
lodge.blob(wall, LOG, hexc("#4a2a20"), lx=1, ly=0.2, cuts=(-0.2, 0.5))
for y in range(26, 45, 4):
    for x in range(7, 57):
        lodge.set(x, y, hexc("#94603a"))
for y in range(25, 46, 4):  # log ends
    lodge.set(5, y, hexc("#e8b888"))
    lodge.set(58, y, hexc("#b8844e"))
roofm = set()
for i in range(22):
    inset = max(0, 12 - i)
    roofm |= {(x, i + 3) for x in range(inset + 1, 63 - inset)}
lodge.blob(roofm, [SNOW[0], SNOW[1], SNOW[2]], SNOW_OUT, lx=0.9, ly=0.4, cuts=(-0.1, 0.45))
for x in range(2, 62):
    lodge.set(x, 25, hexc("#6e4228"))
    if x % 4 == 1:
        lodge.set(x, 26, hexc("#dcecfc"))
# gable window + windows + door
lodge.fill(rect(29, 12, 6, 6), hexc("#6e4228"))
lodge.fill(rect(30, 13, 4, 4), WARM)
lodge.set(30, 13, WARM_HI)
for wx in (12, 21, 39, 48):
    lodge.fill(rect(wx, 31, 5, 6), hexc("#5a3424"))
    lodge.fill(rect(wx + 1, 32, 3, 4), WARM)
    lodge.set(wx + 1, 32, WARM_HI)
lodge.fill(rect(29, 34, 6, 12), hexc("#5a3424"))
lodge.fill(rect(30, 35, 4, 11), hexc("#a8543c"))
lodge.fill({(31, 38), (32, 38), (31, 39), (32, 39)}, hexc("#3a7e62"))
# chimney
lodge.fill(rect(46, 2, 6, 12), hexc("#9a96b4"))
lodge.fill(rect(46, 2, 1, 12), hexc("#b4b0cc"))
lodge.fill(rect(45, 0, 8, 3), SNOW[0])
for (x, y) in edge(rect(46, 2, 6, 12)):
    if y > 2:
        lodge.set(x, y, hexc("#4e4a6a") if x in (46, 51) else lodge.get(x, y))
shadow(118, 150, 60, 5)
paste(img, lodge, 138, 106)
smoke(img, R, 187, 106, n=4)
wood = Sprite(14, 10)  # a little firewood stack by the lodge
for (lx, ly) in ((1, 5), (5, 5), (9, 5), (3, 1), (7, 1)):
    wood.blob(ellipse(lx + 1.5, ly + 1.5, 1.8, 1.8), [hexc("#f0c898"), hexc("#d8a470")], hexc("#4a2a20"), cuts=(0.2,))
wood.fill({(x, 0) for x in range(3, 11)}, SNOW[0])
paste(img, wood, 204, 140)

# ---- Icicle Station (pin tip 470,180): station house at the foot of the range, cable up the slope ----
st = Sprite(48, 36)
st.blob(rect(4, 14, 40, 18), [hexc("#e88a7a"), hexc("#d0685c"), hexc("#b0504a")], hexc("#5a2430"),
        lx=1, ly=0.2, cuts=(-0.2, 0.5))
for x in range(6, 43, 4):
    for y in range(15, 31):
        st.set(x, y, hexc("#b0504a"))
sroof = set()
for i in range(12):
    inset = max(0, 6 - i // 2)
    sroof |= {(x, i + 2) for x in range(inset, 48 - inset)}
st.blob(sroof, [SNOW[0], SNOW[1], SNOW[2]], SNOW_OUT, lx=0.9, ly=0.4, cuts=(-0.1, 0.45))
for x in range(1, 47):
    st.set(x, 14, hexc("#fbf1e4"))
    if x % 3 == 0:
        st.set(x, 15, hexc("#dcecfc"))
        if x % 6 == 0:
            st.set(x, 16, hexc("#a8c8ec"))
st.fill(rect(30, 18, 12, 12), hexc("#4a3a58"))    # bay with the bullwheel
for (x, y) in edge(ellipse(35.5, 23.5, 5, 5)):
    st.set(x, y, hexc("#9aa0c4"))
st.set(35, 23, hexc("#d8dcf0"))
for wx in (8, 17):
    st.fill(rect(wx, 19, 6, 5), hexc("#5a2430"))
    st.fill(rect(wx + 1, 20, 4, 3), WARM)
    st.set(wx + 1, 20, WARM_HI)
st.fill(rect(9, 25, 5, 6), hexc("#8a4a3a"))
shadow(446, 170, 50, 4)
paste(img, st, 444, 142)
d.rectangle([438, 173, 502, 178], fill=hexc("#b07a4c"), outline=hexc("#4a2a20"))  # platform
d.line([439, 173, 501, 173], fill=SNOW[0])
# the cable climbing to the top station on the peak, with a tiny gondola
CA, CB = (482, 160), (590, 44)
for off in (0, 4):
    d.line([CA[0], CA[1] + off, CB[0], CB[1] + off], fill=hexc("#4e4a70"))
for (tx, ty) in ((520, 119), (556, 80)):  # pylons
    d.line([tx, ty, tx, ty + 18], fill=hexc("#6a7098"), width=2)
    d.line([tx - 4, ty, tx + 4, ty], fill=hexc("#4e4a70"))
gx, gy = 540, 102
d.line([gx, gy - 4, gx, gy], fill=hexc("#4e4a70"))
orect(d, gx - 5, gy, gx + 5, gy + 7, hexc("#e8584e"), hexc("#5a1a2a"))
d.rectangle([gx - 3, gy + 2, gx + 3, gy + 3], fill=hexc("#bcd8f0"))
d.line([gx - 5, gy - 1, gx + 5, gy - 1], fill=SNOW[0])
orect(d, CB[0] - 6, CB[1] - 4, CB[0] + 8, CB[1] + 6, hexc("#d0685c"), hexc("#5a2430"))
d.rectangle([CB[0] - 7, CB[1] - 7, CB[0] + 9, CB[1] - 4], fill=SNOW[0], outline=SNOW_OUT)

# ---- Hearthstone Square (pin tip 300,340): snowy cobbled plaza, stalls, a fir and the hearth ----
d.ellipse([236, 284, 364, 356], fill=hexc("#a8a8c8"))
d.ellipse([238, 286, 362, 354], fill=hexc("#dcdcec"))
for _ in range(260):  # cobbles peeking through the snow
    x, y = R.randint(242, 358), R.randint(290, 350)
    if ((x - 300) / 60) ** 2 + ((y - 320) / 32) ** 2 < 1 and R.random() < 0.7:
        px[x, y] = R.choice((hexc("#b4b4d0"), hexc("#c4c4dc"), hexc("#f4f6fc")))


def stall(stripe, w=26):
    S = Sprite(w + 2, 24)
    S.blob(rect(2, 13, w - 3, 9), [hexc("#d8a068"), hexc("#b07a4a"), hexc("#8a5a38")], hexc("#4a2a1c"),
           cuts=(-0.2, 0.5))
    for i, c in enumerate(("#e0474c", "#8cc4ee", "#ffd24a", "#c07a44", "#e0474c", "#8cc4ee")):
        x = 4 + i * 4
        if x < w - 3:
            S.set(x, 13, hexc(c))
            S.set(x + 1, 13, hexc(c))
    S.fill(rect(3, 8, 1, 6), hexc("#6a4030"))
    S.fill(rect(w - 3, 8, 1, 6), hexc("#6a4030"))
    aw = rect(1, 1, w, 7) | {(x, 8) for x in range(1, w + 1) if x % 4 in (1, 2)}
    for (x, y) in aw:
        on = (x // 4) % 2 == 0
        c = stripe if on else hexc("#fff4e4")
        if y >= 6:
            c = mix(c, (80, 40, 60, 255), 0.18)
        S.set(x, y, c)
    for p in edge(aw):
        S.set(*p, mix(stripe, (40, 20, 40, 255), 0.6))
    for x in range(1, w + 1):  # snow dusting
        S.set(x, 1, SNOW[0])
        if x % 3:
            S.set(x, 2, SNOW[0] if x < w * 0.6 else SNOW[2])
        S.set(x, 0, SNOW_OUT)
    return S


for (sx, sy, col) in ((244, 292, "#e0584e"), (284, 282, "#4e8ab8"), (324, 292, "#3f9a7a"),
                      (252, 318, "#9a6ac8"), (320, 318, "#e0a040")):
    shadow(sx + 2, sy + 21, 26, 3)
    paste(img, stall(hexc(col)), sx, sy)
# the hearth, a glowing ring of stones by the pin
for gy in range(-6, 7):
    for gx in range(-10, 11):
        if gx * gx / 100 + gy * gy / 36 < 1 and dith(300 + gx, 330 + gy, 0.45):
            px[300 + gx, 330 + gy] = mix(px[300 + gx, 330 + gy], hexc("#ffd890"), 0.6)
oellipse(d, 294, 326, 306, 333, hexc("#f08a3a"), hexc("#6a6682"))
px[299, 328] = hexc("#ffe890")
px[300, 327] = hexc("#ffe890")

# ---- cottages scattered around ----
COTTAGES = ((40, 94, "#e0584e"), (250, 70, "#8e6ac8"), (80, 220, "#4e8ab8"), (380, 262, "#e0a040"),
            (150, 390, "#3f9a7a"), (400, 360, "#e878a0"), (18, 290, "#9a6ac8"))
for (x, y, c) in COTTAGES:
    shadow(x + 1, y + 22, 22, 3)
    paste(img, cottage(hexc(c)), x, y)

# ---- pines (avoid landmarks, paths, mountains, lake, calm zones) ----
KEEP_OUT = [(108, 96, 232, 180), (228, 270, 372, 372), (430, 136, 508, 184), (0, 0, W, 34), (0, 414, W, H),
            (LCX - LRX - 12, LCY - LRY - 12, LCX + LRX + 12, LCY + LRY + 12)]
KEEP_OUT += [(x - 4, y - 6, x + 28, y + 28) for (x, y, _c) in COTTAGES]


def under_mountain(x, y):
    return any(abs(x - cx) < bw * 0.55 and base - h - 4 < y < base + 8 for (cx, base, h, bw) in PEAKS)


placed = []


def free(x, y, w, h, pad=3):
    if any(x < b[2] and x + w > b[0] and y < b[3] and y + h > b[1] for b in KEEP_OUT):
        return False
    if under_mountain(x + w / 2, y + h) or under_mountain(x + w / 2, y):
        return False
    if near_path(x + w / 2, y + h - 3, 10) or near_path(x + w / 2, y + h / 2, 9):
        return False
    return all(abs(x - px_) > w + pad - 4 or abs(y - py_) > h + pad - 8 for px_, py_ in placed)


# clusters: pick a few centres and scatter around them, plus loose singles
CENTRES = [(60, 60), (220, 210), (110, 290), (330, 200), (40, 360), (200, 60), (380, 400), (600, 300),
           (240, 400), (400, 190)]
for _ in range(4000):
    cx_, cy_ = R.choice(CENTRES)
    tiers = R.choice((3, 3, 4, 4, 5))
    S = map_pine(tiers)
    x = int(cx_ + R.gauss(0, 34))
    y = int(cy_ + R.gauss(0, 26))
    if R.random() < 0.25:
        x, y = R.randint(0, W - 14), R.randint(34, H - 30)
    if 0 <= x < W - S.w and free(x, y, S.w, S.h):
        placed.append((x, y))
        shadow(x + 1, y + S.h - 5, S.w - 2, 3)
        paste(img, S, x, y)
    if len(placed) > 130:
        break

# nudge the pale snow toward a cooler, dimmer blue so the game's falling snow reads on top
DUSK = hexc("#8e9ac8")
for y in range(H):
    for x in range(W):
        r, g, b, a = px[x, y]
        if min(r, g, b) > 180 and max(r, g, b) - min(r, g, b) < 40:
            t = 0.34 * (min(r, g, b) - 180) / 75
            px[x, y] = (round(r + (DUSK[0] - r) * t), round(g + (DUSK[1] - g) * t), round(b + (DUSK[2] - b) * t), a)

# sparkles in the snow
for _ in range(220):
    x, y = R.randint(4, W - 8), R.randint(36, H - 8)
    if free(x, y, 2, 2, pad=1) and px[x, y][2] > 230 and not near_path(x, y, 7):
        px[x, y] = hexc("#ffffff")
        px[x + 1, y] = hexc("#dce6f8")

img = save_bg(img, "map_peaks")

# mock with pins/labels for checking
m = img.copy()
md = ImageDraw.Draw(m)
for (x, y, name) in ((170, 160, "Frostpine Lodge"), (470, 180, "Icicle Station"), (300, 340, "Hearthstone Square")):
    md.ellipse([x - 5, y - 16, x + 5, y - 6], fill=hexc("#e8534e"), outline=hexc("#5a1a2a"))
    md.rectangle([x - 45, y + 4, x + 45, y + 26], fill=hexc("#fbf1dc"), outline=hexc("#5a3a3e"))
m.save(os.path.join(PREVIEWS, "_mock_map_peaks_pins.png"))
mock(img, "map_peaks")
