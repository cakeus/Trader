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
    "straw_hat": (
        ["........",
         "..OOOO..",
         ".OWLLsO.",
         ".ORRRrO.",
         "OLLLLLsO",
         "OWLLLssO",
         ".OOOOOO.",
         "........"],
        {"O": hexc("#6b4220"), "W": hexc("#fff0b8"), "L": hexc("#f5d27a"), "s": hexc("#dcaa52"),
         "R": hexc("#e8524a"), "r": hexc("#b0343a")},
    ),
    "hot_cocoa": (
        ["..s.....",
         "...s....",
         "OOOOOO..",
         "OMCMcO..",
         "OLRRdOOO",
         "OWWWwOrO",
         "OLRRdOOO",
         ".OOOO..."],
        {"O": hexc("#5a1626"), "L": hexc("#ff8a7a"), "R": hexc("#e0474c"), "r": hexc("#b83244"),
         "d": hexc("#8c2238"), "W": hexc("#fff6e8"), "w": hexc("#dcc0a8"), "C": hexc("#8a4e32"),
         "c": hexc("#6a3624"), "M": hexc("#fffaf4"), "s": hexc("#d4ccf0")},
    ),
    "crystal": (
        ["...O....",
         "..OWO...",
         "O.OWiO.O",
         "OVOWiOVO",
         "OVOWiOVO",
         "OvOWjOvO",
         "OKKKkkkO",
         ".OOOOOO."],
        {"O": hexc("#3a2c6a"), "W": hexc("#f4fcff"), "i": hexc("#8cc4ee"), "j": hexc("#6a94d8"),
         "V": hexc("#c8b8f4"), "v": hexc("#9a84dc"), "K": hexc("#b8aec8"), "k": hexc("#948aa8")},
    ),
    "music_box": (
        ["OOOOOOO.",
         "OPMMPpO.",
         "OOOOOOO.",
         "ODYYyDOK",
         "OLWDWdOK",
         "OLWWWdO.",
         "OOOOOOO.",
         ".O...O.."],
        {"O": hexc("#48241a"), "L": hexc("#e8a86a"), "W": hexc("#c07a44"), "d": hexc("#98572e"),
         "P": hexc("#c84a6a"), "p": hexc("#962e52"), "M": hexc("#bcdcf0"), "Y": hexc("#ffd24a"),
         "y": hexc("#d89a2a"), "K": hexc("#ffd24a"), "D": hexc("#4a2a22")},
    ),
    "wool_mittens": (
        ["..OOO...",
         ".OLRrOO.",
         ".OLRrOrO",
         ".OLRrOrO",
         ".OLRrrrO",
         ".OWWWwO.",
         ".OCcCcO.",
         ".OOOOOO."],
        {"O": hexc("#5e1c24"), "L": hexc("#ff9a86"), "R": hexc("#e8524a"), "r": hexc("#b8383c"),
         "W": hexc("#fffbea"), "w": hexc("#f2e2c0"), "c": hexc("#f2e2c0"), "C": hexc("#c2a67c")},
    ),
    "sushi_roll": (
        ["..OOOO..",
         ".OWWWWO.",
         "OWWTTCwO",
         "OWPTtCsO",
         "ONOwsOnO",
         "OLNOONnO",
         ".OLNNnO.",
         "..OOOO.."],
        {"O": hexc("#0f1c1c"), "N": hexc("#2f4a40"), "n": hexc("#223830"), "L": hexc("#4c6a58"),
         "W": hexc("#fffdf6"), "w": hexc("#f4eedf"), "s": hexc("#dcd2bf"), "P": hexc("#ff8e8a"),
         "T": hexc("#e8505a"), "t": hexc("#b83246"), "C": hexc("#5cae4c")},
    ),
    "capsule_toy": (
        ["..OOOO..",
         ".OWYYcO.",
         "OCYEYEcO",
         "QQQQQQQQ",
         "QLLRRRrQ",
         "QLRRRrdQ",
         ".QRRrdQ.",
         "..QQQQ.."],
        {"O": hexc("#2e5a6a"), "W": hexc("#ffffff"), "C": hexc("#c8f0ec"), "c": hexc("#9cd8da"),
         "Y": hexc("#f4dc5a"), "E": hexc("#3a2a2a"), "Q": hexc("#5a1c30"), "L": hexc("#ffb0a0"),
         "R": hexc("#f6766e"), "r": hexc("#d2505a"), "d": hexc("#a0384a")},
    ),
    "taiko_drum": (
        ["..h..h..",
         "OOOhhOOO",
         "OWWSSssO",
         "OOOOOOOO",
         "OtRtRtdO",
         "OLRRRRdO",
         "OLRRRRdO",
         ".OOOOOO."],
        {"O": hexc("#3e1a14"), "h": hexc("#d0924e"), "W": hexc("#fff6dc"), "S": hexc("#f6e2b0"),
         "s": hexc("#dcc08a"), "L": hexc("#e89a5a"), "R": hexc("#c0663a"), "d": hexc("#6a2e1e"),
         "t": hexc("#3a2a2a"), "B": hexc("#ffe08a")},
    ),
    "kimono": (
        ["........",
         "OOOOOOOO",
         "OLIcCIiO",
         "OLIICiiO",
         "OOKYYkOO",
         "..OIsO..",
         "..OIsO..",
         "..OOOO.."],
        {"O": hexc("#161a3c"), "L": hexc("#7d8fe0"), "I": hexc("#4c5cb4"), "i": hexc("#36448c"),
         "s": hexc("#222b5e"), "c": hexc("#f0dcbc"), "C": hexc("#fffbea"), "K": hexc("#f2727e"),
         "k": hexc("#c84a5e"), "Y": hexc("#ffe08a")},
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
