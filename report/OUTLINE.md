# Definitive report blueprint (frozen 9 November 2026)

Approved by the maintainer on 9 November 2026 after two external reviews. It supersedes the
6 November outline. Changes from here on are limited to verified evidence corrections, manuscript
accuracy, publication integrity and artifact validation. The scientific framing is final. The
local PDFs of 6–7 November are drafts, not editions. One report is published, with one immutable
reference.

**Title:** Bastion: Execution Boundaries, Control Evolution, and Bounded Evaluation of a Governed
Agent Fleet
**Author line:** Arjun Ganesh, Independent researcher, Stockholm
**Unifying lesson:** application-level correctness claims require evidence at execution
boundaries.

## Contributions

- **C1 — Governed architecture.** A deployed, minimisation-first IAM-review fleet:
  deterministic policy authority, explicit agent handoffs and durable execution controls.
- **C2 — Failure and repair case study.** Dated execution-boundary failures and the controls
  that answered them. Observed behaviour is separated from framework-documented semantics.
- **C3 — Bounded deployment evaluation.** Pre-specified protocols covering successful runs,
  stopped cohorts, model-retry recovery, negative security controls, replay checks, telemetry
  investigation and timeout fault injection.
- C4 (the matched-explanation study) is deferred. It is not an evaluated contribution.

## Table of contents

1. Introduction
2. Background and related work
3. System and threat model
4. Design as finally deployed (v0.9.1)
5. Evaluation method
6. Execution-boundary failures and control evolution
   - 6.1 Historical failures
   - 6.2 Corrective controls and verified recovery
   - 6.3 Remaining limitations
7. Final bounded evaluation
   - 7.1 Run ledger G–M
   - 7.2 Cohort I
   - 7.3 J controls
   - 7.4 Telemetry
   - 7.5 Timeout fault injection
   - 7.6 Pre-upgrade baseline
8. What the evaluation does not demonstrate
9. Discussion and research agenda
10. Conclusion

- Appendix A: Reproducibility and version provenance
- Appendix B: Evidence index
- Appendix C: Protocols, stop records and amendments

## §3 Threat model — fixed points

Trust boundaries:

- Pub/Sub → dispatcher;
- dispatcher → managed Runtime;
- Runtime → A2A workers (peer credential);
- Runtime egress → Agent Gateway;
- worker → model (Model Armor);
- worker → IAM (the minimising tool).

The Gateway is egress-only (`AGENT_TO_ANYWHERE`). It never authorises callers.

## §5 Method

### Per-run pass criteria (all must hold)

| Quantity | Requirement | Source |
|---|---|---|
| Durable investigation attempts | exactly 1; status completed | Firestore record, by event ID |
| Audit trail | gap-free under the sealed E4 observer's contract | Cloud Logging, by investigation ID |
| Review records | 2 (one per routed department), with finding counts {platform-infra 1, security-engineering 2} equal to the fresh baseline | Firestore review store |
| Logical model completions | exactly 2 Auditor `model.request/completed` records | Audit trail |
| Audited model retries | counted separately (`model.request/retrying`); at most 6 per run, and an exhausted retry fails the run | Audit trail |
| Eventarc ingress deliveries to the dispatcher | exactly 1, HTTP 2xx | Cloud Run request log, by isolated time window (not message ID) |
| Not criteria | Findings API notification status; underlying provider attempts | — |

### Workload

Every G–M preflight took a fresh count-only baseline: 62 IAM bindings → 3 findings → 2
departments (G 18:55Z, H 20:09Z and I 22:44Z on 7 November; J 08:27Z on 8 November; M's
preflight repeated the check). This is a deliberately bounded configuration, not a
representative sample. August and October censuses are never reused for November.

### Pre-specification and provenance (state in three distinct parts)

1. For each of G–M, the protocol and criteria were documented before execution, according to
   the project's internal local records.
2. The execution scripts checked their hashes against the locally recorded protocol or
   cost-admission pins at start-up. This establishes that the specified consistency check ran
   at execution.
3. No independent external timestamp establishes when any protocol was fixed. Hence
   "pre-specified", never "pre-registered".

