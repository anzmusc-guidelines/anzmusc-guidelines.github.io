#!/usr/bin/env python3
"""
Pull a standard set of Google Analytics 4 reports for livingguidelines.org and
write them as a Markdown digest.

Credentials come from the cloud environment (never from the repo):
  GA4_SERVICE_ACCOUNT_KEY  the service-account key: the JSON text itself, or that
                           JSON base64-encoded, or a path to the .json file
  GA4_PROPERTY_ID          the numeric GA4 property id (Admin -> Property details)

Needs:  pip install google-auth requests     (see .claude/skills/analytics-report)

Usage:
  python3 .claude/scripts/ga4_report.py                      # last 90 days -> stdout
  python3 .claude/scripts/ga4_report.py --start 2026-08-01 --end 2026-10-31 --out digest.md
  python3 .claude/scripts/ga4_report.py --compare            # also show the previous period
  python3 .claude/scripts/ga4_report.py --json raw.json      # keep the raw API responses too
"""
import argparse
import base64
import datetime as dt
import json
import os
import sys

API = "https://analyticsdata.googleapis.com/v1beta/properties/{pid}:runReport"
SCOPE = ["https://www.googleapis.com/auth/analytics.readonly"]

# Event parameters that scripts.js / search.js send and that must be registered
# in GA4 as event-scoped custom dimensions before they can be reported on.
CUSTOM_DIMS = ["recommendation_id", "recommendation_slug", "recommendation_title",
               "guideline", "tab", "search_term"]


def load_credentials():
    raw = os.environ.get("GA4_SERVICE_ACCOUNT_KEY", "").strip()
    if not raw:
        sys.exit("GA4_SERVICE_ACCOUNT_KEY is not set in this environment. "
                 "See .claude/skills/analytics-report/SKILL.md for the one-off setup.")
    if os.path.isfile(raw):
        with open(raw) as f:
            raw = f.read()
    if not raw.lstrip().startswith("{"):
        try:
            raw = base64.b64decode(raw).decode()
        except Exception:
            sys.exit("GA4_SERVICE_ACCOUNT_KEY is neither JSON, base64 JSON nor a file path.")
    try:
        info = json.loads(raw)
    except json.JSONDecodeError as e:
        sys.exit(f"GA4_SERVICE_ACCOUNT_KEY is not valid JSON: {e}")
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession
    except ImportError:
        sys.exit("Missing libraries: run  pip install google-auth requests")
    creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPE)
    return AuthorizedSession(creds), info.get("client_email", "?")


class GA4:
    def __init__(self, session, property_id, start, end):
        self.s, self.pid, self.start, self.end = session, property_id, start, end
        self.raw = {}
        self.notes = []

    def run(self, name, dimensions, metrics, limit=25, order_by=None, dimension_filter=None,
            start=None, end=None):
        body = {
            "dateRanges": [{"startDate": start or self.start, "endDate": end or self.end}],
            "dimensions": [{"name": d} for d in dimensions],
            "metrics": [{"name": m} for m in metrics],
            "limit": limit,
            "keepEmptyRows": False,
        }
        if order_by:
            body["orderBys"] = [{"metric": {"metricName": order_by}, "desc": True}]
        elif metrics:
            body["orderBys"] = [{"metric": {"metricName": metrics[0]}, "desc": True}]
        if dimension_filter:
            body["dimensionFilter"] = dimension_filter
        r = self.s.post(API.format(pid=self.pid), json=body, timeout=60)
        if r.status_code != 200:
            msg = r.json().get("error", {}).get("message", r.text) if r.text else r.reason
            self.notes.append(f"**{name}** could not be fetched: {msg}")
            self.raw[name] = {"error": msg}
            return []
        data = r.json()
        self.raw[name] = data
        rows = []
        for row in data.get("rows", []):
            dims = [d["value"] for d in row.get("dimensionValues", [])]
            mets = [m["value"] for m in row.get("metricValues", [])]
            rows.append(dims + mets)
        return rows


def eq(dimension, value):
    return {"filter": {"fieldName": dimension, "stringFilter": {"matchType": "EXACT", "value": value}}}


