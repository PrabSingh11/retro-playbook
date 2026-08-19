#!/usr/bin/env python3
"""Bold alt cover (dark, high-contrast) -> cover-bold.png/.jpg. Separate from the cream cover."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

S = 2
W, H = 1600 * S, 2560 * S
HERE = Path(__file__).resolve().parent

# --- dark palette ---
BG      = (26, 42, 36)       # deep ink-green
CREAM   = (243, 241, 231)
SAGE    = (150, 166, 156)    # muted light for kicker/imprint
GOLD    = (230, 178, 74)     # accent for the AI subtitle (pops on dark)
LINE    = (58, 74, 68)
# brightened sticky-note accents so they glow on the dark ground
NOTES   = [(78,150,170),(219,106,62),(110,154,80),(138,116,168),(206,150,52)]

FONTS = "/usr/share/fonts/opentype/urw-base35/"
def font(name, px): return ImageFont.truetype(FONTS + name, px * S)
f_title = font("URWGothic-Demi.otf", 150)
f_kick  = font("URWGothic-Book.otf", 33)
f_sub   = font("URWGothic-DemiOblique.otf", 60)   # bolder subtitle for the USP
f_auth  = font("URWGothic-Book.otf", 46)
f_imp   = font("NimbusSans-Regular.otf", 26)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

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

# keyline frame (subtle, on dark)
m = 66 * S
d.rectangle([m, m, W - m, H - m], outline=LINE, width=3 * S)
m2 = m + 12 * S
d.rectangle([m2, m2, W - m2, H - m2], outline=LINE, width=1 * S)

# kicker
d.line([cx - 150 * S, 210 * S, cx + 150 * S, 210 * S], fill=CREAM, width=2 * S)
tracked(d, cx, 250 * S, "A PRACTICAL, NO-JARGON FIELD GUIDE", f_kick, 6, SAGE)

# title
d.text((cx, 470 * S), "THE RETRO", font=f_title, fill=CREAM, anchor="mm")
d.text((cx, 640 * S), "PLAYBOOK", font=f_title, fill=CREAM, anchor="mm")

# gold rule + subtitle (the USP, in gold, larger/bolder)
d.line([cx - 95 * S, 760 * S, cx + 95 * S, 760 * S], fill=GOLD, width=6 * S)
y = 838 * S
for ln in wrap(d, "Using AI to Run Better Agile Retrospectives", f_sub, 940 * S):
    d.text((cx, y), ln, font=f_sub, fill=GOLD, anchor="ma"); y += 86 * S

# hero: five glowing sticky notes
def sticky(color, deg):
    side, pad = 300 * S, 120 * S
    tile = Image.new("RGBA", (side + pad, side + pad), (0, 0, 0, 0))
    td = ImageDraw.Draw(tile)
    x0 = y0 = pad // 2
    td.rounded_rectangle([x0, y0, x0 + side, y0 + side], radius=10 * S, fill=color + (255,))
    tw, th = 108 * S, 30 * S
    td.rectangle([x0 + side/2 - tw/2, y0 - th/2, x0 + side/2 + tw/2, y0 + th/2], fill=(243, 241, 231, 140))
    for i in range(3):
        ly = y0 + side * 0.42 + i * 46 * S
        td.line([x0 + 44 * S, ly, x0 + side - 44 * S, ly], fill=(255, 255, 255, 110), width=4 * S)
    return tile.rotate(deg, expand=True, resample=Image.BICUBIC)

cy, step = 1520 * S, 250 * S
start_x = cx - step * 2
for i, (color, deg) in enumerate(zip(NOTES, [-9, 5, -3, 7, -6])):
    note = sticky(color, deg)
    nx = int(start_x + i * step - note.width / 2)
    ny = int(cy - note.height / 2 + (18 * S if i % 2 else -18 * S))
    # soft glow behind each note
    alpha = note.split()[3]
    glow = Image.new("RGBA", note.size, (0, 0, 0, 0))
    glow.paste(color + (110,), (0, 0), alpha)
    glow = glow.filter(ImageFilter.GaussianBlur(16 * S))
    img.paste(glow, (nx, ny), glow)
    img.paste(note, (nx, ny), note)

# author + imprint
d.line([cx - 120 * S, 2210 * S, cx + 120 * S, 2210 * S], fill=LINE, width=2 * S)
tracked(d, cx, 2270 * S, "PRABHJIT MUTTI", f_auth, 10, CREAM)
tracked(d, cx, 2380 * S, "RETRO-GENERATOR.COM", f_imp, 6, SAGE)

final = img.resize((1600, 2560), Image.LANCZOS)
final.save(HERE / "cover-bold.png")
final.convert("RGB").save(HERE / "cover-bold.jpg", quality=92)
print("wrote cover-bold.png / cover-bold.jpg")
