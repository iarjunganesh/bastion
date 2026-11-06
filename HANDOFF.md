# Bastion handoff

Read [AGENTS.md](AGENTS.md), this file, the [report plan](docs/research/report-plan.md) and
[upgrade closeout](docs/UPGRADE-PLAN.md). Update Current state, Next step and Session log before stopping.

## Current state — 6 November 2026

- **Final sweep and local PDF complete.** The maintainer requested whole-repo drift cleanup,
  careful simplification and the final technical-report PDF. This supersedes the earlier report
  build hold. Keep `report/` uncommitted. The later request authorizes public branch publication
  and integration into `main` after hosted CI; GCP deployment and paid probes remain separate.
- **Preservation:** before editing, 45 dirty/report files were backed up in
  `.local/sweeps/2026-11-06-final-report/before-sweep.zip` with a manifest. Both F capture seals
  and ZIPs are recorded separately. That snapshot retains the full previous handoff/session log.
  Prior private history removed before 28 October was not restored.
- **Evaluation complete:** N is frozen on the August deployment. Original F updated both surfaces,
  then its pilot failed closed ([E24](assets/evidence/24-upgraded-deployment-and-stopped-pilot.md)).
  Separate corrected recovery passed five normal cases, direct confirmation and two replays;
  its refusal join uses a read-only addendum after a collector false positive
  ([E25](assets/evidence/25-corrected-cohort-F-verification.md)). Runtime stayed unchanged in recovery.
  Preserve the raw collector stop, incomplete X1 and unresolved drain receipt. No further F run.
- **Versions:** the released v0.8.0 tag is `4d70b1b`; the November deployments use later
  descendants plus SDK/parser fixes. The current image asserted ADK 2.13.0/A2A 1.3.0/SDK 2.6.0; Runtime installed
  packages remain unreadable. [VERSIONS](docs/VERSIONS.md) is authoritative. Core validation
  passed 336 cases at 100% configured coverage in the final sweep; Ruff/format, mypy and
  all docs/version/site/diagram/redaction/Markdown gates passed.
- **Billing:** the 6 November reported-usage check passed. Screenshots refreshed balances/expiry;
  the supplied CSV's 61 dated rows corroborate the daily totals and zero report total. Exact
  per-chunk attribution, the small gross aggregation difference and late postings remain bounded.
  Values and both full chunk reservations stay in `.local/credit-verification.json`.
- **End state:** D4 remains 8–10 November, dry run first, before 11 November. Retained
  Firestore, secrets, Runtime/Memory and audit state need an owner decision; none was deleted.
- **Git and public surfaces:** public cleanup (`2a12f5f`) and release-provenance correction
  (`289577d`) are published through [PR #9](https://github.com/iarjunganesh/bastion/pull/9),
  from `docs/evidence-audit-reconciliation` into `main`. The PR records hosted CI and merge status.
  Integration preserves commit history and excludes `report/` and `.local/`; no release tag changes.
  The site snapshot remains the
  28 October inventory. Frozen gallery/video/architecture assets retain their dates and bytes.
- **Report:** canonical `report/sections/` now incorporates the prepared audit corrections,
  separate E24/E25 populations, bounded billing and verified primary references. The 14-page PDF is generated and visually reviewed, with
  38 clickable references, no unresolved
  placeholders or automated layout findings. Twelve report integrity checks passed; the
  canonical sources/build inputs and cited files have a 58-file snapshot. The figure is unchanged.
  No reliability rate, C4 result, universal privacy proof or completed shutdown is claimed.

## Next step

1. Maintainer review of the completed local PDF at `report/bastion-technical-report-v1.pdf`.
   Public source integration is tracked in [PR #9](https://github.com/iarjunganesh/bastion/pull/9);
   report sources/output remain uncommitted and unpublished.
2. Keep `report/source-manifest.json`, `source-snapshot.zip` and `qa/checks.json` with the PDF.
   Unchanged citations use the base commit; changed/unpublished records use the local snapshot.
3. Resume D4 in the agreed 8–10 November window with an owner-reviewed dry run and residual-cost
   decision. Do not bring shutdown forward or broaden deletion targets.
4. Publication/tag/DOI/site release remain separate. Refresh upstream/public references on the
   actual publication date. Keep report sources uncommitted unless explicitly instructed otherwise.

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
local rerun passed 336 tests at 100% configured coverage after using a writable pytest temporary
directory. Public guidance now records this authorization separately from report publication.
The report/PDF bytes and private captures are preserved; no rebuild, retag, GCP deployment,
paid probe or shutdown is part of this integration. The GCP deploy workflow remains manual-only.
