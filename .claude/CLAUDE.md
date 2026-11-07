# livingguidelines.org — working notes for Claude

This repo is the public website for the **ANZMUSC Australian Living Guideline for the
Pharmacological Management of Inflammatory Arthritis** — an NHMRC-endorsed living guideline
(GRADE / Evidence-to-Decision) with two guideline pages: **Adult Inflammatory Arthritis** and
**Juvenile Idiopathic Arthritis (JIA)**. Clinical content is authored in MAGICapp; this site
presents it.

The site is maintained by **Sam Whittle** (rheumatologist and guideline lead; not a web
developer) with **Vanessa Glennon** (project manager — evidence searches, headshots, Google Forms,
Evidence Tables doc). Explain technical choices in plain language.

## Before you change anything

1. Read `.claude/site-decisions.md` — settled decisions, **known non-bugs you must not "fix"**,
   and parked items.
2. For recurring jobs, load the skill first:
   - adding a recommendation → `new-recommendation`
   - recording a quarterly evidence search → `quarterly-evidence-update`
   - adding/replacing a panellist photo → `panellist-headshot`
   - panel members, COI links, publications, media, abbreviations, text pages,
     sharing recommendation links → `site-page-updates`
3. Make sure you're on current `main` (`git fetch origin main`) before branching.

## How changes get published

- GitHub Pages serves `main` directly to **livingguidelines.org** (`CNAME`). There is no build
  step and no staging site. **A push to `main` is a live change.**
- So: **always work on a branch and open a pull request.** Never push to `main`, never
  force-push, never merge the PR yourself unless Sam explicitly asks.
- To let Sam preview, serve the repo locally (`python3 -m http.server`) and open
  `/adult/`, `/jia/` etc. in the built-in browser, or share screenshots.
- Before every commit: `python3 .claude/scripts/verify_site.py` must report **no errors**.
  Mention any *new* warnings in the PR.

## Division of labour

- **Sam owns all clinical content decisions.** Claude does the mechanical work: HTML edits,
  formatting, reference hyperlinking, verification, consistency across pages.
- **Clinical text is reproduced verbatim** from the panel/MAGICapp source — never summarise,
  reorder or rephrase. Preserve source bullets as `<ul>/<li>` and source hyperlinks as `<a>`.
- **Never edit original panel rationale.** Later context goes in Living Updates blocks.
- If something looks wrong in clinical content, or you deviate from a skill, **don't silently
  change it** — list it in the PR description under "Notes for Sam".
- Flag known quirks rather than quietly accepting or "fixing" them.

## Site map

| Path | What it is |
|---|---|
| `index.html` | Gateway — choose Adult or JIA; What's New / Coming Soon; pathway-card rec counts |
| `adult/index.html` | Adult IA guideline (teal) — cards, condition tabs (RA/PsA/axSpA/SLE), modals `rec-0…` |
| `jia/index.html` | JIA guideline (purple) — cards, modals `jia-rec-1…`, no condition tabs |
| `scripts.js` | Shared JS for both guideline pages (modal, tabs, filters, focus trap) |
| `panellists.html` | Panel members, headshots in `images/headshots/` (64 px circles) |
| `coi.html`, `methodology.html`, `how-to-use.html`, `who-we-are.html`, `funding.html`, `abbreviations.html`, `publications.html`, `media.html`, `contact.html` | About/resource pages |
| `404.html` | Root 404 — all links root-anchored |
| `sitemap.xml`, `robots.txt` | SEO; sitemap `lastmod` = real commit date |
| `.claude/` | Claude's notes, skills and checks — **not published** by GitHub Pages |
| `.claude/data/adult-references.csv`, `jia-references.csv` | Master reference lists (ref number → DOI/PubMed) used for citation superscripts |
| `.claude/data/adult-magicapp-urls.csv`, `jia-magicapp-urls.csv` | Master list of every rec's "View in MAGICapp" URL — `verify_site.py` enforces it; never ask Sam to re-collect |
| `search.js`, `search.css`, `search-index.json` | Site-wide search in every page header. The index is **generated** — never hand-edit |
| `.claude/scripts/build_search_index.py` | Rebuilds `search-index.json` from the pages — **run after any content change**, then commit the JSON |
| `.claude/scripts/verify_site.py` | Whole-site integrity check — run before every commit |
| `.claude/scripts/rec_links.py` | Generates the direct-link list (numeric + slug) for every recommendation |

Each guideline page has a slug map (`window.adultSlugMap` / `window.jiaSlugMap`) so
`/adult/#hcq-retinopathy` deep-links to `rec-18`. Every rec needs a slug.

## Conventions worth remembering

- **Dates:** card `Updated Mon YYYY`; modal footer `Last updated: Month YYYY`; Data tab updates
  `Update N (Month YYYY)`. All three must agree. The date is the latest evidence-search month,
  or the panel-meeting month for a new rec.
- **What's New** changes only when a rec is new or its content/facts actually change — not for
  routine "no new evidence" rounds.
- **Adult page is the reference standard**; make JIA consistent with it, not the reverse.
- **MAGICapp links** must deep-link to the specific recommendation (`/section/` or `/rec/`) and match
  `.claude/data/<adult|jia>-magicapp-urls.csv`.
- **Reference superscripts:** prefer DOI over PubMed links; `rel="noopener"`.
- **Accessibility:** text contrast ≥ 4.5:1; don't revert the sentinel-based modal focus trap.
- **Analytics:** every page carries GA `G-XQKQVSHVS5` immediately before `</head>`.
- **Site search:** after editing any recommendation, panellist, publication, abbreviation or text page,
  run `python3 .claude/scripts/build_search_index.py` and commit `search-index.json` (the verifier
  errors if it is stale). Header markup for the box is duplicated on every page, like the nav.
- Spelling: Australian English. "Macular" (adjective), not "macula", e.g. "macular abnormalities".
  Monitoring wording: "6-monthly or less frequently".

## Things that live outside this repo

Ask Sam for these when a task needs them — don't guess:
Most live in Sam's Google Drive folder "Guideline Website Working Documents":
- Recommendation content (MAGICapp; Google Docs; `Adult Recommendations Text original build.xlsx`,
  `JIA_Guideline_Content_UPDATED.xlsx`) and panel lists (`Guideline Panellists.xlsx`, JIA docs)
- Quarterly search-update sheets (e.g. `IA LGL Search Updates for website August 2026.xlsx`)
- Adult Evidence Tables Google Doc `1o9ncE6gWrJWJylOAXFOqd1nxLZzEz1jZFkjGs8ysMfw` — Claude
  can't edit Google Docs; give Sam/Vanessa paste-ready text
- The feedback Google Forms (adding a rec to the dropdown is a manual step for Sam/Vanessa)

## Open backlog (as of Nov 2026)

- Evidence-search round(s) since Jun 2026 (Adult) / Feb 2026 (JIA) still to be recorded — waiting on
  Vanessa's search-update summary
- Adult rec-0 and rec-2 show an "Update in progress" badge pending living-NMA updates after the next
  panel meeting; the Thomas 2026 Cochrane NMA (CD013562.pub2) is to be linked from rec-2 then
- No `og:image` share preview (needs an image chosen by Sam)
- Keyboard access for header dropdowns (parked — see site-decisions §4)
- 10 of 50 panellist headshots still outstanding (Vanessa collecting)
