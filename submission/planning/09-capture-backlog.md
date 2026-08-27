# Observation backlog

**Status:** opened 2026-08-16. Every deterministic engineering item is closed in
[08-audit-remediation-plan.md](08-audit-remediation-plan.md); what remains here is *observation*
— capabilities that are deployed and tested but have not been watched working and recorded.

This distinction is the project's own standard, not bookkeeping. [ADR-006](../../docs/adr/006-pillar-coverage.md)
holds that a pillar closes only when implementation, deployment, and an observable proof agree,
and [SUBMISSION.md](../SUBMISSION.md)'s checkbox convention means *observed*, not *built*. A
capability with code and no capture is deliberately not claimed.

## Carried in from `v0.6.0` — the repository moved and the deployment did not

**Both surfaces still run the `google-adk` 2.7.1 resolution `v0.4.0` deployed; the repository now
pins 2.8.0.** This is not an observation gap in the usual sense — the capability is not merely
unwatched, the deployment is a release behind the tree that describes it. It sits here because the
consequence is observational: redeploying mints new Cloud Run revisions, and
[evidence 11](../../assets/evidence/11-current-route-correlation.md) and
[12](../../assets/evidence/12-agent-mediated-model-armor-refusal.md) name
`bastion-access-auditor-00031-sbr` and `bastion-escalation-agent-00027-nkv` explicitly.

Closing it therefore means, in order: redeploy both surfaces, re-verify live, re-run the
investigation, re-capture evidence 11, 12 and 13, and recompose gallery images 03, 04 and 05 from
the new captures. Nothing may claim production runs the newer resolution until that is done.

The alternative is equally acceptable and costs nothing: leave the fleet where it is and say so,
which is what every current claim already does.

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
| 1 | ~~An approved exception seeded, then a later matching finding suppressed after a real elapsed gap~~ | — | **Closed 2026-08-22, re-confirmed 2026-08-23** — [evidence 10](../../assets/evidence/10-cross-week-suppression.md). Approved 08-19, suppressed 08-22; `notify_human` fired once and the owning department was not paged. Re-run 08-23 against the same still-valid exception after the P0.1–P0.3 deterministic-delivery rewrite: identical result, queried directly from `bastion_human_review` rather than inferred. |
| 2 | ~~Model Armor refusing through an agent's `before_model_callback`, not the direct `screen_prompt` probe~~ | — | **Closed 2026-08-25** — [evidence 12](../../assets/evidence/12-agent-mediated-model-armor-refusal.md). The approved injection sample was sent to the deployed Auditor's authenticated A2A surface: a benign control completed, the sample's task failed closed with `model_armor.input` / `refused` / `policy_match`, and zero model submissions, completions or tool calls followed. This is a compromised authorized caller, not an anonymous one. |
| 3 | ~~One investigation's reasoning chain in Cloud Trace~~ | — | **Closed 2026-08-25** — [evidence 13](../../assets/evidence/13-current-route-trace.md). One connected 22-span trace over 1m 5.401s covers the managed Runtime, both A2A hops with their agent-card fetches, the Firestore exception lookup nested inside `policy_step`, and `escalation_gate`. D2's feared trace impairment did not materialise on this route. |
| 4 | ~~Structured audit logs correlated by context ID for that same run, **including a refusal**~~ | — | **Closed 2026-08-25, with a stated boundary** — [evidence 11](../../assets/evidence/11-current-route-correlation.md) assembles 28 unique payload-free events across three invocation ids under one investigation id, and [evidence 12](../../assets/evidence/12-agent-mediated-model-armor-refusal.md) supplies a refusal recorded under the same audit contract. The refusal comes from a separate probe, not from the correlated run itself, so the guardrail trail is observed but the two are not one investigation. |
| 5 | ~~The redacted real-IAM basis for the findings, from the current route~~ | — | **Closed 2026-08-25** — [evidence 11](../../assets/evidence/11-current-route-correlation.md). A count-only companion probe on the current route measured 62 live bindings, 3 deterministic findings, 2 canonical owning departments and 0 raw IAM fields at the model boundary. This supersedes [evidence 02](../../assets/evidence/02-gemini-investigation.md), which stays retained as historical pre-Gateway proof. |
| 6 | Gateway refusals: unregistered caller, undeclared skill | — | **Two**, not three. The rate-limit refusal was removed by decision below, not deferred; both remaining refusals are asserted offline in `tests/security/test_gateway_policy.py` |
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

