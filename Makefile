.PHONY: help install test test-unit test-integration test-security test-load test-fast \
        coverage lint format format-check typecheck markdown docs versions diagrams ci \
        run-orchestrator iam-policy deploy verify smoke rollback teardown \
        audit-dependencies clean

PYTHON ?= python
PROJECT ?= $(GCP_PROJECT_ID)

help:
	@echo "install           - create .venv and install requirements"
	@echo "test              - run pytest"
	@echo "lint              - ruff check"
	@echo "format-check      - verify ruff formatting"
	@echo "typecheck         - mypy the shipped Python packages"
	@echo "ci                - run the local quality gate"
	@echo "run-orchestrator  - run the Orchestrator locally"
	@echo "iam-policy        - dump the live IAM policy (gitignored; redact before publishing)"
	@echo "deploy            - deploy every service to Cloud Run"
	@echo "verify            - fail unless the deployed fleet is private, regional, catalogued"
	@echo "smoke             - production smoke: Runtime, findings IAM/idempotency, async state"
	@echo "rollback          - dry-run-first rollback of the deployed revisions"
	@echo "teardown          - emergency only; dry-run-first, preserves compliance state"

# Invokes the venv interpreter rather than a POSIX-only bin/pip path, so the same target works
# on the Windows authoring machine and on Linux CI.
install:
	$(PYTHON) -m venv .venv
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

test:
	pytest -q

test-unit:
	pytest tests/unit -q

test-integration:
	pytest tests/integration -q

test-security:
	pytest tests/security -q

test-load:
	pytest tests/load -q

test-fast:
	pytest -q -m "not load"

coverage:
	pytest --cov --cov-report=xml --cov-report=term-missing --cov-fail-under=100

lint:
	ruff check .

format:
	ruff format .

format-check:
	ruff format --check .

typecheck:
	mypy agents gateway identity registry runtime model_armor observability infrastructure

audit-dependencies:
	uv pip install --system -r requirements.lock
	uvx pip-audit -r requirements.lock

ci: lint format-check typecheck coverage markdown docs versions diagrams audit-dependencies

docs:
	$(PYTHON) scripts/check_docs.py

versions:
	$(PYTHON) scripts/check_versions.py

diagrams:
	$(PYTHON) scripts/render_diagrams.py --check --no-gif

markdown:
	npx --yes markdownlint-cli2 "**/*.md"

# The production Orchestrator runs on managed Agent Runtime, not locally: the Cloud Run service
# is durable Eventarc admission only. Local graph construction would be a second production path.
run-orchestrator:
	@echo "The Orchestrator runs on managed Agent Runtime. Use 'make smoke' against the deployed"
	@echo "fleet, or runtime.runner.build_runner() in a test so AuditPlugin stays registered."
	@exit 1

verify:
	$(PYTHON) -m infrastructure.verify_fleet

smoke:
	$(PYTHON) -m infrastructure.smoke_test

# Dry-run first. Never broadens targets or deletes Firestore, secrets, or audit state.
rollback:
	$(PYTHON) -m infrastructure.rollback

# Raw output is gitignored: it carries real principals and real email addresses.
# Redact deliberately before anything derived from it lands in assets/evidence/.
iam-policy:
	gcloud projects get-iam-policy $(PROJECT) --format=json > $(PROJECT).iam-policy.json
	@echo "Wrote $(PROJECT).iam-policy.json (gitignored)."

deploy:
	bash infrastructure/deploy.sh

# NOT part of the normal plan: the services stay up through the Sept 1 - Oct 1 judging
# window, because a hosted URL is an encouraged submission field and idle scale-to-zero
# services cost nothing. This target exists for an emergency (runaway spend, a compromised
# endpoint), not for the day after recording. It is dry-run-first and preserves Firestore,
# secrets, and audit state.
teardown:
	$(PYTHON) -m infrastructure.teardown

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache .ruff_cache .mypy_cache

