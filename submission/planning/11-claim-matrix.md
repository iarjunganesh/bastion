# Final claim matrix

- **Reviewed:** 2026-08-24
- **Purpose:** Internal pre-publication gate before drafting Devpost, article, social, screenshot,
  or demo copy. `Partial` means the public sentence must use the narrower wording in the final
  column; it does not mean the underlying architecture is absent.

| Claim | Implemented | Tested | Deployed | Observed | In demo | Safe to claim? | Evidence boundary and safe wording |
|---|---:|---:|---:|---:|---:|---:|---|
| Real IAM read | Yes | Yes | Yes | Yes | No | Yes | [Evidence 09](../../assets/evidence/09-cross-department-routing.md) observed the deployed Auditor code path reading live IAM through Cloud Asset Inventory with counts only. Say **read-only production IAM**; do not show or imply retention of raw principals or bindings. Refresh the mutable counts in P0.9 before final copy. |
| Exact deterministic finding set | Yes | Yes | Yes | Yes | No | Yes | P0.1 compares the model report field-by-field with the tool's canonical findings and was deployed before the Aug 23 successful run recorded in [ADR-012](../../docs/adr/012-structured-findings-across-a2a.md). Say the model may write bounded rationale but cannot add, drop, re-score, or redirect a finding. Mutation refusals are test proof; the live observation is the successful enforced path. |
| Cross-department routing | Yes | Yes | Yes | Yes | No | Yes | [Evidence 09](../../assets/evidence/09-cross-department-routing.md) measured three findings routed deterministically to two departments from live data. This is routing proof, not by itself a completed-investigation trace; pair it with delivery or suppression evidence when claiming an end-to-end action. |
| Human exception continuity | Yes | Yes | Yes | Yes | No | Yes | [Evidence 10](../../assets/evidence/10-cross-week-suppression.md) observes a real three-day gap across deployments and restarts and re-verifies suppression after P0.1-P0.3. Say **remembered across a real elapsed gap** or **durable asynchronous context**; never say a literal week elapsed or that expiry firing was observed. |
| Escalation IAM denial | Yes | Yes | Yes | Yes | No | Yes | [Evidence 03](../../assets/evidence/03-escalation-agent-denied.md) records a successful impersonation followed by a real IAM-read denial, while the Auditor identity succeeds. Say IAM structurally denies the Escalation identity. Disclose that the retained denial was produced by workstation impersonation, not mid-investigation. |
| Agent-mediated Armor refusal | Yes | Yes | Yes | No | No | Partial | [Evidence 01](../../assets/evidence/01-model-armor-block.md) is a direct managed-template refusal; callback and fail-closed behavior are tested and deployed. Until P0.6, claim only **the managed template refused the sample and the agent callback is tested/deployed**. Do not call it an observed agent-mediated pre-Gemini refusal. |
| Managed Gateway refusal | Yes | Yes | Yes | Partial | No | Partial | [Evidence 05](../../assets/evidence/05-runtime-gateway.md) proves the Runtime is Gateway-bound and the fail-closed policy is configured. Live IAP refusal is observed for a catalogued non-standard Google host, which is residual platform behavior, not the intended unregistered-caller test. Until P0.10, claim the governed route and fail-closed observation; do not claim the planned destination/caller refusal scenarios. |
| Retry/DLQ behavior | Yes | Yes | Yes | Partial | No | Partial | [Evidence 06](../../assets/evidence/06-durable-findings.md) observes one successful delivery, a dependency failure left failed/reclaimable, idempotent review, and a configured five-attempt DLQ. Until P0.11, say **bounded delivery is configured and retry/idempotency paths are tested**; do not say Eventarc redelivery or the fifth-attempt dead-letter boundary was observed. |
| Correlated trace/audit | Yes | Yes | Yes | Partial | No | Partial | [Evidence 10](../../assets/evidence/10-cross-week-suppression.md) assembles 32 payload-free audit records under one investigation across Runtime and both workers; [evidence 07](../../assets/evidence/07-observability.md) proves retention controls. Cloud Trace remains uncaptured. Claim correlated retained audit separately; do not claim a complete current-route Cloud Trace chain until P0.7. |
| Recurring trigger or event-driven limitation | Yes | Yes | Yes | Yes | No | Yes | The deployed Pub/Sub/Eventarc path is event-driven and observed; the measured state has no Scheduler job. Say **triggered by an approved enterprise event source** and explicitly state that this snapshot claims no recurring schedule. Never use `continuous`, `scheduled`, or `on its own` for Bastion's current cadence. |

## Publication rule

No row is currently in the demo because the final public video has not been recorded. Public copy
may use every `Yes` row within its stated boundary. A `Partial` row must keep the narrower wording
above until its named capture closes and the evidence ledger, submission handoff, site, and this
matrix are updated together.

Mutable live counts, upstream issue/PR status, public links, official rules, and video availability
must be refreshed immediately before publication; this review is not authority for facts that can
change after 2026-08-24.
