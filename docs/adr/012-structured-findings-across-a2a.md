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
  **Closed 2026-08-23 by P0.2 — see the amendment below.**

## Not claimed

That no model touches finding data anywhere — the Auditor's model still emits the structured
report, and the Escalation Agent's still fills in tool arguments. That suppression has been
observed working; the defect that made it unreliable is fixed, and the retained observation is
[evidence 10](../../assets/evidence/10-cross-week-suppression.md).

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

## Amendment 2026-08-23 — schema-valid was never the same claim as faithful (P0.1)

The schema constrains *shape*: a fabricated id cannot match `^[0-9a-f]{24}$`, an invented reason
cannot match the enumeration, an adjusted score cannot leave `[0, 1]`. Nothing above stopped a
model from returning a schema-valid `AuditReport` that dropped a finding, added a plausible one,
or nudged a real finding's score or department — every value still validated, none of it checked
against what `audit_iam_policy` had actually found.

`agents/access_auditor/agent.py` now closes that gap at the model layer itself.
`persist_canonical_findings`, an `after_tool_callback`, records the tool's real answer under its
own state key (`CANONICAL_FINDINGS_KEY`) the moment the tool returns — not by changing
`audit_iam_policy`'s body, which stays zero-argument for the same ADR-007 reason it always was.
`validate_auditor_fidelity`, chained after `screen_after_model` in `after_model_callback`, then
compares the model's final structured answer against that canonical list by `finding_id`:
the id set must match exactly (no addition, omission, or duplicate), `department`, `reason` and
`risk_score` must be copied verbatim, and the reported `count` must equal the list it describes.
Only `rationale` is the model's to write. Any mismatch raises `AuditorFidelityError` from the
callback — the same fail-visibly shape as `PolicyNotEnforcedError` downstream — after one
payload-free audit record naming a bounded reason code, never a finding value.

The canonical state never leaves the Auditor's own session: it is written to `tool_context.state`,
which — like `audit_findings` before it — does not cross the A2A hop, so there is nothing here for
`observability.audit`'s payload-free rule to guard against by policy alone; the transport already
guarantees it.

## Amendment 2026-08-23 — the last hop stopped being a model copying values too (P0.2)

The "Consequences" section above named the remaining gap precisely: `notify_human`'s arguments
still originated from the Escalation Agent's *model*, which could skip a routed department, pick
a different one, fabricate a schema-valid opaque id, or finish without the required call while
the sequence still reported success.

`agents/escalation_agent/agent.py` replaces that `LlmAgent` with a deterministic `BaseAgent`,
`EscalationAgent`. It reads the routing envelope `policy_step` already produced — from shared
session state in-process, or from the inbound A2A message's content when deployed, the same
content-not-state lesson `policy_step`'s own routing already had to learn — validates every
department bucket completely (department id, opaque finding ids, allowlisted risk categories,
and that the count matches the ids it claims to summarise) before calling `notify_human` for any
of them, then calls it exactly once per bucket. A validation failure or a delivery failure both
raise out of the method uncaught, which fails the remote A2A task and the investigation with it —
the same visible, retryable shape `PolicyEnforcementGate` already gives a skipped policy step.
`notify_human`'s existing idempotency key makes a retry safe rather than a duplicate human-review
record.

The Escalation Agent now holds no tool declaration, no model, and no Model Armor callback: the
same class of "no tool surface to poison" guarantee `policy_step` already had
([tests/security/test_tool_surface.py](../../tests/security/test_tool_surface.py)) extends to the
worker that used to be this ADR's one remaining model-in-the-loop hand-off. "Three institutional
agents" still names the fleet correctly — ADR-002 already settled that a worker's institutional
identity and IAM boundary define an agent, not whether a model runs inside it, and
`escalation-agent-sa`'s no-IAM-read denial is unchanged.

## Amendment 2026-08-23 — content crosses the hop, but not verbatim (a third A2A surprise)

Deploying the two amendments above exposed a defect neither anticipated. Every deployed
investigation after P0.2 shipped failed at the Escalation Agent with a new, deterministic,
payload-free refusal: `escalation.envelope rejected reason=missing_routing_envelope`. This was
not a repeat of D6/D8 — the content genuinely arrived — and it was not a state-crossing question
at all, which is why the first fix attempt (reading `InvocationContext.user_content`, the correct
callee-side channel for "what was I asked this turn," in place of scanning session history) still
failed the same way.

