# Evidence 08 — the tool-declaration boundary, observed at construction

**Captured:** 2026-08-16, re-measured 2026-08-22, by `pytest tests/security/test_tool_surface.py`
under Python 3.12.
**Requires no deployment.** This is the one guardrail claim provable entirely offline, because
it is about what an agent *can* reach before any model runs.

[Evidence 01](01-model-armor-block.md) measured Model Armor declining to block a tool-poisoning
sample — correctly, since the threat is not primarily in the prompt text.
[ADR-007](../../docs/adr/007-tool-poisoning.md) names the control that does hold. This file is
its measurement.

## Declared tool sets

| Agent | Tools declared at construction |
|---|---|
| `access_auditor` | `audit_iam_policy` |
| `escalation_agent` | `notify_human` |

The Escalation Agent holds **no policy-reading tool at all** — not a tool it is instructed not
to call. An injected instruction cannot reach a capability that was never declared.

`policy_step` was listed here on 2026-08-16 holding `apply_policy_rules` and
`route_by_department`. It no longer appears, because it is no longer an `LlmAgent`: it calls the
threshold and the routing catalog directly and reaches no model at all
([ADR-010](../../docs/adr/010-policy-enforcement-gate.md)). An agent with no model has no
thought loop for a poisoned description to act on, so the strongest available form of this
boundary is the one where the tool declaration does not exist. The re-measured suite asserts that
absence rather than skipping it: `test_the_policy_step_reaches_no_model_and_so_declares_no_tools`
fails if `policy_step` ever regains a model, a tool list, or a model callback.

## Capability separation, stated differentially

| Module | Holds `asset_v1` IAM/Asset client |
|---|---|
| `agents/access_auditor/agent.py` | **yes** |
| `agents/escalation_agent/agent.py` | **no** |

Asserted as a difference rather than an absence on purpose: proving only that the Escalation
module lacks the client would also pass if the Access Auditor had quietly lost it, at which
point the test would be measuring nothing.

## The assertions were confirmed to fail when the boundary is widened

A test that cannot fail is not evidence. The constructed `escalation_agent` was given
`audit_iam_policy` in memory — the exact tool-poisoning outcome ADR-007 exists to prevent — and
the suite was re-run against the mutated agent:

```text
CAUGHT   fixed tool set (escalation_agent): assertion raised
CAUGHT   no policy-reading tool: assertion raised
CONTROL  access_auditor still passes unmutated
```

Both assertions fired; the unmutated control still passed, so the suite is discriminating rather
than uniformly red. The mutation was in-process only and never written to disk.

## Proof boundary

- This is **construction-time** proof: it establishes the reachable tool surface, not a refusal
  trace from a live agent under attack.
- The IAM half of the boundary is separately deployed proof —
  [evidence 03](03-escalation-agent-denied.md) captured the Escalation identity denied IAM read
  while the Auditor was permitted. A passing test proves the tool set; the denial proves the
  workload boundary. Neither substitutes for the other.
- `route_by_department` is sourced from `registry/departments.py` rather than `agents/`. It is
  repository-owned static source, which is what the assertion checks. It would **not** satisfy
  this control if a tool description were ever read from a Registry record at runtime, which is
  the catalog-as-supply-chain case ADR-007 requires be amended before it is introduced.
- No principal, binding, endpoint, token, or finding appears in this capture. Tool names are
  repository-owned identifiers.

```powershell
pytest tests/security/test_tool_surface.py -v
```
