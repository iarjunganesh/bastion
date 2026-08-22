# ADR-012: The Auditor answers in a schema, and the policy step holds no model

**Status:** Accepted 2026-08-22
**Traces to:** [ADR-001](001-real-iam-not-mock-data.md), [ADR-002](002-three-agents.md), [ADR-007](007-tool-poisoning.md), [ADR-010](010-policy-enforcement-gate.md)

## Decision

The Access Auditor declares an `output_schema`, so its findings cross the A2A boundary as
validated structured data rather than prose. `policy_step` is no longer an `LlmAgent`: scoring
and routing run as plain Python in the Orchestrator's own sequence.

## Context

`audit_iam_policy` is deterministic — [ADR-001](001-real-iam-not-mock-data.md) makes detection
plain Python precisely so that a compliance product never answers *"why was this flagged?"* with
*"the model thought so"*. But the agent's `output_key` stored the **model's prose**, and the
policy step then asked a second model to reconstruct a findings list from those sentences before
handing it to the threshold.

So the deterministic guarantee ended at the tool boundary. Every opaque id, risk category and
score that policy actually applied had been retyped by a language model in between. The
repository said models do not decide whether IAM is safe; the running system had two of them in
the path.

Three observed symptoms were the same defect:

- **`notify_human` failing intermittently** with `UnsafeRiskCategoryError` — the model had
  produced a category outside the deterministic reason codes. The allowlist was working; the
  input to it was fabricated.
- **Cross-week suppression that could not have worked reliably.** An approved exception is keyed
  by a 24-hex finding id. Suppression required a model to reproduce that id character-perfect
  from a sentence it had written earlier.
- **Enforcement skipped entirely** when Model Armor refused the policy model's call
  ([ADR-010](010-policy-enforcement-gate.md)).

## Why removing the model is the fix, not a shortcut

There was never a decision at this step for a model to make. The threshold is a constant,
ownership comes from a catalog, and both were already tools *specifically* so they could not be
argued with ([ADR-007](007-tool-poisoning.md)). A model that cannot alter the outcome but can
corrupt the input is pure liability.

Removing it has a second effect worth naming: a step that makes no model call needs no
screening, so the policy path no longer depends on Model Armor egress from the Agent Runtime,
which is denied (observation backlog, D2). That is a consequence of the right design, not the
reason for it.

The tool boundary is not weakened by having no tools. `policy_step` declares none because it
reaches no model — there is nothing left for a poisoned instruction to talk it into.
`tests/security/test_tool_surface.py` asserts that rather than exempting the step.

## What the schema enforces

`AuditReport` constrains what a model is able to say at all: `finding_id` must match
`^[0-9a-f]{24}$`, `reason` must be one of the three deterministic codes, `risk_score` must lie in
`[0, 1]`. A model that embellishes now produces a validation failure instead of a plausible
finding. The model still writes the `rationale`, which is the one field where prose is the point.

A missing or misshapen report raises rather than scoring an empty list: clearing an investigation
that never looked is the same fail-open shape [ADR-010](010-policy-enforcement-gate.md) exists to
catch. A genuinely clean run returns an empty `findings` list and is scored normally.

## Consequences

- The reasoning chain has one fewer model call. The trace is shorter, and what remains is the
  part where a model adds value: the Auditor's rationale and the Escalation Agent's routing.
- ADK enforces `output_schema` at the model layer, so this cannot be fully proven offline. The
  suite pins the schema, the deterministic step and every fail-closed path; **that the deployed
  Gemini call honours the schema is verified in the deployed fleet, not here.**
- `notify_human`'s arguments still originate from the Escalation Agent's model. The values it
  copies are now deterministic and validated upstream, which removes the observed failure's
  cause, but the last hop is still a model copying values. Closing that is separate work.

## Not claimed

That no model touches finding data anywhere — the Auditor's model still emits the structured
report, and the Escalation Agent's still fills in tool arguments. That suppression has been
observed working; the defect that made it unreliable is fixed, and the capture is still open.

## Amendment 2026-08-22 — the schema is also what makes the A2A reply readable

Deploying this exposed a second defect the schema turned out to solve. `output_key` writes into
the session of the agent that declares it, so the Auditor's `audit_findings` landed in the
*worker's* session and never crossed back. Every local run and every test saw a populated key,
because in-process the declaring agent and the reading agent share one session; the deployed
Orchestrator saw nothing and refused.

`policy_step` now reads the Auditor's A2A reply when the state key is absent. That is only
defensible because of the decision recorded above: with `output_schema` the reply is validated
`AuditReport` JSON, so reading it is parsing, not interpreting. Without the schema this fallback
would have meant a deterministic step scraping findings out of prose — which is the exact failure
this record exists to prevent, reintroduced at a different layer. A reply that does not parse is
skipped, and skipping everything fails closed.
