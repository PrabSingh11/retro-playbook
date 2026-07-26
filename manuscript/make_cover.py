#!/usr/bin/env python3
"""Render the Kindle cover (1600x2560) in the book's palette, via Pillow at 2x supersample."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

S = 2                       # supersample factor
W, H = 1600 * S, 2560 * S
HERE = Path(__file__).resolve().parent

# --- palette (from book.css) ---
PAPER   = (237, 236, 226)
PAPERDP = (225, 223, 208)
INK     = (36, 53, 47)
INKSOFT = (91, 102, 93)
INKFAINT= (139, 145, 136)
RULE    = (201, 196, 172)
ACCENTS = [(63,118,132),(193,90,52),(82,113,63),(100,81,126),(169,120,31)]  # teal ember moss plum gold

FONTS = "/usr/share/fonts/opentype/urw-base35/"
def font(name, px): return ImageFont.truetype(FONTS + name, px * S)
f_title = font("URWGothic-Demi.otf", 150)
f_kick  = font("URWGothic-Book.otf", 33)
f_sub   = font("NimbusRoman-Italic.otf", 62)
f_auth  = font("URWGothic-Book.otf", 46)
f_imp   = font("NimbusSans-Regular.otf", 26)

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

def tracked(draw, cx, y, text, fnt, tracking, fill):
    """draw letter-spaced text centered on cx (top y)."""
    tr = tracking * S
    widths = [draw.textlength(c, font=fnt) for c in text]
    total = sum(widths) + tr * (len(text) - 1)
    x = cx - total / 2
    for c, w in zip(text, widths):
        draw.text((x, y), c, font=fnt, fill=fill)
        x += w + tr

def wrap(draw, text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

cx = W // 2

# --- framing keyline ---
m = 66 * S
d.rectangle([m, m, W - m, H - m], outline=RULE, width=3 * S)
m2 = m + 12 * S
d.rectangle([m2, m2, W - m2, H - m2], outline=RULE, width=1 * S)

# --- kicker ---
tracked(d, cx, 250 * S, "A FUN, PRACTICAL FIELD GUIDE", f_kick, 8, INKSOFT)
d.line([cx - 150 * S, 210 * S, cx + 150 * S, 210 * S], fill=INK, width=2 * S)

# --- title (two lines) ---
d.text((cx, 470 * S), "THE RETRO", font=f_title, fill=INK, anchor="mm")
d.text((cx, 640 * S), "PLAYBOOK", font=f_title, fill=INK, anchor="mm")

# short rule under title
d.line([cx - 90 * S, 760 * S, cx + 90 * S, 760 * S], fill=ACCENTS[0], width=5 * S)

# --- subtitle ---
sub = "Using AI to Run Better Agile Retrospectives"
y = 838 * S
for ln in wrap(d, sub, f_sub, 900 * S):     # wraps to two balanced lines at this size
    d.text((cx, y), ln, font=f_sub, fill=INK, anchor="ma")
    y += 88 * S

# --- hero motif: five sticky notes (the five color-coded parts) ---
def sticky(color, deg):
    side = 300 * S
    pad = 120 * S
    tile = Image.new("RGBA", (side + pad, side + pad), (0, 0, 0, 0))
    td = ImageDraw.Draw(tile)
    x0 = y0 = pad // 2
    td.rounded_rectangle([x0, y0, x0 + side, y0 + side], radius=10 * S, fill=color + (255,))
    # tape strip
    tw, th = 108 * S, 30 * S
    td.rectangle([x0 + side/2 - tw/2, y0 - th/2, x0 + side/2 + tw/2, y0 + th/2],
                 fill=(246, 245, 236, 150))
    # faint "writing" lines
    for i in range(3):
        ly = y0 + side * 0.42 + i * 46 * S
        td.line([x0 + 44 * S, ly, x0 + side - 44 * S, ly], fill=(255, 255, 255, 90), width=4 * S)
    return tile.rotate(deg, expand=True, resample=Image.BICUBIC)

notes = []
for color, deg in zip(ACCENTS, [-9, 5, -3, 7, -6]):
    notes.append(sticky(color, deg))

cy = 1520 * S
step = 250 * S
start_x = cx - step * 2
for i, note in enumerate(notes):
    nx = int(start_x + i * step - note.width / 2)
    ny = int(cy - note.height / 2 + (18 * S if i % 2 else -18 * S))
    # soft shadow
    alpha = note.split()[3]
    sh = Image.new("RGBA", note.size, (0, 0, 0, 0))
    sh.paste((30, 40, 35, 120), (0, 0), alpha)
    sh = sh.filter(ImageFilter.GaussianBlur(10 * S))
    img.paste(sh, (nx + 8 * S, ny + 12 * S), sh)
    img.paste(note, (nx, ny), note)

# --- author + imprint ---
d.line([cx - 120 * S, 2210 * S, cx + 120 * S, 2210 * S], fill=RULE, width=2 * S)
tracked(d, cx, 2270 * S, "PRAB MUTTI", f_auth, 10, INK)
tracked(d, cx, 2380 * S, "RETRO-GENERATOR.COM", f_imp, 6, INKFAINT)

# --- downsample & save ---
final = img.resize((1600, 2560), Image.LANCZOS)
final.save(HERE / "cover.png")
final.convert("RGB").save(HERE / "cover.jpg", quality=92)
print("wrote cover.png and cover.jpg (1600x2560)")
