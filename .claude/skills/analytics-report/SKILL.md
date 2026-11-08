---
name: analytics-report
description: >
  Use whenever Sam asks about website traffic or Google Analytics for livingguidelines.org:
  "how many people visited", "which recommendations are being read", "pull the analytics",
  "what are people searching for on the site", "quarterly traffic report", "where are visitors
  from". Covers pulling GA4 data through the Data API with the service account stored in the
  cloud environment, turning it into a plain-language digest, and the one-off setup steps
  (service account, custom dimensions) if they have not been done yet.
---

# Analytics Report Skill

The site carries the GA4 tag `G-XQKQVSHVS5` on every page. `scripts.js` also sends two custom
events (`view_recommendation`, `view_recommendation_tab`) and `search.js` sends `search` and
`select_content`, so GA4 can report *which recommendation* was read and *what people typed* into
the site search, not just which page they landed on.

## Pulling the data

1. Check the credentials are present in this session (both are set by Sam in the cloud
   environment's settings, never in the repo):

   ```bash
   test -n "$GA4_SERVICE_ACCOUNT_KEY" && test -n "$GA4_PROPERTY_ID" && echo "credentials present"
   ```

   If either is missing, see **One-off setup** below and give Sam the steps. Don't ask him to
   paste a key into the chat.

2. Install the two libraries into a scratch virtual environment (the container is fresh each
   session), then run the report:

   ```bash
   python3 -m venv /tmp/ga && /tmp/ga/bin/pip install -q google-auth requests
   /tmp/ga/bin/python .claude/scripts/ga4_report.py --start 2026-08-01 --end 2026-10-31 --compare --out digest.md
   ```

   `--start`/`--end` take `YYYY-MM-DD` or GA relative dates (`90daysAgo`, `today`).
   `--compare` adds the preceding period of equal length to the overview (real dates only).
   `--json raw.json` keeps the raw API responses if a question needs more digging.

3. Write the digest for Sam from the Markdown the script produces. He is a clinician, not an
   analyst: lead with what changed and what it means, keep tables short, say "people" not
   "active users". Things worth calling out every time:
   - total visitors and the trend against the previous period;
   - Adult vs JIA page share;
   - the most and least opened recommendations (the least opened matter for the panel too);
   - whether deep links (`/adult/#slug`) appear as landing pages, i.e. whether shared links are used;
   - Australia/New Zealand share and the top cities;
   - phone vs desktop share (affects layout priorities);
   - site-search terms, especially ones that look like gaps (a drug, condition or abbreviation
     we don't cover or don't name the way clinicians search for it).
   Put the digest in the scratchpad (or the repo only if Sam asks for it to be kept) and send
   it with `SendUserFile`. Don't commit raw analytics data to the public repo.

4. If the recommendation/search tables are empty or the Notes section says a `customEvent:`
   dimension is invalid, the custom dimensions have not been registered yet (see setup step 4)
   or were registered after the period requested. Say so plainly.

## One-off setup (Sam, about 15 minutes)

Everything below is done once. The result is a read-only "robot" account that can see the
Analytics numbers and nothing else; its key lives in Sam's Claude cloud environment.

1. **Google Cloud project and API.** At console.cloud.google.com (signed in as the Google
   account that owns the Analytics property): create a project (e.g. `livingguidelines-analytics`)
   or reuse one, then *APIs & Services → Library → "Google Analytics Data API" → Enable*.
2. **Service account.** *IAM & Admin → Service Accounts → Create service account*, name it
   `analytics-reader`, no roles needed on the project. Open it → *Keys → Add key → Create new
   key → JSON*. A `.json` file downloads; keep it private (it is a password). Copy the account's
   email address (ends in `.iam.gserviceaccount.com`).
3. **Give it read access in Analytics.** analytics.google.com → *Admin → Property → Property
   access management → + → Add users*, paste the service-account email, role **Viewer**,
   untick "notify by email". While in Admin, open *Property details* and note the numeric
   **Property ID**.
4. **Register the custom dimensions** so the per-recommendation and search data appear in
   reports and the API. *Admin → Data display → Custom definitions → Create custom dimension*,
   scope **Event**, one per row (dimension name can equal the parameter name):

   | Event parameter | Sent by |
   |---|---|
   | `recommendation_id` | `view_recommendation`, `view_recommendation_tab` |
   | `recommendation_slug` | same |
   | `recommendation_title` | same |
   | `guideline` | same (`adult` / `jia`) |
   | `tab` | `view_recommendation_tab` |
   | `search_term` | `search`, `select_content` (site search) |

   GA4 only fills a dimension from the day it is created, so do this straight after the
   tracking change goes live.
5. **Store the key for Claude.** In a Claude Code cloud session: the environment menu in the
   title bar → *Edit* the environment → *Environment variables*:
   - `GA4_PROPERTY_ID` = the numeric property id
   - `GA4_SERVICE_ACCOUNT_KEY` = the whole contents of the downloaded `.json` file. If the
     field won't take line breaks, paste the base64 form instead (on a Mac:
     `base64 -i ~/Downloads/the-key.json | pbcopy`); the script accepts either.

   Then start a **new** session (variables are read when a session starts) and ask for the report.

If Sam ever wants to revoke access: delete the key under the service account in Google Cloud,
or remove the account from Property access management.

## What the events record (for reference)

| Event | When | Parameters |
|---|---|---|
| `view_recommendation` | a rec's modal opens (card click, What's New, deep link, site search) — once per opening | `recommendation_id`, `recommendation_slug`, `recommendation_title`, `guideline` |
| `view_recommendation_tab` | a different tab is chosen inside an open modal, or a deep link names a tab | the above + `tab` (`recommendation`, `etd`, `practical`, `evidence`, `data`) |
| `search` | a site-search query of 3+ characters (debounced) | `search_term`, `results` |
| `select_content` | a site-search result is clicked | `content_type`, `item_id`, `search_term` |

Events only fire when `gtag` has loaded; ad-blockers that block Analytics simply mean those
visits are not counted, which is normal and not a bug.
