#!/usr/bin/env python3
"""Structural copyedit checks for The Retro Playbook chapter HTML.

Catches the mechanical stuff a proofreading pass shouldn't have to eyeball by hand:
tag balance, broken/orphan citation links, and dead internal links. It does NOT judge
prose, voice, or factual claims -- see COPYEDIT.md for that part of the process.

Usage:
    python3 scripts/copyedit_check.py                # check everything
    python3 scripts/copyedit_check.py chapters/03-facilitation-101.html
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TAGS = ["div", "section", "article", "aside", "ul", "ol", "li"]


def check_tag_balance(path: Path) -> list[str]:
    html = path.read_text()
    issues = []
    for tag in TAGS:
        opens = len(re.findall(rf"<{tag}[ >]", html))
        closes = len(re.findall(rf"</{tag}>", html))
        if opens != closes:
            issues.append(f"<{tag}> mismatch -- {opens} open, {closes} close")
    return issues


def defined_citation_ids() -> set[str]:
    ref_file = ROOT / "references.html"
    if not ref_file.exists():
        return set()
    return set(re.findall(r'id="([a-zA-Z0-9_-]+)"', ref_file.read_text()))


def check_citations(path: Path, defined_ids: set[str]) -> list[str]:
    html = path.read_text()
    used = re.findall(r'references\.html#([a-zA-Z0-9_-]+)', html)
    issues = []
    for cid in used:
        if cid not in defined_ids:
            issues.append(f'cites "#{cid}" -- no matching id in references.html')
    return issues


def check_internal_links(path: Path) -> list[str]:
    html = path.read_text()
    links = re.findall(r'href="([^"#]+)(?:#[^"]*)?"', html)
    issues = []
    for link in links:
        if link.startswith(("http://", "https://", "mailto:", "data:")):
            continue
        target = (path.parent / link).resolve()
        if not target.exists():
            issues.append(f'links to "{link}" -- file does not exist')
    return issues


def main():
    args = sys.argv[1:]
    scoped = bool(args)
    if scoped:
        files = [Path(a) for a in args]
    else:
        files = sorted((ROOT / "chapters").glob("*.html")) + [
            ROOT / "index.html", ROOT / "references.html",
            ROOT / "agents.html", ROOT / "toolkit.html",
        ]
        files = [f for f in files if f.exists()]

    defined_ids = defined_citation_ids()
    used_ids = set()
    total_issues = 0

    for f in files:
        html = f.read_text()
        used_ids |= set(re.findall(r'references\.html#([a-zA-Z0-9_-]+)', html))
        issues = (
            check_tag_balance(f)
            + check_citations(f, defined_ids)
            + check_internal_links(f)
        )
        if issues:
            total_issues += len(issues)
            try:
                rel = f.relative_to(ROOT)
            except ValueError:
                rel = f
            for issue in issues:
                print(f"{rel}: {issue}")

    # Orphan-id check only makes sense when scanning the whole book -- a scoped
    # run would flag every id not cited in that one file as a false "orphan".
    orphan_ids = set()
    if not scoped:
        orphan_ids = defined_ids - used_ids
        if orphan_ids:
            print(f"references.html: orphan ids not cited anywhere -- {sorted(orphan_ids)}")

    if total_issues == 0 and not orphan_ids:
        print("No structural issues found.")


if __name__ == "__main__":
    main()
