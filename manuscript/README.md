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
Use `build_epub.py` — it does the pandoc build **and** the Kindle-safety steps
(rasterises the SVG diagrams to PNG and rewrites the SVG cover page to a plain
`<img>`). Kindle's converter fails on SVG/SVGZ with "couldn't convert your HTML
file to Kindle format", so never ship the raw pandoc EPUB.
```bash
cd manuscript
.buildvenv/bin/pip install cairosvg lxml   # one-time, alongside weasyprint/bs4
.buildvenv/bin/python build_epub.py        # -> The-Retro-Playbook.epub (no SVG)
```
Verify before upload: `unzip -l The-Retro-Playbook.epub` should show only `.png`
media (no `.svgz`), and Kindle Previewer should open it cleanly.

## Rebuild the print interior PDF (6×9″)
Needs WeasyPrint + BeautifulSoup in a venv (system Python is externally-managed):
```bash
cd manuscript
python3 -m venv .buildvenv
.buildvenv/bin/pip install weasyprint beautifulsoup4
.buildvenv/bin/python build_print.py    # -> The-Retro-Playbook-6x9-interior.pdf
```
`build_print.py` reuses `build.clean()`, adds a title page / copyright / dedication /
part dividers / a page-numbered table of contents, interleaves a **selected subset**
of the "Your Turn" exercises after their parent chapters (see `ARCHIVED-your-turn.md`
for which are excluded from print), applies
`book.css` + `activity.css` + `print.css` (grayscale, mirrored margins with a binding
gutter, running heads, roman front-matter + arabic body page numbers), and renders
with WeasyPrint. Current build: **218 pages**.

### Gutter / margins note
`print.css` sets a 0.75″ inside (gutter) margin — comfortably above KDP's minimum for
a 151–300-page book (0.625″). If the page count crosses 300, bump the gutter to 0.75″+
(already there) and re-check outside/top/bottom (currently 0.55″/0.7″/0.7″, all above
the 0.25″ minimum).

## Before publishing
- Validate the EPUB with **Kindle Previewer** (or `epubcheck`).
- EPUB **cover** done (`cover.png/.jpg`, ~1600×2560). Print **wrap cover** done
  (`wrap-cover.pdf`, spine sized to the 218-page count — 0.491″).
- Fill in the **dedication** in `00-front-matter.md` (currently a blank placeholder page).
