# Living Guidelines — Site Decisions Register

**Purpose.** A single, durable record of *settled decisions*, *conventions*, and *known
non-bugs* for livingguidelines.org. Unlike the dated work-summary logs (which record "what we
did on date X"), this document records "what is true and why" — the things that should inform or
constrain future work.

**Where this lives.** In the repository at `.claude/site-decisions.md`, referenced from
`.claude/CLAUDE.md` so every Claude Code session on the site reads it before making changes.
(Moved here in November 2026 from claude.ai project knowledge, so it is version-controlled
alongside the code it describes. Files under `.claude/` are not published by GitHub Pages.)

**How to use it.** Before "fixing" something that looks wrong, check the *Known non-bugs* section.
Before changing an established pattern, check *Design & architecture decisions* and *Conventions*.
Add new entries as decisions are made — keep each one to a decision + a one-line rationale + a date.

---

## 1. Known non-bugs — do NOT "fix" these

Things a code review or a fresh pair of eyes will likely flag as errors, but which are correct
by design. Verify against these before changing.

- **JIA rec-7 and rec-8 share MAGICapp `section/240276`** *(confirmed 5 Jul 2026)*
  Both intentionally deep-link to the same section — "6.2 Intra-articular therapies for juvenile
  idiopathic arthritis" — because MAGICapp groups both recommendations (choice of intra-articular
  glucocorticoid; use of anaesthesia for intra-articular injection) under that single section.
  Two site recommendations sharing one MAGICapp section ID is **not** a copy-paste error. In
  general: verify a suspected duplicate section link against MAGICapp before treating it as a bug.

- **rec-10 (Exercise therapy) MAGICapp link is correct as `section/240279`** *(confirmed 5 Jul 2026)*
  It fits the sequence (rec-9 foot orthoses = 240278). The same recommendation can also be
  addressed as `guideline/nyxpZL/rec/E865MV` — the alphanumeric guideline code and `/rec/` path
  are valid equivalents of the numeric `10522` / `/section/` form (just as the Adult guideline is
  both `11207` and `LqRV3n`). The site uses the numeric `10522/section/…` form consistently for JIA.

- **Adult rec-18 card date does not match its Data tab** *(known quirk)*
  rec-18 (HCQ retinopathy screening) is dated by its development month, which is later than its
  initial evidence synthesis. `verify_site.py` may warn about it; this is expected.

- **JIA card categories are shortened forms of the modal categories** *(noted 4 Nov 2026)*
  e.g. card "Non-pharmacological" vs modal "Non-pharmacological interventions for JIA". Intentional
  for card space; `verify_site.py` accepts one containing the other.

---

## 2. Design & architecture decisions (with rationale)

- **Single shared `scripts.js` across Adult and JIA pages** *(3 Jul 2026)*
  JIA previously carried a private inline copy that had drifted from the Adult page's shared script.
  Unified into one script (condition-tab logic made optional, since JIA has no condition tabs) so
  fixes are made once and both pages — and every future recommendation — benefit automatically.

- **Teal palette darkened for WCAG AA** *(3 Jul 2026)*
  `--primary-teal` `#0d9488` → `#0f766e` (now 5.47:1 on white); `--primary-teal-dark` `#0f766e` →
  `#115e59`. Chose "Approach A" — change the palette variable once per page — over per-rule
  surgical fixes, because one clean rule is more maintainable for a self-maintained site.
  New teal-on-white / white-on-teal combinations must stay ≥4.5:1 for text.

- **Sentinel-based modal focus trap (for Safari)** *(3 Jul 2026)*
  Safari skips `<a>` links in tab order by default, so a "last focusable element" computed from
  links let focus escape. Fix: inject two invisible focusable `<div>` sentinels just inside the top
  and bottom of each modal; being divs (not links), every browser includes them in tab order. This
  is browser-agnostic and must not be reverted to a link-based computation.

- **SLE described as retinopathy-screening scope, not lupus management** *(5 Jul 2026)*
  When adding SLE to the Adult page metadata/schema (for rec-18 discoverability), it was framed
  specifically as "hydroxychloroquine retinopathy screening for people with systemic lupus
  erythematosus," not as general lupus management — because the guideline covers one screening
  recommendation relevant to HCQ users, not SLE treatment. Keep this framing if reworded.

- **No separate clinical disclaimer added** *(5 Jul 2026)*
  A substantive liability disclaimer already exists at the bottom of the funding page (best
  evidence at compilation; no liability for loss/damage from reliance). A new one was judged
  unnecessary. Open, optional enhancement: surface a "Disclaimer" link in the guideline-page
  footers for discoverability — not done, and not required.

