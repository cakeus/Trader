"""Shelly: a sea otter beachcomber in a sunny bucket hat, hugging a pink shell."""
import math

from pixelkit import hexc, ellipse, edge
from portraitkit import new, poly, eye, blush, clip, finish, smile, GLINT

S = new()

FUR = [hexc("#d8a878"), hexc("#a8744a"), hexc("#86573a"), hexc("#66402a")]
F_OUT = hexc("#3a2218")
FACE = [hexc("#fff4e0"), hexc("#f0dcc0"), hexc("#d8bc9c")]
HAT = [hexc("#fff0a0"), hexc("#ffd24a"), hexc("#e8a22c"), hexc("#c07a1c")]
H_OUT = hexc("#6a4414")
STRIPE = hexc("#3f8f8a")
SHELL = [hexc("#ffe4d6"), hexc("#fbb9a4"), hexc("#e98a86"), hexc("#bf5f72")]
SHELL_OUT = hexc("#7a2e4a")

# body (bare otter fur, lighter belly)
body = clip(ellipse(32, 64, 26, 15))
S.blob(body, FUR, F_OUT, cuts=(-0.5, 0.2, 0.7))
belly = clip(ellipse(32, 66, 14, 12)) - edge(body)
S.blob(belly, FACE, None, cuts=(-0.1, 0.6))

# small round ears
for cx in (17, 47):
    ear = ellipse(cx, 25, 4, 3.6)
    S.blob(ear, FUR, F_OUT, cuts=(-0.2, 0.5))
    S.set(cx, 25, FUR[3])

# head + pale face
head = ellipse(32, 33, 17, 14)
S.blob(head, FUR, F_OUT, cuts=(-0.5, 0.25, 0.75))
face = ellipse(32, 37, 12, 8.5) - edge(head)
S.blob(face, FACE, None, cuts=(-0.2, 0.6))

# bucket hat
crown = poly([(19, 23), (45, 23), (42, 12), (22, 12)])
S.blob(crown, HAT, H_OUT, cuts=(-0.4, 0.3, 0.75))
brim = ellipse(32, 23, 20, 3.6)
S.blob(brim, HAT, H_OUT, cuts=(-0.3, 0.4, 0.8))
for x in range(21, 44):
    if (x, 19) in crown and (x, 19) not in edge(crown):
        S.set(x, 19, STRIPE)
S.set(25, 14, GLINT)

# face details
eye(S, 25, 30, 3, 3)
eye(S, 36, 30, 3, 3)
nose = ellipse(32, 35, 2.6, 1.8)
S.fill(nose, F_OUT)
S.set(31, 34, GLINT)
S.set(32, 37, F_OUT)
smile(S, 29, 38, 7, F_OUT)
# whisker dots
for (x, y) in ((25, 36), (27, 37), (25, 38), (37, 37), (39, 36), (39, 38)):
    S.set(x, y, FUR[2])
blush(S, 21, 35)
blush(S, 42, 35)

# seashell hugged to the chest, with little paws
PX, PY = 32, 61
fan = set()
for y in range(44, 63):
    for x in range(18, 47):
        dx, dy = x - PX, PY - y
        a = math.atan2(dx, dy)
        t = (a + math.radians(58)) / math.radians(116) * 5
        rim = 11.8 + 1.4 * abs(math.cos(math.pi * t))
        if abs(a) <= math.radians(58) and math.hypot(dx, dy) <= rim:
            fan.add((x, y))
# hinge "ears" at the bottom of the scallop
hinge = {(x, y) for y in range(58, 63) for x in range(26, 39)} - fan
S.blob(hinge, SHELL, SHELL_OUT, cuts=(-0.2, 0.5))
S.blob(fan, SHELL, SHELL_OUT, cuts=(-0.35, 0.2, 0.6), center=(PX, 53))
inner = fan - edge(fan)
for i in range(1, 5):
    a = math.radians(-58 + 116 * i / 5)
    for r10 in range(30, 130):
        r = r10 / 10
        p = (round(PX + math.sin(a) * r), round(PY - math.cos(a) * r))
        if p in inner:
            S.set(*p, SHELL[3] if p[0] > PX + 2 else SHELL[2])
S.set(27, 51, GLINT)
S.set(28, 50, GLINT)
for cx in (20, 44):
    paw = ellipse(cx, 56, 3.4, 3)
    S.blob(paw, FUR, F_OUT, cuts=(-0.2, 0.5))

finish(S, "shelly")
