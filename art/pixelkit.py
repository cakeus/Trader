"""Shared helpers for the procedural pixel-art pipeline.

Sprites are built on a `Sprite` canvas that stores RGBA tuples per pixel.
Shapes are described as *masks* (sets of (x, y)); helpers turn a mask into
an outlined, upper-left-lit blob in the reference-sheet style:

  * tinted outline (never black), one per material
  * 3-4 value ramp: light / base / shade / deep
  * small specular glints, 1px details with 1px shadows
  * no anti-aliasing against transparency
"""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.normpath(os.path.join(HERE, "..", "game", "public", "assets"))
PREVIEWS = os.path.join(HERE, "previews")

N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def hexc(s, a=255):
    """'#rrggbb' -> (r, g, b, a)."""
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


def mix(c1, c2, t):
    return tuple(round(a + (b - a) * t) for a, b in zip(c1, c2))


# ---------------------------------------------------------------- masks ---

def ellipse(cx, cy, rx, ry):
    """Pixels whose centers fall inside the ellipse (cx, cy are pixel coords)."""
    m = set()
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                m.add((x, y))
    return m


def rect(x0, y0, w, h):
    return {(x, y) for y in range(y0, y0 + h) for x in range(x0, x0 + w)}


def rounded_rect(x0, y0, w, h, r=1):
    m = rect(x0, y0, w, h)
    for i in range(r):
        for j in range(r - i):
            for (x, y) in ((x0 + j, y0 + i), (x0 + w - 1 - j, y0 + i),
                           (x0 + j, y0 + h - 1 - i), (x0 + w - 1 - j, y0 + h - 1 - i)):
                m.discard((x, y))
    return m


def rows_mask(rows, ox=0, oy=0, chars=None):
    """Mask from text rows; any non-'.' char (or only `chars`) counts."""
    return {(ox + x, oy + y) for y, row in enumerate(rows) for x, c in enumerate(row)
            if c != "." and (chars is None or c in chars)}


def edge(mask):
    """Mask pixels that touch the outside (4-neighbour)."""
    return {(x, y) for (x, y) in mask if any((x + dx, y + dy) not in mask for dx, dy in N4)}


def ring(mask):
    """Pixels just outside the mask (4-neighbour)."""
    out = set()
    for (x, y) in mask:
        for dx, dy in N4:
            q = (x + dx, y + dy)
            if q not in mask:
                out.add(q)
    return out


def bbox(mask):
    xs = [p[0] for p in mask]
    ys = [p[1] for p in mask]
    return min(xs), min(ys), max(xs), max(ys)


# --------------------------------------------------------------- sprite ---

class Sprite:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = {}

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h and c is not None:
            self.px[(x, y)] = c

    def get(self, x, y):
        return self.px.get((x, y))

    def fill(self, mask, c):
        for (x, y) in mask:
            self.set(x, y, c)

    def blob(self, mask, ramp, outline=None, lx=0.75, ly=0.55, cuts=(-0.3, 0.3, 0.65),
             center=None):
        """Outlined, shaded shape. ramp = [light, base, shade, (deep)].

        Interior pixels are shaded by v = nx*lx + ny*ly where nx, ny in [-1, 1]
        relative to the mask's bbox (or `center`), so light comes from the
        upper-left. Edge pixels get `outline` (skip outline with None).
        """
        x0, y0, x1, y1 = bbox(mask)
        cx, cy = center if center else ((x0 + x1) / 2, (y0 + y1) / 2)
        rx, ry = max(1, (x1 - x0) / 2), max(1, (y1 - y0) / 2)
        e = edge(mask) if outline else set()
        for (x, y) in mask:
            if (x, y) in e:
                self.set(x, y, outline)
                continue
            v = (x - cx) / rx * lx + (y - cy) / ry * ly
            i = sum(v >= t for t in cuts)
            self.set(x, y, ramp[min(i, len(ramp) - 1)])

    def outline_around(self, mask, c):
        """Outline drawn *outside* the mask (for overlays like leaves)."""
        for (x, y) in ring(mask):
            self.set(x, y, c)

    def rows(self, rows, pal, ox=0, oy=0):
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch != "." and ch != " ":
                    self.set(ox + x, oy + y, pal[ch])

    def shift(self, dx, dy):
        self.px = {(x + dx, y + dy): c for (x, y), c in self.px.items()
                   if 0 <= x + dx < self.w and 0 <= y + dy < self.h}

    def center(self, margin=1):
        """Center the drawn content inside the canvas."""
        if not self.px:
            return
        x0, y0, x1, y1 = bbox(self.px.keys())
        dx = (self.w - (x1 - x0 + 1)) // 2 - x0
        dy = (self.h - (y1 - y0 + 1)) // 2 - y0
        self.shift(dx, dy)

    def image(self):
        img = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        for (x, y), c in self.px.items():
            img.putpixel((x, y), c)
        return img

    def save(self, name, subdir, scale=10, show=True):
        return save_image(self.image(), name, subdir, scale, show)


def save_image(img, name, subdir, scale=10, show=False):
    """Write assets/<subdir>/<name>.png + previews/<name>_preview.png and verify."""
    out_dir = os.path.join(ASSETS, subdir)
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(PREVIEWS, exist_ok=True)
    path = os.path.join(out_dir, name + ".png")
    img.save(path)
    img.resize((img.width * scale, img.height * scale), Image.NEAREST).save(
        os.path.join(PREVIEWS, name + "_preview.png"))
    chk = Image.open(path)
    corner = chk.getpixel((0, 0))
    print(f"{name}: size={chk.size} mode={chk.mode} bbox={chk.getbbox()} corner={corner}")
    if show and img.width <= 64:
        print(ascii_dump(img))
    return path


def ascii_dump(img):
    """Rough text view: '.' transparent, else a luminance char."""
    ramp = "@%#*+=-:"
    lines = []
    for y in range(img.height):
        row = ""
        for x in range(img.width):
            r, g, b, a = img.getpixel((x, y))
            if a == 0:
                row += "."
            else:
                lum = (r * 299 + g * 587 + b * 114) / 1000
                row += ramp[min(len(ramp) - 1, int(lum / 256 * len(ramp)))]
        lines.append(row)
    return "\n".join(lines)
