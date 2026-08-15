# Evidence 02 — One full investigation, live Gemini, real IAM policy, cross-department routing

**Captured:** 2026-08-15
**Model:** `gemini-3.5-flash` via Vertex AI, `GOOGLE_CLOUD_LOCATION=global`
**Framework:** `google-adk==2.7.0`, `SequentialAgent` over three `LlmAgent`s
**Guardrail:** Model Armor `bastion-guardrail` (`europe-west4`) on `before_model_callback`

One investigation, run end to end against the live `bastion-fleet-2026` IAM policy:

```text
  tool call   : audit_iam_policy
  tool result : audit_iam_policy    -> {'count': 2}
  tool call   : apply_policy_rules
  tool result : apply_policy_rules  -> {'escalate_count': 2, 'clear_count': 0}
  tool call   : route_by_department
  tool result : route_by_department -> {'department_count': 2, 'escalated_total': 2}

  agents ran  : ['access_auditor', 'policy_step', 'escalation_agent']
  model calls : 5
  tool calls  : 3
  tokens      : in=4091 out=486

  VERDICT: GEMINI CALLED
```

## What this closes

| Gate | Before | Now |
|---|---|---|
| Gemini 3.5+ via Vertex AI | Model reachable, **no call site** | **5 model calls in one investigation** |
| One Google Agent Framework | ADK pinned, **not imported** | Three ADK agents composed and executed |
| One Google Cloud infra service | Clients wired, nothing exercised | Cloud Asset Inventory read the live policy |

All three mandatory technologies are now met **in code that ran**, not in configuration.

## What it also demonstrates

- **The findings are real.** `count: 2` came from Cloud Asset Inventory against the project's
  actual IAM policy — no fixture, no seeded overlay.
- **Cross-department routing fired.** Two findings, **two different owning teams**. The track
  asks for agents *"cataloged for cross-department use"*; this is one investigation fanning out
  to the teams that own the principals rather than to one central inbox.
- **Detection stayed deterministic.** `audit_iam_policy` returned its count before any model
  reasoning; the five model calls wrote rationale and drove tool selection, and never produced
  a finding.

## Redaction

The run deliberately printed only integers and agent names. Member identifiers, role bindings,
finding text and model output were never emitted — the harness filters tool responses to scalar
values only. This file therefore contains no principal from the audited project.

## What is still not proven

- **Nothing is deployed.** This ran locally against live Google APIs. No Cloud Run service, no
  Agent Engine deployment, no Cloud Trace span.
- **The Model Armor block was not exercised here** — the investigation prompt is benign, so the
  guardrail correctly passed it through. The block itself is
  [evidence 01](01-model-armor-block.md).
- **No memory.** `InMemorySessionService` was used, so nothing persisted and no prior-week
  exception was recalled. The Memory Bank suppression proof is still owed.
