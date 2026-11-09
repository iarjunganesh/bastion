# Bastion handoff

Read [AGENTS.md](AGENTS.md), this file, the [report plan](docs/research/report-plan.md) and
[upgrade closeout](docs/UPGRADE-PLAN.md). Update Current state, Next step and Session log before stopping.

## Current state — 9 November 2026

- **Evidence is frozen.** v0.9.0 (cohorts G, H) and v0.9.1 (cohort I, chunks J–M) were deployed
  and measured on 7–8 November ([E26–E29](assets/README.md)). I validated 98 of 98, and its I99
  addendum is separate. J's controls passed. K plus a 142-trace census show incomplete Runtime
  graph-span export. M observed a worker timeout reaching dead-letter review, with worker
  computation continuing after the timeout. L (an instrument stop) and M's preflight amendment are
  retained. Nothing is rerun or pooled. Protocols are **pre-specified**, not pre-registered. Sealed
  hashes: `.local/measurements/seal-2026-11-09.json`.
- **Fleet retired (D4 closed 9 November).** Teardown A (`teardown.py` from `8f63fc6`) deleted
  25 of 26 allowlisted serving resources. The Gateway `bastion-egress` is retained because the
  retained Runtime engine's `agentGatewayConfig` references it (`FAILED_PRECONDITION`; an authz
  policy also targets it). It was not retried, by the maintainer's decision. The image repository
  and both build buckets are deleted (B). The 2 dead-letter messages were captured first by a
  separately dated, non-acknowledging read-only inspection (A0): exact event-ID joins to F1 and M1.
  The deployed v0.9.0/v0.9.1 images were exported by digest and verified.
- **Report:** one definitive report. The blueprint was frozen on 9 November (`report/OUTLINE.md`,
  local) after two external reviews and the maintainer's approval. The 6–7 November PDFs are drafts.
  Title: *Bastion: Execution Boundaries, Control Evolution, and Bounded Evaluation of a Governed
  Agent Fleet.*
- **Billing:** daily checks passed on 6 and 8 November (2–8 November fully offset by credits, net
  0). On 9 November billing was disconnected from `bastion-fleet-2026` only (verified: no billing
  account, billing disabled). The shared account and the other project are unchanged. Charges
  incurred earlier, including soft-deleted storage, may still post.
- **Retained, not deleted:** the Gateway (with its authz policy and extension), 2 Runtime engines
  with Sessions/Memory, Firestore, 2 secrets, the `bastion-audit` log bucket, service accounts and
  IAM. With billing off, billing-gated APIs refuse access, and these may become unrecoverable.
- **Known teardown gap:** `teardown.py` does not inventory the Gateway's dependants (the authz
  policy, the extension, the Runtime gateway reference). Its dry runs therefore could not predict
  the stop.
- **Preservation:** the local archives and an encrypted, independently verified off-laptop copy
  (695 files: the seal, A0 and both OCI images). Records are in `.local/d4/`, including
  `d4-closeout-2026-11-09.json`.

## Next step

1. **Done (local, uncommitted `report/`):** the complete manuscript was written from the frozen
   blueprint. It has 10 sections, Appendices A–C, 3 figures and about 11,400 words, and it builds
   to 23 pages with no validation findings. The claim-by-claim reconciliation is in
   `report/qa/claim-reconciliation.md`. One citation item is open: the first-author name of R7
   ("Gray Failure", HotOS 2017).
2. **Next:** the maintainer reviews the PDF (`report/bastion-technical-report-2026-11.pdf`).
   Corrections are verified evidence or accuracy fixes only, then one final build.
3. Run the final billing check after late postings.
4. Only after the maintainer approves the manuscript and the publication manifest: the
   `report-2026-11` tag, the DOI (Zenodo) and the site release. No new experiments.

## Session log

### 28 October–4 November

v0.8.0 source release and D1–D4 decisions; cohort N collected, audit corrections prepared,
main manuscript rewrite and T1–T3 wording approved. The full earlier journal is retained privately
in the pre-sweep snapshot; current evidence and protocols are linked from the report plan.

### 5 November

Original F failed closed after deployment. Separately approved same-day recovery deployed the
exact Escalation parser correction with Runtime unchanged and observed the bounded controls.
Its final refusal collector stopped on a temporal false positive; read-only exact-ID validation
closed the observation without rerunning a paid probe. Both cohorts were sealed separately.

### 6 November — billing and final sweep

Reviewed Overview, daily SKU, Project, Credits and the supplied CSV; recorded a passed daily
reported-usage check with attribution/late-posting limits. CLI/API metadata alone exposed no
accessible billing export. The maintainer then authorized the final PDF and shorter current docs.
Preserved the dirty tree/report and requested independent review. Corrected stale F/billing,
security/dependency and approximate-dead-letter claims; retained original capture disclosures.
Final validation: 336 core cases at 100% configured statements/branches, 12 report checks,
9 study cases plus 6 subtests, Ruff/format, mypy (40 files), docs/version, redaction, diagram
freshness, static site build/check and Markdown lint passed. The 14-page PDF passed automated
and full visual review after table-width and generated-Markdown spacing corrections; all collection disclosures remain.
Original F/recovery seals and the pre-sweep preservation ZIP were rechecked. No cloud call,
new paid probe, commit, push, tag, publication or shutdown occurred in this sweep.

