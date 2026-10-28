# Final claim matrix

- **Reviewed:** 2026-08-24; reconciled 2026-08-27 against release `v0.6.0` after the P0.6-P0.9
  evidence sprint, the gallery composition, and the dependency bump; reconciled again 2026-08-29
  against `v0.7.0`, when the demo was published and the `In demo` column became answerable
- **Report supplement:** 2026-10-27 live validation, documented 2026-10-28 below; the August
  capture dates, submitted demo and two `Partial` classifications are preserved.
- **Purpose:** Internal pre-publication gate before drafting Devpost, article, social, screenshot,
  or demo copy. `Partial` means the public sentence must use the narrower wording in the final
  column; it does not mean the underlying architecture is absent.

| Claim | Implemented | Tested | Deployed | Observed | In demo | Safe to claim? | Evidence boundary and safe wording |
|---|---:|---:|---:|---:|---:|---:|---|
| Real IAM read | Yes | Yes | Yes | Yes | Yes | Yes | [Evidence 11](../../assets/evidence/11-current-route-correlation.md) is the 25 Aug binding/count proof: 62 live bindings, 3 deterministic findings, 2 canonical owning departments and 0 raw IAM finding-schema fields. [Evidence 14](../../assets/evidence/14-live-validation.md) re-observes 20 IAM-tool/gated execution paths on 27 Oct, without a new binding/pre-policy census. Evidence 09's 52 bindings remain earlier history; evidence 02 remains pre-Gateway. Say **read-only production IAM**, keep census dates explicit, and never imply raw principals/bindings are retained. |
| Exact deterministic finding set | Yes | Yes | Yes | Yes | Yes | Yes | P0.1 checks model fields against canonical tool findings; [ADR-012](../../docs/adr/012-structured-findings-across-a2a.md) records the Aug 23 successful enforced path. [Evidence 14](../../assets/evidence/14-live-validation.md) adds 20 gated successful paths on 27 Oct, not new mutation probes. The model may write bounded rationale, not alter authoritative fields; mutation refusals remain offline test proof. |
| Cross-department routing | Yes | Yes | Yes | Yes | Yes | Yes | [Evidence 11](../../assets/evidence/11-current-route-correlation.md): 25 Aug, 3 canonical findings/2 departments before policy, 2 delivered findings/1 review record after suppression. [Evidence 14](../../assets/evidence/14-live-validation.md): 27 Oct, 3 delivered instances/2 department records per investigation, across 20 runs. The latter is not a new canonical census or expiry measurement; 60 delivered instances are not 60 distinct risks. |
| Human exception continuity | Yes | Yes | Yes | Yes | Yes | Yes | [Evidence 10](../../assets/evidence/10-cross-week-suppression.md) observes the 19-22 Aug three-day gap, reverified 23 Aug. Not re-probed on 27 Oct. Say **remembered across a real elapsed gap**; do not infer expiry or a literal week from October's delivered counts. |
| Escalation IAM denial | Yes | Yes | Yes | Yes | Yes | Yes | [Evidence 03](../../assets/evidence/03-escalation-agent-denied.md) records successful impersonation then IAM-read denial on 15 Aug, with an Auditor success control. This negative probe was not repeated on 27 Oct; successful Escalation deliveries are not new denial proof. |
| Agent-mediated Armor refusal | Yes | Yes | Yes | Yes | Yes | Yes | **Closed 2026-08-25:** [evidence 12](../../assets/evidence/12-agent-mediated-model-armor-refusal.md), authenticated Auditor injection refused with no subsequent model/tool call. This models a **compromised authorized caller**, not an anonymous one. October's normal successful path did not repeat the refusal probe; evidence 01 remains the earlier direct-template measurement. |
| Managed Gateway refusal | Yes | Yes | Yes | Partial | No | Partial | [Evidence 05](../../assets/evidence/05-runtime-gateway.md) retains Gateway binding/fail-closed configuration; the residual IAP denial is not the intended unregistered-caller test. [Evidence 14](../../assets/evidence/14-live-validation.md) adds 20 approved Runtime/worker flows, not a new Registry/IAP decision or refusal probe. P0.10 remains open. |
| Retry/DLQ behavior | Yes | Yes | Yes | Partial | No | Partial | [Evidence 06](../../assets/evidence/06-durable-findings.md) retains completion/failure-reclaim, receiver idempotency and configured five-attempt DLQ. [Evidence 14](../../assets/evidence/14-live-validation.md) adds 20 one-attempt completions and five replay publications with unchanged effects for 120s; delivery was not confirmed per message. P0.11 remains open: no observed Eventarc redelivery/fifth-attempt dead letter. |
| Correlated trace/audit | Yes | Yes | Yes | Yes | Yes | Yes | [Evidence 11](../../assets/evidence/11-current-route-correlation.md)/[13](../../assets/evidence/13-current-route-trace.md): 25 Aug, 28 events/3 invocations and a 22-span trace. [Evidence 14](../../assets/evidence/14-live-validation.md): 27 Oct, 560 events/60 invocations and one time-matched 22-span trace, not an embedded investigation-ID join. Retention remains dated [evidence 07](../../assets/evidence/07-observability.md) configuration proof; no new retention/immutability claim. |
| Recurring trigger or event-driven limitation | Yes | Yes | Yes | Yes | Yes | Yes | August snapshot: observed Pub/Sub/Eventarc path, no Scheduler job. [Evidence 14](../../assets/evidence/14-live-validation.md): 20 further Pub/Sub/Eventarc completions on 27 Oct, without a fresh Scheduler census. Say **triggered by an approved enterprise event source**, not recurring/continuous operation. |

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
currency cost were not freshly measured. These observations strengthen bounded execution/
delivery evidence but do not change either `Partial` row, the demo column, the 25 August
62-binding measurement, exception-expiry proof, or C4's deferred status.

