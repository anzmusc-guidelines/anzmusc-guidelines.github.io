---
name: new-recommendation
description: >
  Use this skill whenever adding a new recommendation to the livingguidelines.org website.
  Triggers include: "add a new recommendation", "create a card and modal for [rec name]",
  "the [rec name] recommendation is ready to publish", "add the HCQ retinopathy rec",
  "new rec for [guideline]", "publish the [topic] recommendation". This skill covers the
  full lifecycle: preparation checklist, reference management, HTML build (card + 5-tab modal),
  academic citation hyperlinking, adding new condition tabs, and all post-build page-level
  updates (gateway page, panellists, abbreviations, feedback form, recommendation links).
  Always use this skill when building any new recommendation — even experienced developers
  should consult it to avoid branding and consistency errors between the card, modal, and tabs.
---

# New Recommendation Skill

This skill guides the **full lifecycle** of adding a new recommendation to either the Adult IA (`adult/index.html`) or JIA (`jia/index.html`) page. It is organised into three phases:

- **Phase 0: Preparation** — checklist of inputs, reference management, files needed
- **Phase 1: Build** — HTML card, modal, and all 5 tabs
- **Phase 2: Post-build** — page-level updates across the site

Read `references/html-templates.md` (in this skill's folder) for the complete copy-paste HTML templates.

---

# PHASE 0: PREPARATION

Complete this phase before writing any HTML. The goal is to have every input ready so the build can proceed without interruption.

## Step 0.1: Collect inputs via the checklist

Use or generate a checklist document (`.docx`) covering all required inputs. The checklist is organised into sections:

**A. Identity & Classification**
- [ ] Guideline: Adult IA or JIA?
- [ ] Recommendation ID — use next sequential number (e.g. `rec-19` for Adult IA, `jia-rec-11` for JIA)
- [ ] Category label (e.g. "Monitoring", "Glucocorticoids", "Non-pharmacological")
- [ ] Card title (short, suitable for the card grid)
- [ ] Modal title (can be longer/more descriptive, or same as card title)
- [ ] Strength: Strong For / Conditional For / Conditional Against / Strong Against / Consensus
- [ ] `data-conditions` (Adult IA only): space-separated disease codes. Standard set: `ra`, `psa`, `axspa`. New conditions (e.g. `sle`) may be added — see Step 3
- [ ] `data-tags`: space-separated lowercase keywords for behind-the-scenes search filtering (not visible to users). E.g. `monitoring hydroxychloroquine retinopathy screening`
- [ ] Card tag labels: the visible pill-shaped tags displayed on the card. E.g. "Monitoring", "csDMARDs", "Retinopathy"

> **Tags vs data-tags:** `data-tags` is the invisible search attribute on the card `<div>`. Card tag labels are the visible `<span class="card-tag">` pills inside the card body. They serve different purposes — `data-tags` should be comprehensive for search; card tag labels should be concise for display. They often overlap but don't have to match exactly.

**B. Recommendation Content**
- [ ] Recommendation text (exact panel-approved wording — never paraphrase)
- [ ] Remark(s), if any
- [ ] Rationale text
- [ ] ETD domain ratings and text (7 domains — see Phase 1, Step 4)
- [ ] Practical Info content

These may be provided in a separate document (Google Doc or uploaded file). If referencing the Google Doc, note the document ID so Claude can fetch it.

> **Verbatim text principle:** All recommendation content (recommendation text, remark, rationale, ETD domains, practical info) must be used verbatim from the source document. Do not summarise, reorganise, or rephrase any clinical content. Subheadings may be added to improve readability (e.g. grouping practical info bullets under thematic headers), but the text of each bullet or paragraph must be exactly as provided. Additionally:
> - **Preserve document structure:** If the source has bullet points (list items), render them as `<ul>/<li>` in HTML — do not flatten into `<p>` tags. If there are nested/indented sub-bullets, use nested `<ul>` elements.
> - **Preserve hyperlinks:** If the source document contains hyperlinks (e.g. to RANZCO guidelines, ARA patient info sheets), reproduce them as `<a>` tags in the HTML.
> - **Check formatting programmatically:** Use `python-docx` to inspect list levels (`w:numPr/w:ilvl`) and hyperlinks (`w:hyperlink` elements with relationship targets) in the source `.docx` file.

**C. Evidence & Data**
- [ ] PICO number and text
- [ ] Initial evidence synthesis Google Drive URL
- [ ] Initial evidence synthesis date (month and year)

**D. Dates & Panel**
- [ ] Panel meeting date (full date, e.g. "6 March 2026")
- [ ] Development month/year (= panel meeting month for new recs — used as "Updated" date)
- [ ] Panel members list with titles and roles

**E. Links**
- [ ] MAGICapp section URL (or "Not yet available" for placeholder)
- [ ] Feedback form URL — auto-generated from card title (see Step 13 and the encoding reference in the templates file)

---

## Step 0.2: Reference management

Academic references are managed in a spreadsheet (`Adult_guideline_reference_urls.xlsx` for Adult IA; a separate file for JIA). Each row has:

| Column | Content |
|---|---|
| Reference # | Sequential number (global across the whole guideline) |
| First author surname | For matching citations in text |
| Publication year | For matching citations in text |
| PubMed link | URL with hyperlink |
| Journal link | DOI URL with hyperlink (preferred for superscript links) |
| Recommendation | Which recommendation(s) use this reference |

**When new references are provided:**

1. **Accept `.ris` files** — parse using Python's `re` module to extract: first author (`AU` field, take surname before comma), year (`PY`), DOI (`DO`), PubMed URL (from `UR` fields matching `pubmed.ncbi.nlm.nih.gov` or `www.ncbi.nlm.nih.gov/pubmed`), and institutional author (`A3` field as fallback when no `AU`).

2. **Cross-reference against existing spreadsheet** — match on (first author surname, year) to identify which references are genuinely new vs already listed.

3. **Add new references** — append to the spreadsheet starting from the next sequential number. Add hyperlinks to both PubMed and DOI cells. Tag the Recommendation column.

4. **Handle citations in recommendation text** — the source text may use several citation formats, sometimes mixed within the same document:

   **Bracketed citations (most common):**
   - `[Author Year]` — e.g. `[Melles 2014]`
   - `[Author Year; Author Year]` — semicolon-separated, e.g. `[Marmor 2014; Browning 2025]`
   - `[Author Year, Author Year, Author Year]` — comma-separated, e.g. `[Alarcon 2007, Fessler 2005, Sciascia 2016]`
   - `[Author; Author; Author]` — short-form without years, e.g. `[Wolfe; Marmor; Daftarian]`. For these, map each surname to its most commonly cited year in the same document, or to the only matching entry in the spreadsheet.

   **Parenthetical citations:**
   - `(Author Year, Author Year)` — e.g. `(Alarcon 2007, Fessler 2005)`. Only replace if ALL parts match known references; otherwise leave unchanged (it may be a statistical expression like `(HR 1.56, 95% CI 1.31–1.86)`).

   **Narrative citations:**
   - Author name in running text followed by year: e.g. "Melles 2023 identified a cumulative incidence..." — add a superscript after the year.

   **Numbered citations:**
   - `[number]` — match directly to the Reference # column.

   Match all formats against (First author surname, Publication year) in the spreadsheet. Flag ambiguities (e.g. two papers by the same first author in the same year) for Sam to resolve. Note that some references may come from earlier recommendations (not tagged to the current rec) — check the full spreadsheet, not just the new references.

5. **Convert to superscript hyperlinks** in the HTML:
```html
<sup><a href="[DOI_OR_PUBMED_URL]" target="_blank" rel="noopener" title="[Author] ([Year])">[ref_number]</a></sup>
```
   - **Prefer DOI** (Journal link column); fall back to PubMed link if no DOI available
   - Multiple consecutive references: separate `<sup>` tags (no commas or spaces between them)
   - Always include `rel="noopener"` for external links
   - Style: teal colour for Adult IA, purple for JIA (handled by existing CSS)

**For references without a DOI or PubMed link** (e.g. institutional reports like RANZCO guidelines), use any direct URL provided in the `.ris` file's `UR` field. If no URL exists at all, use the reference number without a hyperlink and flag for Sam.

---

## Step 0.3: Confirm inputs needed at build time

The site pages themselves are already here in the repository — work on them directly; never on a downloaded or project-knowledge copy. Before starting, `git pull` (or fetch) so you are building on the current `main`.

Ask Sam for whatever is not in the repo:

1. **The completed checklist** (or answers in chat)
2. **The recommendation content document** (Google Doc ID, or uploaded file with all text for rec/remark/rationale/ETD/practical info)
3. **The reference spreadsheet** (`Adult_guideline_reference_urls.xlsx`) — shared as an `.xlsx` upload, not via Drive, so hyperlinks survive. Read links with `openpyxl` via `cell.hyperlink.target`, not `cell.value`.
4. **`recommendation-links.csv`** if it needs updating (it lives outside the repo — see Step 14)

---

# PHASE 1: BUILD

Do all build work on a new branch (e.g. `new-rec-19-<slug>`), never on `main`.

## Step 1: Choose the strength variant

| Strength | CSS class | Badge text | Icon |
|---|---|---|---|
| Strong For | `strong-for` | `⊕⊕ Strong Recommendation For` | See references file |
| Conditional For | `conditional-for` | `⊕ Conditional Recommendation For` | Plus icon |
| Conditional Against | `conditional-against` | `⊖ Conditional Recommendation Against` | Minus icon |
| Strong Against | `strong-against` | `⊖⊖ Strong Recommendation Against` | See references file |
| Consensus | `consensus` | `≈ Consensus Recommendation` | See references file |

The strength indicator circle on the card uses the same CSS class as the modal strength badge.

---

## Step 2: Adult IA vs JIA differences

| Feature | Adult IA (`adult/index.html`) | JIA (`jia/index.html`) |
|---|---|---|
| Card category colour | `var(--primary-teal)` | `var(--jia-purple)` |
| `data-conditions` attribute | Required (e.g. `ra`, `psa`, `axspa`, `sle`) | Not used — omit entirely |
| Rec ID prefix | `rec-N` | `jia-rec-N` |
| Modal ID | `modal-rec-N` | `modal-jia-rec-N` |
| `openModal()` call | `openModal('rec-N')` | `openModal('jia-rec-N')` |
| `switchTab()` calls | `switchTab('rec-N', 'tab')` | `switchTab('jia-rec-N', 'tab')` |
| Tab content IDs | `rec-N-recommendation`, etc. | `jia-rec-N-recommendation`, etc. |
| Feedback form base URL | `...1FAIpQLSevmap58hDjm9OAKdOB9gd1VSXUaRAIRn-q8XcYFgmwv2WczQ/viewform` | `...1FAIpQLSfarxWPaubepAaUzvm3HLxMgM57JlzKRtej-eWcRt7vw4wBAg/viewform` |
| MAGICapp base URL | `https://app.magicapp.org/#/guideline/LqRV3n` | `https://app.magicapp.org/#/guideline/10522/section/[SECTION_ID]` |
| Slug map variable | `window.adultSlugMap` | `window.jiaSlugMap` |

The feedback form `entry.1797546299` parameter value is the URL-encoded recommendation title.

---

## Step 3: Adding a new condition tab (Adult IA only)

If a new recommendation requires a `data-conditions` value that doesn't already exist as a tab (e.g. adding `sle` when the page currently only has `ra`, `psa`, `axspa`), the following changes are needed:

1. **Add a new tab button** in the condition tabs bar (find the existing tab buttons and add after the last one):
```html
<button class="condition-tab" data-condition="sle">Systemic Lupus Erythematosus</button>
```
Note: condition tabs do NOT use `onclick` handlers. They use `data-condition` attributes only — the JS binds via event listeners on the `.condition-tab` class and filters cards generically by matching the `data-condition` attribute value against each card's `data-conditions` attribute. No JS changes are needed when adding a new condition.

2. **Add new topic filter buttons** if the recommendation introduces `data-tags` values not already represented in the tag-filters section. Find the existing `<button class="tag-filter">` elements and add new ones:
```html
<button class="tag-filter" data-tag="hydroxychloroquine">Hydroxychloroquine</button>
<button class="tag-filter" data-tag="retinopathy">Retinopathy</button>
```
Like condition tabs, topic filter buttons use `data-tag` attributes and are handled generically by JS — no code changes needed.

3. **Set `data-conditions`** on the new card to include the new value (e.g. `data-conditions="ra sle"`).

4. **Consider existing recommendations** — if any existing recommendations should also appear under the new tab, their `data-conditions` attribute needs updating too. Ask Sam before making this change.

> **Important:** Adding a new condition tab is a structural change to the page. Always confirm with Sam which existing recommendations (if any) should appear under the new tab.

---

## Step 4: The 5 modal tabs

Every modal has exactly these tabs in this order:

1. **Recommendation** — strength badge, recommendation box, optional remark box, rationale text
2. **Evidence to Decision (etd)** — 7 GRADE ETD domains (see below)
3. **Practical Info (practical)** — implementation notes, patient considerations, resource links
4. **Data (data)** — PICO section + Evidence Summaries list
5. **More Info (moreinfo)** — panel members list + panel meeting date

### ETD domain structure

The 7 standard domains, in order (use these exact titles — they must match existing recommendations):
1. Benefits and Harms
2. Certainty of the Evidence
3. Values and Preferences
4. Resources
5. Equity
6. Acceptability
7. Feasibility

Each domain uses this structure:
```html
<div class="etd-domain">
    <div class="etd-domain-header">
        <span class="etd-domain-title">[Domain name]</span>
        <span class="etd-rating">[Rating, e.g. "Low", "Moderate", "Favours intervention"]</span>
    </div>
    <div class="etd-domain-text">
        <p>[Domain assessment text]</p>
    </div>
</div>
```

### Post-import formatting check (REQUIRED for any content pasted from MAGICapp)

When ETD text (or any other tab content) is pasted in from MAGICapp, **list items frequently get flattened into a single run-on paragraph during transfer**. The words are all there and the HTML is valid, but what should be a `<ul>` of bullet points ends up as one long `<p>` with the items separated only by extra spaces. The result reads poorly and obscures the parallel structure the original author intended.

This is most common in the Benefits and Harms domain, where MAGICapp authors use bullet lists heavily (e.g. enumerating participant groups, outcome lists). It also occurs in Practical Info and rationale paragraphs.

**Check after every paste:**
- Scan each `<p>` in the new content for run-on patterns: multiple capitalised phrases separated by spaces (not punctuation), parallel grammatical structures, or paragraphs that re-read as obviously list-shaped.
- Compare side-by-side against the MAGICapp source — anywhere MAGICapp shows a bulleted list, the website must also show a `<ul>` with matching `<li>` items.
- Re-render any flattened lists as a `<ul>`/`<li>` block using the same wording.

**Heuristic:** if a paragraph contains the same key phrase repeated 2+ times in parallel constructions (e.g. "In people using X... In people using Y... In people using Z..."), it is almost certainly a flattened list.

Example of the failure mode (seen in rec-3 Benefits and Harms):

```html
<!-- WRONG: list flattened into a paragraph on import -->
<p>In people using csDMARDs alone, dose reduction or discontinuation of csDMARDs versus continuation of csDMARDs  In people using background b/tsDMARDs, dose reduction or discontinuation of csDMARDs (with continued background treatment of b/tsDMARD) versus continuation of csDMARDs (and continued dose of b/tsDMARD) In people using background b/tsDMARDs, dose reduction or discontinuation of both csDMARDs and b/tsDMARDs versus continuation of csDMARDs (with or without continued b/tsDMARD use)</p>

<!-- CORRECT: matches MAGICapp formatting -->
<ul>
    <li>In people using csDMARDs alone, dose reduction or discontinuation of csDMARDs versus continuation of csDMARDs</li>
    <li>In people using background b/tsDMARDs, dose reduction or discontinuation of csDMARDs (with continued background treatment of b/tsDMARD) versus continuation of csDMARDs (and continued dose of b/tsDMARD)</li>
    <li>In people using background b/tsDMARDs, dose reduction or discontinuation of both csDMARDs and b/tsDMARDs versus continuation of csDMARDs (with or without continued b/tsDMARD use)</li>
</ul>
```

### MAGICapp link format (REQUIRED — recommendation-specific URL, not guideline-level)

The "View in MAGICapp" link in the modal footer **must point to the specific recommendation**, not to the guideline as a whole.

- ✅ Correct: `https://app.magicapp.org/#/guideline/{guideline-id}/section/{section-id}` (e.g. `.../guideline/11207/section/260420`)
- ❌ Wrong: `https://app.magicapp.org/#/guideline/{guideline-id}` with no `/section/` path — this opens the guideline at whatever recommendation MAGICapp lands on by default, taking the user to the wrong content.

**To obtain the rec-specific URL:** open the recommendation in MAGICapp in a browser and copy the full URL from the address bar. The portion after `/section/` is the section ID.

**URL format notes:**
- The Adult IA guideline can be addressed by either a numeric ID (e.g. `11207`) or a short alphanumeric code (e.g. `LqRV3n`) — both have been seen in the wild. Use whichever appears in the URL when you copy it from MAGICapp.
- The recommendation-specific path uses `/section/{id}` in the current MAGICapp URL scheme. An older format using `/rec/{id}` also exists on some recommendations. Either is acceptable provided it deep-links to the specific recommendation; the failure mode to avoid is a guideline-level URL with no rec/section path at all.

> **Shared MAGICapp sections are NOT duplicates.** Some site recommendations intentionally deep-link to the *same* MAGICapp section because MAGICapp groups multiple recommendations under one combined section. Confirmed example: JIA rec-7 (Choice of intra-articular glucocorticoid) and rec-8 (Use of anaesthesia for intra-articular injection) both correctly point to `section/240276` — "6.2 Intra-articular therapies for JIA" — which contains both recommendations. **Do not treat two recommendations sharing a section ID as a copy-paste error to fix.** Verify against MAGICapp first: if the section legitimately contains both recommendations, the shared link is correct.

Many existing recommendations on the site currently have only the guideline-level URL (the deep-linking convention was not consistently applied historically). These are not blockers for new builds but should be batched and fixed when convenient — `verify_site.py` lists them as warnings.

---

## Step 5: Card placement

New cards go at the **end** of their thematic section within the recommendations grid, or in a new section if the category is new. Do not insert mid-section.

For Adult IA: cards are grouped by condition tabs (RA, PsA, axSpA, and any new conditions) via `data-conditions`. A card with `data-conditions="ra psa axspa"` appears under all three tabs.

For JIA: no condition tabs — all cards are in a single grid.

---

## Step 6: Modal placement

Modals are placed after the closing `</main>` tag and before the `<footer>`, in sequential ID order. Add the new modal after the last existing modal.

---

## Step 7: "Updated" date for new recommendations

For new recommendations, the card and modal "Updated" date = the **month of recommendation development** (i.e. the panel meeting month), not an evidence search date.

- Card: `<span class="card-updated">Updated [Abbrev Month] [YYYY]</span>`
- Modal footer: `<span class="card-updated">Last updated: [Full Month] [YYYY]</span>`

---

## Step 8: Academic reference hyperlinking

After building the card and modal with all content, convert all academic citations in the text to superscript hyperlinks:

1. **Load the reference spreadsheet** using `openpyxl`. Extract hyperlinks via `cell.hyperlink.target`. Build a lookup dict mapping `"Author Year"` strings to `(ref_number, url)` tuples.

2. **Find all citations** in the HTML text — see Step 0.2 for the full list of citation formats (bracketed, parenthetical, narrative, short-form, numbered).

3. **Process in order:** bracketed `[...]` first, then parenthetical `(...)`, then narrative. This avoids double-processing.

4. **For short-form citations** (author surname without year, e.g. `[Wolfe; Daftarian]`): map each surname to its most commonly cited year in the document, or to the only matching entry in the spreadsheet. Build a separate short-form lookup dict.

5. **Replace with superscript HTML:**
```html
<sup><a href="[URL]" target="_blank" rel="noopener" title="[Author] ([Year])">[number]</a></sup>
```

6. **Prefer DOI** (`Journal link` column) over PubMed. For references with neither, use any available URL or leave as plain superscript text.

7. **Do not modify citations inside HTML attributes** (e.g. `href`, `title`) — only replace citations in visible text content.

8. **Verify all citations resolved** — count the total superscript links generated and compare against the number of unique citations in the source text. Flag any unresolved citations.

---

## Step 9: Final consistency check

### 9.0 Automated verification (REQUIRED)

Run from the repo root:

```bash
python3 .claude/scripts/verify_site.py
```

This checks the **whole page**, not just the new recommendation: every card's `onclick` has a matching modal; no two cards open the same modal; no orphaned modals; ids are contiguous; card and modal categories/titles agree; card and modal footer dates match; `switchTab()` calls and tab ids belong to their own modal; every rec has a slug and every slug points at a real rec; the hero-badge count matches the number of cards; headshot references resolve; every page carries the analytics tag.

It exists because of a real bug: a one-character typo put `openModal('rec-18')` on the lab-monitoring card, so clicking rec-10 opened rec-18. That kind of error is invisible when you look only at the new rec.

If any **ERROR** is reported, **stop and fix before committing**, and tell Sam what was wrong. **WARNINGS** are often known items (e.g. guideline-level MAGICapp links; rec-18's card date not matching its Data tab — see `.claude/site-decisions.md`); mention any new ones.

### 9.1 Manual card & modal checks

**Card & Modal:**
- [ ] All `switchTab()` calls use the correct rec ID
- [ ] All tab content `id` attributes follow the `[rec-id]-[tab]` pattern
- [ ] Card date, modal footer date, and Data tab date all consistent (same month/year)
- [ ] `data-tags` on card matches the tags visible in the card body
- [ ] Adult IA: `data-conditions` set correctly; JIA: no `data-conditions` attribute
- [ ] Feedback URL has correct base URL for the guideline (Adult vs JIA)
- [ ] MAGICapp link uses the **rec-specific** URL format (`/guideline/{id}/section/{section-id}`), not the guideline-level URL — see Step 4
- [ ] Panel members list complete in More Info tab (with correct CSS classes for chair/facilitator)
- [ ] Initial evidence synthesis link in Data tab
- [ ] All academic citations converted to superscript hyperlinks

**Page-level (if applicable):**
- [ ] If new condition tab added: tab button exists with correct `data-condition` attribute
- [ ] If new topic tags introduced: new `tag-filter` buttons added
- [ ] Gateway What's New updated
- [ ] Coming Soon removed/updated
- [ ] Deep-link mapping added in script block
- [ ] Panellists page: new members added, all members' rec lists updated
- [ ] Abbreviations page: new abbreviations added in alphabetical order
- [ ] `recommendation-links.csv` updated
- [ ] Evidence Tables Google Doc entry provided
- [ ] Google Form dropdown update flagged as manual to-do
- [ ] Recommendation count updated: hero badge on guideline page, gateway page pathway card
- [ ] About section text updated (if guideline scope expanded)
- [ ] `sitemap.xml` `lastmod` refreshed for changed pages (real commit date — see site-decisions)

---

# PHASE 2: POST-BUILD UPDATES

After the card and modal are complete, the following page-level updates are needed. Confirm each with Sam before proceeding.

## Step 10: Gateway page updates

**What's New section** (`index.html` — the gateway page):
- Add a "New Recommendation" entry with the teal "New" badge
- Use the recommendation title and the development month/year
- The entry should link to the recommendation on the guideline page (not open a modal directly from the gateway)

**Coming Soon section:**
- Remove or update the Coming Soon item if this recommendation was listed there
- If another recommendation is in the pipeline, update with new title and anticipated date
- If nothing is planned, remove the Coming Soon section entirely (or leave empty/commented out)

## Step 10b: Guideline page What's New section

The guideline page itself (e.g. `adult/index.html`) also has a What's New panel at the top. Update it with the new recommendation title and date. This is separate from the gateway page What's New.

## Step 10c: About section text

If the new recommendation expands the scope of the guideline to cover a new disease area (e.g. adding SLE to a guideline that previously only covered RA, PsA, axSpA), update the About section text to reflect the expanded scope.

## Step 10d: Deep-link mapping

The guideline page has a JavaScript mapping from slug URLs to recommendation IDs (e.g. `'hcq-retinopathy': 'rec-18'` in `window.adultSlugMap`). Add an entry for the new recommendation. The slug should be a short, URL-friendly identifier.

## Step 11: Panellists page

Check whether any panel members for this recommendation are **not already on the panellists page**. For new panellists:

- Add their entry in the correct **alphabetical position** (by surname)
- Include: name with title, guideline badge(s), profession, institution, bio (if available)
- Add headshot if available (use the `panellist-headshot` skill); otherwise use initials placeholder (e.g. `<div class="panellist-avatar">EC</div>`)
- Add COI declaration link if available; otherwise leave the declaration line empty (flag as a to-do)
- New panellists who are not rheumatologists (e.g. ophthalmologists, pharmacists, consumer representatives) should still be listed — the panellists page covers all guideline contributors
- Use the appropriate `data-profession` value (e.g. `ophthalmologist`, `pharmacist`, `consumer`, `rheumatologist`)

**For ALL panel members** (new and existing), update their `panellist-recs` div to include the new recommendation title. This is the list of recommendations each panellist contributed to.

**Panel member CSS classes in the More Info tab:**
- Chair/facilitator roles: `<span class="panel-member chair">Dr Samuel Whittle (Chair &amp; Facilitator)</span>`
- Regular voting members: `<span class="panel-member">Dr Elisa Cornish</span>`
- Include title (Dr/Prof/A-Prof/Mr/Ms) for all members

## Step 12: Abbreviations page

Check whether the recommendation text introduces any abbreviations not already on the abbreviations page. Common candidates for new recommendations in specialised areas:
- Disease-specific terms (e.g. SLE, HCQ)
- Clinical test abbreviations (e.g. OCT, SD-OCT, FAF, mfERG)
- Scoring systems or frameworks

Add any missing abbreviations in alphabetical order.

## Step 13: Feedback form

The recommendation card's "Suggest feedback" link uses a pre-filled Google Form URL. Two things to check:

1. **Pre-filled URL** — Claude auto-generates this from the card title using URL encoding. No manual action needed for the link itself.

2. **Google Form dropdown** — the Google Form itself may have a dropdown listing all recommendations. Adding a new option to the form is a **manual step** that Sam or Vanessa must do in the Google Forms editor. Flag this as a to-do item.

## Step 14: Recommendation links

`recommendation-links.csv` is kept **outside** this repository (it is not published). Ask Sam for the current copy, add the new row, and return the updated file. Columns:

```
Guideline,Rec #,Title,Numeric URL,Slug URL
Adult IA,18,Retinopathy screening for adults taking hydroxychloroquine,https://livingguidelines.org/adult/#rec-18,https://livingguidelines.org/adult/#hcq-retinopathy
```

The slug URL uses the same slug as the deep-link mapping (Step 10d).

## Step 15: Evidence Tables Google Doc

Add an entry for the new recommendation's PICO in the `Adult_Guideline_Evidence_Tables` Google Doc (Doc ID: `1o9ncE6gWrJWJylOAXFOqd1nxLZzEz1jZFkjGs8ysMfw`). Follow the existing format:

```
***SECTION HEADING IN CAPS AND ITALICS:***

**PICO [N]: [Recommendation title]**
Initial Evidence Synthesis ([Month Year]) - please click **HERE** [linked to Google Drive URL]
```

Claude cannot directly edit Google Docs — provide the exact text for Sam/Vanessa to paste.

## Step 16: Update recommendation count

Update the recommendation count in **three places**:
1. **Guideline page hero badge** — the hero banner contains a badge showing the total number of recommendations (e.g. `19 Recommendations` inside a `<span class="hero-badge">`). Update this to the new total. (`verify_site.py` checks this one.)
2. **Guideline page intro text** — if there is any other introductory text mentioning the number of recommendations, update it too.
3. **Gateway page** — the pathway card for the guideline displays a numeric count (e.g. `<div class="pathway-stat-value">19</div>`). Update this to the new total. Also update the pathway card subtitle if the guideline's scope has changed.

## Step 17: Commit and open a pull request

1. Re-run `python3 .claude/scripts/verify_site.py` — must report no errors.
2. Commit on the branch and open a pull request against `main`. **Never push to `main` directly** — GitHub Pages publishes it straight to livingguidelines.org.
3. In the PR description, list: pages changed; anything you deviated from the source text or skill on (and why); manual to-dos for Sam/Vanessa (Google Form dropdown, Evidence Tables doc, recommendation-links.csv, COI links, headshots).

---

## Reference file

See `references/html-templates.md` for complete copy-paste HTML templates for:
- The full card block
- The full modal block (all 5 tabs)
- All strength indicator icon SVGs
- Remark box HTML
- Feedback URL encoding reference
