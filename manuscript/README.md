# Manuscript — KDP build

Source for the Kindle ebook (and, later, the print PDF), generated from the website chapters.

## Files
- `metadata.yaml` — title, author, rights (edit author/dedication here).
- `00-front-matter.md` — copyright, dedication, "Start Here" preface.
- `ebook.css` — grayscale, reflowable e-reader stylesheet.
- `build.py` — cleans the website HTML (strips nav/chrome, remaps citation links to internal anchors, extracts inline-SVG diagrams to grayscale image files) into `body.html`.
- `img/` — diagrams extracted from the chapters (Sailboat, Weather Map).
- `The-Retro-Playbook.epub` — the built Kindle ebook. **Download this.**

## Rebuild the EPUB
```bash
cd manuscript
python3 build.py
pandoc 00-front-matter.md --to html5 -o front.html
{ echo '<!doctype html><html><head><meta charset="utf-8"><title>The Retro Playbook</title></head><body>'; cat front.html body.html; echo '</body></html>'; } > combined.html
pandoc combined.html --from html --to epub3 --toc --toc-depth=1 --split-level=1 \
  --css ebook.css --resource-path=.:img \
  -M title="The Retro Playbook" -M author="Prab Mutti" -M lang=en-GB \
  -M rights="© 2026 Prab Mutti. All rights reserved." \
  -o The-Retro-Playbook.epub
```

## Before publishing
- Validate with **Kindle Previewer** (or `epubcheck`).
- Add a **cover** (Kindle wants ~1600×2560 JPEG/PNG) — not yet built.
- The **print paperback PDF** (6×9″) is a separate build, still to do.
