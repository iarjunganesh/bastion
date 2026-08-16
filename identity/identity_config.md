# Workload identity contract

Bastion has no key files and no shared agent service account. `identity/policy.py` is the
machine-checked baseline; this document explains the deployed split.

| Workload | Identity | Capabilities |
|---|---|---|
| Managed Orchestrator | Agent Runtime Agent Identity | Gateway/IAP egress to catalogued destinations; Vertex, Firestore, Model Armor, logs, traces, metrics; worker invocation |
| Durable ingress | `orchestrator-sa` | Invoke managed Runtime; Firestore state; logs, traces, metrics; no peer origin secret, worker invoker, Model Armor, or Pub/Sub publisher role |
| Access Auditor | `access-auditor-sa` | Read-only IAM security review, Cloud Asset, Recommender, Vertex/Model Armor, HMAC and A2A secrets |
| Escalation Agent | `escalation-agent-sa` | Vertex/Model Armor, A2A secret, private findings invocation; no IAM/Asset read |
| Findings API | `findings-api-sa` | Firestore create/read for idempotent review records |
| Eventarc delivery | `eventarc-invoker-sa` | Invoke only durable ingress; Eventarc receiver |

Managed Google service agents retain their product service-agent roles. They are not Bastion
workload identities and are not represented as agents.

## Enforced route

The Eventarc identity can reach only the Cloud Run ingress. The ingress can reach the managed
Runtime but cannot authenticate directly to workers. The Runtime's Agent Identity is admitted by
Gateway IAP per Registry resource and by worker invocation policy; workers additionally validate
the origin secret. Escalation alone can invoke the IAM-private findings API.

`infrastructure/deploy.sh` reconciles stale grants from the former direct-peer topology.
`infrastructure/verify_fleet.py` fails when the dispatcher retains a peer secret or lacks its
managed Runtime target.

## Verification

The captured negative test in
[assets/evidence/03-escalation-agent-denied.md](../assets/evidence/03-escalation-agent-denied.md)
shows the Escalation identity denied IAM policy access. Security tests cover token audience and
origin-secret rejection. Production smoke verifies anonymous findings denial and a successful
write under the real Escalation identity, then confirms the duplicate is collapsed.
