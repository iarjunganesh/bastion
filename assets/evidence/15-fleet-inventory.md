# Evidence 15 — count-only fleet inventory

**Captured:** 28 October 2026, 00:39:39 UTC. Read-only GCP census using
`scripts/capture_gcp_state.py`'s `capture()` function. No deployment, model invocation,
event publication, IAM change, or fault injection was performed.

The [machine-readable snapshot](fleet-inventory-2026-10-28.json) records **21/21 enabled
APIs and 39 resources**. Its values are identical to the August architecture snapshot
except for the capture timestamp. It contains counts and service names only.

| Resource | Count |
|---|---:|
| Cloud Run services | 4 |
| Firestore databases | 1 |
| Pub/Sub topics | 2 |
| Scheduler jobs | 0 |
| Secrets | 2 |
| Artifact repositories | 1 |
| Agent Gateways | 1 |
| Registry services | 17 |
| Model Armor templates | 1 |
| Agent engines | 2 |
| Project-created service accounts | 8 |

This establishes existence and counts, not package resolution, IAM binding counts,
operational readiness, negative control outcomes, scheduled investigations, retention
correctness, or model/data residency. Enabled Scheduler API with zero jobs does not mean
a schedule is running. ADK 2.13.0 source validation and production upgrade are separate.

The public console uses this capture for its inventory stamp. The August architecture
masters, screenshots, video, and sealed October study bundle remain unchanged and dated.
