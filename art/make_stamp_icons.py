"""16x16 icons for the Rare stamps -> assets/ui/icon_<name>.png.

Same style as make_ui.py's icons: tinted outlines, light from the upper-left, a cream glint.
"""
import os

from PIL import Image

from pixelkit import ASSETS, PREVIEWS, Sprite, edge, ellipse, hexc, rect, rounded_rect, rows_mask

GOLD = [hexc("#fff0a0"), hexc("#ffd24a"), hexc("#e8a22c"), hexc("#c07a1c")]
GOLD_O = hexc("#7a4a14")
GLINT = hexc("#fffaf0")
WOOD = [hexc("#d8a070"), hexc("#b07848"), hexc("#8a5a34")]
WOOD_O = hexc("#4a2a1c")


def icon(name, draw):
    S = Sprite(16, 16)
    draw(S)
    S.center()
    S.save("icon_" + name, "ui", scale=12, show=False)


def shape(S, rows, ramp, outline, ox=0, oy=0, cuts=(-0.3, 0.3, 0.65)):
    m = rows_mask(rows, ox, oy)
    S.blob(m, ramp, outline, cuts=cuts)
    return m


def eye(S):
    """Bird's Eye: a wide-open eye."""
    white = rows_mask(["....######....",
                       "..##########..",
                       ".############.",
                       "##############",
                       ".############.",
                       "..##########..",
                       "....######...."], 1, 4)
    S.fill(white, hexc("#fffaf0"))
    S.fill({(x, y) for (x, y) in white if x + y > 17}, hexc("#dcd4e8"))
    iris = ellipse(8, 7, 2.9, 2.9)
    S.blob(iris, [hexc("#8ad0f8"), hexc("#4a9ae0"), hexc("#2a6ab0")], None, cuts=(-0.3, 0.4))
    S.fill(ellipse(8.3, 7.3, 1.2, 1.2), hexc("#1e2a4a"))
    S.set(7, 5, hexc("#ffffff"))
    S.fill(edge(white), hexc("#3b3a5a"))
    for (x, y) in ((3, 2), (6, 1), (10, 1), (13, 2)):  # lashes
        S.set(x, y, hexc("#3b3a5a"))


def haggle(S):
    """Haggler: a speech bubble with a $ in it."""
    bubble = rounded_rect(1, 1, 14, 11, 2) | {(4, 12), (5, 12), (4, 13)}
    S.fill(bubble, hexc("#fffaf0"))
    S.fill({(x, y) for (x, y) in bubble if x >= 12 or y >= 10}, hexc("#e8dcc8"))
    S.fill(edge(bubble), hexc("#5a3a3e"))
    S.rows(["..#..",
            ".####",
            "#.#..",
            ".###.",
            "..#.#",
            "####.",
            "..#.."], {"#": hexc("#3a9a4a")}, 6, 3)


def fannypack(S):
    """Fanny Pack: a zipped pouch on a strap."""
    for (x, y) in ((0, 3), (1, 3), (1, 4), (2, 4), (2, 5), (15, 3), (14, 3), (14, 4), (13, 4), (13, 5)):
        S.set(x, y, hexc("#5a3a2a"))
    pouch = rounded_rect(2, 5, 12, 9, 3)
    S.blob(pouch, [hexc("#9ae0d0"), hexc("#4ab8a8"), hexc("#2a8a88"), hexc("#1e6a70")], hexc("#1e3a4a"))
    for x in range(4, 12):
        S.set(x, 8, hexc("#ffd24a"))
    S.set(12, 8, hexc("#e8a22c"))
    S.set(12, 9, hexc("#e8a22c"))
    S.set(4, 6, GLINT)
    S.set(5, 6, GLINT)


def crowd(S):
    """Packed House: three little traders squeezed together."""
    # the one at the back first
    for cx, hy, body, skin in ((8, 3, "#6cc06a", "#f8d0b0"), (3.5, 6, "#e8534e", "#f8c8a0"),
                               (12.5, 6, "#4a9ae0", "#e8b088")):
        b = {(x, y) for (x, y) in ellipse(cx, hy + 6.5, 3.4, 3.6) if y <= 15}
        S.blob(b, [hexc(body), hexc(body), hexc("#3b3a5a")], hexc("#3b2a3a"), cuts=(0.5, 0.9))
        h = ellipse(cx, hy, 2.5, 2.5)
        S.blob(h, [hexc("#fff0e0"), hexc(skin), hexc("#c89070")], hexc("#6a3a2a"))


