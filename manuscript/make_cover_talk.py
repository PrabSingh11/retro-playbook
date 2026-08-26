#!/usr/bin/env python3
"""Cover concept F: the retro CONVERSATION — overlapping speech bubbles on cobalt,
one carrying an AI spark. cover_talk.png/.jpg."""
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = 2
W, H = 1600 * S, 2560 * S

COB_TOP = (28, 62, 140)
COB_BOT = (20, 44, 104)
CREAM   = (245, 242, 234)
WHITE   = (255, 255, 255)
GOLD    = (245, 190, 80)
MUTE    = (168, 186, 224)

FONTS = "/usr/share/fonts/opentype/urw-base35/"
def font(name, px): return ImageFont.truetype(FONTS + name, px * S)
f_title = font("URWGothic-Demi.otf", 172)
f_kick  = font("URWGothic-Book.otf", 33)
f_sub   = font("NimbusRoman-Italic.otf", 44)
f_auth  = font("URWGothic-Book.otf", 46)
f_imp   = font("NimbusSans-Regular.otf", 26)

img = Image.new("RGB", (W, H))
px = img.load()
for y in range(H):
    t = y / H
    row = tuple(int(COB_TOP[i] + (COB_BOT[i]-COB_TOP[i])*t) for i in range(3))
    for x in range(W): px[x, y] = row
cx = W // 2

def bubble(layer, x, y, w, h, fill, tail="left"):
    dd = ImageDraw.Draw(layer)
    r = 46 * S
    dd.rounded_rectangle([x, y, x+w, y+h], radius=r, fill=fill)
    if tail == "left":
        dd.polygon([(x + 70*S, y+h-6*S), (x + 60*S, y+h+56*S), (x + 150*S, y+h-6*S)], fill=fill)
    else:
        dd.polygon([(x+w - 70*S, y+h-6*S), (x+w - 60*S, y+h+56*S), (x+w - 150*S, y+h-6*S)], fill=fill)

# --- bubble cluster (lower half) with soft shadow ---
shadow = Image.new("RGBA", (W, H), (0,0,0,0))
notes = Image.new("RGBA", (W, H), (0,0,0,0))

# each: (x, y, w, h, fill, tail, dotcolor)
specs = [
    (300*S, 1360*S, 560*S, 300*S, CREAM, "left",  (72,150,168)),
    (760*S, 1520*S, 520*S, 270*S, CREAM, "right", (255,120,96)),
    (360*S, 1760*S, 480*S, 250*S, CREAM, "left",  (120,180,96)),
    (820*S, 1820*S, 540*S, 300*S, GOLD,  "right", None),   # the AI bubble
]
for (x,y,w,h,fill,tail,dot) in specs:
    bubble(shadow, x+10*S, y+16*S, w, h, (0,0,20,120), tail)
shadow = shadow.filter(ImageFilter.GaussianBlur(16*S))
img = Image.alpha_composite(img.convert("RGBA"), shadow)

for (x,y,w,h,fill,tail,dot) in specs:
    bubble(notes, x, y, w, h, fill, tail)
img = Image.alpha_composite(img, notes).convert("RGB")
d = ImageDraw.Draw(img)

# content inside bubbles: three "text" lines; AI bubble gets a spark + dots
for (x,y,w,h,fill,tail,dot) in specs:
    if fill == GOLD:
        # AI spark
        sx, sy = x + w*0.30, y + h*0.42
        for ang, ln in [(0,52),(90,52),(180,52),(270,52),(45,32),(135,32),(225,32),(315,32)]:
            a = math.radians(ang)
            d.line([(sx,sy),(sx+ln*S*math.cos(a), sy+ln*S*math.sin(a))], fill=(60,44,10), width=6*S)
        d.ellipse([sx-20*S,sy-20*S,sx+20*S,sy+20*S], fill=(60,44,10))
        for i in range(2):
            ly = y + h*0.62 + i*46*S
            d.line([(x+90*S, ly), (x+w-90*S, ly)], fill=(120,90,24), width=8*S)
    else:
        d.ellipse([x+70*S, y+62*S, x+118*S, y+110*S], fill=dot)   # avatar dot
        for i in range(3):
            ly = y + 80*S + i*52*S
            ln_w = w - 220*S if i < 2 else w - 320*S
            d.line([(x+150*S, ly), (x+150*S+ln_w, ly)], fill=(200,204,196), width=9*S)

def tracked(cxx, y, text, fnt, tracking, fill):
    tr = tracking*S
    widths=[d.textlength(c,font=fnt) for c in text]
    total=sum(widths)+tr*(len(text)-1); x=cxx-total/2
    for c,w in zip(text,widths): d.text((x,y),c,font=fnt,fill=fill); x+=w+tr

def wrap(text, fnt, maxw):
    words,lines,cur=text.split(),[],""
    for w in words:
        t=(cur+" "+w).strip()
        if d.textlength(t,font=fnt)<=maxw: cur=t
        else: lines.append(cur); cur=w
    if cur: lines.append(cur)
    return lines

# frame + type
m = 66*S
d.rectangle([m,m,W-m,H-m], outline=(120,150,210), width=3*S)
d.rectangle([m+12*S,m+12*S,W-m-12*S,H-m-12*S], outline=(84,116,180), width=1*S)

tracked(cx, 250*S, "A FUN, PRACTICAL FIELD GUIDE", f_kick, 8, MUTE)
d.line([cx-150*S, 220*S, cx+150*S, 220*S], fill=GOLD, width=3*S)
d.text((cx, 480*S), "THE RETRO", font=f_title, fill=CREAM, anchor="mm")
d.text((cx, 660*S), "PLAYBOOK", font=f_title, fill=GOLD, anchor="mm")
y=810*S
for ln in wrap("Using AI to Run Better Agile Retrospectives", f_sub, 1000*S):
    d.text((cx,y), ln, font=f_sub, fill=(210,222,244), anchor="ma"); y+=64*S

d.line([cx-120*S, 2300*S, cx+120*S, 2300*S], fill=(120,150,210), width=2*S)
tracked(cx, 2360*S, "PRAB MUTTI", f_auth, 10, CREAM)
tracked(cx, 2470*S, "RETRO-GENERATOR.COM", f_imp, 6, MUTE)

final = img.resize((1600,2560), Image.LANCZOS)
final.save("cover_talk.png")
final.convert("RGB").save("cover_talk.jpg", quality=92)
print("wrote cover_talk.png / cover_talk.jpg")
