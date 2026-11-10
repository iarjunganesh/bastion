# Final review of the definitive report, 9 November 2026

**Current closeout, 10 November:** ready for the publication-manifest review. All 16 follow-up
findings, including the reopened I7/M4 residuals, are corrected and verified against the current
PDF (`f3b2bb95…9071`), with all 25 pages visually inspected. See
[the dated closeout](final-closeout-2026-11-10.md) for current hashes, page locations and scope.
The 9 November closure claims below are historical and are superseded by that closeout.

**Original verdict: ready after the listed fixes.** Critical: none. Important: nine. Minor: five.

**Closeout, 9 November: all 14 items are fixed and verified.** The corrected local PDF is
ready for the publication-manifest review. The findings below describe the preserved
pre-correction draft; they are retained as the review record.

Reviewed `report/manuscript.md`, the 23-page review PDF, the frozen `OUTLINE.md` and the
author-side reconciliation. Evidence E14, E19 and E24-E29 was read line by line. The evidence
and production source match public base `aa398f6953de6dd3d56d84b2ae981a4a06591474`; the
production-code differences from v0.9.1 are the documented dispatcher-comment correction and
the later teardown implementation. R1-R11 and U1-U4 were checked against primary sources;
ACM's Crossref metadata and the published paper resolve R7 as Peng Huang. R9's bibliographic
metadata was also verified through Crossref after the publisher's full-text endpoint failed.

The 17 existing report checks passed. The assembled manuscript matches the canonical section
sources. All 70 source-manifest entries and their ZIP members verify, including the figures;
the snapshot CRC passes. The manifest and PDF hashes match the review receipt. All 23 rendered
pages and the three figure masters were inspected. Text, metadata and link checks found no
prohibited private content or employer affiliation; the affiliation is exactly
"Independent researcher, Stockholm". These are bounded inspection results, not a privacy
guarantee. No manuscript, PDF, figure, evidence record or publication artifact was rebuilt.

All ten sections and Appendices A-C are present. The 98/98 count, the conditional statistical
illustration confined to Sections 5.7 and 8, the three-part provenance statement, M's
reconstructed hash, the completion-control attribution and the separate stop records are
present. C4 and the cross-framework study remain explicitly unperformed.

## Verified correction closeout

The maintainer authorised all listed corrections. Canonical sections and the report-only
figure sources were corrected, the reconciliation was updated, and the PDF was built once.
All 25 rendered pages were inspected. The minimum figure-label size is 8.425 points at the
actual PDF placement. All 70 source-snapshot hashes and ZIP CRC verify; the frozen outline
and the stopped-run/dead-letter table rows are unchanged. The 17 report checks, scoped
Ruff/format, documentation/version checks and Markdown lint pass. Finite scans of manuscript,
PDF text, metadata and links found no prohibited private-value patterns.

| Item | Status | Corrected location and verification |
|---|---|---|
| I1 | Fixed | §6.3, PDF p. 13; cancellation statement confined to M's configuration |
| I2 | Fixed | Abstract p. 1, §9.1 p. 18, conclusion p. 19; D6 refusal and D8 unknown terminal status retained |
| I3 | Fixed | §8, p. 17; November preflights separated from the October census and N |
| I4 | Fixed | Abstract p. 1, C3 p. 2, conclusion p. 19; G/H v0.9.0, I–M v0.9.1 |
| I5 | Fixed | Appendix B, pp. 21–22; all four acquisition/seal disclosures explicit |
| I6 | Fixed | Figure 1 and caption, p. 5; Gateway lies on the worker call path; audit/trace joins separated |
| I7 | Fixed | Figures on pp. 5, 10 and 15; minimum 8.425 pt, no text clipping/collisions, visually inspected |
| I8 | Fixed | §5.6, pp. 8–9; collector actions distinguished from automatic system retries |
| I9 | Fixed | §8, p. 17; F pilot and H28 retained as separate retry observations |
| M1 | Fixed | Figure 2, p. 10; D6 at 21 Aug with 22 Aug repair; caption says selected cases |
| M2 | Fixed | E25 recovery in §6.2, p. 12; removed from §7.6 baseline table, p. 16 |
| M3 | Fixed | §4.5 p. 6 and §5.5 p. 8; numbered items rendered as separate paragraphs |
| M4 | Fixed | First-use definitions expanded; census F1 identified as recovery; N7/N7b mapping in C.1 p. 22 |
| M5 | Fixed | Figure 3 caption, p. 15; post-boundary IAM calls limited to attempts 1–3 |

