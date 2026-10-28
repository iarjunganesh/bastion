# Bastion handoff

Read [AGENTS.md](AGENTS.md), this file, then the [report plan](docs/research/report-plan.md)
and [upgrade plan](docs/UPGRADE-PLAN.md). This is the shared session record for Codex,
Claude Code, and GitHub Copilot. Update Current state, Next step, and Session log before stopping.

## Current state

- **28 October 2026, Claude Code:** the report and GCP evidence work follow one sequence,
  [docs/research/report-plan.md](docs/research/report-plan.md) (uncommitted). **D1–D4 are
  decided** (no upgrade coupling, C4 deferred, per-chunk approval, teardown after the 8 November
  freeze); D5 is open. The report evaluates one primary cohort, N (November), on the unchanged
  August deployment; August and 27 October become provenance and pilot, not results.
- **E1 census done read-only (28 Oct 19:23 UTC):** fleet verifier passes; one image digest built
  23 August serves all four services; Runtime updated 23 August; **56** IAM bindings, three
  findings (1 `platform-infra`, 2 `security-engineering`); the only exception expired
  18 September; `bastion-audit` log bucket 365 days, unlocked; no Scheduler jobs. Private
  outputs: `.local/measurements/2026-10-28-ground-truth/`. Installed packages remain unlisted.
- **Repository reorganized (uncommitted, branch `feature/technical-report`, HEAD `2b35e6d`):**
  hackathon material is frozen in [archive/hackathon-2026/](archive/hackathon-2026/README.md);
  the claim matrix, remediation ledger, observation backlog and report plan are in
  `docs/research/`. Files the Devpost page or public console link on `main` stayed in place.
  CI, `check_docs.py`, `check_versions.py`, the redaction gate, Makefile and `.gitignore` follow
  the new paths; demo-video Make targets were retired; Ruff skips the frozen archive scripts.
- **Local cleanup:** caches, temporary folders, duplicate report build and `.local/` were removed
  after a verified out-of-repo archive (`C:/ws/.archives/bastion/`, 28 October). `.venv` was
  rebuilt from `requirements.lock` (ADK 2.13.0, A2A 1.3.0, 150 packages); use it for all gates.
- **Gates on the fresh `.venv`:** Ruff/format, mypy (40 files), 321 tests at 100% configured
  core coverage, nine experiment tests, versions (75 documents/18 pins), diagrams, redaction,
  site build/check and Markdownlint pass. `check_docs.py` passes except two historical paths in
  the untracked `report/build_report.py` (S5/S11), deferred to the Phase 5 re-pin.
