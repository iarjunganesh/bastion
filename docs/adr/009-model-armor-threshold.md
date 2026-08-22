# ADR-009: The Model Armor threshold is `MEDIUM_AND_ABOVE`, and it is not the lever

**Status:** Accepted 2026-08-19
**Traces to:** [ADR-003](003-pillars-on-geap.md), [ADR-007](007-tool-poisoning.md)

## Decision

The `bastion-guardrail` prompt-injection filter enforces at `MEDIUM_AND_ABOVE`, with enforcement
`ENABLED`. The configuration lives in [`model_armor/template.py`](../../model_armor/template.py),
is applied by provisioning, and is gated by `verify_fleet`.

`HIGH` was tried and reverted. It is recorded here because the negative result is the useful part.

## Context

The template was deployed at `LOW_AND_ABOVE`. Model Armor fails closed by design, so a flagged
prompt is a refused model call — and at that setting every agent was refused. The fleet produced
no model output, made no tool calls, raised no findings, and wrote no escalation. Investigations
reached `completed` in roughly forty seconds having done nothing, which is why the failure
survived unnoticed: the durable lifecycle reported success while the work never happened.

This was found by trying to seed the cross-week exception ledger and discovering there was
nothing to approve. No test could have caught it — the suite exercises the callback's logic, and
the logic is correct. What was wrong was a threshold in a console.

## Measurement

Screened against the live template rather than reasoned about:

| Prompt | Detection confidence |
|---|---|
| The injection probe from [evidence 01](../../assets/evidence/01-model-armor-block.md) | `HIGH` |
| `access_auditor` instruction (repository-owned) | `LOW` |
| The fleet's internal A2A hand-off | `HIGH` |
| `escalation_agent` instruction, investigation envelope, benign control | no detection |

The investigation envelope was screened across thirty freshly generated instances and never
matched, so the false positive is not classifier instability.

Raising the threshold to `HIGH` was expected to clear the Auditor while still refusing the
injection. **It did not.** The Auditor was refused at `HIGH` exactly as at `MEDIUM_AND_ABOVE`,
which establishes that the internal hand-off scores at the same confidence as a genuine
injection. That is not a tuning problem. To the classifier, a message that instructs an agent
what to do is a prompt injection, because structurally that is what it is — the difference is
provenance, which a content classifier cannot see.

The threshold is therefore not the lever, and `HIGH` was reverted: it traded sensitivity for
nothing.

## What the hand-off is

Unidentified. It is 159 characters in a single part, stable in length across runs with a digest
that changes per run, and reproduces as neither the investigation envelope, nor ADK's wrapped
trigger message, nor any repository-owned string — every serialization of the stored event was
brute-forced against a digest of the screened text and none matched. It is generated inside the
deployed A2A path. Identifying it needs a local reproduction of that path, which has not been
done.

## Rationale for the setting that remains

- **`MEDIUM_AND_ABOVE` over `LOW_AND_ABOVE`:** `LOW` additionally refused the agents' own
  repository-owned instructions, which is a strictly larger false-positive surface for no gain.
- **`MEDIUM_AND_ABOVE` over `HIGH`:** `HIGH` fixes nothing here and detects less. There is no
  argument for it once the fleet is refused either way.
- **Enforcement stays on.** The threshold moves; the filter is not disabled.

## Consequences

- **The Access Auditor is still refused, and the fleet still cannot complete an investigation.**
  This ADR does not claim to have fixed that. The remaining fix is to narrow *what* is screened
  — internal orchestration between repository-owned agents is not the untrusted surface the
  control exists for — rather than to keep moving a threshold.
- Narrowing the screening surface is a security change in its own right and needs its own record,
  including what stops being screened and why that is not where injection enters.
- The tuning rests on one probe plus the fleet's own traffic. A corpus of injection variants —
  indirect, role-play, incremental — screened against the live template would make the choice
  evidential rather than anecdotal.
- `tests/security/test_model_armor_template.py` pins threshold and enforcement; `verify_fleet`
  fails when the deployed template drifts, including when it becomes unreadable, which under
  fail-closed screening is equally fatal.

## Not claimed

That the guardrail is correctly tuned — it refuses legitimate traffic today. That Model Armor
prevents tool poisoning; [ADR-007](007-tool-poisoning.md) is explicit that the fixed tool
boundary does that. That raising or lowering this threshold would make the fleet work.
