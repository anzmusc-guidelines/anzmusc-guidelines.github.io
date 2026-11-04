# Reference lists

Master copies of the guideline reference lists, used to turn in-text citations
(e.g. `[Melles 2014]`) into numbered superscript links. See the `new-recommendation` skill, Steps 0.2 and 8.

| File | Columns | Rows |
|---|---|---|
| `adult-references.csv` | Reference #, First author surname, Publication year, PubMed link, Journal link, Recommendation | 335 |
| `jia-references.csv` | Reference #, First author surname, Year, PubMed link, Journal/DOI link, Reference text | 180 |

- Converted on 4 Nov 2026 from `Adult_guideline_reference_urls.xlsx` and
  `jia_guideline_reference_urls_complete.xlsx` in Sam's Google Drive. URLs were taken from the
  cells' embedded hyperlinks; every hyperlink matched its displayed text.
- **These CSVs are now the master copy.** Add new references here (in the same PR as the
  recommendation that cites them), not to the old spreadsheets.
- "Journal link" is the DOI link and is preferred for superscripts; fall back to PubMed.
- Adult references with **no link at all**: 4, 5, 200, 202, 203, 225, 319. If one of these is
  cited, link it from another source (e.g. a URL in a `.ris` file) or flag it for Sam.
- The JIA "Year" column is filled for only 12 of 180 rows; match JIA citations on surname plus the
  reference text.
- Some JIA "Reference text" entries are cut short — that truncation is in the source spreadsheet.
