# Changelog

All notable changes to this project are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versioning per
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

An entry describes **what became true**, not which files moved. Historical sections preserve the
state known on their date; current proof and limitations are recorded together.

The current release process is in
[`submission/planning/07-release-plan.md`](submission/planning/07-release-plan.md).

## [0.2.1] — 2026-08-22

A patch release with one defect and one capture. 0.2.0 fixed session state failing to cross the
A2A boundary in one direction; this fixes the other direction, which turned out to be the reason a
human-approved exception had never once been honoured in production.

### Fixed — a policy decision now survives the escalation hop

- An approved exception was scored as `suppress` and escalated anyway. Nothing was wrong with the
  policy: `apply_policy_rules_with_memory` marked it and `route_by_department` excluded it. Both
  results were discarded one hop later.
- `PolicyStep` yielded an event carrying only `state_delta`, and ADK builds the outgoing A2A
  message from `event.content.parts` — so a state-only event contributes nothing to it, and the
  most recent content the Escalation Agent saw was still the Auditor's report. The routing now
  travels as event content as well as state: state is what the gate reads in-process, content is
  the only thing that crosses.
- Sending the routing was necessary but not sufficient. `route_by_department` returned counts and
  reasons but **no finding ids**, so the Escalation Agent had to take ids from the raw report even
  when it read the routing. Each bucket now carries its own `finding_ids` — the only
  decision-filtered list of ids in the system. A finding without an id is counted and no id is
  invented for it, because a fabricated id matches no finding and can key no exception.
- **This is a class, not an incident.** 0.2.0 fixed the Auditor's report failing to reach the
  policy step; this fixes the policy step's decision failing to reach escalation. Same root cause,
  opposite direction, and any future step that assumes session state crosses A2A will fail the
  same way — silently, and only in the deployed topology.

### Observed — the track's cross-week obligation, with a real elapsed gap

- [Evidence 10](assets/evidence/10-cross-week-suppression.md): an exception approved **2026-08-19**
  suppressed its matching finding on **2026-08-22**, through the deployed Runtime and both
  workers. `notify_human` fired **once**; the department owning the suppressed finding received no
  notification at all rather than an empty one.
- The immediately preceding runs that day delivered the same finding to that department while the
  same exception was already live. That is the before-and-after this fix is measured by.
- This was the one open claim whose critical path was elapsed time rather than effort, and the
  repository deliberately did not claim it until now. The gap is three days, not a calendar week,
  and the write-up says so. Expiry firing has not elapsed and remains covered by tests only.

### Changed — the suite is 251 tests

- Up from 247, at 100% statement and branch coverage. The new tests pin both halves of the defect:
  that the routing leaves `policy_step` as content, and that a suppressed finding is absent from
  what crosses to escalation.

## [0.2.0] — 2026-08-22

The fleet was deployed at 0.1.0 and then watched. This release is what watching produced: seven
defects that no offline gate could have found, four new decision records, and a screening outage
whose cause was the fleet's own dispatch message. Two defects remain open; they are named here
rather than left for a reader to discover.

### Observed — one investigation, end to end, under a single correlation id

- 2026-08-22 16:49Z, against the live project: **34 audit records sharing one `investigation_id`**,
  spanning the managed Runtime and both Cloud Run workers. `investigation.run started` →
  Auditor (two model calls, `audit_iam_policy`, completion) → **`policy_step` ran and completed** →
  **`policy_gate` ran and completed** → Escalation Agent → `notify_human` **twice, to two
  departments** → `investigation.run completed`. No refusal, no error, no truncation.
- This is the first trail in the project's history that can be assembled across the A2A boundary,
  and it retires D6. D1's fix is observed rather than only tested: the deterministic step and its
  gate both executed inside the deployed Runtime.
- `python -m infrastructure.smoke_test` passes end to end — fleet, findings IAM and idempotency,
  durable async state, and Runtime.
- Not claimed: a refusal has not been captured on this route, so capture 4 in the observation
  backlog remains open. A trail of successes proves nothing about the guardrails.