Publishing sealed hashes (seal of 9 November) establishes integrity from that date onward. It is
not retrospective proof of independent pre-registration. M's original protocol hash was
reconstructed after the run (`5425df…`, with the amendment record removed) and is an additional
explicit limitation.

### 98/98 statistic (method and limitations only; never in the abstract or conclusion)

Under a hypothetical independent, identically distributed Bernoulli model with a constant
failure probability, zero failures in 98 trials yields a one-sided 95% Clopper–Pearson upper
confidence limit of about 3.01% (1 − 0.05^(1/98)). The serial, shared-infrastructure
observations do not establish this model. The interval is illustrative and is not a field
reliability estimate or SLO.

### Instrument policy

- Observation reads may retry within a bounded window. Measured actions never retry.
- Instrument stops are classified separately from system failures.
- Stopped runs are retained, never rerun and never pooled.
- Post-hoc read-only analyses (I99 addendum, M ordering, trace census) are labelled as such.

## §6 Chronology

Each row records: date · observed · repair · deployed · verified · unresolved.

### 6.1 Historical execution-boundary failures

- **D1 (21 Aug, observed).**
  - Observed: the LLM policy step's `before_model_callback` refused, so its tools never ran. The
    investigation still escalated (two deliveries) and `investigation.run` reported completed.
  - Repair: a deterministic `BaseAgent` plus a gate (ADR-010), in 0.2.0, observed fixed 22 Aug.
  - Classification: application contract violation.
- **D6 (21 Aug, observed).**
  - Observed: the Auditor's `output_key` landed in the worker's own session.
  - Classification: framework-documented semantics; Bastion's assumption was the violation.
  - Repair: read the validated A2A reply. Verified 22 Aug.
- **D8 (22 Aug).**
  - Observed: an approved exception was scored `suppress`, then escalated anyway. A
    state-delta-only event and missing finding IDs meant the next hop saw the Auditor's report.
  - Repair: explicit routing content with finding IDs. Verified by E10. Reported upstream as
    google/adk-python#6854.
  - The affected runs' terminal status is not independently established.
- **D9 (23 Aug, introduced and fixed the same day).**
  - Observed: the callee read the wrong channel; attribution-wrapped history broke parsing;
    `RemoteA2aAgent` turned the failed task into a contentless, error-free event; a half-updated
    deployment left the escalation gate out of the live graph; the audit reported completed.
  - Repair: tolerant parsing and both deployment surfaces updated.
- **E19 (3 Nov).**
  - Observed: the durable record read completed (1 attempt, 81 s) with no audit record, review
    or model call; two Runtime instances started during the run.
  - Identified dispatcher bug: the end of the stream was treated as success.
  - The underlying Runtime cause is not established. Instance replacement is not claimed as the
    cause.

### 6.2 Corrective controls and verified recovery (attribution kept distinct)

- **Deterministic policy authority and explicit A2A handoffs:** D1/D6/D8 → ADR-010/012.
- **Dispatcher completion confirmation (E19 → `run_managed_runtime`).**
  - Positive confirmations were observed directly in E25 F0, J0, K1 and K2.
  - Completed normal investigations on v0.9.x imply the dispatcher saw the expected
    confirmation, under the implemented dispatcher contract.
  - M shows the dispatcher rejecting a missing confirmation (5 × `RuntimeIncompleteError`).
  - H28 shows a failed-closed policy-execution path after the model 429
    (`PolicyNotEnforcedError`).
  - Neither H28 nor M is evidence that `EscalationCompletionGate` itself executed and rejected
    an invalid receipt.
- **Parser correction:** the E24 pilot failed closed; recovered in E25 (5 Nov).
- **Routing provenance and finding-ID receipts.**
  - Source fix 7 Nov (review finding; no live harm observed); deployed in v0.9.0/v0.9.1.
  - J (8 Nov) shows Auditor-attributed routing in relayed history is rejected
    (`missing_routing_envelope`, 0 reviews) and the policy-step positive control completes.
  - Bare JSON on the authorised request path is still accepted by design and is bounded by the
    worker-origin credential. This is not proof that unauthorised routing can never be accepted.
