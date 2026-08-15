.PHONY: help install test test-unit test-integration test-security test-load test-fast \
        coverage lint format format-check typecheck markdown docs versions diagrams ci \
        run-orchestrator iam-policy deploy teardown clean

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
	@echo "teardown          - delete the Cloud Run services after the demo is recorded"

install:
	$(PYTHON) -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt

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
	mypy agents registry model_armor observability

ci: lint format-check typecheck coverage markdown docs versions diagrams

docs:
	$(PYTHON) scripts/check_docs.py

versions:
	$(PYTHON) scripts/check_versions.py

diagrams:
	$(PYTHON) scripts/render_diagrams.py --check --no-gif

markdown:
	npx --yes markdownlint-cli2 "**/*.md"

run-orchestrator:
	@echo "Use runtime.runner.build_runner() so AuditPlugin is registered; CLI wiring is pending durable runtime setup."
	@exit 1

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
# endpoint), not for the day after recording.
teardown:
	@echo "TODO: add infrastructure/teardown.sh. Emergency use only - see submission/planning/03-build-plan.md."
	@exit 1

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache .ruff_cache .mypy_cache

