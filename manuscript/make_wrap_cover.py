#!/usr/bin/env python3
"""Render the KDP paperback WRAP cover (back + spine + front) in the book palette.

Sized for 6x9", 246-page interior on WHITE paper:
  spine  = 246 * 0.002252" = 0.554"
  wrap   = 0.125 bleed + 6 back + 0.554 spine + 6 front + 0.125 bleed = 12.804" x 9.25"
  output = 3841 x 2775 px @ 300 DPI  (rendered 2x, downsampled)

If the page count changes, edit PAGES below and rerun.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

# ---- trim / bleed / spine geometry -------------------------------------
PAGES        = 218
PAGE_THICK   = 0.002252          # white paper, inches per page (KDP)
TRIM_W, TRIM_H = 6.0, 9.0
BLEED        = 0.125
SPINE        = PAGES * PAGE_THICK        # 0.554"
DPI          = 300
S            = 2                          # supersample

WRAP_W = 2 * BLEED + 2 * TRIM_W + SPINE   # 12.804"
WRAP_H = TRIM_H + 2 * BLEED               # 9.25"

def I(inch):                              # inches -> supersampled px
    return round(inch * DPI * S)

W, H = I(WRAP_W), I(WRAP_H)
HERE = Path(__file__).resolve().parent

# panel x-edges (inches from left)
BACK_X0  = BLEED
BACK_X1  = BLEED + TRIM_W
SPINE_X0 = BACK_X1
SPINE_X1 = BACK_X1 + SPINE
FRONT_X0 = SPINE_X1
FRONT_X1 = SPINE_X1 + TRIM_W
TOP, BOT = BLEED, BLEED + TRIM_H

# ---- palette (book.css) ------------------------------------------------
PAPER   = (237, 236, 226)
PAPERDP = (225, 223, 208)
INK     = (36, 53, 47)
INKSOFT = (91, 102, 93)
INKFAINT= (139, 145, 136)
RULE    = (201, 196, 172)
ACCENTS = [(63,118,132),(193,90,52),(82,113,63),(100,81,126),(169,120,31)]  # teal ember moss plum gold

FONTS = "/usr/share/fonts/opentype/urw-base35/"
def font(name, pt):  # pt at 300dpi
    return ImageFont.truetype(FONTS + name, int(pt * S))

f_title = font("URWGothic-Demi.otf", 150)
f_kick  = font("URWGothic-Book.otf", 33)
f_sub   = font("NimbusRoman-Italic.otf", 60)
f_auth  = font("URWGothic-Book.otf", 46)
f_imp   = font("NimbusSans-Regular.otf", 26)
f_bhead = font("URWGothic-Demi.otf", 74)
f_hook  = font("URWGothic-Demi.otf", 52)
f_emph  = font("NimbusRoman-Italic.otf", 44)
f_inside= font("URWGothic-Demi.otf", 42)
f_body  = font("NimbusRoman-Regular.otf", 38)
f_bul   = font("URWGothic-Book.otf", 37)
f_bio   = font("NimbusRoman-Italic.otf", 33)
f_spine = font("URWGothic-Demi.otf", 66)
f_spauth= font("URWGothic-Book.otf", 40)

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# ---- helpers -----------------------------------------------------------
def tracked(draw, cx, y, text, fnt, tracking, fill, top=True):
    tr = tracking * S
    widths = [draw.textlength(c, font=fnt) for c in text]
    total = sum(widths) + tr * (len(text) - 1)
    x = cx - total / 2
    anchor = "la" if top else "lm"
    for c, w in zip(text, widths):
        draw.text((x, y), c, font=fnt, fill=fill, anchor=anchor)
        x += w + tr

def wrap_lines(draw, text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def para(draw, x, y, text, fnt, maxw, fill, lh):
    for ln in wrap_lines(draw, text, fnt, maxw):
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y

def keyline(x0, y0, x1, y1):
    d.rectangle([I(x0), I(y0), I(x1), I(y1)], outline=RULE, width=3 * S)
    o = 0.02
    d.rectangle([I(x0+o), I(y0+o), I(x1-o), I(y1-o)], outline=RULE, width=1 * S)

# ============================================================ FRONT PANEL
fcx = I((FRONT_X0 + FRONT_X1) / 2)
FM = 0.30                                   # keyline inset from trim
keyline(FRONT_X0+FM, TOP+FM, FRONT_X1-FM, BOT-FM)

# kicker
d.line([fcx - I(0.55), I(TOP+0.86), fcx + I(0.55), I(TOP+0.86)], fill=INK, width=2*S)
tracked(d, fcx, I(TOP+0.95), "A PRACTICAL, NO-JARGON FIELD GUIDE", f_kick, 6, INKSOFT)

# title (two lines)
d.text((fcx, I(TOP+1.85)), "THE RETRO", font=f_title, fill=INK, anchor="mm")
d.text((fcx, I(TOP+2.55)), "PLAYBOOK", font=f_title, fill=INK, anchor="mm")
d.line([fcx - I(0.33), I(TOP+3.05), fcx + I(0.33), I(TOP+3.05)], fill=ACCENTS[0], width=5*S)

# subtitle
y = I(TOP+3.35)
for ln in wrap_lines(d, "Using AI to Run Better Agile Retrospectives", f_sub, I(3.6)):
    d.text((fcx, y), ln, font=f_sub, fill=INK, anchor="ma")
    y += I(0.36)

# hero: five sticky notes (the five parts)
def sticky(color, deg):
    side, pad = I(1.15), I(0.5)
    tile = Image.new("RGBA", (side + pad, side + pad), (0,0,0,0))
    td = ImageDraw.Draw(tile)
    x0 = y0 = pad // 2
    td.rounded_rectangle([x0, y0, x0+side, y0+side], radius=I(0.04), fill=color+(255,))
    tw, th = I(0.42), I(0.12)
    td.rectangle([x0+side/2-tw/2, y0-th/2, x0+side/2+tw/2, y0+th/2], fill=(246,245,236,150))
    for i in range(3):
        ly = y0 + side*0.42 + i*I(0.17)
        td.line([x0+I(0.17), ly, x0+side-I(0.17), ly], fill=(255,255,255,90), width=4*S)
    return tile.rotate(deg, expand=True, resample=Image.BICUBIC)

cy = I(TOP+5.75)
step = I(0.96)
start_x = fcx - step*2
for i, deg in enumerate([-9,5,-3,7,-6]):
    note = sticky(ACCENTS[i], deg)
    nx = int(start_x + i*step - note.width/2)
    ny = int(cy - note.height/2 + (I(0.07) if i%2 else -I(0.07)))
    alpha = note.split()[3]
    sh = Image.new("RGBA", note.size, (0,0,0,0))
    sh.paste((30,40,35,120), (0,0), alpha)
    sh = sh.filter(ImageFilter.GaussianBlur(10*S))
    img.paste(sh, (nx+I(0.03), ny+I(0.045)), sh)
    img.paste(note, (nx, ny), note)

# author + imprint
d.line([fcx - I(0.46), I(TOP+7.75), fcx + I(0.46), I(TOP+7.75)], fill=RULE, width=2*S)
tracked(d, fcx, I(TOP+7.95), "PRAB MUTTI", f_auth, 10, INK)
tracked(d, fcx, I(TOP+8.42), "RETRO-GENERATOR.COM", f_imp, 6, INKFAINT)

# ============================================================ SPINE
# light spine (matches paper field); title rotated, author at foot.
sp_w, sp_h = I(SPINE), I(TRIM_H)
spine_img = Image.new("RGBA", (sp_h, sp_w), (0,0,0,0))   # drawn horizontally, rotated later
sd = ImageDraw.Draw(spine_img)
# title runs along spine, centered
t = "THE RETRO PLAYBOOK"
tw = sd.textlength(t, font=f_spine)
sd.text(((sp_h - tw)/2, sp_w*0.5), t, font=f_spine, fill=INK, anchor="lm")
# author near the foot end (will be bottom after rotation)
aw = sd.textlength("PRAB MUTTI", font=f_spauth)
sd.text((sp_h - aw - I(0.35), sp_w*0.5), "PRAB MUTTI", font=f_spauth, fill=INKSOFT, anchor="lm")
spine_rot = spine_img.rotate(90, expand=True, resample=Image.BICUBIC)
img.paste(spine_rot, (I(SPINE_X0), I(TOP)), spine_rot)
# hairline spine folds (guide only-ish, very light)
d.line([I(SPINE_X0), I(TOP+0.5), I(SPINE_X0), I(BOT-0.5)], fill=RULE, width=1*S)
d.line([I(SPINE_X1), I(TOP+0.5), I(SPINE_X1), I(BOT-0.5)], fill=RULE, width=1*S)

# ============================================================ BACK PANEL
bx0, bx1 = BACK_X0, BACK_X1
keyline(bx0+FM, TOP+FM, bx1-FM, BOT-FM)
TXX = bx0 + 0.62                 # text left
TXR = bx1 - 0.62                 # text right
TW  = TXR - TXX                  # text column width (inches)

by = I(TOP+0.62)

# hook headline
by = para(d, I(TXX), by,
          "Every Scrum retrospective book you've read was written for a world "
          "that no longer exists.", f_hook, I(TW), INK, I(0.30)); by += I(0.18)

# punchy triple (emphasis)
by = para(d, I(TXX), by,
          "Same sticky notes. Same three questions. Same disengaged team.",
          f_emph, I(TW), INKSOFT, I(0.25)); by += I(0.20)

# main pitch
by = para(d, I(TXX), by,
          "AI has changed the game — and The Retro Playbook shows you exactly how to "
          "use it to run retrospectives your team actually wants to show up for. Real "
          "prompts. Real tools. Real facilitation techniques. Not theory.",
          f_body, I(TW), INK, I(0.185)); by += I(0.14)

# second pitch paragraph
by = para(d, I(TXX), by,
          "Flip it open five minutes before your stand-up and steal a ready-to-run "
          "format, an icebreaker that won't make anyone cringe, or a facilitation move "
          "for the room you're actually walking into. Then let AI handle the prep, the "
          "clustering and the follow-up while you focus on the conversation.",
          f_body, I(TW), INK, I(0.185)); by += I(0.16)

# Inside:
d.text((I(TXX), by), "Inside:", font=f_inside, fill=INK); by += I(0.32)
bullets = [
    "30+ retrospective formats, ready to run",
    "The modern AI toolkit — what's worth using, what to skip",
    "Core facilitation skills for honest, blame-free conversations",
    "Ready-to-use templates",
    "29 icebreakers you can run cold, no prep needed",
    "AI prompts for every stage of the retro",
]
for i, b in enumerate(bullets):
    d.rounded_rectangle([I(TXX), by+I(0.035), I(TXX)+I(0.12), by+I(0.155)], radius=I(0.02),
                        fill=ACCENTS[i % len(ACCENTS)])
    for ln in wrap_lines(d, b, f_bul, I(TW-0.28)):
        d.text((I(TXX+0.28), by), ln, font=f_bul, fill=INK); by += I(0.23)
    by += I(0.055)
by += I(0.16)

# closing line
by = para(d, I(TXX), by,
          "Whether you're new to Scrum Mastery or have been running retros for years, "
          "this book gets your team's next retrospective working — starting tomorrow.",
          f_body, I(TW), INK, I(0.185)); by += I(0.22)

# the one rule, emphasised (centered)
tracked(d, I((bx0+bx1)/2), by, "AI handles the paperwork.", f_emph, 0, INK); by += I(0.26)
tracked(d, I((bx0+bx1)/2), by, "Humans handle the talking.", f_emph, 0, INK); by += I(0.30)

print(f"  back-cover main copy ends at y={by/(DPI*S):.2f}in")

# KDP fixed barcode clear-zone: exactly 2.0 x 1.2", 0.25" from back-cover right
# trim edge and 0.5" from bottom trim edge. Pure white, NO border, NO label.
# Coords below are given from the bottom-left of the wrap (0,0); PIL's I() is
# top-left, so vertical values are flipped via WRAP_H - <dist-from-bottom>.
BC_LEFT, BC_RIGHT   = 3.875, 5.875               # from left edge
BC_BOTTOM, BC_TOP   = 0.625, 1.825               # from bottom edge
bw_x0, bw_x1 = BC_LEFT, BC_RIGHT
bw_y0, bw_y1 = WRAP_H - BC_TOP, WRAP_H - BC_BOTTOM   # top-left y (0.625->8.625 etc.)
d.rectangle([I(bw_x0), I(bw_y0), I(bw_x1), I(bw_y1)], fill=(255,255,255))

# author bio: bottom-left, in a column to the LEFT of the barcode, aligned to its top
bio_w = bw_x0 - 0.30 - TXX          # stop short of the barcode's left edge
d.line([I(TXX), I(bw_y0), I(TXX)+I(0.9), I(bw_y0)], fill=RULE, width=2*S)
para(d, I(TXX), I(bw_y0+0.16),
     "Prab Mutti is an agile leader with 10 years of delivery experience and the "
     "creator of retro-generator.com, a tool used by teams to create unique, "
     "interesting, AI-retrospectives.", f_bio, I(bio_w), INKSOFT, I(0.20))

# ---- downsample & save -------------------------------------------------
fw, fh = round(WRAP_W*DPI), round(WRAP_H*DPI)
final = img.resize((fw, fh), Image.LANCZOS)
final.save(HERE / "wrap-cover.png")
rgb = final.convert("RGB")
rgb.save(HERE / "wrap-cover.jpg", quality=94, dpi=(DPI, DPI))
# print-ready PDF at true physical size (KDP "upload your own cover")
rgb.save(HERE / "wrap-cover.pdf", "PDF", resolution=DPI)
print(f"wrote wrap-cover.png / .jpg / .pdf  ({fw}x{fh} px @ {DPI}dpi; "
      f"{WRAP_W:.3f}x{WRAP_H:.3f}in; spine {SPINE:.3f}in, {PAGES}pp)")