- **v0.8.0 released 28 Oct** (PR #2 with the reorganization, merged and tagged). One
  OpenTelemetry advisory, CVE-2026-114603, is accepted with a single-ID audit exception because
  every ADK release caps OpenTelemetry below the fix; removal is tracked in [issue #3](https://github.com/iarjunganesh/bastion/issues/3).
  Source pins do not establish deployed pins: the fleet is unchanged since August.
- Report sources stay **uncommitted** in `report/`, excluded from release; only the interim
  13-page `report/bastion-technical-report-v1.pdf` remains. No manuscript prose was edited; the
  editorial source key in `sections-3-5.md` was repointed to the moved files.
- **Paid execution held** until the Phase 2 billing check: allocated credits only, no card
  charges; the private credit record is recreated in `.local/credit-verification.json` then.
- The report remains a draft; no DOI/arXiv deposit or author approval is implied by a code release.

## Next step

Follow [docs/research/report-plan.md](docs/research/report-plan.md); do not start from the older
sequence in docs/UPGRADE-PLAN.md until D1 is answered.

1. Phase 2 passed 28 Oct: October usage fully offset by credits (net 0.00 SEK). Next, pull the
   deployed image to list installed packages (E1 rest; Docker daemon was not running).
2. Phase 1, local and free: `report/OUTLINE.md` with the claim map and evidence-gap list, plus
   the offline A2A reproduction rerun on ADK 2.13.0 (O1). No manuscript prose or PDF builds.
3. Phase 3 in order E2, E3 → E4 → E7 → E5, E6, each with a pre-registered protocol approved
   in-session, a pilot, a sealed bundle, a promoted evidence file and a next-day billing check.
4. Evidence freeze on 8 November; fleet end state (D4) before the first credit expires on
   11 November; write and build the report once; publish only with explicit approval.
5. Track U: when an ADK release admits `opentelemetry-api` 1.45.1, close [issue #3](https://github.com/iarjunganesh/bastion/issues/3)
   and remove the audit exception. Redeploy only after the evidence freeze (D1).

## Session log

### 2026-10-28 / Codex — preservation and reconciliation

- Verified the existing feature branch and backed up 105 files with SHA256/ZIP verification.
- Confirmed live-site/source drift and latest ADK 2.13.0, including SDK/telemetry changes.
- Added shared root guidance and handoff, thin Claude/Copilot entry points, public-safe
  report roadmap, and upgrade/control plan. Kept private history in `.local/`.
- Upgrade and validation are in progress; no release or new cloud study is claimed here.

### 2026-10-28 / Codex — release audit and read-only fleet verification

- Existing-fleet verifier passed: four governed services, durable DLQ, Registry/Gateway and
  Model Armor configuration; zero new events/model calls/deployments.
- CI found vulnerable retained transitive pins. Refreshed the lock, removed evaluation-only
  fleet extras and raised Pillow to 13.0.0; only the ADK-constrained OpenTelemetry advisory
  remains. Hold Python release; static console correction is independent.
- Maintainer stopped iterative report edits/builds; no report change since that correction.

### 2026-10-28 / Codex — public console verified, closeout

- Published the reviewed static console from `d3fe889` through Vercel production deployment
  `dpl_BEFTqCsqiwydwdouBL7ArGYmc2k1`; public custom domain is READY. HTML/JSON/JavaScript
  match source (line-ending normalization only). Nine immutable evidence targets exist.
- Production desktop 1440px/mobile 375px checks pass: nine cards, dated inventory,
  explicit release-pending source stamp, no overflow/page errors/private network requests.
- PR #2 holds refreshed dependency remediation. At `d3fe889` every check except the known
  OpenTelemetry audit passes. No tag, GCP deployment, new event or model call was performed.
- The report remains uncommitted and untouched since the maintainer stopped iterative builds.
  Finish engineering/control evidence before one clean report generation.
- Validated local interpreter: `.tmp/adk-upgrade-venv/Scripts/python.exe` (Python 3.12);
  the pre-existing `.venv` was preserved and still represents the older environment. Recreate
  a fresh environment from `requirements.lock` when resuming; do not infer pins from `.venv`.
- Starting and final private/report work are preserved in external verified archives;
  exact machine-local paths and billing details remain in `.local/`, outside public commits.

### 2026-10-28 / Claude Code — grounding and master plan

- Grounded Codex's overnight work: five commits (`5524abe`–`2b35e6d`), PR #1 merged as `75ab108`,
  PR #2 green except the OpenTelemetry audit, evidence 15, and a second ignored report build
  `report/bastion-technical-report-v1-upgrade-review.pdf` beside the canonical PDF.
- Found why GCP work stalled (credits, then upgraded deployment, then a blocked release, chained)
  and listed six structural report defects, including stale E14/Scheduler statements now that
  evidence 14 and 15 are on `main`.
- Rewrote BASTION-REPORT-ROADMAP.md as the single master plan with decisions D1–D5, phases 0–6
  and evidence chunks E1–E8. Read-only inspection only; nothing deleted, built, run or committed.

### 2026-10-28 / Claude Code — archive, cleanup and root reorganization

- At the maintainer's request: deleted caches, `.tmp/`, `site/dist`, the duplicate report build,
  report QA renders and a stale Claude lock; archived `.local/` plus the OpenTelemetry
  patched-wheel records to a verified ZIP outside the repository, then deleted `.local/`.
- Moved 59 tracked hackathon files (and the ignored video master) into `archive/hackathon-2026/`
  with `git mv`, rewrote every link that pointed at them, and moved the three live ledgers and
  the plan into `docs/research/`.
  Merged the two Markdownlint configs into `.markdownlint-cli2.jsonc`.
- Rebuilt `.venv` from the lock and reran every offline gate (results under Current state).
  No GCP call, commit, push or report rebuild.

### 2026-10-28 / Claude Code — live ground truth and decisions D1–D4

- Ran read-only GCP checks: fleet verifier, Cloud Run revisions/image digests, Runtime update
  times and package spec, count-only IAM census (throwaway ID key, no secret read), Firestore
  exception/investigation/review counts, log-bucket retention, budgets and subscriptions.
- Recorded D1–D4 as decided and reframed the evaluation around cohort N; added E7, a
  repeatability batch with the instrumentation October lacked, and fixed the chunk order.
- Did not restructure the code into per-agent A2A services: it forces a redeploy, which D1
  defers until after the freeze. No deployment, event, model call, commit or push.

### 2026-10-28 / Claude Code — v0.8.0 release

- Confirmed no ADK release admits the OpenTelemetry fix (v2.8.0–v2.12.0 cap at 1.42.1, 2.13.0 at
  1.44). With the maintainer's explicit approval, accepted CVE-2026-114603 through a single-ID
  audit exception, documented in docs/DEPENDENCY-STATUS.md and tracked in [issue #3](https://github.com/iarjunganesh/bastion/issues/3).
- Released the reorganization and PR #2 content as v0.8.0; updated the site footer stamp. The
  fleet was not redeployed and the report stayed uncommitted.