R7 and the additional reconciliation corrections below are also closed. Detailed receipts
are `checks.json`, `figure-layout.json` and `final-fix-integrity.json` in this directory.
The report remains local and uncommitted; no experiment, cloud action or publication occurred.

## Important

### I1. Section 6.3 turns M into a universal timeout rule

**Current** (`manuscript.md:324`): "A caller-visible timeout does not cancel in-flight remote
computation (Section 7.5)."

**Problem:** this is unconditional, unlike the tested-configuration claim in Sections 7.5
and 8. E29 explicitly excludes a universal timeout rule.

**Evidence:** `assets/evidence/29-timeout-fault-injection-l-m.md:83-108`;
`docs/research/claim-matrix.md:38`.

**Replace with:** "In M's tested configuration, worker execution continued beyond the five
estimated caller timeout boundaries; cancellation propagation is not guaranteed (Section 7.5)."

### I2. The historical summary wrongly gives every failure a success report and one cure

**Current** (`manuscript.md:514`): "In each, a component reported success without the work
behind it"; compare the shared-shape assertion in the abstract (`:13`) and "Every failure in
Section 6 had the same cure" (`:477`).

**Problem:** D6's caller refused the missing report; D8's terminal status is expressly
unestablished. D8 performed the policy calculation but lost the decision downstream. The
additional E24 parser failure and H28 model rejection also had distinct repairs.

**Evidence:** `docs/adr/012-structured-findings-across-a2a.md:82-95`;
`report/OUTLINE.md:127-147`; `manuscript.md:272-277`; E24:54-61; E26:91-94.

**Abstract replacement for the shared-shape sentences:** "Between August and November 2026,
five dated failures exposed gaps between local execution signals and downstream work. A
completed status, a worker-local state key, a state-only policy decision, an error-free remote
reply or a closed response stream did not establish that the intended work had run across the
boundary. Repairs made policy execution, handoffs and downstream completion explicitly
checkable."

**Conclusion replacement for the sentence starting 'In each' and the following 'Each was
answered' sentence:** "The failures involved a skipped policy step, a report stranded in a
worker's session, a decision lost at an A2A hop, a failed remote task delivered as an empty
event, and an empty Runtime stream recorded as a completed investigation. False completion
was observed in D1, D9 and E19; D6's caller refused the missing report, and D8's terminal status
is not independently established. The repairs made policy execution, handoffs and downstream
completion explicitly checkable."

**Section 9.1 replacement for its first two sentences:** "The historical failures motivate a
common design principle: make execution and downstream completion explicitly checkable at
each boundary. The individual repairs differed, including explicit message content, receipt
checks, parser compatibility and bounded model retry."

### I3. Section 8 broadens the November binding census to the wrong dates

**Current** (`manuscript.md:447`): "62 bindings, 3 findings and 2 departments at every November
preflight."

**Problem:** this extends the 7-8 November preflight counts to cohort N. N retains the separate
28 October 56-binding census; no census on N's evaluation days was established.

**Evidence:** E23:27-45; E26:25-26; E27:3-5; `OUTLINE.md:79-84`.

**Replace the first two sentences of this limitation with:** "There was one Google Cloud
project. The 7-8 November G-M preflights recorded a bounded workload of 62 bindings, 3 findings
and 2 departments; the earlier 56-binding census belongs to 28 October and does not establish
a binding count for cohort N's 3-4 November investigations."