Diagnostic logging of the actual `user_content.parts` (structure only, standard practice for a
production incident, though see the note below) showed the routing JSON present but not as bare
text. ADK's A2A layer flattens a multi-hop conversation into attributed lines when it builds the
next hop's request — `policy_step`'s content arrived as `"[policy_step] said: {...}"`, with a
literal `"For context:"` line before it — rather than forwarding the prior turn's content
byte-for-byte. A bare `json.loads` on that text raises, and the code that existed at the time
caught the exception and moved on to the next part, which read as "no routing envelope" rather
than "found one, wrong shape."

`_parse_json_object` in `agents/escalation_agent/agent.py` now strips a `^\[[^\]]*\]\s*said:\s*`
prefix before parsing when bare JSON fails, so the fidelity check finds the envelope whether it
arrives verbatim (in-process) or attributed (deployed). This is content-shape tolerance, not a
new trust boundary: the envelope is still validated field-by-field once parsed, exactly as before.

Two things compounded this into a `completed`-not-`failed` investigation before either fix
landed, worth recording because they are as reusable as the fix itself:

- **A raised exception inside a deployed A2A worker does not reach the caller as a Python
  exception.** `RemoteA2aAgent` converts a failed remote task into an ordinary, contentless
  `Event` — no `error_message`, no `error_code` — because `convert_a2a_task_to_event` only
  copies a task's status message into event content for the `INPUT_REQUIRED`/`AUTH_REQUIRED`
  states, not `FAILED`. The failure reason this worker raised and audit-logged locally never
  reaches the Orchestrator's own process at all.
- **Updating the four Cloud Run services with `deploy.sh` does not redeploy the Orchestrator's
  agent graph.** `policy_step`, `policy_gate`, `escalation_agent`, and the new `escalation_gate`
  all run inside the managed Agent Runtime (a Vertex AI Reasoning Engine), a separate deployment
  surface (`infrastructure.deploy_agent_runtime`, documented in `CLAUDE.md`). Until that ran,
  `escalation_gate` was not part of the live graph at all — the Runtime was still executing the
  pre-P0.3, four-step sequence, so there was nothing downstream to catch the swallowed failure
  above and the sequence simply reported `completed`.

Together these meant the *first* deployed regression was invisible by two independent
mechanisms, not one: content that should have failed loudly instead evaporated at the transport
layer, and the one step built specifically to catch a silent gap like this was not yet running.
Both are now closed — `escalation_gate` is live and confirmed passing
(`agent.run completed escalation_gate`, observed 2026-08-23) — but the transport-level swallowing
of `TS_FAILED` task messages is an ADK behavior, not something this repository's code controls,
and is recorded here as a live risk rather than something the fix above resolved.

A note on the diagnostic itself: it logged full `user_content` part contents (department names,
finding rationale text, JSON structure) to the retained audit sink at `outcome: "debug"` for the
minutes it took to find this. No principal, binding, or credential was in that content, but it
was still model/tool-adjacent text in a channel this codebase otherwise keeps payload-free by
construction — an accepted, bounded exception for live incident diagnosis, not a precedent.

## Upstream contribution status (checked live 2026-08-23)

- Issue [google/adk-python#6854](https://github.com/google/adk-python/issues/6854), opened by
  Arjun Ganesh: **open**. Documents both directions of the state-crossing defect above with a
  production reproducer, root cause, and proposed warnings/documentation.
- PR [google/adk-python#6859](https://github.com/google/adk-python/pull/6859), authored by
  Sylvester Kaczmarek: **open, not merged**. Adds warnings for the outbound state-only-loss
  direction and the rejected inbound remote-state-delta direction, plus tests and docs.
- PR [google/adk-python#6862](https://github.com/google/adk-python/pull/6862), authored by Arjun
  Ganesh: **open, not merged**. Adds the complementary construction-time warning for the adjacent
  `LlmAgent(output_key) -> RemoteA2aAgent` case, which carries event content and is not covered
  by the state-only warning.
- The third finding recorded in this amendment set — attributed-history wrapping breaking a
  bare-JSON parse on the callee side of a hop, and a failed remote task reaching the caller as an
  empty, error-free event — has not been filed upstream. It is a live risk, documented here, not
  yet a reported one.

None of the three items above should be described as accepted, merged, or resolved by Google
until this status is re-checked immediately before publication (`gh pr view --repo
google/adk-python <number>`, or the corresponding issue command).
