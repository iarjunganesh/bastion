# Changelog

All notable changes to this project are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versioning per
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

An entry describes **what became true**, not which files moved. A capability appears here only
once it has been observed working — see the "Verified" and "Not yet true" sections, which are
part of the record rather than a disclaimer appended to it.

The release ladder from `v0.1.0` to `v1.0.0`, with target dates and what each version is
allowed to claim, is in [`submission/planning/07-release-plan.md`](submission/planning/07-release-plan.md).

## [Unreleased]

Pre-`v0.1.0`. The initial untagged repository commits are published on `main`; no release tag
exists because the managed deployment evidence is not yet earned.

### Added — reproducible fleet controls

- A complete Cloud Run image context, private A2A ID-token transport, registry publication
  script, deployment verifier, Firestore/Pub/Sub bootstrap, and an explicit non-memory runtime
  requirement.
- Durable replay, security, and concurrent gateway-policy tests; a transitive `uv` lock and
  known-vulnerability audit gate.
- Field-level data governance and release operations objectives that distinguish configured
  controls from deployment evidence still owed.

### Added — architecture diagrams that state their own build state

Levels 1 and 2 are hand-authored SVG masters at **1920×1080**, so a frame drops into a 16:9
demo scene without letterboxing, and `brand/banner-16x9.svg` is the matching title card. Level
3 stays an inline mermaid fence: a state machine has no layout decisions to get wrong.

- **`scripts/render_diagrams.py`** — emits `-light` and `-dark` variants from one master, plus
  an **animated GIF** of each. Two files rather than one `prefers-color-scheme` block because an
  SVG loaded through an `<img>` tag does **not** inherit the page's colour scheme, so the media
  query resolves against the browser default and a light-mode reader gets the dark palette.
  Measured in a headless browser, not assumed. CI checks the variants with `--no-gif`;
  rasterising needs a browser and ffmpeg the runner does not have, so the SVG is the checked
  artifact.
- **The raster is a GIF because Devpost does not accept SVG.** It takes JPG, PNG and GIF, so a
  still PNG would have discarded the animation at the one surface that cannot recover it.
  Gallery images cap at 5 MB and `check_docs.py` now fails above it; all six render at about
  0.5 MB at full 1920×1080.
- **Two pipeline assumptions were wrong and are recorded rather than quietly fixed.**
  Chromium's `--virtual-time-budget` does not advance SMIL — four renders at different budgets
  came back byte-identical, so an earlier comment claiming it stepped the animation was false
  and every frame was time zero. And batching fifteen frames into one tall page, seven times
  faster, is unsound: two cells at the *same* animation time differed in 7% of their pixels,
  which destroyed inter-frame compression and took the banner from 0.5 MB to 6.5 MB — over
  Devpost's cap. One launch per frame is byte-identical across runs, so that is what ships.
- **Both diagrams animate the full investigation, not half of it.** The request travels out to
  the live policy, and then findings fan out to the three owning departments — the
  cross-department claim, which was previously drawn but never moved. Dots only travel edges
  that already carry an arrow and a label, so a reader who suppresses animation still loses
  nothing. Every SMIL duration divides the 6s loop exactly, or the GIF visibly jumps at its
  loop point.
- **Every committed SVG discloses its build state in its own text**, and `check_docs.py` fails
  the build if one does not. The previous gate accepted a caption and lifted entirely once
  `sum(resources)` passed one — which made a *count* the only thing between the repository and
  a fictional diagram. A caption is separable from the picture; a screenshot is not.
- **A raster is allowed only beside the SVG it was rendered from.** Its text is pixels, so
  it cannot carry a disclosure a gate can read.

### Fixed — code that disagreed with a merged ADR

- **The Escalation Agent posted to Slack.** It read `SLACK_WEBHOOK_URL` and sent a single
  `text` blob, while [ADR-003](docs/adr/003-pillars-on-geap.md) had already settled the
  escalation surface as the read-only findings API behind the dashboard, and three planning
  documents state that Slack is not among the twenty services. Code contradicting a merged
  decision is the one thing CLAUDE.md says may never sit silently, so the code moved to the
  decision: `BASTION_FINDINGS_ENDPOINT`, and a **typed body** carrying `finding_count` rather
  than a sentence — a free-text field is where principal identifiers end up. `.env.example`,
  the unit tests and the Secret Manager badges moved with it.
