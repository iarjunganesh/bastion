# Bastion handoff

Read [AGENTS.md](AGENTS.md), this file, then the [report plan](docs/research/report-plan.md)
and [upgrade plan](docs/UPGRADE-PLAN.md). This is the shared session record for Codex,
Claude Code, and GitHub Copilot. Update Current state, Next step, and Session log before stopping.

## Current state (4 November 2026, evening)

- **Cohort N is complete and recorded.** All chunks ran on the unchanged August deployment and
  are written up as evidence 16–22:

  | Chunk | Result | Evidence |
  |---|---|---|
  | E1 census + packages | 56 bindings, 3 findings; one image digest (built 23 Aug, `google-adk` 2.7.1, 161 packages) | 23 |
  | E4 exception lifecycle | approval suppressed, expiry returned the finding | 16 |
  | E2 negative authorization | 15/15 expected (13 refusals or denials, 2 controls) | 17 |
  | E3 Model Armor re-probe | control completed, injection refused | 18 |
  | E7 / E7b repeatability | E7 stopped on a false completion; E7b 20/20 | 19 |
  | E5 Gateway (read-only) | 176 fail-closed IAP denials; the same as the August defect D2 | 20 |
  | E6 retry and dead letter | 5 deliveries, dead-lettered with count 5, no state written | 21 |
  | O1 offline A2A repro | boundary unchanged on 2.13.0; both upstream warnings fire | 22 |

  E8 was skipped (C4 deferred, decision D2). Cohort N spend was under 1 SEK, fully offset by
  credits (billing to 4 Nov: 0.84 SEK gross, 0.00 net).
- **Claim matrix reconciled.** The August `Partial` rows (Gateway, retry/DLQ) closed with
  narrowed wording. *Durable completion integrity* stays not-safe-to-claim until cohort F. The
  Gateway wording must say the refused host is registered (defect D2), never "unregistered
  destination".
- **Source fixes are merged but not deployed.** `run_managed_runtime` requires the completion
  gate's confirmation, and guardrail refusals carry the investigation ID. Suite: 330 tests at 100%
  configured core coverage. Codecov upload is best-effort (3-minute limit).
- **Git:** the base `main` includes PRs #4–#7 (merged 4 Nov). The active branch is
  `fix/study-budget-and-report-notes`, preparing the tracked study-budget correction and handoff.
  The private bundles are in
  `.local/measurements/`, sealed with manifests and ZIPs.
