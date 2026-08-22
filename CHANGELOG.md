# Changelog

All notable changes to this project are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versioning per
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

An entry describes **what became true**, not which files moved. Historical sections preserve the
state known on their date; current proof and limitations are recorded together.

The current release process is in
[`submission/planning/07-release-plan.md`](submission/planning/07-release-plan.md).

## [Unreleased]

### Changed — the reviewer grant is applied by deployment

- `deploy.sh` applies `roles/run.invoker` on the findings API from `BASTION_APPROVER_PRINCIPAL`,
  and warns when it is unset. `gcloud run deploy` re-establishes the service IAM policy, so a
  grant made by hand does not survive the next deploy — and the only path that can create an
  exception would stop working with nothing reporting it.
- ADR-008 records how a human reaches an IAM-private service: `gcloud run services proxy`. A user
  credential cannot mint an audience-scoped identity token, and impersonating a service account
  would replace the human in the ledger with the identity the record exists to distinguish them
  from.

### Added — the secret scan covers principal inventories, not only credentials

- The scan now fails on any real service-account principal in a tracked file outside `tests/`,
  which carry `bastion-ci-mock` identities deliberately, and `.gitignore` excludes captured
  console output.
- The shape this covers: `gcloud ... add-iam-policy-binding` prints the resulting policy, so a
  redirected operator session is a principal inventory in an ordinary `.txt` — matched by none of
  the credential-filename, embedded-JSON, API-key or private-key rules.

### Added — the track's first obligation is now measured, not asserted

- Captured [evidence 09](assets/evidence/09-cross-department-routing.md): 52 live IAM bindings
  produced 3 overly-broad findings that routed to **2 different owning departments**,
  deterministically. Cross-department routing existed and was tested; nothing recorded that
  production data actually exercises it, which is the difference between a `department` column
  and cross-department support.

### Changed — sovereignty is stated as minimisation, not residency

- The README led with the disclaimer that Gemini runs on `global` and therefore claims no EU
  residency. True, but the weaker half of the argument: raw members, roles, resources and
  bindings never reach the model at all, so there is no prompt from which a principal could be
  recovered. Residency keeps regulated data in a region; this keeps it out of the model entirely.
  The disclosure stays — it is now the second point rather than the first.

### Added — "scalable network" is answered explicitly

- The track asks for a scalable network; the fleet is fixed at three agents by ADR-002, which a
  judge should not have to reconcile alone. The README now states the actual scaling axes —
  owning departments, catalogued agents, and bounded throughput — with evidence 09 as the
  measured proof that the first is real. `BASTION_MAX_INSTANCES=3` is named as a budget ceiling
  following the organizers' cost guidance, not an architectural limit.

### Changed — departments are repository-owned by decision, not by default

- `registry/departments.py` records why the catalog stays in static source: Agent Registry
  catalogs *agents*, and a routing table any registered agent could write to would let a
  compromised one redirect its own findings away from the team that owns them. `load_catalog()`
  remains the single seam if that reasoning ever changes.

### Changed — `.env.example` is the complete environment contract

- Every variable the code and deployment scripts read is declared, grouped by purpose: what is
  required with no default, the three region planes and why conflating them breaks, the managed
  governance surfaces, deployment shape, and which variables hold secret *ids* rather than secret
  values. A clean clone can configure the fleet from this file alone.
- `tests/unit/test_environment_contract.py` parses the code and the deployment scripts and fails
  on drift in either direction — a variable the code reads that the example omits, or one the
  example declares that nothing reads — and fails if a secret value is ever committed there.

### Added — the exception ledger has a production writer, and it is a human

- `POST /v1/exceptions` to the private findings API: the only path that creates an
  exception. The reviewer comes from the **verified caller ID token**, never the request body —
  a self-asserted reviewer field is an attestation the caller forges about itself. Expiry is
  capped at 90 days so a silent suppression cannot outlive its reasoning unnoticed.
- `notify_human` now carries opaque `finding_ids`. The signature is still the control: it is
  handed identifiers and counts, never bindings, and a fabricated id is inert because it can only
  key an exception no real finding will match.