### Fixed — the production smoke test exercises the path production actually uses

- `verify_runtime` let its client become a temporary. `Client(...).agent_engines.get(...)` leaves
  the client unreferenced, so garbage collection could close its aiohttp session mid-stream and
  surface as `assert self._connector is not None` deep inside aiohttp — an error naming nothing
  about ownership, which reads like a fleet fault during a release gate. `agent_server` had
  already learned this; the smoke path never had the lesson applied.
- It also sent an imperative sentence, which is the shape the dispatcher stopped sending because
  Model Armor scores an instruction addressed to an agent like a real injection. A smoke test
  that sends what production is forbidden to send is exercising a path no deployment uses. It now
  sends the same structured payload and run-config metadata as dispatch.
- Not unit-tested, and deliberately so: `infrastructure/smoke_test.py` requires `gcloud` at import
  and is outside the coverage source, so a test for it would be skipped on CI rather than run. It
  is verified by the gate itself passing.

### Fixed — the Auditor's report reaches the policy step over A2A

- Found by deploying, not by testing, and it is the defect this release exists to catch.
  `output_key` writes into the session of the agent that *declares* it. In-process that is the
  Orchestrator's own session, so `audit_findings` was simply there — for every local run, every
  integration test, and every CI job. Over A2A it is the **worker's** session, which never crosses
  back, so the deployed Orchestrator read an empty key.
- Observed 2026-08-22 on the live fleet: the Auditor produced a complete sub-trail — two model
  calls, `audit_iam_policy`, a clean completion — and `policy_step` then refused with *"the Access
  Auditor returned no structured report; refusing to score nothing"*. No test could have reached
  this, because the state key is populated in exactly the topology tests run in.
- This is the true cause of D6, and it reframes D1. The old model-driven policy step read the same
  empty key and escalated anyway, which is why humans were paged about findings no threshold had
  scored: the model was not merely retyping findings, it was inventing them from nothing. The
  deterministic step turned a silent fabrication into a visible refusal, which is precisely what
  [ADR-010](docs/adr/010-policy-enforcement-gate.md) promised it would do.
- `policy_step` now falls back to the Auditor's A2A reply when the state key is absent. Reading
  that reply is sound rather than a workaround **because** of `output_schema`: the content is
  validated `AuditReport` JSON, not prose to be interpreted. A reply that fails to parse is
  skipped rather than guessed at, and skipping everything still fails closed.

### Fixed — one investigation can be assembled into one trail

- ADK mints a fresh `invocation_id` per agent run, and a worker reached over A2A is a separate run
  in a separate process, so a single investigation scattered its audit records across three
  unrelated ids. The audit docstring claimed `invocation_id` grouped an investigation; it groups
  one agent run, and only inside that run.
- The durable event id is seeded into `RunConfig.custom_metadata` at dispatch and forwarded to each
  worker as A2A request metadata, so every record carries the same `investigation_id`. Metadata
  rather than message content: the id must reach the far side without becoming something a model
  reads, restates, or can be talked into changing.
- `event_id` is the correlation key rather than `context_id` because `InvestigationEvent` validates
  it as a UUID while `context_id` is only checked non-empty. The value crosses A2A from a peer and
  lands in a 365-day retained bucket, so an unvalidated field would be a channel for arbitrary text
  into the compliance log. The audit boundary re-validates the shape regardless of what upstream
  sent, and records `unknown` rather than writing through.

### Fixed — the deterministic threshold cannot be skipped, and findings are not retyped

- On 2026-08-21 two investigations escalated to humans with no threshold ever applied, and the
  lifecycle recorded `completed` with no error anywhere. Enforcement did not fail closed; it
  disappeared. `policy_step` was an `LlmAgent` whose deterministic tools a model chose to call, so
  a Model Armor refusal of that model call meant the tools never ran and the sequence continued.
