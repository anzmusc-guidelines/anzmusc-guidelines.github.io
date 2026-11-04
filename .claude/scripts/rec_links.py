#!/usr/bin/env python3
"""
Generate the list of direct links to every recommendation, straight from the site.

    python3 .claude/scripts/rec_links.py                 # print CSV to the screen
    python3 .claude/scripts/rec_links.py --out FILE.csv  # write CSV to a file
    python3 .claude/scripts/rec_links.py --markdown      # print a readable table

Columns: Guideline, Rec #, Title, Numeric URL, Slug URL — the same layout as the old
recommendation-links.csv, which this replaces. Because it reads the live pages, it can't
drift out of date: rerun it whenever someone asks for the links.

Title  = the modal title (<h2 class="modal-title">)
Slug   = from window.adultSlugMap / window.jiaSlugMap on each page
Both URL forms work on the live site (scripts.js accepts #rec-N, #jia-rec-N and slugs).

Requires: beautifulsoup4
"""
import argparse
import csv
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
BASE = "https://livingguidelines.org"

PAGES = [
    # label,     file,               url path, id prefix,  slug map var
    ("Adult IA", "adult/index.html", "/adult/", "rec-",     "adultSlugMap"),
    ("JIA",      "jia/index.html",   "/jia/",   "jia-rec-", "jiaSlugMap"),
]


def collect():
    rows = []
    for label, rel, path, prefix, slug_var in PAGES:
        html = (ROOT / rel).read_text(encoding="utf-8")
        soup = BeautifulSoup(html, "html.parser")
        m = re.search(rf"window\.{slug_var}\s*=\s*\{{(.*?)\}};", html, re.DOTALL)
        slug_for = {}
        if m:
            for slug, rid in re.findall(r"'([^']+)'\s*:\s*'([^']+)'", m.group(1)):
                slug_for[rid] = slug
        recs = []
        for mod in soup.select("div.modal-overlay[id^=modal-]"):
            rid = mod["id"][len("modal-"):]
            num = re.fullmatch(rf"{re.escape(prefix)}(\d+)", rid)
            if not num:
                continue
            title_el = mod.select_one(".modal-title")
            title = re.sub(r"\s+", " ", title_el.get_text(" ", strip=True)) if title_el else ""
            slug = slug_for.get(rid)
            recs.append((int(num.group(1)), [
                label, num.group(1), title,
                f"{BASE}{path}#{rid}",
                f"{BASE}{path}#{slug}" if slug else "",
            ]))
        rows += [r for _, r in sorted(recs)]
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", help="write CSV to this file instead of the screen")
    ap.add_argument("--markdown", action="store_true", help="print a Markdown table")
    args = ap.parse_args()

    rows = collect()
    header = ["Guideline", "Rec #", "Title", "Numeric URL", "Slug URL"]

    if args.markdown:
        print("| " + " | ".join(header) + " |")
        print("|" + "---|" * len(header))
        for r in rows:
            print("| " + " | ".join(c.replace("|", "\\|") for c in r) + " |")
        return

    fh = open(args.out, "w", newline="", encoding="utf-8") if args.out else sys.stdout
    w = csv.writer(fh)
    w.writerow(header)
    w.writerows(rows)
    if args.out:
        fh.close()
        print(f"Wrote {len(rows)} recommendations to {args.out}")


if __name__ == "__main__":
    main()