def sparkle(S):
    """Cramazing: a big four-pointed sparkle and a little one."""
    big = {(x, y) for x in range(15) for y in range(15)
           if abs(x - 6) * 3 + abs(y - 8) <= 7 or abs(x - 6) + abs(y - 8) * 3 <= 7}
    S.blob(big, [hexc("#ffffff"), hexc("#b8f4f8"), hexc("#5ad0e0"), hexc("#2aa0b8")], hexc("#1e5a6a"))
    for (x, y) in ((12, 1), (12, 2), (12, 3), (11, 2), (13, 2)):
        S.set(x, y, hexc("#ffd24a"))
    S.set(12, 2, hexc("#fffaf0"))


def mixed(S):
    """Mixed Bag: four different goods, as little colored balls."""
    for (cx, cy), ramp in (((4, 4), ["#ff9a8a", "#e8534e", "#b83a44"]),
                           ((11, 4), ["#8ad0f8", "#4a9ae0", "#2a6ab0"]),
                           ((4, 11), ["#fff0a0", "#ffd24a", "#e8a22c"]),
                           ((11, 11), ["#b8f0a0", "#6cc06a", "#3a8a4a"])):
        m = ellipse(cx, cy, 3.3, 3.3)
        S.blob(m, [hexc(c) for c in ramp], hexc("#3b2a3a"), cuts=(-0.3, 0.4))
        S.set(cx - 1, cy - 1, GLINT)


def bell(S):
    """Last Call: a hand bell."""
    m = shape(S, ["....##....",
                  "...####...",
                  "..######..",
                  "..######..",
                  "..######..",
                  ".########.",
                  ".########.",
                  "##########",
                  "##########"], GOLD, GOLD_O, 3, 2)
    S.set(6, 5, GLINT)
    S.set(6, 6, GLINT)
    S.fill({(7, 0), (8, 0), (7, 1), (8, 1)}, hexc("#8a5a34"))
    S.fill(ellipse(8, 12.5, 1.3, 1.3), hexc("#c07a1c"))
    S.set(8, 13, GOLD_O)


def bigtip(S):
    """Big Tipper: a tall stack of coins."""
    for i, y in enumerate((12, 9, 6, 3)):
        coin = rounded_rect(2 + (i % 2), y, 11, 4, 1)
        S.blob(coin, GOLD, GOLD_O, cuts=(-0.5, 0.2, 0.7))
        for x in range(4 + (i % 2), 11 + (i % 2), 2):
            S.set(x, y + 2, hexc("#e8a22c"))
    S.set(4, 4, GLINT)
    S.set(5, 4, GLINT)


def dice(S):
    """Fuzzy Dice: a fluffy pink die."""
    d = rounded_rect(1, 2, 13, 13, 3)
    S.blob(d, [hexc("#ffd0e0"), hexc("#f890b8"), hexc("#d85a90"), hexc("#b03a70")], hexc("#6a1a4a"))
    for (x, y) in ((2, 1), (6, 1), (10, 1), (0, 6), (0, 11), (14, 5), (14, 10)):  # fuzz
        S.set(x, y, hexc("#f890b8"))
    for (x, y) in ((5, 6), (8, 9), (11, 12), (11, 6), (5, 12)):
        S.fill(rect(x - 1, y - 1, 2, 2), hexc("#6a1a4a"))
        S.set(x - 1, y - 1, hexc("#fffaf0"))


def sleepbag(S):
    """Sleeping Bag: a rolled-up bag with two straps."""
    roll = rounded_rect(1, 4, 13, 9, 2)
    S.blob(roll, [hexc("#b8f0a0"), hexc("#6cc06a"), hexc("#3a8a4a"), hexc("#2a6a3a")], hexc("#1e4a2a"))
    end = ellipse(12, 8, 2.6, 4.2)
    S.fill(end, hexc("#fbe8c0"))
    for p in edge(end):
        S.set(*p, hexc("#1e4a2a"))
    S.fill(edge(ellipse(12, 8, 1.2, 2.2)), hexc("#c89a6a"))
    for x in (4, 8):
        for y in range(4, 13):
            S.set(x, y, hexc("#7a4a2a"))
    S.set(3, 6, GLINT)


