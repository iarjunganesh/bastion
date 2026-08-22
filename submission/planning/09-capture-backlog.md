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
| 2 | Model Armor refusing through an agent's `before_model_callback`, not the direct `screen_prompt` probe | Deployed Runtime, D2 | Achievable through the A2A body, which is a real untrusted surface — see the scope note below |
| 3 | One investigation's reasoning chain in Cloud Trace | Deployed Runtime | `enable_tracing=True` is configured; configuration is not a capture |
| 4 | Structured audit logs correlated by context ID for that same run, **including a refusal** | Capture 3 | A trail of successes proves nothing about the guardrails |
| 5 | The redacted real-IAM basis for the findings, from the current route | — | [Evidence 02](../../assets/evidence/02-gemini-investigation.md) is labelled historical and pre-Gateway |
| 6 | Gateway refusals: unregistered caller, undeclared skill, rate limit | Decision below | Two are asserted offline in `tests/security/test_gateway_policy.py`; the third has no implementation |
| 7 | A worker timing out, retrying, then escalating | Deployed Runtime | Retry is deployed and suite-tested; the sequence has not been watched end to end |

## Scope note on capture 2

An earlier working assumption held that the fleet has **no** untrusted-input route to a model, and
that capture 2 was therefore unachievable without building a target to attack. That assumption was
wrong, and it was nearly written up as a claim.

What is true is narrower and still worth stating: the *IAM findings path* carries no
attacker-controlled text to a model. `fetch_iam_policy` copies only `role` and `members` from each
binding — a binding's `condition`, whose `title`/`description`/`expression` are free text settable
by anyone able to create the binding, is never read. The Auditor's tool emits an opaque 24-hex id,
a closed-set department, a fixed reason code and a fixed score. That is data minimisation working,
and it is the honest version of the original claim.

But two free-text routes to a model do exist:

1. **The A2A message body.** Both worker services carry an `allUsers` Cloud Run invoker binding
   (documented in [SECURITY.md](../../SECURITY.md)); the only gate is the origin secret checked by
   `install_peer_origin_auth`. An A2A body is unbounded text, arrives as a `.text` part, and *is*
   screened by `screen_before_model`. This is a genuine deployed surface, so capture 2 needs no
   decoy input field. It demonstrates a **compromised authorized caller**, not an anonymous
   attacker, and the write-up must say so.
2. **`exception_policy_version`.** An operator-supplied 1-64 character string reaches the policy
   model inside a tool result — and is *not* screened on the way in. See D4.

**What must be said plainly when capture 2 is written up:** every refusal observed in the deployed
fleet so far has been a false positive on the fleet's own traffic (`policy_match` on internal
orchestration text, `screening_unavailable` on the D2 egress denial). No refusal of a real
injection has been observed. Route 1 makes one obtainable; until it is captured, it is not claimed.

## Blocking defects observed in the deployed fleet

Found 2026-08-19/22 while attempting captures 1-4. Each was watched in the deployed system, not
inferred from code. They are recorded here because all four open captures sit behind them.

**Status at 2026-08-22:** D1, D3, D4, D5, D6 and D7 are fixed and shipped in 0.2.0. Only D2
remains open, and it is no longer blocking. D1, D3 and D6 are additionally **observed**: a live
investigation completed end to end at 16:49Z with 34 audit records under a single
`investigation_id` across the Runtime and both workers, and `smoke_test` passes.
What is still not observed is a **refusal** on that route, so capture 4 stays open — a trail of successes
proves nothing about the guardrails.

### D1. Deterministic policy enforcement does not run, and does not fail closed

**Fixed 2026-08-22** — see [ADR-010](../../docs/adr/010-policy-enforcement-gate.md) and
[ADR-012](../../docs/adr/012-structured-findings-across-a2a.md). Both halves are closed. An
earlier revision of this entry said only the fail-open half was fixed and that the step still
could not run because D2 was unresolved. That is no longer true, and the reason is worth stating:
the step was made deterministic, so it no longer needs the screening that D2 denies.

`policy_step` was an `LlmAgent` whose `apply_policy_rules` and `route_by_department` tools were
reachable **only through a model call** (`agents/orchestrator/agent.py`). Its
`before_model_callback` refused, so the model never ran and neither tool ever executed. It is now
a `BaseAgent` that calls both directly. Because it reaches no model it needs no screening, which
takes this path off the blocked egress as a consequence of the design rather than as a workaround
for it. `policy_gate` refuses to escalate unless the deterministic path left its own result in
state, so the fail-open shape below cannot recur even if the step were to fail some other way.

Observed end to end on 2026-08-21 (two runs, 16:27:49Z and 16:34:49Z): `policy_step` was refused,
its tools did not run, and the investigation **continued to escalation anyway** — `notify_human`
delivered twice and `investigation.run` reported `completed`. No error was recorded.