Two free-text routes were identified. The first still exists; the second is historical:

1. **The A2A message body.** Both worker services carry an `allUsers` Cloud Run invoker binding
   (documented in [SECURITY.md](../../SECURITY.md)); the only gate is the origin secret checked by
   `install_peer_origin_auth`. An A2A body is unbounded text, arrives as a `.text` part, and *is*
   screened by `screen_before_model`. This is a genuine deployed surface, so capture 2 needs no
   decoy input field. It demonstrates a **compromised authorized caller**, not an anonymous
   attacker, and the write-up must say so.
2. **Historical `exception_policy_version` route.** An operator-supplied 1-64 character string
   reached the former policy model inside a tool result. D4 added inbound tool-result screening,
   and the current policy step is model-free, so this route no longer reaches a model. See D4.

**What must be said plainly when capture 2 is written up:** every refusal observed in the deployed
fleet so far has been a false positive on the fleet's own traffic (`policy_match` on internal
orchestration text, `screening_unavailable` on the D2 egress denial). No refusal of a real
injection has been observed. Route 1 makes one obtainable; until it is captured, it is not claimed.

## Blocking defects observed in the deployed fleet

Found 2026-08-19/22 while attempting captures 1-4. Each was watched in the deployed system, not
inferred from code. They are recorded here because every capture then outstanding sat behind them;
captures 1-5 have since closed and only 6 and 7 remain.

**Status at 2026-08-22:** D1, D3, D4, D5, D6, D7 and D8 are fixed. D1-D7 shipped in 0.2.0;
D8 is fixed after it and ships in 0.2.1. Only D2 remains open, and it is no longer blocking.
D1, D3 and D6 are **observed**, and capture 1 is now closed by
[evidence 10](../../assets/evidence/10-cross-week-suppression.md). What is still not observed is
a **refusal** on this route, so capture 4 stays open — a trail of successes proves nothing about
the guardrails.

**Status update 2026-08-23:** a fourth instance of the same class was found and fixed the same
day it was introduced — see D9 below. It is recorded immediately rather than smoothed over,
consistent with how D1/D6/D8 are written up here.

**Status update 2026-08-25:** captures 2, 3, 4 and 5 closed in one evidence sprint against the
`c81b4af` fleet — evidence 11, 12 and 13. The 08-22 note above says capture 4 stays open because a
trail of successes proves nothing about the guardrails; that is now answered, though precisely
rather than fully. A refusal *is* recorded under the audit contract, but it comes from the
agent-mediated Model Armor probe rather than from the correlated investigation itself, and the
backlog row says so. D2's predicted consequence — that IAP-mediated egress might impair the
Runtime's OTel export and cost us capture 3 — did not occur: the trace is complete and connected.
Captures 6 (Gateway refusals) and 7 (timeout/retry/dead-letter) remain open and unclaimed.

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

### D8. A policy decision does not survive the escalation hop

**Fixed and observed 2026-08-22.** A human-approved exception was scored as `suppress` and
escalated anyway. Nothing was wrong with the policy: `apply_policy_rules_with_memory` marked it,
and `route_by_department` excluded it. Both results were discarded one hop later.

`PolicyStep` yielded an event carrying only `state_delta`, and ADK builds the outgoing A2A
message from `event.content.parts` — so the most recent content the Escalation Agent saw was
still the Auditor's report. `route_by_department` also returned no finding ids, so even reading
the routing would not have given the Escalation Agent an id to copy. Both are fixed, and
[evidence 10](../../assets/evidence/10-cross-week-suppression.md) records the run that honoured
the exception.

