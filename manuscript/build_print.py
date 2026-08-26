#!/usr/bin/env python3
"""Build the print-ready 6x9" paperback interior PDF (KDP) from the website chapters.

Reuses build.clean() to strip web chrome and extract SVG diagrams, then adds
title page / copyright / dedication / part dividers / a page-numbered TOC, applies
book.css + activity.css + print.css (grayscale, mirrored margins), and renders with
WeasyPrint.

Run with the build venv:  .buildvenv/bin/python build_print.py
"""
import re, subprocess, sys, html
from pathlib import Path
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # reuse clean(), ROOT, CH

ROOT = build.ROOT
CH = build.CH
MAN = Path(__file__).resolve().parent

# ---- reading order: parts, chapters, interleaved "Your Turn" exercises, back matter
#   (kind, slug/path, display-number, title-override)
#   kind: part | ch | ex | bm
STRUCT = [
    ("part", "Part I",  "Retro Basics (Without the Boring Bits)", "gets you running a decent retro by chapter 3"),
    ("ch", "01-five-ways-retros-fail",   "1"),
    ("ch", "02-the-five-stage-recipe",   "2"),
    ("ex", "warm-up-questions",          "✎"),
    ("ch", "03-facilitation-101",        "3"),

    ("part", "Part II", "The Icebreaker Box", "one page per icebreaker, flip and go"),
    ("ch", "04-the-icebreaker-box",      "4"),
    ("ex", "rapid-fire-facilitation",    "✎"),

    ("part", "Part III", "The Retro Format Cookbook", "30+ formats, recipe-card style"),
    ("ch", "05-pick-your-format",        "5"),
    ("ex", "pick-format-case-study",     "✎"),
    ("ch", "06-the-classics-done-well",  "6"),
    ("ch", "07-formats-for-specific-moments", "7"),
    ("ch", "08-creative-high-energy-formats", "8"),
    ("ch", "09-remote-and-async-formats", "9"),
    ("ch", "10-from-talk-to-change",     "10"),

    ("part", "Part IV", "Your AI Co-Pilot", "AI handles the paperwork, humans handle the talking"),
    ("ex", "interlude-the-retro-that-almost-wasnt", "❧"),
    ("ch", "11-where-ai-helps-where-it-hurts", "11"),
    ("ch", "12-ai-before-the-retro",     "12"),
    ("ch", "13-ears-choosing-themes",    "13"),
    ("ex", "ears-case-study",            "✎"),
    ("ch", "14-ai-during-and-after",     "14"),
    ("ch", "15-keep-the-trust",          "15"),
    ("ch", "16-when-ai-is-on-the-team",  "16"),
    ("ch", "17-the-reflective-habit",    "17"),

    ("part", "Back Matter", "", "sources, tools, and where to go next"),
    ("bm", "toolkit",       "–"),
    ("bm", "agents",        "–"),
    ("bm", "references",    "–"),
]

def path_for(kind, slug):
    return (ROOT / f"{slug}.html") if kind == "bm" else (CH / f"{slug}.html")

def first_h1_text(fragment):
    m = re.search(r"<h1[^>]*>(.*?)</h1>", fragment, re.S)
    if not m:
        return ""
    return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()

# ---------------------------------------------------------------- front matter
def frontmatter_sections():
    """Render 00-front-matter.md and split into copyright / dedication / start-here."""
    fm_html = subprocess.run(
        ["pandoc", str(MAN / "00-front-matter.md"), "-f", "markdown", "-t", "html"],
        capture_output=True, text=True, check=True).stdout
    soup = BeautifulSoup(fm_html, "html.parser")
    groups, cur = [], []
    for el in list(soup.children):
        if getattr(el, "name", None) == "h1":
            if cur:
                groups.append(cur)
            cur = [el]
        elif cur is not None:
            cur.append(el)
    if cur:
        groups.append(cur)

    out = []
    for g in groups:
        inner = "".join(str(x) for x in g)
        hid = g[0].get("id", "")
        if hid == "copyright":
            out.append(f'<section class="copyrightpage">{inner}</section>')
        elif hid == "dedication":
            body = "".join(str(x) for x in g[1:]).strip()
            # placeholder comment renders empty -> keep page but note it
            out.append(f'<section class="dedicationpage"><div class="ded-body">{body}</div></section>')
        else:  # start-here and anything else -> normal frontmatter prose
            out.append(f'<section class="frontmatter prose narrow">{inner}</section>')
    return "\n".join(out)

