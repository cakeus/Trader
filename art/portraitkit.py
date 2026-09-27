"""Shared bits for the 64x64 actor portraits (built on pixelkit)."""
import math

from pixelkit import Sprite, hexc, ellipse, edge

W = H = 64

EYE_DARK = hexc("#2a1a2e")
GLINT = hexc("#fffaf0")
BLUSH = hexc("#f28a8a")


def new():
    return Sprite(W, H)


def poly(points):
    """Filled polygon mask (pixel centers inside)."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    m = set()
    n = len(points)
    for y in range(int(min(ys)), int(max(ys)) + 1):
        for x in range(int(min(xs)), int(max(xs)) + 1):
            px, py = x + 0.5, y + 0.5
            inside = False
            j = n - 1
            for i in range(n):
                xi, yi = points[i]
                xj, yj = points[j]
                if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi:
                    inside = not inside
                j = i
            if inside:
                m.add((x, y))
    return m


def line(x0, y0, x1, y1, width=1):
    """Pixels along a line (optionally thickened)."""
    m = set()
    steps = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
    for i in range(steps + 1):
        t = i / steps
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t
        if width == 1:
            m.add((round(x), round(y)))
        else:
            m |= ellipse(x, y, width / 2, width / 2)
    return m


def curve(pts, width=1):
    """Polyline through points."""
    m = set()
    for a, b in zip(pts, pts[1:]):
        m |= line(a[0], a[1], b[0], b[1], width)
    return m


def eye(S, x, y, w=3, h=4, dark=EYE_DARK, glint=GLINT):
    """Solid cute eye with a 1px glint in its upper-left."""
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            corner = (yy in (y, y + h - 1)) and (xx in (x, x + w - 1)) and w > 2 and h > 3
            if not corner:
                S.set(xx, yy, dark)
    S.set(x, y + (1 if w > 2 and h > 3 else 0), glint)


def shiny_eye(S, cx, cy, r, ramp, outline, glint=GLINT):
    """Big round glossy eye (moth / alien)."""
    m = ellipse(cx, cy, r, r)
    S.blob(m, ramp, outline, cuts=(-0.3, 0.4))
    S.set(round(cx - r * 0.45), round(cy - r * 0.45), glint)
    S.set(round(cx - r * 0.45) + 1, round(cy - r * 0.45), glint)
    S.set(round(cx - r * 0.45), round(cy - r * 0.45) + 1, glint)


def blush(S, x, y, c=BLUSH):
    S.set(x, y, c)
    S.set(x + 1, y, c)


def spiral(cx, cy, r0, r1, turns, start=0.0):
    m = set()
    steps = int(turns * 120)
    for i in range(steps + 1):
        t = i / steps
        a = start + t * turns * 2 * math.pi
        r = r0 + (r1 - r0) * t
        m.add((round(cx + math.cos(a) * r), round(cy + math.sin(a) * r)))
    return m


def smile(S, x, y, w, c):
    """Small u-shaped mouth, w pixels wide."""
    S.set(x, y, c)
    for i in range(1, w - 1):
        S.set(x + i, y + 1, c)
    S.set(x + w - 1, y, c)


def clip(mask):
    return {(x, y) for (x, y) in mask if 0 <= x < W and 0 <= y < H}


def finish(S, name, bottom_flush=True):
    """Center horizontally; keep busts sitting on the bottom edge (1px margin)."""
    from pixelkit import bbox
    x0, y0, x1, y1 = bbox(S.px.keys())
    dx = (W - (x1 - x0 + 1)) // 2 - x0
    dy = (H - 2 - y1) if bottom_flush else (H - (y1 - y0 + 1)) // 2 - y0
    S.shift(dx, dy)
    S.save(name, "actors", scale=6, show=False)


def eyeball(S, cx, cy, r, outline, pupil=EYE_DARK, white=None, look=(1, 0)):
    """Round eyeball (for stalk eyes) with a pupil and glint."""
    white = white or [hexc("#ffffff"), hexc("#f4eee8"), hexc("#d8ccd0")]
    m = ellipse(cx, cy, r, r)
    S.blob(m, white, outline, cuts=(-0.2, 0.6))
    px, py = round(cx + look[0]), round(cy + look[1])
    for (x, y) in ((px, py), (px, py - 1), (px - 1, py), (px - 1, py - 1)):
        S.set(x, y, pupil)
    S.set(px - 1, py - 1, GLINT)


def fuzz(mask, period=3):
    """Add a bumpy, fluffy fringe around a mask."""
    out = set(mask)
    for (x, y) in edge(mask):
        if (x * 7 + y * 13) % period == 0:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (x + dx, y + dy) not in mask:
                    out.add((x + dx, y + dy))
    return out
