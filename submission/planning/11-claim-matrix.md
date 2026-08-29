# Final claim matrix

- **Reviewed:** 2026-08-24; reconciled 2026-08-27 against release `v0.6.0` after the P0.6-P0.9
  evidence sprint, the gallery composition, and the dependency bump; reconciled again 2026-08-29
  against `v0.7.0`, when the demo was published and the `In demo` column became answerable
- **Purpose:** Internal pre-publication gate before drafting Devpost, article, social, screenshot,
  or demo copy. `Partial` means the public sentence must use the narrower wording in the final
  column; it does not mean the underlying architecture is absent.

| Claim | Implemented | Tested | Deployed | Observed | In demo | Safe to claim? | Evidence boundary and safe wording |
|---|---:|---:|---:|---:|---:|---:|---|
| Real IAM read | Yes | Yes | Yes | Yes | Yes | Yes | [Evidence 11](../../assets/evidence/11-current-route-correlation.md) is now the current-route proof: a count-only companion probe measured 62 live bindings, 3 deterministic findings, 2 canonical owning departments and 0 raw IAM fields at the model boundary on 2026-08-25. [Evidence 09](../../assets/evidence/09-cross-department-routing.md) records an earlier 52-binding measurement and remains valid for its own date; [evidence 02](../../assets/evidence/02-gemini-investigation.md) is historical pre-Gateway. Say **read-only production IAM**, quote 62 from evidence 11, and never imply raw principals or bindings are retained. |
| Exact deterministic finding set | Yes | Yes | Yes | Yes | Yes | Yes | P0.1 compares the model report field-by-field with the tool's canonical findings and was deployed before the Aug 23 successful run recorded in [ADR-012](../../docs/adr/012-structured-findings-across-a2a.md). Say the model may write bounded rationale but cannot add, drop, re-score, or redirect a finding. Mutation refusals are test proof; the live observation is the successful enforced path. |
| Cross-department routing | Yes | Yes | Yes | Yes | Yes | Yes | [Evidence 11](../../assets/evidence/11-current-route-correlation.md) now carries this end to end on the current route: 3 canonical findings across 2 departments, of which 2 were delivered to `security-engineering` after policy suppressed the approved `platform-infra` finding, with exactly one durable review record created. [Evidence 09](../../assets/evidence/09-cross-department-routing.md) remains the standalone routing measurement. This pair supports an end-to-end action claim; evidence 09 alone does not. |
| Human exception continuity | Yes | Yes | Yes | Yes | Yes | Yes | [Evidence 10](../../assets/evidence/10-cross-week-suppression.md) observes a real three-day gap across deployments and restarts and re-verifies suppression after P0.1-P0.3. Say **remembered across a real elapsed gap** or **durable asynchronous context**; never say a literal week elapsed or that expiry firing was observed. |
| Escalation IAM denial | Yes | Yes | Yes | Yes | Yes | Yes | [Evidence 03](../../assets/evidence/03-escalation-agent-denied.md) records a successful impersonation followed by a real IAM-read denial, while the Auditor identity succeeds. Say IAM structurally denies the Escalation identity. Disclose that the retained denial was produced by workstation impersonation, not mid-investigation. |
| Agent-mediated Armor refusal | Yes | Yes | Yes | Yes | Yes | Yes | **Closed 2026-08-25.** [Evidence 12](../../assets/evidence/12-agent-mediated-model-armor-refusal.md) observed the deployed `before_model_callback` refusing the approved injection sample on the Auditor's authenticated A2A surface: benign control completed, sample's task failed closed with `policy_match`, and 0 model submissions, completions or tool calls followed. Describe the threat as a **compromised authorized caller**, not an anonymous attacker. [Evidence 01](../../assets/evidence/01-model-armor-block.md) stays the historical direct-template probe. |
| Managed Gateway refusal | Yes | Yes | Yes | Partial | No | Partial | [Evidence 05](../../assets/evidence/05-runtime-gateway.md) proves the Runtime is Gateway-bound and the fail-closed policy is configured. Live IAP refusal is observed for a catalogued non-standard Google host, which is residual platform behavior, not the intended unregistered-caller test. Until P0.10, claim the governed route and fail-closed observation; do not claim the planned destination/caller refusal scenarios. |
| Retry/DLQ behavior | Yes | Yes | Yes | Partial | No | Partial | [Evidence 06](../../assets/evidence/06-durable-findings.md) observes one successful delivery, a dependency failure left failed/reclaimable, idempotent review, and a configured five-attempt DLQ. Until P0.11, say **bounded delivery is configured and retry/idempotency paths are tested**; do not say Eventarc redelivery or the fifth-attempt dead-letter boundary was observed. |
| Correlated trace/audit | Yes | Yes | Yes | Yes | Yes | Yes | **Closed 2026-08-25.** [Evidence 11](../../assets/evidence/11-current-route-correlation.md) assembles 28 unique payload-free events across 3 invocation ids under one investigation id; [evidence 13](../../assets/evidence/13-current-route-trace.md) adds the connected 22-span Cloud Trace over 1m 5.401s; [evidence 07](../../assets/evidence/07-observability.md) proves the 365-day `europe-west4` retention. Always keep the two artifacts distinct: the trace is sampled and expires, the audit trail is the compliance record. Retention is proven; immutability is not — the bucket is unlocked. |
| Recurring trigger or event-driven limitation | Yes | Yes | Yes | Yes | Yes | Yes | The deployed Pub/Sub/Eventarc path is event-driven and observed; the measured state has no Scheduler job. Say **triggered by an approved enterprise event source** and explicitly state that this snapshot claims no recurring schedule. Never use `continuous`, `scheduled`, or `on its own` for Bastion's current cadence. |

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

**One claim shape is newly unsafe as of `v0.6.0`:** anything implying the repository's dependency
versions are the ones running in production. They are not. The repository pins `google-adk` 2.8.0;
both deployed surfaces still run the 2.7.1 resolution `v0.4.0` deployed. Every observation in the
evidence set stays true of the fleet it observed, but "we run ADK 2.8.0 in production" is not
available until a redeploy and live re-verification happen — which will also oblige re-capturing
evidence 11, 12 and 13 and recomposing gallery images 03, 04 and 05.

Mutable live counts, upstream issue/PR status, public links, official rules, and video availability
must be refreshed immediately before publication; this review is not authority for facts that can
change after 2026-08-27.