def fmt(value, kind):
    try:
        v = float(value)
    except ValueError:
        return value
    if kind == "int":
        return f"{int(round(v)):,}"
    if kind == "secs":
        m, s = divmod(int(round(v)), 60)
        return f"{m}m {s:02d}s"
    if kind == "pct":
        return f"{v * 100:.0f}%"
    return f"{v:.1f}"


def table(headers, rows, kinds):
    if not rows:
        return "_No data for this period._\n"
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for r in rows:
        out.append("| " + " | ".join(fmt(c, k) if k else str(c) for c, k in zip(r, kinds)) + " |")
    return "\n".join(out) + "\n"


def month_label(yyyymm):
    try:
        return dt.datetime.strptime(yyyymm, "%Y%m").strftime("%b %Y")
    except ValueError:
        return yyyymm


def pretty_path(p):
    return {"/": "/ (gateway)", "/adult/": "/adult/ (Adult IA)", "/jia/": "/jia/ (JIA)"}.get(p, p)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--start", default="90daysAgo", help="YYYY-MM-DD or e.g. 90daysAgo (default)")
    ap.add_argument("--end", default="today", help="YYYY-MM-DD or today (default)")
    ap.add_argument("--compare", action="store_true", help="also fetch the preceding period of equal length")
    ap.add_argument("--out", help="write the Markdown digest here (default: stdout)")
    ap.add_argument("--json", help="also save the raw API responses to this file")
    ap.add_argument("--property", default=os.environ.get("GA4_PROPERTY_ID", ""),
                    help="GA4 numeric property id (default: $GA4_PROPERTY_ID)")
    a = ap.parse_args()
    if not a.property.isdigit():
        sys.exit("GA4_PROPERTY_ID (numeric) is not set. Admin -> Property -> Property details in Analytics.")

    session, who = load_credentials()
    ga = GA4(session, a.property, a.start, a.end)
    try:
        session.credentials.refresh(__import__("google.auth.transport.requests", fromlist=["Request"]).Request())
    except Exception as e:  # bad/revoked key, API not enabled, etc.
        sys.exit(f"Google rejected the service-account key for {who}: {e}\n"
                 "Check the key is current and the Google Analytics Data API is enabled in its project.")
    md = [f"# livingguidelines.org analytics digest", "",
          f"Period: **{a.start} to {a.end}** (fetched {dt.date.today():%d %b %Y} as `{who}`)", ""]

    # 1. Overview, optionally against the previous period
    overview_metrics = ["activeUsers", "newUsers", "sessions", "screenPageViews",
                        "averageSessionDuration", "engagementRate"]
    cur = ga.run("overview", [], overview_metrics)
    md.append("## At a glance\n")
    labels = ["Users", "New users", "Sessions", "Page views", "Avg session", "Engagement rate"]
    kinds = ["int", "int", "int", "int", "secs", "pct"]
    if cur:
        rows = [[l, fmt(v, k)] for l, v, k in zip(labels, cur[0], kinds)]
        headers = ["Metric", "This period"]
        if a.compare:
            # Only works with real dates; the API's relative dates can't be shifted here.
            try:
                s = dt.date.fromisoformat(a.start); e = dt.date.fromisoformat(a.end)
                span = (e - s).days + 1
                ps, pe = s - dt.timedelta(days=span), s - dt.timedelta(days=1)
                prev = ga.run("overview_previous", [], overview_metrics, start=ps.isoformat(), end=pe.isoformat())
                if prev:
                    headers += [f"Previous ({ps:%d %b}–{pe:%d %b %Y})", "Change"]
                    for row, pv, cv, k in zip(rows, prev[0], cur[0], kinds):
                        row.append(fmt(pv, k))
                        pvf, cvf = float(pv), float(cv)
                        row.append("–" if pvf == 0 else f"{(cvf - pvf) / pvf * 100:+.0f}%")
            except ValueError:
                ga.notes.append("`--compare` needs real dates (--start/--end as YYYY-MM-DD).")
        md.append(table(headers, rows, [None] * len(headers)))
    else:
        md.append("_Overview unavailable._\n")

    # 2. Month by month
    rows = ga.run("monthly", ["yearMonth"], ["activeUsers", "sessions", "screenPageViews"], limit=36)
    rows.sort(key=lambda r: r[0])
    md.append("## Month by month\n")
    md.append(table(["Month", "Users", "Sessions", "Page views"],
                    [[month_label(r[0])] + r[1:] for r in rows], [None, "int", "int", "int"]))

    # 3. Pages
    rows = ga.run("pages", ["pagePath"], ["screenPageViews", "activeUsers", "userEngagementDuration"], limit=25)
    md.append("## Most viewed pages\n")
    md.append(table(["Page", "Views", "Users", "Total time on page"],
                    [[pretty_path(r[0])] + r[1:] for r in rows], [None, "int", "int", "secs"]))

    # 4. Landing pages (shows whether deep links / shared links are used)
    rows = ga.run("landing", ["landingPagePlusQueryString"], ["sessions", "activeUsers"], limit=20)
    md.append("## Where visitors arrive (landing pages)\n")
    md.append(table(["Landing page", "Sessions", "Users"], rows, [None, "int", "int"]))

    # 5. Acquisition
    rows = ga.run("channels", ["sessionDefaultChannelGroup"], ["sessions", "activeUsers", "engagementRate"])
    md.append("## How visitors arrive (channel)\n")
    md.append(table(["Channel", "Sessions", "Users", "Engagement rate"], rows, [None, "int", "int", "pct"]))
    rows = ga.run("sources", ["sessionSource", "sessionMedium"], ["sessions", "activeUsers"], limit=20)
    md.append("### Top sources\n")
    md.append(table(["Source", "Medium", "Sessions", "Users"], rows, [None, None, "int", "int"]))

    # 6. Geography
    rows = ga.run("countries", ["country"], ["activeUsers", "sessions"], limit=20)
    md.append("## Countries\n")
    md.append(table(["Country", "Users", "Sessions"], rows, [None, "int", "int"]))
    rows = ga.run("cities", ["city", "country"], ["activeUsers"], limit=15)
    md.append("### Cities\n")
    md.append(table(["City", "Country", "Users"], rows, [None, None, "int"]))

    # 7. Devices
    rows = ga.run("devices", ["deviceCategory"], ["activeUsers", "sessions", "engagementRate"])
    md.append("## Devices\n")
    md.append(table(["Device", "Users", "Sessions", "Engagement rate"], rows, [None, "int", "int", "pct"]))

    # 8. Recommendations (custom events from scripts.js)
    md.append("## Recommendations opened\n")
    rows = ga.run("recommendations",
                  ["customEvent:recommendation_title", "customEvent:guideline"],
                  ["eventCount", "activeUsers"], limit=100,
                  dimension_filter=eq("eventName", "view_recommendation"))
    md.append(table(["Recommendation", "Guideline", "Opens", "Users"], rows, [None, None, "int", "int"]))
    rows = ga.run("tabs", ["customEvent:tab"], ["eventCount"], limit=10,
                  dimension_filter=eq("eventName", "view_recommendation_tab"))
    md.append("### Which tabs people open after the recommendation\n")
    md.append(table(["Tab", "Opens"], rows, [None, "int"]))

    # 9. Site search
    md.append("## Site search terms\n")
    rows = ga.run("search_terms", ["customEvent:search_term"], ["eventCount"], limit=40,
                  dimension_filter=eq("eventName", "search"))
    md.append(table(["Search term", "Searches"], rows, [None, "int"]))

    # 10. Event summary, so new/missing events are obvious
    rows = ga.run("events", ["eventName"], ["eventCount", "activeUsers"], limit=30)
    md.append("## All events\n")
    md.append(table(["Event", "Count", "Users"], rows, [None, "int", "int"]))

    if ga.notes:
        md.append("## Notes\n")
        for n in ga.notes:
            md.append(f"- {n}")
        if any("customEvent" in n or "not a valid dimension" in n.lower() for n in ga.notes):
            md.append("- A `customEvent:` dimension fails until that parameter is registered in GA4 "
                      "(Admin → Data display → Custom definitions → Create custom dimension, event scope). "
                      "Register: " + ", ".join(f"`{d}`" for d in CUSTOM_DIMS) + ". "
                      "Data is only collected into a dimension from the day it is registered.")
        md.append("")

    text = "\n".join(md)
    if a.out:
        with open(a.out, "w") as f:
            f.write(text)
        print(f"Wrote {a.out}")
    else:
        print(text)
    if a.json:
        with open(a.json, "w") as f:
            json.dump(ga.raw, f, indent=1)


if __name__ == "__main__":
    main()
