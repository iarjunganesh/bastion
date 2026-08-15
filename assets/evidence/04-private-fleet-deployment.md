# Evidence 04 — measured private fleet deployment

**Captured:** 2026-08-15 UTC by `scripts/capture_gcp_state.py` against
`bastion-fleet-2026`. The committed state file contains counts only; it deliberately omits
principal identifiers, service-account emails, policy bindings, URLs, and request payloads.

## What was measured

- **21/21 named APIs enabled.**
- **20 deployed resources:** four Cloud Run services, one Firestore database, one Pub/Sub topic,
  one Secret Manager secret, one Artifact Registry repository, one Model Armor template, one
  Agent Engine, six user-created service accounts, and four Agent Registry records.
- **Three Bastion services were registered** as private JSON-RPC/A2A Registry services:
  Access Auditor, Orchestrator, and Escalation Agent. The fourth record is Google's pre-existing
  Workspace Agent and is not counted as a Bastion achievement.
- **Ingress is internal and Cloud Run does not allow unauthenticated invocation.** Eventarc uses
  its dedicated delivery identity; the Escalation Agent alone has invoker access to the private,
  count-only findings API.

## Boundaries of this evidence

This is deployment evidence, not a retained successful multi-agent trace. It does **not** prove
a cross-week memory replay, a managed Agent Gateway route, a production audit-log capture, or a
full model-success trace; those remain explicitly tracked in
[ADR-006](../../docs/adr/006-pillar-coverage.md).

## Reproduce

```powershell
python scripts/capture_gcp_state.py
python scripts/capture_gcp_state.py --check
```

The resulting committed measurement is
[`assets/architecture/gcp-state.json`](../architecture/gcp-state.json).
