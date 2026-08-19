#!/usr/bin/env python3
"""Cover concept C: a coach's TACTICS-BOARD 'playbook' on a bold tangerine ground.
Completely different design + imagery from the sticky-note covers.
Writes cover_play.png / cover_play.jpg. Touches nothing else."""
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = 2
W, H = 1600 * S, 2560 * S

# --- bold, high-visibility palette ---
ORANGE_TOP = (198, 74, 36)     # deep ember
ORANGE_BOT = (232, 126, 48)    # bright tangerine
CHALK      = (247, 242, 230)
CHALK_SOFT = (247, 242, 230, 150)
INKDOT     = (150, 44, 16)
CREAM      = (247, 242, 230)

FONTS = "/usr/share/fonts/opentype/urw-base35/"
def font(name, px): return ImageFont.truetype(FONTS + name, px * S)
f_title = font("URWGothic-Demi.otf", 168)
f_kick  = font("URWGothic-Book.otf", 33)
f_sub   = font("NimbusRoman-Italic.otf", 44)
f_auth  = font("URWGothic-Book.otf", 46)
f_imp   = font("NimbusSans-Regular.otf", 26)

# --- background: vertical tangerine gradient + soft vignette ---
img = Image.new("RGB", (W, H))
px = img.load()
for y in range(H):
    t = y / H
    r = int(ORANGE_TOP[0] + (ORANGE_BOT[0] - ORANGE_TOP[0]) * t)
    g = int(ORANGE_TOP[1] + (ORANGE_BOT[1] - ORANGE_TOP[1]) * t)
    b = int(ORANGE_TOP[2] + (ORANGE_BOT[2] - ORANGE_TOP[2]) * t)
    for x in range(W):
        px[x, y] = (r, g, b)
# vignette
vig = Image.new("L", (W, H), 0)
vd = ImageDraw.Draw(vig)
vd.ellipse([-W*0.25, -H*0.15, W*1.25, H*1.15], fill=40)
vig = vig.filter(ImageFilter.GaussianBlur(160 * S))
dark = Image.new("RGB", (W, H), (150, 50, 22))
img = Image.composite(img, dark, vig)

# chalk layer (separate RGBA so we can use real alpha compositing)
layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(layer)
base = ImageDraw.Draw(img)

def tracked(draw, cx, y, text, fnt, tracking, fill):
    tr = tracking * S
    widths = [draw.textlength(c, font=fnt) for c in text]
    total = sum(widths) + tr * (len(text) - 1)
    x = cx - total / 2
    for c, w in zip(text, widths):
        draw.text((x, y), c, font=fnt, fill=fill); x += w + tr