# ---------------------------------------------------------------- assembly
def main():
    build.main()  # regenerate img/ diagrams + keep in step (writes body.html; we re-clean here)
    build.clean.counter = 0  # reset SVG numbering so files match this run

    bodies, toc_rows = [], []
    ch_idx = 0
    for row in STRUCT:
        if row[0] == "part":
            _, ptitle, psub, pnote = row
            bodies.append(
                f'<section class="part-divider">'
                f'<div class="pd-kicker">{html.escape(ptitle)}</div>'
                + (f'<div class="pd-title">{html.escape(psub)}</div>' if psub else "")
                + f'<div class="pd-note">{html.escape(pnote)}</div></section>')
            toc_rows.append(("part", None, None, ptitle if not psub else f"{ptitle} · {psub}"))
            continue

        kind, slug, num = row[0], row[1], row[2]
        p = path_for(kind, slug)
        if not p.exists():
            print("WARNING missing:", p, file=sys.stderr); continue
        frag = build.clean(p)
        title = first_h1_text(frag)
        sid = f"c-{slug}"
        cls = "chapter" + (" is-exercise" if kind == "ex" else "")
        bodies.append(f'<section class="{cls}" id="{sid}">{frag}</section>')
        toc_rows.append((kind, sid, num, title))

    # ---- title page + front matter
    title_page = (
        '<section class="titlepage">'
        '<div class="tp-title">The Retro<br>Playbook</div>'
        '<div class="tp-sub">Using AI to Run Better Agile Retrospectives</div>'
        '<div class="tp-author">Prab Mutti</div>'
        '<div class="tp-imprint">retro-generator.com</div>'
        '</section>')
    front = frontmatter_sections()

    # ---- TOC
    toc_items = ['<section class="toc"><h1>Contents</h1>']
    for kind, sid, num, title in toc_rows:
        if kind == "part":
            toc_items.append(f'<div class="toc-part">{html.escape(title)}</div>')
        else:
            exc = " ex" if kind in ("ex",) else ""
            toc_items.append(
                f'<a class="{exc.strip()}" href="#{sid}">'
                f'<span class="toc-num">{html.escape(num)}</span>'
                f'<span class="toc-title">{html.escape(title)}</span>'
                f'<span class="toc-dots"></span><span class="toc-page"></span></a>')
    toc_items.append('</section>')
    toc = "\n".join(toc_items)

    # ---- stylesheet bundle (inlined so WeasyPrint needs no network)
    css = "\n".join((ROOT / "assets" / f).read_text(encoding="utf-8")
                    for f in ("book.css", "activity.css"))
    css += "\n" + (MAN / "print.css").read_text(encoding="utf-8")

    doc = (f'<!doctype html><html lang="en-GB"><head><meta charset="utf-8">'
           f'<title>The Retro Playbook</title><style>{css}</style></head><body>'
           f'{title_page}{front}{toc}{"".join(bodies)}</body></html>')

    out_html = MAN / "print.html"
    out_html.write_text(doc, encoding="utf-8")
    print(f"wrote {out_html} ({len(doc)} bytes, {len(toc_rows)} toc rows)")

    from weasyprint import HTML
    pdf = MAN / "The-Retro-Playbook-6x9-interior.pdf"
    HTML(string=doc, base_url=str(MAN)).write_pdf(str(pdf))
    print(f"wrote {pdf} ({pdf.stat().st_size//1024} KB)")

if __name__ == "__main__":
    main()
