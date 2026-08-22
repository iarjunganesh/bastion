# Evidence 04 — measured private fleet deployment

**Captured:** 2026-08-22 UTC by `scripts/capture_gcp_state.py` against the Bastion project.
The committed state contains counts only and omits principals, service-account addresses, policy
bindings, URLs, request payloads, and secret metadata.

## Measured state

- **21/21** named APIs enabled.
- **39** resources: four Cloud Run services, one Firestore database, two Pub/Sub topics, zero
  Scheduler jobs, two secrets, one Artifact Registry repository, one Agent Gateway, seventeen
  Registry services, one Model Armor template, two Agent Engines, and eight user-created service
  accounts.
- The seventeen Registry records comprise three Bastion agents and fourteen approved platform
  destinations. Only two Bastion records are A2A worker cards; the Orchestrator is the managed
  Runtime entry.
- The count rose from 33 on 2026-08-16. Four of the five new resources are Registry destinations
  for the mTLS and regional hosts Google API clients actually resolve to, which a plain
  `*.googleapis.com` entry does not cover; the fifth is the break-glass approver identity that
  replaced an unusable direct grant to the human reviewer.
- It rose again to 39 on 2026-08-22: the federated CI deploy identity. **The Workload
  Identity pool and provider backing it are not in this number** - `capture_gcp_state.py`
  does not enumerate them, so the figure understates the deployed surface by two. Recorded
  rather than quietly corrected, because the count is only worth citing if what it omits is
  stated.
- Cloud Run has one internal durable ingress, two origin-protected worker surfaces, and one
  IAM-private findings endpoint.

## Proof boundary

This proves resource existence and counts. Runtime traversal, findings behavior, and retained
operations configuration are separate evidence 05–07. Current machine-readable measurement:
[gcp-state.json](../architecture/gcp-state.json).

```powershell
python scripts/capture_gcp_state.py
python scripts/capture_gcp_state.py --check
```
