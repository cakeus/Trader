"""UI kit: 9-slice panels, button states, small HUD icons, and the cursor.

9-slice images are 24x24 with 8px corners (the game stretches the middle).
"""
from PIL import Image

from pixelkit import Sprite, hexc, ellipse, rect, rounded_rect, edge, save_image


def nine_slice(name, outline, fill, hi, lo, shadow=None, size=24):
    """Rounded box: tinted outline, 1px top/left highlight, bottom/right shade."""
    S = Sprite(size, size)
    h = size - (1 if shadow else 0)
    box = rounded_rect(0, 0, size, h, 2)
    S.fill(box, fill)
    inner = box - edge(box)
    ie = edge(inner)
    for (x, y) in ie:
        # upper-left highlight, lower-right shade
        S.set(x, y, hi if (x - size / 2) + (y - h / 2) < 0 else lo)
    S.fill(edge(box), outline)
    if shadow:
        for x in range(2, size - 2):
            S.set(x, size - 1, shadow)
        S.set(1, size - 2, shadow)
        S.set(size - 2, size - 2, shadow)
    return S.save(name, "ui", show=False)


# paper panel (dialogs, cards)
nine_slice("panel", hexc("#5a3a3e"), hexc("#fbf1dc"), hexc("#fffaf0"), hexc("#ead8bc"),
           shadow=hexc("#3a2230", 110))
# dark tooltip / HUD bar
nine_slice("panel_dark", hexc("#1e1630"), hexc("#3b2f55"), hexc("#55467a"), hexc("#2e2444"),
           shadow=hexc("#140e20", 110))
# buttons: normal / hover / down / disabled
nine_slice("btn", hexc("#6e3a2c"), hexc("#f5b66a"), hexc("#ffe0a8"), hexc("#d98a4a"),
           shadow=hexc("#4a2418", 160))
nine_slice("btn_hover", hexc("#6e3a2c"), hexc("#ffc983"), hexc("#fff0c8"), hexc("#e89a58"),
           shadow=hexc("#4a2418", 160))
nine_slice("btn_down", hexc("#6e3a2c"), hexc("#d98a4a"), hexc("#c07038"), hexc("#e8a060"))
nine_slice("btn_disabled", hexc("#6a5c66"), hexc("#c9bcb4"), hexc("#ddd2ca"), hexc("#b0a29c"),
           shadow=hexc("#40343c", 120))
# row highlight inside dialogs
nine_slice("row", hexc("#c9a98a"), hexc("#f3e2c4"), hexc("#fff4dc"), hexc("#e2cca8"))
nine_slice("row_hover", hexc("#b87a4a"), hexc("#ffe7b8"), hexc("#fff6dc"), hexc("#f2d094"))

# --- 16x16 icons -------------------------------------------------------------

def icon(name, draw):
    S = Sprite(16, 16)
    draw(S)
    S.center()
    S.save("icon_" + name, "ui", scale=12, show=False)


def coin(S):
    m = ellipse(7.5, 7.5, 6.6, 6.6)
    S.blob(m, [hexc("#fff0a0"), hexc("#ffd24a"), hexc("#e8a22c"), hexc("#c07a1c")],
           hexc("#7a4a14"), cuts=(-0.4, 0.25, 0.7))
    inner = ellipse(7.5, 7.5, 3.6, 3.6)
    for p in edge(inner):
        if p[0] + p[1] > 15:
            S.set(*p, hexc("#fff0a0"))
        else:
            S.set(*p, hexc("#c07a1c"))
    S.set(4, 4, hexc("#fffaf0"))
    S.set(5, 3, hexc("#fffaf0"))


def bag(S):
    body = ellipse(7.5, 9.5, 6.2, 5.2) | rect(4, 5, 8, 4)
    S.blob(body, [hexc("#e8b87a"), hexc("#c88a4e"), hexc("#a0663a"), hexc("#7e4a2a")],
           hexc("#4a2a1c"), cuts=(-0.4, 0.25, 0.7))
    tie = rect(4, 4, 8, 2)
    S.fill(tie, hexc("#e8534e"))
    S.fill(edge(tie) & rect(4, 5, 8, 1), hexc("#a83040"))
    top = {(5, 2), (6, 1), (7, 2), (8, 2), (9, 1), (10, 2), (6, 2), (9, 2), (7, 3), (8, 3)}
    S.fill(top, hexc("#c88a4e"))
    S.outline_around(top | tie, hexc("#4a2a1c"))
    S.fill(tie, hexc("#e8534e"))
    S.fill(top, hexc("#c88a4e"))
    S.set(4, 8, hexc("#f8d8a4"))
    S.set(4, 9, hexc("#f8d8a4"))


