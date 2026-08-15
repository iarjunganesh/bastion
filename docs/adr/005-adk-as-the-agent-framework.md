# ADR-005: Google ADK as the agent framework

**Status:** Accepted 2026-08-13. **Amended 2026-08-15** — version raised to 2.7.0, and the
rejection of the Antigravity SDK now rests on a measured incompatibility rather than a
judgement about documentation quality.
**Date:** 2026-08-15

## Decision

Bastion's three agents are **ADK agents** (`google-adk==2.7.0`). ADK owns the agent
definition, the tool-calling loop, and the session and memory service interfaces
([ADR-003](003-pillars-on-geap.md)). The GenAI SDK, Antigravity SDK, and Genkit are not used.

Concretely: each agent is an `LlmAgent` with explicitly declared tools; the Orchestrator
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
- **Zero installation risk.** Verified 2026-08-15 against `google-adk==2.7.0`:
  `google.adk.agents`, `.tools`, `.memory`, `.sessions`, `.a2a`, `.plugins` and
  `vertexai.agent_engines.AdkApp` all import cleanly.

**The Antigravity SDK is not merely undocumented — it cannot be installed alongside this
stack.** `google-antigravity` 0.1.12 ships protobuf **7** gencode:

```text
VersionError: Detected incompatible Protobuf Gencode/Runtime versions when loading
google/antigravity/proto/localharness.proto: gencode 7.35.0 runtime 6.33.6
```

while `a2a-sdk` and `google-cloud-aiplatform` both pin `protobuf<7`. Adopting Antigravity
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

ADK holds `opentelemetry-api`/`sdk` at `<=1.42.1`, which is why `requirements.txt` pins
1.42.1 rather than the newest release. Raise both together when ADK does.

**ADK ships FastAPI, Starlette and uvicorn.** Bastion's Flask surfaces were competing with the
framework's own server; Flask is removed from `requirements.txt`.

**ADK releases fast — 2.6.3 to 2.7.0 inside two days.** Every document naming a version goes
stale silently, and the README badge is the version a judge actually reads.
`scripts/check_versions.py` holds documents to `requirements.txt` offline on every push, and
`--check-upstream` compares the pin against PyPI before a tag.

### `SequentialAgent` is deprecated in 2.7.0, and Bastion keeps using it

Importing `agents/orchestrator/agent.py` emits:

```text
DeprecationWarning: SequentialAgent is deprecated in favor of Workflow and will be removed in
a future version. Workflow cannot yet be used as an LlmAgent sub-agent.
```

**The warning names its own blocker in its second sentence.** Bastion composes three
`LlmAgent`s under one parent, which is precisely the arrangement `Workflow` cannot yet serve,
so the deprecated class is not a shortcut here — it is the only construct that expresses the
design. Migrating early would mean either flattening the fleet to a single agent, which
[ADR-002](002-three-agents.md) rules out, or hand-rolling the sequencing, which is the mistake
[ADR-003](003-pillars-on-geap.md) exists to prevent.

Recorded rather than suppressed. A `filterwarnings` entry would hide the one signal that says
when to move, and this repository's whole argument is that its claims are checkable. The
migration trigger is explicit: **when `Workflow` can be an `LlmAgent` sub-agent, switch.**
`scripts/check_versions.py --check-upstream` runs before every tag, so a release that changes
this will not pass unnoticed.

This also bounds the blast radius. The composition is four lines in one module; nothing else
in the repository names `SequentialAgent`, because the pillars are managed products and the
agents are plain `LlmAgent`s.

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
interleaved logs. That is `invocation_id` in `observability/audit.py`, recorded by the
`BasePlugin` on every agent, model, and tool event.

`adk deploy cloud_run --a2a` exposes the endpoint; Agent Gateway routes to it.