- **Span-content setting restored after template set-up.** The census found 0 content-carrying
  attributes in 142 traces, which bounds only what was inspected.
- **v0.9.1 bounded model retry.**
  - Retries 429/500/502/503/504 only, at most 4 provider attempts per logical call, only before
    the first response; each retry is audited.
  - Motivated by H28 (7 Nov: a 429 failed closed, then was redelivered and completed on
    attempt 2).
  - I57 shows one successful model-level retry (429 → recovered, one durable attempt), not
    general recovery.

### 6.3 Remaining boundary limitations

- **Gateway misclassification (D2/E20):** the start-up project lookup to a registered host is
  refused; platform-side.
- **Observed incomplete Runtime graph-span export.**
  - 5 of 142 agent traces (see the §7.4 definition) carry Runtime graph spans: F1, H1, J0, K1
    and L1, matched by time window.
  - K1 had them and K2 did not. Each of the five followed a pause; the converse was not tested.
  - Root cause unresolved; no platform rule is claimed.
- **Cancellation:** there is no guarantee that in-flight remote computation is cancelled after a
  caller-visible timeout (§7.5).

## §7 Final bounded evaluation

### 7.1 Run ledger (heterogeneous protocols; never a rate)

| Run | Fleet | Classification | Evidence |
|---|---|---|---|
| G | v0.9.0 | Instrument stop after 4 validated passes (transient Firestore read); G5 completed in the cloud | E26 |
| H | v0.9.0 | System failure at H28: model 429, failed closed, redelivered and completed. Stopped by rule | E26 |
| I | v0.9.1 | 98 validated passes, then an instrument stop at I99 (Cloud Logging HTTP 500). The separate read-only addendum shows I99 met every criterion; it stays outside the 98 | E26 |
| J | v0.9.1 | Direct control, 5 replays, refusal, envelope pair: all passed | E27 |
| K | v0.9.1 | Trace-export isolation, plus the census | E28 |
| L | v0.9.1 | Instrument failure in its first read. The fault never reached its investigation; no valid injection occurred. Restored and verified | E29 |
| M | v0.9.1 | Attempt 1 stopped in preflight: no injection, no publication. Amendment M-A1 recorded 09:26:18Z. Attempt 2 met all 8 pre-specified criteria | E29 |

M's preflight attempts are protocol execution attempts. They are never called "durable
attempts", which means the five deliveries of M1.

### 7.2 Cohort I

- When: 22:53Z 7 Nov to 01:52Z 8 Nov, serial.
- Result: 98/98 validated. Client confirmation median 15.453 s (15.250–60.781 s, which includes
  5-second polling).
- 2,745 correlated audit records, 196 model completions, 196 review records.
- 1 audited model retry (I57).
- Not pooled with G or H.

### 7.3 J controls (no deploy; same fleet as I)

- J0: direct Runtime control.
- Five completed-event replays (originals I1, I25, I50, I75, I98) produced no additional
  durable, review, agent-invocation or model effects during their 120-second windows.
  - I98 replaced the planned I100, which was never run. I98 qualified as I's last validated run.
  - The substitution was recorded in J's protocol at 08:29:01Z, before execution at 08:29:29Z.
- One Model Armor refusal: no model or tool work at or after it, and joined to its
  investigation ID.
- The envelope pair.

### 7.4 Telemetry

- J0 produced one connected 172-span trace (Runtime graph, both worker workflows, 2 model calls,
  1 tool call) with no content attributes.
- **Census definition.**
  - Unit: one Cloud Trace trace ID containing any `invoke_workflow` span, starting between
    5 Nov 00:00Z and 8 Nov 10:00Z.
  - Collection: Cloud Trace v1 list API, fully paginated (63 pages).
  - Traces are not joined one-to-one to investigations (about 149 dispatches in the window
    against 142 traces). Sampling is unknown.
  - Read-only and post hoc.

### 7.5 M — two separate findings