- Recorded the decision in [ADR-008](docs/adr/008-human-approval-loop.md), and the boundary in
  SECURITY.md and DATA_GOVERNANCE.md. Approval is deliberately not an agent tool; the tool-surface
  security suite fails if any agent ever declares one.

### Changed — google-auth is pinned as the direct dependency it is

- `gateway/cloud_run_auth.py` mints Cloud Run ID tokens and the approval endpoint verifies them,
  both importing `google.auth`/`google.oauth2` by name, so the package is pinned directly rather
  than inherited from `google-cloud-firestore`'s constraint. Pinned at the version the lock
  already resolved, so install behaviour is unchanged.

### Changed — the test-count gate requires the claim to exist

- It asserts that at least one document states the suite total before comparing, so a claim that
  was removed cannot read as a claim that was met.

### Added — the tool-declaration boundary is now asserted, not only documented

- Added `tests/security/test_tool_surface.py`, the enforcement behind ADR-007's tool-declaration
  boundary. It asserts each agent's tool set by equality at construction, that the Escalation Agent
  holds neither a policy-reading tool nor an Asset client (differentially against the Auditor,
  which must still hold one), and that every tool description is repository-owned static source.
- Captured [evidence 08](assets/evidence/08-tool-poisoning.md), including confirmation that the
  assertions **fail** when the escalation agent is mutated in memory to hold `audit_iam_policy`.
  A guardrail test that has never been seen to fail is not evidence that the guardrail holds.

### Changed — the documented test total is verified, not asserted

- The suite total — the number that changes most often and is quoted in six documents — is now
  verified alongside the pillar, ADR, agent, badge, and diagram counts.
- The assertion lives in `tests/unit/test_documented_test_count.py` rather than in
  `check_docs.py`, because CI's docs and diagrams jobs run that script on a bare interpreter with
  no dependencies installed — there is no pytest there to collect with, and making those jobs
  install the full tree to count tests would trade a fast standalone gate for a slow one. Inside
  the suite the collected count is already known. It skips on a partial run, so narrowing to one
  directory does not fire it. Released CHANGELOG sections are exempt: they record what was true
  at their tag.

### Added — the observation backlog is tracked in the repository

- Added [09-capture-backlog.md](submission/planning/09-capture-backlog.md), which tracks what is
  deployed and tested but not yet observed. What remains before submission is observation, not
  construction, and that distinction is now a tracked document rather than an assumption.
- Records that the cross-week continuity seed targets the Firestore `bastion_exceptions`
  collection. Memory Bank backs managed session memory, so seeding it would produce a capture
  that proves nothing about suppression.
- Records that rate limiting is not implemented, with the three ways forward and the reason the
  choice precedes the capture attempt.

### Changed — release runs are named after the release

- The Release workflow names each run after the release ref rather than the tagged commit's full
  message, which for an annotated tag is several paragraphs.

## [0.1.0] — 2026-08-16

First tagged release. The production path is deployed and verified; the remaining work before
submission is observation and publication, not construction. What is deployed but **not yet
captured as an observed artifact** is recorded in
[`submission/SUBMISSION.md`](submission/SUBMISSION.md) rather than claimed here.

### Added — governed managed Runtime path

- Deployed the Orchestrator to Python 3.12 managed Agent Runtime with Agent Identity and
  Agent-to-Anywhere Gateway binding; catalogued it beside two institutionally described A2A
  worker cards and approved platform destinations.
- Reduced Cloud Run Orchestrator to durable Eventarc admission and Runtime dispatch. Deployment
  now reconciles away its peer secret, direct worker invoker grants, and obsolete Model Armor and
  Pub/Sub roles, leaving no production local-graph bypass.
- Added Firestore leases/reclaim, failure/retry semantics, five-attempt dead-letter delivery,
  idempotent findings, private findings IAM, full payload-free AuditPlugin lifecycle, fail-closed
  Model Armor, and deterministic protected-data screening.
