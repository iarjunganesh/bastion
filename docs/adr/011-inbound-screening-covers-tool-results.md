# ADR-011: Inbound screening covers tool results, not only prompt text

**Status:** Accepted 2026-08-22
**Traces to:** [ADR-003](003-pillars-on-geap.md), [ADR-007](007-tool-poisoning.md)

## Decision

`screen_before_model` screens `function_response` parts as well as `text` parts. Both directions
of the Model Armor callback pair now read the same content.

## Context

`screen_before_model` joined only `part.text`. `screen_after_model` already read
`function_response` parts as well. The asymmetry meant a tool result re-entered the model
**without ever passing an inbound screen** — outbound was guarded, inbound was blind.

This was not theoretical. `apply_policy_rules` returns `exception_policy_version` inside its
result: a 1-64 character operator-supplied string that arrives through the findings API, is
stored in the exception ledger, and is copied into the tool's return value. It reaches the
policy model as a `function_response` part, which nothing screened.

The brief that this fleet answers names **tool poisoning** as one of three threats.
[ADR-007](007-tool-poisoning.md) holds that the fixed per-agent tool allowlist is the control
for a poisoned tool *declaration*, and that remains true. But a poisoned tool *result* is a
different surface, and it was the one flowing unscreened.

## Consequences

- The screened surface grows: every tool result is now classified before the model sees it. On
  the Cloud Run workers, where screening works, this is additional latency per tool call.
- More screened content means more opportunity for the false positives
  [ADR-009](009-model-armor-threshold.md) documents. The threshold is unchanged; if tool results
  begin matching, that is a tuning problem to measure rather than a reason to narrow the surface
  back to where the gap was.
- The audit `shape` fields (`screened_chars`, `screened_parts`) now count tool results too, so
  the two numbers continue to describe the same screen. Sizes remain shape, never content.

## Not claimed

That Model Armor prevents tool poisoning — [ADR-007](007-tool-poisoning.md) is explicit that the
fixed tool boundary does that, and screening a result does not stop a tool from being called.
That this closes every unscreened path into a model; it closes the one that was found and
verified by reading the request the callback receives.
