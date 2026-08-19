# Manuscript — KDP build

Source for the Kindle ebook (and, later, the print PDF), generated from the website chapters.

## Files
- `metadata.yaml` — title, author, rights (edit author/dedication here).
- `00-front-matter.md` — copyright, dedication, "Start Here" preface.
- `ebook.css` — grayscale, reflowable e-reader stylesheet.
- `build.py` — cleans the website HTML (strips nav/chrome, remaps citation links to internal anchors, extracts inline-SVG diagrams to grayscale image files) into `body.html`.
- `img/` — diagrams extracted from the chapters (Sailboat, Weather Map).
- `The-Retro-Playbook.epub` — the built Kindle ebook. **Download this.**
- `build_print.py` + `print.css` — the print (paperback) build; produces `The-Retro-Playbook-6x9-interior.pdf`.
- `The-Retro-Playbook-6x9-interior.pdf` — the built 6×9″ print interior. **Download this for KDP paperback.**

## Rebuild the EPUB
```bash
cd manuscript
python3 build.py
pandoc 00-front-matter.md --to html5 -o front.html
{ echo '<!doctype html><html><head><meta charset="utf-8"><title>The Retro Playbook</title></head><body>'; cat front.html body.html; echo '</body></html>'; } > combined.html
pandoc combined.html --from html --to epub3 --toc --toc-depth=1 --split-level=1 \
  --css ebook.css --resource-path=.:img \
  -M title="The Retro Playbook" -M author="Prabhjit Mutti" -M lang=en-GB \
  -M rights="© 2026 Prabhjit Mutti. All rights reserved." \
  -o The-Retro-Playbook.epub
```

## Rebuild the print interior PDF (6×9″)
Needs WeasyPrint + BeautifulSoup in a venv (system Python is externally-managed):
```bash
cd manuscript
python3 -m venv .buildvenv
.buildvenv/bin/pip install weasyprint beautifulsoup4
.buildvenv/bin/python build_print.py    # -> The-Retro-Playbook-6x9-interior.pdf
```
`build_print.py` reuses `build.clean()`, adds a title page / copyright / dedication /
part dividers / a page-numbered table of contents, interleaves the "Your Turn"
exercises after their parent chapters (matching the website reading order), applies
`book.css` + `activity.css` + `print.css` (grayscale, mirrored margins with a binding
gutter, running heads, roman front-matter + arabic body page numbers), and renders
with WeasyPrint. Current build: **246 pages**.

### Gutter / margins note
`print.css` sets a 0.75″ inside (gutter) margin — comfortably above KDP's minimum for
a 151–300-page book (0.625″). If the page count crosses 300, bump the gutter to 0.75″+
(already there) and re-check outside/top/bottom (currently 0.55″/0.7″/0.7″, all above
the 0.25″ minimum).

## Before publishing
- Validate the EPUB with **Kindle Previewer** (or `epubcheck`).
- EPUB **cover** done (`cover.png/.jpg`, ~1600×2560). Print **wrap cover** (front+spine+back,
  spine width from the 246-page count) still to build.
- Fill in the **dedication** in `00-front-matter.md` (currently a blank placeholder page).
