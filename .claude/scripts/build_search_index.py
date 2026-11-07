#!/usr/bin/env python3
"""
Build the site-wide search index for livingguidelines.org.

Reads the two guideline pages and the about/resource pages and writes
/search-index.json, which /search.js loads in the visitor's browser the first
time they type in the header search box. Nothing runs on a server.

Run after ANY content change (new/updated recommendation, panellist,
publication, abbreviation, text page):

    python3 .claude/scripts/build_search_index.py

verify_site.py rebuilds the index in memory and errors if the committed file
differs, so a stale index cannot be published by accident.

Index shape (one entry per searchable thing):
  {
    "id":      "adult:rec-3" | "jia:jia-rec-2" | "about:panellists:12" ...
    "type":    "adult" | "jia" | "about"
    "badge":   short label shown in results ("Adult", "JIA", "Panel", "Abbreviation", ...)
    "title":   result heading
    "url":     root-anchored link; for recs "/adult/#slug" (search.js appends "/tab")
    "sections": [ {"label": "Recommendation", "tab": "recommendation", "w": 5, "text": "..."}, ... ]
  }
Section weights: title 10 (implicit), Category/tags 6, Recommendation 5,
Rationale/ETD/Practical 2, Data/More Info/about-page body 1.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "search-index.json"

TAB_LABELS = {
    "recommendation": "Recommendation",
    "etd": "Evidence to Decision",
    "practical": "Practical Info",
    "data": "Data",
    "moreinfo": "More Info",
}
TAB_WEIGHT = {"recommendation": 2, "etd": 2, "practical": 2, "data": 1, "moreinfo": 1}


def clean(text):
    text = re.sub(r"\s+", " ", text or "").strip()
    text = re.sub(r"\s+([.,;:!?)\]])", r"\1", text)   # "(methotrexate) ." -> "(methotrexate)."
    text = re.sub(r"([(\[])\s+", r"\1", text)
    return text


def node_text(el):
    if el is None:
        return ""
    for sup in el.select("sup"):  # drop citation superscripts from searchable text
        sup.decompose()
    return clean(el.get_text(" ", strip=True))


def slug_map(html, var):
    m = re.search(rf"window\.{var}\s*=\s*(\{{.*?\}});", html, re.S)
    out = {}
    if m:
        for k, v in re.findall(r"""["']?([\w-]+)["']?\s*:\s*["']([\w-]+)["']""", m.group(1)):
            out[v] = k  # rec id -> slug
    return out


def guideline_entries(rel, gtype, badge, var):
    html = (ROOT / rel).read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    slugs = slug_map(html, var)
    cards = {}
    for c in soup.select(".recommendation-card"):
        oc = c.get("onclick", "")
        m = re.search(r"openModal\('([^']+)'\)", oc)
        if m:
            cards[m.group(1)] = c
    entries = []
    for mod in soup.select(".modal-overlay"):
        rid = mod["id"].replace("modal-", "")
        title = node_text(mod.select_one(".modal-title"))
        card = cards.get(rid)
        meta = []
        if card is not None:
            meta.append(node_text(card.select_one(".card-category")))
            meta.extend(node_text(t) for t in card.select(".card-tag"))
            cond = card.get("data-conditions", "")
            meta.append(cond.replace("ra", "rheumatoid arthritis RA").replace("psa", "psoriatic arthritis PsA")
                        .replace("axspa", "axial spondyloarthritis axSpA").replace("sle", "systemic lupus erythematosus SLE")
                        if cond else "")
        sections = [{"label": "Category", "tab": "recommendation", "w": 6, "text": clean(" ".join(meta)), "snip": False}]
        for tab, label in TAB_LABELS.items():
            tc = mod.select_one(f"#{rid}-{tab}")
            if tc is None:
                continue
            tc = BeautifulSoup(str(tc), "html.parser")  # copy so sup removal doesn't affect others
            if tab == "recommendation":
                rec = " ".join(node_text(x) for x in tc.select(".recommendation-box, .remark-box"))
                for x in tc.select(".recommendation-box, .remark-box, .strength-badge"):
                    x.decompose()
                rest = node_text(tc)
                sections.append({"label": "Recommendation", "tab": "recommendation", "w": 5, "text": rec})
                if rest:
                    sections.append({"label": "Rationale", "tab": "recommendation", "w": 2, "text": rest})
            else:
                txt = node_text(tc)
                if txt:
                    sections.append({"label": label, "tab": tab, "w": TAB_WEIGHT[tab], "text": txt})
        slug = slugs.get(rid, rid)
        entries.append({
            "id": f"{gtype}:{rid}", "type": gtype, "badge": badge, "title": title,
            "url": f"/{gtype}/#{slug}", "sections": sections,
        })
    return entries


def page_soup(name):
    html = (ROOT / name).read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    for t in soup.select("script, style, header, footer, nav, svg"):
        t.decompose()
    return soup


