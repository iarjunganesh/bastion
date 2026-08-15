# ADR-003: The seven pillars run on GEAP, not on reimplementations of it

**Status:** Accepted 2026-08-13. **Amended 2026-08-15** — the original conclusion was wrong
about two pillars, and the error is recorded rather than edited away.
**Date:** 2026-08-15

## Decision

Every pillar the Fortified Enterprise Fleet track names is served by its **managed Gemini
Enterprise Agent Platform product**, reached through ADK where ADK has a seam for it. Bastion
writes no substitute for any of them.

| Pillar | What serves it | Reached by |
|---|---|---|
| **Agent Registry** | GEAP **Agent Registry** — catalogs agents, tools, and MCP servers | Managed surface |
| **Agent Runtime** | GEAP **Agent Runtime** / Agent Engine | `adk deploy agent_engine`, `vertexai.agent_engines.AdkApp` |
| **Memory Bank** | GEAP **Memory Bank** (GA) | `VertexAiMemoryBankService`, `--memory_service_uri` |
| **Agent Identity** | Agent credential brokering; per-agent service accounts for GCP IAM | `google-cloud-agentidentitycredentials`; Gateway authorises on it |
| **Agent Gateway** | GEAP **Agent Gateway** | `gcloud network-services agent-gateways` |
| **Model Armor** | **Model Armor**, delegated to by Agent Gateway | `ModelArmorClient`, `before_model_callback` |
| **Agent Observability** | Cloud Trace + Cloud Logging via ADK | `adk deploy cloud_run --trace_to_cloud` |

Sessions use `VertexAiSessionService`, with ADK's `InMemorySessionService` in tests.

## Context

**This record previously concluded that Agent Registry had no managed equivalent and must be
built DIY over Firestore.** It also never evaluated Agent Gateway at all, so that pillar was
built as a Flask service by default rather than by decision. Both were wrong:

- **Agent Registry is a managed GEAP product** — *"a unified catalog that lets you securely
  store, discover, and manage Model Context Protocol (MCP) servers, tools, and AI agents
  across your organization."* It covers publishing and discovery, and extends past the
  track's wording by cataloging MCP servers and tools, not only agents.
- **Agent Gateway is a managed GEAP product** — the networking component that *"secures and
  governs connectivity for all agentic interactions"*, with ingress and egress modes,
  configured through `gcloud network-services agent-gateways`.

**The error was one of scope, not of method.** The 2026-08-13 probe asked whether a registry
surface existed *in `vertexai.agent_engines`*, found none, and generalised that to "no managed
registry exists." GEAP's Registry is a separate surface, and the probe never looked at it. A
negative result from one namespace was recorded as a fact about the platform.

The correction also revealed that the three governance pillars are **one composed stack**
rather than three independent ones: a provisioned Agent Gateway would enforce policy through IAM and
Identity-Aware Proxy, **delegates content sanitization to Model Armor**, and **authorises on
Agent Identity as the principal**, secured with mTLS and DPoP. Bastion had them as three
unrelated modules, which is a worse architecture than the one Google ships.

## Rationale

- **Reimplementing a managed pillar argues against the submission.** The track asks how an
  organisation adopts enterprise agent infrastructure. Answering with a hand-rolled Flask
  router is a worse answer to *Architectural Discipline* (30%) than using the product, and it
  costs schedule that the pass/fail gates need.
- **ADK is the seam, and it holds.** Verified against the pinned tree
  (`google-adk==2.7.0`): `VertexAiMemoryBankService`, `VertexAiSessionService`,
  `BaseMemoryService`/`BaseSessionService`, `google.adk.a2a`, `google.adk.plugins.BasePlugin`,
  and `vertexai.agent_engines.AdkApp` all import cleanly. Memory and session backends stay a
  configuration change rather than a rewrite.
- **The A2A contract is a dependency, not a file.** `a2a-sdk` supplies `AgentCard`,
  `AgentSkill`, `Task`, `TaskState`, `TaskStatus` and `Message`. Bastion's deleted A2A envelope
  module reimplemented the first three.
