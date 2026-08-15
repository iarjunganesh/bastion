# Contributing

Bastion is a solo hackathon submission on an 18-day schedule. This document exists so the
conventions are written down rather than remembered — including for the author, three days
from now, at midnight.

## Before you change anything

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — what the system is.
- [`docs/adr/`](docs/adr/README.md) — decisions that constrain the implementation. If a
  change contradicts one, amend that ADR in the same commit or add a new one. The code and
  the decision record are not allowed to disagree silently.
- [`submission/planning/03-build-plan.md`](submission/planning/03-build-plan.md) — what is supposed to be true today.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

cp .env.example .env       # edit GOOGLE_CLOUD_PROJECT, GCP_PROJECT_ID, Model Armor
gcloud auth application-default login
python -m dotenv run -- adk run --in_memory agents/orchestrator \
  "Run one Bastion access-review investigation."
```

There is no `make` on the author's Windows machine, so every command shown here is the direct
form. The `Makefile` remains the canonical description of *what* each step does, and CI runs on
Linux where `make` exists.

**There is no `make` on the author's Windows machine** — not in PowerShell, not in Git Bash.
The `Makefile` stays the canonical description of *what* each step does, and CI runs on Linux
where `make` exists, but anything typed here needs the direct command:

```powershell
python -m venv .venv; .venv\Scripts\Activate.ps1; pip install -r requirements-dev.txt
Copy-Item .env.example .env
gcloud auth application-default login
python infrastructure/trigger_investigation.py --mock-data
```

`GOOGLE_CLOUD_LOCATION=global` and `GCP_REGION=europe-north2` are **different settings**. Gemini
3.5 has no regional endpoint, so collapsing them 404s every model call with a message that
reads like a permissions failure ([ADR-004](docs/adr/004-flash-only-global-endpoint.md)).

## Conventions

**Commits** use a `type: subject` prefix — `feat:`, `fix:`, `docs:`, `chore:`, `release:`.
The subject says what became true, not which files moved.

**Releases** are annotated tags, `vX.Y.Z`, following
[`submission/planning/07-release-plan.md`](submission/planning/07-release-plan.md). Minor bump for a capability a judge
could watch; patch for a fix or captured evidence. **Never re-point a tag** — if `v0.6.0`
was wrong, `v0.6.1` fixes it. `CHANGELOG.md` is updated in the change that earns the entry,
not at release time.

**Python** is type-hinted on public functions, `ruff` clean, no bare `except`. `make ci` runs
lint, typecheck, and tests together; without `make`, that is:

```powershell
ruff check .; ruff format --check .
mypy agents registry runtime memory gateway model_armor observability
pytest tests -q --cov --cov-fail-under=100
python scripts/check_docs.py
npx markdownlint-cli2 "**/*.md"
```

`ruff format --check` is a separate gate from `ruff check` — a change that lints clean can
still fail the build on formatting. The coverage floor is 100% and matches real coverage; a
floor below it is a decoration, not a gate.

**Every deployed agent-to-agent call uses private Cloud Run A2A with workload identity.** The
managed Agent Gateway is not provisioned; contributors must not describe it as the current path.

## The two rules that matter most here

**Never commit a credential or a raw IAM policy dump.** See [`SECURITY.md`](SECURITY.md).

**Do not write a claim before it is verified.** This project's entire argument is
auditability. A README asserting a working injection block before one has been observed is
the exact failure the product is about. `submission/SUBMISSION.md` holds the list of
claims that are not yet earned; move an item out of it only after seeing the thing work.
