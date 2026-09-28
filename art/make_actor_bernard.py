"""Bernard: a St. Bernard rescue dog. White blaze and jowly muzzle, big
droopy russet ears and eye patches, a red collar with the classic little
wooden barrel (full of cocoa, for emergencies)."""
from pixelkit import hexc, ellipse, edge, rect, rounded_rect
from portraitkit import new, poly, eye, blush, clip, finish, smile, GLINT

S = new()

BROWN = [hexc("#e0a070"), hexc("#c0703c"), hexc("#9a522a"), hexc("#743a1e")]
BR_OUT = hexc("#40200e")
WHITE = [hexc("#ffffff"), hexc("#f8f0e6"), hexc("#e4d6c6"), hexc("#c8b6a4")]
WH_OUT = hexc("#6a5448")
COLLAR = [hexc("#ff8a7a"), hexc("#e0474c"), hexc("#b83244")]
CO_OUT = hexc("#5a1626")
WOOD = [hexc("#d8a46a"), hexc("#b07840"), hexc("#8a5a2e"), hexc("#6a4222")]
WD_OUT = hexc("#3a2212")
METAL = [hexc("#fff4c0"), hexc("#f4c24a"), hexc("#c08a2a")]
NOSE = hexc("#3a2230")
TONGUE = hexc("#f28a9a")

# body: brown shoulders, white chest
body = clip(ellipse(32, 66, 28, 15))
S.blob(body, BROWN, BR_OUT, cuts=(-0.5, 0.2, 0.7))
chest = clip(ellipse(32, 67, 13, 14)) - edge(body)
S.blob(chest, WHITE, None, cuts=(-0.3, 0.3, 0.7))

# long droopy ears (behind the head)
# neck so the head sits on the shoulders
neck = ellipse(32, 48, 14, 8)
S.blob(neck, BROWN, BR_OUT, cuts=(-0.5, 0.2, 0.7))
S.blob(ellipse(32, 50, 7, 6) - edge(neck), WHITE, None, cuts=(-0.3, 0.3, 0.7))
for cx in (16, 48):
    ear = ellipse(cx, 33, 6, 12) | ellipse(cx + (2 if cx < 32 else -2), 22, 5, 4)
    S.blob(ear, BROWN, BR_OUT, cuts=(-0.3, 0.2, 0.6))

# head: white with brown patches
head = ellipse(32, 30, 17, 15)
S.blob(head, WHITE, WH_OUT, cuts=(-0.5, 0.25, 0.75))
inner = head - edge(head)
for side in (-1, 1):
    patch = ellipse(32 + side * 10, 26, 8, 8) & inner
    patch -= {(x, y) for (x, y) in patch if abs(x - 32) <= 2}   # white blaze
    S.blob(patch, BROWN, None, cuts=(-0.4, 0.2, 0.7), center=(29, 26))
# brown cap with a white blaze down the middle
top = {(x, y) for (x, y) in inner if y <= 19 and abs(x - 32) > 2}
S.blob(top, BROWN, None, cuts=(-0.4, 0.2, 0.7), center=(29, 26))

# eyes (a little droopy) in the patches
eye(S, 23, 26, 3, 4)
eye(S, 38, 26, 3, 4)
for (x, y) in ((22, 25), (23, 24), (24, 24), (25, 24), (37, 24), (38, 24), (39, 24), (40, 25)):
    S.set(x, y, BROWN[3])   # heavy lids

# jowly muzzle
muz = ellipse(27.5, 37, 6.5, 5) | ellipse(36.5, 37, 6.5, 5)
S.blob(muz, WHITE, WH_OUT, cuts=(-0.2, 0.5, 0.85))
nose = ellipse(32, 32.5, 3.6, 2.4)
S.fill(nose, NOSE)
S.set(31, 32, GLINT)
S.set(30, 32, hexc("#6a4a5a"))
for y in (35, 36, 37):
    S.set(32, y, WH_OUT)
# little tongue peeking out
S.fill({(31, 41), (32, 41), (33, 41), (31, 42), (32, 42), (33, 42)}, TONGUE)
S.set(33, 42, hexc("#c86a7a"))
for (x, y) in ((25, 37), (27, 38), (37, 38), (39, 37)):
    S.set(x, y, WHITE[3])
blush(S, 19, 34)
blush(S, 43, 34)

# red collar
for x in range(18, 47):
    t = (x - 32) / 15
    y0 = 43 + round(4 * (1 - t * t))
    for dy, c in ((0, CO_OUT), (1, COLLAR[0] if x < 32 else COLLAR[1]), (2, COLLAR[1]),
                  (3, COLLAR[2]), (4, CO_OUT)):
        S.set(x, y0 - 2 + dy, c)

# little cocoa barrel hanging from the collar
BX, BY = 25, 50
barrel = rounded_rect(BX, BY, 15, 10, r=3)
S.blob(barrel, WOOD, WD_OUT, lx=0.4, ly=1.0, cuts=(-0.5, 0.2, 0.7))
for x in range(BX + 1, BX + 14):   # stave lines
    if x in (BX + 4, BX + 8, BX + 11):
        for y in range(BY + 1, BY + 9):
            S.set(x, y, WOOD[3])
for bx in (BX + 2, BX + 12):   # brass hoops
    for y in range(BY, BY + 10):
        if (bx, y) in barrel:
            S.set(bx, y, METAL[1] if y < BY + 5 else METAL[2])
S.set(BX + 2, BY + 1, METAL[0])
S.set(BX + 6, BY + 2, GLINT)
S.set(BX + 7, BY + 2, GLINT)
# ring holding it
S.set(BX + 7, BY - 1, METAL[2])

finish(S, "bernard")