- **`identity/identity_config.md` listed five service accounts, two for services that no
  longer exist.** Gateway and Registry each had one because each used to be a Cloud Run service
  here; ADR-003 replaced both with managed products on 2026-08-15. The file already recorded
  the same failure once — a Policy Enforcer row that outlived ADR-002 — so the table is now
  stated to derive from what `deploy.sh` deploys, and nothing else. It also now says plainly
  that the three agents currently share **one** identity, because they run as `sub_agents` of a
  single `SequentialAgent`.

### Documented — a deprecation that is not going to be actioned yet

`SequentialAgent` is deprecated in ADK 2.7.0 *"in favor of Workflow"*, and the warning names
its own blocker in the next sentence: *"Workflow cannot yet be used as an LlmAgent sub-agent."*
That is exactly Bastion's arrangement, so the deprecated class is the only construct that
expresses the design. Recorded in [ADR-005](docs/adr/005-adk-as-the-agent-framework.md) with an
explicit migration trigger rather than suppressed with a `filterwarnings` entry, which would
have hidden the one signal that says when to move.

### Fixed — the measurement that would have permitted a fictional diagram

`capture_gcp_state.py` counted the service accounts **Google creates for a project**, so an
empty project reported two deployed resources — one row above the threshold at which the image
gate stopped objecting. The measurement built to prevent an overclaim was one default account
from producing one.

- Google-created default service accounts are excluded; the count answers "what has Bastion
  deployed", so it counts what Bastion deployed.
- **Model Armor templates are probed over REST**, because `gcloud model-armor templates list`
  returns `PERMISSION_DENIED` for an account holding `roles/owner` while the identical REST GET
  succeeds. Trusting the CLI reported the project's one real resource as absent.
- Agent Gateway, Agent Registry and Agent Identity joined the service list — **20 services, not
  seventeen** — and gateways and registered agents are now probed.

### Fixed — claims that outran the code

- **`infrastructure/deploy.sh` deployed two services that no longer exist.** It called
  `gcloud run deploy --source` against `gateway/` and `registry/`, both deleted on 2026-08-15.
  Rewritten on `adk deploy cloud_run`, where four pillars are flags rather than code. It also
  now says plainly that running it today stands up three services running overlapping agents,
  because the three agents are still `sub_agents` of one `SequentialAgent`.
- **`roles/iam.securityReviewer` was described as the Access Auditor's scope.** The project's
  policy contains ten distinct roles and that is not among them; the captured investigation
  read the live policy under the author's own credentials. The restraint is real but enforced
  by the code holding no policy client, which is weaker than IAM — and is now described as
  weaker, in `README.md` and `docs/ARCHITECTURE.md`.
- **PII screening was listed as an outbound control.** No `after_model_callback` exists. The
  row now says so.
- **`mypy` failed on seven errors** — ADK does not re-export `LlmRequest`, `LlmResponse`,
  `BaseTool` or `ToolContext` from its package roots — so the typecheck job would have failed
  on the first push. Imports moved to the defining submodules.
- **CI required `assets/architecture/architecture.mmd`**, a file that does not exist, so the
  documentation job would have failed on the first push.
- `docs/ARCHITECTURE.md`'s pillar sections still described the deleted DIY implementation — a
  Firestore `/registry/{agent_id}` schema, a hand-rolled gateway with a rate limiter, Cloud Run
  services triggered by Pub/Sub. Rewritten against the managed products and the ADK seams, with
  a build-state marker on every heading.

### Added — inter-agent contract and audit trail

#### A2A as the inter-agent contract, and an audit trail that records refusals

The Gateway took an untyped `{caller, target, payload}` body. That shape cannot support the
thing the track actually asks for — *"audit their reasoning"* — because it has no task
identity, so a retry is indistinguishable from a duplicate; no context identity, so hops
cannot be assembled into a chain; and no state, so there is nothing to audit transitions of.
[ADR-005](docs/adr/005-adk-as-the-agent-framework.md).

- **the A2A envelope module (removed 2026-08-15)** — a typed task with `task_id`, `context_id`, an explicit lifecycle, and
  agent cards. Transport-free by construction, so the contract survives a move to Agent Engine
  or ADK's own `a2a` transport. Identifiers are validated at the boundary: a newline in a task
  id is log forging against the trail that is supposed to prove what happened.
