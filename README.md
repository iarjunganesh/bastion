# Bastion

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/brand/banner-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/brand/banner-light.svg">
    <img width="900" src="assets/brand/banner-light.svg"
         alt="Bastion — the access review that reviews itself. A key turns in a shield-mounted padlock, the shackle lifts, and an audit sweep passes over the shield before it closes again. All Things Agentic Hackathon 2026."/>
  </picture>
</p>

<p align="center">
  <strong>A private, durable access-review fleet: three ADK agents, separate Cloud Run identities, authenticated A2A, an Eventarc inbox, and a count-only human-review endpoint.</strong>
</p>

> **All Things Agentic Hackathon 2026 — Fortified Enterprise Fleet**
>
> **Live private fleet; evidence capture in progress.** Four Cloud Run services, the Eventarc
> investigation route, managed Agent Engine state, Model Armor, and the EU Firestore/Pub/Sub
> boundary are deployed. The [proof ledger](#build--deployment-status) separates deployment
> from the remaining end-to-end and scheduled-run evidence.

[![CI](https://github.com/iarjunganesh/bastion/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/iarjunganesh/bastion/actions/workflows/ci.yml)
[![Codecov](https://codecov.io/gh/iarjunganesh/bastion/graph/badge.svg)](https://codecov.io/gh/iarjunganesh/bastion)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Gemini Enterprise Agent Ready](https://img.shields.io/badge/GEAR-Gemini_Enterprise_Agent_Ready-4285F4?logo=google&logoColor=white)](https://developers.google.com/profile/badges/community/gear?u=iarjunganesh)

**Target Google Cloud service map — deployment status is tracked below.**

<!-- Row 2 — Google Cloud, in the order one investigation uses them (1/2) -->
[![Cloud Scheduler](https://img.shields.io/badge/1_Cloud_Scheduler-fires_the_review-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/scheduler)
[![Pub/Sub](https://img.shields.io/badge/2_Pub%2FSub-opens_the_investigation-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/pubsub)
[![Cloud Run](https://img.shields.io/badge/3_Cloud_Run-runs_the_agents-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/run)
[![Cloud IAM](https://img.shields.io/badge/4_Cloud_IAM-one_SA_per_agent-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/iam)
[![Asset Inventory](https://img.shields.io/badge/5_Asset_Inventory-reads_the_policy-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/asset-inventory/docs/overview)
[![IAM Recommender](https://img.shields.io/badge/6_IAM_Recommender-corroborates_findings-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/iam/docs/recommender-overview)
[![Model Armor](https://img.shields.io/badge/7_Model_Armor-screens_the_prompt-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/security-command-center/docs/model-armor-overview)
[![Vertex AI](https://img.shields.io/badge/8_Vertex_AI-gemini_3.5_flash-4285F4?logo=googlegemini&logoColor=white)](https://cloud.google.com/vertex-ai)

<!-- Row 3 — Google Cloud, in the order one investigation uses them (2/2) -->
[![Firestore](https://img.shields.io/badge/9_Firestore-findings_and_exceptions-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/firestore)
[![Secret Manager](https://img.shields.io/badge/10_Secret_Manager-findings_endpoint-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/secret-manager)
[![Cloud Trace](https://img.shields.io/badge/11_Cloud_Trace-the_reasoning_chain-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/trace)
[![Cloud Logging](https://img.shields.io/badge/12_Cloud_Logging-structured_logs-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/logging)
[![Cloud Monitoring](https://img.shields.io/badge/13_Cloud_Monitoring-budget_alerts-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/monitoring)
[![BigQuery](https://img.shields.io/badge/14_BigQuery-findings_over_time-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/bigquery)
[![Looker Studio](https://img.shields.io/badge/15_Looker_Studio-the_trend_view-4285F4?logo=googlecloud&logoColor=white)](https://lookerstudio.google.com/)
[![Cloud Build](https://img.shields.io/badge/16_Cloud_Build-source_deploys-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/build)
[![Firebase Hosting](https://img.shields.io/badge/17_Firebase_Hosting-the_judge_path-4285F4?logo=googlecloud&logoColor=white)](https://firebase.google.com/docs/hosting)

<!-- Row 4 — Backend -->
[![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Google ADK](https://img.shields.io/badge/Google_ADK-2.7.0-4285F4?logo=google&logoColor=white)](https://google.github.io/adk-docs/)
[![A2A SDK](https://img.shields.io/badge/a2a--sdk-1.1.2-34A853?logo=google&logoColor=white)](https://github.com/a2aproject/A2A)
[![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-1.42.1-425CC7?logo=opentelemetry&logoColor=white)](https://opentelemetry.io/)
[![Ruff](https://img.shields.io/badge/Ruff-lint%20%2B%20format-D7FF64?logo=ruff&logoColor=111827)](https://docs.astral.sh/ruff/)
[![Mypy](https://img.shields.io/badge/Mypy-type_checked-2A6DB2?logo=python&logoColor=white)](https://mypy-lang.org/)
[![pytest](https://img.shields.io/badge/pytest-9.1.1-0A9EDC?logo=pytest&logoColor=white)](https://docs.pytest.org/)

---

## The Problem

Access review is still a spreadsheet job. Once a quarter someone exports who-can-touch-what
across a dozen systems, cross-references it by hand, chases owners for approvals, and files the
result. It takes days, it is stale the moment it is finished, and the permissions it misses stay
open until the next quarter comes around.

The failure is not that nobody knows how to review access. It is that reviewing access is
continuous work being done on a quarterly schedule by a person who has other things to do.

> **A stale permission is not caught when it is granted. It is caught when someone finally
> gets around to looking.**

What makes this hard to automate *honestly* is memory. The reviewer has to remember what was
already decided. An agent that re-raises a finding a human closed three weeks ago is worse than
the spreadsheet it replaced, because now the alert fatigue is automated too.

---

## What is deployed, what is proven

- ✅ **Reads production IAM read-only** through Cloud Asset Inventory; deterministic policy rules
  decide clear, reject, or escalate before a model can influence the outcome.
- ✅ **Separates authority** with three Cloud Run services, one workload identity per agent, and
  authenticated internal A2A calls. The Escalation Agent can invoke only Bastion's private,
  count-only findings endpoint.
- ✅ **Maintains durable investigation identity**: Eventarc admission atomically deduplicates a
  CloudEvent in Firestore and maps its stable context ID to managed Agent Engine session/memory.
- ✅ **Protects the model and delivery boundaries**: Model Armor fails closed before model input;
  a deterministic protected-data screen blocks model output before it can reach state or the
  human-review inbox. Audit events are emitted through ADK's Cloud telemetry integration.
- ◐ **End-to-end proof is being captured**: the Eventarc route and private peer cards are deployed;
  a retained production trace, duplicate-delivery capture, and cross-week replay are the remaining
  evidence, not unimplemented capabilities.
- ⬜ **Cloud Scheduler cadence** and a human-review UI are intentionally not part of the current
  deployment; investigations can be triggered by the authenticated Pub/Sub publisher today.

### The audit target is real IAM

This is the decision the whole project rests on ([ADR-001](docs/adr/001-real-iam-not-mock-data.md)).

Bastion audits the IAM policy of the GCP project it is deployed into. Not invented entitlement
rows across fictional SaaS tools.

That policy contains the service accounts Bastion's own agents run under. **The system audits
its own permissions** — so when the Access Auditor reports that the Escalation Agent holds a
broader role than its job needs, that is a real finding about a real system, produced live
rather than staged.

A small seeded overlay is permitted to guarantee one specific finding appears on camera. Any
use of it is disclosed here and in the recording. The primary source is real.

---

## How It Works

**This is the deployed topology.** The services are private; the only admitted asynchronous
entry point is Eventarc from the Bastion investigation topic. The proof ledger below calls out
which live paths still need retained demo evidence.

1. **Cloud Scheduler** fires the review on a cadence. Nothing waits on a human remembering.
2. **Pub/Sub** opens an investigation. The trigger is external to the fleet, so a run outlives
   the session that started it.
3. The **Orchestrator** (an ADK agent on Cloud Run) looks the fleet up in the **Agent Registry**,
   writes investigation state, and dispatches work. It owns the retry and escalation policy, so
   a failing agent is never the thing deciding what to do about the failure.
4. The **Access Auditor** reads the **live IAM policy** through Cloud Asset Inventory —
   read-only, under `roles/iam.securityReviewer` — and returns findings with the bindings they
   came from. Detection is deterministic: explicit rules, not a model guess.
5. Each finding can be corroborated against the **IAM Recommender**; this optional enrichment is
   deliberately separate from deterministic detection.
6. The durable Eventarc boundary stores and deduplicates the event, then reuses its stable context
   ID as the managed Agent Engine session/memory identity.
7. The Orchestrator's **policy rules** decide clear-or-escalate, and **Gemini 3.5 Flash** writes
   the human-readable rationale — it explains the finding rather than making it.
8. The **Escalation Agent** packages only validated counts, category, and an allowlisted summary
   for the private findings inbox. Its service account has **no IAM read permission at all**.
9. Every model call is screened by **Model Armor** before and after the model. Tool poisoning is
   contained by fixed, repository-owned tool declarations and IAM. Every peer call has a
   Cloud Run audience-bound identity token; ADK emits Cloud telemetry for the investigation.

---

## Architecture

One investigation, end to end. `●` ran and was captured, `◐` API enabled and nothing wired,
`○` not started — and those markers are not typed by hand, they come from
[`gcp-state.json`](assets/architecture/gcp-state.json).

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/architecture/level-1-context-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/architecture/level-1-context-light.svg">
    <img width="1000" src="assets/architecture/level-1-context-light.svg"
         alt="Cloud Scheduler opens a review; the Bastion fleet of three ADK agents reads the live GCP IAM policy read-only through Cloud Asset Inventory, asks Gemini 3.5 Flash for rationale only, and escalates to the department that owns each principal. A dotted return edge shows the policy contains the service accounts Bastion runs under. Nothing is deployed."/>
  </picture>
</p>

Three edges carry the argument. The **thick one is real** — the Access Auditor reads a live IAM
policy through Cloud Asset Inventory, no fixture, and the two findings it returned are in
[evidence 02](assets/evidence/02-gemini-investigation.md). The **dotted red one going back** is
the whole idea: the policy Bastion reads contains the service accounts Bastion runs under. And
the escalation fans out to **the departments that own the principals**, not to one central
inbox — two findings, two different teams, in the same run.

Gemini is asked for rationale, never for detection, and never sees the raw policy. The
prompt-injection block that keeps a ticket from talking the fleet into an approval is a
separate control at `before_model_callback`, captured in
[evidence 01](assets/evidence/01-model-armor-block.md) and drawn in the container-level diagram
in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

**Nothing above is deployed.** It ran locally against live Google APIs.

> **A note on the diagrams.** An earlier version of this README showed a rendered architecture
> image containing Firestore, Cloud Run services, Pub/Sub topics and a Model Armor template on
> a day when the project contained exactly one resource. It was deleted rather than corrected.
> Every committed diagram now states its build state **inside the image**, where a screenshot
> or a Devpost paste cannot separate the picture from the disclaimer, and
> [`scripts/check_docs.py`](scripts/check_docs.py) fails the build if one does not. In a
> repository arguing that its claims are checkable, the diagram is a claim.

### The three agents

Policy enforcement is a function of the Orchestrator, not a fourth agent
([ADR-002](docs/adr/002-three-agents.md)). The scope column is IAM, not documentation.

| Agent | Responsibility | Scope, enforced by its own service account | Folder |
|---|---|---|---|
| **Orchestrator** | Triggers investigations, routes work, applies policy rules, owns retry and escalation | Read the registry; write investigation state | [`agents/orchestrator/`](agents/orchestrator/) |
| **Access Auditor** | Reads the live IAM policy, flags anomalies | Read-only on IAM (`roles/iam.securityReviewer`) | [`agents/access_auditor/`](agents/access_auditor/) |
| **Escalation Agent** | Packages high-risk findings for a human | Write-only to the notification surface; **no IAM read access** | [`agents/escalation_agent/`](agents/escalation_agent/) |

**That scope column is the design, and neither binding exists yet.** Nothing is deployed, so
there is no agent service account to bind a role to — the captured investigation read the live
policy under the author's own credentials. The restraint is real but it is enforced by the code
holding no policy client, which is weaker than IAM enforcing it, and is described as weaker in
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md#least-privilege-stated-just-as-honestly).

### The seven pillars, in the brief's four groups

The status column is the honest one. A folder existing is not a pillar working.

**Bastion uses the managed Gemini Enterprise Agent Platform surfaces, with proof status shown
explicitly below.** It writes no substitute for any of them — the ~3,460 lines that did were
deleted on 2026-08-15 ([ADR-003](docs/adr/003-pillars-on-geap.md)).

| Group | Pillar | The managed product that serves it | Reached by | Status |
|---|---|---|---|---|
| **Discovery & Lifecycle** | Agent Registry | GEAP **Agent Registry** — the central catalog for agents, tools, and MCP servers | Three private JSON-RPC/A2A services are published | ✅ catalogued |
| **Core Execution & State** | Agent Runtime | GEAP **Agent Runtime** / Agent Engine — long-running async execution | A private Agent Engine is created; Cloud Run/Eventarc provides durable admission | ✅ deployed |
| **Core Execution & State** | Memory Bank | GEAP **Memory Bank** (GA) — persistent cross-session context and the exception store | Managed session/memory endpoints plus Firestore investigation identity | ◐ replay evidence pending |
| **Security & Governance** | Agent Identity | **Agent Identity** as the Gateway's authorization principal (mTLS + DPoP), plus one least-privilege service account per agent | Separate Cloud Run identities and IAM-authenticated internal calls | ✅ deployed |
| **Security & Governance** | Agent Gateway | GEAP **Agent Gateway** — routing and policy enforcement, ingress and egress | API enabled; current fleet uses direct private Cloud Run A2A | ◐ Gateway itself pending |
| **Security & Governance** | Model Armor | **Model Armor**, which Agent Gateway delegates sanitization to | `ModelArmorClient` · `before_model_callback` | ✅ live guardrail |
| **Telemetry** | Agent Observability | Cloud Trace + Cloud Logging, via ADK's own OpenTelemetry spans | Payload-free audit logs and no-content ADK telemetry | ◐ retained trace pending |

The three governance pillars are **one composed stack, not three independent ones**: Agent
The planned Gateway would enforce policy through IAM and Identity-Aware Proxy and delegate content sanitization to
Model Armor, and authorizes on Agent Identity as the principal. That is how Google ships them,
and it is a better architecture than the three unrelated modules this repository used to hold.

### What the brief asks entrants to demonstrate

| The brief asks for | Where Bastion answers it |
|---|---|
| *"agents cataloged for cross-department use"* | Three private Bastion JSON-RPC services are published in Agent Registry; department routing is repository-owned policy. Version/approval metadata is not yet evidenced. |
| *"safely maintain context across weeks of asynchronous operations"* | Eventarc/Firestore creates a durable investigation identity and maps it to Agent Engine session/memory. A prior-week suppression replay remains the required proof. |
| *"interact with production data without violating enterprise compliance, data sovereignty, or security policies"* | A **live** IAM policy, read-only, never written back — and an explicit, honest position on residency below |

**Data sovereignty, stated rather than implied.** Cloud Run, Firestore, and Pub/Sub are pinned
to `europe-north2`, so state stays in one EU region. **Model traffic is not** — Gemini 3.5 is
served only from Vertex AI's `global` location, with no regional endpoint to choose. What
crosses that boundary is minimised by design: detection is deterministic and runs *before* any
model call, so Gemini writes the rationale for a finding rather than finding it, and never
receives the raw policy. A production system handling third-party principals would need a
residency guarantee `global` cannot give. That is a real limit of this build, recorded in
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) rather than hidden.

**There is no DIY branch left.** An earlier version of this README described Registry, Runtime,
and Memory Bank as an ADK interface with *either* GEAP or a Firestore implementation behind it.
That framing is gone: every pillar is the managed product, and the reimplementations were
deleted rather than kept as a fallback. [ADR-003](docs/adr/003-pillars-on-geap.md) records both
the decision and the scope error that produced the earlier one.

### Architecture Decision Records

Every record traces to a quoted line in
[`submission/DEVPOST.md`](submission/DEVPOST.md), which captures the hackathon's own pages.

| ADR | Decision | Status |
|---|---|---|
| [001](docs/adr/001-real-iam-not-mock-data.md) | Audit a real GCP IAM policy, not mock entitlement rows; detection stays deterministic | Accepted |
| [002](docs/adr/002-three-agents.md) | Three agents; policy enforcement inside the Orchestrator | Accepted |
| [003](docs/adr/003-pillars-on-geap.md) | All seven pillars run on their managed GEAP product; no reimplementation | Accepted; **amended** |
| [004](docs/adr/004-flash-only-global-endpoint.md) | Gemini 3.5 Flash on `global`, no Pro tier; infra in `europe-north2` | Accepted; **verified** |
| [005](docs/adr/005-adk-as-the-agent-framework.md) | **Google ADK** as the agent framework; A2A as the inter-agent contract | Accepted; **amended** |
| [006](docs/adr/006-pillar-coverage.md) | One observable proof closes each pillar, and each submission artifact | Accepted |
| [007](docs/adr/007-tool-poisoning.md) | Tool poisoning defended at the tool-declaration boundary | Accepted |

**Thirteen records were cut to seven on 2026-08-15** and renumbered `001`–`007`. Six described
a premise that had stopped existing — Model Armor's fallback, the DIY registry and gateway, the
hand-written A2A envelope — and their substance was merged into the survivors, each of which
names what it absorbed.

---

## Tech Stack

### Language and runtime

[![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Google ADK](https://img.shields.io/badge/Google_ADK-2.7.0-4285F4?logo=google&logoColor=white)](https://google.github.io/adk-docs/)
[![A2A SDK](https://img.shields.io/badge/a2a--sdk-1.1.2-34A853?logo=google&logoColor=white)](https://github.com/a2aproject/A2A)
[![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-1.42.1-425CC7?logo=opentelemetry&logoColor=white)](https://opentelemetry.io/)

### Model and agent framework

[![Vertex AI](https://img.shields.io/badge/Vertex_AI-gemini_3.5_flash-4285F4?logo=googlegemini&logoColor=white)](https://cloud.google.com/vertex-ai)
[![Location](https://img.shields.io/badge/model_location-global-EA4335?logo=googlecloud&logoColor=white)](docs/adr/004-flash-only-global-endpoint.md)
[![Region](https://img.shields.io/badge/infra_region-europe--north2-34A853?logo=googlecloud&logoColor=white)](docs/adr/003-pillars-on-geap.md)

### Compute, state and messaging

[![Cloud Run](https://img.shields.io/badge/Cloud_Run-agents_+_gateway-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/run)
[![Firestore](https://img.shields.io/badge/Firestore-findings_+_exceptions-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/firestore)
[![Pub/Sub](https://img.shields.io/badge/Pub%2FSub-async_investigations-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/pubsub)
[![Cloud Scheduler](https://img.shields.io/badge/Cloud_Scheduler-continuous_review-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/scheduler)

### Security and governance

[![Cloud IAM](https://img.shields.io/badge/Cloud_IAM-one_SA_per_service-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/iam)
[![Asset Inventory](https://img.shields.io/badge/Asset_Inventory-policy_read-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/asset-inventory/docs/overview)
[![IAM Recommender](https://img.shields.io/badge/IAM_Recommender-corroboration-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/iam/docs/recommender-overview)
[![Model Armor](https://img.shields.io/badge/Model_Armor-injection_+_PII-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/security-command-center/docs/model-armor-overview)
[![Secret Manager](https://img.shields.io/badge/Secret_Manager-findings_endpoint-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/secret-manager)

### Telemetry, history and delivery

[![Cloud Trace](https://img.shields.io/badge/Cloud_Trace-reasoning_chain-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/trace)
[![Cloud Logging](https://img.shields.io/badge/Cloud_Logging-audit_logs-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/logging)
[![Cloud Monitoring](https://img.shields.io/badge/Cloud_Monitoring-budget_alerts-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/monitoring)
[![BigQuery](https://img.shields.io/badge/BigQuery-findings_over_time-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/bigquery)
[![Looker Studio](https://img.shields.io/badge/Looker_Studio-trend_view-4285F4?logo=googlecloud&logoColor=white)](https://lookerstudio.google.com/)
[![Firebase Hosting](https://img.shields.io/badge/Firebase_Hosting-judge_path-FFA000?logo=firebase&logoColor=white)](https://firebase.google.com/docs/hosting)
[![Cloud Build](https://img.shields.io/badge/Cloud_Build-source_deploys-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/build)
[![Artifact Registry](https://img.shields.io/badge/Artifact_Registry-images-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/artifact-registry)

### Quality gates

[![Ruff](https://img.shields.io/badge/Ruff-lint%20%2B%20format-D7FF64?logo=ruff&logoColor=111827)](https://docs.astral.sh/ruff/)
[![Mypy](https://img.shields.io/badge/Mypy-type_checked-2A6DB2?logo=python&logoColor=white)](https://mypy-lang.org/)
[![pytest](https://img.shields.io/badge/pytest-9.1.1-0A9EDC?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![Coverage floor](https://img.shields.io/badge/coverage_floor-being_reset-9CA3AF?logo=codecov&logoColor=white)](codecov.yml)

Twenty-one Google Cloud services, each with a job — the rules ask for one. The reasoning, and
the pre-agreed cut order if the schedule slips, is [ADR-003](docs/adr/003-pillars-on-geap.md).

| Layer | Service | Why it is here |
|---|---|---|
| Model | **`gemini-3.5-flash`** via Vertex AI, `locations/global` | Every call. No Pro tier — 3.5 Pro is unavailable to this project ([ADR-004](docs/adr/004-flash-only-global-endpoint.md)) |
| Agent framework | **Google ADK** | The chosen framework of the four the rules permit ([ADR-005](docs/adr/005-adk-as-the-agent-framework.md)). Three `LlmAgent`s composed by a `SequentialAgent`, executed 2026-08-15 |
| Compute | **Cloud Run** · `europe-north2` | `min-instances=0`, capped `max-instances`, authenticated except one read-only service |
| State & memory | **Firestore** · `europe-north2` | Durable investigation identity and the private, idempotent findings inbox |
| Async | **Pub/Sub** + **Eventarc** | One deployed topic delivers investigations to the private Orchestrator |
| Schedule | **Cloud Scheduler** | API enabled; no cadence job is provisioned |
| Findings source | **Recommender API** | API enabled; not in the current deterministic decision path |
| Policy read | **Cloud Asset Inventory** | Policy search across resources, not a single-project dump |
| Identity | **IAM** | One least-privilege service account per agent |
| Guardrails | **Model Armor** | Managed, fail-closed input screening; deterministic output boundary before delivery |
| Secrets | **Secret Manager** | One secret is provisioned; the private findings origin is currently deterministic deployment configuration, not a secret |
| Telemetry | **Cloud Trace** · **Cloud Logging** · **Cloud Monitoring** | The audit trail is the deliverable |
| History | **BigQuery** → **Looker Studio** | APIs enabled only; neither is in the deployed evidence path |
| Judge path | **Firebase Hosting** | Target only; no hosted frontend exists yet |
| Build | **Cloud Build** · **Artifact Registry** | Source-to-Cloud-Run deploys |

---

## Build & deployment status

Live private fleet against an Aug 31, 2026 deadline. This section distinguishes deployed
controls from retained proof artifacts, because both a missing control and an invented proof
would undermine the submission.

| | |
|---|---|
| ✅ | The GCP project is live, budgeted, and **`gemini-3.5-flash` answers through Vertex AI** — verified reachable ([ADR-004](docs/adr/004-flash-only-global-endpoint.md)) |
| ✅ | **100% coverage across 132 tests**, including security, integration, and load contracts. The CI floor stays at 100 |
| ✅ | Architecture, **seven** decision records, and brand assets are done and reviewable |
| ✅ | **Gemini is called.** One investigation, 5 model calls, 3 tool calls, against the live IAM policy ([evidence 02](assets/evidence/02-gemini-investigation.md)) |
| ✅ | **The agents are ADK agents.** Three `LlmAgent`s under a `SequentialAgent`, ADK 2.7.0 ([ADR-005](docs/adr/005-adk-as-the-agent-framework.md)) |
| ✅ | Four private Cloud Run services, Eventarc, EU Firestore/Pub/Sub, managed Agent Engine state, and the EU-replicated HMAC secret are deployed; Cloud Scheduler cadence remains intentionally unprovisioned |
| ✅ | Three redacted evidence records captured: Model Armor, a live-IAM Gemini run, and an IAM denial |

Progress is tracked as tagged releases: [`submission/planning/07-release-plan.md`](submission/planning/07-release-plan.md)
holds the ladder from `v0.1.0` to `v1.0.0` and what each version may claim. Claims not yet
earned are enumerated in [`submission/SUBMISSION.md`](submission/SUBMISSION.md). The ordered
post-audit build contract is
[`submission/planning/08-audit-remediation-plan.md`](submission/planning/08-audit-remediation-plan.md).

---

## Evidence

◐ **Four of fourteen captured.** [Evidence 01](assets/evidence/01-model-armor-block.md) records
a direct Model Armor block, [evidence 02](assets/evidence/02-gemini-investigation.md) records one
live-policy investigation, and [evidence 03](assets/evidence/03-escalation-agent-denied.md)
records the least-privilege IAM contrast. [Evidence 04](assets/evidence/04-private-fleet-deployment.md)
records the count-only, live deployment measurement. [`assets/README.md`](assets/README.md) is
the complete fourteen-shot plan.

Four of those shots carry the submission, and they are the last to be cut:

| Shot | What it proves |
|---|---|
| The IAM policy dump the findings came from | The data is real |
| A prior week's exception recalled, the finding not re-raised | Context maintained across weeks |
| A mis-scoped call denied | Zero trust is enforced, not documented |
| The malicious ticket blocked before it reaches Gemini | The system cannot be instructed by its inputs |

---

## Quick Start

This is the existing-project developer path. It runs the local ADK fleet against the Google
project configured in `.env`; it does not provision infrastructure or deploy the target fleet.

Requires Python 3.14+, the [gcloud CLI](https://cloud.google.com/sdk/docs/install), and a GCP
project with billing enabled and **a budget alert already set**.

```bash
git clone https://github.com/iarjunganesh/bastion.git
cd bastion

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env: set GOOGLE_CLOUD_PROJECT, GCP_PROJECT_ID, and MODEL_ARMOR_TEMPLATE_ID.

gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID

python -m dotenv run -- adk run --in_memory agents/orchestrator \
  "Run one Bastion access-review investigation."
```

<details>
<summary><strong>On Windows — PowerShell 7+</strong></summary>

```powershell
git clone https://github.com/iarjunganesh/bastion.git
cd bastion

python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

Copy-Item .env.example .env
# Edit .env: set GOOGLE_CLOUD_PROJECT, GCP_PROJECT_ID, and MODEL_ARMOR_TEMPLATE_ID.

gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID

python -m dotenv run -- adk run --in_memory agents/orchestrator `
  "Run one Bastion access-review investigation."
```

</details>

> **The one configuration mistake that costs a day.** `GOOGLE_CLOUD_LOCATION=global` and
> `GCP_REGION=europe-north2` are **different settings**. Gemini 3.5 has no regional endpoint,
> so pointing model calls at your infrastructure region returns a 404 whose message reads like
> a permissions failure.

### Auditing the real policy

```bash
make iam-policy    # writes <project>.iam-policy.json — gitignored, deliberately

# without make:
gcloud projects get-iam-policy "$GCP_PROJECT_ID" --format=json > "$GCP_PROJECT_ID.iam-policy.json"
```

**Write it to a file; do not print it.** That output carries real principals and real email
addresses, and a terminal is not ephemeral — it lands in scrollback, in transcripts, and in
anything later pasted into an issue or a screen recording. The file is gitignored, and
anything derived from it that reaches [`assets/evidence/`](assets/README.md) is redacted
first. When you only need the roles, ask for only the roles:
`--format="value(bindings.role)"` returns no identities at all. See
[`SECURITY.md`](SECURITY.md).

### Deploy

The repository has a reproducible private-Cloud-Run deployment path: one complete image context,
per-agent service accounts, internal ingress, audience-bound A2A tokens, Registry publication,
and post-deploy verification. Firestore and Pub/Sub are provisioned in `europe-north2`.

**The deployed fleet is internal-only.** The deploy script refuses to start with ephemeral
memory or without the pre-approved Model Armor template, builds one auditable image digest, and
publishes that image to all services. See
[`infrastructure/REQUIRED_GCP_ACCESS.md`](infrastructure/REQUIRED_GCP_ACCESS.md) for the
remaining administrator prerequisites.

---

## Project Structure

Every path below exists. Where a folder holds only a placeholder, it says so.

```text
bastion/
├── agents/                         # one folder per deployable agent
│   ├── orchestrator/agent.py       # SequentialAgent + the policy step; ADR-002 keeps
│   │                               #   enforcement here rather than in a fourth agent
│   ├── access_auditor/agent.py     # deterministic detection over the live IAM policy
│   └── escalation_agent/agent.py   # write-only; cannot read what it escalates
│
├── registry/departments.py         # ┐ The pillars that are still code here: the
├── model_armor/guardrails.py       # │ department catalog, the before_model_callback
├── observability/audit.py          # ┘ screen, and the audit BasePlugin. Each is a SEAM
│                                   #   onto a managed GEAP product, not a copy of one
├── identity/identity_config.md     #   Scope per agent — enforced in IAM, so it is
│                                   #   configuration rather than code
│                                   #   gateway/ runtime/ memory/ are GONE (ADR-003)
│
├── infrastructure/
│   ├── provision.py                # idempotent Firestore, Pub/Sub, and IAM bootstrap
│   ├── deploy.sh                   # private Cloud Run fleet + Registry + verifier
│   ├── register_agents.py          # managed Agent Registry catalog publication
│   └── trigger_investigation.py    # acknowledged event publication with stable identity
│
├── scripts/
│   ├── check_docs.py               # the documentation gate CI runs
│   ├── check_versions.py           # pins vs documents, and vs PyPI before a tag
│   ├── capture_gcp_state.py        # measures the live project → gcp-state.json
│   └── render_diagrams.py          # SVG masters → light/dark variants + animated GIFs
│
├── tests/                          # unit, integration, security, and load contracts
│   ├── conftest.py                 # patches import-time clients at collection, not in
│   │                               #   a fixture — pytest imports modules before those run
│   ├── unit/                       # 6 modules: the three agents + the three seams
│   ├── integration/                # durable replay and idempotent notification flow
│   ├── security/                   # policy, identity, and private-Cloud-Run auth
│   └── load/                       # concurrent admission/refusal contract
│
├── docs/
│   ├── ARCHITECTURE.md             # the system, with per-box build state
│   └── adr/001…007 + README.md     # decisions that constrain the implementation
│
├── submission/
│   ├── DEVPOST.md                  # the hackathon captured verbatim — source of truth
│   ├── SUBMISSION.md               # Devpost checklist, and claims not yet earned
│   └── planning/00…07              # judging matrix, build plan, storyboard, release ladder
│
├── assets/
│   ├── brand/                      # logo (static + animated) + banners, light and dark
│   ├── architecture/               # gcp-state.json + Level 1/2 masters, variants, GIFs.
│   │                               #   Each SVG discloses its build state in its own text
│   ├── evidence/                   # 3 of 14 captured — machine-generated, redacted
│   ├── screenshots/                # EMPTY — console frames, numbered in walkthrough order
│   ├── demo-video/                 # EMPTY — sources the final cut is made from
│   └── demo-voiceover/             # EMPTY — narration script and takes
│
├── .github/workflows/
│   ├── ci.yml                      # lint · types · tests · docs · secrets · state
│   └── release.yml                 # tag-triggered gate + GitHub release
│
├── pyproject.toml  requirements.txt  requirements-dev.txt
├── Makefile  codecov.yml  .markdownlint.json  .env.example
└── README.md  CHANGELOG.md  CONTRIBUTING.md  SECURITY.md  CLAUDE.md  LICENSE
```

---

## Production & Quality

**All four local layers are populated today.** They verify deterministic controls and durable
replay without CI credentials. Managed-service smoke evidence remains pending deployment.

| Layer | Question | Command |
|---|---|---|
| `tests/unit/` | Does the implemented local code behave? | `make test-unit` |
| `tests/integration/` | Durable replay and idempotent notification flow | `make test-integration` |
| `tests/security/` | Gateway policy, identity manifest, Cloud Run token contract | `make test-security` |
| `tests/load/` | 16-way concurrent admission/refusal policy contract | `make test-load` |

```bash
make ci          # lint · types · tests · coverage · markdown · docs gate
make test-fast   # everything except the load layer
```

**Failure tolerance remains unimplemented.** The rules page grades this track on
*"is the inter-agent routing logic failure-tolerant — how does the system recover if a worker
agent loops or returns a hallucination?"*. The previous retry implementation was deleted with
the DIY runtime. The replacement must be demonstrated on the chosen managed runtime and backed
by integration tests before Bastion claims this criterion.

Three things worth knowing about how this suite is built:

**CI holds no GCP credentials, deliberately.** A workflow able to read a real IAM policy would
be a credential path into the very project Bastion audits. Every outbound call is mocked, and a
test that needs Google APIs is a test that is checking the wrong thing.

**The security layer asserts what is *not* yet true, too.** The Escalation Agent's denial
cannot be captured without a deployed service account, so a test asserts the weaker offline
property — that the module imports no policy client and leaks no bindings. That test is
replaced by the captured `403` rather than deleted. Model Armor is the one control that has
moved the other way: it was a stub asserted to raise, and is now
[observed blocking prompt injection live](assets/evidence/01-model-armor-block.md).

Beyond pytest, CI runs a **documentation gate** (`scripts/check_docs.py`) that verifies every
counted claim — "seven pillars", "three agents" — against the directories that actually exist,
checks every ADR is indexed and referenced, and fails if `.env.example` loses the `global` model
location that [ADR-004](docs/adr/004-flash-only-global-endpoint.md) exists to protect. It also
runs a **credential scanner** that fails the build on a committed service-account key, private
key, API key, or raw IAM policy dump.

---

## Documentation

| Document | What it is |
|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | The system: agents, pillars, data flow, stack |
| [docs/adr/](docs/adr/README.md) | Decisions that constrain the implementation |
| [submission/DEVPOST.md](submission/DEVPOST.md) | The hackathon captured verbatim — rules, criteria, prizes, updates |
| [submission/SUBMISSION.md](submission/SUBMISSION.md) | Devpost checklist, and claims not yet earned |
| [submission/planning/](submission/planning/07-release-plan.md) | Working notes `00`–`07`: judging matrix, build plan, storyboard, release ladder |
| [assets/README.md](assets/README.md) | The evidence plan and demo shot list |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Conventions, commit and release discipline |
| [SECURITY.md](SECURITY.md) | Credentials, IAM dumps, and the properties Bastion asserts about itself |
| [CHANGELOG.md](CHANGELOG.md) | What became true, per release |

The numbered documents under `submission/planning/` are working notes rather than judge-facing
prose: the judging matrix, the build plan, the demo storyboard, the release ladder, and the
review that set the current scope.

---

## Trust Model & Disclosure

**The audited data is real.** Bastion reads the IAM policy of a live GCP project. That is the
point, and it is why raw policy dumps never enter this repository — they carry real principals
and real email addresses. Published evidence is redacted deliberately.

**Bastion's own claims are meant to be checked.** Every security property in
[`SECURITY.md`](SECURITY.md) — scoped identities, gateway-only routing, injection screening,
authenticated endpoints — is a claim this project earns only once it has been observed working.
Which ones are verified is tracked in [`submission/SUBMISSION.md`](submission/SUBMISSION.md),
and anything that ships unverified is named as such.

**Read-only by design.** Bastion reads IAM and escalates to humans. It does not revoke access,
modify bindings, or write to the policy it audits. An access-governance agent with write
permission on the thing it audits is a harder safety problem than an 18-day build should attempt.

**Built for a hackathon.** Not production software, no support commitment. Licensed
[MIT](LICENSE).