### I4. The abstract, C3 description and conclusion blur the two fleet versions

**Current:** "The final evaluation ran on the v0.9.1 deployment" (`:15`), "Pre-specified
protocols on the final v0.9.1 deployment, covering ... two stopped cohorts" (`:40`) and
"The final evaluation on v0.9.1" (`:516`).

**Problem:** G and H used v0.9.0; only I-M used v0.9.1. The detailed ledger is correct.

**Evidence:** E26:31-50; `manuscript.md:333-341`.

**Abstract first-sentence replacement:** "The final bounded evaluation covered G and H on
v0.9.0 and I-M on v0.9.1 on 7-8 November 2026 under pre-specified protocols."

**C3 first-sentence replacement:** "Pre-specified protocols on v0.9.0 (G and H) and v0.9.1
(I-M), covering successful serial runs, two stopped cohorts, a model-retry recovery, negative
security controls, replay checks, a telemetry census and a timeout fault injection."

**Conclusion first-sentence replacement:** "The final bounded evaluation covered G and H on
v0.9.0 and I-M on v0.9.1, observing the controls within those measured cases."

### I5. Appendix B compresses away material collection and seal disclosures

**Current** (`:606`): "Earlier bundles have their own manifests, with the gaps disclosed in
their records."

**Problem:** the original October census has no original manifest or ZIP. The sentence also
does not tell the reader about E18's separately sealed join, E14's collector repair or E21's
crash/resume and less-specific document query.

**Evidence:** E14:35-52; E21:65-74;
`docs/research/evidence-audit-2026-11-04.md:28-36,90-96,157`.

**Replace the quoted sentence with:** "Earlier records have distinct acquisition limits.
E14 paused after seven investigations when one audit entry was absent from the query result;
a collector-only repair and read-only recovery restored the 28-event record without
republishing a successful investigation. E18's two-hop correlation addendum is outside the
original acquisition ZIP and has its own digest. E21's collector crashed after publication;
its resumed observer recovered the delivery logs without republishing and checked for any
investigation document since publication rather than querying the probe's event ID. The
28 October census has no original manifest or ZIP; its later checksum does not establish an
October seal or an independent capture date. [S13]"

### I6. Figure 1 depicts a path around the Gateway

**Current:** "Deployed topology of v0.9.1" (`:126`); the figure draws Runtime-to-worker arrows
and a separate Runtime-to-Gateway dead end.

**Problem:** that picture can be read as direct worker egress bypassing the Gateway. Its audit
and telemetry box also leaves ambiguous whether both audit and traces join by investigation ID.

**Evidence:** `docs/ARCHITECTURE.md:20-26,200-205`; E28:50-59;
`report/make_figures.py:80-95`; PDF p. 5.

**Exact caption replacement:** "Figure 1. Logical call relationships and trust boundaries of
v0.9.1. Runtime-to-worker arrows denote A2A calls whose egress traverses the Agent Gateway
(T4) before reaching the workers (T3). Dashed green arrows show the completion-confirmation
chain. Audit records join by investigation ID; traces are matched by time window. Regions:
transport and Firestore in `europe-north2`; managed agent services and audit in `europe-west4`;
Gemini inference on Vertex AI `global`."

**Figure title replacement:** "Bastion v0.9.1: logical calls and trust boundaries".

**Audit-box replacement labels:** "Audit: payload-free, investigation ID" and
"Cloud Trace: sampled, time-window joins". The final rendering must make the mandatory
Gateway transit unambiguous; this corrects the depiction of the existing architecture.

### I7. Figures 1-3 are too small to read comfortably in the PDF

**Current labels:** for example "A2A request" and "after boundary: models ..." in Figure 3.

**Problem:** each 2400-pixel-wide image is placed at 499.276 points. Labels specified at
18-24 pixels render at about 3.74-4.99 points; sharper raster export alone cannot fix this.

**Evidence:** PDF pp. 5, 9 and 13;
`make_figures.py:30,74,142-143,193-198`; `build_report.py:479,498-502`.