- **Site work happens in Claude Code against this repo, via pull requests** *(4 Nov 2026)*
  Conventions, skills and the verification script live in `.claude/`. Changes go on a branch and
  through a PR so Sam reviews the diff before GitHub Pages publishes `main`.

---

## 3. Conventions to apply in future work

- **MAGICapp URLs live in a master list** *(7 Nov 2026)*
  `.claude/data/adult-magicapp-urls.csv` and `jia-magicapp-urls.csv` hold the "View in MAGICapp"
  URL for every recommendation (supplied by Sam, 7 Nov 2026; Adult uses the `LqRV3n/rec/…` form,
  JIA the `10522/section/…` form). `verify_site.py` errors if a modal's link differs from the CSV.
  When a URL changes or a rec is added, update the CSV and the page together. Sam should never
  have to re-collect these.

- **Every pull request targets `main` — never stack one PR on another's branch** *(4 Nov 2026)*
  A PR based on another PR's branch does not get retargeted to `main` when that branch merges;
  Sam merged such a PR (#5) and nothing went live. If two changes would conflict, finish and merge
  the first, then branch the second from the updated `main`.

- **Sitemap `lastmod` = real git commit date** *(5 Jul 2026)*
  When refreshing `sitemap.xml`, use each file's actual last-commit date (from the GitHub commits
  API or `git log -1 --format=%cs -- <file>`), not a blanket "today." Leave `changefreq` and
  `priority` untouched unless there's a reason.

- **Google Analytics** *(5 Jul 2026)*
  Measurement ID `G-XQKQVSHVS5`. The standard gtag block goes immediately before `</head>`. All
  pages carry it (checked by `verify_site.py`). Any new page must include the same block.

- **Per-recommendation analytics events** *(8 Nov 2026)*
  Opening a modal doesn't change the page, so GA4's default page views couldn't say which
  recommendation was read. `scripts.js` now sends `view_recommendation` (once per opening, from
  `openModal`) and `view_recommendation_tab` (from `switchTab`, only when the tab actually changes),
  each with `recommendation_id`, `recommendation_slug`, `recommendation_title`, `guideline`.
  Chosen over "virtual page views" so real page-view counts stay honest. The parameters only show
  in GA4 once registered as event-scoped custom dimensions (Sam's one-off job, see the
  `analytics-report` skill). Reports are pulled with `.claude/scripts/ga4_report.py` using a
  read-only service account whose key lives in Sam's Claude cloud environment, never in the repo.

- **Social-share image is the ANZMUSC logo** *(7 Nov 2026)*
  `images/og-share.png` (1200×630, logo centred on white) is the `og:image` / `twitter:image` on
  every page except the 404. Sam chose the plain logo; a designed card can replace the file later
  without touching any page. Every indexable page carries the full Open Graph + Twitter block.
- **Phone header: compact logo row + "Menu" button; shared `header.css` / `header.js`** *(7 Nov 2026)*
  Before: on a phone the header (search strip, three wrapped partner links, 50 px logo, two-line
  title, wrapped menu) was ~440 px tall — over half the screen — and inconsistent between pages
  (only the gateway hid its nav). Now, at ≤768 px: partner links hidden (they are in the footer),
  30 px logo, 15 px title, and the nav collapses behind a Menu button with tap-to-expand sections.
  Header ≈ 126–154 px. Desktop is unchanged, except dropdown headings now also toggle on
  click/Enter (keyboard access). Rules are prefixed `body header …` so they beat each page's own
  inline styles, which load later. Header markup (menu button, `nav#site-nav`) is duplicated on
  every page like the rest of the header.

- **Site-wide search is a generated static index searched in the browser** *(7 Nov 2026)*
  Chosen over Pagefind because the site has no build step. `build_search_index.py` extracts every
  recommendation (per tab, weighted: title > category/tags > recommendation > rationale/ETD/practical
  > data/more-info), the about pages (per heading), each panellist, publication, media item and
  abbreviation into `search-index.json` (~600 KB, gzipped by GitHub Pages). `search.js` does AND
  matching with light stemming and abbreviation synonyms, ranks, and deep-links to `#slug/tab`
  (`scripts.js` opens the tab). Search terms are logged to GA as `search` events (Sam approved).
  The per-page card filter on the guideline pages is kept; it does a different job. Decisions by
  Sam: box on every page; about pages included; GA logging on.
  Abbreviations on `abbreviations.html` become search synonyms automatically (MTX, TNFi, JAKi,
  NMA, PsA, axSpA, IA were added to the page for this on 7 Nov 2026); `EXTRA_SYNONYMS` in the
  builder holds only spelled-out phrases the page does not give.

