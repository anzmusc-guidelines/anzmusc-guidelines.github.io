#!/usr/bin/env python3
"""
Site integrity checks for livingguidelines.org.

Run from the repository root after ANY edit, before committing:

    python3 .claude/scripts/verify_site.py

Exit code 0 = no errors (warnings may still be printed).
Exit code 1 = at least one error; fix before publishing.

What it checks
--------------
Guideline pages (adult/index.html, jia/index.html):
  E  every card has exactly one openModal('<id>') and a matching modal exists
  E  no two cards open the same modal; no duplicate modal ids; no orphan modals
  E  recommendation ids form a contiguous sequence (rec-0.. / jia-rec-1..)
  E  card category ~ modal category (one contains the other); card title ~ modal title
  E  card "Updated Mon YYYY" == modal footer "Last updated: Month YYYY"
     (or BOTH read "Update in progress" via .card-updated-pending - the placeholder used
      while a living NMA update is being finalised; see site-decisions.md)
  E  switchTab() calls and tab-content ids inside each modal use that modal's id
  E  every rec id has a slug in the page's slug map, and every slug points at a real rec
  E  hero-badge recommendation count == number of cards
  W  latest "Update N (Month YYYY)" in the Data tab != card date
     (expected for brand-new recs dated by panel month, e.g. rec-18 - see site-decisions.md)
  W  Data-tab update numbers not sequential (Update 1, 2, 3 ...)
  E  modal MAGICapp link == the master list .claude/data/<adult|jia>-magicapp-urls.csv
  W  MAGICapp link is guideline-level rather than rec-specific

Site-wide:
  E  search-index.json matches a fresh build (run .claude/scripts/build_search_index.py)
  E  every page has the header search box and loads /search.css and /search.js
  E  every page has the Menu button, nav#site-nav, /header.css and /header.js
  E  every headshot <img> on panellists.html resolves to a real .jpg file
  E  every top-level HTML page carries the Google Analytics tag
  W  headshot files over 40 KB (see the panellist-headshot skill)

Requires: beautifulsoup4  (pip install beautifulsoup4)
"""
import csv
import os
import re
import sys
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("beautifulsoup4 is required: pip install beautifulsoup4")

ROOT = Path(__file__).resolve().parents[2]
GA_ID = "G-XQKQVSHVS5"
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
ABBR = {m[:3]: m for m in MONTHS}

errors, warnings = [], []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def text(el):
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True)) if el else ""


def norm(s):
    return re.sub(r"[^a-z0-9 ]", "", s.lower())


