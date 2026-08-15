# Audit remediation plan

**Baseline date:** 2026-08-15  
**Objective:** turn the truthful local prototype into a demonstrably secure, durable,
enterprise agent fleet for the Fortified Enterprise Fleet track.

This is the execution contract produced by the repository-wide audit. A checkbox closes only
when its exit evidence exists; code or configuration alone is not sufficient.

## Order of work

### 0. Commit-zero hygiene and truthful baseline

- [x] Exclude local workflow state, raw notes, credentials, IAM dumps, caches, and coverage output.
- [x] Remove account, organization, project-number, and full-principal identifiers from public files.
- [x] Replace unsupported or stale CI, Makefile, diagram, and ADK environment-variable commands.
- [x] Reconcile README, architecture, security, identity, and submission claims with observed state.
- [x] Pass Ruff, format, mypy, 73 unit tests at 100% coverage, Markdown, docs, versions, and diagrams.
- [ ] Create one untagged initial commit after explicit approval; do not create a release tag.

**Exit evidence:** clean initial-commit inventory, all local gates green, remote still empty until
approval.

### 1. P0 — deterministic safety boundary

- [ ] Replace the missing-risk fail-open path with a typed, fail-closed investigation decision.
- [ ] Validate model-produced tool arguments against deterministic policy and bounded schemas.
- [ ] Minimize IAM data before any model boundary; do not send raw members or bindings globally.
- [ ] Screen structured model input and output, not only text prompt parts.
- [ ] Sanitize and schema-check escalation output before the notification boundary.
- [ ] Register `AuditPlugin` on every runner and correlate refusal, failure, model, tool, and agent
      records by investigation ID without payload values.
- [ ] Make notification side effects idempotent and refuse delivery without an idempotency key.

**Exit evidence:** populated security tests for fail-closed decisions, prompt injection, outbound
PII, unsafe tool arguments, audit refusals/failures, and duplicate notification delivery.

### 2. P0 — durable asynchronous investigations and memory

- [ ] Define a versioned investigation event with event ID, tenant/department scope, attempt,
      deadline, trace context, and data-classification fields.
- [ ] Implement an acknowledged consumer with persisted state transitions, retry policy, dead-letter
      handling, deduplication, and an outbox for side effects.
- [ ] Store only minimized durable context and approved exceptions with provenance, expiry, reviewer,
      and policy version.
- [ ] Demonstrate a prior-week approved exception being recalled and suppressed in a later run.
- [ ] Prove safe resume after process loss without duplicate escalation or lost audit records.

**Exit evidence:** integration test across restart, duplicate event, partial failure, retry, and a
captured cross-week Memory Bank demonstration.

### 3. P0 — cataloged, zero-trust remote fleet

- [ ] Publish each agent card and its owner, department, purpose, skills, data classification,
      version, health, and policy metadata in Agent Registry.
- [ ] Replace direct peer URLs and in-process fallback in production mode with authenticated,
      registry-resolved routing through Agent Gateway.
- [ ] Enforce caller, target, declared skill, tenant/department, and payload policy at the Gateway.
- [ ] Bind one least-privilege service account to each deployed agent with no key files.
- [ ] Prove both allowed and denied cross-agent calls and record both decisions in the audit trail.

**Exit evidence:** Registry catalog screenshots/API capture, Gateway admission/refusal records,
per-agent runtime identities, and no production bypass route.

### 4. P0 — reproducible deployment

- [ ] Replace the current folder-only `adk deploy cloud_run` flow with build contexts that include
      shared packages and pinned runtime dependencies.
- [ ] Keep `GOOGLE_CLOUD_LOCATION=global` separate from the regional compute/state target.
- [ ] Inject project, Model Armor, Registry, Gateway, peer-card, and findings configuration through
      managed deployment configuration; keep secrets in Secret Manager.
- [ ] Provision dependencies before agents, deploy workers before the Orchestrator, and fail if any
      required endpoint or identity is absent.
- [ ] Add infrastructure as code, least-privilege IAM, authenticated ingress, bounded scaling,
      teardown, and a new-project bootstrap path.
- [ ] Run a post-deploy smoke test from schedule/event through audit and human escalation.

**Exit evidence:** clean-project deployment log, authenticated service inventory, smoke-test trace,
and a documented rollback/teardown rehearsal.

### 5. P1 — production verification and failure tolerance

- [ ] Populate integration, security, and load suites; their current `__init__.py` files are not tests.
- [ ] Test real wiring with emulated or isolated dependencies, not only mocked unit boundaries.
- [ ] Exercise worker timeout, malformed response, hallucinated argument, dependency outage, retry,
      dead letter, duplicate event, stale memory, Gateway refusal, and notification failure.
- [ ] Define measurable latency, throughput, error-rate, retry, and audit-completeness objectives.
- [ ] Resolve or consciously accept deprecated `SequentialAgent` and experimental remote A2A use.
- [ ] Add a transitive, reproducible dependency lock and supply-chain scanning.

**Exit evidence:** green four-layer suite, failure-injection report, load report, locked dependency
graph, and recorded risk acceptance for any experimental component.

### 6. P1 — sovereignty, compliance, and observability proof

- [ ] Document the data-flow inventory, lawful/authorized purpose, retention, deletion, residency,
      access control, and processor boundaries for each payload field.
- [ ] State plainly that Gemini's global endpoint is not regional residency and prove minimization
      before that boundary.
- [ ] Export correlated traces, logs, metrics, policy decisions, and immutable audit records with
      defined retention and redaction.
- [ ] Add alerts and dashboards for stuck investigations, refusal spikes, audit gaps, retry storms,
      Model Armor failures, and budget anomalies.

**Exit evidence:** field-level data-flow table, redacted end-to-end trace, audit completeness check,
retention configuration, and operational dashboard.

### 7. P2 — submission-grade product and evidence

- [ ] Complete the read-only findings UI, scheduled trigger, Recommender corroboration, history view,
      and hosted judge path only where they strengthen the scored story.
- [ ] Capture all fourteen evidence artifacts with sensitive fields redacted before recording.
- [ ] Record an under-four-minute story: catalog → durable memory → live production data → enforced
      refusal → correlated audit trail.
- [ ] Re-run the official rules matrix, deployment smoke test, security suite, and public-repository
      secret scan immediately before the release candidate.
- [ ] Create annotated release tags only after the matching changelog claim and evidence exist.

**Exit evidence:** public hosted path, final video, architecture image, complete Devpost fields,
release-candidate gate, and a judge-readable evidence index.

## Non-negotiable release blockers

No release tag or Devpost-ready claim while any of these remains true:

- production can bypass Agent Gateway or resolve an unregistered peer directly;
- a missing risk value clears a finding;
- raw principal/binding data or unsanitized summaries cross a model or notification boundary;
- asynchronous work has no durable ID, deduplication, retry/dead-letter, or idempotent side effect;
- `AuditPlugin` is unregistered or refusal/failure records cannot be correlated;
- the deployment cannot be reproduced from a clean project;
- integration, security, or load suites are empty;
- documentation describes a target control as deployed or observed.
