# Contributing

Bastion is a solo hackathon submission, but the repository treats every change as an auditable
production change.

## Before changing code

Read [architecture](docs/ARCHITECTURE.md), [ADRs](docs/adr/README.md),
[security](SECURITY.md), and the [submission proof ledger](archive/hackathon-2026/submission/SUBMISSION.md). Amend an ADR
in the same change when implementation reverses a recorded decision.

## Python 3.12 setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt -c requirements.lock
Copy-Item .env.example .env
gcloud auth application-default login
```

`py -3.12` resolves only a CPython registered with the Windows launcher. If `py -0p` does not list
3.12, call that interpreter by its own path, or use `python3.12 -m venv .venv` on macOS and Linux —
see [10-reproducibility.md](archive/hackathon-2026/submission/planning/10-reproducibility.md).

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
python scripts/redact_evidence.py --check
npx markdownlint-cli2 "**/*.md"
```

CI also runs dependency audit and secret scanning. Coverage remains 100% for statements and
branches in the configured core scope from `pyproject.toml`. Add unit, integration, security, or
load coverage at the boundary you change.

One class in that scope, `FirestoreDurableStore` (`runtime/firestore.py`), carries a blanket
`# pragma: no cover`: its transactional logic needs a real Firestore transaction coordinator, and
a mocked client would test the mock, not the adapter. It is exercised instead through real
production behavior — `infrastructure.smoke_test`'s durable-async-event check and every live
investigation the deployed fleet runs, which drive `receive`/`claim`/`finish`/`enqueue`/
`approved_exception` against the actual service. That is why the 100% figure is stated as
"configured core," not "100% of the codebase": the pragma is a scoping decision made once and
documented here, not new production logic excluded to keep the number after the fact.

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
