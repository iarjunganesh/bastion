# ADR-005: Google ADK as the agent framework

**Status:** Accepted 2026-08-13. **Amended 2026-08-15** — version raised to 2.7.0, and the
rejection of the Antigravity SDK now rests on a measured incompatibility rather than a
judgement about documentation quality. **Amended 2026-08-22** — version raised to 2.7.1 for the
`v0.2.0` tag, and the composition below corrected: not every step is an `LlmAgent` any more.
**Amended 2026-08-23** — the Escalation Agent is no longer an `LlmAgent` either (P0.2); only the
Access Auditor still is. **Amended 2026-08-27** — version raised to 2.8.0 for the `v0.6.0` tag; see "2.8.0 was reviewed, declined, then taken" below. **Date:** 2026-08-27

## Decision

Bastion's three agents are **ADK agents** (`google-adk==2.13.0`). ADK owns the agent
definition, the tool-calling loop, and the session and memory service interfaces
([ADR-003](003-pillars-on-geap.md)). The GenAI SDK, Antigravity SDK, and Genkit are not used.

Concretely: the Access Auditor is an `LlmAgent` with an explicitly declared tool. The Escalation
Agent is a deterministic `BaseAgent` (P0.2, [ADR-012](012-structured-findings-across-a2a.md)) —
it has no tool declaration and no model, because *whether* and *which* department to notify are
not decisions a model should be in a position to make either. The Orchestrator's internal
sequence contains three further `BaseAgent` steps that hold no model at all — `policy_step`,
`policy_gate`, and `escalation_gate` — for the same reason: applying a constant threshold,
refusing to continue without a recorded result, and refusing to report completion without a
confirmed delivery are not model decisions
([ADR-010](010-policy-enforcement-gate.md)). ADK supports this directly: `BaseAgent` is a
first-class member of a `SequentialAgent`, so removing the model cost no framework support. The
Orchestrator
composes the Access Auditor and the Escalation Agent through ADK's orchestration agents
(`SequentialAgent`, `ParallelAgent`, `LoopAgent`) rather than a hand-rolled `asyncio.gather`;
and inter-agent traffic crosses the **managed Agent Gateway**, which is what the observability
layer records.

Cross-cutting controls attach at ADK's own seams rather than at call sites:

| Control | Seam |
|---|---|
| Model Armor screening | `before_model_callback(callback_context, llm_request)` |
| Tool allowlist ([ADR-007](007-tool-poisoning.md)) | `before_tool_callback` |
| Fleet-wide audit records | `google.adk.plugins.BasePlugin` — 15 hooks, applied once |

## Context

This is a **pass/fail gate**, quoted verbatim from the overview:

> *"At least one Google Agent Framework: Google ADK, GenAI SDK, Antigravity SDK or GenKit."*

**Four options are named.** On 2026-08-13 none of them was in use: `google-adk` was pinned and
imported nowhere, the README carried an ADK badge, and the three "agents" were plain Python
modules behind Flask routes. A pinned dependency is not a framework. That defect is closed by
the rewrite this record describes; the false claims came out of `README.md` first, ahead of
any code.

## Rationale

- **ADK is the framework the hackathon is organised around.** The overview names it in its
  opening paragraph, the resources page lists it first under *Build your agent*, and two of
  the four webinars are ADK sessions.
- **ADK is what makes [ADR-003](003-pillars-on-geap.md) resolvable.** `BaseSessionService` and
  `BaseMemoryService` turn GEAP-versus-DIY into a backend configuration.
- **`adk deploy` is the deployment path**, so the framework choice and the runtime choice are
  one choice. `adk deploy` offers `agent_engine`, `cloud_run`, and `gke`; the Cloud Run form
  carries `--trace_to_cloud`, `--a2a`, `--session_service_uri` and `--memory_service_uri`, so
  four pillars are flags rather than modules.