- **M-Safety (pre-specified; all 8 criteria met).**
  - Auditor request timeout set to 3 s (normally 300 s).
  - 5 Eventarc deliveries about 20–25 s apart, each answered 503.
  - 5 Auditor A2A 504s at about 3.0 s.
  - 5 durable attempts, ending failed (exact, by event ID).
  - 5 audited `RuntimeIncompleteError` dispatch failures.
  - 0 review records, and no Escalation execution.
  - Dead-letter attribution rests on the review backlog rising from 1 to 2 within the isolated
    window. The message was never pulled, so there is no message-ID join.
  - Restored and verified; one normal control then passed.
  - Controls that operated: fail-closed handling, redelivery and dead-lettering.
- **M-Cancellation (post-hoc, read-only; by timestamp and worker invocation ID).** Use this
  statement:

  > In one controlled timeout-injection investigation, worker-side execution continued beyond
  > five estimated three-second caller timeout boundaries. Six of ten model completions and
  > three of five IAM tool calls were recorded after those boundaries. The investigation failed
  > closed with no review records and was dead-lettered. These observations establish
  > incomplete cancellation propagation in the tested configuration, not a universal timeout
  > rule.

  - The boundary is estimated as request-received time + 3.0 s.
  - Worker runs finished 8–31 s after their boundaries.
  - Not claimed: denial-of-wallet, or cost.

### 7.6 Pre-upgrade baseline (separate)

N, 3–4 Nov (E16–E23); 27 Oct (E14); August E10–E13. Each keeps its own date and census.

## §8 Does not demonstrate

- A general or field reliability rate, or any SLO.
- Representativeness: one project, one bounded workload.
- Concurrency, scale, multiple tenants, or scheduled operation.
- Tracing of every investigation.
- An unregistered-caller Gateway refusal (impossible in this architecture).
- C4.
- Exact cost (bounded only).
- The Runtime's installed packages.
- Any guarantee that in-flight remote computation is cancelled after a caller-visible timeout.

## §9 Research agenda

**Primary direction — "Across the Agent Boundary: Do Agent Frameworks Preserve Execution
Contracts When Sub-Agents Become Remote?"**

- Compare equivalent workflows composed locally and over remote A2A within each framework, using
  naive and idiomatic ports.
- Measure: error and refusal propagation; state and policy-decision visibility; A2A task-state
  fidelity; context and correlation propagation; outcome uncertainty after partial failure;
  persisted side effects against an independent observation ledger.
- Separate documented framework behaviour from application violations.
- Not yet performed. Motivated by D6/D8/D9 and M-Cancellation.

Also: C4 (harness ready), verifying telemetry on managed platforms, and cancellation propagation.

## Appendix A — source vs deployment

| Fleet | Source | Deployed | Used by |
|---|---|---|---|
| August/October | earlier tags | Aug | E10–E14 |
| 5 Nov upgrade | ADK 2.13 | 5 Nov | F, E25 |
| v0.9.0 | tag be5c621, ADK 2.14.0 | 7 Nov (Runtime 19:30Z) | G, H |
| v0.9.1 | tag 755dd07 | 7 Nov 22:45–22:53Z | I–M |

- L and M created Auditor revisions 00036–00039 with the same image digest and verified identical
  configuration.
- The Runtime's installed packages were never read independently.

## Publication-integrity blockers (clear before DOI)

1. Evidence pages E26–E29 and claim-matrix rows for every new claim.
2. Docs PR: the v0.9.1 sweep and site data; the E19 docstring overstatement (comment only).
3. "Pre-specified" wording across G–M, plus the three-part provenance statement and M's
   reconstructed hash.
4. The D4 end state recorded before the report states it.
5. A final billing check after late postings; cost stays bounded.
6. The immutable reference: deployed code is v0.9.1; the report and evidence cite a later
   docs-only reference (maintainer choice pending: `report-2026-11` recommended). The maintainer
   approves the tag, DOI and site release (D5).
7. Historical baseline numbers are verified before being cited, and never carried into November.

The [report plan](../docs/research/report-plan.md) governs publication and the fleet end state.
