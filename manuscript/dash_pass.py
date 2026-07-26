#!/usr/bin/env python3
"""Convert em-dashes to spaced en-dashes (British house style) across the book,
leaving <pre> code/prompt blocks untouched so copy-paste prompts stay verbatim."""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FILES = (
    sorted((ROOT / "chapters").glob("*.html"))
    + [ROOT / "index.html", ROOT / "references.html", ROOT / "toolkit.html", ROOT / "agents.html"]
    + [ROOT / "manuscript" / "00-front-matter.md"]
)

def convert(text):
    # normalise entity forms to the literal char first
    text = text.replace("&mdash;", "—").replace("&#8212;", "—")
    # spaced en-dash, collapsing any surrounding whitespace to single spaces
    return re.sub(r"\s*—\s*", " – ", text)

def process(path):
    src = path.read_text(encoding="utf-8")
    if path.suffix == ".html":
        # protect <pre>...</pre> spans
        parts = re.split(r"(<pre\b.*?</pre>)", src, flags=re.S)
        out = "".join(p if i % 2 else convert(p) for i, p in enumerate(parts))
    else:
        out = convert(src)  # markdown front matter: no code blocks
    before = src.count("—")
    after = out.count("—")
    path.write_text(out, encoding="utf-8")
    return before, after

total_before = 0
for f in FILES:
    if not f.exists():
        print("MISSING", f, file=sys.stderr); continue
    b, a = process(f)
    total_before += b
    if b:
        print(f"{f.name:42} {b:4d} em-dashes -> converted ({a} left inside <pre>)")
print(f"\nTOTAL em-dashes converted (outside <pre>): {total_before}")
