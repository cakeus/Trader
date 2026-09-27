"""Contact sheet of all actor portraits on cream cards (previews/_actors_sheet.png).

Includes every actor in actors.json plus any other portrait PNGs in assets/actors,
laid out in rows of 8.
"""
import glob
import json
import os

from PIL import Image, ImageDraw

from pixelkit import ASSETS, PREVIEWS

ids = [a["id"] for a in json.load(open(os.path.join(ASSETS, "..", "data", "actors.json")))]
for path in sorted(glob.glob(os.path.join(ASSETS, "actors", "*.png"))):
    n = os.path.splitext(os.path.basename(path))[0]
    if n not in ids:
        ids.append(n)

SC = 3
cell = 72
per_row = 8
rows = (len(ids) + per_row - 1) // per_row
sheet = Image.new("RGBA", (cell * per_row + 8, cell * rows + 8), (90, 120, 110, 255))
d = ImageDraw.Draw(sheet)
for i, n in enumerate(ids):
    x = 4 + (i % per_row) * cell
    y = 4 + (i // per_row) * cell
    d.rectangle((x, y, x + cell - 5, y + cell - 1), fill=(251, 241, 220, 255), outline=(90, 58, 62, 255))
    im = Image.open(os.path.join(ASSETS, "actors", n + ".png"))
    sheet.alpha_composite(im, (x + 2, y + 2))
sheet.resize((sheet.width * SC, sheet.height * SC), Image.NEAREST).save(os.path.join(PREVIEWS, "_actors_sheet.png"))
print("sheet:", ids)
