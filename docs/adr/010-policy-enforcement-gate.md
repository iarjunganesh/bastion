# ADR-010: Deterministic policy enforcement is gated, not merely intended

**Status:** Accepted 2026-08-22
**Traces to:** [ADR-002](002-three-agents.md), [ADR-007](007-tool-poisoning.md), [ADR-009](009-model-armor-threshold.md)

## Decision

`apply_policy_rules` writes its result into session state, and a deterministic
`PolicyEnforcementGate` step between `policy_step` and the Escalation Agent refuses to continue
when that record is absent or malformed. A missing decision now fails the investigation closed
instead of allowing it to escalate.

## Context

`policy_step` is an `LlmAgent` whose `apply_policy_rules` and `route_by_department` tools are
reachable **only through a model call**. When `before_model_callback` refuses — which
[ADR-009](009-model-armor-threshold.md) records as the fleet's standing condition inside the
Agent Runtime — the model never runs, so neither tool ever executes.

Nothing noticed. The `SequentialAgent` moved on to the Escalation Agent, which read the
Auditor's output independently, and humans were paged about findings that no threshold had ever
been applied to. `investigation.run` recorded `completed` and no error was written anywhere.

Observed twice in production on 2026-08-21 (16:27:49Z and 16:34:49Z): `policy_step` refused,
tools skipped, `notify_human` delivered twice, investigation `completed`.

This inverted the project's own rule that missing or malformed risk fails closed. Enforcement
did not fail closed — it *disappeared*, and disappearance is indistinguishable from success in
every artifact the system produces. That is the worst available failure mode for a compliance
control: the audit trail asserts a review happened.

## Why the evidence is the tool's, not the step's

The obvious gate — "is `policy_decisions` populated?" — does not work. When the callback
refuses, ADK still stores the refusal text under the step's `output_key`, so the slot is
occupied by prose reading "This input was blocked by Model Armor." A gate that accepted any
non-empty state would wave through exactly the case it exists to catch.

So the deterministic tool records its own result under a separate key. That evidence can only
be produced by the code path that actually applies the threshold. `tests/unit/test_orchestrator.py`
pins both halves: the tool writes the record, and the gate rejects model prose in its place.

## Why a step and not a check inside the Escalation Agent

The Escalation Agent is remote over A2A. A guard that travels to the callee is a guard the
caller must trust the callee to run, and the Orchestrator cannot verify that it did. Keeping
the gate in the Orchestrator keeps policy enforcement where [ADR-002](002-three-agents.md) put
it — in-process, in the agent that owns the decision.

The gate is **not a fourth agent**. It has no model, no instruction and no tools; it is a
deterministic step in the Orchestrator's own sequence. The fleet is still three agents.

## Consequences

- An investigation whose policy step was screened out now **fails** rather than escalating. That
  is louder and correct: a failed investigation is visible and retryable.
- **This does not fix the underlying screening outage.** The Runtime's Model Armor egress is
  still denied (see the observation backlog, D2). The gate converts a silent wrong answer into
  a visible failure; it does not make the fleet work.
- Cross-week suppression still cannot be demonstrated while the policy step cannot run, because
  suppression is a decision that step makes.
- The Auditor's findings still cross the A2A boundary as **model prose**, so the policy tool
  reconstructs risk scores and opaque ids from a sentence. The gate proves the tool ran; it
  cannot prove the tool was given faithful input. That is a separate defect and needs its own
  record.

## Not claimed

That policy enforcement now runs in production — it does not, because screening still refuses.
That the gate validates the *content* of a decision; it validates that the deterministic path
produced one. That a failed investigation is retried automatically beyond the Eventarc policy
already in place.
