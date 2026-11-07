# Bastion handoff

Read [AGENTS.md](AGENTS.md), this file, the [report plan](docs/research/report-plan.md) and
[upgrade closeout](docs/UPGRADE-PLAN.md). Update Current state, Next step and Session log before stopping.

## Current state — 7 November 2026

- **Independent review remediation in progress** on branch `fix/review-remediation-2026-11-07`
  (local commits `84b9d86`, `55e3647` and this handoff; not pushed). The review found no
  numerical error in the report and verified the F/recovery seals, hashes, counts and billing
  corroboration. Its findings and the ordered plan are in the private prompt
  `.local/prompts/review-remediation-2026-11-07.md`; a verified bundle of `main` and all tags and a
  copy of `report/` are in `.local/backups/`.
- **Source-only fixes after the final deployment (not deployed):** the Escalation worker acts only
  on bare JSON or routing attributed to `policy_step` (latest wins); the Auditor refuses fields
  outside `AuditReport`; the Runtime app restores `ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS=false` after
  the template's set-up; the smoke Runtime check requires the completion confirmation; operator
  scripts are tested against the real SDK `Client`; receipts name their finding IDs and the
  completion gate compares them (deploy worker and Runtime together); a suite-wide isolation
  guard refuses child processes and non-loopback network. 360 tests at 100% configured coverage. The
  deployed fleet keeps the earlier behaviour; no GCP redeploy is planned or authorized.
- **Documentation:** CHANGELOG `[Unreleased]` corrected (the completion fix was deployed on
  5 November) with a dated v0.8.0 known issue: the tag calls `Client.agent_engines`, absent from
  its own pinned SDK, so it is not deployable as tagged. VERSIONS records that and the `d7d6a99`
  amendment of PR #8's `ed1d820`. Architecture, claim matrix and observation backlog bound the
  routing-provenance and span-content findings. Evidence 13, 19 and 22 gained append-only notes.
- **Site:** Vercel deploys production from `main`. The PR #9 merge redeployed the console; on
  7 November its footer matched `2a12f5f`. Treat every merge to `main` as a site deployment.
- **Evaluation, versions, billing and end state** are unchanged from 6 November: N frozen; F
  failed closed (E24); corrected recovery passed its bounded controls (E25); Runtime packages
  unreadable; the 6 November reported-usage check passed with values kept private; D4 remains
  8–10 November, dry run first, before 11 November.
- **Git:** PR #9 (`6c1c832`) and PR #10 (`000a227`) are merged; their branches were deleted locally
  and on `origin` on 7 November. Integration keeps merge commits; no history rewrite or retag.
- **Report:** `report/` sources now carry the review corrections (N1–N7 chunk names, routing and
  release limitations, nits, a §7.4 addition) and builder checks (two-digit evidence citations, no
  chunk-style E names, no split hyphenation, line-ending-canonical hashes, non-link code colour);
  16 report checks pass. The 6 November PDF, manifest and snapshot are unchanged and **no longer
  match the edited sources**; one rebuild follows the merge, with the link base moved to it.

## Next step

1. Maintainer decisions: push this branch and open a PR; merge with a merge commit after CI
   (the merge redeploys the console); optional receipts that echo finding IDs (deploy-order
   hazard); keep or disable Vercel auto-deploy; the v0.8.0 GitHub release-note addition; the
   report edition label and date.
2. After the merge: set `REVISION` in `report/build_report.py` to the merge commit, update the
   A.1 link-base text, build the PDF once, review every page visually, re-verify all links and
   record `qa/checks.json` honestly. Keep `report/` uncommitted.
3. Resume D4 in the agreed 8–10 November window with an owner-reviewed dry run and residual-cost
   decision. Do not bring shutdown forward or broaden deletion targets.
4. Publication, tag, DOI and any GCP redeploy remain separate approvals.

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
Gates: Ruff/format, mypy (40 files), 360 tests at 100% configured coverage, docs, versions, site,
diagram, redaction, Markdown lint, 9 study cases and 16 report checks. No push, merge, deployment,
paid probe, PDF rebuild or publication.
