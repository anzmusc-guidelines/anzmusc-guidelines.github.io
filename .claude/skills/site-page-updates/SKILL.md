---
name: site-page-updates
description: >
  Use for routine edits to livingguidelines.org pages other than adding a recommendation or
  recording an evidence search: adding or editing a panel member, adding a declaration of
  interests (COI) link, adding a publication, adding media coverage, adding an abbreviation,
  editing methodology/funding/contact/who-we-are text, or sharing direct links to
  recommendations. Triggers: "add [name] to the panel", "new COI declaration for…",
  "add this paper to publications", "we were in the news…", "add the abbreviation…",
  "send me the links to the recommendations".
---

# Site Page Updates Skill

Templates and rules for the smaller, non-recommendation edits. Ported (Nov 2026) from the
January 2026 `CONTENT-UPDATE-GUIDE.md`, with every template re-checked against the current
markup. For new recommendations use `new-recommendation`; for evidence searches use
`quarterly-evidence-update`; for photos use `panellist-headshot`.

**Workflow for every change here:** branch → edit → `python3 .claude/scripts/verify_site.py`
→ commit → pull request. Never commit to `main` (it is the live site).

## Which file to edit

| What | File |
|---|---|
| Adult IA / JIA recommendations | `adult/index.html` / `jia/index.html` (use the other skills) |
| Panel members | `panellists.html` |
| Declarations of interest | `coi.html` |
| Publications | `publications.html` |
| Media coverage | `media.html` |
| Abbreviations | `abbreviations.html` |
| Methodology / funding / contact / who we are / how to use | `methodology.html`, `funding.html`, `contact.html`, `who-we-are.html`, `how-to-use.html` |
| Gateway (home) page | `index.html` |

Header and footer navigation are **duplicated on every page** — a menu change must be made in
all of them (and in `404.html`, where links are root-anchored: `/coi.html`, not `coi.html`).

---

## 1. Panel member (`panellists.html`)

Insert in **alphabetical order by surname** within the grid. Copy the surrounding markup — current
template:

```html
<div class="panellist-card" data-profession="rheumatologist" data-guideline="adult">
    <div class="panellist-avatar">XX</div>
    <div class="panellist-info">
        <h3 class="panellist-name">Dr Firstname Lastname</h3>
        <div class="guideline-badges"><span class="guideline-badge adult">Adult IA</span></div>
        <p class="panellist-profession">Rheumatologist</p>
        <p class="panellist-institution">Institution</p>
        <p class="panellist-bio">Bio text (verbatim from the panellist).</p>
        <div class="panellist-recs"><span class="rec-label adult">Adult IA:</span> Rec title, Rec title</div>
        <p class="panellist-declaration"><a href="[COI LINK]" target="_blank">View Declaration of Interests [external-link SVG — copy from a neighbouring card]</a></p>
    </div>
</div>
```

- `data-guideline`: `adult`, `jia` or `both`. For both, show both badges
  (`…adult">Adult IA</span><span class="guideline-badge jia">JIA</span>`) and both rec lines
  separated by `<br>` (`<span class="rec-label jia">JIA:</span> …`).
- `data-profession`: use one of the values already on the page so the filter works —
  `rheumatologist`, `paediatric-rheumatologist`, `rheumatology-nurse`, `gp`, `paediatrician`,
  `immunologist`, `ophthalmologist`, `orthopaedic-surgeon`, `pharmacist`, `physiotherapist`,
  `podiatrist`, `consumer`, `methodologist`, `evidence-team`. A genuinely new profession also
  needs a new filter button — ask Sam first.
- Avatar: initials until a photo arrives (then use `panellist-headshot`). Chair/facilitator
  avatars carry the extra `chair` class, and their name gets a role badge:
  `<h3 class="panellist-name">Prof Name<span class="role-badge chair">Chair</span></h3>`.
- No COI link yet → leave the declaration paragraph out and list it as a to-do in the PR.
- If the person sat on a recommendation panel, also add them to that rec's More Info tab
  (see `new-recommendation` Step 11).

## 2. Declaration of interests (`coi.html`)

Three tables under "Panel Member Declarations": Both Guidelines, Adult Inflammatory Arthritis,
Juvenile Idiopathic Arthritis. Add a row in alphabetical order by
surname in the right table:

```html
<tr>
    <td class="panellist-name">Dr Firstname Lastname</td>
    <td><a href="[GOOGLE SHEETS LINK]" target="_blank" class="declaration-link">View declaration [external-link SVG — copy from a neighbouring row]</a></td>
</tr>
```

Use the same link on the person's `panellists.html` card.

## 3. Publication (`publications.html`)

```html
<div class="publication-card featured">
    <span class="publication-badge guideline">Guideline</span>
    <div class="publication-title">
        <a href="https://doi.org/[DOI]" target="_blank">Publication title</a>
    </div>
    <div class="publication-authors">Whittle SL, Glennon V, Buchbinder R</div>
    <div class="publication-journal">Journal Name. Year;Volume:Pages</div>
</div>
```

- Badge: `guideline` (teal) or `methodology` (blue); place in the matching section, newest first.
- Link by DOI (`https://doi.org/…`), not PubMed.
- Authors in Vancouver style as on the paper; don't abbreviate the title.

## 4. Media coverage (`media.html`)

Copy the nearest existing `<article class="media-item">` block whole — it contains two inline
SVGs (source icon and date icon) that must be kept. For an article, copy a news entry (e.g. The
Hospital Research Foundation Group); for audio, copy the Rheumatology Republic (Podcast) entry so
you get its icon and "Listen/Read" label. Update: source name, title + link, one-sentence
description, date, and the link. Newest first.

## 5. Abbreviation (`abbreviations.html`)

Add in alphabetical order:

```html
<tr>
    <td class="abbreviation-term">ABBR</td>
    <td class="abbreviation-definition">Full definition</td>
</tr>
```

Use the expansion exactly as it appears in the guideline text.

## 6. Text pages (methodology, funding, contact, who we are, how to use)

Reproduce text Sam supplies verbatim. Keep existing headings/classes. The funding page holds the
site disclaimer — don't remove or reword it without Sam asking.

## 7. Direct links to recommendations

Don't hand-maintain a list. Generate it from the site:

```bash
python3 .claude/scripts/rec_links.py --markdown        # readable table
python3 .claude/scripts/rec_links.py --out links.csv   # CSV for sharing
```

Both `#rec-N` / `#jia-rec-N` and slug forms (`#hcq-retinopathy`) work. Older formats
(`#ia-rec-N`, `index.html#…`) appeared in an old cheatsheet — `#ia-rec-N` does **not** work.

---

## Before opening the PR

- `verify_site.py` passes (it checks the analytics tag on every page — any new page needs the
  GA block immediately before `</head>`; see site-decisions).
- New external links have `target="_blank"`.
- Preview the changed page locally (`python3 -m http.server`, then open it) and check it on a
  narrow (phone-width) window.
- PR description lists what changed and any to-dos (missing COI link, missing photo, etc.).
