"""32x32 wool mittens: a matching red pair, thumbs toward each other, the back one a little
higher, with cream ribbed cuffs, a cream knit stripe and the yarn string that joins them."""
from pixelkit import Sprite, hexc, ellipse, rect, edge

W = H = 32
S = Sprite(W, H)

RED = [hexc("#ff9a86"), hexc("#e8524a"), hexc("#b8383c"), hexc("#8a2630")]
RED_BACK = [hexc("#e8786a"), hexc("#c8443e"), hexc("#9c3036"), hexc("#74202a")]
RED_OUT = hexc("#5e1c24")
CREAM = [hexc("#fffbea"), hexc("#f2e2c0"), hexc("#d4bc92")]
CREAM_OUT = hexc("#8a6a48")
RIB = hexc("#c2a67c")
YARN = hexc("#f2e2c0")
GLINT = hexc("#fffbea")


def mitten(ox, oy, flip, ramp):
    """One mitten, 12 wide; the thumb on the right (or the left when flipped)."""
    def fx(x):
        return ox + (11 - x if flip else x)
    hand = {(x, y) for (x, y) in ellipse(4.5, 5.0, 4.5, 5.0) if y <= 5}
    hand |= rect(0, 5, 10, 9)
    thumb = ellipse(10.0, 7.6, 1.9, 3.4) | {(9, 10), (9, 11), (10, 11), (8, 12), (9, 12)}
    body = {(fx(x), oy + y) for (x, y) in hand | thumb}
    S.blob(body, ramp, RED_OUT, lx=0.8, ly=0.45, cuts=(-0.5, 0.25, 0.7))
    # the line where the thumb meets the hand
    for y in range(6, 11):
        S.set(fx(9), oy + y, RED_OUT if y < 8 else ramp[3])
    # knit stripe across the back of the hand: a cream band with a row of red stitches
    for x in range(1, 9):
        for y in (9, 10):
            S.set(fx(x), oy + y, CREAM[0] if x < 3 else CREAM[1])
        if x % 2 == 1:
            S.set(fx(x), oy + 9 + (x // 2) % 2, ramp[1])
    # ribbed cuff
    cuff = {(fx(x), oy + y) for (x, y) in rect(0, 13, 10, 5)}
    S.blob(cuff, CREAM, CREAM_OUT, lx=0.8, ly=0.3, cuts=(-0.5, 0.45))
    for (x, y) in cuff - edge(cuff):
        if (x - ox) % 2 == 0:
            S.set(x, y, RIB)
    return body | cuff


back = mitten(15, 2, True, RED_BACK)
front = mitten(2, 7, False, RED)

# the yarn string that joins the cuffs, drooping below them
# (from under the front cuff at x 7 to under the back cuff at x 21)
for (x, y) in ((7, 25), (7, 26), (8, 27), (9, 28), (10, 28), (11, 28), (12, 28), (13, 28),
               (14, 27), (15, 26), (16, 25), (17, 24), (18, 23), (19, 22), (20, 21), (21, 20)):
    S.set(x, y, YARN)
    if S.get(x, y + 1) is None:
        S.set(x, y + 1, CREAM_OUT)

# glints, upper-left of each mitten
for (x, y) in ((5, 9), (4, 10), (18, 4), (17, 5)):
    S.set(x, y, GLINT)

S.center()
S.save("wool_mittens", "goods")
