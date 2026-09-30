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
    "hammer": (
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


def pickaxe(S):
    """Curved steel head upper-left, handle to the lower-right (as make_pickaxe.py)."""
    wood = [hexc("#f0c488"), hexc("#d0924e"), hexc("#a8683a")]
    steel = [hexc("#e4eef8"), hexc("#a8bcd4"), hexc("#7890b0"), hexc("#566a8c")]
    r2 = 1 / math.sqrt(2)

    def region(test):
        m = set()
        for y in range(16):
            for x in range(16):
                dx, dy = x + 0.5 - 14.5, y + 0.5 - 14.5
                if test(-(dx + dy) * r2, (-dx + dy) * r2):
                    m.add((x, y))
        return m

    L = 9.4
    handle = region(lambda u, v: -0.5 <= u <= 13 and abs(v) <= 1.75)
    wrap = region(lambda u, v: -0.5 <= u <= 4 and abs(v) <= 1.9)
    head = region(lambda u, v: abs(v) <= L and abs(u - (13.4 - 3.8 * (v / L) ** 2))
                  <= 2.0 * (1 - (abs(v) / L) ** 1.6) + 0.6)
    S.blob(handle, wood, hexc("#4a2a1c"), lx=0.6, ly=0.6)
    S.blob(wrap, [hexc("#8ab8c8"), hexc("#5a8aa0"), hexc("#3e6478")], hexc("#4a2a1c"), cuts=(-0.2, 0.5))
    S.blob(head, steel, hexc("#27304a"), lx=0.65, ly=0.65, cuts=(-0.4, 0.15, 0.6))


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


def lucky_cat(S):
    """Gold maneki-neko waving both paws, red collar and bell (as make_lucky_cat.py)."""
    S.rows(["...O......O.....",
            "OO.OOO..OOO.OO..",
            "OYOORLOOORROYO..",
            "OyYOLYYYYYyOyYO.",
            "OYyOWYYYYYYOYyO.",
            ".OOWYFYYYFYyOO..",
            "..OYYYYppYYyO...",
            "..OYYYFYYFYdO...",
            "..ORRRRRRRRrO...",
            "..OYYYOGGOYdO...",
            ".OYYYYOgdOYydO..",
            ".OYYYYYOOYYddO..",
            ".OYYYYYYyyyddO..",
            "..OOOOOOOOOOO..."],
           {"O": hexc("#6e4216"), "W": hexc("#fff2a8"), "Y": hexc("#ffd552"), "y": hexc("#e8a93a"),
            "d": hexc("#b87426"), "L": hexc("#fff2a8"), "R": hexc("#e0503f"), "r": hexc("#a8332f"),
            "F": hexc("#5a3212"), "p": hexc("#ff9a9a"), "G": hexc("#fff2a8"), "g": hexc("#e0a83a")})


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


def paper_lantern(S):
    """Ribbed red chochin with dark rings, a loop and a tassel (as make_paper_lantern.py)."""
    S.rows(["......GG........",
            "....OOOOOO......",
            "....OccCCO......",
            "...OOOOOOOO.....",
            "..OLRRRRRRdO....",
            ".OLMrrrrrrrdO...",
            ".OLRRRRRRRRdO...",
            ".OWMrrrrrrrdO...",
            ".OLRRRRRRRRdO...",
            ".OLMrrrrrrrdO...",
            "..OLRRRRRRdO....",
            "...OOOOOOOO.....",
            "....OccCCO......",
            "....OOOOOO......",
            "......TT........",
            "......Tt........"],
           {"O": hexc("#5e1c24"), "L": hexc("#ffb08a"), "M": hexc("#f27a5c"), "R": hexc("#e0503f"),
            "r": hexc("#b83a34"), "d": hexc("#a8332f"), "W": hexc("#fff4ee"), "c": hexc("#7e78a0"),
            "C": hexc("#4e4870"), "G": hexc("#e0a83a"), "T": hexc("#e0503f"), "t": hexc("#a8332f")})


ORDER = ["strawberry", "seashell", "old_record", "hammer", "hot_cocoa", "crystal", "music_box", "pickaxe",
         "sushi_roll", "lucky_cat", "taiko_drum", "paper_lantern"]
DRAWN = {"old_record": record, "pickaxe": pickaxe, "sushi_roll": sushi_roll, "lucky_cat": lucky_cat,
         "taiko_drum": taiko_drum, "paper_lantern": paper_lantern}
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