**Reported upstream 2026-08-22** as [google/adk-python#6854](https://github.com/google/adk-python/issues/6854), covering both directions and asking for a construction-time warning rather than only a documentation note. Bastion needs no fix from it — both hand-offs are already corrected here — but the next team to compose a `SequentialAgent` with a `RemoteA2aAgent` should not have to find this by deploying.

**This is a class, not an incident.** D6 was the Auditor's report failing to reach the policy
step; D8 is the policy step's decision failing to reach escalation. Both are the same root
cause — ADK session state does not cross an A2A boundary — and any future step that assumes it
does will fail the same way, silently, in the deployed topology only.

### D9. The deterministic Escalation Agent (P0.2/P0.3) could not read its own inbound request

**Introduced and fixed the same day, 2026-08-23**, while deploying P0.1–P0.3. Every deployed
investigation failed at the Escalation Agent with a payload-free, correctly-audited refusal
(`escalation.envelope rejected reason=missing_routing_envelope`) — and every one of them still
reported `investigation.run completed`, for two independent, compounding reasons documented in
full in [ADR-012's 2026-08-23 amendment](../../docs/adr/012-structured-findings-across-a2a.md):

1. `EscalationAgent` is the A2A **callee**, and the routing envelope arrives as the current
   turn's own inbound content (`InvocationContext.user_content`), which is a different channel
   from scanning session history — the pattern that correctly reads a *reply* on the *caller*
   side (as `_audit_report` does for the Auditor's reply). Reading the right channel was still
   not enough: ADK flattens multi-hop history into `"[policy_step] said: {...}"`-attributed
   text when building the next hop's request, so a bare `json.loads` on it raised and was
   silently treated as "no envelope found."
2. `RemoteA2aAgent` converts a failed remote task into an ordinary, contentless, error-free
   `Event` rather than surfacing the failure as a Python exception — and, separately,
   `infrastructure/deploy.sh` alone does not redeploy the Orchestrator's actual agent graph
   (it runs on the managed Agent Runtime, updated only by
   `infrastructure.deploy_agent_runtime`). Until that ran, `escalation_gate` — the step built
   specifically to catch a swallowed failure like this — was not even part of the live graph.

Both are fixed: `_parse_json_object` tolerates the attribution wrapping, and both deployment
surfaces were updated. Confirmed working end to end 2026-08-23: `escalation_gate` observed
passing, and exactly one `bastion_human_review` record created for the correct department with
the approved exception's finding still suppressed (capture 1, above).

**This is now a fourth instance of the same class**, and the two compounding mechanisms above —
an ADK transport that swallows a worker's own failure signal, and a deployment surface that is
easy to update only half of — are recorded as live risks for the next change to either hand-off,
not only as history.

### D2. IAP-mediated egress cannot resolve a non-standard Google host

**Reclassified 2026-08-22 from blocking defect to residual platform behaviour, with no
observed consequence.** The original title — *Model Armor screening is unavailable inside the
Runtime* — describes something that can no longer happen, and saying so is more useful than
leaving it open as though it still threatens the fleet.

Three measurements settle it.

1. **No model call happens inside the Agent Runtime at all.** The Orchestrator is a
   `SequentialAgent`; `policy_step` and `policy_gate` are model-free `BaseAgent`s; the two
   `LlmAgent`s run in Cloud Run workers. There is nothing left in the Runtime for Model Armor
   to screen, so `screening_unavailable` is not merely absent — it is unreachable. The last
   Model Armor event of any kind from the Runtime was 2026-08-22T08:16Z, before the policy
   step stopped calling a model.
2. **The workers screen successfully against the same host.** Cloud Run egress does not
   traverse Agent Gateway or IAP, and `modelarmor.europe-west4.rep.googleapis.com` answers
   them normally. The host is fine; the path through IAP is not.
3. **The denials no longer correlate with investigations.** They cluster at Runtime deploy and
   startup (18:31:29-18:32:04 around a deploy whose `updateTime` is 18:31:37), not at
   investigation time. Investigations complete, `verify_fleet` passes, and the production
   smoke passes with these denials still being emitted.

   **Measured again 2026-08-25, and more precisely.** The 12 denials recorded that day fell in a
   single 1.2-second burst at 16:31:52.643Z-16:31:53.857Z. The investigation's root span opens at
   16:31:56.197Z — three seconds *after* the last denial — and the run then completes at
   16:33:01.597Z with no further IAP event of any kind. So the denials belong to instance cold
   start, not to the request path, and the whole governed route ran clean behind them. Every one of
   the 100 most recent denials resolves to `unregisteredEndpoint` with an empty
   `authenticationInfo`, which is the same signature described above and not a caller being refused.

**What is actually happening.** Six registered destinations use non-standard Google hostnames
(`*.rep.googleapis.com`, `*.mtls.googleapis.com`); eight use plain `*.googleapis.com`. Every
IAP authorization event resolves to
`projects/.../locations/global/iap_web/agentRegistry/endpoints/unregisteredEndpoint` and denies
`iap.webServiceVersions.egressViaIAP`, with an **empty `authenticationInfo`**. Plain hosts are
never IAP-checked at all, so they cannot be denied. **[inferred]** IAP's endpoint resolution
does not match a non-standard host to its Agent Registry entry, however correctly that entry is
registered — which is consistent with every observation and with the fact that the resolution
namespace is `locations/global` while the Registry is regional.

Eliminated by experiment across two sessions: registering in the `global` Registry location
(the Gateway binds only to its regional registry — reverted), rebinding interfaces from `GRPC`
to `HTTP_JSON`, redeploying the Runtime, Registry `bindings` (`auth_provider is required`; that
field is for OAuth connectors, not Google-API egress), and IAM (the Agent Identity holds
`roles/iap.egressor` at project level, and no IAP authorization has ever been granted).

**Not fixable from this repository.** The remaining action is a Google Cloud support question,
and it should be asked precisely: *why does Agent-to-Anywhere IAP resolve a registered
`*.rep.googleapis.com` destination to `unregisteredEndpoint`, when a plain `*.googleapis.com`
destination in the same regional registry is admitted without an IAP check at all?*

**Consequence measured 2026-08-25: none.** The concern recorded here was that IAP-mediated egress
to non-standard hosts might impair the Runtime's OTel export (`telemetry.mtls.googleapis.com`) and
cost us capture 3. It did not. The trace captured that day is complete and connected — 22 spans
across the managed Runtime and both A2A workers in one tree, recorded in
[evidence 13](../../assets/evidence/13-current-route-trace.md). D2 remains open as residual
platform behaviour with, now, a measured absence of consequence on both the request path and the
telemetry path.

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

## Decision taken 2026-08-22 — rate limiting stays unimplemented, and is not claimed

**Rate limiting does not exist anywhere in the codebase.** It was absent, not stale. Three
ways forward were recorded and the choice belonged to the platform owner; it has now been
made, on evidence rather than preference.

**Option 1 — rely on the managed Gateway's quota surface — is not available.** Measured
against the live `bastion-egress` gateway: its entire configuration surface is
`agentGatewayCard`, `googleManaged.governedAccessPath`, `labels`, `protocols` and
`registries`. There is no rate or quota field, and `gcloud network-services agent-gateways
update` exposes no such flag. The managed product does not offer this control, so there is
nothing to configure and nothing to capture.

**Option 3 — implement it locally — is rejected, and the reason is specific rather than
doctrinal.** `gateway/policy.py` exists to mirror what the deployed Gateway enforces; its own
docstring says so, and the security suite asserts against it. Every refusal it evaluates is
also applied in production. A local limiter would be the one rule in that file the managed
control does not apply, so the suite would assert a refusal production does not make.

That is not hypothetical. This repository has now shipped **three** defects of exactly that
shape — the model-gated policy step, the Auditor hand-off, the escalation hand-off — each one
true of the code and false of the deployed system, and each found by watching the fleet rather
than by running the tests. Adding a fourth deliberately, in the file whose purpose is to agree
with production, would be the least defensible version of that mistake.

**Option 2 is taken: two refusals are claimed, because two are enforced.** No document claims
a rate limit, and none will.

**What does bound throughput, described as what it is.** `BASTION_MAX_INSTANCES` caps Cloud
Run concurrency and Eventarc delivery is bounded to five attempts before a message reaches the
dead-letter subscription. Those are real, deployed and observable — and they are a concurrency
cap and a delivery bound, not a per-caller rate limit. Calling them one would be the same
category error in prose that option 3 would be in code.

Recorded as an amendment to [ADR-003](../../docs/adr/003-pillars-on-geap.md), which is the
record this reasoning applies.

## Closing rule

Nothing here may be marked closed in [SUBMISSION.md](../SUBMISSION.md) on the strength of a
passing test. A test proves the logic; the capture proves the deployed system did it. Where only
one exists, say which — as [evidence 08](../../assets/evidence/08-tool-poisoning.md) does for the
tool boundary, and as [ADR-006](../../docs/adr/006-pillar-coverage.md) does for Memory Bank.
