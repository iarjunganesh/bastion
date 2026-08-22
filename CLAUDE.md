# CLAUDE.md

Repository guidance for coding agents and contributors.

## Project and current state

Bastion is a Fortified Enterprise Fleet submission for the All Things Agentic Hackathon. Three
Google ADK agents continuously review a real GCP IAM policy: a managed Runtime Orchestrator, a
read-only Access Auditor, and a no-IAM-read Escalation Agent.

As of 2026-08-16 the production path is deployed and verified: Pub/Sub/Eventarc durable ingress,
Firestore lifecycle, Agent Runtime/Identity, Memory Bank, Agent Gateway/IAP, Agent Registry, two
protected Cloud Run A2A workers, Model Armor, an IAM-private findings API, and retained operations
controls. The count-only capture records 21/21 APIs and 33 resources. The Python 3.12 suite has
211 tests at 100% statement and branch coverage.

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
- Google ADK 2.7.0 and A2A SDK 1.1.2 are pinned.
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

Rollback and teardown are dry-run-first. Never broaden targets, delete Firestore/secrets/audit
state, or lock the audit bucket without explicit platform-owner direction. Bucket locking is
irreversible.

## Code conventions

- Type-hint public functions; use Ruff formatting; avoid bare `except`.
- Fixed agent tool sets and repository-owned descriptions only. Never interpolate external text
  into a tool declaration or Registry authority decision.
- Production dependencies are pinned in `requirements.txt`; the transitive lock is
  `requirements.lock`.
- Add tests at the boundary changed: unit for deterministic logic, integration for lifecycle,
  security for authorization/data leaks, load for concurrency.
- Maintain 100% statement and branch coverage; do not exclude new production logic merely to keep
  the number.
- Preserve payload-free audit semantics on every new model/tool/agent seam.

## Documentation and visuals

Claims must distinguish implemented, deployed, observed, configured, and not claimed. Update every
affected Markdown file, evidence record, diagram text, and count in the same change.

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
