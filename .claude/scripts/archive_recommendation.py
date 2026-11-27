#!/usr/bin/env python3
"""
Freeze a superseded version of a recommendation as a static archive page.

Run this BEFORE editing a recommendation's text after a panel re-deliberation
(see .claude/site-decisions.md, "Panel re-deliberation: revise in place, archive the old version").

    python3 .claude/scripts/archive_recommendation.py \
        --guideline jia --rec jia-rec-3 --slug btsdmard-uveitis \
        --label 2021-10 --from "October 2021" --to "November 2026" \
        [--source-ref main] [--content-ref <commit>]

It reads <guideline>/index.html as it stands at --source-ref (a git ref; default: main), copies the
recommendation's modal (every tab; taken from --content-ref instead when wording edits for the new
version have already reached main, so the archive holds the text as it was BEFORE any of them) into <guideline>/archive/<slug>-<label>.html, and records the
page's SHA-256 in .claude/data/archive-manifest.csv. verify_site.py then fails if the page is ever
altered, goes missing, or loses its "noindex" tag.

Archive pages are public (linked from the rec's "Recommendation History" in More Info) but are kept
out of Google (noindex), the sitemap and the site search. Never edit one after it is created; if a
snapshot was wrong, delete the page and its manifest row and run this again.
"""
import argparse
import csv
import datetime
import hashlib
import re
import subprocess
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / ".claude" / "data" / "archive-manifest.csv"
FIELDS = ["path", "guideline", "rec_id", "slug", "current_from", "current_to",
          "source_commit", "archived_on", "sha256"]

# Same wording -> colour mapping as ETD_RATING_LEVELS in scripts.js, baked in so the frozen page
# needs no JavaScript to show the rating colours.
ETD_LEVELS = {
    'substantial net benefits of the recommended alternative': 'good',
    'small net benefit, or little difference between alternatives': 'caution',
    'important harms': 'serious',
    'high': 'good', 'moderate': 'caution', 'low': 'concern', 'very low': 'serious',
    'no substantial variability expected': 'good',
    'substantial variability is expected or uncertain': 'caution',
    'no important issues with the recommended alternative': 'good',
    'important issues, or potential issues not investigated': 'caution',
    'important negative issues': 'serious',
    'intervention likely increases inequity': 'serious',
    'intervention is likely difficult to implement': 'serious',
}

ARCHIVE_CSS = """
    /* ---- archive page only ---- */
    .archive-main { max-width: 900px; margin: 0 auto; padding: 32px 24px 64px; }
    .archive-banner { background: #fff4d1; border: 1px solid #e0b84a; border-left: 6px solid #b7791f; border-radius: 8px; padding: 18px 22px; margin-bottom: 28px; color: #5b4300; font-size: 15px; line-height: 1.6; }
    .archive-banner strong { display: block; font-size: 17px; margin-bottom: 4px; }
    .archive-banner a { color: #5b4300; font-weight: 600; }
    .archive-category { font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-light); margin-bottom: 6px; }
    .archive-main h1 { font-family: 'Source Serif 4', Georgia, serif; font-size: 26px; font-weight: 600; color: var(--primary-blue); line-height: 1.35; margin-bottom: 28px; }
    .archive-section { margin-bottom: 40px; }
    .archive-section > h2 { font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: var(--text-light); border-bottom: 2px solid var(--border-light); padding-bottom: 8px; margin-bottom: 20px; }
    .archive-meta { font-size: 13px; color: var(--text-light); border-top: 1px solid var(--border-light); padding-top: 16px; }
    @media print { header, footer, .header-top { display: none !important; } .archive-main { padding: 0; } }
"""


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout


