---
name: quarterly-evidence-update
description: >
  Use this skill whenever updating a recommendation on the livingguidelines.org website
  following a quarterly evidence search. Triggers include: "update the evidence search",
  "add a new evidence update", "quarterly update for [recommendation]", "evidence search
  came back [result]", "no new evidence for [rec]", "new evidence found for [rec]",
  "update [rec name] with [month year] search results". This skill encodes all the
  precise conventions for keeping card, modal footer, Data tab, and Living Updates
  sections consistent across both Adult IA (teal) and JIA (purple) guideline pages.
  Always use this skill for any task involving evidence search result recording — even
  if the task seems simple, the consistency rules are easy to get wrong without it.
---

# Quarterly Evidence Update Skill

This skill guides the process of updating a recommendation after a quarterly evidence search. It covers all the places that need to change and the exact conventions to follow.

## Overview of what needs updating

Every evidence search update touches **up to five locations**, all of which must be consistent:

| Location | What changes |
|---|---|
| **Card footer** | `card-updated` date text |
| **Modal footer** | `Last updated: [Month YYYY]` |
| **Data tab** — Evidence Summaries list | New `<li>` entry added |
| **Living Updates section** | New `update-entry` block (if applicable) |
| **What's New section** | Gateway panel entry (only if recommendation text or factual content changed) |

> **Key rule from project conventions:** The "Updated" date on cards/modals = the month of the latest evidence search, or the recommendation development month for new recommendations. Card, modal footer, and Data tab must always be consistent with each other.

---

> **Search index:** any change to modal text (Living Updates, Data tab entries) changes the site-search index. Run `python3 .claude/scripts/build_search_index.py` before committing and include `search-index.json` in the commit.

## Step 1: Identify the recommendation and search outcome

Confirm:
- Which guideline: **Adult IA** (`adult/index.html`) or **JIA** (`jia/index.html`)
- Which recommendation (by title or rec ID, e.g. `rec-6`, `jia-rec-3`)
- The search month/year (e.g. "March 2026")
- The outcome — see the four outcome types below

> **"Update in progress" placeholder:** Some recommendations (currently Adult `rec-0` and `rec-2`,
> which are awaiting living network meta-analysis updates) show an `Update in progress` badge
> (`<span class="card-updated card-updated-pending">`) on the card and modal footer instead of a date,
> plus a `<span class="pending-note">…</span>` in the modal footer. When that update is published,
> **remove the placeholder**: change both spans back to `<span class="card-updated">Updated Mon YYYY</span>`
> / `<span class="card-updated">Last updated: Month YYYY</span>` and delete the `pending-note` span.
> `verify_site.py` warns while a placeholder is in place and errors if only one of card/modal carries it.
> See `.claude/site-decisions.md` §3.

> **New recommendations:** When a newly published recommendation receives its first quarterly evidence update, its Data tab will contain only the "Initial Evidence Synthesis" entry (no updates yet). The first update should be labelled "Update 1". There will be no existing Living Updates block — create one only if required by the outcome type (see Step 2).

---

## Step 2: Determine the outcome type

| Outcome | Badge class | Typical text |
|---|---|---|
| No new evidence | `no-change` | "Evidence search [Month YYYY] — no new evidence identified." |
| New evidence, no change to recommendation | `no-change` | "Evidence search [Month YYYY] — new evidence identified; recommendation unchanged." |
| Factual update (e.g. PBS change, drug availability) | `factual` | Describe the factual change specifically. |
| Recommendation text amended | `text-amended` | Describe what changed and why. |

For **no new evidence** and **new evidence, no change**: add a Living Updates entry only if this is the *first* update for that recommendation, or if there's something noteworthy. Routine "no new evidence" rounds for established recommendations typically only need the Data tab list updated plus the card/modal date refreshed — no new Living Updates block needed unless instructed.

For **factual** or **text-amended** outcomes: always add a Living Updates entry.

---

## Step 3: Update the card footer

Find the recommendation card. Update the `card-updated` span:

```html
<!-- Before -->
<span class="card-updated">Updated Jan 2026</span>

<!-- After (example: March 2026 search) -->
<span class="card-updated">Updated Mar 2026</span>
```