def fire(S):
    """Camp Fire: a flame over two crossed logs."""
    shape(S, ["......#.......",
              ".....##.......",
              ".....###......",
              "....####...#..",
              "...######.##..",
              "...#########..",
              "..##########..",
              "..###########.",
              "..###########.",
              "...#########..",
              "....#######..."],
          [hexc("#fff4b0"), hexc("#ffd24a"), hexc("#f89a3a"), hexc("#e8534e")], hexc("#8a2a1e"), 1, 0,
          cuts=(-0.6, -0.1, 0.4))
    inner = ellipse(7, 8, 1.6, 2.2)
    S.fill(inner, hexc("#fff4b0"))
    for i in range(12):
        S.set(1 + i, 12 + i // 5, hexc("#8a5a34"))
        S.set(13 - i, 12 + i // 5, hexc("#b07848"))
    for i in range(12):
        S.set(1 + i, 11 + i // 5, WOOD_O if i in (0, 11) else hexc("#b07848"))


def monocle(S):
    """Monocle: a gold-rimmed lens on a chain."""
    lens = ellipse(6.5, 6.5, 5.2, 5.2)
    S.fill(lens, hexc("#e8f6fa"))
    S.fill({(x, y) for (x, y) in lens if x + y > 14}, hexc("#bcdce8"))
    rim = edge(lens) | edge(lens - edge(lens))
    S.blob(rim, GOLD, None, cuts=(-0.4, 0.2, 0.7))
    S.fill(edge(lens), GOLD_O)
    S.set(4, 4, hexc("#ffffff"))
    S.set(5, 3, hexc("#ffffff"))
    S.set(4, 5, hexc("#ffffff"))
    for (x, y) in ((11, 11), (12, 12), (12, 13), (13, 14), (14, 14), (15, 13)):
        S.set(x, y, hexc("#c07a1c"))


def detour(S):
    """Detour: a signpost with arrows pointing both ways."""
    post = rect(7, 3, 2, 13)
    S.fill(post, hexc("#b07848"))
    S.fill(edge(post), WOOD_O)
    right = rows_mask(["#########.",
                       "##########",
                       "#########."], 5, 2)
    left = rows_mask([".#########",
                      "##########",
                      ".#########"], 1, 7)
    S.blob(right, [hexc("#ffe0a0"), hexc("#f8c060"), hexc("#d89a3a")], WOOD_O, cuts=(-0.3, 0.4))
    S.blob(left, [hexc("#ffe0a0"), hexc("#f8c060"), hexc("#d89a3a")], WOOD_O, cuts=(-0.3, 0.4))
    S.set(7, 3, hexc("#fffaf0"))


def vintage(S):
    """Vintage: an hourglass, sand running down."""
    for y in (0, 14):
        bar = rect(2, y, 12, 2)
        S.blob(bar, WOOD, WOOD_O)
    glass = rows_mask(["##########",
                       ".########.",
                       "..######..",
                       "...####...",
                       "....##....",
                       "...####...",
                       "..######..",
                       ".########.",
                       "##########",
                       "##########"], 3, 2)
    S.fill(glass, hexc("#e0f2f6"))
    sand_top = rows_mask(["..######..", "...####...", "....##...."], 3, 4)
    sand_bot = rows_mask(["....##....", "..######..", ".########.", "##########"], 3, 8)
    S.fill(sand_top | sand_bot | {(7, 7), (8, 8)}, hexc("#f0c060"))
    S.fill({(x, y) for (x, y) in sand_bot if x >= 9}, hexc("#d89a3a"))
    S.fill(edge(glass) - rect(0, 2, 16, 1) - rect(0, 11, 16, 1), hexc("#4a6a7a"))
    S.set(4, 3, hexc("#ffffff"))


def broom(S):
    """Clean Sweep: a broom, sweeping."""
    for i in range(8):
        S.set(13 - i, 1 + i, hexc("#b07848"))
        S.set(14 - i, 1 + i, hexc("#8a5a34"))
    S.set(13, 0, WOOD_O)
    S.set(14, 0, WOOD_O)
    bristle = rows_mask(["...####.",
                         "..######",
                         ".#######",
                         "########",
                         "#######.",
                         "######..",
                         "####...."], 1, 8)
    S.blob(bristle, [hexc("#fff0a0"), hexc("#f0c060"), hexc("#c89a3a")], hexc("#6a4a1c"))
    S.fill({(4, 8), (5, 8), (6, 8), (7, 8), (5, 9), (6, 9), (7, 9), (8, 9)} & bristle, hexc("#e8534e"))
    for (x, y) in ((3, 12), (5, 12), (4, 13)):
        S.set(x, y, hexc("#c89a3a"))


def flip(S):
    """Flipper: a pancake flipped up out of a pan."""
    pan = rows_mask([".########.......",
                     "##########......",
                     "##########"+"######",
                     ".########.......",], 0, 11)
    S.blob(pan, [hexc("#8a94a8"), hexc("#5a6478"), hexc("#3b4258")], hexc("#1e2438"), cuts=(-0.2, 0.5))
    S.fill(rect(10, 13, 6, 1), hexc("#7a4a2a"))
    S.set(2, 12, hexc("#c0c8d8"))
    cake = ellipse(6, 5, 4.6, 2.2)
    S.blob(cake, [hexc("#ffe0a0"), hexc("#f0b860"), hexc("#c8843a")], hexc("#6a3a1a"), cuts=(-0.3, 0.4))
    S.set(4, 4, GLINT)
    for (x, y) in ((12, 2), (13, 3), (13, 5), (12, 6), (1, 8), (2, 9)):  # motion arcs
        S.set(x, y, hexc("#c8b8a8"))


def planner(S):
    """Perfect Planner: a clipboard with a ticked list."""
    board = rounded_rect(2, 2, 12, 14, 1)
    S.blob(board, WOOD, WOOD_O)
    paper = rect(4, 4, 8, 10)
    S.fill(paper, hexc("#fffaf0"))
    S.fill({(11, y) for y in range(4, 14)}, hexc("#e8dcc8"))
    clip = rect(6, 1, 4, 3)
    S.blob(clip, [hexc("#f0f4f8"), hexc("#c0c8d8"), hexc("#8a94a8")], hexc("#3b3a5a"))
    for y in (6, 9, 12):
        S.set(5, y, hexc("#3a9a4a"))
        S.set(6, y - 1, hexc("#3a9a4a"))
        for x in range(8, 11):
            S.set(x, y, hexc("#b8a08c"))


def truck(S):
    """Dump Truck: a little truck tipping its load."""
    bed = rows_mask(["#.........",
                     "###.......",
                     "######....",
                     "#########.",
                     "##########"], 0, 4)
    load = rows_mask(["##", "###", "####", "###"], 0, 1)
    S.blob(load, [hexc("#d8a070"), hexc("#b07848"), hexc("#8a5a34")], WOOD_O)
    S.blob(bed, [hexc("#fff0a0"), hexc("#ffd24a"), hexc("#e8a22c")], GOLD_O, cuts=(-0.3, 0.4))
    cab = rect(10, 5, 5, 5) | rect(1, 9, 14, 3)
    S.blob(cab, [hexc("#ff9a8a"), hexc("#e8534e"), hexc("#b83a44")], hexc("#5a1a2a"), cuts=(-0.3, 0.4))
    S.fill(rect(11, 6, 3, 2), hexc("#cfe8ec"))
    S.set(11, 6, hexc("#ffffff"))
    for cx in (4, 12):
        w = ellipse(cx, 12.5, 1.8, 1.8)
        S.fill(w, hexc("#3b3a5a"))
        S.set(cx, 12, hexc("#b8b0c0"))


ICONS = (("eye", eye), ("haggle", haggle), ("fannypack", fannypack), ("crowd", crowd),
         ("sparkle", sparkle), ("mixed", mixed), ("bell", bell), ("bigtip", bigtip), ("dice", dice),
         ("sleepbag", sleepbag), ("fire", fire), ("monocle", monocle), ("detour", detour),
         ("vintage", vintage), ("broom", broom), ("flip", flip), ("planner", planner), ("truck", truck))

for n, f in ICONS:
    icon(n, f)

# contact sheet: on the stamp window colour and on the dark tooltip colour
sheet = Image.new("RGBA", (len(ICONS) * 20 + 4, 44), hexc("#fff6e8"))
sheet.paste(Image.new("RGBA", (sheet.width, 22), hexc("#3b2f55")), (0, 22))
for i, (n, _) in enumerate(ICONS):
    im = Image.open(os.path.join(ASSETS, "ui", "icon_" + n + ".png"))
    sheet.alpha_composite(im, (4 + i * 20, 3))
    sheet.alpha_composite(im, (4 + i * 20, 25))
sheet.resize((sheet.width * 5, sheet.height * 5), Image.NEAREST).save(
    os.path.join(PREVIEWS, "_stamp_icons_sheet.png"))