def wrap(draw, text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

cx = W // 2

def dashed(pts, dash, gap, width, fill):
    """Draw a dashed polyline through pts (list of (x,y))."""
    carry = 0.0
    drawing = True
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        seg = math.hypot(x1 - x0, y1 - y0)
        if seg == 0: continue
        ux, uy = (x1 - x0) / seg, (y1 - y0) / seg
        pos = 0.0
        while pos < seg:
            span = (dash if drawing else gap) - carry
            end = min(pos + span, seg)
            if drawing:
                d.line([(x0 + ux*pos, y0 + uy*pos), (x0 + ux*end, y0 + uy*end)],
                       fill=fill, width=width)
            consumed = end - pos
            carry = 0.0 if consumed >= span else carry + consumed
            if consumed >= span:
                drawing = not drawing
            pos = end

def arrowhead(tip, ang, size, fill):
    l = (tip[0] - size*math.cos(ang - 0.42), tip[1] - size*math.sin(ang - 0.42))
    r = (tip[0] - size*math.cos(ang + 0.42), tip[1] - size*math.sin(ang + 0.42))
    d.polygon([tip, l, r], fill=fill)

def node_O(cx0, cy0, r, w):
    d.ellipse([cx0-r, cy0-r, cx0+r, cy0+r], outline=CHALK, width=w)

def node_X(cx0, cy0, r, w):
    d.line([(cx0-r, cy0-r), (cx0+r, cy0+r)], fill=CHALK, width=w)
    d.line([(cx0-r, cy0+r), (cx0+r, cy0-r)], fill=CHALK, width=w)

# ---------- HERO: the play ----------
# A big looping "retro cycle" arrow (looking back → iterate) plus routes & players.
lcx, lcy = cx, 1640 * S          # loop centre
ra, rb = 360 * S, 300 * S        # ellipse radii
# build ellipse points, leave a gap where the arrowhead lands
start_deg, end_deg = -60, 255    # open loop
pts = []
for deg in range(start_deg, end_deg + 1, 3):
    a = math.radians(deg)
    pts.append((lcx + ra*math.cos(a), lcy + rb*math.sin(a)))
dashed(pts, 30*S, 22*S, 9*S, CHALK)
# arrowhead at the loop's open end, tangent direction
a_end = math.radians(end_deg)
tip = (lcx + ra*math.cos(a_end), lcy + rb*math.sin(a_end))
tang = math.atan2(rb*math.cos(a_end), -ra*math.sin(a_end))   # d/dtheta of ellipse
arrowhead(tip, tang, 46*S, CHALK)

# straight "pass" routes crossing the board
def route(p0, p1, curve=0.0):
    # quadratic-ish via midpoint offset
    mx, my = (p0[0]+p1[0])/2, (p0[1]+p1[1])/2
    nx, ny = -(p1[1]-p0[1]), (p1[0]-p0[0])
    nlen = math.hypot(nx, ny) or 1
    mx += nx/nlen*curve; my += ny/nlen*curve
    seg = [ (p0[0]*(1-t)**2 + 2*mx*(1-t)*t + p1[0]*t**2,
             p0[1]*(1-t)**2 + 2*my*(1-t)*t + p1[1]*t**2) for t in [i/24 for i in range(25)] ]
    dashed(seg, 26*S, 18*S, 7*S, (247,242,230,225))
    # arrowhead
    q0, q1 = seg[-2], seg[-1]
    arrowhead(q1, math.atan2(q1[1]-q0[1], q1[0]-q0[0]), 34*S, (247,242,230,225))

route((lcx - 520*S, 1360*S), (lcx - 40*S, 1180*S), curve=90*S)
route((lcx + 520*S, 1360*S), (lcx + 90*S, 1120*S), curve=-110*S)
route((lcx - 300*S, 2060*S), (lcx + 260*S, 2040*S), curve=120*S)

# players / markers around the play
node_O(lcx - 520*S, 1360*S, 40*S, 8*S)
node_O(lcx + 520*S, 1360*S, 40*S, 8*S)
node_X(lcx - 300*S, 2060*S, 38*S, 9*S)
node_X(lcx + 260*S, 2040*S, 38*S, 9*S)
# the ball / focal dot in the loop centre
d.ellipse([lcx-26*S, lcy-26*S, lcx+26*S, lcy+26*S], fill=CHALK)
# small "chalk" tick marks / notes dots scattered
for (mx, my) in [(lcx-430*S,1720*S),(lcx+400*S,1680*S),(lcx-120*S,2120*S)]:
    d.ellipse([mx-9*S,my-9*S,mx+9*S,my+9*S], fill=(247,242,230,180))

# composite chalk layer down
img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
base = ImageDraw.Draw(img)

# ---------- type ----------
# keyline frame
m = 66 * S
base.rectangle([m, m, W - m, H - m], outline=(247,242,230), width=3 * S)
m2 = m + 12 * S
base.rectangle([m2, m2, W - m2, H - m2], outline=(247,242,230), width=1 * S)

# kicker chip
tracked(base, cx, 250 * S, "A FUN, PRACTICAL FIELD GUIDE", f_kick, 8, (252, 226, 200))
base.line([cx - 150 * S, 220 * S, cx + 150 * S, 220 * S], fill=CHALK, width=2 * S)

# title
base.text((cx, 470 * S), "THE RETRO", font=f_title, fill=CHALK, anchor="mm")
base.text((cx, 650 * S), "PLAYBOOK", font=f_title, fill=CHALK, anchor="mm")
base.line([cx - 90 * S, 770 * S, cx + 90 * S, 770 * S], fill=(255,255,255), width=6 * S)

# subtitle
y = 855 * S
for ln in wrap(base, "Using AI to Run Better Agile Retrospectives", f_sub, 1000 * S):
    base.text((cx, y), ln, font=f_sub, fill=(252, 232, 214), anchor="ma"); y += 64 * S

# author + imprint
base.line([cx - 120 * S, 2270 * S, cx + 120 * S, 2270 * S], fill=(247,242,230), width=2 * S)
tracked(base, cx, 2330 * S, "PRABHJIT MUTTI", f_auth, 10, CHALK)
tracked(base, cx, 2440 * S, "RETRO-GENERATOR.COM", f_imp, 6, (252, 226, 200))

final = img.resize((1600, 2560), Image.LANCZOS)
final.save("cover_play.png")
final.convert("RGB").save("cover_play.jpg", quality=92)
print("wrote cover_play.png / cover_play.jpg")