### 6 November — local Git cleanup

The maintainer asked why public changes were still uncommitted. The sweep had completed;
only the report was required to remain uncommitted. Finalized the reviewed public code,
documentation, evidence and site-source changes in a local commit after an explicit-path
staging check. `report/` and `.local/` were excluded. The completed PDF/source snapshot retain
their original bytes and base-revision provenance; Git housekeeping does not rebuild the report.
No push, tag, cloud action or publication.

### 6 November — explicit release/deployment provenance

Added the missing v0.8.0 release row and commit to Appendix A, retaining the distinction from
the later deployed image/source overlays. Verified GitHub release/tag metadata and local Git
ancestry. Pinned the report's public-link base so unpublished local commits cannot silently
replace it. The 14-page PDF has 38 clickable references and a 58-file source snapshot; twelve
report checks, automated layout checks and changed-page visual review passed. Version-ledger
and handoff corrections are committed locally; report sources/output remain uncommitted.
No push, retag, deployment or new probe.

### 6 November — public source integration

The maintainer requested branch publication and merge into `main`. Published the two public
commits and opened [PR #9](https://github.com/iarjunganesh/bastion/pull/9); integration requires
passing hosted CI on the final head and uses a merge commit to preserve history. The final
local rerun passed 336 cases at 100% configured coverage after using a writable pytest temporary
directory. Public guidance now records this authorization separately from report publication.
The report/PDF bytes and private captures are preserved; no rebuild, retag, GCP deployment,
paid probe or shutdown is part of this integration. The GCP deploy workflow remains manual-only.

### 6 November — late link review

PR #9 merged with history preserved; all eight post-merge CI jobs passed. An automated review
arrived after merge and identified removed README anchors still advertised by the Agent Card
and frozen submission. Verified both references and restored `the-fleet` and `quality-gates`
beside the replacement sections. Runtime metadata and archived files need no changes.
Report sources/output remain uncommitted and byte-identical; no report rebuild or cloud action.

### 7 November — independent review and remediation

An independent read-only review cross-checked code, evidence 16–25, the sealed F/recovery and
billing records, and the PDF. It verified the numbers and seals and found two code-level gaps,
an undisclosed v0.8.0 deployability issue, documentation drift and report clarity issues. Merged
branches were deleted locally and on `origin`; `main` was backed up as a verified bundle.
Remediation on `fix/review-remediation-2026-11-07`: source-only code fixes with tests (`84b9d86`),
documentation and append-only evidence notes (`55e3647`), and uncommitted report-source and
builder corrections. While the new SDK-surface tests were being written, two read-only
`gcloud run services describe` calls against a non-existent test project ran because of a wrong
override variable name; both failed and nothing changed. A suite-wide isolation guard now refuses
child processes and non-loopback network or DNS in every test (the suite needed no exemption).
Receipts now name their finding IDs and the completion gate compares them; deploy both surfaces
together.
Gates: Ruff/format, mypy (41 files), 373 core cases at 100% configured coverage, docs, versions, site,
diagram, redaction, Markdown lint, 9 study cases and 16 report checks. No push, merge, deployment,
paid probe, PDF rebuild or publication.

### 7–9 November — final deployment, measurement and blueprint freeze

PR #11 (v0.9.0) and PR #12 (v0.9.1, the bounded audited model retry, after H28's 429) were merged
and tagged. Measurement covered G and H on v0.9.0, and I–M on v0.9.1. Billing was checked on
8 November. After a GPT/Codex second opinion, the maintainer chose one definitive report and
approved a frozen blueprint (9 November), using "pre-specified" wording, three-part provenance
statements and M's reconstructed protocol hash as a disclosed limitation. Read-only post-hoc
analyses (the M ordering check and the trace census) are labelled as such. The G–M records were
sealed on 9 November.

### 9 November — D4 closeout

PR #13 (E26–E29 and the documentation sweep) and PR #14 were merged. PR #14 is the
inventory-first, allowlisted teardown, with four review findings fixed: status-only errors, exact
not-found parsing, list/describe reconciliation and delete timeouts. Before teardown:

- A0 inspected the 2 dead-letter messages without acknowledging them and joined them to F1 and
  M1 by event ID. It is post hoc and separately dated; E29 is unchanged.
- The two deployed images were exported by digest.
- The cohort build sources were verified against the source manifests.
- The encrypted off-laptop backup was independently verified.

Then A deleted 25 of 26 resources; the Gateway was retained because of the Runtime dependency.
The maintainer then ran B (the repository and 2 buckets) and C (billing unlinked from this project
only) in their own terminal, because local permission rules blocked Claude's delete commands.
Read-only checks confirmed the end state. The seals are unchanged (73/73 files).

Then the complete manuscript was written once from the frozen blueprint. The previous drafts are
archived privately. It has 3 new figures (topology and trust boundaries, chronology, M's timeout
timeline), was reconciled claim by claim against E01–E29 and the v0.9.1 source, and was built to
a 23-page review draft with no layout or citation findings. The tag and DOI are not created.
