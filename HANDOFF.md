# Bastion handoff

Read [AGENTS.md](AGENTS.md), this file, the [report plan](docs/research/report-plan.md) and
[upgrade closeout](docs/UPGRADE-PLAN.md). Update Current state, Next step and Session log before stopping.

## Current state — 7 November 2026

- **Night of 7 November (uncommitted; records in `.local/measurements/2026-11-07-G` and `-H`):**
  cohort G deployed v0.9.0 (one build, amendment A1 for a stale keep-alive resume) and stopped at
  G5 on an observation-read failure (`collector_RetryError`; 4 validated). Cohort H reused G's fleet
  with bounded read retries (none were needed) and stopped at H28 (`unexpected_retry_or_failure`;
  27 validated): the Access Auditor's model call got `429 RESOURCE_EXHAUSTED`, the Orchestrator
  failed closed (`PolicyNotEnforcedError`), and Pub/Sub redelivery completed attempt 2. Both are
  stopped with no rerun and not pooled. The maintainer chose (7 November, 23:2x local) to fix this
  the production way: v0.9.1 adds a bounded, audited retry of transient model errors to the
  Access Auditor, and cohort I deploys v0.9.1 and repeats the design with model retries counted,
  not stops. Then E26, one docs PR, the 8 November billing check, the report edition, and D4.
- **v0.9.0 release prepared** on branch `fix/review-remediation-2026-11-07`: the review
  remediation, `google-adk` 2.14.0 with OpenTelemetry 1.45.2 (the v0.8.0 advisory is resolved;
  `pip-audit` clean with no exception) and the full documentation sweep. The maintainer approved,
  on 7 November: v0.9.0 (merge with a merge commit, then tag), the v0.8.0 release-note addition,
  keeping Vercel auto-deploy, cohort G on the v0.9.0 tag (200 SEK chunk cap, D3 total 400 SEK),
  a report edition labelled for v0.9.0, and no GitHub repository-setting changes. The review's
  findings and plan are in `.local/prompts/review-remediation-2026-11-07.md`; backups of `main`,
  all tags and `report/` are in `.local/backups/`.
- **Source-only fixes after the final deployment (not deployed):** the Escalation worker acts only
  on bare JSON or routing attributed to `policy_step` (latest wins); the Auditor refuses fields
  outside `AuditReport`; the Runtime app restores `ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS=false` after
  the template's set-up; the smoke Runtime check requires the completion confirmation; operator
  scripts are tested against the real SDK `Client`; receipts name their finding IDs and the
  completion gate compares them (deploy worker and Runtime together); a suite-wide isolation
  guard refuses child processes and non-loopback network. 373 tests at 100% configured coverage. The
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

1. Push, open the PR, wait for all CI jobs, merge with a merge commit (this redeploys the
   console), verify the live footer, tag the merge commit `v0.9.0` and verify the release, add
   the v0.8.0 known-issue note to its GitHub release, and close issue #3.
2. Cohort G: write and get approval for the protocol under `.local/measurements/2026-11-07-G/`,
   deploy the exact v0.9.0 tag to both surfaces together, run it before the D4 window, seal it,
   record evidence 26 and run the next-day billing check.
3. Rebuild the report once as the v0.9.0 edition with its link base on the tag commit; review
   every page and link; keep `report/` uncommitted.
4. Resume D4 in the agreed 8–10 November window, dry run first, after G's billing check.

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
Gates: Ruff/format, mypy (41 files), 373 tests at 100% configured coverage, docs, versions, site,
diagram, redaction, Markdown lint, 9 study cases and 16 report checks. No push, merge, deployment,
paid probe, PDF rebuild or publication.
