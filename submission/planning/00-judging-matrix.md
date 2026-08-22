# Judging matrix

This is the final evidence map for the Fortified Enterprise Fleet submission. Official wording is
preserved in [DEVPOST.md](../DEVPOST.md); this file maps that wording to repository proof.

| Gate / criterion | Bastion answer | Proof |
|---|---|---|
| Gemini 3.5+ | Gemini 3.5 Flash through Vertex AI `global` | [evidence 02](../../assets/evidence/02-gemini-investigation.md), pinned config |
| Google agent framework | Google ADK 2.7.1 and official A2A SDK | Runtime/agent code, version gate |
| GCP infrastructure | Managed Runtime/Memory/Gateway/Registry plus Cloud Run, Firestore, Eventarc, Model Armor, Logging/Monitoring | [evidence 04–07](../../assets/README.md) |
| Innovation and utility | Read-only IAM review of the same project that runs the agents; deterministic self-audit and human exception memory | [ADR-001](../../docs/adr/001-real-iam-not-mock-data.md) |
| Technical implementation | Durable admission/leases/retry/DLQ, no direct production bypass, fixed schemas, Model Armor, separated identities | [architecture](../../docs/ARCHITECTURE.md), [P0/P1 ledger](08-audit-remediation-plan.md) |
| Demo and presentation | Catalog → durable event → governed route → denial/refusal → minimized review → audit dashboard | [storyboard](02-demo-storyboard.md) |

## Track-specific questions

| Requirement | Evidence-backed response |
|---|---|
| Cataloged for cross-department use | Three governed agent entries, institutional Agent Card metadata, deterministic department ownership, unknown-route refusal |
| Context across weeks of asynchronous operations | Managed session/memory plus Firestore lifecycle and expiring approved exceptions; restart and simulated prior-week suppression tests |
| Production data and compliance/security | Read-only live IAM, pre-model minimisation, `global` disclosure, protected output screen, IAM-private count-only findings, payload-free audit |
| Separation of concerns | Runtime Orchestrator, IAM-read Auditor, no-IAM-read Escalation; negative permission proof |
| Failure-tolerant routing | Lease/reclaim, duplicate collapse, retry/DLQ, malformed response and dependency-outage tests |
| Prompt injection, tool poisoning, PII | Model Armor; repository-owned fixed tool declarations and IAM; deterministic output/schema boundary |
| Audit logs and reasoning traces | Separate payload-free audit records and no-content ADK telemetry; regional retention/metrics/alerts/dashboard |

No score is self-awarded. The submission avoids unsupported latency, accuracy, availability,
cost, immutable-storage, legal-compliance, and end-to-end regional-residency claims.
