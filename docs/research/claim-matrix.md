# Claim matrix

- **Reviewed:** 2026-08-24; reconciled 2026-08-27 against release `v0.6.0` after the P0.6-P0.9
  evidence sprint, the gallery composition, and the dependency bump; reconciled again 2026-08-29
  against `v0.7.0`, when the demo was published and the `In demo` column became answerable
- **Report supplement:** 2026-10-27 live validation, documented 2026-10-28 below; the August
  capture dates and submitted demo are preserved.
- **Cohort N:** reconciled 2026-11-04 against evidence 16–23. The two August `Partial` rows
  (Gateway refusal, retry/DLQ) closed with narrowed wording. One new row, durable completion
  integrity, was deployed on 5 November. The initial F pilot failed closed (E24); the
  separately corrected recovery passed the predefined positive/replay controls (E25). The
  refusal audit also carried the direct investigation-ID join. No reliability rate is claimed.

- **G–M:** reconciled 2026-11-09 against evidence 26–29 (v0.9.0/v0.9.1 cohorts, targeted controls, telemetry census, timeout fault injection). Evidence is frozen; protocols are described as pre-specified, not pre-registered.

- **Purpose:** Pre-publication gate for report and public claims. The `In demo` column records
  the frozen August submission. `Implemented` and `Tested` describe source support for the claim;
  `Deployed` and `Observed` describe the claimed production behaviour. Observing a defect does
  not establish that its fix was deployed or observed working. Any `Partial` entry requires the
  narrower wording in the final column; it does not mean the underlying architecture is absent.

