# Final verification closeout — 10 November 2026

**Verdict: ready for the publication-manifest review.** All 16 findings from the 10 November
verification are corrected and verified in the existing 25-page PDF. The original I7 and M4
residuals are closed. No further manuscript or layout correction was found in this closeout.

The 9 November review and its earlier closure claims remain historical records. The 10 November
verification reopened I7/M4 and identified additional accuracy/editorial issues; this dated
closeout supersedes those earlier current-status summaries.

## Artifact identity

| Artifact | SHA-256 |
|---|---|
| `bastion-technical-report-2026-11.pdf` | `f3b2bb95f5ae52b9e9d964519f92dd367fceeb58342e0570d07274692e5f9071` |
| `source-manifest.json` | `923952eb7c1f6f9f4081405642d20b4714add7c3678c68b0f5fcf354fee7bd3f` |
| `source-snapshot.zip` | `a23554b962fad34e785a48dae21a4ed539e5b565ffd8a0f2c918c52db27572c2` |
| `manuscript.md` | `0498fd9b0982bf9e831dd31b5253411f40d3b0695a59abe892b5a2eec06423c3` |
| `OUTLINE.md` | `fae36638d94e567cc3888e37af0c65c177efe7f07d3a23be9d72ddee59259015` |

Artifact paths are relative to `report/`. The PDF has 25 pages and 62 clickable HTTPS links.
All 70 source-manifest entries match both the current files and ZIP members. The ZIP CRC and
embedded manifest pass; there is no public-source overlay. Canonical assembly matches the
manuscript after Windows CRLF/LF normalisation.

## Findings closed

| Finding | Verified correction | Current PDF |
|---|---|---|
| 1 — Important | C.4 discloses private raw pull-response retention; §5.8 distinguishes it from live-collector handling | pp.9, 23 |
| 2 | D8 label keeps the complete date on one line | p.10 |
| 3 | Figure 3 boundary dashes clear the worker-end labels | p.15 |
| 4 | N7/N7b defined in the Figure 2 caption at first use | p.10 |
| 5 | Attributed-routing rule distinguishes bare JSON on the authorised path | p.6 |
| 6 | Conclusion narrows control attribution; D6 body explicitly records refusal | pp.11, 19 |
| 7 | Gateway refusal is separated from later dependency observations; cause remains unestablished | pp.13, 21 |
| 8 | Billing sentence describes the scope of D4's action | p.21 |
| 9 | Stopped records, L/M protocols and M-A1 preflight amendment distinguished | p.9 |
| 10 | Six-fact and classification promises qualified; E19 repair/deployment stated | pp.9, 11 |
| 11 | Later documentation/teardown link base distinguished from deployed code | p.20 |
| 12 | Abstract explicitly states rejection of the forged envelope | p.1 |
| 13 | G5/L1 cloud completions distinguished from protocol stops | p.18 |
| 14 | Replay labels qualified as E27's labels | p.14 |
| 15 | Read-only recovery “found” the events | p.22 |
| 16 | British “behaviour” restored | p.8 |

The optional F-pilot dispatcher attribution, R7 page range and first-use expansions are also
present. The F pilot, H28 and M remain distinct from an observed receipt rejection by
`EscalationCompletionGate`. The C.4 summary-field description was checked against the inspection
script; no private raw response contents were opened.

## Full visual verification

Codex inspected every complete rendered page, 1–25, at the saved 1.5× PDF rendering scale.
All 25 saved page images were compared pixel for pixel with fresh in-memory renders of the
current PDF. Every figure embedded in the PDF also matches its current figure PNG.

The inspection covered headers/footers, page numbers, margins, paragraph and list flow,
reference labels, all three figures and captions, and table continuations. The split tables
on pages 15–16, 16–17, 21–22 and 22–23 repeat their headers and retain their rows. The numbered
confirmation and provenance statements remain distinct. Figure 2's date wrapping and Figure
3's line-to-label clearance were checked visually, beyond the label-only collision guard.
The minimum figure-label size remains 8.425 points at the measured placement width.
No clipping, overlap or unreadable label was found in this inspection.

## Integrity, claims and privacy

The frozen outline matches the preserved pre-correction draft byte for byte. Appendix C.1's
stop ledger, C.2's amendment records and C.4's dead-letter table are unchanged. Evaluation table
rows are unchanged apart from the clarified replay label. No stopped observation was replaced
or pooled. Statistical placement, three-part protocol provenance, M's reconstructed hash,
control attribution and deferred C4/cross-framework status remain bounded as previously reviewed.

Finite pattern checks covered canonical sections, assembled Markdown, extracted PDF text,
PDF metadata and link targets. They found zero matches for email/service-account addresses,
private-key headers, selected token/JWT forms, private service URLs, billing-account IDs,
IAM-principal forms or explicit credit-balance values. The PDF has no embedded files, and the
source ZIP has no private capture/raw/key paths. Manual page/text review found no raw IAM,
unredacted findings, credit balance or employer affiliation. The affiliation is exactly
“Independent researcher, Stockholm”. These are bounded checks, not a general disclosure guarantee.

The 17 report checks, scoped Ruff/format, docs/version checks and Markdown lint pass for this
closeout. Machine-readable details are in `checks.json`, `figure-layout.json` and
`final-fix-integrity.json`; the claim reconciliation records the additional checked claims.
Earlier primary-source citation checks are carried forward from the dated review, rather
than represented as newly fetched here.

This is technical verification with AI assistance; no independent peer review is claimed.
Only QA, README and handoff/plan records were updated in this closeout. Canonical sections,
figures, builder, PDF, source manifest and snapshot were not changed or rebuilt. Sources and
output remain local and uncommitted. Publication approval, tag, DOI and site release remain
separate; no experiment or cloud action occurred.

Deferred: C4 and the cross-framework study remain future work under the frozen blueprint.