- **Favicon and per-page SEO tags** *(4 Nov 2026)*
  Every page links `/favicon.ico`, `/favicon-32x32.png` and `/apple-touch-icon.png` (root-anchored,
  generated from the ANZMUSC emblem) and carries a `<meta name="description">` plus
  `<link rel="canonical">`. New pages must include all of these. External links that open in a new
  tab carry `rel="noopener"`.

- **404 page uses root-anchored paths** *(5 Jul 2026)*
  `404.html` lives at the repo root (GitHub Pages serves one root-level 404 for all missing paths).
  Because the browser keeps the *missing* URL in the address bar, every internal link/asset in the
  404 must be root-anchored (`/`, `/adult/`, `/jia/`, `/anzmusc-logo-header.png`) or it will break
  on deep paths. Keep the page `noindex` and keep the GA tag (so 404 hits are tracked).

- **Gateway research-survey banner removed** *(4 Nov 2026)*
  The Monash guideline-uptake survey (MUHREC 52237) closed, so the banner and its CSS were deleted
  from `index.html`. Don't reinstate without a new, open survey. Media page deliberately left at
  two items (nothing newer to add); funding page ALEC period shown as 2024–2026.

- **"Update in progress" placeholder for recs awaiting a living NMA update** *(4 Nov 2026)*
  Where a recommendation's last evidence date is old only because a living network meta-analysis
  is being finalised for it (Adult rec-0 initial DMARD therapy, rec-2 DMARD after TNFi), the card
  and modal footer show an `Update in progress` badge (`.card-updated.card-updated-pending`) instead
  of a date, plus a one-line `.pending-note` in the modal footer. Rationale: a 2021/2022 date on a
  living guideline reads as neglect when the work is actually under way. Both card and modal must
  carry the badge (verify_site.py errors if only one does, and warns while it is in place). To
  clear it, follow the `quarterly-evidence-update` skill: restore `Updated Mon YYYY` /
  `Last updated: Month YYYY` and delete the `.pending-note`.

- **Adult card order follows the treatment pathway, not id order** *(8 Nov 2026)*
  The first row of the Adult grid is `rec-0` (initial DMARD therapy) → `rec-2` (choice of DMARD after
  TNFi) → `rec-1` (subcutaneous vs oral methotrexate), so the "choice of DMARD" recommendations sit
  together: DMARD-naive, then (future rec) methotrexate/csDMARD inadequate responders, then
  bDMARD inadequate responders. Only the card markup was moved; ids, slugs, modals, MAGICapp URLs
  and deep links are unchanged, so nothing linking to `#rec-1`/`#rec-2` breaks. Card order in the
  grid is independent of id order (ids are never renumbered — too many things link to them).

- **What's New entries are removed once a recommendation is about 6 months old** *(15 Nov 2026)*
  A "New recommendation" entry stays on the gateway `index.html` What's New list and in the
  guideline-page hero panel for roughly six months, then is removed (first applied to Adult rec-18,
  HCQ retinopathy, new March 2026). When the Adult hero panel has nothing to show, the whole
  `.whats-new-section` block is removed from the hero rather than left as an empty heading; its
  CSS stays in the page and an HTML comment marks where to re-add it. The gateway section is likewise
  removed when it would be completely empty (done the same day for JIA jia-rec-5, new October 2025);
  its CSS stays and a comment marks the spot. Rationale: "new" stops being true, and a dated entry
  makes a living guideline look stale.

