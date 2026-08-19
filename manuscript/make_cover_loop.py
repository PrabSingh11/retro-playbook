#!/usr/bin/env python3
"""Cover concept D: charcoal + electric cyan, ONE clean sprint-loop arrow with an
AI spark. Bold type, high contrast, deliberate single focal image.
Writes cover_loop.png / cover_loop.jpg. Touches nothing else."""
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = 2
W, H = 1600 * S, 2560 * S

CHAR   = (18, 21, 27)          # near-black charcoal
CHAR_UP= (30, 35, 44)          # slightly lifted centre
CYAN   = (38, 214, 240)        # electric accent
CYAN_DK= (16, 150, 180)
WHITE  = (240, 244, 248)
MUTE   = (150, 160, 172)

FONTS = "/usr/share/fonts/opentype/urw-base35/"
def font(name, px): return ImageFont.truetype(FONTS + name, px * S)
f_title = font("URWGothic-Demi.otf", 176)
f_kick  = font("URWGothic-Book.otf", 33)
f_sub   = font("NimbusRoman-Italic.otf", 44)
f_auth  = font("URWGothic-Book.otf", 46)
f_imp   = font("NimbusSans-Regular.otf", 26)

# --- background: charcoal with a soft central lift ---
img = Image.new("RGB", (W, H), CHAR)
glow_bg = Image.new("L", (W, H), 0)
gd = ImageDraw.Draw(glow_bg)
gd.ellipse([W*0.05, H*0.42, W*0.95, H*0.86], fill=90)
glow_bg = glow_bg.filter(ImageFilter.GaussianBlur(220 * S))
lift = Image.new("RGB", (W, H), CHAR_UP)
img = Image.composite(lift, img, glow_bg)

cx = W // 2

# ---------- HERO: the sprint loop ----------
lcx, lcy = cx, 1660 * S
R = 360 * S
thick = 34 * S
# gap at the top for the arrowhead to break through
a_start, a_end = 292, 248        # PIL: 0=right, +clockwise; ~30deg gap centred on top(270)

# soft outer glow
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gdraw = ImageDraw.Draw(glow)
gdraw.arc([lcx-R, lcy-R, lcx+R, lcy+R], a_start, a_end + 360, fill=CYAN + (255,), width=thick + 26*S)
glow = glow.filter(ImageFilter.GaussianBlur(26 * S))
img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")

d = ImageDraw.Draw(img)
# crisp ring
d.arc([lcx-R, lcy-R, lcx+R, lcy+R], a_start, a_end + 360, fill=CYAN, width=thick)

# arrowhead at the end angle, tangent = clockwise direction (angle + 90)
ar = math.radians(a_end)
tip_ang = a_end + 90
tr = math.radians(tip_ang)
tipx = lcx + R*math.cos(ar) + (thick*0.2)*math.cos(tr)
tipy = lcy + R*math.sin(ar) + (thick*0.2)*math.sin(tr)
ah = 62 * S
back = tr + math.pi
lft = (tipx + ah*math.cos(back - 0.5), tipy + ah*math.sin(back - 0.5))
rgt = (tipx + ah*math.cos(back + 0.5), tipy + ah*math.sin(back + 0.5))
d.polygon([(tipx, tipy), lft, rgt], fill=CYAN)

# --- AI spark node sitting on the ring (top-left, where the loop "learns") ---
sp_ang = math.radians(210)
spx = lcx + R*math.cos(sp_ang)
spy = lcy + R*math.sin(sp_ang)
# glow dot
sg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(sg).ellipse([spx-40*S, spy-40*S, spx+40*S, spy+40*S], fill=WHITE + (255,))
sg = sg.filter(ImageFilter.GaussianBlur(22 * S))
img = Image.alpha_composite(img.convert("RGBA"), sg).convert("RGB")
d = ImageDraw.Draw(img)
d.ellipse([spx-22*S, spy-22*S, spx+22*S, spy+22*S], fill=WHITE)
# four-point spark rays
for ang, ln in [(0, 66), (90, 66), (180, 66), (270, 66), (45, 40), (135, 40), (225, 40), (315, 40)]:
    a = math.radians(ang)
    d.line([(spx, spy), (spx + ln*S*math.cos(a), spy + ln*S*math.sin(a))], fill=WHITE, width=6*S)

# a couple of small nodes on the ring to imply "each sprint"
for deg in (30, 120, 340):
    a = math.radians(deg)
    nx, ny = lcx + R*math.cos(a), lcy + R*math.sin(a)
    d.ellipse([nx-13*S, ny-13*S, nx+13*S, ny+13*S], fill=CHAR)
    d.ellipse([nx-13*S, ny-13*S, nx+13*S, ny+13*S], outline=WHITE, width=5*S)

# central label inside the loop
midf = font("URWGothic-Book.otf", 30)
mt = "ITERATE"
mw = d.textlength(mt, font=midf)
tr2 = 7 * S
x = lcx - (mw + tr2*(len(mt)-1)) / 2
for c in mt:
    d.text((x, lcy - 20*S), c, font=midf, fill=MUTE)
    x += d.textlength(c, font=midf) + tr2

def tracked(draw, cxx, y, text, fnt, tracking, fill):
    tr = tracking * S
    widths = [draw.textlength(c, font=fnt) for c in text]
    total = sum(widths) + tr * (len(text) - 1)
    xx = cxx - total / 2
    for c, w in zip(text, widths):
        draw.text((xx, y), c, font=fnt, fill=fill); xx += w + tr

def wrap(draw, text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

# ---------- type ----------
tracked(d, cx, 250 * S, "A FUN, PRACTICAL FIELD GUIDE", f_kick, 8, MUTE)
d.line([cx - 150 * S, 220 * S, cx + 150 * S, 220 * S], fill=CYAN, width=3 * S)

# title — PLAYBOOK in cyan to pop
d.text((cx, 480 * S), "THE RETRO", font=f_title, fill=WHITE, anchor="mm")
d.text((cx, 680 * S), "PLAYBOOK", font=f_title, fill=CYAN, anchor="mm")

y = 830 * S
for ln in wrap(d, "Using AI to Run Better Agile Retrospectives", f_sub, 1000 * S):
    d.text((cx, y), ln, font=f_sub, fill=(206, 214, 222), anchor="ma"); y += 64 * S

# author + imprint
d.line([cx - 120 * S, 2300 * S, cx + 120 * S, 2300 * S], fill=(70, 80, 92), width=2 * S)
tracked(d, cx, 2360 * S, "PRABHJIT MUTTI", f_auth, 10, WHITE)
tracked(d, cx, 2470 * S, "RETRO-GENERATOR.COM", f_imp, 6, MUTE)

final = img.resize((1600, 2560), Image.LANCZOS)
final.save("cover_loop.png")
final.convert("RGB").save("cover_loop.jpg", quality=92)
print("wrote cover_loop.png / cover_loop.jpg")
