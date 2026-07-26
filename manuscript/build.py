#!/usr/bin/env python3
"""Assemble a clean single-file HTML body from the website chapters, for pandoc -> EPUB."""
import re, sys
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent      # repo root
CH = ROOT / "chapters"
IMGDIR = Path(__file__).resolve().parent / "img"

# map the website's CSS custom-property colours to grayscale equivalents,
# so inline-SVG diagrams render standalone (no external stylesheet in an ebook)
VARMAP = {
    "paper": "#f4f4f2", "paper-deep": "#eeece2", "card": "#f4f4f2",
    "ink": "#222222", "ink-soft": "#555555", "ink-faint": "#888888",
    "rule": "#bbbbbb", "rule-soft": "#d5d5d5",
    "check": "#555555", "ember": "#555555", "moss": "#555555", "plum": "#555555", "gold": "#555555",
    "check-tint": "#dddddd", "ember-tint": "#dddddd", "moss-tint": "#dddddd",
    "plum-tint": "#dddddd", "gold-tint": "#dddddd", "accent": "#555555", "accent-tint": "#dddddd",
}
SVG_LABEL_STYLE = ('<style>.dg-label{font-family:monospace;font-size:9.5px;fill:#555;}'
                   '.dg-label-strong{font-family:sans-serif;font-weight:700;font-size:11px;fill:#222;}</style>')

def _resolve_vars(svg_markup):
    return re.sub(r"var\(--([a-z-]+)\)", lambda m: VARMAP.get(m.group(1), "#888888"), svg_markup)

# reading order: front matter (md, added by pandoc) then these bodies
ORDER = [
    CH/"01-five-ways-retros-fail.html",
    CH/"02-the-five-stage-recipe.html",
    CH/"03-facilitation-101.html",
    CH/"04-the-icebreaker-box.html",
    CH/"05-pick-your-format.html",
    CH/"06-the-classics-done-well.html",
    CH/"07-formats-for-specific-moments.html",
    CH/"08-creative-high-energy-formats.html",
    CH/"09-remote-and-async-formats.html",
    CH/"10-from-talk-to-change.html",
    CH/"interlude-the-retro-that-almost-wasnt.html",
    CH/"11-where-ai-helps-where-it-hurts.html",
    CH/"12-ai-before-the-retro.html",
    CH/"13-ears-choosing-themes.html",
    CH/"14-ai-during-and-after.html",
    CH/"15-keep-the-trust.html",
    CH/"16-when-ai-is-on-the-team.html",
    CH/"17-the-reflective-habit.html",
    ROOT/"toolkit.html",
    ROOT/"agents.html",
    ROOT/"references.html",
]

def clean(path):
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    page = soup.select_one("div.page") or soup.body or soup
    # strip web chrome
    for sel in ["a.back", "footer.colophon", "nav.chapter-nav", "div.kicker"]:
        for el in page.select(sel):
            # remove the wrapping <p> if the back-link sits alone in one
            if el.name == "a" and el.parent and el.parent.name == "p" and len(el.parent.get_text(strip=True)) == len(el.get_text(strip=True)):
                el.parent.decompose()
            else:
                el.decompose()
    # lift the chapter <h1>+dek out of the <header class="lid"> wrapper so the
    # heading sits at top level and pandoc can split the EPUB on it
    for lid in page.select("header.lid"):
        lid.unwrap()
    # extract content diagrams (inline SVG) to standalone grayscale image files,
    # since pandoc drops inline SVG on HTML import
    for svg in page.select("svg"):
        n = clean.counter = getattr(clean, "counter", 0) + 1
        markup = _resolve_vars(str(svg))
        markup = re.sub(r"(<svg\b[^>]*>)", r"\1" + SVG_LABEL_STYLE, markup, count=1)
        # bs4 lowercases viewBox -> viewbox; restore so SVG scales
        markup = markup.replace("viewbox=", "viewBox=")
        IMGDIR.mkdir(exist_ok=True)
        fname = f"diagram-{n:02d}.svg"
        (IMGDIR / fname).write_text(markup, encoding="utf-8")
        alt = svg.get("aria-label", "Diagram")
        img = soup.new_tag("img", src=f"img/{fname}", alt=alt)
        svg.replace_with(img)
    # handle links
    for a in page.find_all("a", href=True):
        href = a["href"]
        if "references.html#" in href:                 # citation -> internal anchor (works after epub split)
            a["href"] = "#" + href.split("#", 1)[1]
        elif href.startswith("http"):                  # external -> keep
            pass
        else:                                          # cross-chapter link -> plain text
            a.replace_with(*a.contents)
    return page.decode_contents() + "\n"

def main():
    parts = [clean(p) for p in ORDER if p.exists()]
    missing = [p.name for p in ORDER if not p.exists()]
    if missing:
        print("WARNING missing:", missing, file=sys.stderr)
    body = "\n".join(parts)
    out = Path(__file__).parent / "body.html"
    out.write_text(body, encoding="utf-8")
    print(f"wrote {out} ({len(parts)} sections, {len(body)} bytes)")

if __name__ == "__main__":
    main()