**Date format:** Abbreviated month + full year. Use standard 3-letter abbreviations: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec.

---

## Step 4: Update the modal footer

Find the matching modal. Update the `Last updated:` span in `.modal-footer-left`:

```html
<!-- Before -->
<span class="card-updated">Last updated: January 2026</span>

<!-- After -->
<span class="card-updated">Last updated: March 2026</span>
```

**Date format here:** Full month name + full year (different from card — card uses abbreviated month).

---

## Step 5: Update the Data tab — Evidence Summaries list

Find the `<ul class="evidence-list">` inside the recommendation's Data tab content (`#[rec-id]-data`).

### If there IS a Google Drive link (new evidence found):

```html
<li><a href="[GOOGLE_DRIVE_URL]" target="_blank">Update [N] ([Month YYYY])</a></li>
```

The update number N is the next sequential number after the last listed update.

### If there is NO new evidence:

```html
<li><span class="no-link">Update [N] ([Month YYYY])</span> <span class="evidence-note">(no new evidence)</span></li>
```

Note: some recommendations use slightly different phrasing like "no new trials" — match existing phrasing style for that recommendation.

---

## Step 6: Add a Living Updates entry (when required)

See Step 2 for when this is needed. There are two placement types:

### Block Living Updates (end of Recommendation tab rationale)

Used for substantive updates visible at the bottom of the Recommendation tab. Typically for factual or text-amended outcomes.

**Adult IA version (teal):**
```html
<div class="living-updates">
    <div class="living-updates-header">
        <svg class="living-updates-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M15.312 11.424a5.5 5.5 0 01-9.201 2.466l-.312-.311h2.433a.75.75 0 000-1.5H3.989a.75.75 0 00-.75.75v4.242a.75.75 0 001.5 0v-2.43l.31.31a7 7 0 0011.712-3.138.75.75 0 00-1.449-.39zm1.23-3.723a.75.75 0 00.219-.53V2.929a.75.75 0 00-1.5 0v2.43l-.31-.31A7 7 0 003.239 8.188a.75.75 0 101.448.389A5.5 5.5 0 0113.89 6.11l.311.31h-2.432a.75.75 0 000 1.5h4.243a.75.75 0 00.53-.219z" clip-rule="evenodd"/>
        </svg>
        <span class="living-updates-title">Living Guideline Updates</span>
    </div>
    <div class="living-updates-content">
        <div class="update-entry">
            <span class="update-date">[Month YYYY]</span>
            <span class="update-text">[Update text here.] <span class="update-badge [badge-class]">[Badge label]</span></span>
        </div>
    </div>
</div>
```

**JIA version (purple):** Identical structure — the CSS classes are the same; the colour difference is handled by the CSS variables already defined for each page.

### Inline Living Updates (within rationale text)

Used when a specific paragraph in the rationale is affected and needs contextual annotation. Place immediately after the relevant `<p>` tag.

```html
<div class="living-updates-inline">
    <div class="living-updates-header">
        <svg class="living-updates-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M15.312 11.424a5.5 5.5 0 01-9.201 2.466l-.312-.311h2.433a.75.75 0 000-1.5H3.989a.75.75 0 00-.75.75v4.242a.75.75 0 001.5 0v-2.43l.31.31a7 7 0 0011.712-3.138.75.75 0 00-1.449-.39zm1.23-3.723a.75.75 0 00.219-.53V2.929a.75.75 0 00-1.5 0v2.43l-.31-.31A7 7 0 003.239 8.188a.75.75 0 101.448.389A5.5 5.5 0 0113.89 6.11l.311.31h-2.432a.75.75 0 000 1.5h4.243a.75.75 0 00.53-.219z" clip-rule="evenodd"/>
        </svg>
        <span class="living-updates-title">Update</span>
    </div>
    <div class="living-updates-content">
        <div class="update-entry">
            <span class="update-date">[Month YYYY]</span>
            <span class="update-text">[Update text here.] <span class="update-badge [badge-class]">[Badge label]</span></span>
        </div>
    </div>
</div>
```