- **`REJECTED` is not a kind of `FAILED`.** A policy refusal is the guardrail working, and
  collapsing the two makes every guardrail decision invisible in the one place it most needs
  to be visible.
- **A retry keeps its `task_id`.** A timeout is exactly the case where the first attempt may
  have succeeded unseen; a fresh id would turn one retried task into three tasks in the trail.
- **the audit module (removed 2026-08-15)** — the half of the Telemetry pillar that is not the trace. One
  record per transition, written at the Gateway, never derived from traces: a trace is sampled
  and expires, a compliance record is neither. `propagate = False` so a caller's logging config
  cannot decide what a compliance record looks like. Payloads are stripped in one function
  rather than by a habit at each call site.
- **The Registry became a routing input rather than a table.** Cards carry department, skills
  and scopes; the Gateway refuses a skill the target never declared; `/cards` is the routing
  view and `/agents?department=` the cross-department one. Writes are allowlisted, because the
  Registry is a supply chain for the Gateway's decisions.
- **The Runtime now separates "will never work" from "might work next time."** Pub/Sub retries
  anything non-2xx, so a malformed message answered with a 500 is a poison pill redelivered
  forever at the one layer whose job is to keep running.
- Tests went 104 → **201**, still at 100% line and branch coverage.

#### Fixed — the rate limiter was itself a memory-exhaustion path

A refused call still reached the limiter and still appended its timestamp, so a single caller
hammering past the limit grew its own window without bound inside one window. The dict-key
eviction closed only the *other* half of the same problem. Refused calls are no longer
recorded, which also gives plain sliding-window semantics rather than a penalty box the
attacker's own traffic keeps extending. A load test asserts the bound.

### Corrected

#### The decision record traces to the requirement

All thirteen ADRs are traceable to a quoted line in
[`submission/DEVPOST.md`](submission/DEVPOST.md) — the capture of the hackathon's own pages.
The capture was accurate all along; nothing downstream cited it, so the ADRs described an
architecture idea rather than a response to a brief.

- **ADR-003 decided on its due date**, inside its half-day cap, and its premise turned out to
  be wrong. GEAP versus DIY was never a fork: ADK ships `BaseSessionService` and
  `BaseMemoryService`, and `VertexAiMemoryBankService` imports cleanly, so the managed service
  and the Firestore implementation are two backends behind one interface. That framing is why
  all three pillars had sat half-built — neither branch was worth finishing while the other
  might win. The Registry stays DIY because `agent_engines` offers publish, list, and delete
  but no versioning, ownership, or scope, which is three of the words in the brief's definition.
- **Seven records for seven requirements that would otherwise have none:** ADK as the agent
  framework (007), where Gemini sits in the loop (008), one observable proof per pillar (009),
  the cross-department and multi-week obligations (010), tool poisoning as a threat distinct
  from injection (011), the submission artifacts as build constraints (012), and A2A with its
  audit trail (013).
- **ADR-003 gained a measured state column.** It previously listed seventeen jobs and read as a
  description of a running system. Enabled, wired, and deployed are three different things.

#### Documentation reconciled against the brief

A sweep of every markdown file against the captured requirement. What it found:

- **Two pass/fail requirements asserted as met while unmet in code.** `README.md` carried
  *"Agent framework | Google ADK | Orchestrates the three agents"* plus an ADK badge, and
  `00-judging-matrix.md` claimed *"All agents call Gemini 3.5 Flash through Vertex AI"* — with
  no `google.adk` import and no model call anywhere. In a repository whose stated rule is *do
  not write a claim before it is verified*, these were the most serious defects present.
- **Two files contradicting the capture.** `00-judging-matrix.md` and `06-project-review.md`
  both declared the overview/rules-page conflict resolved; `DEVPOST.md` recorded that it was
  not, on the same day. Corrected to match the capture, with the rule written down: where a
  planning file and the capture disagree, the capture wins.
- **"Six required pillars" above a seven-row table**, propagated from `01-architecture.md`'s
  header into `04-why-we-win.md`. The brief names seven.
- **A resolved decision still open in prose.** ADR-003's GEAP cap read as pending work in four
  files; "dashboard OR Slack, pick one" survived in three after ADR-003 fixed a service surface
  that contains no Slack.
- **Contradictory teardown guidance.** `01-architecture.md` said tear down after recording while
  three other documents said stay up through judging. Staying up is correct and now says why the
  organizers' tip is deliberately not followed.