## Publication rule

The column says `Yes` only where a claim appears in the *published* cut. The 3:53 demo was
published on 2026-08-29 at <https://youtu.be/Xpj8YmzFfpk>, so eight rows are now `Yes` — each
verified against the beat text rather than assumed from the row title. The two `Partial` rows are
the two that stay `No`: the narration never claims a managed Gateway refusal or an observed
redelivery, which is the point. The narration was drafted against this table —
every sentence in [`../DEMO_SCRIPT.md`](../DEMO_SCRIPT.md) is defensible against a row here, and
the two `Partial` rows are absent from it entirely rather than narrowed, so no wording below can
be weakened by what gets said aloud. Public copy may use every `Yes` row within its stated
boundary. A `Partial` row must keep the narrower wording
above until its named capture closes and the evidence ledger, submission handoff, site, and this
matrix are updated together.

Two rows remain `Partial`, and they are exactly the two captures still open in
[09-capture-backlog.md](09-capture-backlog.md): managed Gateway refusals (capture 6) and
timeout/retry/dead-letter (capture 7). Until those close, public copy says **bounded delivery is
configured and retry/idempotency paths are tested** and claims only the governed route and its
fail-closed observation — never an observed Eventarc redelivery, an observed fifth-attempt
dead-letter, or the planned unregistered-caller refusal. Per-caller rate limiting is never claimed
at all; it does not exist.

For the current hackathon packet, those two captures are deliberately deferred rather than treated
as video blockers. The narrower wording above is the accepted publication boundary; with the
five-image gallery composed on 2026-08-27 and the cut locked on 2026-08-29, the remaining
mandatory work is uploading the assembled cut and publishing its URL.

Three gallery captions are themselves narrower than this matrix allows, because the panels they
planned were never captured: image 02 shows the catalog but not per-agent ownership or policy
metadata, image 04 shows inline screening but not the IAM read split, and image 05 shows
correlation and retention but not cross-week exception continuity. Each underlying claim keeps its
status here — the narrowing is about what a screenshot proves, not about what is true.

**Version boundary:** the source targets Google ADK 2.13.0; the retained August and
October cohorts describe the earlier deployment. A source pin does not establish a production
version. See [the canonical provenance table](../../docs/VERSIONS.md). Fresh captures must name
new revisions and remain separate from the immutable historical bundles.

Mutable live counts, upstream issue/PR status, public links, official rules, and video availability
must be refreshed immediately before publication; this review is not authority for facts that can
change after 2026-08-27.
