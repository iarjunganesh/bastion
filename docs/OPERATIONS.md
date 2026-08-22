# Operations objectives and release gates

The live project has four log-based metrics, five enabled alert policies, a 365-day regional
analytics log bucket, a payload-free audit sink, and the **Bastion Fleet Operations** dashboard.
These are configured controls; the objectives below are service targets, not historical SLO
attainment claims.

| Signal | Objective | Live detection / response |
|---|---|---|
| Investigation completion | 99% of admitted events finish within 10 minutes | Stuck-delivery alert; inspect Firestore status/lease and Eventarc delivery |
| Duplicate effects | Zero duplicate review records | Deterministic idempotency key and create-once receiver; replay returns `accepted=false` |
| Audit failures | Every supported run/agent/model/tool action has a terminal audit event | Audit-failure metric and alert; correlate by investigation ID across hops, invocation ID within one agent run |
| Policy refusals | Refusal rate remains explainable by bounded reason | Refusal-spike alert; never bypass policy to restore throughput |
| Model Armor | Unavailable or matched screening always fails closed | Dedicated failure/refusal metric and alert |
| Dead letters | Zero unresolved review messages | Backlog alert on `bastion-dead-letter-review`; investigate before replay |
| Cost/capacity | Cloud Run max instances stays within `BASTION_MAX_INSTANCES` | Deployment verifier plus platform budget controls; no automatic IAM widening |

## Release procedure

1. Run the Python 3.12 quality gates from the README.
2. Deploy one immutable image to the four Cloud Run services.
3. Configure Registry, Gateway, Runtime, IAM, DLQ, audit routing, metrics, alerts, and dashboard.
4. Run `python -m infrastructure.verify_fleet` and `python -m infrastructure.smoke_test`.
5. Capture only redacted counts/statuses in `assets/evidence/`.

`infrastructure/rollback.py` is dry-run by default and permits only one of the two newest safe
revisions. `infrastructure/teardown.py` is also dry-run by default and preserves Firestore,
secrets, managed Runtime/Memory, and audit logs. Applying teardown requires the exact project ID.

## Failure semantics

A handler admits an event before execution, owns a bounded lease, returns `503` for a concurrent
or failed attempt so Eventarc retains delivery, and acknowledges an already-completed replay.
Expired leases are reclaimable. Delivery stops after five attempts at the dead-letter review
subscription. Dependency errors are audited by class without leaking response content.
