"""Hand-drawn 16x16 good icons for the map tooltip -> assets/goods/<id>_16.png.

Same palettes as the 32x32 and 8x8 icons: tinted outlines, upper-left light.
"""
import os

from PIL import Image

from pixelkit import ASSETS, PREVIEWS, Sprite, edge, ellipse, hexc

ICONS = {
    "strawberry": (
        [".......oo.......",
         "......oGo.......",
         "..oooooHGooooo..",
         ".oHGGGGGGGGGGgo.",
         "OLoGgoGGGgoGgoRO",
         "OLWoRRoggoRRoRdO",
         "OLWRRyRRRRyRRRdO",
         "OLRRRRRRyRRRRydO",
         "OLRyRRRRRRRyRRdO",
         ".ORRRRyRRRRRRdO.",
         ".ORRRRRRRyRRRdO.",
         "..ORyRRRRRRRdO..",
         "..ORRRRRyRRddO..",
         "...ORRRRRRddO...",
         "....ORRRdddO....",
         ".....OOOOOO....."],
        {"O": hexc("#5c1626"), "R": hexc("#e63a40"), "L": hexc("#f67062"), "d": hexc("#8c1c34"),
         "W": hexc("#ffeee2"), "y": hexc("#ffde78"), "o": hexc("#1e482c"), "G": hexc("#5cbe4c"),
         "g": hexc("#308a3e"), "H": hexc("#9ee26c")},
    ),
    "seashell": (
        ["................",
         ".....OOOOOO.....",
         "...OOLWLLPLOO...",
         "..OLWLSLPSPPdO..",
         ".OLWLSLPSPSPSdO.",
         ".OLLSLPSPSPSPdO.",
         "OLLSLPSPSPSPSPdO",
         "OLPSLPSPSPSPSddO",
         "OPPSPPSPSPSPSddO",
         ".OPSPPSPSPSPddO.",
         "..OSPPSPSPSddO..",
         "...OOPSPSPdOO...",
         "....OEEOOeeO....",
         "...OEEEOOeeeO...",
         "...OOOOOOOOOO...",
         "................"],
        {"O": hexc("#7a2e4a"), "W": hexc("#fffaf2"), "L": hexc("#ffe4d6"), "P": hexc("#fbb9a4"),
         "S": hexc("#d9737a"), "d": hexc("#bf5f72"), "E": hexc("#f0a294"), "e": hexc("#b25c70")},
    ),
    "tools": (
        ["..........OO....",
         ".........OWWO...",
         "........OWWSSO..",
         ".......OWWSSSSO.",
         "......OWSSSSSSdO",
         "......OOSSSSSddO",
         ".....OHhOSSSdddO",
         "....OHHhOOSdddO.",
         "...OHHhO..OddO..",
         "..ORRhO....OO...",
         ".ORRrO..........",
         "ORRrO...........",
         "ORrO............",
         ".OO............."],
        {"O": hexc("#2c3444"), "W": hexc("#eef3f8"), "S": hexc("#bac6d2"), "d": hexc("#7a889a"),
         "H": hexc("#f0c488"), "h": hexc("#a8683a"), "R": hexc("#ff8a7a"), "r": hexc("#c03a44")},
    ),
}


def record(S):
    disc = ellipse(7.5, 7.5, 7.4, 7.4)
    S.blob(disc, [hexc("#8a7aac"), hexc("#6a5a8c"), hexc("#46395f"), hexc("#34294a")],
           hexc("#140e20"), cuts=(-0.45, 0.2, 0.7))
    # a groove, lit on the upper-left
    for (x, y) in edge(ellipse(7.5, 7.5, 5.1, 5.1)):
        S.set(x, y, hexc("#c4b8e4") if (x - 7.5) + (y - 7.5) < -4 else hexc("#3a2f52"))
    label = ellipse(7.5, 7.5, 2.6, 2.6)
    S.blob(label, [hexc("#ff9a8a"), hexc("#ff9a8a"), hexc("#e8534e")], None, cuts=(0.3,))
    S.set(7, 7, hexc("#140e20"))
    S.set(6, 6, hexc("#fff0e8"))
    S.set(3, 4, hexc("#fffaf0"))
    S.set(4, 3, hexc("#fffaf0"))


ORDER = ["strawberry", "seashell", "old_record", "tools"]
for gid in ORDER:
    S = Sprite(16, 16)
    if gid == "old_record":
        record(S)
    else:
        rows, pal = ICONS[gid]
        S.rows(rows, pal)
    S.center()
    S.save(f"{gid}_16", "goods", scale=16, show=False)

# contact sheet: 4x and 1x on the dark tooltip colour
sheet = Image.new("RGBA", (len(ORDER) * 72 + 8, 92), hexc("#3b2f55"))
for i, gid in enumerate(ORDER):
    im = Image.open(os.path.join(ASSETS, "goods", f"{gid}_16.png"))
    sheet.alpha_composite(im.resize((64, 64), Image.NEAREST), (8 + i * 72, 4))
    sheet.alpha_composite(im, (8 + i * 72, 72))
sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(
    os.path.join(PREVIEWS, "_icons16_sheet.png"))