- Even when the call succeeded the model was **retyping** the findings — reconstructing opaque ids,
  categories and scores from the Auditor's prose. A fabricated category is why `notify_human` failed
  intermittently; a mistyped 24-hex id is why an approved exception would never have matched.
- `policy_step` is now a `BaseAgent` calling the threshold and the routing catalog directly. There
  was never a decision here for a model to make. Because it reaches no model it declares no tools
  and needs no screening. [ADR-010](docs/adr/010-policy-enforcement-gate.md).
- The Auditor answers in a validated `AuditReport` schema, so findings cross A2A as data rather than
  prose, and a missing or misshapen report fails closed instead of scoring an empty list.
  [ADR-012](docs/adr/012-structured-findings-across-a2a.md). Whether the deployed Gemini call
  honours `output_schema` is enforced at the model layer and is **not** proven by the offline suite.
- `PolicyEnforcementGate` refuses to escalate unless the deterministic path left its own result in
  state. An `output_key` is not proof: ADK stores a screening refusal under that key too.

### Fixed — inbound screening covers tool results, not only the prompt

- `before_model_callback` read only text parts, so everything a tool returned reached the model
  unscreened, leaving the shorter and likelier path as the one neither callback looked at.
- Not theoretical: `apply_policy_rules` returns `exception_policy_version`, an operator-supplied
  string the findings API writes and the policy step hands straight to a model — free text crossing
  a trust boundary inside exactly the part type the screen skipped.
  [ADR-011](docs/adr/011-inbound-screening-covers-tool-results.md).

### Fixed — a declared-but-empty environment variable is treated as absent

- `os.environ.get(key, default)` returns an empty string for a key that is present and empty, so
  `BASTION_INVESTIGATION_LEASE_SECONDS` reached `int("")` and durable ingress died on its first
  delivery — at request time rather than startup, so the service reported healthy and failed only
  under traffic.
- The suite had the same defect from the other side via `os.environ.setdefault`: nine tests failed
  for contributors who export their environment, while CI — which exports nothing — stayed green. A
  gate that only passes on machines with an empty environment is not verifying what it appears to.

### Fixed — the Runtime screens and egresses under its own identity

- Agent-to-Anywhere refused every Runtime call as incorrect or unregistered. Three separate causes
  wore one error message.
- The managed Runtime does not run as `orchestrator-sa`; it runs as a GEAP Agent Identity
  principal, so granting the workload account `roles/modelarmor.user` changed nothing and the
  policy step reported `screening_unavailable` on every investigation. Deployment now grants the
  Agent Identity directly. The `orchestrator-sa` grant is reverted — durable ingress constructs no
  agent, so it calls no model — along with the test that required it, since an over-grant enforced
  by a gate is harder to remove than one nobody checks.
- `roles/iap.egressor` carries the permission the denial names, and nobody held it. Registering a
  destination is necessary but not sufficient. The catalog was also genuinely incomplete: Google API
  clients resolve to mTLS hosts when a client certificate is available, and each is a distinct
  endpoint. Both the role and the endpoints are applied by deployment and required by
  `verify_fleet`.
- Refusals inside the notification boundary all raised one `SensitiveDataError`, so the trail said
  only that something was rejected. `UnsafeRiskCategoryError` and `OpaqueFindingIdError` make the
  exception type the bounded reason, keeping events payload-free while making them answerable.

### Fixed — the dispatcher sends data, not an instruction

- Model Armor scored the dispatcher's own repository-owned sentence at HIGH confidence — the same
  as a genuine injection probe — and since screening fails closed it refused **every investigation
  the fleet had ever run**.
- Neither threshold separated them. To a prompt-injection classifier an imperative addressed to an
  agent is what an injection is; the difference is provenance, which content classification cannot
  see. `HIGH` was tried and reverted: it fixed nothing and detected less.
  [ADR-009](docs/adr/009-model-armor-threshold.md) records that the threshold is not the lever.
- The message is now a JSON object carrying the correlation id, with a test pinning the shape so the
  outage cannot return as a well-meaning rewording. Instructing the model to use only registered
  agents was never something it could honour or ignore — Registry and IAP authorize egress
  deterministically — so asking for it in prose bought nothing and cost the entire pipeline.

