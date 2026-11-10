# AGENTS.md

Canonical repository guidance for Codex, Claude Code, GitHub Copilot, and contributors.
Read HANDOFF.md next, then docs/research/report-plan.md and docs/UPGRADE-PLAN.md.

## Shared state and private material

- Update root HANDOFF.md Current state, Next step, and Session log before ending work.
- Canonical manuscript sources live in report/. Never replace them with private historical copies.
- .local/ is the ignored home for private captures, study checkpoints and private values such as
  the credit record. Never commit it. Its pre-28-October history was archived outside the
  repository and removed at the maintainer's request; do not recreate it from old copies.
- Root guidance and roadmaps contain only public-safe project state.
- The 28 October maintainer request authorizes the ADK upgrade, documentation/site reconciliation,
  and a v0.8.0 release after validation (released 28 October). Report sources stayed uncommitted
  until the 10 November release PR (#18); they are now tracked in `report/`.
- Prepare the control matrix before paid execution; record a numeric study budget and stop rules.
  Credit availability alone is not a per-run spending cap. Previous study authorization is spent.
- The 7 November maintainer decisions authorize the review remediation, the `google-adk`
  2.14.0/OpenTelemetry 1.45.2 bump, release v0.9.0 (merge with a merge commit, then tag), keeping
  Vercel's auto-deploy from `main`, and cohort G on the v0.9.0 tag under a written protocol: a
  200 SEK credits-only chunk cap within a D3 total raised to 400 SEK. GitHub repository settings
  (branch protection, auto-delete, merge methods) stay unchanged.
- The 7–9 November decisions add: v0.9.1 (bounded, audited model retry) deployed for cohort I;
  separate chunks J–M to close the unreached controls, the trace and timeout gaps (credits only,
  per-chunk caps); evidence frozen after run M; **one definitive report** from the blueprint
  frozen on 9 November. No further live experiment is authorized. Editorial approval is not
  authority to delete resources (D4).

## Project and current state

Bastion is a three-agent, read-only GCP IAM-review fleet and technical-report case study.
The source pins Google ADK 2.14.0/A2A SDK 1.3.0 on Python 3.12. The core suite has
398 tests with 100% configured statement and branch coverage. [VERSIONS](docs/VERSIONS.md)
separates source pins, measured/asserted Cloud Run packages and unreadable Runtime resolution.

Cohort N is frozen on the August deployment. On 5 November both surfaces were updated, but F's
first pilot failed closed on an Escalation parser incompatibility ([E24](assets/evidence/24-upgraded-deployment-and-stopped-pilot.md)).
Separate corrected recovery passed its bounded controls; the refusal join uses a read-only
addendum after a collector false positive ([E25](assets/evidence/25-corrected-cohort-F-verification.md)).
Runtime stayed unchanged during recovery. Daily reported-usage billing passed on 6 November;
private values, late-posting and attribution limits stay in the credit record. On 7–8 November
v0.9.0 (cohorts G, H) and v0.9.1 (I–M) were deployed and measured: I validated 98 of 98, J's
controls passed, K and a census bounded trace export, and M observed a worker timeout reaching
dead-letter review ([E26–E29](assets/README.md)). Stopped runs are retained, never rerun or pooled;
protocols are pre-specified (local records, no external timestamp), not pre-registered.

Report sources are canonical and committed in `report/`. The report was released on
10 November as tag `report-2026-11` (merge commit `e9e86b0`), with the hashed PDF, source
manifest and snapshot attached to the GitHub release and DOI `10.5281/zenodo.24120596`.
Never move the tag, replace its assets or rebuild the released PDF. The blueprint
(`report/OUTLINE.md`) was frozen on 9 November: one definitive report, C1–C3, C4 deferred. The
6–7 November PDFs are drafts. Keep the author line “Independent researcher, Stockholm”, dated
counts (62 bindings on 25 August, 56 on 28 October, 62 at each 7–8 November preflight),
upstream contribution credit and every collection disclosure.

The hackathon is over. Tag `v0.7.0` is the 29 August submission; no award is claimed.
[The archive](archive/hackathon-2026/README.md), gallery and fixed video remain frozen.
Devpost embeds architecture images from `main`: render diagrams only by an explicit decision,
otherwise use `--check`. Do not regenerate those publication assets during a routine sweep.

Read these before changing architecture or claims:

| File | Purpose |
|---|---|
| [Architecture](docs/ARCHITECTURE.md) | Current production route and trust boundaries |
| [ADRs](docs/adr/README.md) | Decisions and accepted risks |
| [Security](SECURITY.md) | Data/credential and enforcement rules |
| [Data governance](docs/DATA_GOVERNANCE.md) | Field-level processing and sovereignty |
| [Claim matrix](docs/research/claim-matrix.md) | Bounds every public and report claim |
| [P0/P1 ledger](docs/research/remediation-ledger.md) | Remediation closure |
| [Observation backlog](docs/research/observation-backlog.md) | Deployed but not yet observed |
| [Evidence](assets/README.md) | Redacted observations and their proof boundaries |

## Non-negotiable architecture

The offline study in `experiments/minimisation/` uses synthetic policies only to
evaluate this design. The real-IAM rule below governs the product path. Study
fixtures must never use the project's actual IAM, HMAC key or credentials.
The study is outside shipped runtime code, core coverage and mypy scope.

- Audit real project IAM; synthetic data is never the primary source.
- Keep exactly three agents. Policy enforcement remains deterministic inside Orchestration.
- The production Eventarc dispatcher invokes managed Runtime only. It must not construct a local
  agent graph, hold the worker origin secret, or gain direct worker invocation.
- Runtime egress goes through Agent Gateway and Registry/IAP authorization.
- Raw IAM members, roles, resources, and bindings stop inside the deterministic Auditor tool.
- Missing or malformed risk fails closed. Models do not decide whether IAM is safe.
- Model Armor fails closed; deterministic protected-data screening runs after model output.
- Notification uses the fixed findings schema and deterministic idempotency key. No arbitrary URL
  or free-form binding payload is permitted.
- Audit events never contain tool values, prompts, responses, principals, exception messages, or
  secret material.
- IAM remains read-only. Bastion can request human review but cannot modify a binding.

## Regions and versions

- Python 3.12 everywhere: CI, release, Docker, Runtime, commands, and docs.
- Google ADK 2.14.0 and A2A SDK 1.3.0 are pinned. Historical captures retain their
  actual package versions. Only fresh verification of both deployment surfaces can
  establish an upgraded-production claim; see docs/VERSIONS.md.
- `GCP_REGION=europe-north2` for Cloud Run/data transport.
- `AGENT_RUNTIME_REGION=europe-west4` for Runtime, Memory, Gateway, Registry, Armor, audit.
- `GOOGLE_CLOUD_LOCATION=global` for Gemini 3.5 Flash. Never replace it with the compute region;
  this creates a misleading 404 and a false residency claim.

## Sensitive-output rule

Never commit or print service-account keys, ADC files, access/identity tokens, secret values,
`.env`, raw IAM policy/Asset output, full Cloud Run environments, principal inventories, private
URLs, prompts/responses, or unredacted findings. Ask GCP for the narrow field required. Evidence
must be redacted before it enters Git or a recording.

If a credential is exposed, rotate it first and rewrite history second. If a principal or policy
value appears in a capture, discard and re-record the capture.

## Local commands

Use Python 3.12. On the author's Windows machine there is no `make`; run direct commands:

```powershell
ruff check .
ruff format --check .
mypy agents gateway identity registry runtime model_armor observability infrastructure
pytest tests --cov --cov-report=term-missing --cov-fail-under=100
python scripts/check_docs.py
python scripts/check_versions.py
python scripts/render_diagrams.py --check
python scripts/redact_evidence.py --check
npx markdownlint-cli2 "**/*.md"
```

Before a tag only, `python scripts/check_versions.py --check-upstream` may use the network.

Live operator commands require explicit environment values and approved credentials. The
author's default `gcloud` project is not Bastion's: pass `--project bastion-fleet-2026` to every
CLI call, select the same project as each client library's quota project, and check CLI
authentication as JSON rather than text.

```powershell
python -m infrastructure.verify_fleet
python -m infrastructure.smoke_test
python -m infrastructure.rollback
python -m infrastructure.teardown
python scripts/capture_gcp_state.py --check
```

**`infrastructure/deploy.sh` alone does not redeploy the Orchestrator's actual agent graph.**
It only pushes the four Cloud Run services (findings API, Access Auditor, Escalation Agent, and
the durable Eventarc ingress named "orchestrator"). The `SequentialAgent` in
`agents/orchestrator/agent.py` runs on the managed Agent Runtime (a Vertex AI Reasoning Engine),
a separate deployment surface updated only by `python -m infrastructure.deploy_agent_runtime`
(idempotent against the existing `BASTION_RUNTIME_AGENT_ENGINE_ID`). Observed 2026-08-23: changing
`build_sub_agents()` to add a fifth step and redeploying only via `deploy.sh` left the Runtime
silently running the old four-step graph — no error, `investigation.run` still reported
`completed`. After any change to `agents/orchestrator/agent.py` or `runtime.py`, run both.
Since 7 November the Escalation worker's receipts and the completion gate share a contract
(each receipt names its routed finding IDs): a worker or Runtime deployed without the other
fails every investigation closed, so deploy both surfaces together:

```powershell
bash infrastructure/deploy.sh
python -m infrastructure.deploy_agent_runtime
```

`bootstrap.ps1` already does both in the right order; this note is for a code-only redeploy.

Rollback and teardown are dry-run-first. Never broaden targets, delete Firestore/secrets/audit
state, or lock the audit bucket without explicit platform-owner direction. Bucket locking is
irreversible.

## Code conventions

- Type-hint public functions; use Ruff formatting; avoid bare `except`.
- Fixed agent tool sets and repository-owned descriptions only. Never interpolate external text
  into a tool declaration or Registry authority decision.
- Production dependencies are pinned in `requirements.txt`; the transitive lock is
  `requirements.lock`; use it as constraints in development, Cloud Run, and managed Runtime.
- Add tests at the boundary changed: unit for deterministic logic, integration for lifecycle,
  security for authorization/data leaks, load for concurrency.
- Maintain 100% statement and branch coverage in the configured core scope; do not exclude new
  production logic merely to keep the number.
- Preserve payload-free audit semantics on every new model/tool/agent seam.

## Documentation and visuals

Claims must distinguish implemented, deployed, observed, configured, and not claimed. Update every
affected Markdown file, evidence record, diagram text, and count in the same change — **and
`site/`**. The public evidence console at
[bastion.arjunganesh.dev](https://bastion.arjunganesh.dev/) makes the same architecture and fleet
claims in `site/index.html` and `site/data/site-content.json` as the Markdown does, and it is easy
to forget precisely because it deploys separately (Vercel, not this repository's own CI/CD).
Observed 2026-08-23: a full doc sweep after the P0.1–P0.3 rewrite caught two stale site claims
(the Escalation card still read as model-driven; the Orchestrator card named only one gate) that
would otherwise have shipped unnoticed. Before any tag that changes agent count, agent
determinism, the request-path sequence, or a pillar's status, check `site/index.html` and
`site/data/site-content.json` against the same claim, then run `node site/build.mjs` and
`python scripts/check_site.py`.

`assets/architecture/gcp-state.json` is generated from live GCP and contains counts only. Never
hand-edit it. Architecture/16:9 SVG masters generate theme variants and GIFs with
`scripts/render_diagrams.py`; do not hand-edit generated variants. The README light/dark banner
pair is hand-reviewed and must stay visually aligned.

Do not claim immutable audit storage, end-to-end EU model residency, legal certification,
historical SLO attainment, or a wall-clock-week test. The precise limitations are part of the
topology, not marketing disclaimers.

## Git and release hygiene

Preserve unrelated user changes. Do not rewrite, squash, amend, or re-point history unless the
user explicitly asks. Release tags are separate from ordinary commits. Before pushing, inspect the
full diff, run offline/live gates appropriate to the change, and verify GitHub Actions after push.

## Credits-only execution condition

No new billable GCP work is authorized unless covered by the allocated credits with
no credit-card charges. The private numeric ceiling and billing verification belong in
`.local/credit-verification.json`. Eligibility was verified on 28 October: all October usage,
the 27 October study included, was fully offset by credits. There is still no hard cap, so paid
work runs only as approved, capped chunks with a next-day billing check, and the fleet must reach
its agreed end state before the credits expire. Budget alerts are not billing hard caps.
Never change billing linkage, payment methods, IAM or enable paid products to bypass this hold.

## Report generation order (maintainer correction, 28 October)

The original order was code/dependencies/site, deployment and feasible evidence first, then
one clean report. The maintainer explicitly authorized the final source/builder reconciliation
and local PDF on 6 November. The report was built, reviewed and released on 10 November
(`report-2026-11`); do not rebuild or re-release it. Publication, site deployment and the D4 end state remain separate.