| Claim | Implemented | Tested | Deployed | Observed | In demo | Safe to claim? | Evidence boundary and safe wording |
|---|---:|---:|---:|---:|---:|---:|---|
| Real IAM read | Yes | Yes | Yes | Yes | Yes | Yes | [Evidence 11](../../assets/evidence/11-current-route-correlation.md) is the 25 Aug companion count proof: 62 bindings, 3 deterministic findings, 2 canonical owning departments and 0 raw IAM finding-schema fields. [Evidence 14](../../assets/evidence/14-live-validation.md) re-observes 20 IAM-tool/gated execution paths on 27 Oct without a new census. [Evidence 23](../../assets/evidence/23-deployment-census.md) records the separate 28 Oct census: 56 bindings and 3 findings across the same two departments; its original census seal is unavailable, as disclosed in the [audit](evidence-audit-2026-11-04.md#original-census-seal-is-unavailable). Evidence 09's 52 bindings remain 18 Aug history; evidence 02 remains pre-Gateway. Say **read-only production IAM**, keep census dates explicit, and never imply raw principals/bindings are retained or that the census ran on the November evaluation days. |
| Exact deterministic finding set | Yes | Yes | Yes | Yes | Yes | Yes | P0.1 checks model fields against canonical tool findings; [ADR-012](../adr/012-structured-findings-across-a2a.md) records the Aug 23 successful enforced path. [Evidence 14](../../assets/evidence/14-live-validation.md) adds 20 gated successful paths on 27 Oct, not new mutation probes. The model may write bounded rationale, not alter authoritative fields; mutation refusals remain offline test proof. |
| Cross-department routing | Yes | Yes | Yes | Yes | Yes | Yes | [Evidence 11](../../assets/evidence/11-current-route-correlation.md): 25 Aug, 3 canonical findings/2 departments before policy, 2 delivered findings/1 review record after suppression. [Evidence 14](../../assets/evidence/14-live-validation.md): 27 Oct, 3 delivered instances/2 department records per investigation, across 20 runs. The latter is not a new canonical census or expiry measurement; 60 delivered instances are not 60 distinct risks. Routing provenance and finding-ID receipts are deployed from v0.9.0; [evidence 27](../../assets/evidence/27-targeted-controls-j.md) shows Auditor-attributed routing rejected (`missing_routing_envelope`, 0 reviews) and the policy-step positive control completed. Bare JSON on the authorized request path remains accepted, bounded by the worker credential: say **rejects Auditor-attributed routing**, never that unauthorized routing is impossible. |
| Human exception continuity | Yes | Yes | Yes | Yes | Yes | Yes | [Evidence 10](../../assets/evidence/10-cross-week-suppression.md) observes the 19-22 Aug three-day gap, reverified 23 Aug. Say **remembered across a real elapsed gap**; do not infer expiry or a literal week from October's delivered counts. |
| Human exception expiry | Yes | Yes | Yes | Yes | No | Yes | [Evidence 16](../../assets/evidence/16-exception-lifecycle.md), 3 Nov: a 15-minute approval suppressed one `platform-infra` finding (R2: 0 of 1) and the same finding returned 120 s after expiry (R3). One lifecycle on one finding; not a rate. Its durations are cold-start confounded and its tokens are not attributable per run. |
| Escalation IAM denial | Yes | Yes | Yes | Yes | Yes | Yes | [Evidence 03](../../assets/evidence/03-escalation-agent-denied.md) records successful impersonation then IAM-read denial on 15 Aug, with an Auditor success control. Re-probed 3 Nov in [evidence 17](../../assets/evidence/17-negative-authorization.md): impersonation succeeded, `getIamPolicy` returned `PERMISSION_DENIED`, and a permission test showed the Auditor holds the read the Escalation identity lacks. |
| Exception approval authorization | Yes | Yes | Yes | Yes | No | Yes | [Evidence 17](../../assets/evidence/17-negative-authorization.md), 3 Nov: missing, malformed, wrong-service and maintainer-user tokens refused (401/403); four invalid approver payloads refused (400) and one schema error (422); the ledger was unchanged. Single probes, not fuzzing. |
| Agent-mediated Armor refusal | Yes | Yes | Yes | Yes | Yes | Yes | **Closed 2026-08-25:** [evidence 12](../../assets/evidence/12-agent-mediated-model-armor-refusal.md), authenticated Auditor injection refused with no subsequent model/tool call. This models a **compromised authorized caller**, not an anonymous one. Re-probed 3 Nov in [evidence 18](../../assets/evidence/18-model-armor-refusal-reprobe.md) with a completed benign control: same 141-character fixture, `policy_match`, task failed, nothing logged after refusal. That refusal joins in two hops through its invocation ID. The separate 5 Nov [evidence 25](../../assets/evidence/25-corrected-cohort-F-verification.md) establishes a direct investigation-ID join through a read-only exact-ID query about 393 s later, with no model completion/tool record or post-refusal model/tool event found. Its collector falsely counted a pre-refusal plugin entry; the original stop and addendum are retained. No continuous monitoring or directly measured production provider-request count is claimed. Evidence 01 remains the direct-template measurement. |
| Managed Gateway refusal | Yes | Yes | Yes | Yes | No | Yes | [Evidence 20](../../assets/evidence/20-gateway-unmatched-egress-refusal.md), 4 Nov (read-only): with fail-closed IAP enforcement IAP made 176 denial decisions on Runtime egress it resolved to `unregisteredEndpoint`, from 88 failed project lookups by the SDK (Resource Manager): 156 decisions within 90 s of the 13 instance starts (12 each) and 20 during runs; investigations continued. Say **refused egress it did not match to a registered endpoint**, never "refused an unregistered destination": the refused host is registered. This is the August defect D2 ([observation backlog](observation-backlog.md#d2-iap-mediated-egress-cannot-resolve-a-non-standard-google-host)), unchanged: IAP misclassifies non-standard Google hostnames, plain `*.googleapis.com` egress is not IAP-checked, and no IAP grant has ever been logged. So this shows fail-closed handling of unmatched traffic, not registered-versus-unregistered discrimination. Incidental, not an experimenter-chosen destination. The Gateway governs egress only; caller checks at the workers are evidence 17. P0.10 closed with this wording. |
| Durable completion integrity | Yes | Yes | Yes | Yes | No | Yes | [Evidence 24](../../assets/evidence/24-upgraded-deployment-and-stopped-pilot.md) retains the unconfirmed pilot failing closed across five automatic deliveries. In the separate corrected recovery, [evidence 25](../../assets/evidence/25-corrected-cohort-F-verification.md), five normal investigations completed in one durable attempt with expected reviews, the direct Runtime control returned trusted confirmation, and two replays had bounded unchanged effects. Say **verified completion confirmation in five normal cases plus one separate direct control**, not a universal guarantee. No live forced-empty-stream experiment was performed. [Evidence 19](../../assets/evidence/19-repeatability-and-false-completion.md) keeps the earlier false completion; none of these cohorts is pooled. **v0.9.0/v0.9.1 (7–8 Nov):** direct positive confirmations in J0, K1 and K2 ([evidence 27](../../assets/evidence/27-targeted-controls-j.md), [28](../../assets/evidence/28-telemetry-census-k.md)); the 129 validated normal investigations of G, H and I ([evidence 26](../../assets/evidence/26-cohorts-g-h-i.md)) imply dispatcher confirmation under its implemented contract; run M ([evidence 29](../../assets/evidence/29-timeout-fault-injection-l-m.md)) shows the dispatcher rejecting a missing confirmation five times (`RuntimeIncompleteError`). Neither H28 nor M is evidence that the escalation completion gate rejected a receipt. |
| Repeatability, latency and tokens | Yes | Yes | Yes | Yes | No | Yes | [Evidence 19](../../assets/evidence/19-repeatability-and-false-completion.md), E7b: all 20 runs passed, 1 attempt each, 25/25 Eventarc deliveries, 5/5 replays unchanged; corrected conventional median 20.6 s with 5 of 20 runs at approximately 136–206 s; median 1,788 input / 1,600 output tokens per run. The original record's 20.4 s used the lower-middle `p50`; see the [numerical correction](evidence-audit-2026-11-04.md#e19-median-correction). One batch, not a reliability rate. |
| Retry/DLQ behavior | Yes | Yes | Yes | Yes | No | Yes | [Evidence 21](../../assets/evidence/21-redelivery-and-dead-letter.md), 4 Nov: one synthetic `mock_data: true` event on the production subscription was rejected (HTTP 400) on 5 deliveries, then forwarded with `CloudPubSubDeadLetterSourceDeliveryCount = 5`, found and cleared in review; no investigation state written. Start-to-start gaps were 32.3, 14.0, 17.2 and 22.9 s; the first response itself took 18.6 s. Say **one rejected event was delivered five times in all, including four redeliveries, and then dead-lettered**. This is one permanent rejection, not a guaranteed delivery bound or a worker-timeout sequence. Transient failure and reclaim stay [evidence 06](../../assets/evidence/06-durable-findings.md); Google documents the attempt count as approximate. P0.11 is closed with this wording. **Worker timeout, 8 Nov ([evidence 29](../../assets/evidence/29-timeout-fault-injection-l-m.md)):** with the Auditor timeout injected at 3 s, one investigation got 5 deliveries (each 503 after a 504), 5 failed durable attempts, 0 reviews, and was dead-lettered (review backlog 1 → 2; attribution by isolated window, not message ID). Say **one investigation failed closed through five timed-out attempts and reached dead-letter review**; worker computation continued past the estimated timeout boundaries (no cancellation guarantee). |
| Production investigations on v0.9.1 | Yes | Yes | Yes | Yes | No | Yes | [Evidence 26](../../assets/evidence/26-cohorts-g-h-i.md), cohort I, 7–8 Nov: **98 of 98 validated** serial investigations (one durable attempt, gap-free audit, baseline review counts, two model completions, one 2xx ingress delivery each), stopped at I99 on a Cloud Logging outage; I99's read-only addendum is separate and outside the 98. G and H are separate stopped cohorts, never pooled. The 3.01% Clopper–Pearson bound is only a conditional illustration under an unestablished i.i.d. model; never call it a reliability rate or SLO. Protocols are **pre-specified** (local records, execution-time hash checks, no external timestamp), not pre-registered. |
| Bounded model retry | Yes | Yes | Yes | Yes | No | Yes | v0.9.1 retries 429/500/502/503/504 only, at most 4 provider attempts per logical call, only before the first response, each audited. Motivated by H28's failed-closed 429 ([evidence 26](../../assets/evidence/26-cohorts-g-h-i.md)); I57 shows **one** successful model-level retry within one durable attempt. Not general recovery from service failure. |
| Cancellation after a caller-visible timeout | Yes | No | Yes | Yes | No | Partial | [Evidence 29](../../assets/evidence/29-timeout-fault-injection-l-m.md), post-hoc: in one timeout-injection investigation, 6 of 10 model completions and 3 of 5 IAM tool calls were recorded after five **estimated** 3-second caller timeout boundaries. Say **incomplete cancellation propagation in the tested configuration**; no universal timeout rule, no denial-of-wallet or cost claim. `Implemented` refers to the timeout itself; no cancellation propagation is implemented. |
| Correlated trace/audit | Yes | Yes | Yes | Yes | Yes | Yes | [Evidence 11](../../assets/evidence/11-current-route-correlation.md)/[13](../../assets/evidence/13-current-route-trace.md): 25 Aug, 28 events/3 invocations and a 22-span trace. [Evidence 14](../../assets/evidence/14-live-validation.md): 27 Oct, 560 events/60 invocations and one time-matched 22-span trace, not an embedded investigation-ID join. [Evidence 19](../../assets/evidence/19-repeatability-and-false-completion.md), 3 Nov: 28 events per run across 20 runs; 18 of 20 runs had a sampled trace, joined by time window only (no ID on spans). Retention remains dated [evidence 07](../../assets/evidence/07-observability.md) configuration proof; no new retention/immutability claim. Evidence 13's content-free spans rest on the Runtime making no model or tool call; the template overrides the deployed span-content setting (dated follow-up on evidence 13). **v0.9.1, 8 Nov ([evidence 28](../../assets/evidence/28-telemetry-census-k.md)):** J0 reproduced one connected 172-span Runtime + worker trace with zero content-bearing attributes; the read-only census found Runtime graph spans in 5 of 142 agent traces (5–8 Nov), so per-investigation end-to-end tracing is **not** claimed after the upgrade. |
| Recurring trigger or event-driven limitation | Yes | Yes | Yes | Yes | Yes | Yes | August snapshot: observed Pub/Sub/Eventarc path, no Scheduler job. [Evidence 14](../../assets/evidence/14-live-validation.md): 20 further Pub/Sub/Eventarc completions on 27 Oct. The separate 28 Oct [inventory](../../assets/evidence/15-fleet-inventory.md) again records zero Scheduler jobs. Say **triggered by an approved enterprise event source**, not recurring/continuous operation. |

## Retained-evidence audit, 4–5 November 2026

The [complete audit](evidence-audit-2026-11-04.md) covers every row and all 23 numbered records,
their available bundles and promoted screenshots. It records the E19 median correction, the
unavailable original census seal, and the distinction between a configured policy and a measured
outcome. Original capture bytes remain unchanged; the audit is not a new live verification.

## Post-hackathon report validation, 27 October 2026

[Evidence 14](../../assets/evidence/14-live-validation.md) adds 20 one-attempt real-IAM
executions on one project, 560 correlated audit records/60 invocations, 40 model submissions
and 40 review records carrying three delivered finding instances per investigation.
Client confirmation median 20.461s includes 5s polling; Runtime audit median 15.948207s
measures a different interval. Original source/checkpoint and the collector's read-only
recovery are retained; no successful investigation was rerun or excluded.

Five replay publications had unchanged effects observed for 120s, not independently
confirmed per-message Eventarc delivery. The new pilot trace is a unique-name/time-window
match, not an embedded investigation-ID join. Installed package resolution and actual
currency cost were not freshly measured. At that date, these observations strengthened bounded
execution/delivery evidence but did not close the two then-`Partial` rows, alter the demo column
or the 25 August 62-binding measurement, prove exception expiry, or change C4's deferred status.
The November evidence and current statuses are recorded in the table above.

## Publication rule

The `In demo` column says `Yes` only where a claim appears in the published cut. The 3:53 demo
was published on 2026-08-29 at <https://youtu.be/Xpj8YmzFfpk>; its eight `Yes` entries were
checked against the [beat text](../../archive/hackathon-2026/submission/DEMO_SCRIPT.md), not
inferred from row titles. The narration contains neither the managed Gateway refusal nor an
observed redelivery. Those rows were partial when the demo was made, and remain `No` in that
historical column even though narrower report claims closed on 4 November.

`Safe to claim?` is a separate current assessment: a `Yes` permits only the bounded sentence
supported by its evidence. A `No` keeps the production claim unavailable. An implementation or
test completion does not establish deployment or live verification. Report publication and site
updates follow the approvals and sequence in the [report plan](report-plan.md); this matrix
grants no publication or live-run authorization.

Until 4 November two rows were `Partial`, exactly the two captures then open in
[09-capture-backlog.md](observation-backlog.md): managed Gateway refusals (capture 6) and
timeout/retry/dead-letter (capture 7). Until then, public copy said **bounded delivery is
configured and retry/idempotency paths are tested** and claims only the governed route and its
fail-closed observation — never an observed Eventarc redelivery, an observed fifth-attempt
dead-letter, or the planned unregistered-caller refusal. The unregistered-caller refusal and a
worker timeout sequence are still never claimed. Per-caller rate limiting is never claimed at
all; it does not exist.

**4 November 2026:** both captures are now closed for the report, by evidence
[20](../../assets/evidence/20-gateway-unmatched-egress-refusal.md) (Gateway, narrowed wording;
the refusals are defect D2's misclassification of a registered host) and
[21](../../assets/evidence/21-redelivery-and-dead-letter.md) (redelivery and dead letter). The
published demo still claims neither, so its `In demo` column stays `No`.

The hackathon packet is archived: its five-image gallery was composed on 2026-08-27 and its
published cut was locked on 2026-08-29. Uploading or changing that cut is not outstanding report
work. Preserve the frozen archive and its dated proof boundaries.

Three gallery captions are themselves narrower than this matrix allows, because the panels they
planned were never captured: image 02 shows the catalog but not per-agent ownership or policy
metadata, image 04 shows inline screening but not the IAM read split, and image 05 shows
correlation and retention but not cross-week exception continuity. Each underlying claim keeps its
status here — the narrowing is about what a screenshot proves, not about what is true.

**Version boundary:** the source targets Google ADK 2.14.0 (v0.9.0); the retained August and
October cohorts describe the earlier deployment, and the 5 November cohorts ran `google-adk` 2.13.0. A source pin does not establish a production
version. See [the canonical provenance table](../VERSIONS.md). Fresh captures must name
new revisions and remain separate from the immutable historical bundles.

Mutable live counts, upstream issue/PR status, public links, official rules, and video availability
must be refreshed immediately before publication; this review is not authority for facts that can
change after their recorded check dates.
