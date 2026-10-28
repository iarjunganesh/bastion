# Resource quick reference

## Ground truth

- [Captured official brief](../DEVPOST.md)
- [Submission checklist](../SUBMISSION.md)
- [Architecture](../../docs/ARCHITECTURE.md)
- [Security](../../SECURITY.md)
- [Data governance](../../docs/DATA_GOVERNANCE.md)
- [Operations](../../docs/OPERATIONS.md)
- [ADRs](../../docs/adr/README.md)
- [Evidence index](../../assets/README.md)

## Operator entry points

- `infrastructure/bootstrap.ps1` — Windows 11 deployment/reconciliation
- `infrastructure/verify_fleet.py` — deployed control verifier
- `infrastructure/smoke_test.py` — live Runtime, async, findings IAM/idempotency smoke
- `infrastructure/rollback.py` — dry-run-first safe revision rollback
- `infrastructure/teardown.py` — dry-run-first serving-resource removal
- `scripts/capture_gcp_state.py` — count-only live inventory
- `scripts/render_diagrams.py` — SVG variants and GIFs
- `scripts/redact_evidence.py` — declared masks for promoted PNGs and MP4s; `--check` is the gate
- `scripts/generate_demo_voiceover.py` — narration, captions, and the measured shot table
- `scripts/assemble_demo_video.py` — cuts the video from that narration; `--check` reports the plan
- `scripts/capture_site_hook.mjs` — records the opening beat from the live public console

## Fixed versions and regions

- Python 3.12; Google ADK 2.13.0; A2A SDK 1.3.0.
- Cloud Run/data transport: `europe-north2`.
- managed agent controls/audit: `europe-west4`.
- Gemini 3.5 Flash: Vertex AI `global`.

Do not copy values from private environment files into documentation. Placeholder project/engine
arguments in public instructions are deliberate.
