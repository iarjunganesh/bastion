# Bastion handoff

Read [AGENTS.md](AGENTS.md), this file, then the [report roadmap](BASTION-REPORT-ROADMAP.md)
and [upgrade plan](docs/UPGRADE-PLAN.md). This is the shared session record for Codex,
Claude Code, and GitHub Copilot. Update Current state, Next step, and Session log before stopping.

## Current state

- 28 October 2026: branch `feature/technical-report`; starting HEAD `405988a`.
  Preparing the v0.8.0 source/evidence/site release; no GCP deployment or paid study performed.
- Source pins Google ADK 2.13.0, A2A SDK 1.3.0, AI Platform/Agent Platform 2.6.0,
  and Model Armor 0.7.3. Universal Python 3.12 lock applies to CI, Cloud Run and managed Runtime.
- Locked offline gates: 321 tests, 100% configured core statement/branch coverage; mypy
  40 files; Ruff/format; nine experiment checks; six local report checks; docs/versions,
  diagram/redaction/site checks. See `.local/` logs for machine-local verification output.
- Report sources/build tools remain **uncommitted locally**, explicitly excluded from release.
  Canonical `report/bastion-technical-report-v1.pdf` rebuilt: 13 pages, 41 HTTPS links,
  zero automated findings and identical historical architecture-frame pixels. Section 4.1
  now holds one cohort/version table; historical measured versions remain unchanged.
- Starting work preserved in a verified external ZIP/manifest; machine-local location is in
  `.local/HANDOFF.md`. Never delete `.local/` or substitute its old report copies.
- Evidence 14 retains the unchanged 27 October sealed study. New evidence 15 is a read-only
  28 October census: 21 enabled APIs, 39 resources, four Cloud Run services, zero Scheduler jobs.
  The console's inventory stamp uses evidence 15; August diagrams/gallery/video stay historical.
- Production framework upgrade remains unverified; source pins do not establish deployed pins.
- **Paid execution held:** maintainer requires allocated credits only, with no card charges.
  The linked account is paid; eligibility and spillover protection remain unresolved. Private
  balance/expiry/ceiling evidence is in `.local/credit-verification.json`; do not publish it.
- Shared state is root-level. `.local/` holds private histories/captures only. Remote clones
  intentionally do not include the uncommitted manuscript; do not recreate it from old snapshots.
- The report remains a draft; no DOI/arXiv deposit or author approval is implied by a code release.

## Next step

1. Verify/publish the prepared v0.8.0 source/evidence/site tree, excluding `report/`.
   Confirm GitHub Actions and the public Vercel HTML/JSON against the release source.
2. Resolve credit usage scope and paid-account spillover protection. Budget alerts are not hard caps. No payment/billing mutation.
3. Once credits-only coverage is established, deploy both Cloud Run and managed Runtime,
   verify exact package/image/revision provenance and one pilot before any batch.
4. Run the control matrix in `docs/UPGRADE-PLAN.md` with count/time/cost limits and fresh
   evidence cohorts. Old study authorization is complete; no replay of its checkpoint.
5. Integrate any new measured results into the local report, rebuild/review, and obtain
   author approval separately before any manuscript commit or publication.

## Session log

### 2026-10-28 / Codex — preservation and reconciliation

- Verified the existing feature branch and backed up 105 files with SHA256/ZIP verification.
- Confirmed live-site/source drift and latest ADK 2.13.0, including SDK/telemetry changes.
- Added shared root guidance and handoff, thin Claude/Copilot entry points, public-safe
  report roadmap, and upgrade/control plan. Kept private history in `.local/`.
- Upgrade and validation are in progress; no release or new cloud study is claimed here.

## Report generation order (maintainer correction, 28 October)

Stop iterative manuscript/PDF amendments and rebuilds. Finish the code, dependency, site,
deployment and feasible control/evidence work first. Then reconcile the final evidence and
generate one clean technical report. The current report is an interim local draft; preserve
it uncommitted. Do not rebuild it as a routine gate during the remaining implementation.