- **Report:** rewritten on 4 Nov (maintainer's request) to `report/OUTLINE.md`, one file per
  section in `report/sections/`, private and uncommitted. Thesis: *silent success at agent
  boundaries*, data minimisation as the design. Only cohort F results, the date, `REVISION`, the
  billing recheck and the U1–U4 refresh are `[[…]]` placeholders. The 28 Oct draft and PDF are
  archived in `.local/report-archive-2026-11-04/`. `build_report.py` still targets the old layout.
- **Unchanged facts:** v0.8.0 is the current release (28 Oct). One OpenTelemetry advisory is
  accepted ([issue #3](https://github.com/iarjunganesh/bastion/issues/3)). The fleet runs the
  23 August build. The public console makes no cohort-N claims yet.
- **Targeted report wording changes applied on 4 November, with maintainer approval.** T1–T3
  credit the upstream contribution in §7.2/U2, date the census measurements in §5.1/E11, and
  clarify §9's deferred matched-explanation study. §8 refers to the dated census rather than
  repeating an undated binding count. Supporting upstream records were checked read-only on
  4 November. Report sources stay uncommitted; placeholders, cohort F text and build tools are
  unchanged. The tracked study config and validator now allow at most D3's 100 SEK total;
  any future approved budget must fit the remaining allocation. Generation remains disabled.

## Next step

**Immediate:** validate and merge the tracked study-budget correction through a PR, as authorized
by the maintainer. Keep `report/` uncommitted; C4 stays deferred and missing-workflow-step cases
remain planned. No PDF build or live run is part of this wording/budget correction.

Follow [docs/research/report-plan.md](docs/research/report-plan.md). Live or paid steps need the
maintainer's go (D3). Credits only; 100 SEK total cap.

1. **5 Nov:** billing recheck for late-posted 3–4 Nov usage. Verify related-work references
   against their primary sources (offline).
2. **8 Nov:** evidence freeze.
3. **8–10 Nov, cohort F** (needs a go at deploy time): redeploy `main` to the four Cloud Run
   services and the managed Runtime, verify the fleet, run about 5 investigations, and report
   them separately. Note that this also moves the fleet from `google-adk` 2.7.1 to 2.13.0, so
   F measures the fixes and the upgrade together.
4. **Before 11 Nov:** fleet end state D4, dry run first. The maintainer chooses the residual
   storage; Firestore, secrets and audit state are never deleted.
5. **8–13 Nov:** write the report once from the outline. **14–16 Nov:** publish with explicit
   approval (tag, release, Zenodo DOI, site update).
6. Track U: when an ADK release admits `opentelemetry-api` 1.45.1, close issue #3 (still blocked
   on 2.13.0).
7. Optional: ask Google Cloud support the D2 question in the observation backlog.

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

### 2026-11-03 / Claude Code — E4 exception lifecycle

- Built the E4 collector from the October bundle's collector, passed a read-only preflight
  (fixed the approver impersonation billing to the CLI default quota project), then ran three
  investigations and one maintainer-authorized, 15-minute exception approval.
- Every expected count matched; the approval replaced only the exception that had expired
  18 September. No retries, replays, deployments or IAM changes.
- Sealed the private bundle (manifest, ZIP, protected-shape scan clean), wrote evidence 16,
  added the claim-matrix row, and recorded the token and trace gaps for E7. Nothing committed.

### 2026-11-03 / Claude Code — E2 and E3

- On the maintainer's go: wrote both probes from the E4 collector, passed read-only preflights,
  then ran them once each. E2 made no model call; E3 sent two A2A messages to the Auditor with
  the peer credential held in memory only.
- E2: all 15 checks matched expectations (13 refusals or denials, 2 positive controls), with the
  exception ledger unchanged. E3's control completed and its
  injection was refused; the refusal record was found by service and time because it lacks
  the investigation ID.
- Sealed both bundles, wrote evidence 17 and 18, updated the claim matrix and plan. Nothing
  committed.

### 2026-11-03 / Claude Code — E7 stopped

- On the maintainer's request, ran E7 with two-minute idle boundaries for token attribution
  and per-publish delivery matching (both validated on E4's data first).
- Stopped at run 8 on `unexpected_delivered_counts`: a false completion with no work done.
  Diagnosed read-only from Runtime and Orchestrator logs; no rerun. Sealed the bundle and
  ran the token, delivery and trace reads for the eight runs.

### 2026-11-03 / Claude Code — E7b

- Fresh 20-run batch on the maintainer's go, recording false completions instead of stopping.
  all 20 runs passed with no false completion; replays, deliveries and per-run tokens measured.
- Matched the five slow runs to Runtime instance starts read-only (three coincide, two do not).
  Sealed the bundle, wrote evidence 19, added two claim-matrix rows. Nothing committed.

### 2026-11-04 / Claude Code — billing, evidence commit and source fixes

- Billing 29 Oct–4 Nov from the maintainer's console: 0.84 SEK gross, fully offset, 0.00 net
  (3 Nov evening may still be posting). Recorded in the private credit record.
- Branched `evidence/cohort-n` from `main`; committed evidence 16–19 and the ledgers, then
  reworded batch pass counts the suite-total gate misread as test totals. Not pushed.
- Wrote both source fixes with tests (uncommitted, deploy after the freeze). The first run
  needed pytest's base temp in the scratchpad (sandbox denied the default temp folder).

### 2026-11-04 / Claude Code — completion-check risk closed, E8 skipped

- Verified the Runtime stream's wire shape in the SDK (server and client) instead of assuming
  it; made the check exact and pinned it to the SDK serializer. Suite still 330 at 100%.
- Recorded the 4 Nov gate: E8 skipped. Reviewed the draft report: substantial rewrite after
  the freeze, with an outline now. Nothing committed for the fixes.

### 2026-11-04 / Claude Code — E5/E6 design, grounded read-only

- Merged PR #4 (cohort N evidence and fixes) and PR #5 (Copilot wording corrections); deleted
  the merged branches. `main` is current.
- E5: the Gateway governs Runtime egress only, so the plan's "unregistered caller" framing was
  wrong. 176 IAP refusals of unmatched egress already exist in the logs (12 per Runtime
  instance start); the refused host does have a Registry entry, which stays unexplained.
- E6: dead-letter grants are present and the boundary has never fired. Proposed one synthetic
  rejected event on the production subscription. Both notes are in the report plan and
  await the maintainer's go; no live action taken.

### 2026-11-04 / Claude Code — E5 and E6 executed

- E5 (read-only): configuration, 176 IAP decisions, 13 instance starts and investigation
  counts collected and sealed in `.local/measurements/2026-11-04-E5/`; evidence 20.
- E6 (approved fault injection): one `mock_data: true` event published 20:35:51 UTC; five
  HTTP 400 deliveries, dead-lettered with delivery count 5, pulled by marker and acknowledged;
  0 investigation documents. The first collector crashed on an empty pull; resumed without
  republishing, disclosed in evidence 21 and kept in the bundle.
- Claim matrix: Gateway and Retry/DLQ rows now `Yes` with their stated wording.

### 2026-11-04 / Claude Code — E1 packages, O1, outline, PR #6

- E1: streamed the serving image's pip layer (no disk write): 161 distributions, Python 3.12.14,
  requirements identical to `f589b25`. The Runtime returns no source archive; stated, not inferred.
- O1: fresh 3.12 env from the lock; original repro and an extended both-directions run; both
  upstream warnings fire; evidence 22.
- Codex review on PR #6: reconciled AGENTS.md and the observation backlog. The public site makes
  no Gateway-refusal or dead-letter claim; cohort N evidence reaches it with the report (D5).

### 2026-11-04 / Claude Code — documentation reconciliation

- Corrected evidence 20: its "unexplained mismatch" is the August defect D2, recorded with the
  same signature and an inferred cause. Also removed Model Armor and Vertex AI from the Runtime's
  egress list (the Runtime calls neither). The claim matrix, report plan, backlog and outline
  now say the same.
- Rewrote this handoff's current state and next steps. Brought the report plan (status line,
  cohort F, order as run), VERSIONS, README, ADR-006 and AGENTS.md up to date.

### 2026-11-04 / Claude Code — report rewrite and evidence 23

- Confirmed PR #6 merged and no feature branches remain.
- Backed up `report/` (hash-verified ZIP), removed the 28 Oct draft files, and wrote the
  manuscript to the outline in `report/sections/` (about 5,000 words plus references; citation
  keys all resolve).
- Evidence 15 never covered the IAM census or packages (it is a count-only inventory), so both
  are now evidence 23; evidence 15 gains a pointer only.

### 2026-11-04 / Codex — targeted report wording review

- Prepared T1–T3 as current text, proposed replacements and supporting sources for maintainer
  review. Verified issue #6854, PR #6859's two author commits, import `d2cb22e` and the v2.12.0
  release record read-only on GitHub.
- Checked the dated E11/E23 census boundaries and the synthetic study's matched explanation
  and injection cases. Missing-workflow-step cases remain a planned extension, with no C4 run
  authorized; the study's configured 200 SEK ceiling still needs reconciliation with D3.
- Updated this handoff only. No manuscript edit, PDF build, commit, push, deployment or live
  experiment; proposed wording awaits the maintainer's explicit go.

### 2026-11-04 / Codex — approved wording and study-budget correction

- On the maintainer's go, applied T1–T3 to the uncommitted manuscript and removed §8's undated
  duplicate census count. Preserved the title, author line, placeholders, cohort F text, disclosure
  and build tools. No PDF build or live run.
- Lowered the tracked study config and validator from 200 to 100 SEK, within D3's remaining total;
  generation remains disabled and C4 remains deferred. Documented missing-workflow-step cases as
  planned, with no model runner or new spending authorization.
- The 101 SEK rejection test failed before the fix; all nine offline controls pass after it.
  Added these controls to CI. Ruff, Markdown lint and the public documentation/version gates pass
  (the latter in a clean tracked-file export). Local checks still see the pre-existing private
  report-builder paths and historical-version entry; those stay outside this correction.
