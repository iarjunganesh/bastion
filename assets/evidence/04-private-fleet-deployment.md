# Evidence 04 — measured private fleet deployment

**Captured:** 2026-08-16 UTC by `scripts/capture_gcp_state.py` against the Bastion project.
The committed state contains counts only and omits principals, service-account addresses, policy
bindings, URLs, request payloads, and secret metadata.

## Measured state

- **21/21** named APIs enabled.
- **33** resources: four Cloud Run services, one Firestore database, two Pub/Sub topics, zero
  Scheduler jobs, two secrets, one Artifact Registry repository, one Agent Gateway, thirteen
  Registry services, one Model Armor template, two Agent Engines, and six user-created service
  accounts.
- The thirteen Registry records comprise three Bastion agents and ten approved platform
  destinations. Only two Bastion records are A2A worker cards; the Orchestrator is the managed
  Runtime entry.
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