- **The demo storyboard had no shot for the IAM denial** — the project's strongest card and the
  direct answer to the rules page's *"strictly enforced separation of concerns"*. Added, with a
  note that the denial is safe to film because it returns an error rather than a policy.
- **`get-iam-policy` shown as a command to run unredirected** in three files, against this
  repository's own rule. Rewritten to redirect to a gitignored file or ask for roles only.
- **A cadence justified by naming two unrelated repositories** in `07-release-plan.md`. Nothing
  here should reference a project a judge cannot open.
- `CLAUDE.md` gained a **staleness sweep** listing each rot shape above, since every one of them
  actually occurred rather than being hypothetical.

### Added

#### Cloud environment, live and verified (2026-08-13)

- GCP project `bastion-fleet-2026` configured for the `europe-north2` regional target.
- Free-trial and hackathon credits were confirmed on the intended account on Aug 13, 2026;
  billing identifiers, balances, and expiry details are intentionally omitted from the public
  repository.
- **One billing account and one project, deliberately.** Empty scaffolds were deleted and an
  unused second billing account was closed. A governance product
  whose own cloud footprint contains unaccounted-for accounts argues against itself.
- Budget of kr500 with alerts at 50/90/100%, configured to **exclude credits** so it measures
  gross usage. Google's default (`INCLUDE_ALL_CREDITS`) would have measured post-credit spend,
  which stays at zero while the trial covers everything — an alert that never fires.
- **All seventeen services from [ADR-003](docs/adr/003-pillars-on-geap.md) enabled and
  verified on the project**: Vertex AI, Cloud Run, Firestore, Pub/Sub, Cloud Scheduler,
  Recommender, Cloud Asset Inventory, IAM, Model Armor, Secret Manager, Cloud Trace, Logging,
  Monitoring, BigQuery, Firebase Hosting, Cloud Build, Artifact Registry. Looker Studio needs
  no API — it reads BigQuery. Enabling an API costs nothing; it is not a claim that the service
  is wired in, and none of them is yet.
- **The Model Armor API is enabled**, which is the precondition for the managed path rather
  than evidence it works. [ADR-003](docs/adr/003-pillars-on-geap.md) stays open and the
  security test still asserts `NotImplementedError` until a block is observed.

#### Repository governance

- `LICENSE` (MIT), `CONTRIBUTING.md`, `SECURITY.md`, `Makefile`, and a `.gitignore` written for
  a project that handles real IAM dumps and service-account credentials.
- `.markdownlint.json` and a clean lint baseline: 664 markdown findings resolved to zero across
  24 files, and ruff resolved to zero across the Python scaffold.

#### Judge-facing documentation

- `docs/ARCHITECTURE.md` — the system, separated from the numbered planning notes.
- `docs/adr/` — thirteen decision records, indexed with verification status.
- `submission/SUBMISSION.md` — the Devpost checklist, unchecked, with an explicit list of
  claims that may not be made before they are verified.
- `assets/README.md` — a fourteen-shot evidence plan, written before the evidence exists.

#### Test suite — 100% coverage, four layers

- **201 tests, 100% line and branch coverage** of every agent and pillar module, with the CI
  and Codecov floors both set to 100. A floor below real coverage is a decoration rather than
  a gate.
- `tests/unit/` — per-module behaviour, including that a malformed IAM binding does not raise
  (a policy read that crashes the auditor is a governance system that silently stops governing).
- `tests/integration/` — the loop wired together with only Google APIs mocked: open state,
  read the policy, flag the broad grants, suppress what a human already approved, escalate the
  rest. One test asserts the central claim directly — the fleet flags **its own**
  over-permissioned service account.
- `tests/security/` — one test per property asserted in `SECURITY.md`, including a static check
  that no agent imports another agent directly (which would bypass the Gateway), and a check
  that the Escalation Agent posts a count rather than the bindings behind it.
- `tests/load/` — the Gateway under 500 sequential and 16-way concurrent callers: the rate
  limit holds exactly, stays per-caller rather than degrading into a global limit, and the
  call log stays coherent under contention.
- `tests/conftest.py` patches the import-time clients at conftest import time rather than in a
  fixture, because pytest imports test modules during collection before fixtures run.

#### Continuous integration

