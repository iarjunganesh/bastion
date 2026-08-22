# Observation backlog

**Status:** opened 2026-08-16. Every deterministic engineering item is closed in
[08-audit-remediation-plan.md](08-audit-remediation-plan.md); what remains here is *observation*
— capabilities that are deployed and tested but have not been watched working and recorded.

This distinction is the project's own standard, not bookkeeping. [ADR-006](../../docs/adr/006-pillar-coverage.md)
holds that a pillar closes only when implementation, deployment, and an observable proof agree,
and [SUBMISSION.md](../SUBMISSION.md)'s checkbox convention means *observed*, not *built*. A
capability with code and no capture is deliberately not claimed.

## Why this file exists

The backlog previously lived only in an untracked scratch file. A record of outstanding work that
is itself untracked is the failure mode this repository argues against, and one correction below
(the exception store) had already been lost once that way.

## Correction carried forward

**The cross-week continuity seed targets Firestore, not Memory Bank.** Approved exceptions are
held in the `bastion_exceptions` collection — see `runtime/firestore.py` and the
`approved_exception()` call in `agents/orchestrator/agent.py`. `VertexAiMemoryBankService` in
`agents/orchestrator/runtime.py` backs managed *session* memory, which is a different store.
Seeding Memory Bank would produce a capture that proves nothing about suppression.

## Open captures

Each needs live GCP credentials and an approved operator workstation. None is a build task.

| # | Capture | Depends on | Note |
|---|---|---|---|
| 1 | An approved exception seeded, then a later matching finding suppressed after a real elapsed gap | Firestore seed, see correction above | The only item whose critical path is elapsed time rather than effort; it cannot be compressed by working harder |
| 2 | Model Armor refusing through an agent's `before_model_callback`, not the direct `screen_prompt` probe | Deployed Runtime | [Evidence 01](../../assets/evidence/01-model-armor-block.md) states plainly that it is not an agent-mediated trace |
| 3 | One investigation's reasoning chain in Cloud Trace | Deployed Runtime | `enable_tracing=True` is configured; configuration is not a capture |
| 4 | Structured audit logs correlated by context ID for that same run, **including a refusal** | Capture 3 | A trail of successes proves nothing about the guardrails |
| 5 | The redacted real-IAM basis for the findings, from the current route | — | [Evidence 02](../../assets/evidence/02-gemini-investigation.md) is labelled historical and pre-Gateway |
| 6 | Gateway refusals: unregistered caller, undeclared skill, rate limit | Decision below | Two are asserted offline in `tests/security/test_gateway_policy.py`; the third has no implementation |
| 7 | A worker timing out, retrying, then escalating | Deployed Runtime | Retry is deployed and suite-tested; the sequence has not been watched end to end |

## Open decision

**Rate limiting does not exist anywhere in the codebase.** It is absent, not stale — no
`gateway/`, `registry/`, or agent module implements it. Three ways forward, and the choice
belongs to the platform owner:

1. Rely on the managed Gateway/IAP quota surface and capture whatever it actually enforces.
2. Drop the third refusal and claim two, which the deterministic policy already supports.
3. Implement it locally — but weigh this against ADR-003's no-reimplementation rule before
   hand-rolling a limiter that a managed product may already provide.

Deciding after the capture attempt rather than before is how a claim ends up written to fit
whatever happened to be observable.

## Closing rule

Nothing here may be marked closed in [SUBMISSION.md](../SUBMISSION.md) on the strength of a
passing test. A test proves the logic; the capture proves the deployed system did it. Where only
one exists, say which — as [evidence 08](../../assets/evidence/08-tool-poisoning.md) does for the
tool boundary, and as [ADR-006](../../docs/adr/006-pillar-coverage.md) does for Memory Bank.