- **Zero installation risk.** Re-verified 2026-08-27 against `google-adk` v2.8.0, as it was on
  2026-08-22 against 2.7.1 and 2026-08-15 against 2.7.0: `google.adk.agents`, `.tools`, `.memory`,
  `.sessions`, `.a2a`, `.plugins` and `vertexai.agent_engines.AdkApp` all import cleanly. Re-run
  rather than
  re-dated — a verification claim that is edited to match a new pin is no longer a verification.

**Historical incompatibility (15 August 2026).** The Antigravity SDK could not be
installed alongside the then-current stack: `google-antigravity` 0.1.12 ships protobuf **7** gencode:

```text
VersionError: Detected incompatible Protobuf Gencode/Runtime versions when loading
google/antigravity/proto/localharness.proto: gencode 7.35.0 runtime 6.33.6
```

At that capture, `a2a-sdk` and `google-cloud-aiplatform` both pinned `protobuf<7`. Adopting Antigravity
means giving up the A2A contract and Agent Engine — the Gateway and Runtime pillars. It was
installed on 2026-08-15, observed to fail, and uninstalled. Genkit remains JS/Go-first, and
the GenAI SDK is a model client rather than an agent framework: ADK already depends on
`google-genai`, so importing it alone would satisfy the letter of the gate while leaving the
multi-agent structure hand-rolled.

**The fork of `google/adk-python` is a convenience, not an architecture.** It gives a place to
carry a patch or open a pull request; it does not change what `pip install google-adk`
resolves. Nothing in the submission should present it as a technical choice.

## Consequences

ADK's tool-calling loop is where **tool poisoning** becomes reachable, because declared tools
are what an injected instruction would try to redirect. That is
[ADR-007](007-tool-poisoning.md), a consequence of this decision rather than an independent
idea.

ADK 2.13.0 accepts `opentelemetry-api`/`sdk` through 1.44. The current candidate uses
the 1.44.0 pair; its unresolved security advisory blocks the Python release (see
[dependency status](../DEPENDENCY-STATUS.md)). ADK changes its default GenAI trace schema in this release;
new traces must be reviewed rather than assumed identical to the August captures.

**ADK ships FastAPI, Starlette and uvicorn.** Bastion's Flask surfaces were competing with the
framework's own server; Flask is removed from `requirements.txt`.

**ADK releases fast — 2.6.3 to 2.7.0 inside two days.** Every document naming a version goes
stale silently, and the README badge is the version a judge actually reads.
`scripts/check_versions.py` holds documents to `requirements.txt` offline on every push, and
`--check-upstream` compares the pin against PyPI before a tag. Only the five packages a document
names can *fail* that check; since `v0.6.0` every other pin is surveyed and reported too, because
a gate covering five of twenty-three pins was being read as covering all of them.

### `SequentialAgent` is deprecated in 2.7.0, and Bastion keeps using it

Importing `agents/orchestrator/agent.py` emits:

```text
DeprecationWarning: SequentialAgent is deprecated in favor of Workflow and will be removed in
a future version. Workflow cannot yet be used as an LlmAgent sub-agent.
```

**The warning names its own blocker in its second sentence.** Bastion composes `LlmAgent`s
under one parent, which is precisely the arrangement `Workflow` cannot yet serve,
so the deprecated class is not a shortcut here — it is the only construct that expresses the
design. Migrating early would mean either flattening the fleet to a single agent, which
[ADR-002](002-three-agents.md) rules out, or hand-rolling the sequencing, which is the mistake
[ADR-003](003-pillars-on-geap.md) exists to prevent.

Recorded rather than suppressed. A `filterwarnings` entry would hide the one signal that says
when to move, and this repository's whole argument is that its claims are checkable. The
migration trigger is explicit: **when `Workflow` can be an `LlmAgent` sub-agent, switch.**
`scripts/check_versions.py --check-upstream` runs before every tag, so a release that changes
this will not pass unnoticed.

### 2.8.0 was reviewed, declined, then taken

`--check-upstream` failed before the `v0.6.0` tag: PyPI carried a newer release than this ADR's
pin. The first decision was to decline it, on the grounds that the migration trigger had not
fired and that the deployed fleet was running the older resolution. The platform owner overrode
that, and the pin moved. Both halves are recorded because the reasoning for declining is still
the reasoning that governs the *deployment*, which has not moved with it.