- **`europe-north2` survives.** It is one of 48 Vertex AI locations on `bastion-fleet-2026`,
  and `reasoningEngines` LIST returns `HTTP 200` there. The regional risk this record raised
  on 2026-08-13 did not materialise. **A 200 on LIST is not proof that a deploy succeeds** —
  that is settled by deploying one trivial agent, which is the first build task.

## Consequences

**~3,460 lines were deleted on 2026-08-15**, across `gateway/`, `registry/`, `runtime/`,
`memory/`, `model_armor/`, `observability/`, the Orchestrator's hand-rolled retry and circuit
breaker, and the ten test files bound to them. The `DIY FALLBACK` banner problem this record
described is resolved by the files no longer existing.

**Coverage is not 100% while the rewrite lands.** The CI floor was measured against modules
that were deleted. Lowering it is a deliberate act with a date attached, not a drift — see
[ADR-006](006-pillar-coverage.md).

**Data residency now has two answers, and both must be stated before either is claimed.**
Memory Bank being managed means investigation state may leave `europe-north2`, and the model
endpoint is already `global` ([ADR-004](004-flash-only-global-endpoint.md)). The track names
data sovereignty explicitly, so the residency note in `README.md` covers both or neither.

**Agent Gateway and Agent Registry are two GCP surfaces that must actually be provisioned.**
Neither has been created on `bastion-fleet-2026` yet. Until they are, this record describes
an intention, and nothing may claim them as built.

## Absorbed records

Three earlier records were folded into this one on 2026-08-15, because each described a
decision this one now makes. They are deleted rather than left as files: a brand-new repository
with thirteen records, six of them describing premises that no longer exist, costs a judge more
attention than it earns.

### Model Armor (was ADR-004)

Model Armor screens the model boundary. The tool allowlist screens the tool boundary
([ADR-007](007-tool-poisoning.md)), and Agent Gateway screens the agent boundary — three
controls that **compose rather than overlap**, which is why screening more text is not a
defence against a poisoned tool declaration.

That record hedged with a documented fallback and a hard cutoff date, in case the managed
service did not ship in time. It shipped: `google-cloud-modelarmor` exposes
`sanitize_user_prompt` and `sanitize_model_response`; `model_armor/guardrails.py` calls the
first from ADK's `before_model_callback`, while a deterministic `after_model_callback` blocks
protected data before the count-only findings receiver. **The fallback is withdrawn** — a second Gemini call
asking "is this an injection?" would have been a weaker control described in stronger words.

Screening **fails closed**: an unset template or an exception on the screening path refuses the
call. A missing environment variable must not be able to silently disable a security control
while every document still claims it works.

### The GCP service surface and the cut order (was ADR-006)

Twenty-one services, each with a job — seventeen from this record, Eventarc for durable
investigation delivery, plus the three GEAP surfaces enabled 2026-08-15
(`networkservices`, `agentregistry`, `agentidentity`). GEAP consolidates several of them, so the count is no
longer the interesting number — the **cut order** is, and it is unchanged: BigQuery and Looker
Studio go first, then Cloud Asset Inventory, then Secret Manager. The judge path, the
Recommender API, and Cloud Scheduler are **not** cut, because each is load-bearing for a
scoring criterion rather than for a feature.

`scripts/capture_gcp_state.py` writes the measured state of these services by querying the live
project, so any diagram derived from it is measured rather than typed.

### Cross-department catalog and multi-week context (was ADR-010)

The track asks that agents be *"cataloged for cross-department use"* and *"safely maintain
context across weeks of asynchronous operations."* Both are now managed products rather than
schema decisions: Agent Registry carries the catalog, and Memory Bank carries the context. What
survives from that record is the **obligation**, not the implementation — an investigation
opened Monday must still be resumable on Thursday, and a finding a human closed weeks ago must
be suppressed rather than re-raised. [ADR-006](006-pillar-coverage.md) holds the proof for each.
