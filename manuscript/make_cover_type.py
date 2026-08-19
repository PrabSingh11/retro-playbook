#!/usr/bin/env python3
"""Cover concept E: editorial BIG-TYPE, left-aligned, deep plum + coral accent.
No illustration — type and colour do the work. cover_type.png/.jpg."""
from PIL import Image, ImageDraw, ImageFont

S = 2
W, H = 1600 * S, 2560 * S

PLUM_TOP = (52, 33, 66)
PLUM_BOT = (38, 24, 50)
CREAM    = (244, 240, 232)
CORAL    = (255, 104, 92)
GOLD     = (240, 186, 82)
MUTE     = (176, 158, 186)
ACCENTS  = [(72,150,168),(255,104,92),(120,180,96),(240,186,82),(190,140,220)]

FONTS = "/usr/share/fonts/opentype/urw-base35/"
def font(name, px): return ImageFont.truetype(FONTS + name, px * S)
f_huge = font("URWGothic-Demi.otf", 210)
f_the  = font("URWGothic-Book.otf", 58)
f_kick = font("URWGothic-Book.otf", 33)
f_sub  = font("NimbusRoman-Italic.otf", 46)
f_auth = font("URWGothic-Book.otf", 46)
f_imp  = font("NimbusSans-Regular.otf", 26)

img = Image.new("RGB", (W, H))
px = img.load()
for y in range(H):
    t = y / H
    px_row = tuple(int(PLUM_TOP[i] + (PLUM_BOT[i]-PLUM_TOP[i])*t) for i in range(3))
    for x in range(W): px[x, y] = px_row
d = ImageDraw.Draw(img)

LX = 150 * S       # left margin
RX = W - 150 * S

def tracked(x, y, text, fnt, tracking, fill):
    for c in text:
        d.text((x, y), c, font=fnt, fill=fill); x += d.textlength(c, font=fnt) + tracking*S

# kicker
tracked(LX, 230*S, "A FUN, PRACTICAL FIELD GUIDE", f_kick, 8, MUTE)
d.line([LX, 300*S, LX + 300*S, 300*S], fill=CORAL, width=4*S)

# --- big stacked title, left aligned ---
d.text((LX - 6*S, 430*S), "THE", font=f_the, fill=MUTE)
d.text((LX - 10*S, 520*S), "RETRO", font=f_huge, fill=CREAM)
d.text((LX - 10*S, 730*S), "PLAY", font=f_huge, fill=CREAM)
d.text((LX - 10*S, 940*S), "BOOK", font=f_huge, fill=CORAL)

# subtitle
d.multiline_text((LX, 1240*S), "Using AI to Run Better\nAgile Retrospectives",
                 font=f_sub, fill=(214, 200, 222), spacing=18*S)

# --- motif: a stacked "sprint timeline" of colour bars, lower area ---
bar_x = LX
bar_y = 1740 * S
bar_h = 44 * S
gap   = 34 * S
widths = [560, 700, 470, 640, 520]
for i, (c, bw) in enumerate(zip(ACCENTS, widths)):
    y0 = bar_y + i * (bar_h + gap)
    d.rounded_rectangle([bar_x, y0, bar_x + bw*S, y0 + bar_h], radius=bar_h//2, fill=c)
    # small end cap dot
    d.ellipse([bar_x + bw*S + 26*S, y0 + bar_h/2 - 9*S, bar_x + bw*S + 26*S + 18*S, y0 + bar_h/2 + 9*S], fill=MUTE)

# author + imprint (bottom-left, editorial)
d.line([LX, 2320*S, LX + 120*S, 2320*S], fill=CORAL, width=3*S)
tracked(LX, 2360*S, "PRABHJIT MUTTI", f_auth, 6, CREAM)
tracked(LX, 2460*S, "RETRO-GENERATOR.COM", f_imp, 5, MUTE)

final = img.resize((1600, 2560), Image.LANCZOS)
final.save("cover_type.png")
final.convert("RGB").save("cover_type.jpg", quality=92)
print("wrote cover_type.png / cover_type.jpg")
