# Evidence 07 — retained operations controls

**Verified:** 2026-08-16 UTC by the idempotent observability provisioner and live API reads.

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

```powershell
python -m infrastructure.provision_observability
```