def check_guideline(rel_path, prefix, slug_var, first_index):
    path = ROOT / rel_path
    magic_csv = ROOT / ".claude" / "data" / f"{Path(rel_path).parts[0]}-magicapp-urls.csv"  # adult-… / jia-…
    magic_master = {}
    if magic_csv.exists():
        with open(magic_csv, newline="", encoding="utf-8") as f:
            magic_master = {row["rec_id"]: row["magicapp_url"].strip() for row in csv.DictReader(f)}
    if not path.exists():
        err(f"{rel_path}: file missing")
        return
    html = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    label = rel_path

    # ---- cards -----------------------------------------------------------
    cards = soup.select("div.recommendation-card")
    card_map = {}
    for i, card in enumerate(cards):
        m = re.findall(r"openModal\('([^']+)'\)", card.get("onclick", ""))
        if len(m) != 1:
            err(f"{label}: card #{i + 1} has {len(m)} openModal() calls (expected 1)")
            continue
        rid = m[0]
        if rid in card_map:
            err(f"{label}: two cards both open '{rid}'")
        card_map[rid] = card
        if prefix == "rec" and not card.get("data-conditions"):
            err(f"{label}: card {rid} has no data-conditions (required on Adult page)")
        if prefix == "jia-rec" and card.has_attr("data-conditions"):
            err(f"{label}: card {rid} has data-conditions (not used on JIA page)")

    # ---- modals ----------------------------------------------------------
    modals = soup.select("div.modal-overlay[id^=modal-]")
    modal_map = {}
    for mod in modals:
        rid = mod["id"][len("modal-"):]
        if rid in modal_map:
            err(f"{label}: duplicate modal id 'modal-{rid}'")
        modal_map[rid] = mod

    for rid in card_map:
        if rid not in modal_map:
            err(f"{label}: card opens '{rid}' but no modal-{rid} exists")
    for rid in modal_map:
        if rid not in card_map:
            err(f"{label}: modal-{rid} is orphaned (no card opens it)")

    # ---- contiguous ids --------------------------------------------------
    nums = []
    for rid in card_map:
        mm = re.fullmatch(rf"{prefix}-(\d+)", rid)
        if not mm:
            err(f"{label}: unexpected recommendation id format '{rid}'")
        else:
            nums.append(int(mm.group(1)))
    if nums:
        expected = list(range(first_index, first_index + len(nums)))
        if sorted(nums) != expected:
            missing = sorted(set(expected) - set(nums))
            extra = sorted(set(nums) - set(expected))
            err(f"{label}: ids not contiguous from {prefix}-{first_index} "
                f"(missing {missing}, unexpected {extra})")

    # ---- per-recommendation consistency ---------------------------------
    for rid, card in card_map.items():
        mod = modal_map.get(rid)
        if mod is None:
            continue

        c_cat = text(card.select_one(".card-category"))
        m_cat = text(mod.select_one(".modal-category"))
        # Card category may be a shortened form of the modal's (e.g. JIA
        # "Non-pharmacological" vs "Non-pharmacological interventions for JIA"),
        # so require only that one contains the other, ignoring case.
        if c_cat and m_cat and c_cat.lower() not in m_cat.lower() and m_cat.lower() not in c_cat.lower():
            err(f"{label}: {rid} category mismatch - card '{c_cat}' vs modal '{m_cat}'")

        c_title = norm(text(card.select_one(".card-title")))
        m_title = norm(text(mod.select_one(".modal-title")))
        if c_title and m_title and c_title not in m_title and m_title not in c_title:
            # loose fallback: most card-title words should appear in the modal title
            words = [w for w in c_title.split() if len(w) > 3]
            hits = sum(w in m_title for w in words)
            if not words or hits / len(words) < 0.6:
                err(f"{label}: {rid} title mismatch - card '{text(card.select_one('.card-title'))}' "
                    f"vs modal '{text(mod.select_one('.modal-title'))}'")

        # dates
        c_date_el = card.select_one(".card-updated")
        c_date = None
        c_pending = bool(card.select_one(".card-updated-pending"))
        m_pending = bool(mod.select_one(".modal-footer .card-updated-pending"))
        if c_pending or m_pending:
            if not (c_pending and m_pending):
                err(f"{label}: {rid} 'Update in progress' placeholder must be on BOTH the card and the modal footer")
            if c_pending and text(c_date_el) != "Update in progress":
                err(f"{label}: {rid} pending card badge text should be 'Update in progress': '{text(c_date_el)}'")
            if c_pending and m_pending:
                warn(f"{label}: {rid} shows 'Update in progress' instead of a date (placeholder - clear it when the update is published)")
        elif c_date_el:
            mm = re.search(r"Updated\s+([A-Z][a-z]{2})\s+(\d{4})", text(c_date_el))
            if mm and mm.group(1) in ABBR:
                c_date = f"{ABBR[mm.group(1)]} {mm.group(2)}"
            else:
                err(f"{label}: {rid} card date not in 'Updated Mon YYYY' form: '{text(c_date_el)}'")
        else:
            err(f"{label}: {rid} card has no .card-updated date")

        m_date = None
        for span in mod.select(".card-updated"):
            mm = re.search(r"Last updated:\s*([A-Z][a-z]+)\s+(\d{4})", text(span))
            if mm:
                m_date = f"{mm.group(1)} {mm.group(2)}"
        if m_date is None and not m_pending:
            err(f"{label}: {rid} modal footer has no 'Last updated: Month YYYY'")
        elif c_date and m_date != c_date:
            err(f"{label}: {rid} date mismatch - card '{c_date}' vs modal footer '{m_date}'")

        # Data tab: latest update vs card date; sequential numbering
        data_tab = mod.select_one(f"#{rid}-data")
        if data_tab is None:
            err(f"{label}: {rid} has no data tab (#{rid}-data)")
        else:
            updates = []
            for li in data_tab.select("ul.evidence-list li"):
                mm = re.search(r"Update\s+(\d+)\s*\(([A-Z][a-z]+)\s+(\d{4})\)", text(li))
                if mm:
                    updates.append((int(mm.group(1)), f"{mm.group(2)} {mm.group(3)}"))
            if updates:
                ns = [u[0] for u in updates]
                if ns != list(range(1, len(ns) + 1)):
                    warn(f"{label}: {rid} Data-tab update numbers not sequential: {ns}")
                latest = updates[-1][1]
                if c_date and latest != c_date:
                    warn(f"{label}: {rid} latest Data-tab update '{latest}' != card date '{c_date}'")

        # tab ids and switchTab() calls belong to this rec
        for tc in mod.select(".tab-content[id]"):
            if not tc["id"].startswith(f"{rid}-"):
                err(f"{label}: modal-{rid} contains tab '{tc['id']}' belonging to another rec")
        for call in re.findall(r"switchTab\('([^']+)'", str(mod)):
            if call != rid:
                err(f"{label}: modal-{rid} has switchTab('{call}', ...) - wrong rec id")

        # MAGICapp deep link - must match the master list in .claude/data/<prefix>-magicapp-urls.csv
        link = mod.select_one("a.magicapp-link")
        if link is None:
            warn(f"{label}: {rid} has no 'View in MAGICapp' link")
        else:
            href = link.get("href", "")
            if not re.search(r"/(section|rec)/", href):
                warn(f"{label}: {rid} MAGICapp link is guideline-level, not rec-specific")
            if magic_master:
                if rid not in magic_master:
                    err(f"{label}: {rid} missing from {magic_csv.name} - add its MAGICapp URL there")
                elif magic_master[rid] != href:
                    err(f"{label}: {rid} MAGICapp link '{href}' differs from {magic_csv.name} "
                        f"('{magic_master[rid]}') - the CSV is the master list")

    # ---- slug map ----------------------------------------------------------
    sm = re.search(rf"window\.{slug_var}\s*=\s*\{{(.*?)\}};", html, re.DOTALL)
    if not sm:
        err(f"{label}: could not find window.{slug_var}")
    else:
        pairs = re.findall(r"'([^']+)'\s*:\s*'([^']+)'", sm.group(1))
        slugs, targets = [p[0] for p in pairs], [p[1] for p in pairs]
        if len(slugs) != len(set(slugs)):
            err(f"{label}: duplicate slug in {slug_var}")
        for s, t in pairs:
            if t not in card_map:
                err(f"{label}: slug '{s}' points at '{t}', which does not exist")
        for rid in card_map:
            if rid not in targets:
                err(f"{label}: {rid} has no slug in {slug_var}")

    # ---- hero badge count ----------------------------------------------------
    for badge in soup.select(".hero-badge"):
        mm = re.search(r"(\d+)\s+Recommendations?", text(badge))
        if mm and int(mm.group(1)) != len(cards):
            err(f"{label}: hero badge says {mm.group(1)} recommendations but page has {len(cards)} cards")

    print(f"  {label}: {len(cards)} cards, {len(modals)} modals checked")