**The migration trigger still has not fired.** The newer release changes neither
`SequentialAgent`'s deprecation status nor `Workflow`'s eligibility as an `LlmAgent` sub-agent, so
the one condition this ADR commits to acting on remains unmet and the composition below is
unchanged.

**What was verified before the pin moved.** The full suite passes on the new resolution — 321
tests at 100% statement and branch coverage — along with Ruff, the type checker, and every
documentation gate. The import claim above was re-run rather than re-dated. A local A2A
round-trip was exercised end to end: a `SequentialAgent` calling a `RemoteA2aAgent` served over
HTTP, agent card resolved, remote executed.

**What was not verified, and cannot be from here.** OpenTelemetry is capped by the framework at
`<=1.42.1`, so the trace path did not move and needs no re-verification. But the release adds
native task mode to `RemoteA2aAgent` and a Model Armor guardrail plugin, which are the two seams
[ADR-009](009-model-armor-threshold.md)'s fail-closed callback and both A2A worker hops occupy.
A passing local suite is not a live fleet.

**So the repository and the deployment now disagree, deliberately and temporarily.** The managed
Agent Runtime and both Cloud Run workers are still running the resolution `v0.4.0` deployed.
Until both surfaces are redeployed and re-verified live, every "deployed and verified" claim in
the evidence set describes the older resolution, and redeploying will mint new Cloud Run
revisions — which the evidence records name explicitly, so
[evidence 11](../../assets/evidence/11-current-route-correlation.md),
[12](../../assets/evidence/12-agent-mediated-model-armor-refusal.md) and
[13](../../assets/evidence/13-current-route-trace.md) will need re-capturing when it happens.
That is the cost of the bump, and it is stated here rather than discovered later.

This also bounds the blast radius. The composition is a handful of lines in one module; nothing
else in the repository names `SequentialAgent`, because the pillars are managed products, the
Access Auditor is the fleet's one `LlmAgent`, and the Escalation Agent plus the three
deterministic Orchestrator steps are plain `BaseAgent`s.

## Absorbed record: A2A as the inter-agent contract (was ADR-013)

Folded in on 2026-08-15. A2A is Google's agent-to-agent protocol, and it is the contract
between Bastion's agents — but it is no longer a decision this repository implements.

`a2a-sdk` ships `AgentCard`, `AgentSkill`, `Task`, `TaskState`, `TaskStatus` and `Message`, and
ADK ships `google.adk.a2a` with its executor, converters, and `agent_card_builder`. The earlier
record specified an envelope with a typed task, an investigation context id, and an explicit
lifecycle; all of it exists in a dependency now installed, and the hand-written version was
deleted.

What survives is the **obligation the envelope existed to serve**: every hop carries an id that
lets the audit trail be reassembled into one reasoning chain rather than inferred from
interleaved logs.

This record originally named `invocation_id` as that id. **Amended 2026-08-22: it is not, and
deleting the hand-written envelope did drop something after all.** ADK mints `invocation_id` per
agent run, and a worker reached over A2A is a separate run in a separate process, so one
investigation produced three unrelated ids and its records could not be assembled at all — the
exact obligation this section claimed was satisfied. The dependency supplies the transport, not
the correlation.

The id that now carries across every hop is `investigation_id`, seeded from the durable event at
dispatch and forwarded as A2A request metadata rather than as message content, so no model ever
reads or restates it. `invocation_id` is still recorded, and still groups one agent run — which
is all it ever did.

`adk deploy cloud_run --a2a` exposes the endpoint; Agent Gateway routes to it.

## 28 October upgrade

The source target is Google ADK 2.13.0 with A2A SDK 1.3.0 and Google Cloud AI Platform
2.6.0. Local dependency/contract verification and both deployment surfaces must pass before
claiming the new production resolution. See [VERSIONS.md](../VERSIONS.md) and
[UPGRADE-PLAN.md](../UPGRADE-PLAN.md). The dated decisions above remain historical records.
