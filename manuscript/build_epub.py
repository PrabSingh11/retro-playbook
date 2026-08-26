#!/usr/bin/env python3
"""Build the Kindle-safe EPUB from the website chapters.

Kindle's converter chokes on SVG (it stores inline SVG as .svgz and fails with
"couldn't convert your HTML file to Kindle format"). So this build rasterises the
two extracted diagrams to PNG and rewrites the pandoc cover page from an SVG
wrapper to a plain <img>. The result contains no SVG at all.

Run with the build venv (needs cairosvg + lxml):  .buildvenv/bin/python build_epub.py
"""
import re, subprocess, zipfile, shutil
from pathlib import Path

MAN = Path(__file__).resolve().parent
EPUB = MAN / "The-Retro-Playbook.epub"

META = dict(title="The Retro Playbook", author="Prab Mutti", lang="en-GB",
            rights="© 2026 Prab Mutti. All rights reserved.")


def run(*cmd):
    subprocess.run([str(c) for c in cmd], cwd=MAN, check=True)


def main():
    import build, cairosvg  # build.py writes body.html + extracts img/diagram-NN.svg

    # Extract the diagrams in COLOUR for the ebook (the print build runs in its own
    # process and keeps build.py's grayscale VARMAP). Palette = book.css :root.
    build.VARMAP = {
        "paper": "#EDECE2", "paper-deep": "#E1DFD0", "card": "#F6F5EC",
        "ink": "#24352F", "ink-soft": "#5B665D", "ink-faint": "#8B9188",
        "rule": "#C9C4AC", "rule-soft": "#DAD6C3",
        "check": "#3F7684", "ember": "#C15A34", "moss": "#52713F",
        "plum": "#64517E", "gold": "#A9781F",
        "check-tint": "#DDE7E6", "ember-tint": "#F0DFD2", "moss-tint": "#DEE5D3",
        "plum-tint": "#E2DBE9", "gold-tint": "#EBE0C4",
        "accent": "#3F7684", "accent-tint": "#DDE7E6",
    }
    build.SVG_LABEL_STYLE = (
        '<style>.dg-label{font-family:monospace;font-size:9.5px;fill:#5B665D;}'
        '.dg-label-strong{font-family:sans-serif;font-weight:700;font-size:11px;fill:#24352F;}</style>')

    build.main()

    # rasterise the extracted diagrams and point the <img> tags at the PNGs
    body = (MAN / "body.html").read_text(encoding="utf-8")
    for svg in sorted((MAN / "img").glob("diagram-*.svg")):
        png = svg.with_suffix(".png")
        cairosvg.svg2png(url=str(svg), write_to=str(png),
                         output_width=1400, background_color="white")
        body = body.replace(f'src="img/{svg.name}"', f'src="img/{png.name}"')
    (MAN / "body.html").write_text(body, encoding="utf-8")

    # front matter -> html, then one combined document for pandoc
    run("pandoc", "00-front-matter.md", "--to", "html5", "-o", "front.html")
    combined = (
        '<!doctype html><html><head><meta charset="utf-8">'
        '<title>The Retro Playbook</title></head><body>'
        + (MAN / "front.html").read_text(encoding="utf-8")
        + body + "</body></html>")
    # Strip the decorative label emoji (🎯 🧰 👥 🏠 …). Kindle's fonts don't cover
    # them, so they render as tofu squares; the labels read fine as plain text.
    # (Print strips the same range; ✎/❧ TOC markers are outside it and kept.)
    combined = re.sub(
        "[\U0001F000-\U0001FAFF\U00002600-\U000026FF\U0000FE0F\U0000200D]", "", combined)
    (MAN / "combined.html").write_text(combined, encoding="utf-8")

    run("pandoc", "combined.html", "--from", "html", "--to", "epub3",
        "--toc", "--toc-depth=1", "--split-level=1", "--css", "ebook.css",
        "--resource-path=.:img", "--epub-cover-image=cover.png",
        "-M", f"title={META['title']}", "-M", f"author={META['author']}",
        "-M", f"lang={META['lang']}", "-M", f"rights={META['rights']}",
        "-o", EPUB.name)

    _desvg_cover(EPUB)
    print(f"wrote {EPUB} (Kindle-safe: no SVG)")


def _desvg_cover(epub):
    """Rewrite pandoc's SVG-wrapped cover page to a plain <img> (Kindle-friendly)."""
    zin = zipfile.ZipFile(epub)
    names = zin.namelist()
    data = {n: zin.read(n) for n in names}
    zin.close()

    cx = next(n for n in names if n.endswith("cover.xhtml"))
    opf = next(n for n in names if n.endswith(".opf"))
    cover = re.sub(
        r'<svg[^>]*>\s*<image[^>]*xlink:href="([^"]+)"[^>]*/>\s*</svg>',
        lambda m: f'<img src="{m.group(1)}" alt="{META["title"]}" '
                  'style="max-width:100%;height:auto"/>',
        data[cx].decode("utf-8"), flags=re.S)
    data[cx] = cover.encode("utf-8")
    data[opf] = data[opf].decode("utf-8").replace(' properties="svg"', "").encode("utf-8")

    tmp = epub.with_suffix(".tmp.epub")
    zo = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
    zo.writestr("mimetype", data["mimetype"], compress_type=zipfile.ZIP_STORED)
    for n in names:
        if n != "mimetype":
            zo.writestr(n, data[n])
    zo.close()
    shutil.move(tmp, epub)


if __name__ == "__main__":
    main()