### Changed — the Model Armor template is configuration, not console state

- The deployed template enforced prompt-injection detection at `LOW_AND_ABOVE`, which matched the
  fleet's own prompts. Investigations completed in forty seconds having done nothing. A control
  that blocks all legitimate traffic supplies an outage, not security.
- The threshold was measured against the live template rather than guessed, and the configuration
  now lives in `model_armor/template.py` so the posture is diffable and restorable. `verify_fleet`
  fails when the deployed template drifts, including when it is merely unreadable — equally fatal
  under fail-closed screening.
- Refusals carry screened character and part counts. Sizes are not values: a length may travel where
  a principal may not, which keeps this inside the payload-free rule. A digest used during diagnosis
  was removed once it had served, because a fingerprint of a prompt is still derived from a prompt.

### Fixed — approval cannot be granted by an agent that can reach the endpoint

- `caller_identity` accepted any principal with a verifiable ID token carrying an email claim, and
  every worker identity that posts a review record necessarily holds `run.invoker` on the findings
  API. The Escalation Agent could approve the suppression of a finding it had just raised.
  Confirmed against the deployed service.
- ADR-008 had named `gcloud run services proxy` as the reviewer's path, and that path cannot work:
  Cloud Run accepts only a Google-signed ID token whose audience is the service, and no user
  credential can mint one. The record stated the constraint and then contradicted it.
- Approval now checks one deployment-configured approver identity and fails closed when unset. The
  human reaches it through a break-glass identity holding no project role and exactly one
  capability, which only the configured principal may impersonate — so the human stays named in the
  IAM audit log.
- Firestore's default database is literally named `(default)`; sourced unquoted into a POSIX shell
  that is array-assignment syntax yielding a different database name, with no error at any layer.

### Changed — the local permission grant is ignored by the repository

- `.claude/settings.local.json` authorizes an agent to deploy against the live project. It was
  untracked only because a personal `~/.config/git/ignore` rule matched it — a rule absent on CI, in
  a fresh clone, and on every other checkout. The protection held precisely where it was least
  needed.

### Known — two defects remain open

- **Model Armor egress from inside the Runtime is denied by IAP.** Five hypotheses were eliminated:
  global Registry registration, GRPC to HTTP_JSON rebinding, a Runtime redeploy, Registry
  `bindings`, and IAM. The Agent Identity holds `roles/iap.egressor` at project level and there are
  no IAP grants in the denial window. The deterministic policy step no longer depends on this path,
  so it is not blocking, but it is not solved.
- **Investigations truncating after the Auditor (D6) is closed** — fixed and observed
  completing end to end on 2026-08-22. Its cause is recorded above.
- Both are tracked in
  [09-capture-backlog.md](submission/planning/09-capture-backlog.md) alongside the observation
  backlog. Nothing in this release claims either is fixed.

### Changed — dependency pins raised for the tag

- `google-adk` 2.7.0 → **2.7.1** and `google-cloud-aiplatform` 1.164.0 → **1.165.1**, with
  `requirements.lock` regenerated. `scripts/check_versions.py --check-upstream` is the documented
  pre-tag gate and it failed on both; a tag is a claim that the pinned stack is current, so the
  pins move before the tag rather than after it.
- ADR-005's installation claim was **re-run** against 2.7.1 rather than re-dated. A verification
  line edited to match a new pin has stopped being a verification.
- No behavioural change surfaced: 247 tests at 100% statement and branch coverage, mypy, and every
  documentation gate pass identically on 2.7.1. `SequentialAgent` remains deprecated-but-required
  in 2.7.1, so ADR-005's migration trigger — `Workflow` becoming usable as an `LlmAgent` sub-agent
  — has still not fired.

### Changed — the suite is 247 tests

- Up from 208, at 100% statement and branch coverage under Python 3.12. Every new boundary added in
  this release carries tests at the layer it changed.

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
