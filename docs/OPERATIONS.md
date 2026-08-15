# Operations objectives and release checks

These are release objectives, not observed production metrics. The fleet must not claim them as
met until Cloud Monitoring records a full investigation run.

| Signal | Objective | Alert / release condition |
|---|---|---|
| Investigation completion | 99% of accepted events complete within 10 minutes | Alert when a received/running event exceeds 10 minutes |
| Duplicate effects | Zero duplicate notification keys | Block release if outbox has duplicate delivered keys |
| Audit completeness | One audit record for every model/tool/refusal/error action | Alert on a trace invocation with no matching audit record |
| Gateway refusals | Refusal rate is visible by caller/target/reason | Alert on a 5× baseline spike; investigate rather than auto-open access |
| Model Armor failures | Any unavailable/blocked decision is fail-closed | Alert on error/refusal spike; never retry by bypassing Armor |
| Dead letters | Zero unresolved dead letters | Page the owning department on a dead-letter transition |
| Cost | Cloud Run max instances remains ≤ `BASTION_MAX_INSTANCES` | Alert on budget anomaly and suspend scheduler before widening IAM scope |

The private deployment emits no-content ADK telemetry and structured payload-free audit JSON to
Cloud Logging. `infrastructure/verify_fleet.py` verifies private ingress, workload identities,
and internal classification after deployment. Alert policies and dashboards remain an approved
platform-owner provisioning task; they are deliberately not represented as deployed controls.
