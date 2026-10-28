# AGENTS.md

Canonical repository guidance for Codex, Claude Code, GitHub Copilot, and contributors.
Read HANDOFF.md next, then BASTION-REPORT-ROADMAP.md and docs/UPGRADE-PLAN.md.

## Shared state and private material

- Update root HANDOFF.md Current state, Next step, and Session log before ending work.
- Canonical manuscript sources live in report/. Never replace them with private historical copies.
- .local/ holds private captures, study checkpoints, publication notes, and historical plans.
  It is ignored, durable, and must never be committed or deleted during routine cleanup.
- Root guidance and roadmaps contain only public-safe project state.
- The 28 October maintainer request authorizes the ADK upgrade, documentation/site reconciliation,
  and a v0.8.0 release after validation. Preserve report edits uncommitted on the feature branch
  as explicitly requested; exclude report sources/build tools from release commits.
- Prepare the control matrix before paid execution; record a numeric study budget and stop rules.
  Credit availability alone is not a per-run spending cap. Previous study authorization is spent.

## Project and current state

Bastion is a Fortified Enterprise Fleet submission for the All Things Agentic Hackathon. Three
Google ADK agents review a real GCP IAM policy from approved asynchronous events: a managed Runtime
Orchestrator, a read-only Access Auditor, and a no-IAM-read Escalation Agent.

The source targets Google ADK 2.13.0 and A2A SDK 1.3.0. Deployment remains a separate
verification step; see [version provenance](docs/VERSIONS.md). As of 2026-08-25 the production path is deployed and verified: Pub/Sub/Eventarc durable ingress,
Firestore lifecycle, Agent Runtime/Identity, Memory Bank, Agent Gateway/IAP, Agent Registry, two
protected Cloud Run A2A workers, Model Armor, an IAM-private findings API, and retained operations
controls. The count-only capture records 21/21 APIs and 39 resources. The Python 3.12 suite has
321 tests at 100% configured core statement and branch coverage.

Five of seven observation captures are closed. Current-route IAM provenance, the agent-mediated
Model Armor refusal, the correlated payload-free audit trail and the Cloud Trace chain were all
captured on 2026-08-25 (evidence 11, 12, 13). Two remain deliberately open and their claims stay
narrowed: a managed Gateway refusal of an unregistered caller, and a watched
timeout/retry/dead-letter sequence. The five Devpost gallery images were composed on
2026-08-27 from those captures and are all dark; three carry captions narrowed to the panels
actually captured.

**The demo video is assembled, not edited.** As of 2026-08-29 `assets/demo-video/bastion.mp4`
exists: **3:53**, twelve beats, built by
[`scripts/assemble_demo_video.py`](scripts/assemble_demo_video.py) from the committed narration
rather than from a timeline editor, so the picture cannot drift from the sound. The opening is a
recording of the live public console; the rest is the redacted console and terminal evidence
retained as evidence 11, 12 and 13, plus the generated architecture and brand masters. The
narration therefore says the cut was **captured from the deployed fleet**, not that it happens live
on camera. It was published on 2026-08-29 at [https://youtu.be/Xpj8YmzFfpk](https://youtu.be/Xpj8YmzFfpk) with the 36-cue
caption track attached, and any beat can still be upgraded by dropping a screen recording into
`assets/demo-video/beats/`, which takes precedence automatically — a re-cut means re-uploading,
since the URL now points at a fixed file.

**The hackathon is over; the Devpost page still reads from `main`.** The entry was submitted on
2026-08-29 and judging has closed; no award is claimed anywhere. The judging freeze no longer
applies, but the public project page still embeds the architecture image from
`raw.githubusercontent.com/.../main/`, so a `scripts/render_diagrams.py` run on `main` silently
changes that page. Re-render on `main` only as an explicit decision. The video is a fixed YouTube
upload that cannot be replaced in place. Tag `v0.7.0` is the submission.

**A technical report is in progress** under `report/` (local draft): C1-C3 from the
August captures plus the separately dated
[27 October live validation](assets/evidence/14-live-validation.md). Twenty real-IAM
investigations completed in one durable attempt each, with 560 audit records across
60 invocations; this is one-project repeatability, not 20 independent policies or a privacy/SLO
benchmark. Preserve the collector-recovery disclosure and replay/trace/cost limits. Quote 62
bindings only from evidence 11 (25 Aug); no new binding census was exported. Installed package
resolution was not freshly enumerated, and the fleet was not upgraded for the study. State
upstream status with its check date and keep the author line "Independent researcher, Stockholm".

Read these before changing architecture or claims:

| File | Purpose |
|---|---|
| [Architecture](docs/ARCHITECTURE.md) | Current production route and trust boundaries |
| [ADRs](docs/adr/README.md) | Decisions and accepted risks |
| [Security](SECURITY.md) | Data/credential and enforcement rules |
| [Data governance](docs/DATA_GOVERNANCE.md) | Field-level processing and sovereignty |
| [Official brief](submission/DEVPOST.md) | Captured source requirements; do not paraphrase over it |
| [Submission ledger](submission/SUBMISSION.md) | Engineering proof versus human publication tasks |
| [P0/P1 ledger](submission/planning/08-audit-remediation-plan.md) | Remediation closure |
| [Observation backlog](submission/planning/09-capture-backlog.md) | Deployed but not yet observed |
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
- Google ADK 2.13.0 and A2A SDK 1.3.0 are pinned. Historical captures retain their
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

Live operator commands require explicit environment values and approved credentials:

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
`completed`. After any change to `agents/orchestrator/agent.py` or `runtime.py`, run both:

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
no credit-card charges. The private numeric ceiling and billing verification are in
`.local/credit-verification.json`. Paid-account credit spillover and eligibility remain
unresolved; hold deployment and paid controls. Budget alerts are not billing hard caps.
Never change billing linkage, payment methods, IAM or enable paid products to bypass this hold.

## Report generation order (maintainer correction, 28 October)

Stop iterative manuscript/PDF amendments and rebuilds. Finish the code, dependency, site,
deployment and feasible control/evidence work first. Then reconcile the final evidence and
generate one clean technical report. The current report is an interim local draft; preserve
it uncommitted. Do not rebuild it as a routine gate during the remaining implementation.