def calendar(S):
    page = rect(1, 2, 14, 13)
    S.fill(page, hexc("#fbf1dc"))
    S.fill(rect(1, 2, 14, 4), hexc("#e8534e"))
    S.fill(edge(page), hexc("#5a3a3e"))
    for (x, y) in ((4, 1), (11, 1), (4, 2), (11, 2)):
        S.set(x, y, hexc("#3b2f55"))
    for y in (8, 11):
        for x in (4, 7, 10):
            S.set(x, y, hexc("#b8a08c"))
    S.set(10, 11, hexc("#e8534e"))


def check(S):
    rows = ["..........##",
            ".........###",
            "........###.",
            ".##....###..",
            ".###..###...",
            "..######....",
            "...####.....",
            "....##......"]
    pal = {"#": hexc("#6cd06a")}
    S.rows(rows, pal, 2, 4)
    m = {p for p in S.px}
    S.outline_around(m, hexc("#1e5a34"))
    S.rows(rows, pal, 2, 4)
    for (x, y) in ((12, 4), (11, 5), (3, 7)):
        S.set(x, y, hexc("#c8f4a8"))


def pin(S):
    head = ellipse(7.5, 5.5, 4.6, 4.6)
    tail = {(x, y) for y in range(9, 15) for x in range(8 - (14 - y) // 2, 8 + (14 - y) // 2 + 1)}
    m = head | tail
    S.blob(m, [hexc("#ff9a8a"), hexc("#e8534e"), hexc("#b83a44"), hexc("#8a2a3a")],
           hexc("#5a1a2a"), cuts=(-0.4, 0.2, 0.7), center=(7.5, 6))
    dot = ellipse(7.5, 5.5, 1.6, 1.6)
    S.fill(dot, hexc("#fbf1dc"))
    S.set(5, 3, hexc("#fffaf0"))


def star(S):
    rows = [".....#.....",
            "....###....",
            "....###....",
            "###########",
            ".#########.",
            "..#######..",
            "..###.###..",
            ".###...###.",
            ".##.....##."]
    m = {(x + 2, y + 3) for y, r in enumerate(rows) for x, c in enumerate(r) if c == "#"}
    S.blob(m, [hexc("#fff4b0"), hexc("#ffd24a"), hexc("#e8a22c")], hexc("#7a4a14"),
           cuts=(-0.2, 0.5))


def flag(S):
    pole = rect(3, 1, 2, 14)
    S.fill(pole, hexc("#c8a078"))
    S.fill(edge(pole), hexc("#5a3a2a"))
    rows = ["#########.",
            "##########",
            "#########.",
            "########..",
            "#######..."]
    m = {(x + 5, y + 2) for y, r in enumerate(rows) for x, c in enumerate(r) if c == "#"}
    S.blob(m, [hexc("#ff9a8a"), hexc("#e8534e"), hexc("#b83a44")], hexc("#5a1a2a"), cuts=(-0.3, 0.4))
    S.set(4, 1, hexc("#fffaf0"))


def tag(S):
    """A sale tag (hole on the left, string curling up) with a % on it."""
    rows = [".....##########",
            "....###########",
            "...############",
            "..#############",
            ".##############",
            "..#############",
            "...############",
            "....###########",
            ".....##########"]
    m = {(x, y + 4) for y, r in enumerate(rows) for x, c in enumerate(r) if c == "#"}
    S.blob(m, [hexc("#ff9a8a"), hexc("#e8534e"), hexc("#b83a44")], hexc("#5a1a2a"), cuts=(-0.6, 0.6))
    S.set(4, 8, hexc("#5a1a2a"))  # the hole
    for (x, y) in ((4, 7), (3, 6), (3, 5), (3, 4), (4, 3), (5, 2), (6, 2)):
        S.set(x, y, hexc("#8a6a4a"))
    pct = ["##..#",
           "##.#.",
           "..#..",
           ".#.##",
           "#..##"]
    for y, r in enumerate(pct):
        for x, c in enumerate(r):
            if c == "#":
                S.set(x + 8, y + 6, hexc("#fffaf0"))


def tip(S):
    """A tip jar: a glass jar with coins inside and one dropping in."""
    jar = rect(3, 6, 10, 9) | rect(4, 5, 8, 1)
    S.fill(jar, hexc("#cfe8ec"))
    S.fill({(x, y) for (x, y) in jar if x >= 10}, hexc("#a8cad4"))
    coins = rect(4, 11, 8, 3) | rect(5, 10, 4, 1)
    S.fill(coins, hexc("#ffd24a"))
    S.fill({(x, 13) for x in range(4, 12)} | {(11, 12), (11, 11)}, hexc("#e8a22c"))
    for (x, y) in ((5, 11), (8, 12), (6, 10)):
        S.set(x, y, hexc("#fff0a0"))
    S.fill(edge(jar), hexc("#4a6a7a"))
    S.set(4, 7, hexc("#ffffff"))
    S.set(4, 8, hexc("#ffffff"))
    S.rows([".oooo.",
            "oh###o",
            "o###so",
            ".oooo."], {"o": hexc("#7a4a14"), "#": hexc("#ffd24a"), "h": hexc("#fff0a0"),
                        "s": hexc("#e8a22c")}, 5, 0)  # the coin dropping in, above the open jar


def more(S):
    """A coin with a green arrow rising beside it (prices going up)."""
    m = ellipse(5.5, 10, 4.8, 4.8)
    S.blob(m, [hexc("#fff0a0"), hexc("#ffd24a"), hexc("#e8a22c"), hexc("#c07a1c")],
           hexc("#7a4a14"), cuts=(-0.4, 0.25, 0.7))
    for p in edge(ellipse(5.5, 10, 2.4, 2.4)):
        S.set(*p, hexc("#fff0a0") if p[0] + p[1] > 15.5 else hexc("#c07a1c"))
    S.set(3, 7, hexc("#fffaf0"))
    arrow = ["...#...",
             "..###..",
             ".#####.",
             "#######",
             "..###..",
             "..###..",
             "..###.."]
    am = {(x + 8, y + 1) for y, r in enumerate(arrow) for x, c in enumerate(r) if c == "#"}
    S.outline_around(am, hexc("#1e5a34"))
    S.fill(am, hexc("#6cd06a"))
    for (x, y) in ((11, 2), (10, 3), (9, 4), (10, 5), (10, 6), (10, 7)):
        S.set(x, y, hexc("#c8f4a8"))


def collector(S):
    """A postage stamp (perforated edge) with a magnifying glass over its corner."""
    st = rect(1, 3, 10, 12)
    perf = {(x, y) for (x, y) in st if (x in (1, 10) and y % 2 == 0) or (y in (3, 14) and x % 2 == 0)}
    body = st - perf
    S.fill(body, hexc("#fff4e4"))
    S.fill({(x, y) for (x, y) in body if x == 9 or y == 13}, hexc("#e2cca8"))
    inner = rect(3, 5, 6, 8)
    S.blob(inner, [hexc("#ff9a8a"), hexc("#e8534e"), hexc("#b83a44")], hexc("#5a1a2a"), cuts=(-0.3, 0.4))
    S.set(4, 6, hexc("#fffaf0"))
    S.fill(edge(body) - inner, hexc("#8a6a5a"))
    # the magnifier: glass ring and a handle to the lower right
    lens = ellipse(11, 5, 3.6, 3.6)
    S.fill(lens, hexc("#cfe8ec"))
    S.fill({(x, y) for (x, y) in lens if x + y > 17}, hexc("#a8cad4"))
    S.fill(edge(lens), hexc("#4a6a7a"))
    S.set(10, 3, hexc("#ffffff"))
    S.set(9, 4, hexc("#ffffff"))
    for (x, y) in ((13, 8), (14, 9), (15, 10), (14, 10), (13, 9)):
        S.set(x, y, hexc("#7a4a2a"))
    S.set(14, 8, hexc("#b87a4a"))


for n, f in (("coin", coin), ("bag", bag), ("calendar", calendar), ("check", check),
             ("pin", pin), ("star", star), ("flag", flag), ("tag", tag), ("tip", tip), ("more", more), ("collector", collector)):
    icon(n, f)

# --- cursor (12x14 arrow) -------------------------------------------------------
CUR = ["O...........",
       "OO..........",
       "OWO.........",
       "OWWO........",
       "OWWWO.......",
       "OWWWWO......",
       "OWWWWWO.....",
       "OWWWWWWO....",
       "OWWWWWWWO...",
       "OWWWWOOOOO..",
       "OWWOWO......",
       "OWO.OWO.....",
       "OO..OWO.....",
       ".....OO....."]
S = Sprite(12, 14)
S.rows(CUR, {"O": hexc("#3b1f3a"), "W": hexc("#fff4e4")})
S.set(1, 3, hexc("#fffaf0"))
for (x, y) in ((5, 8), (6, 8), (7, 8), (4, 7), (5, 7), (6, 7)):
    S.set(x, y, hexc("#f2c8b8"))
S.save("cursor", "ui", scale=12, show=False)

# --- ui sheet preview ------------------------------------------------------------
import os
from pixelkit import ASSETS, PREVIEWS
names = ["panel", "panel_dark", "btn", "btn_hover", "btn_down", "btn_disabled", "row", "row_hover",
         "icon_coin", "icon_bag", "icon_calendar", "icon_check", "icon_pin", "icon_star", "icon_flag", "icon_tag", "icon_tip", "icon_more", "icon_collector", "cursor"]
sheet = Image.new("RGBA", (len(names) * 28 + 4, 30), (120, 150, 130, 255))
for i, n in enumerate(names):
    im = Image.open(os.path.join(ASSETS, "ui", n + ".png"))
    sheet.alpha_composite(im, (4 + i * 28, 3))
sheet.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save(
    os.path.join(PREVIEWS, "_ui_sheet.png"))
