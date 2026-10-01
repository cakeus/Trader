"""Bigger stars for the quota tally -> assets/ui/icon_star16.png (the star rows) and
icon_star24.png (the Stars earned total).

A plump five-point star filling its frame, hand-drawn as rows: gold ramp lit from the
upper-left, a dark gold outline, a lighter rim along the upper-left edges and a cream glint.
(The HUD's icon_star in make_ui.py is a smaller, squatter one.)
"""
from pixelkit import Sprite, edge, hexc, rows_mask

GOLD = [hexc("#fff4b0"), hexc("#ffd24a"), hexc("#e8a22c"), hexc("#c07a1c")]
GOLD_O = hexc("#7a4a14")
GLINT = hexc("#fffaf0")

STAR16 = ["......###......",
          "......###......",
          ".....#####.....",
          ".....#####.....",
          "###############",
          ".#############.",
          "..###########..",
          "...#########...",
          "...#########...",
          "..###########..",
          "..#####.#####..",
          ".#####...#####.",
          ".####.....####.",
          ".###.......###."]

STAR24 = ["..........###..........",
          "..........###..........",
          ".........#####.........",
          ".........#####.........",
          "........#######........",
          "........#######........",
          ".......#########.......",
          "#######################",
          ".#####################.",
          "..###################..",
          "...#################...",
          "....###############....",
          ".....#############.....",
          ".....#############.....",
          "....###############....",
          "....#######.#######....",
          "...#######...#######...",
          "...######.....######...",
          "..######.......######..",
          "..#####.........#####..",
          ".#####...........#####.",
          ".###...............###."]


def make(rows, size, glints):
    assert len({len(r) for r in rows}) == 1, "ragged rows"
    S = Sprite(size, size)
    m = rows_mask(rows)
    S.blob(m, GOLD, GOLD_O, cuts=(-0.35, 0.2, 0.7))
    # a lighter rim just inside the outline along the upper-left edges
    inner = m - edge(m)
    w = len(rows[0])
    for (x, y) in edge(inner):
        if x + y < w * 0.75 and (x - 1, y) not in inner or (x, y - 1) not in inner and x < w / 2:
            S.set(x, y, GOLD[0])
    for (x, y) in glints:
        S.set(x, y, GLINT)
    S.center()
    return S


make(STAR16, 16, [(6, 5), (5, 6)]).save("icon_star16", "ui", scale=12, show=False)
make(STAR24, 24, [(9, 8), (8, 9), (9, 9)]).save("icon_star24", "ui", scale=8, show=False)