def root_anchor(html):
    """The guideline pages use ../ paths; an archive page sits one folder deeper, so anchor to /."""
    return re.sub(r'(href|src)="\.\./', r'\1="/', html)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--guideline", required=True, choices=["adult", "jia"])
    ap.add_argument("--rec", required=True, help="modal id without 'modal-', e.g. jia-rec-3")
    ap.add_argument("--slug", required=True, help="the rec's slug, e.g. btsdmard-uveitis")
    ap.add_argument("--label", required=True, help="YYYY-MM the archived version became current")
    ap.add_argument("--from", dest="cur_from", required=True, help='e.g. "October 2021"')
    ap.add_argument("--to", dest="cur_to", required=True, help='e.g. "November 2026"')
    ap.add_argument("--source-ref", default="main", help="git ref supplying the page styles, header and footer")
    ap.add_argument("--content-ref", default=None,
                    help="git ref holding the recommendation text to freeze (default: same as --source-ref)")
    a = ap.parse_args()

    rel = f"{a.guideline}/archive/{a.slug}-{a.label}.html"
    out = ROOT / rel
    if out.exists():
        sys.exit(f"{rel} already exists - archive pages are never overwritten.")

    content_ref = a.content_ref or a.source_ref
    commit = git("rev-parse", "--short", content_ref).strip()
    src = git("show", f"{a.source_ref}:{a.guideline}/index.html")
    soup = BeautifulSoup(src, "html.parser")
    content = git("show", f"{content_ref}:{a.guideline}/index.html")
    modal = BeautifulSoup(content, "html.parser").find(id=f"modal-{a.rec}")
    if modal is None:
        sys.exit(f"modal-{a.rec} not found in {a.guideline}/index.html at {content_ref}")

    title = modal.select_one(".modal-title").get_text(" ", strip=True)
    category = modal.select_one(".modal-category").get_text(" ", strip=True)
    labels = {b["data-tab"]: b.get_text(" ", strip=True) for b in modal.select(".modal-tab")}

    for el in modal.select("[onclick]"):
        del el["onclick"]
    for pill in modal.select(".etd-rating"):
        level = ETD_LEVELS.get(re.sub(r"\s+", " ", pill.get_text()).strip().lower())
        if level:
            pill["class"] = pill.get("class", []) + [f"etd-rating--{level}"]
            box = pill.find_parent(class_="etd-domain")
            if box:
                box["class"] = box.get("class", []) + [f"etd-domain--{level}"]

    sections = []
    for tab in modal.select(".tab-content"):
        key = tab["id"].replace(f"{a.rec}-", "")
        sections.append(f'<section class="archive-section">\n<h2>{labels.get(key, key)}</h2>\n'
                        f'{tab.decode_contents()}\n</section>')
    last_updated = ""
    for span in modal.select(".modal-footer .card-updated"):
        last_updated = span.get_text(" ", strip=True)

    styles = "\n".join(str(s) for s in soup.find_all("style"))
    styles = styles.replace("</style>", ARCHIVE_CSS + "</style>", 1)
    ga = re.search(r'<script async src="https://www\.googletagmanager\.com/gtag/js[^>]*></script>\s*<script>.*?</script>', src, re.S)
    if not ga:
        sys.exit("could not find the Google Analytics tag in the source page")
    header = root_anchor(str(soup.find("header")))
    footer = root_anchor(str(soup.find("footer")))
    current_url = f"/{a.guideline}/#{a.slug}"

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Superseded version ({a.cur_from}): {title} | Australian Living Guidelines</title>
    <meta name="description" content="Archived, superseded version of an Australian Living Guideline recommendation, kept as a historical record. It was current from {a.cur_from} to {a.cur_to}.">
    <meta name="robots" content="noindex, follow">
    <link rel="stylesheet" href="/search.css">
    <script src="/search.js" defer></script>
    <link rel="stylesheet" href="/header.css">
    <script src="/header.js" defer></script>
    <link rel="icon" href="/favicon.ico" sizes="any">
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@300;400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap" rel="stylesheet">
{styles}
    {ga.group(0)}
</head>
<body>
{header}
<main class="archive-main">
    <div class="archive-banner">
        <strong>Superseded version &ndash; kept as a historical record</strong>
        This is the recommendation as it stood from {a.cur_from} until {a.cur_to}. It is no longer current and should not be used to guide care.
        <a href="{current_url}">View the current recommendation</a>.
    </div>
    <div class="archive-category">{category}</div>
    <h1>{title}</h1>
{chr(10).join(sections)}
    <p class="archive-meta">Archived version, current {a.cur_from} to {a.cur_to}. At the time of archiving the recommendation showed &ldquo;{last_updated}&rdquo;.</p>
</main>
{footer}
</body>
</html>
"""
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    sha = hashlib.sha256(out.read_bytes()).hexdigest()

    new_file = not MANIFEST.exists()
    with MANIFEST.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            w.writeheader()
        w.writerow({"path": rel, "guideline": a.guideline, "rec_id": a.rec, "slug": a.slug,
                    "current_from": a.cur_from, "current_to": a.cur_to, "source_commit": commit,
                    "archived_on": datetime.date.today().isoformat(), "sha256": sha})
    print(f"Archived {a.rec} ({a.cur_from} to {a.cur_to}) from {commit} -> {rel}")
    print(f"sha256 {sha} recorded in {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
