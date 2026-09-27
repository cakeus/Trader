"""Hand-drawn 8x8 good icons for compact UI lists -> assets/goods/<id>_8.png.

Same palettes as the 32x32 icons: tinted outlines, upper-left light.
"""
import os

from PIL import Image

from pixelkit import ASSETS, PREVIEWS, Sprite, hexc

ICONS = {
    "strawberry": (
        ["..oGGo..",
         ".OGHGgO.",
         "OLWRRyRO",
         "OLRyRRdO",
         "ORRRRydO",
         ".OyRRdO.",
         "..ORdO..",
         "...OO..."],
        {"O": hexc("#5c1626"), "R": hexc("#e63a40"), "L": hexc("#f67062"), "d": hexc("#8c1c34"),
         "W": hexc("#ffeee2"), "y": hexc("#ffde78"), "o": hexc("#1e482c"), "G": hexc("#5cbe4c"),
         "g": hexc("#308a3e"), "H": hexc("#9ee26c")},
    ),
    "seashell": (
        ["..OOOO..",
         ".OWLPLO.",
         "OLSLSPSO",
         "OLSPSPdO",
         "OPSPSPdO",
         ".OSPSdO.",
         ".OEOOeO.",
         "..O..O.."],
        {"O": hexc("#7a2e4a"), "W": hexc("#fffaf2"), "L": hexc("#ffe4d6"), "P": hexc("#fbb9a4"),
         "S": hexc("#d9737a"), "d": hexc("#bf5f72"), "E": hexc("#f0a294"), "e": hexc("#b25c70")},
    ),
    "old_record": (
        ["..OOOO..",
         ".OSVVVO.",
         "OSVVVVVO",
         "OVVRrVgO",
         "OVVrrVgO",
         "OVVVVggO",
         ".OVggVO.",
         "..OOOO.."],
        {"O": hexc("#140e20"), "V": hexc("#6a5a8c"), "S": hexc("#c4b8e4"), "g": hexc("#46395f"),
         "R": hexc("#ff9a8a"), "r": hexc("#e8534e")},
    ),
    "tools": (
        ["OOOOOOOO",
         "OWSSSSdO",
         "OOOHhOOO",
         "..OHhO..",
         "..OHhO..",
         "..ORrO..",
         "..ORrO..",
         "..OOOO.."],
        {"O": hexc("#2c3444"), "W": hexc("#eef3f8"), "S": hexc("#bac6d2"), "d": hexc("#7a889a"),
         "H": hexc("#f0c488"), "h": hexc("#a8683a"), "R": hexc("#ff8a7a"), "r": hexc("#c03a44")},
    ),
}

for gid, (rows, pal) in ICONS.items():
    S = Sprite(8, 8)
    S.rows(rows, pal)
    S.save(f"{gid}_8", "goods", scale=16, show=False)

# contact sheet: 1x and 4x on cream and on the dark tooltip color
sheet = Image.new("RGBA", (len(ICONS) * 44 + 8, 64), hexc("#3b2f55"))
for i, gid in enumerate(ICONS):
    im = Image.open(os.path.join(ASSETS, "goods", f"{gid}_8.png"))
    sheet.alpha_composite(im.resize((32, 32), Image.NEAREST), (8 + i * 44, 4))
    sheet.alpha_composite(im, (8 + i * 44, 44))
sheet.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save(
    os.path.join(PREVIEWS, "_icons8_sheet.png"))