- **EtD ratings are colour-coded from their wording** *(22 Nov 2026)*
  Sam found the EtD tab hard to scan without MAGICapp's colours. Each `.etd-rating` pill, plus a
  4 px stripe on the left of its `.etd-domain` box, is coloured by `ETD_RATING_LEVELS` at the end of
  `scripts.js` (matched on the pill's text, case-insensitive), so new recs need no extra markup.
  Sam approved this mapping in preference to MAGICapp's own: green = substantial net benefits / High /
  no substantial variability / no important issues; amber = small net benefit or little difference /
  Moderate / substantial variability expected or uncertain / important issues or potential issues not
  investigated; orange = Low; red = important harms / Very low / important negative issues / likely
  increases inequity / likely difficult to implement. A rating whose wording is not in the table
  stays neutral grey - add it to the table (and tell Sam which colour was chosen). The certainty
  colours match the badges on `how-to-use.html`. The rating is written "Very low" (lower-case l)
  everywhere; "Very Low Disease Activity" in adult rec text is a clinical term and is left as is.

- **Panel Members page is split into "Current" and "Previous" panel members** *(22 Nov 2026)*
  A team member pointed out that one undivided list implied an ongoing relationship with everyone on
  it. `panellists.html` now has two `.panel-group` blocks, each with its own `.panellists-grid`:
  `#current-panel-members` and `#previous-panel-members` (`.previous-panel`). Previous members keep
  their full card (recommendations contributed to, declaration link) because that record must stay
  public; no reason for the move is given on the page. **Sam decides who is "previous"** - default
  is current, including people who have not sat on a panel recently but remain available. The
  filters work across both groups and hide a group's heading when it has no matches. Search results
  label these people "Previous panel member". `coi.html` is not split.

- **Panel re-deliberation: revise in place, archive the old version** *(27 Nov 2026)*
  First used for JIA `jia-rec-3` (uveitis) after the 23 Nov 2026 panel meeting on the JUVE-BRIGHT trial
  (recommendation and all EtD ratings unchanged; rationale, three EtD domains and practical info reworded).
  Sam's aim: a reader sees one succinct, current account and can trust it is up to date, while the record
  of how the decision evolved stays available without piling up on the page. So there are two kinds of event:
  1. *Editorial / factual note, no panel decision* - inline or block Living Updates note; original text
     untouched (unchanged practice, e.g. Adult rec-0 and the bridging-glucocorticoid rec, Jan 2026).
  2. *Panel re-deliberation* - (a) freeze the outgoing version first with
     `.claude/scripts/archive_recommendation.py` -> `<guideline>/archive/<slug>-<YYYY-MM>.html`;
     (b) replace the text in place with the panel's new wording, verbatim; (c) add a
     `.living-updates.living-updates-status` note directly under the recommendation box (one entry, the
     latest panel review only - replace it at the next review, do not stack); (d) put a
     `.section-updated` "Updated Mon YYYY" tag on each section whose wording changed (Rationale `h3`,
     `.etd-domain-title`, top of Practical Info) and remove the previous round's tags; (e) add one entry
     at the top of "Recommendation History" in More Info (`.rec-history`), linking the archived version;
     (f) list the update meeting's attendees as a second "Panel Members" group and add the meeting date.
  Routine "no new evidence" searches never create history entries - they stay in the Data tab list.
  The archive must hold the text as it stood before ANY of the round's wording edits: for `jia-rec-3`
  some pre-meeting edits had already reached `main` on 21 Nov 2026, so the snapshot text was taken from
  the commit before them (`--content-ref ff4ce65`) with the page styling from `main`.
  Archives are public for transparency (Sam's decision) but `noindex`, out of the sitemap and out of site
  search, so nobody lands on superseded guidance by accident. MAGICapp is deliberately **not** relied on
  as the archive. Archive pages are never edited; `verify_site.py` compares each with its SHA-256 in
  `.claude/data/archive-manifest.csv`.
  Dates: card / footer / Data tab still follow the evidence-search month (Aug 2026 here); the status
  note, tags and history entry carry the panel-meeting month (Nov 2026).
  The CSS for these pieces is in `jia/index.html` only so far - copy it (teal variables) the first time
  an Adult recommendation needs it.

*(Established conventions already documented in the skill files — clinical-content fidelity/verbatim
reproduction, the "Updated" dating convention, What's New vs Living Updates usage, Adult page as the
reference standard, DOI-preferred reference hyperlinks, rec-specific MAGICapp deep-links — are not
repeated here; the skill files remain the source of truth for those.)*

---

## 4. Deliberately deferred / parked (not oversights)

- *(Keyboard-accessible header dropdowns were parked here from 3 Jul 2026; resolved 7 Nov 2026 by
  `header.js`, which makes each dropdown heading a click/Enter toggle at every width. See §2.)*

## 5. Known cosmetic issues (tracked, not yet decided/done)

Recorded so they aren't mistaken for decisions or missed. *(The © footer and MAGICapp-link items were resolved 4 and 7 Nov 2026.)*


---

## 6. Adding to this document

Keep it lean. For each new entry: state the decision, give a one-line rationale, and date it. When
an item in §5 (known issues) is resolved, either move it into §2/§3 as a decision or delete it. This
document is only useful if it stays trustworthy and current — prune settled/obsolete entries rather
than letting it grow indefinitely.

---

*Started 5 July 2026, consolidating decisions from the 3 July and 5 July work sessions.
Moved into the repository 4 November 2026.*