- `.github/workflows/ci.yml` — six parallel jobs: ruff lint and format, mypy, pytest with a
  coverage ratchet and Codecov upload, documentation hygiene, a credential scanner, and a
  diagram-freshness check.
- **A credential gate that fails the build.** Bastion audits IAM for a living; a committed
  service-account key or raw policy dump would discredit the submission more thoroughly than
  any missing feature. The job scans tracked files for key filenames, `"type":
  "service_account"` payloads, API keys, and PEM private keys.
- **`scripts/check_docs.py`** — every counted claim in the repository ("seven pillars",
  "three agents") is verified against the directories that exist, every ADR file is checked
  against the index and the README, and `.env.example` is checked for the `global` model
  location that ADR-004 exists to protect.
- **A grounding gate on the architecture documentation.** A committed diagram once showed
  Firestore, Cloud Run services, Pub/Sub topics, BigQuery and a Model Armor template while the
  project held exactly one resource. `check_docs.py` now fails if any image is committed to
  `assets/architecture/` while fewer than two resources are deployed, if `gcp-state.json` is
  missing, or if `docs/ARCHITECTURE.md` stops citing it — and a CI step fails if the state file
  ever contains a principal. The gate was watched failing on an injected file before it was
  trusted.
- `.github/workflows/release.yml` — tag-triggered: full quality gate, a check that
  `CHANGELOG.md` has a section for the version being tagged, then a GitHub release whose body
  is extracted from that section.
- `codecov.yml` with informational gates while the pillars are scaffolding.

#### Brand and diagrams

- `assets/brand/` — logo and light/dark banners as SVG.
- `assets/architecture/gcp-state.json` — the **measured** build state of the live project,
  written by `scripts/capture_gcp_state.py`, recording counts only and never a principal. The
  architecture diagrams derive their per-box status from it, so the documentation cannot claim
  a service that is not there.

#### Failure tolerance — the claim the docs were making without code behind it

- **Orchestrator resilience** (removed 2026-08-15; Agent Engine owns it) — retry with exponential backoff and full jitter, a
  per-target circuit breaker (closed → open → half-open, one probe), and a loop guard for a
  worker that never converges. The rules page grades this track on *"is the inter-agent
  routing logic failure-tolerant"*, and until now the Orchestrator's docstring claimed to own
  retry and escalation while containing only TODOs.
- **The Orchestrator dispatches asynchronously** and records an outcome per agent rather than
  raising: an investigation that dies because a sub-agent died is a gap in a compliance
  record, where a recorded failure is an audit trail. Exhausted retries and open circuits are
  reported as distinct outcomes, because "the breaker refused this" and "every attempt was
  used" are different operational facts.
- A **non-retryable error surfaces immediately**. Retrying the Escalation Agent's `403` would
  turn a captured denial into a delayed identical denial.
- Time, randomness and the transport are injected, so the 27 new tests are deterministic and
  none of them sleeps.

#### Python hardening

- **Clients are built on first use, not at import.** `firestore.Client()` in the Memory Bank
  and Registry, the Cloud Trace exporter, and `os.environ["GCP_PROJECT_ID"]` in the Access
  Auditor all ran at import time, so importing a module attempted credential discovery and a
  missing setting raised `KeyError` from an import line. They are now cached factories, and a
  missing project id explains itself in a sentence.
- **`requests` replaced by `httpx`** — explicit connect/read timeout budgets and
  transport-level retries that deliberately do not replay an already-sent request, since
  retrying a delivered notification pages a human twice for one finding.
- **mypy runs in `strict` mode** with `warn_unreachable` and `disallow_any_generics`. It found
  eight bare `dict` generics; those are now `Finding`, `AgentOutcome`, `InboundScreen` and
  `OutboundScreen` TypedDicts. One third-party untyped call carries a narrow inline ignore
  rather than a repository-wide relaxation.
- **A memory-exhaustion path in the Gateway closed.** The per-caller rate limiter kept one
  dictionary key per `agent_id` forever, and `agent_id` is supplied by the caller — an
  unregistered caller cycling identifiers would grow the process until Cloud Run killed it.
  The rate limiter was itself the denial-of-service vector.

#### Deployment correctness

