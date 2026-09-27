"""Postage-stamp backgrounds for Nox's Stamps -> assets/ui/stamp.png, stamp_rare.png.

42x42: perforated paper edge with a tinted outline, and an inner frame around a
32x32 window where the game draws the stamp's icon (at a 5px inset).
"""
import os

from PIL import Image

from pixelkit import ASSETS, PREVIEWS, Sprite, edge, hexc, rect

SIZE = 42
INSET = 5


def perforated():
    """Paper mask: a square with rounded notches (the perforations) cut into every side:
    4px wide at the edge, 2px one row in, every 6px."""
    m = rect(0, 0, SIZE, SIZE)
    far = SIZE - 1
    for a in range(4, SIZE - 7, 6):
        for d, xs in ((0, range(a, a + 4)), (1, range(a + 1, a + 3))):
            for j in xs:
                for p in ((j, d), (j, far - d), (d, j), (far - d, j)):
                    m.discard(p)
    return m


def stamp(name, outline, paper, paper_hi, paper_lo, frame, frame_hi, window):
    S = Sprite(SIZE, SIZE)
    m = perforated()
    # paper: light upper-left, shade lower-right
    for (x, y) in m:
        v = (x + y) / (2 * (SIZE - 1))
        S.set(x, y, paper_hi if v < 0.3 else paper if v < 0.75 else paper_lo)
    S.fill(edge(m), outline)
    # inner frame (1px, lit on the top/left) around the 32x32 icon window, rounded corners
    lo, hi = INSET - 1, INSET + 32
    S.fill(edge(rect(lo, lo, 34, 34)), frame)
    for i in range(lo + 1, hi):
        S.set(i, lo, frame_hi)
        S.set(lo, i, frame_hi)
    for (x, y) in ((lo, lo), (hi, lo), (lo, hi), (hi, hi)):
        S.set(x, y, paper)
    S.fill(rect(INSET, INSET, 32, 32), window)
    S.save(name, "ui", scale=10, show=False)


stamp("stamp", hexc("#8a5a4a"), hexc("#fbf1dc"), hexc("#fffaf0"), hexc("#ead8bc"),
      hexc("#c86a5a"), hexc("#e8a090"), hexc("#fff6e8"))
stamp("stamp_rare", hexc("#4a2a6a"), hexc("#f4eafc"), hexc("#fffaff"), hexc("#dccaec"),
      hexc("#8a4ab8"), hexc("#c49ae4"), hexc("#fbf4ff"))

# contact sheet on the dialog row colour and on the dark tooltip colour
sheet = Image.new("RGBA", (2 * 48 + 8, 2 * 52), hexc("#f3e2c4"))
for y, bg in enumerate((hexc("#f3e2c4"), hexc("#3b2f55"))):
    sheet.paste(Image.new("RGBA", (sheet.width, 52), bg), (0, y * 52))
    for i, n in enumerate(("stamp", "stamp_rare")):
        im = Image.open(os.path.join(ASSETS, "ui", n + ".png"))
        sheet.alpha_composite(im, (8 + i * 48, 5 + y * 52))
sheet.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save(
    os.path.join(PREVIEWS, "_stamp_sheet.png"))