**Exact wording:** retain the labels, applying only the corrections in I6, M1 and M5. Increase
their rendered size to at least 8 points at the final placed width (about 39 source pixels
at the present scale), then visually verify those three pages in the single final build.

### I8. Section 5.6 makes the collector's retry policy sound like the system's retry policy

**Current** (`:237`): "Observation reads may retry within a bounded window. Measured actions
never retry."

**Problem:** H28, I57 and M deliberately include system retries. The intended restriction is
on collector-initiated repetition or replacement, not on observed automatic system behavior.

**Evidence:** E26:49,60,91-94; E29:64-71; `OUTLINE.md:109-114`.

**Replace with:** "Collectors may retry observation reads within bounded windows. They do not
manually repeat or replace measured publications or probes. Automatic Eventarc redelivery and
v0.9.1 model retries are observed system behavior and are counted separately."

### I9. Section 8's retry/dead-letter inventory omits F and H

**Current** (`:466`): "The retry and dead-letter evidence comprises one permanently rejected
event (E21) and one injected worker timeout (M)."

**Problem:** the retained F pilot also had five failed deliveries and was dead-lettered; the
9 November inspection joined that message exactly. H28 supplies another redelivery case.

**Evidence:** E24:30-66; E26:49; `manuscript.md:411,635-644`; retained A0 inspection (9 November).

**Replace the bullet with:** "*Event-specific retry and dead-letter observations.* E21
observed one permanent ingress rejection, the F pilot observed a parser failure with five
failed deliveries (joined to its dead-letter message post hoc in Appendix C.4), and M observed
one injected worker timeout. H28 separately observed redelivery after a model 429. These cases
do not establish a general delivery-attempt bound; Google documents the configured dead-letter
count as approximate, and delivery of a paging notification was not verified. [R11, E21, E24,
E26, E29]"

## Minor

### M1. Figure 2 puts D6 under the wrong observation date and overpromises stop coverage

**Current:** "D6 report in worker's session" is attached to 22 August; the caption says
"stopped runs are named in their labels" (`:256`).

**Problem:** D6 was observed on 21 August and fixed on 22 August. The figure omits several
stops that Appendix C correctly retains, including I99 and M's preflight attempt 1.

**Evidence:** `docs/research/observation-backlog.md:347-356`; `OUTLINE.md:127-130`;
`make_figures.py:124,132,144-152`.

**Replacement D6 label:** "D6 observed 21 Aug; fixed 22 Aug".

**Replacement D8 label:** "D8 decision lost at A2A hop (22 Aug)".

**Caption replacement:** "Figure 2. Selected failures, repairs and evaluation runs,
August-November 2026. Failures are above the line; repairs and evaluation runs are below it.
The complete stop ledger is in Appendix C.1. The August deployment served until 5 November;
v0.9.0 and v0.9.1 were deployed on 7 November, and I continued into 8 November."

### M2. Section 7.6 calls the upgraded F recovery a pre-upgrade baseline

**Current:** "Pre-upgrade baseline" (`:427`) includes "Cohort F recovery | 5 Nov" (`:437`).

**Problem:** F recovery used the upgraded 2.13.0 image; the blueprint reserves this subsection
for the August/October and N baselines.

**Evidence:** E25:8-25; `OUTLINE.md:266-268`; `manuscript.md:195-200`.

**Exact correction:** remove F recovery's table row from Section 7.6. Replace the parser-control
row's final cell in Section 6.2 with: "The pilot failed closed on 5 November (E24). The separate
corrected recovery passed five normal cases (median client confirmation 20.375 s), one direct
control and two replays (E25)."

**Section 5.1 final-sentence replacement:** "The August-October and N records form the
pre-upgrade baseline (Section 7.6); F and its recovery are post-upgrade history (Section 6)."

### M3. Numbered confirmations and provenance statements run together in the PDF