- Added Windows 11 bootstrap, live fleet verification/smoke, safe rollback, dry-run-first teardown,
  count-only state capture, and idempotent observability provisioning.
- Provisioned a 365-day regional audit bucket and sink, four log metrics, five alert policies, and
  the Bastion Fleet Operations dashboard. The bucket remains unlocked; immutability is not claimed.
- Standardized Docker, Runtime, GitHub Actions, release workflow, commands, and documentation on
  Python 3.12.
- Expanded the suite to 161 tests with 100% statement and branch coverage across populated unit,
  integration, security, and load suites.
- Reconciled every Markdown claim and architecture/banner label with the 2026-08-16 measured live
  state: 21/21 APIs and 33 deployed resources.

### Changed — visual system

- Preserved the corrected architecture arrows/status dots and refreshed generated theme variants
  and GIFs from their reviewed masters.
- Updated banner and architecture facts for managed Runtime, Memory, Gateway, Registry, and the
  current count-only deployment measurement.

### Changed — documentation matches the deployed fleet

- The rubric self-assessment in [`submission/DEVPOST.md`](submission/DEVPOST.md) records managed
  retry as implemented and deployed, with the timeout → retry → escalate sequence marked as not
  yet captured rather than upgraded to observed.
- The `Makefile` exposes `verify`, `smoke`, `rollback`, and `teardown` against the real
  operator entry points, and `install` is interpreter-relative so one target serves the Windows
  authoring machine and Linux CI.
- The decision index dates ADR-003 as verified against the deployed fleet on 2026-08-16.

## Pre-deployment baseline — 2026-08-15

The first untagged baseline, before the managed deployment recorded above. Retained as
chronology; the current state is the sections above it.

### Added — the fleet, before it was deployed

- Three ADK agents under one `SequentialAgent`: a read-only Access Auditor over live Cloud
  Asset Inventory, deterministic policy enforcement inside the Orchestrator, and an Escalation
  Agent holding no policy-reading capability.
- Deterministic detection and scoring ahead of every model call, so a finding is produced by
  code and only explained by Gemini. Keyed opaque finding identifiers, allowlisted risk
  categories, and department routing derived from the principal string rather than a model
  judgement.
- A2A as the inter-agent contract: typed tasks carrying `task_id` and `context_id`, an explicit
  lifecycle, and agent cards. A policy refusal is recorded as its own outcome rather than as a
  failure, and a retry keeps its task id so one retried task does not read as three.
- A payload-free audit record per transition, written independently of tracing, because a trace
  is sampled and expires while a compliance record is neither.
- Durable runtime semantics: an inbox and leases, attempt counting, deduplication, terminal
  state, and separation of permanent failure from transient failure so a malformed message is
  not redelivered forever.
- Cloud Run deployment with one service account per workload, explicit regions with no default,
  bounded instance counts, and Secret Manager for the keyed identifier and origin credential.

### Added — judge-facing artifacts

- Level 1 and Level 2 architecture diagrams as hand-authored 1920×1080 SVG masters with light
  and dark variants and animated GIFs, each stating its own build state, with a documentation
  gate that fails the build when a diagram and the measured state disagree.
- A count-only live measurement of the project, generated rather than typed, excluding the
  service accounts Google creates for every project so the number answers what Bastion deployed.
- Thirteen decision records, each tracing to a quoted line in the captured brief, later
  consolidated to seven.

### Added — engineering gates

- Unit, integration, security, and load suites at 100% statement and branch coverage.
- `mypy --strict` with `warn_unreachable` and `disallow_any_generics`, Ruff lint and formatting,
  a transitive dependency lock with a vulnerability audit, and a secret scan.
- Clients constructed on first use rather than at import, so importing a module never attempts
  credential discovery and a missing setting explains itself.
- `httpx` with explicit connect and read budgets and transport-level retries that do not replay
  an already-sent request, since retrying a delivered notification pages a human twice.

### Verified — 2026-08-13

- `gemini-3.5-flash` answering through Vertex AI on the project.
- Application Default Credentials authenticating locally.
- The local quality gate passing end to end.