def sectioned_page(name, title, badge="About"):
    """Split a text page into h2/h3 sections so snippets can say where they came from."""
    soup = page_soup(name)
    main = soup.find("main") or soup.body
    sections, cur_label, buf = [], "Overview", []

    def flush():
        txt = clean(" ".join(buf))
        if txt:
            sections.append({"label": cur_label, "w": 1, "text": txt})

    for el in main.descendants:
        if isinstance(el, NavigableString):
            continue
        if el.name in ("h1", "h2", "h3"):
            flush()
            buf = []
            cur_label = node_text(el) or cur_label
        elif el.name in ("p", "li", "td", "th", "dd", "dt", "blockquote") and not el.find(["p", "li", "td"]):
            buf.append(node_text(el))
    flush()
    return [{"id": f"about:{name}", "type": "about", "badge": badge, "title": title, "url": f"/{name}", "sections": sections}]


def panellists():
    soup = page_soup("panellists.html")
    out = []
    for i, c in enumerate(soup.select(".panellist-card")):
        name = node_text(c.select_one(".panellist-name"))
        name = re.sub(r"\s*(Chair|Co-Chair|Facilitator|Methodologist)\s*$", "", name)
        text = " · ".join(filter(None, [node_text(c.select_one(".panellist-profession")),
                                        node_text(c.select_one(".panellist-institution"))]))
        bio = node_text(c.select_one(".panellist-bio"))
        recs = node_text(c.select_one(".panellist-recs"))
        secs = [{"label": "Panel member", "w": 3, "text": text}]
        if bio:
            secs.append({"label": "Biography", "w": 1, "text": bio})
        if recs:
            secs.append({"label": "Recommendations", "w": 1, "text": recs})
        out.append({"id": f"about:panellists:{i}", "type": "about", "badge": "Panel", "title": name,
                    "url": "/panellists.html", "sections": secs})
    return out


def publications():
    soup = page_soup("publications.html")
    out = []
    for i, c in enumerate(soup.select(".publication-card")):
        title = node_text(c.select_one(".publication-title"))
        a = c.select_one(".publication-title a")
        meta = " ".join(filter(None, [node_text(c.select_one(".publication-authors")),
                                      node_text(c.select_one(".publication-journal"))]))
        out.append({"id": f"about:publications:{i}", "type": "about", "badge": "Publication", "title": title,
                    "url": "/publications.html", "ext": a["href"] if a else "",
                    "sections": [{"label": "Publication", "w": 2, "text": meta}]})
    return out


def media():
    soup = page_soup("media.html")
    out = []
    for i, c in enumerate(soup.select(".media-item")):
        title = node_text(c.select_one(".media-title"))
        text = " ".join(filter(None, [node_text(c.select_one(".media-source")), node_text(c.select_one(".media-excerpt")),
                                      node_text(c.select_one(".media-meta"))]))
        out.append({"id": f"about:media:{i}", "type": "about", "badge": "Media", "title": title,
                    "url": "/media.html", "sections": [{"label": "Media coverage", "w": 2, "text": text}]})
    return out


def abbreviations():
    """One entry per abbreviation, plus the synonym map used by search.js."""
    soup = page_soup("abbreviations.html")
    out, syn = [], {}
    for i, tr in enumerate(soup.select("tr")):
        term = node_text(tr.select_one(".abbreviation-term"))
        defn = node_text(tr.select_one(".abbreviation-definition"))
        if not term or not defn:
            continue
        out.append({"id": f"about:abbr:{i}", "type": "about", "badge": "Abbreviation", "title": f"{term} — {defn}",
                    "url": "/abbreviations.html", "sections": [{"label": "Abbreviation", "w": 3, "text": f"{term} {defn}"}]})
        key = term.lower()
        words = [w for w in re.findall(r"[a-z0-9]+", defn.lower()) if w not in ("of", "and", "the", "for", "in", "or", "a", "an", "to", "with")]
        if key and words:
            syn.setdefault(key, [])
            syn[key].append(defn.lower())  # full phrase; search.js matches it as a phrase
            if len(words) == 1:            # single-word expansion: also map the word back to the abbreviation
                syn.setdefault(words[0], []).append(key)
    return out, syn


# Extra search synonyms beyond what abbreviations.html provides (single-word expansions there are
# already mapped both ways automatically). Keep this to spelled-out phrases readers might type.
EXTRA_SYNONYMS = {
    "tnfi": ["tumour necrosis factor inhibitor"],
    "jaki": ["janus kinase inhibitor"],
}


def build():
    entries = []
    entries += guideline_entries("adult/index.html", "adult", "Adult", "adultSlugMap")
    entries += guideline_entries("jia/index.html", "jia", "JIA", "jiaSlugMap")
    entries += sectioned_page("how-to-use.html", "How to Use These Guidelines")
    entries += sectioned_page("who-we-are.html", "Who We Are")
    entries += sectioned_page("methodology.html", "Methodology")
    entries += sectioned_page("funding.html", "Funding & Support")
    entries += sectioned_page("coi.html", "Conflicts of Interest")
    entries += sectioned_page("contact.html", "Contact")
    entries += panellists()
    entries += publications()
    entries += media()
    abbr, syn = abbreviations()
    entries += abbr
    for k, v in EXTRA_SYNONYMS.items():
        syn.setdefault(k, [])
        for phrase in v:
            if phrase not in syn[k]:
                syn[k].append(phrase)
    for e in entries:
        e["sections"] = [s for s in e["sections"] if s.get("text")]
    return {"entries": entries, "synonyms": syn}


def main():
    data = build()
    body = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    data["hash"] = hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]
    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    n = len(data["entries"])
    print(f"wrote {OUT.relative_to(ROOT)}: {n} entries, {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
