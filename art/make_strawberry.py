"""Generate a 32x32 pixel-art strawberry with a transparent background.

Style follows the reference sheet: tinted dark outlines (not black), soft
saturated fills, light from the upper-left, a small white specular glint.
"""
from PIL import Image

from pixelkit import save_image

W = H = 32
CX = 15.5  # horizontal center

PAL = {
    "O": (92, 22, 38, 255),     # body outline (deep wine)
    "d": (140, 28, 52, 255),    # deepest red shade
    "r": (190, 36, 56, 255),    # red shade
    "R": (230, 58, 64, 255),    # base red
    "L": (246, 112, 98, 255),   # light red
    "W": (255, 238, 226, 255),  # specular glint
    "y": (255, 222, 120, 255),  # seed
    "Y": (214, 160, 70, 255),   # seed in shadow
    "o": (30, 72, 44, 255),     # leaf outline
    "g": (48, 138, 62, 255),    # leaf shade
    "G": (92, 190, 76, 255),    # leaf base
    "H": (158, 226, 108, 255),  # leaf light
    "S": (120, 140, 60, 255),   # stem
}

# Body half-widths per row (row -> half width in pixels)
HALF = {8: 6, 9: 9, 10: 10, 11: 11, 12: 12, 13: 12, 14: 12, 15: 12, 16: 12,
        17: 11, 18: 11, 19: 10, 20: 10, 21: 9, 22: 8, 23: 8, 24: 7, 25: 6,
        26: 5, 27: 4, 28: 3, 29: 2}

LEAVES = [
    "................................",
    "................SS..............",
    "...............SS...............",
    "...............SS...............",
    "..........HH...SS...GG..........",
    "........HHGGG.GSSG.GGgg.........",
    "......HHGGGGGGGGGGGGGGGgg.......",
    ".....HGGGGGGGGGGGGGGGGGGgg......",
    "....HGGGGgGGGGGGGGGGgGGGGgg.....",
    "....GGGg..gGGGGGGGGg..gGGGg.....",
    "...GGg.....gGG..GGg.....gGGg....",
    "...Gg.......gg...Gg......ggg....",
    "............g....g..............",
]

grid = [["." for _ in range(W)] for _ in range(H)]

# --- body -------------------------------------------------------------
body = set()
for y, hw in HALF.items():
    for x in range(int(CX + 0.5 - hw), int(CX + 0.5 + hw)):
        body.add((x, y))

def is_edge(p, mask):
    x, y = p
    return any((x + dx, y + dy) not in mask
               for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))

top, bot = min(HALF), max(HALF)
for (x, y) in body:
    if is_edge((x, y), body):
        grid[y][x] = "O"
        continue
    nx = (x - CX) / HALF[y]
    ny = (y - top) / (bot - top)
    v = nx * 0.75 + ny * 0.55
    grid[y][x] = "L" if v < -0.3 else "R" if v < 0.3 else "r" if v < 0.65 else "d"

# seeds on a staggered grid, each with a small shadow pixel beneath
for i, y in enumerate(range(12, 28, 3)):
    for x in range(2 + (i % 2) * 2, W, 4):
        p = (x, y)
        if p in body and not is_edge(p, body) and all(
                (x + dx, y + dy) in body and not is_edge((x + dx, y + dy), body)
                for dx, dy in ((1, 0), (-1, 0), (0, 1))):
            shaded = grid[y][x] in "rd"
            grid[y][x] = "Y" if shaded else "y"
            grid[y + 1][x] = "d" if shaded else "r"

# specular glint, upper-left
for x, y in ((7, 13), (7, 14), (8, 13), (7, 16)):
    grid[y][x] = "W"

# --- leaves (outline drawn outside the leaf mask) --------------------
leaf = {(x, y) for y, row in enumerate(LEAVES) for x, c in enumerate(row) if c != "."}
for (x, y) in leaf:
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            q = (x + dx, y + dy)
            if q not in leaf and 0 <= q[0] < W and 0 <= q[1] < H and abs(dx) + abs(dy) == 1:
                grid[q[1]][q[0]] = "o"
for (x, y) in leaf:
    grid[y][x] = LEAVES[y][x]

# --- write -------------------------------------------------------------
img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
for y in range(H - 1):
    for x in range(W):
        if grid[y][x] != ".":
            img.putpixel((x, y + 1), PAL[grid[y][x]])  # +1 to center vertically

save_image(img, "strawberry", "goods")
print("\n".join("".join(r) for r in grid))