### Badge classes and labels

| Situation | Class | Label text |
|---|---|---|
| No change / no new evidence | `no-change` | `No change` |
| Factual update (PBS, availability, etc.) | `factual` | `Factual update` |
| Recommendation text amended | `text-amended` | `Text amended` |

---

## Step 7: Adding multiple update entries to an existing Living Updates block

If a Living Updates block already exists for the recommendation, add the new entry **at the top** of the existing `living-updates-content` div (newest first):

```html
<div class="living-updates-content">
    <!-- NEW entry goes here, at top -->
    <div class="update-entry">
        <span class="update-date">March 2026</span>
        <span class="update-text">Evidence search March 2026 — no new evidence identified. <span class="update-badge no-change">No change</span></span>
    </div>
    <!-- existing entries below -->
    <div class="update-entry">
        <span class="update-date">January 2026</span>
        <span class="update-text">...</span>
    </div>
</div>
```

---

## Step 8: Update the What's New section (conditional)

The **What's New** panel on the gateway page (`index.html`) should only be updated when something has actually changed in the recommendation. Do **not** update it for routine evidence search rounds that produce no change.

| Outcome | Update What's New? |
|---|---|
| No new evidence | ✗ No |
| New evidence, recommendation unchanged | ✗ No |
| Factual update | ✓ Yes |
| Recommendation text amended | ✓ Yes |

When updating, find the existing `whats-new-item` for the recommendation and update the label from `new` to `updated` if not already done, and revise the description text to reflect what changed:

```html
<div class="whats-new-item" onclick="openModal('[rec-id]')">
    <div class="whats-new-label updated">Updated</div>
    <div class="whats-new-title">[Recommendation title]</div>
    <div class="whats-new-desc">[Brief description of what changed, e.g. "PBS listing updated."]</div>
</div>
```

If no `whats-new-item` exists yet for this recommendation, add one following the same pattern. If a What's New entry already exists and the label is already `updated`, simply revise the description text.

---

## Step 9: Verify and hand over for review

1. Run `python3 .claude/scripts/verify_site.py` from the repo root. It checks card/modal/Data-tab date consistency and update numbering for every recommendation, not just the one you touched. Any **ERROR** must be fixed before committing.
2. Commit on a branch named for the round (e.g. `evidence-update-2026-11`) and open a pull request. Never push to `main` — GitHub Pages publishes `main` directly to livingguidelines.org.
3. In the PR description, list each recommendation touched, the outcome type, and the new date, so Sam can review against the evidence-search results.

---

## Core principles to never violate

1. **Never modify original panel rationale language.** The Living Updates system exists precisely to preserve the historical accuracy of what the panel said at the time. New context goes in Living Updates blocks — not edits to existing rationale text.

2. **Card date, modal footer date, and Data tab must always be consistent.** After any update, verify all three show the same month/year (card uses abbreviated month, modal uses full month name).

3. **The Data tab evidence list is append-only.** Never remove or alter existing entries. Always add new ones at the bottom of the list.

4. **Match the phrasing style of the existing recommendation.** Some use "no new evidence", some use "no new trials" — use whatever is already established for that specific recommendation's evidence list.

---

## Quick reference: full update checklist

- [ ] Card footer date updated (abbreviated month, e.g. "Mar 2026")
- [ ] Modal footer date updated (full month, e.g. "March 2026")
- [ ] Data tab evidence list: new `<li>` added at bottom
- [ ] Data tab date (`card-updated` span) updated to match card/modal
- [ ] Living Updates entry added (if factual/text-amended, or first update for this rec)
- [ ] What's New section updated (only if factual/text-amended outcome)
- [ ] All three dates consistent with each other (card, modal footer, Data tab)
- [ ] Original panel language untouched
- [ ] `verify_site.py` passes with no errors
- [ ] Changes on a branch with a PR opened — not pushed to `main`
- [ ] Evidence Tables Google Doc updated (Sam/Vanessa — manual step; Doc ID: `1o9ncE6gWrJWJylOAXFOqd1nxLZzEz1jZFkjGs8ysMfw`)
