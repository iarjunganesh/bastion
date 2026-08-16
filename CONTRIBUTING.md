# Contributing

Bastion is a solo hackathon submission, but the repository treats every change as an auditable
production change.

## Before changing code

Read [architecture](docs/ARCHITECTURE.md), [ADRs](docs/adr/README.md),
[security](SECURITY.md), and the [submission proof ledger](submission/SUBMISSION.md). Amend an ADR
in the same change when implementation reverses a recorded decision.

## Python 3.12 setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
gcloud auth application-default login
```

`GOOGLE_CLOUD_LOCATION=global` is the Gemini endpoint; `GCP_REGION=europe-north2` is workload
placement. Do not merge them.

## Quality gates

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

CI also runs dependency audit and secret scanning. Coverage remains 100% for statements and
branches. Add unit, integration, security, or load coverage at the boundary you change.

## Safety and evidence

- Never commit or print credentials, raw IAM/Asset output, principals, private endpoints, full
  environments, prompts/responses, or unredacted findings.
- Keep tool declarations fixed and repository-owned.
- Preserve the production route through managed Runtime, Gateway/IAP, and Registry; the Eventarc
  dispatcher must not gain a direct worker credential.
- Label a capability implemented, deployed, observed, or configured precisely.
- Regenerate `gcp-state.json` only from live GCP and keep it count-only.
- Edit architecture and 16:9 SVG masters, then regenerate variants/GIFs. Do not hand-edit generated
  variants.

## Commits and releases

Commit subjects describe what became true. Do not rewrite existing history, amend another
contributor's commit, or move a tag without explicit instruction. Update `CHANGELOG.md` and every
affected documentation/evidence claim in the same change. A release tag is optional and separate
from an ordinary push to `main`.