def check_headshots():
    page = ROOT / "panellists.html"
    if not page.exists():
        return
    html = page.read_text(encoding="utf-8")
    srcs = re.findall(r'src="images/headshots/([^"]+)"', html)
    for s in srcs:
        if not (ROOT / "images" / "headshots" / s).exists():
            err(f"panellists.html: headshot '{s}' does not exist")
        if not s.lower().endswith(".jpg"):
            err(f"panellists.html: headshot '{s}' is not a .jpg")
    for f in sorted((ROOT / "images" / "headshots").glob("*")):
        if f.suffix.lower() in (".jpg", ".jpeg", ".png") and f.stat().st_size > 40 * 1024:
            warn(f"images/headshots/{f.name} is {f.stat().st_size // 1024} KB (target 10-20 KB)")
    print(f"  panellists.html: {len(srcs)} headshot references checked")


def check_analytics():
    pages = sorted(ROOT.glob("*.html")) + sorted(ROOT.glob("adult/*.html")) + sorted(ROOT.glob("jia/*.html"))

    # ---- site search: index freshness + every page wired up ---------------------
    try:
        sys.path.insert(0, str(ROOT / ".claude" / "scripts"))
        import build_search_index as bsi
        import json as _json
        fresh = bsi.build()
        idx_path = ROOT / "search-index.json"
        if not idx_path.exists():
            err("search-index.json missing - run python3 .claude/scripts/build_search_index.py")
        else:
            current = _json.loads(idx_path.read_text(encoding="utf-8"))
            current.pop("hash", None)
            if current != fresh:
                err("search-index.json is stale - run python3 .claude/scripts/build_search_index.py and commit it")
    except Exception as e:  # noqa: BLE001
        err(f"could not check search index: {e}")
    for p in pages:
        t = p.read_text(encoding="utf-8")
        if 'class="site-search"' not in t or '/search.js' not in t or '/search.css' not in t:
            err(f"{p.relative_to(ROOT)}: header search box / search.css / search.js missing")
        if 'class="menu-toggle"' not in t or 'id="site-nav"' not in t or '/header.js' not in t or '/header.css' not in t:
            err(f"{p.relative_to(ROOT)}: header menu button / nav#site-nav / header.css / header.js missing")
    for p in pages:
        if GA_ID not in p.read_text(encoding="utf-8"):
            err(f"{p.relative_to(ROOT)}: Google Analytics tag {GA_ID} missing")
    print(f"  analytics: {len(pages)} pages checked")


def main():
    os.chdir(ROOT)
    print("Checking livingguidelines.org ...")
    check_guideline("adult/index.html", "rec", "adultSlugMap", 0)
    check_guideline("jia/index.html", "jia-rec", "jiaSlugMap", 1)
    check_headshots()
    check_analytics()

    if warnings:
        print(f"\nWARNINGS ({len(warnings)}) - review, may be known/expected:")
        for w in warnings:
            print(f"  - {w}")
    if errors:
        print(f"\nERRORS ({len(errors)}) - fix before publishing:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("\nOK - no errors.")


if __name__ == "__main__":
    main()