- **`infrastructure/deploy.sh` had four defects, each contradicting a graded claim.**
  `GCP_REGION` defaulted to `us-central1` while the project runs in `europe-north2`, so a
  missing variable would have silently deployed every service to the United States and
  falsified the EU residency position; it now has no default. The Registry, Gateway and
  Orchestrator all shared one service account, contradicting the Agent Identity pillar's
  least-privilege claim; there are now five. `min-instances`/`max-instances` were absent. And
  it deployed a `bastion-policy-enforcer` service for the agent ADR-002 merged away.
- `identity/identity_config.md` still scoped the Access Auditor to a custom role on an
  `entitlements` collection — a leftover from the mock-data design ADR-001 rejected — and
  listed a Policy Enforcer service account. Rewritten around `roles/iam.securityReviewer`.

### Changed

- **The Pro tier is gone.** Probing established that `gemini-3.5-pro` is unavailable to this
  project on `global`, `us-central1`, `europe-west4`, and `us-east5`. The escalate-or-clear
  step now runs on `gemini-3.5-flash` like every other call ([ADR-004](docs/adr/004-flash-only-global-endpoint.md)).
- **Gemini 3.5 is served only from `locations/global`.** No regional endpoint exists. Model
  location and infrastructure region are now separate settings in `.env.example`, because
  collapsing them returns a 404 that reads like a permissions failure.
- **The services will not be torn down after recording.** A full read of the rules found a
  Hosted Project URL described as *"highly encouraged"* and a judging window running
  Sept 1 – Oct 1. An idle `min-instances=0` service bills nothing, so teardown forfeited a
  submission field to save nothing. `make teardown` is now documented as an emergency control.
- **The GCP surface expanded from ten services to seventeen**, each with a stated job and a
  pre-agreed cut order ([ADR-003](docs/adr/003-pillars-on-geap.md)). The additions that
  matter: Recommender API grounds "this role is too broad" in Google's own signal rather than
  the model's opinion, and Cloud Scheduler makes "continuous rather than quarterly" literally
  true instead of asserted.
- **Firebase Hosting was selected as the target public judge path**, but it is not deployed.
- `submission/planning/00-judging-matrix.md` — the open question about the rules page contradicting the
  overview is resolved; the two now agree.
- **Every dependency pinned to its latest release**, verified against PyPI on 2026-08-13, and
  the toolchain moved to **Python 3.14** across `pyproject.toml`, both workflows, and the
  documentation. Exact pins rather than ranges: a submission judged in October has to install
  the same tree the demo was recorded against.
- Ruff's rule set widened to `E, F, I, UP, B, SIM, ANN201, S`, which surfaced twelve real
  findings in the scaffold — including a `requests.post` with no timeout on the escalation
  path, where a hung notification surface would have blocked escalation indefinitely, and a
  `subprocess` call resolving `gcloud` from `PATH` rather than an absolute path.

### Fixed

- Documents describing four agents and a standalone Policy Enforcer, contradicting
  [ADR-002](docs/adr/002-three-agents.md). The demo storyboard had the merged agent performing
  the memory-recall beat in two separate shots.
- `README.md` announced "six required pillars" above a seven-row table.
- **The Gateway returned a 500 for a malformed request.** A missing `caller`, `target`, or
  `payload` raised `KeyError` into a generic server error, which reads as a gateway fault
  rather than a bad request. It now refuses with a 400 naming the missing field — the gateway
  is the boundary, so a caller that sent nonsense should be told so, and nothing half-formed
  should reach an agent. Found by the test written for it.
- **The Registry 500s if a document is deleted between the query and the read.** `to_dict()`
  returns `None` in that race, and `None | dict` raises. A registry that fails mid-race is a
  fleet that cannot discover itself. Found by mypy, not at runtime.
- `from google.cloud import firestore` does not type-check — `google.cloud` is a namespace
  package, so the attribute form fails under mypy even though it runs. Switched to the module
  import form in all three call sites.

### Verified

- `gemini-3.5-flash` answers through Vertex AI on this project — the first capability with
  evidence behind it.
- Application Default Credentials authenticate locally.
- `make ci` equivalent passes: ruff clean, one placeholder test passing, markdown lint clean.

### Not yet true

Stated here because omitting it would be the failure this project is about. Nothing is
deployed: no Cloud Run service, no Firestore database, no Pub/Sub topic, no scheduled trigger,
no dashboard. No agent has read a real IAM policy. Model Armor has blocked nothing. No evidence
has been captured. The pillars exist as scaffolding, not as working services.