This inverts the project's own rule that missing risk fails closed. Enforcement does not fail
closed; it disappears, and the finding escalates un-evaluated while the lifecycle reports success.
`CLAUDE.md`'s "policy enforcement remains deterministic inside Orchestration" is true of the code
and **not true of the deployed system**.

### D2. Model Armor screening is unavailable inside the Runtime because its egress is denied

**Still open at 2026-08-22.** No longer blocking: the only Runtime-side step that depended on
screening was `policy_step`, which now reaches no model at all (D1). Screening remains live on
both Cloud Run workers, which is where the untrusted input actually arrives. What is lost while
this is open is defence in depth on the Runtime, not an enforced control — and nothing in the
0.2.0 release notes claims otherwise.

Every `screening_unavailable` originates from the Agent Runtime; every successful `policy_match`
originates from a Cloud Run worker. The cause is direct rather than a chain: the exact call
`screen_prompt` makes —
`modelarmor.<region>.rep.googleapis.com/google.cloud.modelarmor.v1.ModelArmor/SanitizeUserPrompt`
— is refused at IAP egress, 16ms before each refusal is recorded.

IAP resolves the destination to `unregisteredEndpoint` and denies
`iap.webServiceVersions.egressViaIAP`, **despite** the endpoint being registered in the Gateway's
bound registry with that exact URL, and despite the Runtime's Agent Identity holding
`roles/iap.egressor` at project level. Of every IAP authorization event in a seven-day window,
none was granted. Only non-standard hostnames (mTLS and regional `.rep`) are IAP-mediated at all;
plain `*.googleapis.com` hosts are never checked.

Ruled out by experiment: registering the endpoints in the `global` Registry location (the Gateway
binds only to its regional registry — reverted), and rebinding the interfaces from `GRPC` to
`HTTP_JSON`. The denial log carries **no `authenticationInfo`**, which is consistent with the
workload's Agent Identity not being attached to the outbound call.

### D3. An audit trail cannot be assembled into one investigation

**Fixed 2026-08-22.** Every audit record now carries `investigation_id`, seeded from the durable
event at dispatch and forwarded to each worker as A2A request metadata. Capture 4 has a field to
assemble on; whether the deployed trail actually assembles is the capture, not this fix.

Audit records carried `invocation_id` and no `context_id`. `invocation_id` is minted per agent
run, so one investigation yielded several — one for the Runtime graph and one for each A2A worker
— and tool records sat under the worker's id. Capture 4 was not merely unobserved; there was no
field by which it could be assembled. See the corrected docstring in `observability/audit.py`,
which had claimed `invocation_id` grouped an investigation when it groups one agent run.

`event_id` is the correlation key rather than `context_id`: `InvestigationEvent` validates it as
a UUID while `context_id` is only checked non-empty, and this value crosses A2A from a peer into
a 365-day retained bucket. The audit boundary re-validates the shape and records `unknown` rather
than writing arbitrary text through.

### D4. Inbound screening skips tool output

**Fixed 2026-08-22** — see [ADR-011](../../docs/adr/011-inbound-screening-covers-tool-results.md).
`screen_before_model` now reads `function_response` parts, matching what `screen_after_model`
already did.

`screen_before_model` joins only `part.text`, while `screen_after_model` also reads
`function_response`. Tool results therefore re-enter the model without inbound screening. This is
not hypothetical: `apply_policy_rules` returns `exception_policy_version`, an operator-supplied
1-64 character string from the findings API, inside its result. The asymmetry matters for a
threat model that names tool poisoning.

### D5. The deployed Runtime was six days stale

**Fixed 2026-08-22.** Redeployed in place; `updateTime` 2026-08-22T08:10:24Z. Confirmed live
rather than assumed: refusals now carry the `screened_chars` field that only exists in the
2026-08-19 commits.

The Agent Runtime's `updateTime` was 2026-08-15T23:59Z while nine remediation commits landed on
2026-08-19. Its refusals carried none of the instrumentation added in those commits. Any capture
taken before a redeploy would have described code that is not in the repository.

### D6. Investigations sometimes truncate after the Auditor

**Fixed and observed 2026-08-22.** Cause: `output_key` writes into the session of the agent
that declares it, so the Auditor's `audit_findings` landed in the *worker's* session and never
crossed back. Every local run and every test saw a populated key, because in-process the
declaring and reading agents share one session. `policy_step` now reads the Auditor's
validated A2A
reply when the state key is absent; a live investigation then completed end to end.

Observed 2026-08-21T16:36Z:

### D7. A declared-but-empty environment variable is not treated as absent

`os.environ.get(key, default)` returns `""` for a variable that is present and empty, so a
deployment declaring `BASTION_INVESTIGATION_LEASE_SECONDS=` reached `int("")` and failed on its
first delivery rather than at startup. The same shape defeated `os.environ.setdefault` in the
test bootstrap, which is why nine tests failed for anyone who exported `.env` before running the
suite while CI — which exports nothing — stayed green.

**Fixed 2026-08-22.** The lease parse and the test bootstrap both treat empty as absent, and the
suite now passes identically with and without `.env` exported.

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