**Current:** "Otherwise it raises. 2. The dispatcher ..." (PDF p. 6) and
"at execution. 3. No independent external timestamp ..." (PDF p. 8).

**Problem:** the rendered layout merges numbered items that the Markdown presents separately,
obscuring the confirmation chain and the required three-part provenance statement.

**Evidence:** `manuscript.md:164-165,229-231`; PDF pp. 6 and 8.

**Exact correction:** preserve the wording and insert a blank line between every numbered item
in those two lists, so each item is rendered as a separate paragraph. No wording change.

### M4. Expand the main abbreviations at first use and disambiguate run labels

**Current:** "Google Cloud IAM access" (`:11`), "IAP authorization extension" (`:73`),
"HMAC-SHA256" (`:134`), "Structural defences for LLM agents" (`:48`) and
"F1, H1, J0, K1 and L1" (`:323,384`).

**Problem:** IAM, IAP, HMAC and LLM are not expanded. F1 labels both a failed pilot in Appendix
C.4 and a recovery trace in the census. N7/N7b are also introduced without a mapping to E19's
two batches.

**Evidence:** the cited manuscript locations; E28:46-47 (the F1 trace begins 5 Nov 21:34:50),
E24:33 (pilot published 19:59:11); E19:9-24; `manuscript.md:641`.

**Exact replacements:** "Google Cloud Identity and Access Management (IAM) access";
"Identity-Aware Proxy (IAP) authorization extension";
"HMAC-SHA256 (a keyed hash-based message authentication code)";
"Structural defences for large language model (LLM) agents".

In both census lists, use "F1 from the 5 November recovery, H1, J0, K1 and L1".
Before Appendix C.1's table, add: "N7 and N7b denote E19's stopped batch and fresh batch,
respectively."

### M5. Figure 3's caption can imply post-timeout IAM work in every attempt

**Current** (`:397`): "The red bar is the worker's own run, which continued past the boundary
and recorded model completions and IAM tool calls after it."

**Problem:** attempts 4 and 5 have no IAM tool call after their estimated boundaries.

**Evidence:** E29:92-104; `manuscript.md:415-423`; Figure 3.

**Replace the quoted sentence with:** "Each red bar is one worker run continuing beyond its
estimated boundary. Across the five runs, six model completions and three IAM tool calls were
recorded after those boundaries; post-boundary IAM tool calls occurred only in attempts 1-3."

## Corrections and additions to claim-reconciliation.md

- **Line 60, R7:** change Open to verified. ACM's deposited Crossref record names Peng Huang
  as the first author; the published paper's first page agrees in both the author list and
  its ACM Reference format, for DOI 10.1145/3102980.3103005. Retain Peng Huang in the manuscript.
  Primary records: <https://api.crossref.org/works/10.1145/3102980.3103005> and
  <https://web.eecs.umich.edu/~ryanph/paper/grayfailure-hotos17.pdf>.
- **Line 19, routing:** narrow "accepts ... only" to attributed history; the same source
  deliberately accepts bare JSON on the credential-protected request path. Replacement:
  "Attributed routing must name policy_step; Auditor-attributed routing is rejected. Bare
  JSON remains accepted on the authorised request path."
- **Lines 14 and 30:** the failure count and E19 numbers are correct, but the check misses
  the abstract/conclusion's stronger shared-success assertion (I2).
- **Lines 11, 24 and 47:** retain the verified counts but add the missing summary checks for
  fleet-version attribution (I4), November census dates (I3), cancellation wording (I1) and
  the complete retry/dead-letter inventory (I9).
- **Missing rows:** earlier acquisition/seal gaps (I5), collector-versus-system retry semantics
  (I8), and figure text, caption, date, font-size and final-PDF list checks (I6-I7, M1, M3, M5).
- **Line 65:** resolving S/E links is useful but does not establish sentence-level support or
  visual correctness. Keep the resolution check distinct from those substantive review checks.

**Deferred:** C4 and the cross-framework comparison remain future work under the frozen blueprint.
