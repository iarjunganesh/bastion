# Evidence 07 — retained operations controls

**Verified:** 2026-08-16 UTC by the idempotent observability provisioner and live API reads.
**Capture review:** 2026-08-25; accepted 1920×1080 raw source showing the named bucket,
`europe-west4`, 365-day retention, and Observability Analytics enabled.

- Regional analytics log bucket: `europe-west4`, **365-day retention**, unlocked.
- Payload-free audit sink filtering for audit event and invocation correlation fields.
- Four log-based metrics: audit failures, policy refusals, audit records, and Model Armor
  failures/refusals.
- Five enabled alert policies: audit action failures, refusal spike, Model Armor failure/refusal,
  stuck investigation delivery, and dead-letter backlog.
- One **Bastion Fleet Operations** dashboard.
- No recent Cloud Logging sink-writer/export failure was found after IAM reconciliation.

The bucket is deliberately **not locked**. Retention is proven; immutability/WORM is not claimed
because locking is irreversible. These are live control configurations, not proof that the fleet
has attained its target SLOs over time.

The reviewed Console capture does not expose a lock field, so it is retained as configuration
proof only and does not visually upgrade the immutability boundary.

```powershell
python -m infrastructure.provision_observability
```
