# P0/P1 audit remediation ledger

**Status:** engineering remediation complete on 2026-08-16; publication tasks remain in
[SUBMISSION.md](../SUBMISSION.md).

Closure here means the deterministic engineering is done. Capabilities that are deployed and
tested but have not yet been *observed* working are tracked separately in
[09-capture-backlog.md](09-capture-backlog.md), because a passing test and a capture are
different kinds of proof.

## P0 — deterministic safety

- [x] Missing/invalid risk fails closed.
- [x] IAM fields are minimized and pseudonymized before the model.
- [x] Model Armor is fail-closed at the ADK callback.
- [x] Post-model protected-data and fixed-schema notification checks run before side effects.
- [x] AuditPlugin covers run, agent, model, tool, refusal, and failure without payload values.
- [x] Notification receiver validates identity/schema and creates one record per deterministic key.

## P0 — durable asynchronous work

- [x] Versioned event ID/context/classification contract.
- [x] Firestore atomic admission, leases, attempts, retry, deduplication, terminal state, and
      reclaim after process loss.
- [x] Eventarc five-attempt dead-letter transport and review subscription.
- [x] Managed sessions/Memory Bank plus expiring, human-approved opaque exceptions.
- [x] Restart, duplicate, partial failure, stale memory, simulated prior-week suppression, and
      side-effect replay tested.

## P0 — zero-trust catalogued fleet

- [x] Managed Runtime plus two worker Agent Cards catalogued with institutional metadata.
- [x] Runtime Agent Identity bound to Agent Gateway; IAP grants destinations per Registry record.
- [x] Cloud Run dispatcher reduced to durable ingress and managed-Runtime invocation.
- [x] Dispatcher peer secret/direct invoker grants and obsolete roles removed and reconciled by
      deployment code.
- [x] Worker origin-secret rejection, IAM denial, findings denial, and allowed Runtime route proven.

## P0 — reproducible deployment

- [x] One full-repository Python 3.12 image with pinned dependencies.
- [x] Compute, control, Model Armor, and model regions are explicit and not conflated.
- [x] Idempotent Windows 11 bootstrap for identities, secrets, data plane, workers, Runtime,
      Gateway/Registry, observability, verification, and smoke.
- [x] Bounded Cloud Run scaling, least-privilege IAM, safe rollback candidates, and dry-run-first
      teardown preserving compliance state.

## P1 — verification and failure tolerance

- [x] Populated unit, integration, security, and load suites.
- [x] Timeout, malformed response, hallucinated argument, dependency outage, notification failure,
      duplicate, retry/DLQ, expired lease, stale memory, and policy refusal branches.
- [x] Operational objectives and alert mappings documented without claiming historical SLOs.
- [x] ADK `SequentialAgent` deprecation and experimental Remote A2A accepted with pinned version,
      tests, and migration trigger.
- [x] Locked dependencies, dependency audit, secret scan, type checks, and 100% coverage gate.

## P1 — sovereignty, compliance, and observability

- [x] Field-level data inventory, authorization purpose, processor boundary, deletion ownership,
      and global-model disclosure.
- [x] Payload-free audit events and no-content tracing configuration.
- [x] Regional 365-day analytics audit bucket and sink; four log metrics; five alert policies;
      operations dashboard.
- [x] Explicitly no immutability claim because the bucket is not locked.

## Exit evidence

- [measured fleet](../../assets/evidence/04-private-fleet-deployment.md)
- [managed Runtime/Gateway](../../assets/evidence/05-runtime-gateway.md)
- [durable findings behavior](../../assets/evidence/06-durable-findings.md)
- [retained observability](../../assets/evidence/07-observability.md)
- [tool-declaration boundary](../../assets/evidence/08-tool-poisoning.md)
- `infrastructure/verify_fleet.py`, `smoke_test.py`, `rollback.py`, and `teardown.py`
- Python 3.12 full gate: 198 tests, 100% statement and branch coverage

P2 media and Devpost publication are intentionally excluded from P0/P1 engineering closure.
