"""Hand-drawn 16x16 good icons for the map tooltip -> assets/goods/<id>_16.png.

Same palettes as the 32x32 and 8x8 icons: tinted outlines, upper-left light.
"""
import math
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
    "straw_hat": (
        ["................",
         ".....OOOOOO.....",
         "....OWLLLLsO....",
         "...OLLLLLLssO...",
         "...OLLLLLssbO...",
         ".OOORRRRRRrbbOO.",
         "OLLORRRRRRrrbsLO",
         "OLLLOOOOOOOObssO",
         "OWLLLLLLLLLLsssO",
         ".OLLLLLLLLLsssO.",
         "..OOsLLLLLsssOO.",
         "....OOOOOOOO...."],
        {"O": hexc("#6b4220"), "W": hexc("#fff0b8"), "L": hexc("#f5d27a"), "s": hexc("#dcaa52"),
         "R": hexc("#e8524a"), "r": hexc("#b0343a"), "b": hexc("#8a2630")},
    ),
    "kimono": (
        ["....OOOOOOOO....",
         "OOOOOcIIIICOOOOO",
         "OLIIOLcIICiOIpiO",
         "OLpIOLIcCiiOIIiO",
         "OIIIOLICiiiOpIiO",
         "OLIIOLCIiiiOIIiO",
         "OIIpOKKKKKkOIiiO",
         "OIIIOYYYYYYOIiiO",
         "OiiiOKKKKkkOiiiO",
         ".OOOOLsIIiiOOOO.",
         "....OLsIpIiO....",
         "....OIsIIiiO....",
         "....OLsIIpiO....",
         "....OIsIIiiO....",
         "....OOOOOOOO...."],
        {"O": hexc("#161a3c"), "L": hexc("#7d8fe0"), "I": hexc("#4c5cb4"), "i": hexc("#36448c"),
         "s": hexc("#222b5e"), "p": hexc("#ffb6c8"), "c": hexc("#f0dcbc"), "C": hexc("#fffbea"),
         "K": hexc("#f2727e"), "k": hexc("#c84a5e"), "Y": hexc("#ffe08a")},
    ),
    "hot_cocoa": (
        [".......Ss.......",
         "......Ss........",
         "......S.........",
         ".......Ss.......",
         "..OOOOOOOOOOO...",
         ".OLMMcCCMMcrO...",
         ".OLmmCCCmmrrOOO.",
         ".OLRRRRRRRRrdOrO",
         ".OWWWWWWWWwwdO.O",
         ".OWWRWWRWWRwdO.O",
         ".OWWWWWWWWwwdOrO",
         ".OLRRRRRRRRrdOO.",
         ".OLRRRRRRRrrdO..",
         "..OLRRRRRrrdO...",
         "...OOOOOOOOO....",
         "................"],
        {"O": hexc("#5a1626"), "L": hexc("#ff8a7a"), "R": hexc("#e0474c"), "r": hexc("#b83244"),
         "d": hexc("#8c2238"), "W": hexc("#fff6e8"), "w": hexc("#dcc0a8"), "C": hexc("#8a4e32"),
         "c": hexc("#6a3624"), "M": hexc("#fffaf4"), "m": hexc("#e8c0cc"), "S": hexc("#d4ccf0"),
         "s": hexc("#a49ccc")},
    ),
    "crystal": (
        ["......O.........",
         ".....OWO......y.",
         ".....OWIO.......",
         "....OWIiO....O..",
         "....OWIijO..OVO.",
         ".O..OWIijO.OVvO.",
         "OVO.OWIijOOVvuO.",
         "OVvOOWIijOOVvuO.",
         ".OVvOWIijOOVvuO.",
         ".OVvOWIijOOVvO..",
         "..OVOWIijOOVvO..",
         "..OVOWIijOOVvO..",
         ".QKKOWIijOKKkQ..",
         "QKKKkkkkkkkkkkQ.",
         ".QQQQQQQQQQQQQ..",
         "................"],
        {"O": hexc("#3a2c6a"), "W": hexc("#f4fcff"), "I": hexc("#c4e8fa"), "i": hexc("#8cc4ee"),
         "j": hexc("#6a94d8"), "V": hexc("#c8b8f4"), "v": hexc("#9a84dc"), "u": hexc("#7462bc"),
         "K": hexc("#b8aec8"), "k": hexc("#948aa8"), "Q": hexc("#3e3654"), "y": hexc("#fff8d0")},
    ),
    "music_box": (
        [".............NN.",
         ".OOOOOOOOOOO.N..",
         ".OLPPMMMPPdONN..",
         ".OLPMmMMMpdONN..",
         ".OLPPMMMPpdO....",
         ".OOOOOOOOOOO....",
         "OOOOOOOOOOOOOOO.",
         "OkYYYYYYssskOGO.",
         "OddddddddddgOgO.",
         "OLWWWGGWWWWdKKO.",
         "OLWWWGkWWWWdOGO.",
         "OLWWWWWWWWWdOgO.",
         "OLWWWWWWWWWdOOO.",
         "OLddddddddddO...",
         "OOOOOOOOOOOOO...",
         ".OO.......OO...."],
        {"O": hexc("#48241a"), "L": hexc("#e8a86a"), "W": hexc("#c07a44"), "d": hexc("#98572e"),
         "P": hexc("#c84a6a"), "p": hexc("#962e52"), "M": hexc("#bcdcf0"), "m": hexc("#ffffff"),
         "k": hexc("#4a2a22"), "Y": hexc("#ffd24a"), "s": hexc("#c8d0dc"), "G": hexc("#ffd24a"),
         "g": hexc("#d89a2a"), "K": hexc("#d89a2a"), "N": hexc("#7462bc")},
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


def wool_mittens(S):
    """A red pair with cream cuffs and stripes, joined by a string (as make_wool_mittens.py)."""
    front = [".OOOO...",
             "OLRRrO..",
             "OLRRrOO.",
             "OLRRrOrO",
             "OLRRrrrO",
             "OWWWWwO.",
             "OLRRrrO.",
             "OccccO..",
             "OCcCcO..",
             "OOOOOO.."]
    pal = {"O": hexc("#5e1c24"), "L": hexc("#ff9a86"), "R": hexc("#e8524a"), "r": hexc("#b8383c"),
           "W": hexc("#fffbea"), "w": hexc("#f2e2c0"), "c": hexc("#f2e2c0"), "C": hexc("#c2a67c")}
    back = dict(pal, L=hexc("#e8786a"), R=hexc("#c8443e"), r=hexc("#9c3036"))
    # the back mitten, mirrored and higher, then the front one over it
    # (mirroring moves the lit side to the right, so swap light and shade back)
    S.rows([row[::-1].replace("L", "_").replace("r", "L").replace("_", "r") for row in front],
           back, 8, 0)
    S.rows(front, pal, 0, 4)
    S.rows(["....y",
            "...y.",
            "..y..",
            "yy..."], {"y": hexc("#f2e2c0")}, 7, 10)


def sushi_roll(S):
    """A maki slice: nori wrap, white rice, tuna and cucumber center (as make_sushi_roll.py)."""
    S.rows(["....OOOOOOOO....",
            "..OONNNNNNNNOO..",
            ".ONNWWWWWWWwNNO.",
            "ONWWWooooCCwwwNO",
            "ONWWoPTTToCcwsNO",
            "ONWwoTTTtoCCwsNO",
            "ONNwwoooowwssNNO",
            "OLOONNNNNNNNOOnO",
            "OLLNOOOOOOOONnnO",
            "OLLNNNNNNNNNnnnO",
            "OLLNNnNNNNNnnnnO",
            ".OLNNNNNNNnnnnO.",
            "..OONNNNNNnnOO..",
            "....OOOOOOOO...."],
           {"O": hexc("#0f1c1c"), "N": hexc("#2f4a40"), "n": hexc("#223830"), "L": hexc("#4c6a58"),
            "W": hexc("#fffdf6"), "w": hexc("#f4eedf"), "s": hexc("#dcd2bf"), "o": hexc("#7a1e34"),
            "P": hexc("#ff8e8a"), "T": hexc("#e8505a"), "t": hexc("#b83246"), "C": hexc("#5cae4c"),
            "c": hexc("#a8e07a")})


def capsule_toy(S):
    """Gachapon capsule, clear aqua top with a chick inside, coral bottom (as make_capsule_toy.py)."""
    S.rows(["....OOOOOOO....",
            "..OOCWWCCCCOO..",
            ".OCWCCCCCCCCcO.",
            ".OWCCCCkCCCCcO.",
            "OWCCkYYYYYkCccO",
            "OCCCkYEYEYkcccO",
            "OCCCkPYbYPkcccO",
            "QQQQQQQQQQQQQQQ",
            "QLGLLLLRRRRRRrQ",
            ".QLRRRRRRRrrdQ.",
            ".QRRRRRRRrrrdQ.",
            "..QRRRRrrrrdQ..",
            "...QQrrrrdQQ...",
            ".....QQQQQ....."],
           {"O": hexc("#2e5a6a"), "C": hexc("#c8f0ec"), "c": hexc("#9cd8da"), "W": hexc("#ffffff"),
            "k": hexc("#7e6a3a"), "Y": hexc("#f4dc5a"), "E": hexc("#3a2a2a"), "b": hexc("#e88a4a"),
            "P": hexc("#f0a49a"), "Q": hexc("#5a1c30"), "L": hexc("#ffb0a0"), "R": hexc("#f6766e"),
            "r": hexc("#d2505a"), "d": hexc("#a0384a"), "G": hexc("#ffffff")})


def taiko_drum(S):
    """Barrel drum with a skin head, tacks, a brass ring and crossed sticks (as make_taiko_drum.py)."""
    S.rows(["..OO......OO....",
            "..OhO....OhO....",
            "...OhO..OhO.....",
            "..OOOhOOhOOOO...",
            ".OWWWShhSSSssO..",
            ".OKSSSSSSSssKO..",
            ".OOOOOOOOOOOOO..",
            "OLWtRtRtRtRtrdO.",
            "OLWRRRRRRRRRrdO.",
            "OLWRRRRBbRRRrdO.",
            "OLWRRRRbBbRRrdO.",
            "OLWRRRRRRRRRrdO.",
            "OLWtRtRtRtRtrdO.",
            ".OLRRRRRRRRrdO..",
            "..OOOOOOOOOOO..."],
           {"O": hexc("#3e1a14"), "h": hexc("#d0924e"), "W": hexc("#fff6dc"), "S": hexc("#f6e2b0"),
            "s": hexc("#dcc08a"), "K": hexc("#94462a"), "L": hexc("#e89a5a"), "R": hexc("#c0663a"),
            "r": hexc("#94462a"), "d": hexc("#6a2e1e"), "t": hexc("#3a2a2a"), "B": hexc("#ffe08a"),
            "b": hexc("#a8702a")})


ORDER = ["strawberry", "seashell", "old_record", "straw_hat", "hot_cocoa", "crystal", "music_box",
         "wool_mittens", "sushi_roll", "capsule_toy", "taiko_drum", "kimono"]
DRAWN = {"old_record": record, "wool_mittens": wool_mittens, "sushi_roll": sushi_roll,
         "capsule_toy": capsule_toy, "taiko_drum": taiko_drum}
for gid in ORDER:
    S = Sprite(16, 16)
    if gid in DRAWN:
        DRAWN[gid](S)
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
